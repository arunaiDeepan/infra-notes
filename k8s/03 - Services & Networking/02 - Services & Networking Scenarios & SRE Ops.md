# Services & Networking - Scenarios & SRE Ops

> The failure patterns that account for most Kubernetes networking pain, plus CKA/CKAD tasks, interview questions, EKS production scenarios, the without-node-access vs with-node-access debug toolkit, and runbooks. Pair with [01 - Services & Networking Guide](01%20-%20Services%20%26%20Networking%20Guide.md).

See also: [01 - Services & Networking Guide](01%20-%20Services%20%26%20Networking%20Guide.md) · [02 - Request Lifecycle Scenarios & SRE Ops](02%20-%20Request%20Lifecycle%20Scenarios%20%26%20SRE%20Ops.md) · [02 - Workload Resilience Scenarios & SRE Ops](02%20-%20Workload%20Resilience%20Scenarios%20%26%20SRE%20Ops.md)

---

## Table of Contents

- [1. Frequently Tested Concepts](#1-frequently-tested-concepts)
- [2. Keywords → Cause](#2-keywords--cause)
- [3. The Four Classic Failure Patterns](#3-the-four-classic-failure-patterns)
- [4. CKA/CKAD Practical Tasks](#4-ckackad-practical-tasks)
- [5. Interview Questions](#5-interview-questions)
- [6. EKS Production Scenarios](#6-eks-production-scenarios)
- [7. Debug Toolkit (with / without node access)](#7-debug-toolkit-with--without-node-access)
- [8. Runbooks](#8-runbooks)
- [9. One-Line Recap](#9-one-line-recap)

---

## 1. Frequently Tested Concepts

- **ClusterIP is virtual** - dataplane DNATs it to a Pod IP.
- **Readiness gates traffic**; **EndpointSlices** carry readiness to kube-proxy.
- **Zero endpoints = selector/label mismatch or all-not-ready.**
- **`externalTrafficPolicy: Local`** preserves client IP, costs spread.
- **Hairpin** breaks single-replica self-calls.
- **L7 ingress re-originates** → use `X-Forwarded-For`.
- EKS: **VPC CNI = real Pod IPs**; **ALB (Ingress)** vs **NLB (LoadBalancer)**.
- **NetworkPolicy needs an enforcing CNI** or it's ignored.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords → Cause

| Phrase                                   | Points to                                    |
| :--------------------------------------- | :------------------------------------------- |
| "Running but no traffic"                 | Readiness / EndpointSlices                   |
| "Service has 0 endpoints"                | Selector ↔ label mismatch                    |
| "Pod IP works, Service doesn't"          | kube-proxy / port mapping / dataplane        |
| "binds to 127.0.0.1"                     | App listening on loopback, not `0.0.0.0`     |
| "client IP is node/LB IP"                | SNAT → XFF or `externalTrafficPolicy: Local` |
| "single replica times out on itself"     | Hairpin                                      |
| "NetworkPolicy applied, nothing changed" | CNI doesn't enforce policy                   |
| "EXTERNAL-IP pending / ADDRESS empty"    | LB controller / IAM / subnet tags            |
| "cross-AZ latency + data charges"        | No topology-aware routing                    |

[⬆ Back to top](#table-of-contents)

---

## 3. The Four Classic Failure Patterns

**Pattern 1 - Selector mismatch.** Pods exist (maybe even Ready) but the Service has **zero endpoints** because `.spec.selector` ≠ Pod labels. No networking fix helps.

**Pattern 2 - Wrong readiness probe.** Pods Running, readiness fails → endpoints empty/not-ready. Classic causes: wrong path (`/health` vs `/healthz`), wrong port (probe 80, app 8080), non-200 (app returns 401/302), app bound to `127.0.0.1`.

**Pattern 3 - Readiness coupled to a fragile dependency.** Readiness checks the DB/cache; DB is slow → all Pods NotReady → Service has no endpoints → outage. Readiness should answer "can I serve a request?", not "is the universe perfect?"

**Pattern 4 - Single-replica hairpin.** One Pod calls its own Service → hairpins back to itself → fails if hairpin mode is off. Fix: `localhost` self-checks, >1 replica, or CNI hairpin support.

[⬆ Back to top](#table-of-contents)

---

## 4. CKA/CKAD Practical Tasks

**T1 - Diagnose a Service with no endpoints:**

```bash
kubectl get svc app-svc -o yaml | grep -A4 selector
kubectl get pods --show-labels
kubectl get endpointslices -l kubernetes.io/service-name=app-svc -o wide
```

**T2 - Prove in-cluster routing both ways:**

```bash
kubectl run tmp --rm -it --image=curlimages/curl -- sh
#   curl -v http://app-svc:80/healthz          # via Service
#   curl -v http://<podIP>:8080/healthz         # bypass Service
```

**T3 - Confirm the container is listening on all interfaces:**

```bash
kubectl exec -it <pod> -- sh -c "ss -lntp || netstat -lntp"   # want 0.0.0.0:8080, not 127.0.0.1
```

**T4 - Write a default-deny + allow-DNS NetworkPolicy (CKAD):**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny-ingress }
spec:
  podSelector: {}
  policyTypes: [Ingress]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: allow-dns-egress }
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
    - to: [{ namespaceSelector: {} }]
      ports: [{ protocol: UDP, port: 53 }, { protocol: TCP, port: 53 }]
```

[⬆ Back to top](#table-of-contents)

---

## 5. Interview Questions

**Q1: Service has no endpoints - what's your first move?**

> Compare `.spec.selector` to Pod labels, then check Pod `Ready`. It's labels or readiness, not networking.

**Q2: Explain iptables vs IPVS vs eBPF kube-proxy modes.**

> iptables: per-Service NAT chains, probabilistic LB, heavy at scale. IPVS: kernel LB, real algorithms, scales better. eBPF (Cilium): replaces kube-proxy, in-kernel LB + policy, best observability. Same Service semantics throughout.

**Q3: Why might my backend not see the real client IP?**

> SNAT on cross-node NodePort forwarding, or L7 ingress re-originating the connection. Use `externalTrafficPolicy: Local` (L4) or `X-Forwarded-For` (L7); NLB can preserve source IP.

**Q4: What's a readiness gate and why does AWS use one?**

> An extra condition gating Pod readiness. The AWS LB Controller keeps a Pod not-Ready until it's registered+healthy in the target group, so rollouts don't shift traffic before the LB can route it.

**Q5: Difference between liveness and readiness - and a danger of getting them wrong?**

> Liveness restarts; readiness gates traffic. A too-aggressive liveness probe causes restart storms; readiness coupled to a slow dependency causes cluster-wide endpoint loss.

[⬆ Back to top](#table-of-contents)

---

## 6. EKS Production Scenarios

### Medium

**M1 - `Service type: LoadBalancer` stuck `<pending>`.**

> AWS LB Controller missing/misconfigured, IRSA perms absent, or subnets not tagged (`kubernetes.io/role/elb`). Check controller logs and subnet tags.

**M2 - NetworkPolicy applied but traffic still flows.**

> The enforcing component isn't enabled. On VPC CNI, enable the network-policy agent (or run Cilium). Without it, policies are inert.

**M3 - Intermittent DNS timeouts under load.**

> `ndots:5` amplification + under-scaled CoreDNS + conntrack pressure. Deploy NodeLocal DNSCache, use FQDNs, scale CoreDNS, raise conntrack limits.

**M4 - Pods can't get IPs: `failed to assign an IP`.**

> VPC CNI IP exhaustion. Enable prefix delegation, add secondary CIDRs, or use larger subnets.

### Hard

**H1 - After a default-deny rollout, app + DNS both break.**

> You blocked egress to kube-dns and ingress from the ingress controller. Add allow rules for UDP/TCP 53 to kube-system and from the ingress-controller namespace. Stage default-deny with these allows _first_.

**H2 - 502s only during deploys; ALB shows targets draining slowly.**

> No graceful shutdown + no readiness gate. SIGTERM kills Pods before deregistration. Add `preStop` sleep, `terminationGracePeriodSeconds`, readiness gates, and align target-group deregistration delay.

**H3 - Cross-AZ latency and a surprising data-transfer bill.**

> Traffic spread randomly across AZs. Enable **topology-aware routing** (`service.kubernetes.io/topology-mode: Auto`), spread replicas per AZ so each zone has local endpoints. Lower latency + cost.

**H4 - A single-replica internal service deadlocks on EKS; readiness never passes.**

> Hairpin self-call via Service. Point readiness at `localhost`, run ≥2 replicas, or verify CNI hairpin support.

**H5 - iptables-mode kube-proxy CPU spikes and rule-sync lag on a 5k-Pod cluster.**

> iptables rule explosion. Switch to **IPVS** or **eBPF (Cilium)**; consider kube-proxy replacement. Sync latency drops dramatically.

[⬆ Back to top](#table-of-contents)

---

## 7. Debug Toolkit (with / without node access)

### Without node access (managed-cluster friendly - EKS default)

```bash
kubectl get endpointslices -l kubernetes.io/service-name=<svc> -o wide   # truth: ready endpoints?
kubectl get pods -l app=<app> -o wide                                    # Ready? IPs?
kubectl describe svc <svc>                                               # ports/targetPort/selector
kubectl run tmp --rm -it --image=curlimages/curl -- sh                   # curl Service + Pod IP
kubectl get netpol -A                                                    # policy blocking?
kubectl -n kube-system logs -l k8s-app=kube-proxy --tail=200             # dataplane health
```

### With node access (deep debugging - self-managed nodes)

```bash
iptables -t nat -L -n | grep -E "KUBE-SVC|KUBE-SEP"   # Service NAT chains
conntrack -L | grep <clusterIP>                       # why is return traffic broken?
ipvsadm -Ln                                           # IPVS tables (IPVS mode)
# Cilium: cilium monitor / cilium service list / cilium endpoint list
```

> On EKS managed nodes you usually can't SSH easily - use SSM Session Manager, or `kubectl debug node/<node>` to get a debugging Pod with host namespaces.

[⬆ Back to top](#table-of-contents)

---

## 8. Runbooks

### Runbook: "Service is down but Pods are Running"

1. `kubectl get endpointslices -l kubernetes.io/service-name=<svc>` - any ready endpoints?
2. Zero → compare selector to Pod labels; check Pod `Ready` + probe events.
3. Probe wrong? Verify path/port and that the app binds `0.0.0.0`.
4. Endpoints exist but curl fails → curl Pod IP directly to split app-vs-dataplane.
5. Pod IP works, Service doesn't → kube-proxy/dataplane/port mapping.
6. Fix → confirm endpoints repopulate → re-curl.

### Runbook: roll out a default-deny NetworkPolicy safely

1. Inventory required flows (app↔app, app↔DB, DNS, ingress, metrics scrape).
2. Apply **allow** rules first (DNS egress, ingress-controller ingress, metrics).
3. Apply default-deny in a non-prod namespace; verify with curl matrix.
4. Roll to prod namespace-by-namespace, watching error rates.
5. Keep an "allow-DNS" policy as a permanent baseline.

[⬆ Back to top](#table-of-contents)

---

## 9. One-Line Recap

> **ClusterIP is virtual; readiness gates traffic via EndpointSlices; zero endpoints = labels/readiness, not networking. Preserve client IP with `Local` or XFF. NetworkPolicy needs an enforcing CNI. On EKS: VPC CNI = real Pod IPs (plan IP space), ALB for L7 / NLB for L4, IP-target mode + readiness gates for zero-downtime, topology-aware routing to cut cross-AZ cost.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [01 - Scheduling & Resources Guide](01%20-%20Scheduling%20%26%20Resources%20Guide.md).
