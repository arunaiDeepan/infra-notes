# Kubernetes Interview Q&A

---

## Table of Contents

1. [Kubernetes Cluster Architecture](#1-kubernetes-cluster-architecture)
2. [What happens when you run `kubectl apply` (Pod)](#2-what-happens-when-you-run-kubectl-apply-pod)
3. [Purpose of Services](#3-purpose-of-services-in-kubernetes)
4. [Why hardcoding Pod IPs is bad](#4-why-is-hardcoding-pod-ip-communication-a-bad-practice)
5. [Types of Services](#5-types-of-services-in-kubernetes)
6. [Labels and Selectors](#6-labels-and-selectors)
7. [NodePort vs LoadBalancer recommendation](#7-nodeport-vs-loadbalancer--what-would-you-recommend)
8. [Services and kube-proxy](#8-how-are-services-related-to-kube-proxy)
9. [Disadvantages of LoadBalancer service type](#9-disadvantage-of-loadbalancer-service-type)
10. [Headless Service](#10-headless-service--what-and-when)
11. [Cross-namespace Service access](#11-can-a-pod-access-a-service-in-a-different-namespace)
12. [Restrict DB pod to one app (NetworkPolicy)](#12-restrict-access-to-a-db-pod-to-only-one-app)
13. [Deployment strategy](#13-deployment-strategy-in-your-organization)
14. [Rollback strategy](#14-rollback-strategy-in-your-organization)
15. [Designing to avoid rollbacks](#15-design-a-solution-to-avoid-rollbacks)
16. [Deployment strategies used in the past](#16-deployment-strategies-used-in-the-past)
17. [Role of CoreDNS](#17-role-of-coredns)
18. [Taint `NoSchedule` — can you still schedule?](#18-a-node-is-tainted-noschedule--can-you-still-schedule-a-pod)
19. [CrashLoopBackOff troubleshooting](#19-pod-stuck-in-crashloopbackoff--steps)
20. [Liveness vs Readiness probes](#20-liveness-vs-readiness-probes)
21. [Ingress vs LoadBalancer service](#21-ingress-vs-loadbalancer-service-type)
22. [App works with ClusterIP but fails with Ingress](#22-app-works-with-clusterip-but-fails-with-ingress--troubleshoot)
23. [Why an Ingress controller is needed](#23-why-set-up-an-ingress-controller-after-creating-an-ingress)
24. [In-house load balancer with Ingress](#24-can-we-use-ingress-with-our-in-house-load-balancer)
25. [replicas: 3 but only 1 pod running](#25-replicas-3-but-only-1-pod-running)
26. [ConfigMap changes not reflected](#26-configmap-changes-not-reflected-in-the-pod)
27. [Node Affinity](#27-node-affinity--how-it-works-and-when-to-use)
28. [Node Affinity vs Node Label Selector](#28-node-affinity-vs-nodeselector)
29. [Container runtime](#29-container-runtime-in-kubernetes)
30. [Kubernetes QoS](#30-kubernetes-qos)
31. [Requests and Limits](#31-requests-and-limits)
32. [3 challenges faced with Kubernetes](#32-three-real-challenges-faced-with-kubernetes)
33. [Can we use the master for scheduling pods?](#33-can-we-use-the-master-control-plane-for-scheduling-pods)
34. [Horizontal vs Vertical Scaling](#34-horizontal-vs-vertical-scaling)
35. [Types of Secrets](#35-types-of-secrets-in-kubernetes)

---

## 1. Kubernetes Cluster Architecture

**Theory first.** Kubernetes is a _declarative_ orchestration system. You tell it the **desired state** ("I want 3 replicas of this app"), and a set of controllers continuously work to make the **actual state** match. This is the _reconciliation loop_, and it is the single most important mental model in Kubernetes — everything else is an implementation of it.

A cluster is split into two planes:

### Control Plane (the "brain")

Runs on master node(s). In production you run **3 or 5 control-plane nodes** for HA (odd number for etcd quorum).

| Component                    | Responsibility                                                                                                                                                                                                                             |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **kube-apiserver**           | The front door. The _only_ component that talks to etcd. Everything (kubectl, controllers, kubelet) goes through it. It does authentication, authorization (RBAC), admission control, and validation. Stateless and horizontally scalable. |
| **etcd**                     | Distributed key-value store. The single source of truth — all cluster state lives here. Uses Raft consensus, hence the odd-number quorum requirement. **Back this up.**                                                                    |
| **kube-scheduler**           | Watches for Pods with no node assigned and binds them to a node based on resource requests, affinity, taints/tolerations, topology spread, etc. It only _decides_; it doesn't start the container.                                         |
| **kube-controller-manager**  | Runs the reconciliation loops: Deployment controller, ReplicaSet controller, Node controller, Job controller, endpoints controller, etc. Each watches the API server and drives actual → desired.                                          |
| **cloud-controller-manager** | Integrates with the cloud provider — provisions LoadBalancers, attaches EBS/PD volumes, manages node lifecycle.                                                                                                                            |

### Data Plane / Worker Nodes (the "muscle")

Where your workloads actually run.

| Component             | Responsibility                                                                                                                                                                                           |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **kubelet**           | The node agent. Watches the API server for Pods assigned to its node, then tells the container runtime to start/stop containers. Reports node and pod status back. Runs the probes (liveness/readiness). |
| **container runtime** | Actually runs containers (containerd, CRI-O). Pulls images, sets up namespaces/cgroups.                                                                                                                  |
| **kube-proxy**        | Programs the node's networking (iptables/IPVS) so that Service virtual IPs route to the right backend Pods.                                                                                              |

**One-liner answer for interviews:** _"Kubernetes has a control plane (api-server, etcd, scheduler, controller-manager) that stores and decides desired state, and worker nodes (kubelet, runtime, kube-proxy) that execute it. The api-server is the hub; etcd is the source of truth; controllers reconcile actual state to desired state."_

---

## 2. What happens when you run `kubectl apply` (Pod)

This is the canonical "trace the request" question. Walk it step by step:

1. **kubectl** reads your YAML, converts it to JSON, and sends a REST request (`POST`/`PATCH`) to the **kube-apiserver** over HTTPS, authenticating with your kubeconfig credentials.
2. **api-server** runs the request through:
   - **Authentication** (who are you? — cert/token/OIDC)
   - **Authorization** (RBAC — are you allowed to create pods in this namespace?)
   - **Admission controllers** (mutating, e.g. inject defaults/sidecars; then validating, e.g. policy checks, quota).
3. api-server **persists** the Pod object to **etcd**. At this point the Pod exists but has no node (`spec.nodeName` is empty) and is `Pending`.
4. **kube-scheduler** is _watching_ the api-server. It sees an unscheduled Pod, runs its **filtering** (feasible nodes: enough CPU/mem, tolerates taints, matches affinity) and **scoring** (best node) phases, and writes a **binding** back to the api-server → which updates etcd.
5. The **kubelet** on the chosen node is watching the api-server for pods bound to its node. It sees the new Pod and:
   - Calls the **container runtime** (via CRI) to pull the image and create the container(s).
   - Sets up the **pod sandbox** (network namespace), and the **CNI plugin** assigns the Pod an IP.
   - Mounts volumes, injects ConfigMaps/Secrets, starts containers.
6. kubelet starts running **probes** and continuously **reports status** back to the api-server (`Running`, ready conditions, restart counts), which updates etcd.
7. If the Pod is backed by a Service, the **endpoints/EndpointSlice controller** notices the Pod's labels match a Service selector and adds the Pod IP to the Service's endpoints; **kube-proxy** updates iptables/IPVS so traffic can reach it.

**Key insight to state:** _No component talks directly to another — everything communicates through the api-server using a watch/notify (level-triggered) model. This loose coupling is why Kubernetes is so resilient._

---

## 3. Purpose of Services in Kubernetes

**Theory.** Pods are **ephemeral and fungible**. They die, get rescheduled, scale up/down — and **every time a Pod is recreated it gets a new IP**. If clients pointed at Pod IPs directly, every restart would break them.

A **Service** is a stable abstraction in front of a dynamic set of Pods. It provides:

- **A stable virtual IP (ClusterIP)** and a **stable DNS name** that never change for the life of the Service.
- **Service discovery** — clients resolve `my-svc.my-namespace.svc.cluster.local` instead of tracking Pod IPs.
- **Load balancing** — traffic is spread across all healthy Pods that match the selector.
- **Decoupling** — the front end doesn't need to know how many backend pods exist or where they live.

The Service uses a **label selector** to dynamically determine its backend set (its _endpoints_). As Pods come and go, the endpoints controller keeps the list current automatically.

**One-liner:** _"A Service gives a stable network identity and load balancing to a constantly-changing set of Pods, so clients never have to care about individual Pod IPs."_

---

## 4. Why is hardcoding Pod IP communication a bad practice?

Because it violates everything Pods are designed to be:

1. **Pod IPs are not stable.** A Pod that crashes, gets evicted, is rescheduled to another node, or is rolled during a deployment comes back with a **new IP**. Your hardcoded reference is now pointing at nothing (or worse, a _different_ workload that reused that IP).
2. **No load balancing.** Hardcoding one IP sends all traffic to one Pod — no scaling, no spreading load.
3. **No health awareness.** If that Pod becomes unhealthy, you keep sending traffic to it. A Service only routes to Pods that pass readiness probes.
4. **Breaks horizontal scaling.** Scale to 5 replicas and your hardcoded client still only knows about 1.
5. **Tight coupling / operational nightmare.** Every topology change requires a config change and redeploy of clients.

**The fix:** use a **Service** (stable VIP + DNS) and let kube-proxy + the endpoints controller handle routing to healthy Pods.

---

## 5. Types of Services in Kubernetes

| Type                             | What it does                                                                                                                                           | When to use                                                                               |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------- |
| **ClusterIP** _(default)_        | Exposes the Service on an internal virtual IP, reachable **only inside the cluster**.                                                                  | Internal microservice-to-microservice communication. The default and most common.         |
| **NodePort**                     | Opens a **static port (30000–32767)** on **every node**. Traffic to `NodeIP:NodePort` is forwarded to the Service. Builds on ClusterIP.                | Quick external access, dev/test, or when you put your own LB in front of the nodes.       |
| **LoadBalancer**                 | Provisions an **external cloud load balancer** (ELB/NLB, GCP LB, Azure LB) with a public IP that routes to the NodePort/ClusterIP. Builds on NodePort. | Exposing a service to the internet in a cloud environment. One LB per service.            |
| **ExternalName**                 | Maps the Service to an external DNS name via a **CNAME** record. No proxying, no selector.                                                             | Pointing at an external/managed service (e.g., an RDS endpoint) using an in-cluster name. |
| **Headless** (`clusterIP: None`) | No virtual IP; DNS returns the **Pod IPs directly**.                                                                                                   | StatefulSets, databases, when the client needs to address individual pods.                |

The first three **build on each other**: LoadBalancer → NodePort → ClusterIP.

---

## 6. Labels and Selectors

**Theory.** This is the **glue** of Kubernetes — how loosely-coupled objects find each other.

- **Labels** are key-value pairs attached to objects (`app: payments`, `tier: backend`, `env: prod`). They're metadata used for **identification and grouping**. They are _not_ unique and carry no semantics to Kubernetes itself — you define their meaning.
- **Selectors** are queries that select objects by their labels.

Two selector types:

- **Equality-based:** `app = payments`, `env != staging`.
- **Set-based:** `env in (prod, staging)`, `tier notin (frontend)`, `app` (exists).

**Where they're used (this is the part interviewers want):**

- **Services** select the Pods they route to via `spec.selector`.
- **Deployments/ReplicaSets** track their Pods via `spec.selector.matchLabels`.
- **kubectl** filtering: `kubectl get pods -l app=payments,env=prod`.
- **Node affinity / nodeSelector** uses **node labels**.
- **NetworkPolicies** select pods to apply rules to.

**One-liner:** _"Labels tag objects; selectors query those tags. Services, Deployments, and policies all use selectors to dynamically bind to a set of pods without hardcoding references."_

---

## 7. NodePort vs LoadBalancer — what would you recommend?

**It depends on the environment — and an interviewer wants that nuance.**

**Recommend LoadBalancer when:**

- You're in a **cloud** environment (AWS/GCP/Azure) and need **production internet-facing** access.
- You want a **stable external IP/DNS**, cloud health checks, and TLS offload.
- You don't want to manage the LB yourself.

**Recommend NodePort when:**

- **On-prem / bare metal** with no cloud LB integration (though MetalLB is the better on-prem answer).
- **Dev/test** or internal-only access.
- You already have an **external load balancer** (hardware or your own) and just need an entry port into the cluster.

**My actual recommendation for production HTTP(S):** _neither in isolation — use an **Ingress controller** fronted by a **single LoadBalancer**._ Exposing every service as its own `LoadBalancer` is expensive (one cloud LB per service) and exposing NodePorts directly is insecure and awkward (high ports, no TLS, node-IP coupling). Ingress gives you **host/path routing, TLS termination, and one shared LB** for many services.

**Key downsides to mention:**

- NodePort: high non-standard ports, no built-in TLS, clients must know node IPs, security exposure on every node.
- LoadBalancer: cost and **one LB per service** sprawl.

---

## 8. How are Services related to kube-proxy?

**kube-proxy is the component that makes Services actually work at the network level.**

A Service's ClusterIP is a **virtual IP** — there is no process or interface listening on it. It only "works" because **kube-proxy**, running on every node, programs the kernel's networking to intercept traffic to that VIP and redirect it to a real backend Pod.

Flow:

1. You create a Service → api-server stores it → the **endpoints/EndpointSlice controller** computes the list of Pod IPs matching the selector.
2. **kube-proxy** watches Services and EndpointSlices.
3. For each Service, kube-proxy writes rules into the node's data path:
   - **iptables mode** (default): DNAT rules that rewrite `ClusterIP:port` → a randomly chosen `PodIP:port`.
   - **IPVS mode**: kernel-level L4 load balancer, better at scale (thousands of services) with real LB algorithms (rr, lc, etc.).
4. When a Pod sends traffic to the ClusterIP, the kernel rules rewrite the destination to a healthy backend Pod.

**Important nuance:** kube-proxy does **L4 (TCP/UDP)** load balancing only — it knows nothing about HTTP. Layer-7 routing is Ingress's job. Also note: newer setups can replace kube-proxy entirely with **eBPF (Cilium)** for the same function more efficiently.

**One-liner:** _"kube-proxy turns the abstract Service VIP into real packet-forwarding rules on each node. The Service is the declaration; kube-proxy is the enforcement."_

---

## 9. Disadvantage of LoadBalancer service type

1. **One cloud LB per Service = cost + sprawl.** Each `type: LoadBalancer` provisions a separate cloud load balancer with its own bill and its own public IP. 50 services = 50 LBs. This is the biggest one.
2. **Cloud-provider dependent.** Only works where there's a cloud-controller-manager integration. On bare metal it does nothing without MetalLB.
3. **L4 only by default** — no host/path routing, no native TLS termination, no advanced routing. You'd handle those elsewhere.
4. **Slower to provision / external dependency.** Creating the LB takes time and can fail outside the cluster's control.
5. **Less flexibility** for things like path-based routing, header manipulation, canary by header — all of which Ingress/Gateway API handle.

**The standard production answer:** use **Ingress (or Gateway API)** behind a single LoadBalancer to consolidate cost and gain L7 features.

---

## 10. Headless Service — what and when?

**Theory.** A normal Service gives you **one stable VIP** and load-balances across pods — you don't know or care which pod you hit. Sometimes you need the **opposite**: to address **individual pods** directly and stably.

A **Headless Service** is created by setting `clusterIP: None`. Then:

- Kubernetes assigns **no virtual IP** and does **no proxying/load balancing**.
- A DNS lookup of the Service name returns the **A/AAAA records of all the backing Pod IPs** directly (not a single VIP).
- With a StatefulSet, each pod also gets a **stable per-pod DNS name**: `pod-0.my-svc.ns.svc.cluster.local`.

**When I've used it:**

- **StatefulSets** — databases and clustered systems (Cassandra, Kafka, Elasticsearch, MongoDB, Zookeeper) where each node has a stable identity and peers must discover each other individually.
- **Leader election / peer discovery** — clients need the full list of endpoints, not a load-balanced VIP.
- **Client-side load balancing** — e.g. a gRPC client that wants all backend IPs to manage its own connection pool, instead of L4 round-robin per connection.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: cassandra
spec:
  clusterIP: None # <-- headless
  selector:
    app: cassandra
  ports:
    - port: 9042
```

**One-liner:** _"A headless service skips the VIP and returns pod IPs directly via DNS — used for StatefulSets/databases where you need stable per-pod identity and peer discovery."_

---

## 11. Can a Pod access a Service in a different namespace?

**Yes.** Namespaces are an **organizational/RBAC boundary, not a hard network boundary** (unless a NetworkPolicy enforces one).

Kubernetes DNS gives every Service a **fully qualified domain name (FQDN)**:

```
<service-name>.<namespace>.svc.cluster.local
```

- **Same namespace:** you can use the short name → `payments`.
- **Different namespace:** use the namespace-qualified name → `payments.prod` or the full FQDN `payments.prod.svc.cluster.local`.

Example: a pod in `frontend` namespace reaching a DB service in `data` namespace:

```
postgres.data.svc.cluster.local:5432
```

**Caveats to mention (SRE depth):**

- DNS resolution works cross-namespace by default, but **NetworkPolicies** may block the actual traffic.
- **ExternalName** services and **RBAC** are separate concerns from network reachability.
- The CoreDNS `ndots`/search-domain config is why the short name resolves within a namespace.

---

## 12. Restrict access to a DB pod to only one app

**Use a NetworkPolicy.** By default, Kubernetes networking is **flat and fully open** — any pod can talk to any pod. NetworkPolicies let you implement **micro-segmentation** (zero-trust).

**Critical prerequisite:** NetworkPolicies are enforced by the **CNI plugin**. They do nothing unless your CNI supports them (**Calico, Cilium, Weave** do; the basic flannel does not).

**Strategy:** default-deny ingress to the DB, then allow only the one app by its label.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-allow-only-app
  namespace: myns
spec:
  podSelector:
    matchLabels:
      app: postgres # applies to the DB pods
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: orders-api # ONLY this app may connect
      ports:
        - protocol: TCP
          port: 5432
```

How it works:

- `podSelector` selects the **target** pods the policy protects (the DB).
- The moment a pod is selected by _any_ ingress NetworkPolicy, it becomes **default-deny** for ingress — everything not explicitly allowed is blocked.
- The `from` block whitelists only pods labeled `app: orders-api`.

**SRE extras to mention:**

- Add an explicit **default-deny-all** policy in the namespace as a baseline, then layer allow-rules.
- For cross-namespace, combine `podSelector` with `namespaceSelector`.
- Remember to allow **DNS (UDP/TCP 53 to kube-system)** in egress policies or apps break.

---

## 13. Deployment strategy in your organization

_(Frame this as how you'd run it in production — interviewers want a real, opinionated answer.)_

"We standardize on **rolling updates** as the default for stateless services, and use **canary** (via Argo Rollouts) for high-risk, customer-facing services."

**Rolling Update (default):**

- Kubernetes' native Deployment strategy. New ReplicaSet is scaled up while the old one scales down, governed by `maxSurge` and `maxUnavailable`.
- Zero downtime, gradual replacement, automatic if readiness probes pass.

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 25%
    maxUnavailable: 0 # never drop below desired capacity
```

**Canary (for risky changes):**

- Route a small % of traffic (e.g. 5–10%) to the new version, watch SLOs/error rates/latency (Prometheus), then progressively promote. Implemented with **Argo Rollouts / Flagger** + a service mesh or ingress weighting.
- Automatic rollback if metrics breach thresholds.

**Supporting practices:**

- **GitOps (ArgoCD/Flux)** — Git is the source of truth; deployments are declarative and auditable.
- **Readiness probes + PodDisruptionBudgets** to guarantee capacity during rollout.
- **Progressive delivery gates** tied to real metrics, not just "pod is up."

---

## 14. Rollback strategy in your organization

**Kubernetes-native rollback:**

- Every Deployment update creates a new **ReplicaSet** and a **revision** in its history.
- `kubectl rollout undo deployment/myapp` reverts to the previous ReplicaSet; `--to-revision=N` targets a specific one.
- `kubectl rollout history deployment/myapp` shows revisions (keep enough via `revisionHistoryLimit`).

**How we actually do it (GitOps-aligned):**

1. **Automated rollback on failed rollout** — if readiness probes fail or canary metrics breach thresholds, Argo Rollouts/Flagger **auto-aborts and rolls back** without human action.
2. **Git revert** — since Git is the source of truth, a "rollback" is reverting the commit; ArgoCD reconciles the cluster back to the previous known-good state. This keeps the cluster and Git in sync (a manual `kubectl rollout undo` would drift from Git).
3. **Monitoring-triggered** — alerts on error rate/latency/saturation trigger the rollback runbook.

**Things I always ensure for safe rollbacks:**

- **Backward-compatible database migrations** (expand/contract pattern) — the #1 reason rollbacks fail is a schema change the old code can't read.
- **Immutable image tags** (no `latest`) so a rollback is deterministic.
- Sufficient `revisionHistoryLimit`.

---

## 15. Design a solution to avoid rollbacks

The goal: **catch bad releases before they reach 100% of users**, so a full rollback is rarely needed.

**Layered design:**

1. **Shift-left testing** — strong CI: unit, integration, contract tests, security scans, and a staging environment that mirrors prod.
2. **Progressive delivery (canary / blue-green):**
   - **Blue-Green:** run new version (green) alongside old (blue); flip traffic only after validation; "rollback" is an instant traffic flip back to blue — no pod churn.
   - **Canary:** send 1% → 10% → 50% → 100%, gated on metrics. A bad release is caught at 1% and **automatically aborted**, never reaching most users.
3. **Automated metric analysis** — Argo Rollouts/Flagger query Prometheus for error rate, latency p95/p99, saturation; promotion only proceeds if SLOs hold.
4. **Feature flags** — decouple **deploy** from **release**. Ship code dark, then enable features per-cohort via a flag. A "rollback" becomes toggling a flag (instant, no redeploy).
5. **Backward-compatible changes** — expand/contract DB migrations, additive API changes, so old and new versions coexist safely.
6. **Robust health probes** — readiness gates ensure traffic only hits truly-ready pods.

**One-liner:** _"You don't avoid rollbacks by being careful once — you make releases progressive and reversible: canary + automated metric gates + feature flags + backward-compatible migrations, so a bad change is caught at 1% and flipped off instantly instead of needing a fleet-wide rollback."_

---

## 16. Deployment strategies used in the past

| Strategy               | How it works                                                              | Trade-off                                                                                                                       |
| ---------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **Recreate**           | Kill all old pods, then start new ones.                                   | Simple but **downtime**. OK for non-critical batch/internal apps or when two versions can't coexist (e.g. incompatible schema). |
| **Rolling Update**     | Incrementally replace old pods with new (`maxSurge`/`maxUnavailable`).    | Zero downtime, default, but both versions run simultaneously during rollout.                                                    |
| **Blue-Green**         | Two full environments; switch traffic all at once after validating green. | Instant rollback, no version mixing — but **2× resources** during the switch.                                                   |
| **Canary**             | Gradually shift a % of traffic to the new version, gated on metrics.      | Lowest blast radius, best for risk — but needs traffic-splitting tooling and good observability.                                |
| **A/B testing**        | Route by user attributes (header/cookie/geo) to test variants.            | For product experiments, not just safety; needs L7 routing.                                                                     |
| **Shadow / Mirroring** | Mirror real traffic to the new version without serving its responses.     | Validate under real load with zero user impact; complex to set up.                                                              |

State which you've used: _"Rolling update as the default, blue-green for database-backed services where I wanted an instant flip, and canary with Argo Rollouts for the customer-facing API."_

---

## 17. Role of CoreDNS

**Theory.** CoreDNS is the **cluster DNS server** — it's what makes **service discovery** work. It runs as a Deployment in `kube-system`, fronted by a Service (typically `kube-dns` at a fixed ClusterIP like `10.96.0.10`). Every pod's `/etc/resolv.conf` points at it.

**What it does:**

- Resolves **Service names** → ClusterIPs: `payments.prod.svc.cluster.local` → `10.96.x.x`.
- Resolves **headless service** names → the set of Pod IPs.
- Resolves **per-pod** names for StatefulSets: `db-0.cassandra.data.svc.cluster.local`.
- Forwards **external** queries (google.com) to upstream resolvers.
- Watches the **api-server** for Service/Endpoint changes and updates DNS records dynamically (via the `kubernetes` plugin).

**Why it matters (the search-domain detail):** pod resolv.conf has `search default.svc.cluster.local svc.cluster.local cluster.local` and `ndots:5`. That's why a short name like `payments` resolves within the namespace — CoreDNS + search domains append the suffix.

**SRE reality:** CoreDNS is a **common outage source**. Symptoms like intermittent timeouts often trace to DNS. Tune it: enough replicas, the `cache` plugin, **NodeLocal DNSCache** for high-QPS clusters, and watch for `ndots:5` causing excess lookups for external names.

**One-liner:** _"CoreDNS is the cluster's DNS — it turns stable service names into IPs by watching the api-server, and it's the backbone of service discovery."_

---

## 18. A node is tainted `NoSchedule` — can you still schedule a pod?

**Yes — if the pod has a matching toleration.**

**Theory.** Taints and tolerations are **opposites of node affinity**:

- **Taints** are on **nodes** and **repel** pods ("don't put work here unless it explicitly accepts").
- **Tolerations** are on **pods** and let them **tolerate** a taint ("I'm allowed on that node").

`NoSchedule` means the scheduler **won't place** a pod on that node **unless** the pod tolerates the taint. (It does _not_ evict already-running pods — that's `NoExecute`.)

So a pod **can** be scheduled on the tainted node if its spec includes:

```yaml
tolerations:
  - key: "dedicated"
    operator: "Equal"
    value: "gpu"
    effect: "NoSchedule"
```

**Important nuances (this earns points):**

- A toleration **permits** scheduling onto the tainted node; it does **not force** it. The scheduler can still place the pod elsewhere. To _force_ it onto specific nodes, pair the toleration with **nodeAffinity/nodeSelector**.
- The three taint effects: `NoSchedule` (block new), `PreferNoSchedule` (soft/best-effort avoid), `NoExecute` (block new **and evict** existing non-tolerating pods).
- This is exactly how **control-plane nodes** stay workload-free, and how you reserve **GPU/spot** nodes for specific workloads.

---

## 19. Pod stuck in CrashLoopBackOff — steps

**Theory.** `CrashLoopBackOff` means the container **starts, exits/crashes, and Kubernetes restarts it with exponential backoff** (10s, 20s, 40s … capped at 5 min). It's a **symptom, not a root cause** — the app keeps dying.

**My systematic triage:**

1. **Describe the pod** — events, restart count, last state, exit code, OOMKill:
   ```bash
   kubectl describe pod <pod>
   ```
   Look at `Last State: Terminated`, **Exit Code**, and **Reason** (`OOMKilled`, `Error`).
2. **Read the logs of the crashed container** — the actual error is usually here:
   ```bash
   kubectl logs <pod> --previous   # --previous = the crashed instance
   ```
3. **Interpret the exit code:**
   - `0` → exited cleanly but the entrypoint isn't a long-running process (common misconfig).
   - `1`/`2` → application error (bad config, missing env var, can't reach a dependency).
   - `137` (128+9, SIGKILL) → **OOMKilled** (memory limit too low) or failed liveness probe.
   - `139` (SIGSEGV) → crash/bug.
   - `143` (SIGTERM) → killed.
4. **Common root causes to check:**
   - **OOMKilled** → raise memory limit or fix a leak.
   - **Misconfiguration** → missing/wrong env var, ConfigMap, or Secret; bad command/args.
   - **Failing liveness probe** killing a healthy-but-slow app → fix `initialDelaySeconds`/thresholds.
   - **Dependency not ready** → DB/API unreachable at startup (add retries/init containers).
   - **Bad image / missing binary / permission denied** on the entrypoint.
   - **Read-only FS or volume mount** failure.
5. **Reproduce / inspect interactively** — temporarily override the command to keep it alive and exec in:
   ```bash
   kubectl debug -it <pod> --image=busybox --target=<container>
   # or run the image locally: docker run -it <image> sh
   ```
6. **Check resource & node** — `kubectl top pod`, node pressure, disk.

**One-liner:** _"`describe` for events/exit code, `logs --previous` for the crash reason, then map the exit code (137 = OOM, 1 = app error) to a fix. CrashLoopBackOff is the backoff, not the cause."_

---

## 20. Liveness vs Readiness probes

Both are health checks the **kubelet** runs, but they answer **different questions** and trigger **different actions**. Mixing them up is a classic incident cause.

|                       | **Liveness**                                       | **Readiness**                                                                         |
| --------------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------- |
| **Question**          | "Is the app **alive**, or stuck/deadlocked?"       | "Is the app **ready to serve traffic** right now?"                                    |
| **Action on failure** | **Restarts** the container.                        | **Removes the pod from Service endpoints** (no traffic), but does **not** restart it. |
| **Use case**          | Recover from deadlocks/hangs that a restart fixes. | Hold traffic during startup, warmup, or temporary overload/dependency loss.           |
| **Failure effect**    | Disruptive (kill + restart).                       | Non-disruptive (just stops routing).                                                  |

**Why the distinction matters (SRE war story):**

- A **too-aggressive liveness probe** (short timeout, app slow under load) causes **restart storms** — Kubernetes keeps killing healthy-but-busy pods, making the outage worse. Liveness should only catch _unrecoverable_ states.
- **Readiness** is what gives you **zero-downtime deploys**: a new pod isn't sent traffic until it passes readiness, and a pod losing a dependency stops receiving traffic without being killed.

**Third probe — Startup probe:** for slow-starting apps. It disables liveness/readiness until the app has booted, so a slow start isn't mistaken for a hang. Use it instead of cranking up `initialDelaySeconds`.

```yaml
livenessProbe:
  httpGet: { path: /healthz, port: 8080 }
  initialDelaySeconds: 15
  periodSeconds: 10
readinessProbe:
  httpGet: { path: /ready, port: 8080 }
  periodSeconds: 5
```

**Rule of thumb:** _liveness = restart-worthy deadlocks only; readiness = gate traffic. Keep `/healthz` cheap and don't make liveness depend on downstream services (or one slow dependency restarts your whole fleet)._

---

## 21. Ingress vs LoadBalancer service type

|               | **LoadBalancer (Service)**     | **Ingress**                                      |
| ------------- | ------------------------------ | ------------------------------------------------ |
| **OSI Layer** | **L4** (TCP/UDP)               | **L7** (HTTP/HTTPS)                              |
| **Routing**   | By IP:port only                | By **host** and **URL path**, headers, etc.      |
| **Scope**     | **One LB per service**         | **One LB** fronts **many services**              |
| **TLS**       | Not native (handled elsewhere) | **TLS termination** built in                     |
| **Cost**      | A cloud LB bill per service    | One shared LB                                    |
| **Needs**     | Cloud provider                 | An **Ingress controller** (nginx, Traefik, etc.) |

**Theory.** A `LoadBalancer` service is the simplest way to get external L4 traffic to one service. **Ingress** is an **L7 router**: a single entry point that inspects HTTP requests and routes `api.example.com/orders` → orders-svc and `api.example.com/users` → users-svc, with TLS, all behind **one** load balancer.

**Practical:** in production you almost always front HTTP services with **Ingress** (one LB, host/path routing, TLS) rather than giving each service its own LoadBalancer. Note Ingress itself is usually _exposed_ via a single `LoadBalancer` service in front of the ingress controller.

**Modern note:** the **Gateway API** is the evolving successor to Ingress — more expressive, role-oriented, supports TCP/gRPC/traffic-splitting natively.

---

## 22. App works with ClusterIP but fails with Ingress — troubleshoot

The app is fine internally; the problem is in the **Ingress → Service** path. Work it layer by layer:

1. **Is an Ingress controller installed and running?** Ingress objects do nothing without a controller. Check:
   ```bash
   kubectl get pods -n ingress-nginx
   kubectl get ingressclass
   ```
2. **Does the Ingress reference the right `ingressClassName`?** A mismatch means no controller picks it up.
3. **Does the Ingress backend point to the correct Service name AND port?** This is the #1 cause. The Ingress `service.port.number` must match the **Service port**, not the container port:
   ```bash
   kubectl describe ingress <name>
   kubectl get svc <backend-svc>
   ```
4. **Does the Service have endpoints?** If the selector is wrong, the Service has no backends even if ClusterIP "exists":
   ```bash
   kubectl get endpoints <svc>   # empty = selector/label mismatch or no ready pods
   ```
5. **DNS / host header** — does the request's `Host` match the Ingress `rules.host`? Is DNS pointing at the ingress LB's IP? Test bypassing DNS:
   ```bash
   curl -H "Host: app.example.com" http://<ingress-LB-IP>/
   ```
6. **Path / rewrite rules** — `pathType` (`Prefix` vs `Exact`) and rewrite annotations frequently cause 404s.
7. **TLS / cert issues** — bad/missing secret → 502/handshake errors. Check the referenced TLS secret exists.
8. **Controller logs** — the ground truth:
   ```bash
   kubectl logs -n ingress-nginx <controller-pod>
   ```
9. **NetworkPolicy** — a policy might block traffic from the ingress-controller namespace to your pods.

**Mental model to state:** _"ClusterIP working proves the pods and service selector are fine. So the break is in the new layer: controller present? ingressClass matched? backend svc/port correct? endpoints populated? host/path/TLS right? Controller logs tell you which."_

---

## 23. Why set up an Ingress controller after creating an Ingress?

Because an **Ingress object is just data — a set of routing rules stored in etcd. It does nothing by itself.** Something has to **read those rules and actually implement them.** That something is the **Ingress controller**.

**Theory — declaration vs implementation:**

- The **Ingress resource** declares _desired_ routing ("`/api` → api-svc, terminate TLS with this cert").
- The **Ingress controller** (nginx, Traefik, HAProxy, AWS ALB controller, Contour) is a running pod that **watches** the api-server for Ingress objects and **configures a real proxy/load balancer** to enforce them.

Kubernetes ships with the **Ingress API** but, by design, **no built-in controller** — you choose and install one. Without it, you can `kubectl apply` an Ingress all day and **zero traffic flows**, because nothing translated the rules into an actual reverse proxy config.

**Analogy:** the Ingress is the **blueprint**; the controller is the **builder**. A blueprint with no builder builds no house.

---

## 24. Can we use Ingress with our in-house load balancer?

**Yes.** This is a common on-prem / hybrid pattern. The key is understanding the **two layers**:

- **Layer 1 (your in-house LB):** sits at the edge, terminates external traffic, and forwards to the cluster.
- **Layer 2 (Ingress controller inside the cluster):** does the L7 host/path routing to services.

**How to wire it up:**

1. **Deploy an Ingress controller** (nginx/Traefik/HAProxy) inside the cluster.
2. **Expose the controller** so your LB can reach it — via **NodePort** (your LB points at `NodeIP:NodePort` across the worker nodes) or via a bare-metal LB integration like **MetalLB**.
3. **Point your in-house load balancer** at those node IPs/ports (with health checks). It becomes the external entry; the Ingress controller does the routing.

```
Internet → In-house LB → NodePort → Ingress Controller (nginx) → Service (ClusterIP) → Pods
```

**Considerations to raise:**

- **Health checks** on the LB should target the ingress controller's health endpoint.
- **Preserve client IP** — use `externalTrafficPolicy: Local` and/or PROXY protocol so the app sees the real source IP, not the node's.
- **TLS** — decide whether to terminate at the in-house LB or pass through to the ingress controller.
- This decouples you from cloud LB dependency — exactly why on-prem clusters use **MetalLB** + nginx-ingress.

---

## 25. `replicas: 3` but only 1 pod running

The Deployment wants 3 but only got 1 — so **2 pods can't be created or can't become ready.** Diagnose:

```bash
kubectl get deploy,rs,pods
kubectl describe rs <replicaset>     # creation-level errors
kubectl describe pod <pending-pod>   # scheduling/runtime errors
kubectl get events --sort-by=.lastTimestamp
```

**Most common causes:**

1. **Insufficient resources** — no node has enough CPU/memory to satisfy the pods' **requests**. Pods stay `Pending` with `FailedScheduling: Insufficient cpu/memory`. → add nodes / cluster autoscaler / lower requests.
2. **Node selectors / affinity / taints** — pods require a label or can't tolerate taints, so no feasible node. `0/N nodes are available: node(s) didn't match...`.
3. **Pod anti-affinity / topology spread** — e.g. "one pod per node" but only 1 eligible node → the rest can't place.
4. **ResourceQuota / LimitRange** — namespace quota exhausted; the ReplicaSet is `forbidden` from creating more pods (check `describe rs`).
5. **Image pull failure** on the others — `ImagePullBackOff` (rate limits, wrong tag, missing registry secret).
6. **PVC unbound** — pods waiting on a volume that can't be provisioned/attached (e.g. zone mismatch, single-AZ EBS).
7. **Failing readiness probes** — pods are _Running_ but not _Ready_, so they don't count as available.
8. **Insufficient IPs** — CNI exhausted the node/subnet IP pool.

**Process:** `describe rs` tells you if creation is blocked (quota/forbidden); `describe pod` + events tell you if scheduling or startup is blocked (resources/affinity/image/PVC). Match the message to the cause.

---

## 26. ConfigMap changes not reflected in the pod

**Theory — depends on how the ConfigMap is consumed:**

1. **Mounted as env vars (`envFrom`/`valueFrom`):** env vars are injected **once at container start** and are **immutable for the life of the process**. Editing the ConfigMap does **nothing** until the pod restarts. → **You must restart/roll the pods.**
2. **Mounted as a volume:** the kubelet **does** update the mounted files automatically — but with a **delay** (kubelet sync period + cache TTL, up to ~1–2 minutes), and **only the files change**. Your **application won't notice** unless it watches the file / supports hot-reload. The process keeps using the old value in memory.

**So the two failure modes are:** env-var consumption (never updates without restart) and app-doesn't-reload (file updated, app ignored it).

**Solutions:**

- **Restart the workload** to pick up changes:
  ```bash
  kubectl rollout restart deployment/myapp
  ```
- **Make changes trigger a rollout automatically** — **checksum/hash annotation** pattern: put a hash of the ConfigMap in the pod template annotations, so any change updates the template → triggers a rolling update. (Helm `sha256sum` annotation; Kustomize **`configMapGenerator`** appends a hash suffix and treats configmaps as immutable, forcing a roll.)
- **App-level hot reload** — have the app watch the mounted file (e.g. nginx `-s reload`, or a sidecar like **Reloader** that watches ConfigMaps/Secrets and restarts dependent deployments).
- **Immutable ConfigMaps** (`immutable: true`) — best practice for performance and to force the "new name → new rollout" discipline.

**One-liner:** _"Env-var ConfigMaps never update without a restart; volume-mounted ones update the file after a delay but the app must reload it. Fix: `rollout restart`, or hash-annotation/Kustomize generator to force a roll, or a Reloader sidecar."_

---

## 27. Node Affinity — how it works and when to use

**Theory.** Node affinity is the **expressive successor to `nodeSelector`** — it controls **which nodes a pod is allowed/preferred to run on**, based on **node labels**.

Two flavors:

- **`requiredDuringSchedulingIgnoredDuringExecution`** — a **hard** rule. The pod **won't schedule** unless a node matches. (`IgnoredDuringExecution` = if labels change later, running pods aren't evicted.)
- **`preferredDuringSchedulingIgnoredDuringExecution`** — a **soft** rule with a `weight`. The scheduler **tries** to honor it but will place the pod elsewhere if needed.

```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - key: disktype
              operator: In
              values: ["ssd"]
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 80
        preference:
          matchExpressions:
            - key: topology.kubernetes.io/zone
              operator: In
              values: ["us-east-1a"]
```

**When I use it:**

- **Hardware targeting** — GPU jobs onto GPU nodes, memory-heavy apps onto high-mem nodes, SSD-requiring workloads onto SSD nodes.
- **Zone/topology placement** — keep latency-sensitive pods in a specific AZ, or steer cost-tolerant workloads onto **spot** instances.
- **Compliance/isolation** — pin regulated workloads to specific node pools.
- **Soft preferences** — "prefer this zone but don't fail if it's full."

**Related concepts to mention:** **Pod affinity/anti-affinity** (place pods relative to _other pods_, e.g. spread replicas across nodes), and **taints/tolerations** (the _repelling_ counterpart).

---

## 28. Node Affinity vs nodeSelector

Both place pods based on **node labels**, but differ in **expressiveness**:

|                  | **nodeSelector**                               | **Node Affinity**                                          |
| ---------------- | ---------------------------------------------- | ---------------------------------------------------------- |
| **Syntax**       | Simple key-value map; **all must match** (AND) | Rich `matchExpressions`                                    |
| **Operators**    | Equality only                                  | `In`, `NotIn`, `Exists`, `DoesNotExist`, `Gt`, `Lt`        |
| **Hard vs soft** | Hard only                                      | **Both** hard (`required`) and soft (`preferred` + weight) |
| **Logic**        | AND only                                       | OR (multiple terms), negation, ranges                      |
| **Status**       | Legacy, simplest                               | Superset, recommended                                      |

```yaml
# nodeSelector — simple, hard, equality only
nodeSelector:
  disktype: ssd
```

**Key takeaways:**

- `nodeSelector` is **a strict subset** of node affinity — anything it does, affinity can do.
- Use **`nodeSelector`** for trivial "must be on nodes with label X" cases — it's readable.
- Use **node affinity** when you need **soft preferences**, **negation** (`NotIn`/`DoesNotExist`), **OR logic**, or ranges — e.g. "prefer SSD, but spot is acceptable" — which `nodeSelector` simply can't express.

**One-liner:** _"nodeSelector is hard, AND-only, equality-only. Node affinity is the superset: soft preferences with weights, set operators, negation, and OR. Reach for affinity whenever 'must equal' isn't enough."_

---

## 29. Container runtime in Kubernetes

**Theory.** The **container runtime** is the software that **actually runs containers** on a node — pulling images, unpacking them, and creating the Linux **namespaces + cgroups** that isolate and limit the process. Kubernetes orchestrates; the runtime executes.

**The CRI (Container Runtime Interface):** Kubernetes doesn't hardcode a runtime. The **kubelet** talks to whatever runtime implements the **CRI** gRPC API. This pluggability is why the ecosystem could move off Docker.

**Common runtimes:**

- **containerd** — the de-facto default (graduated CNCF project, extracted from Docker). Lightweight, CRI-native.
- **CRI-O** — purpose-built for Kubernetes (OpenShift default).
- **Docker (dockershim)** — **removed in Kubernetes 1.24**. Docker wasn't CRI-native, so the kubelet used a shim; that was deprecated and dropped. (Docker _images_ still work fine — they're just OCI images; "Docker the runtime" is what went away.)

**Layered picture (good to mention):**

- **High-level runtime** (containerd/CRI-O) — manages image pull, lifecycle, CRI.
- **Low-level runtime** (**runc** — OCI runtime) — does the actual `clone()`/namespaces/cgroups syscalls.
- **Sandboxed runtimes** — **gVisor**, **Kata Containers** for stronger isolation (multi-tenant security).

**One-liner:** _"The container runtime runs containers via namespaces/cgroups. The kubelet talks to it over the CRI, so it's pluggable — containerd is the default since Docker/dockershim was removed in 1.24."_

---

## 30. Kubernetes QoS

**Theory.** **Quality of Service (QoS) classes** determine a pod's **eviction priority** when a node runs out of resources (memory pressure). Kubernetes **assigns** the class automatically based on how you set **requests and limits** — you don't set QoS directly.

Three classes, from most to least protected:

| QoS Class      | Condition                                                                                                                 | Eviction behavior                                        |
| -------------- | ------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| **Guaranteed** | Every container has **requests == limits** for **both CPU and memory** (and both are set).                                | **Last to be evicted.** Highest priority.                |
| **Burstable**  | At least one container has a request/limit set, but **not** equal across the board (requests < limits, or only some set). | Evicted **after** BestEffort, before Guaranteed.         |
| **BestEffort** | **No** requests or limits set on **any** container.                                                                       | **First to be evicted** under pressure. Lowest priority. |

**Why it matters (SRE angle):**

- Under **node memory pressure**, the kubelet evicts **BestEffort first**, then **Burstable** (those most over their requests), protecting **Guaranteed** pods.
- For **critical production workloads** (databases, core services), set **requests == limits** → **Guaranteed** → they're protected from eviction and get more predictable performance.
- It also influences the **OOM score** — BestEffort/Burstable containers are killed first by the kernel OOM killer when memory is exhausted.

**One-liner:** _"QoS (Guaranteed/Burstable/BestEffort) is auto-derived from requests vs limits and decides eviction order under pressure. Set requests == limits for critical pods to make them Guaranteed and last-to-be-evicted."_

---

## 31. Requests and Limits

**Theory.** This is how you tell Kubernetes a container's resource needs. Both matter for **scheduling**, **stability**, and **fairness**.

- **Request** = the **guaranteed minimum** a container is allocated. The **scheduler uses requests** to decide which node has room (it sums requests, not actual usage). The container is _guaranteed_ at least this much.
- **Limit** = the **hard ceiling** the container may use. The **kubelet/runtime enforces** it at runtime.

**Behavior differs by resource type — crucial detail:**

|                    | **CPU** (compressible)                   | **Memory** (incompressible)                             |
| ------------------ | ---------------------------------------- | ------------------------------------------------------- |
| **Over the limit** | **Throttled** — slowed down, not killed. | **OOMKilled** — the container is terminated (exit 137). |
| Why                | CPU can be reclaimed instantly.          | Memory can't be taken back; the only option is to kill. |

```yaml
resources:
  requests:
    cpu: "250m" # 0.25 core guaranteed
    memory: "256Mi"
  limits:
    cpu: "500m" # throttled above this
    memory: "512Mi" # OOMKilled above this
```

**SRE guidance (this is what separates a good answer):**

- **Always set memory requests AND limits** — an unbounded container can consume all node memory and take down neighbors ("noisy neighbor"). Memory request == limit is safest for critical apps.
- **Be careful with CPU limits.** Aggressive CPU limits cause **throttling** that hurts latency even when the node has spare CPU. Many SRE teams **set CPU requests but omit CPU limits** (or set them generously) to avoid throttling, while still setting memory limits firmly.
- Requests drive **scheduling and QoS**; limits drive **enforcement**. Setting them well prevents both over-commit outages and wasted capacity.
- Use **VPA recommendations** / historical metrics to right-size rather than guessing.

---

## 32. Three real challenges faced with Kubernetes

_(Frame as concrete, with root cause + fix — interviewers want lived experience.)_

**1. DNS / CoreDNS intermittent failures at scale.**

- _Symptom:_ sporadic connection timeouts, slow requests, "name resolution failed" under load.
- _Root cause:_ `ndots:5` causing excessive DNS lookups for external names, CoreDNS pods under-provisioned, and the classic Linux conntrack race on UDP DNS.
- _Fix:_ deployed **NodeLocal DNSCache**, scaled CoreDNS with the cache plugin, used FQDNs (trailing dot) for hot external endpoints to skip search-domain expansion, and tuned conntrack. Reliability and tail latency improved sharply.

**2. OOMKills and resource mis-sizing causing cascading failures.**

- _Symptom:_ pods restarting (exit 137), and a memory-hungry pod with no limits starving co-located pods.
- _Root cause:_ missing/under-set memory requests & limits → bad scheduling decisions and noisy-neighbor evictions.
- _Fix:_ set proper **requests/limits**, made critical workloads **Guaranteed QoS**, added **VPA recommendations** to right-size, and used **PodDisruptionBudgets** to protect availability during evictions.

**3. Failed/risky rollouts breaking production.**

- _Symptom:_ a deploy passed "pods are up" but the app was broken; rollback failed because a DB migration wasn't backward compatible.
- _Root cause:_ readiness probe too shallow, no progressive delivery, non-reversible schema change.
- _Fix:_ introduced **canary deployments with Argo Rollouts** + automated metric gates (Prometheus), enforced **expand/contract migrations**, **immutable image tags**, and GitOps (ArgoCD) so rollback = git revert. Bad releases now caught at small traffic % and auto-aborted.

_(Other strong options: stuck PVs/volume attach issues across AZs, network policy misconfig blocking traffic, ingress/TLS cert renewal failures, node autoscaler thrashing, etcd performance/backup.)_

---

## 33. Can we use the master (control plane) for scheduling pods?

**Theory.** By default, **control-plane nodes are tainted** to **prevent** regular workloads from being scheduled on them:

```
node-role.kubernetes.io/control-plane:NoSchedule
```

This **protects the control plane** — you don't want a runaway app starving the api-server/etcd of CPU/memory and taking down the whole cluster.

**Can you still schedule there? Yes, two ways:**

1. **Add a matching toleration** to the pod so it tolerates the control-plane taint (this is how control-plane components and some DaemonSets like CNI/kube-proxy _do_ run there).
2. **Remove the taint** (not recommended for prod):
   ```bash
   kubectl taint nodes <master> node-role.kubernetes.io/control-plane:NoSchedule-
   ```

**Should you? Generally NO in production.** Best practice keeps the control plane **dedicated and isolated** for stability and security. The **exception** is **single-node clusters** (minikube, k3s, kind, edge/dev) where you have no choice — there the taint is removed so workloads can run.

**One-liner:** _"Technically yes — control-plane nodes are just tainted `NoSchedule`, so a toleration or removing the taint lets pods run there. But in production you keep them dedicated to protect etcd/api-server; only single-node/dev clusters intentionally schedule workloads on the master."_

---

## 34. Horizontal vs Vertical Scaling

**Theory — the fundamental distinction:**

- **Horizontal scaling (scale out/in):** add or remove **more instances** (pods/nodes).
- **Vertical scaling (scale up/down):** add or remove **resources to an existing instance** (more CPU/RAM per pod/node).

|                   | **Horizontal**                                             | **Vertical**                                         |
| ----------------- | ---------------------------------------------------------- | ---------------------------------------------------- |
| **What changes**  | Number of replicas                                         | Resources per replica                                |
| **K8s mechanism** | **HPA** (Horizontal Pod Autoscaler)                        | **VPA** (Vertical Pod Autoscaler)                    |
| **Triggers on**   | CPU/memory/custom/external metrics                         | Historical usage recommendations                     |
| **Disruption**    | None — add pods live                                       | Often **requires pod restart** to apply new requests |
| **Ceiling**       | Limited by cluster capacity (pair with Cluster Autoscaler) | Limited by the **biggest single node**               |
| **Best for**      | **Stateless** web/API services                             | Stateful/singletons that can't be sharded (some DBs) |

**Kubernetes specifics:**

- **HPA** — adjusts `replicas` based on observed metrics. The default, ideal for **stateless** apps. Pairs with the **Cluster Autoscaler** (which adds _nodes_ when pods can't schedule).
- **VPA** — recommends/sets right-sized requests & limits. Great for right-sizing, but typically **recreates the pod** to apply changes (in-place resize is improving in newer K8s). **Don't run HPA and VPA on the same metric** — they fight.
- **Cluster Autoscaler / Karpenter** — horizontal scaling at the **node** level.

**Trade-offs (general theory):**

- Horizontal: better **fault tolerance** (no single point of failure), near-limitless scale, but needs the app to be **stateless/shardable** and adds distributed-system complexity.
- Vertical: simpler (no app changes), but has a **hard ceiling** (one machine's max), and scaling usually means **downtime/restart** — a single point of failure remains.

**One-liner:** _"Horizontal = more pods (HPA + Cluster Autoscaler), best for stateless apps and fault tolerance. Vertical = bigger pods (VPA), best for workloads you can't shard, but capped by node size and usually needs a restart. Prefer horizontal in Kubernetes."_

---

## 35. Types of Secrets in Kubernetes

**Theory.** A **Secret** stores small amounts of sensitive data (passwords, tokens, keys, certs). Critical caveat to always state: **by default Secrets are only base64-encoded, NOT encrypted** — anyone with API/etcd access can read them. You must add real protection.

**Built-in Secret types (`type` field):**

| Type                                      | Purpose                                                               |
| ----------------------------------------- | --------------------------------------------------------------------- |
| **`Opaque`**                              | Default, arbitrary user-defined key-value data (passwords, API keys). |
| **`kubernetes.io/service-account-token`** | Token for a ServiceAccount to authenticate to the API server.         |
| **`kubernetes.io/dockerconfigjson`**      | Registry credentials for pulling private images (`imagePullSecrets`). |
| **`kubernetes.io/dockercfg`**             | Legacy form of registry credentials.                                  |
| **`kubernetes.io/basic-auth`**            | Username/password for basic auth.                                     |
| **`kubernetes.io/ssh-auth`**              | SSH private key.                                                      |
| **`kubernetes.io/tls`**                   | TLS cert + private key (used by Ingress for HTTPS).                   |
| **`bootstrap.kubernetes.io/token`**       | Bootstrap tokens for new nodes joining the cluster.                   |

**How Secrets are consumed by pods:**

- As **environment variables** (`valueFrom.secretKeyRef`).
- As **mounted volume files** (preferred — supports rotation, doesn't leak into env/`/proc`).
- As **`imagePullSecrets`** for private registries.

**SRE security best practices (this is what earns the answer):**

- **Enable encryption at rest** for etcd (`EncryptionConfiguration`) — otherwise secrets sit base64 in etcd.
- **RBAC** — tightly restrict who/what can `get`/`list` secrets.
- **External secret managers** — **HashiCorp Vault**, **AWS/GCP/Azure Secret Manager** via the **External Secrets Operator** or **Secrets Store CSI driver**, so secrets aren't stored in etcd/Git at all.
- **Never commit secrets to Git** — use **Sealed Secrets** (encrypted, safe to commit) or SOPS for GitOps.
- Prefer **volume mounts over env vars** (env vars can leak via logs, crash dumps, child processes).
- Enable **audit logging** on secret access.

**One-liner:** _"Several built-in types (Opaque, tls, dockerconfigjson, service-account-token, basic-auth, ssh-auth…). The headline is that Secrets are only base64-encoded by default — in production you enable etcd encryption-at-rest, lock down RBAC, mount as files, and ideally externalize to Vault/cloud secret managers."_

---

> **Final interview tip:** for every "what is X" question, also say **why it exists** (the problem it solves) and **how you'd operate it in production** (the trade-off / gotcha). That's what distinguishes an SRE answer from a textbook definition.
