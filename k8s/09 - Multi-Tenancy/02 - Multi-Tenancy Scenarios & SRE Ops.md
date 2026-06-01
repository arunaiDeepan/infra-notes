# Multi-Tenancy - Scenarios & SRE Ops

> Enforcing tenant isolation and debugging "one tenant broke everyone." Frequently tested concepts, CKA/CKAD tasks, interview questions, EKS production scenarios, and runbooks. Pair with [01 - Multi-Tenancy Guide](01%20-%20Multi-Tenancy%20Guide.md).

See also: [01 - Multi-Tenancy Guide](01%20-%20Multi-Tenancy%20Guide.md) · [02 - Security & RBAC Scenarios & SRE Ops](02%20-%20Security%20%26%20RBAC%20Scenarios%20%26%20SRE%20Ops.md) · [02 - Scheduling & Resources Scenarios & SRE Ops](02%20-%20Scheduling%20%26%20Resources%20Scenarios%20%26%20SRE%20Ops.md)

---

## Table of Contents

- [1. Frequently Tested Concepts](#1-frequently-tested-concepts)
- [2. Keywords → Cause](#2-keywords--cause)
- [3. CKA/CKAD Practical Tasks](#3-ckackad-practical-tasks)
- [4. Interview Questions](#4-interview-questions)
- [5. EKS Production Scenarios](#5-eks-production-scenarios)
- [6. Runbooks](#6-runbooks)
- [7. One-Line Recap](#7-one-line-recap)

---

## 1. Frequently Tested Concepts

- **Namespace ≠ security boundary** alone; multi-tenancy = RBAC + quota + netpol + PSA.
- **Soft (trusted) vs hard (untrusted)** tenancy.
- **ResourceQuota** (namespace totals) vs **LimitRange** (per-Pod defaults/bounds).
- **Default-deny NetworkPolicy** for east-west isolation.
- **PSA restricted** blocks escapes.
- Hard tenancy → **separate clusters / sandboxed runtimes / Fargate / node pools**.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords → Cause

| Phrase                                 | Points to                                     |
| :------------------------------------- | :-------------------------------------------- |
| "one team's CI melted the cluster"     | No ResourceQuota                              |
| "BestEffort pods everywhere"           | No LimitRange defaults                        |
| "tenants can reach each other's pods"  | No NetworkPolicy                              |
| "tenant ran privileged / mounted host" | No PSA restricted                             |
| "team gave themselves cluster-admin"   | RBAC allows cluster-scoped/bind               |
| "untrusted customer workloads"         | Need hard tenancy (separate clusters/sandbox) |
| "quota exceeded, can't deploy"         | ResourceQuota hit                             |

[⬆ Back to top](#table-of-contents)

---

## 3. CKA/CKAD Practical Tasks

**T1 - Create a namespace with quota + limits:**

```bash
kubectl create ns team-a
kubectl create quota team-a-quota --hard=cpu=20,memory=40Gi,pods=100 -n team-a
# LimitRange via YAML (see Guide)
kubectl describe quota -n team-a
```

**T2 - Namespace-admin RBAC for a team (no cluster scope):**

```bash
kubectl create rolebinding team-a-admin --clusterrole=admin \
  --group=team-a --namespace=team-a    # 'admin' ClusterRole used as a namespaced Role
```

**T3 - Default-deny + allow-DNS (see Services topic for YAML):**

```bash
kubectl label ns team-a pod-security.kubernetes.io/enforce=restricted
kubectl get netpol -n team-a
```

**T4 - Verify a tenant can't touch other namespaces:**

```bash
kubectl auth can-i list secrets -n team-b --as=team-a-user        # want: no
kubectl auth can-i create clusterrolebinding --as=team-a-user      # want: no
```

[⬆ Back to top](#table-of-contents)

---

## 4. Interview Questions

**Q1: Is a namespace a security boundary?**

> No, not alone. It scopes names/RBAC/quota/policy. Real isolation needs RBAC + ResourceQuota/LimitRange + NetworkPolicy + PSA. For untrusted tenants, even that's insufficient - use separate clusters or sandboxed runtimes.

**Q2: ResourceQuota vs LimitRange?**

> Quota caps a namespace's _totals_ (sum of CPU/mem, object counts, storage). LimitRange sets _per-Pod/container_ defaults and min/max. Quota often _requires_ requests/limits to be set - LimitRange supplies the defaults so Pods aren't rejected.

**Q3: How do you isolate tenant network traffic?**

> Default-deny ingress+egress NetworkPolicy per namespace, then explicit allows (DNS, ingress controller, approved shared services). Needs an enforcing CNI.

**Q4: Soft vs hard multi-tenancy - what changes?**

> Soft assumes non-malicious teams (prevent accidents) → namespace controls suffice. Hard assumes malice → separate clusters, sandboxed runtimes (Kata/Fargate), dedicated node pools, mesh mTLS, heavy auditing.

**Q5: A tenant exhausted the cluster. Root cause and fix?**

> No quota → unbounded Pod/resource creation. Add ResourceQuota + LimitRange; alert on quota usage; consider dedicated node pools for noisy tenants.

[⬆ Back to top](#table-of-contents)

---

## 5. EKS Production Scenarios

### Medium

**M1 - A CI job in one namespace spawned 500 Pods and triggered massive Karpenter scale-up (and a bill spike).**

> No ResourceQuota. Add quotas (pods, requests) per namespace; cap `services.loadbalancers`; alert on quota and node count.

**M2 - Tenant Pods can curl another tenant's database.**

> No NetworkPolicy. Roll out default-deny + explicit allows; enable the VPC CNI network-policy agent or Cilium.

**M3 - A tenant deployed a privileged Pod and mounted the host filesystem.**

> No PSA. Label tenant namespaces `restricted`; add a Kyverno policy denying privileged/hostPath.

**M4 - `ResourceQuota` rejects deploys: "must specify requests.cpu."**

> Quota requires requests but Pods set none. Add a LimitRange with defaultRequest so Pods get values automatically.

### Hard

**H1 - Onboarding untrusted customer workloads on a shared cluster.**

> Soft controls aren't enough against malice. Move to **separate EKS clusters per customer** or **Fargate/sandboxed runtimes**, dedicated node pools (taints), strict egress + mesh mTLS, and aggressive audit/GuardDuty monitoring.

**H2 - "Isolated" tenants still suffer cross-tenant latency spikes.**

> They share nodes; noisy-neighbor IO/cache contention. Use dedicated node pools per tenant (taints/affinity), Guaranteed QoS for sensitive workloads, and topology spread. Namespaces don't isolate the kernel/hardware.

**H3 - A PDB/NetworkPolicy with a broad selector blocked an unrelated tenant during maintenance.**

> Shared labels. Enforce unique tenant+component labels; scope every PDB/NetworkPolicy precisely; review selectors in CI policy checks.

**H4 - Audit reveals a tenant repeatedly attempting forbidden actions.**

> Admission denials in audit logs are a tripwire. Alert on denial spikes + RBAC change attempts; review the tenant's intent; tighten RBAC and consider isolating them.

**H5 - Cost attribution impossible across tenants on one cluster.**

> No labeling/tagging discipline. Enforce tenant labels via admission, enable Container Insights + cost allocation tags, and use quotas as cost guardrails; consider per-tenant node pools/clusters for clean billing.

[⬆ Back to top](#table-of-contents)

---

## 6. Runbooks

### Runbook: onboard a new tenant (soft)

1. Create `team-x-dev` / `team-x-prod` namespaces.
2. Apply ResourceQuota + LimitRange.
3. Apply default-deny NetworkPolicy + allow-DNS + ingress-controller allow.
4. Label namespaces `pod-security.kubernetes.io/enforce=restricted`.
5. Create namespace-admin RoleBinding (no cluster scope); dedicated SAs + IRSA roles.
6. Verify with `kubectl auth can-i` matrix; confirm cross-namespace denial.

### Runbook: "a tenant is destabilizing the cluster"

1. Identify the offender: `kubectl top pods -A --sort-by=cpu`, quota usage.
2. Throttle: tighten/enforce ResourceQuota; scale down runaway workloads.
3. Network: confirm NetworkPolicy isn't letting them reach others.
4. If recurring → dedicated node pool (taints) or separate cluster.
5. Add alerts on quota breach and Pod-count spikes.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **A namespace isn't a security boundary alone - multi-tenancy = RBAC + Quota/LimitRange + default-deny NetworkPolicy + PSA restricted + audit. Soft tenancy (trusted) fits one cluster; hard tenancy (untrusted) needs separate clusters, Fargate/sandboxed runtimes, or dedicated node pools. On EKS, IRSA-per-workload + tags make isolation and cost attribution real.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [01 - Observability Guide](01%20-%20Observability%20Guide.md).
