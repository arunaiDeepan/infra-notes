# Control Plane Reliability - Scenarios & SRE Ops

> Keeping the control plane "boring," diagnosing throttling/etcd/heartbeat cascades, and surviving upgrades. Frequently tested concepts, CKA/CKAD tasks, interview questions, EKS production scenarios, and runbooks. Pair with [01 - Control Plane Reliability Guide](01%20-%20Control%20Plane%20Reliability%20Guide.md).

See also: [01 - Control Plane Reliability Guide](01%20-%20Control%20Plane%20Reliability%20Guide.md) · [02 - Incident Response Scenarios & SRE Ops](02%20-%20Incident%20Response%20Scenarios%20%26%20SRE%20Ops.md) · [02 - Multi-Cluster Scenarios & SRE Ops](02%20-%20Multi-Cluster%20Scenarios%20%26%20SRE%20Ops.md)

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

- **etcd needs quorum** (3→lose 1, 5→lose 2); disk-latency sensitive.
- **apiserver latency cascades** → nodes NotReady → mass eviction.
- **Leader election** via Lease; flaps on flaky API.
- **Churn (endpoints/events/status)** is the scale killer; **APF** protects the API.
- **Upgrade order:** control plane → add-ons → nodes; PDBs can stall it.
- **etcd snapshot ≠ app data**; restore is whole-cluster.
- EKS: AWS owns etcd/apiserver; you still cause **429 throttling**.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords → Cause

| Phrase                                  | Points to                               |
| :-------------------------------------- | :-------------------------------------- |
| "kubectl hangs, nodes flip NotReady"    | apiserver/etcd slow (heartbeat cascade) |
| "429 Too Many Requests"                 | API throttling / APF; noisy client      |
| "leader changed repeatedly"             | Leader-election flapping (flaky API)    |
| "etcd database space exceeded"          | No compaction/defrag; object bloat      |
| "upgrade stuck draining"                | Too-strict PDB                          |
| "pods can't network after upgrade"      | CNI version incompatibility             |
| "service discovery broke after upgrade" | CoreDNS add-on skew                     |
| "API CPU high, many watches"            | Watch storm / chatty controller         |

[⬆ Back to top](#table-of-contents)

---

## 3. CKA/CKAD Practical Tasks

**T1 - etcd snapshot save/restore (CKA classic, self-managed):**

```bash
ETCDCTL_API=3 etcdctl snapshot save /backup/snap.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key
ETCDCTL_API=3 etcdctl snapshot restore /backup/snap.db --data-dir /var/lib/etcd-restore
```

**T2 - Check apiserver/control-plane health:**

```bash
kubectl get --raw='/healthz?verbose'
kubectl get --raw='/livez?verbose'
kubectl get events -A --field-selector reason=Throttling
```

**T3 - Inspect leader election leases:**

```bash
kubectl -n kube-system get lease
kubectl -n kube-system get lease kube-scheduler -o yaml | grep holderIdentity
```

**T4 - Find the chatty client (APF):**

```bash
kubectl get --raw='/metrics' | grep apiserver_flowcontrol_rejected_requests_total
kubectl get flowschemas,prioritylevelconfigurations
```

[⬆ Back to top](#table-of-contents)

---

## 4. Interview Questions

**Q1: Why does a slow apiserver cause nodes to go NotReady?**

> Kubelets post heartbeats through the apiserver. If it's slow/unreachable, heartbeats miss, the Node controller marks nodes NotReady, and Pods get evicted - a control-plane problem masquerading as a node outage.

**Q2: How many etcd members for HA and why odd?**

> 3 or 5. Quorum is majority; odd counts maximize fault tolerance per node (3 tolerates 1, 5 tolerates 2) without wasting a member on tie-breaking.

**Q3: What is APF and what problem does it solve?**

> API Priority and Fairness classifies/queues/rate-limits API requests so one noisy controller or tenant can't starve the apiserver - keeps system traffic and interactive kubectl alive under load.

**Q4: Walk through a safe cluster upgrade.**

> Control plane first → compatible add-ons (CNI/CoreDNS/CSI) → node pools gradually (cordon/drain, respect PDBs) → verify scheduling/DNS/routing/storage. Don't skip minors.

**Q5: What does an etcd snapshot restore and what doesn't it?**

> Restores all Kubernetes objects (cluster-wide). Doesn't restore volume _data_ or external cloud resources, and it's whole-cluster, not per-namespace.

**Q6: On EKS, what control-plane reliability work remains yours?**

> Avoiding API throttling (well-behaved clients, lean objects), fast/HA admission webhooks, upgrade ordering, and **app-data DR** - AWS handles etcd/apiserver HA and backups.

[⬆ Back to top](#table-of-contents)

---

## 5. EKS Production Scenarios

### Medium

**M1 - Controllers/CI hit `429 Too Many Requests`.**

> A client is hammering the API. Find it via control-plane audit logs / APF rejection metrics; fix it to use watches+backoff; rely on APF to protect system traffic.

**M2 - Cluster upgrade stuck on a node group.**

> A PDB with `DisruptionsAllowed: 0` blocks drain. Scale the workload to ≥2 or relax the PDB. See [01 - Workload Resilience Guide](01%20-%20Workload%20Resilience%20Guide.md).

**M3 - After upgrade, pods can't get IPs / DNS broke.**

> VPC CNI or CoreDNS add-on version skew. Update managed add-ons to versions matching the new control plane (CNI → CoreDNS → kube-proxy).

**M4 - `kubectl` feels sticky cluster-wide for a few minutes.**

> apiserver pressure (watch storm / large LISTs). Stop bulk `get all -A` during the window; find chatty operators; check EKS apiserver CloudWatch metrics.

### Hard

**H1 - A custom operator writes status every second on 10k CRs; the cluster degrades.**

> etcd write amplification + watch churn. Rate-limit reconciliation, shrink status blobs, batch updates, and reconsider whether each object needs frequent status. APF to protect others.

**H2 - Region/AZ event: are you exposed at the control plane on EKS?**

> EKS control plane already spans 3 AZs (AWS-handled). Your exposure is the **data plane** and **data layer** - multi-AZ node groups, topology spread, multi-AZ datastores. Control-plane HA isn't your job on EKS; data resilience is. See [01 - Reliability Architectures Guide](01%20-%20Reliability%20Architectures%20Guide.md).

**H3 - Self-managed cluster lost etcd quorum (2 of 3 members down).**

> Cluster is read-only/unavailable. Recover members if possible; else restore from the latest snapshot to a new quorum (last resort, whole-cluster). Stop high-write workloads. This pain is a strong argument for managed EKS.

**H4 - A slow validating webhook intermittently stalls all deploys.**

> Webhook on the write path with no HA / long timeout. Make it HA, set a tight `timeoutSeconds`, choose `failurePolicy` deliberately (Fail vs Ignore), and scope it to the resources that need it.

**H5 - Event spam from a CrashLoop storm pressures etcd.**

> Fix the crashing workload (root cause), tune event retention, and ensure controllers aren't amplifying. Churn, not CPU, is melting the control plane.

[⬆ Back to top](#table-of-contents)

---

## 6. Runbooks

### Runbook: "the cluster feels frozen" (EKS)

1. Can you `kubectl get ns`? If not → auth/endpoint/control-plane.
2. Check EKS **control-plane logs** + apiserver CloudWatch metrics + AWS Health.
3. Look for **429s** / APF rejections; identify and throttle the noisy client.
4. Check node readiness for a heartbeat cascade pattern.
5. Once API is healthy, confirm controllers resume (scale a test Deployment).

### Runbook: safe EKS version upgrade

1. Pre-flight: scan for deprecated APIs (`pluto`/`kubent`); audit PDBs.
2. `aws eks update-cluster-version` (control plane).
3. Update managed add-ons (VPC CNI → CoreDNS → kube-proxy) to compatible versions.
4. Roll node groups one AZ/group at a time, respecting PDBs.
5. Verify scheduling, DNS, ingress routing, and volume attach after each step.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **etcd = disk + quorum; apiserver = the gate whose latency cascades to NotReady nodes; controllers/scheduler are leader-elected. Scale dies from churn - protect the API with APF, lean objects, fast HA webhooks. Upgrade control plane → add-ons → nodes (PDBs can stall it). On EKS, AWS owns etcd/apiserver HA + backups; you own client behavior, upgrade ordering, and app-data DR.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [01 - Multi-Cluster Guide](01%20-%20Multi-Cluster%20Guide.md).
