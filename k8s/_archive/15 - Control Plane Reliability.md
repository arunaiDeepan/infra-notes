### Kubernetes Control Plane Reliability Deep Dive: etcd, API Server, Leader Election, Upgrades, Backups, and Disaster Recovery

Control plane reliability is the difference between “my workloads are down” and “I can’t even _tell_ what my workloads are doing.” When the control plane is sick, Kubernetes becomes a very confident amnesiac.

---

## 1) etcd: the single most important component you don’t want to think about

**What it is:** distributed key-value store holding cluster state.
**Why it’s critical:**

- Every object you create (Pods, Deployments, Secrets, ConfigMaps, RBAC…) lives here.
- API server reads/writes etcd constantly.

### etcd reliability rules (the big ones)

- etcd needs **quorum** to function.
  - With 3 members, you can lose 1 and still have quorum (2/3).
  - With 5 members, you can lose 2 (3/5).
- Odd numbers are standard for fault tolerance.

### Common etcd failure modes

- **Disk latency / saturation**: etcd is extremely sensitive to slow storage.
- **Member down → quorum loss**: cluster becomes effectively read-only or unavailable.
- **Oversized etcd / too many writes**: huge clusters or too-chatty controllers can stress it.
- **Compaction/defrag neglected**: storage bloat and performance degradation.

### What etcd pain looks like

- API requests get slow or time out.
- Controllers fall behind.
- kubectl feels “sticky” or hangs.
- Events show timeouts.
- In worst case: you cannot create/update objects.

Operational musts:

- frequent snapshots/backups
- monitor latency, fsync times, disk IO
- regular compaction/defrag (depending on managed setup)

---

## 2) kube-apiserver: the traffic cop and the brainstem

**What it does:**

- Authn/authz/admission
- Validates and stores objects
- Serves watch streams to controllers, kubelets, clients

### API server failure modes

- **Too many clients watching** (watch storms) or too many LISTs
- **Expensive admission webhooks** (slow webhooks slow everything)
- **etcd slow** (API server is only as fast as etcd)
- **CPU/memory saturation on control plane nodes**
- **Large objects** (giant CRDs, huge annotations, massive ConfigMaps)

### What API server pain looks like

- kubectl commands slow or fail
- controllers can’t reconcile quickly
- node heartbeats fail → nodes become NotReady (secondary failure!)
- HPA and other autoscalers lag

Operational musts:

- monitor API latency (p50/p95/p99)
- watch error rates (429s, 5xx)
- set sane rate limits for clients
- keep admission webhooks fast and highly available (and set timeouts)

---

## 3) Controller Manager and Scheduler: leader-elected brains

Both kube-controller-manager and kube-scheduler typically run multiple replicas for HA, but only one active leader at a time via **leader election**.

**Leader election basics:**

- active leader holds a “lease” object in the API (coordination API)
- if leader dies or can’t renew lease, a standby takes over

### Failure modes

- If API server is flaky, leader election can flap.
- Flapping leaders can cause jitter: reconciliation pauses, scheduling delays.

Signs:

- bursts of “leader changed” messages in logs
- scheduling latency spikes
- controllers lagging behind desired state

Operational musts:

- HA replicas for these components
- stable API server performance so leases renew smoothly

---

## 4) Node heartbeats depend on control plane health

Nodes report status via kubelet to the API server.  
If API server is slow/unreachable:

- nodes stop posting heartbeats
- Node controller marks them NotReady
- pods may get evicted/rescheduled (mass disruption)

This is a nasty emergent behavior:  
**control plane trouble can look like a node outage** and trigger cascading recovery actions.

Operational must:

- treat API server latency as an availability risk, not “just slowness”

---

## 5) Upgrades: the art of changing the plane while flying

Upgrades involve:

- control plane version upgrades
- node upgrades (kubelet, runtime, OS)
- addon upgrades (CNI, CoreDNS, CSI)

### Compatibility rule of thumb

Kubernetes components support limited skew:

- control plane usually must be >= kubelets, within supported skew window.
- don’t jump too many minor versions at once.

### The “safe upgrade” choreography

1. Upgrade control plane first (managed providers usually handle)
2. Upgrade critical addons if required (CNI, CoreDNS, CSI)
3. Roll node pools gradually:
   - cordon + drain nodes
   - respect PDBs
   - monitor error budgets
4. Verify:
   - scheduling works
   - DNS works
   - services still route
   - storage attach/mount still works

Common upgrade breakers:

- CNI incompatibility → pods can’t network
- CoreDNS misconfig → service discovery breaks
- CSI driver issues → volumes won’t mount
- too-strict PDBs → drains stall and upgrades never finish

---

## 6) Backups and Disaster Recovery: what you can and can’t restore

There are two big categories:

### A) Cluster state backups (etcd snapshots)

This restores:

- Kubernetes objects (Deployments, Services, Secrets, RBAC, etc.)  
   It does not automatically restore:
- external cloud resources not represented fully in etcd
- application data inside volumes (unless your volumes have their own backups)

Important nuance:  
etcd snapshot restore is typically “restore a cluster” not “restore a namespace.” It’s heavy.

### B) Application data backups

For stateful workloads:

- you need volume snapshots/backups (CSI snapshots, cloud snapshots)
- plus app-consistent backups (DB dumps, WAL shipping, operator tooling)  
   Because crash-consistent disk snapshots are not always logically consistent.

### DR strategy tiers (practical)

- **Tier 1:** etcd snapshots + restore runbook
- **Tier 2:** add volume snapshot automation for stateful apps
- **Tier 3:** multi-cluster failover (active/passive or active/active), DNS failover, replicated data

The higher the tier, the more you’re doing distributed systems engineering, not just Kubernetes.

---

## 7) The control plane “red flags” you should alert on

- API server p99 latency spikes
- etcd fsync/disk latency high
- rising 429s (rate limiting) or 5xx responses
- controller queue depth/backlog growing
- scheduler scheduling latency
- leader election flapping
- nodes going NotReady in clusters-wide patterns
- admission webhook timeouts/errors

---

## 8) A clean mental model for reliability

- etcd is storage + consensus (disk + quorum)
- API server is the gate (latency here cascades everywhere)
- controllers and scheduler are leader-elected loops that rely on API responsiveness
- nodes depend on the control plane to be healthy enough to accept heartbeats
- upgrades and DR are safe only when you understand these dependencies

---
