# StatefulSets & Storage - Scenarios & SRE Ops

> Debugging stuck mounts, AZ-pinned volumes, and "the DB didn't fail over." Frequently tested concepts, CKA/CKAD tasks, interview questions, EKS production scenarios, diagnostics, and runbooks. Pair with [01 - StatefulSets & Storage Guide](01%20-%20StatefulSets%20%26%20Storage%20Guide.md).

See also: [01 - StatefulSets & Storage Guide](01%20-%20StatefulSets%20%26%20Storage%20Guide.md) · [02 - Workload Resilience Scenarios & SRE Ops](02%20-%20Workload%20Resilience%20Scenarios%20%26%20SRE%20Ops.md) · [02 - Reliability Architectures Scenarios & SRE Ops](02%20-%20Reliability%20Architectures%20Scenarios%20%26%20SRE%20Ops.md)

---

## Table of Contents

- [1. Frequently Tested Concepts](#1-frequently-tested-concepts)
- [2. Keywords → Cause](#2-keywords--cause)
- [3. CKA/CKAD Practical Tasks](#3-ckackad-practical-tasks)
- [4. Interview Questions](#4-interview-questions)
- [5. EKS Production Scenarios](#5-eks-production-scenarios)
- [6. Diagnostic Commands](#6-diagnostic-commands)
- [7. Runbooks](#7-runbooks)
- [8. One-Line Recap](#8-one-line-recap)

---

## 1. Frequently Tested Concepts

- **StatefulSet = stable identity + per-Pod PVC + ordered ops + headless DNS.**
- **PVC ↔ Pod identity is sticky** (`data-mydb-0`).
- **EBS is RWO + zonal**; **EFS is RWX + multi-AZ**.
- **`WaitForFirstConsumer`** places the volume in the Pod's AZ.
- **reclaimPolicy Retain vs Delete** = keep vs destroy the disk.
- **Stateful ≠ HA**; need replicas + app replication + backups.
- **`OnDelete`** for safe DB upgrades.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords → Cause

| Phrase                                       | Points to                                    |
| :------------------------------------------- | :------------------------------------------- |
| "Multi-Attach error / volume in use"         | EBS RWO still attached to old/dead node      |
| "Pod Pending, volume node affinity conflict" | EBS in AZ-a, no node in AZ-a                 |
| "deleted PVC, disk vanished"                 | `reclaimPolicy: Delete`                      |
| "disks pile up / never freed"                | `reclaimPolicy: Retain` + no cleanup         |
| "DB didn't fail over after node death"       | App-level replication/leader election needed |
| "all replicas on one node died"              | No anti-affinity / topology spread           |
| "rollout broke the DB cluster"               | RollingUpdate too fast; use OnDelete         |
| "can't mount RWO on 2 pods"                  | Wrong access mode (need RWX/EFS)             |

[⬆ Back to top](#table-of-contents)

---

## 3. CKA/CKAD Practical Tasks

**T1 - See identity ↔ storage mapping:**

```bash
kubectl get sts
kubectl get pods -l app=mydb -o wide
kubectl get pvc | grep mydb
kubectl describe pvc data-mydb-0
```

**T2 - StatefulSet with volumeClaimTemplates (CKAD):**

```yaml
apiVersion: apps/v1
kind: StatefulSet
spec:
  serviceName: mydb # headless service
  replicas: 3
  volumeClaimTemplates:
    - metadata: { name: data }
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: ebs-gp3
        resources: { requests: { storage: 20Gi } }
```

**T3 - StorageClass for EBS with correct AZ binding:**

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata: { name: ebs-gp3 }
provisioner: ebs.csi.aws.com
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
parameters: { type: gp3 }
```

**T4 - Expand a PVC:**

```bash
kubectl patch pvc data-mydb-0 -p '{"spec":{"resources":{"requests":{"storage":"40Gi"}}}}'
```

**T5 - Diagnose a mount failure (the smoking gun is in events):**

```bash
kubectl describe pod mydb-0 | sed -n '/Events/,$p'
```

[⬆ Back to top](#table-of-contents)

---

## 4. Interview Questions

**Q1: Deployment vs StatefulSet - when and why?**

> Deployment for interchangeable stateless replicas; StatefulSet when Pods need stable identity, stable per-Pod storage, stable DNS, and/or ordered lifecycle (databases, queues, consensus systems).

**Q2: What does a StatefulSet NOT give you?**

> Data correctness, leader election, and HA. Those are app/operator responsibilities. A 1-replica StatefulSet is still a SPOF.

**Q3: Why is my stateful Pod Pending after a node failure on EKS?**

> Its EBS volume is zonal; if no node exists in that AZ (or the volume hasn't detached from the dead node), it can't schedule. Spread nodes across AZs, use `WaitForFirstConsumer`, and let detach/force-detach complete.

**Q4: EBS vs EFS for Kubernetes storage?**

> EBS: block, RWO, single-AZ, low latency - DB data. EFS: NFS, RWX, multi-AZ, higher latency - shared files and reschedule flexibility.

**Q5: How do you safely upgrade a database StatefulSet?**

> `OnDelete` or partitioned RollingUpdate, one Pod at a time, coordinated with the DB's upgrade/failover procedure; verify replication caught up before the next.

**Q6: reclaimPolicy Retain vs Delete - operational impact?**

> Delete destroys the underlying disk with the PVC (data loss risk); Retain keeps it (manual cleanup, disk leakage risk). Choose per data value.

[⬆ Back to top](#table-of-contents)

---

## 5. EKS Production Scenarios

### Medium

**M1 - Pod stuck `ContainerCreating`: `Multi-Attach error for volume ... already exclusively attached`.**

> EBS RWO volume still attached to a dead/old node. Wait for detach, or force-detach the EBS volume; ensure only one Pod uses the RWO PVC. Common after ungraceful node loss.

**M2 - Stateful Pod `Pending`: `volume node affinity conflict`.**

> EBS volume is in AZ-a but the scheduler wants AZ-b (no AZ-a node). Add nodes in that AZ, or use `WaitForFirstConsumer` so future volumes follow Pods.

**M3 - Someone deleted a PVC and the data is gone.**

> `reclaimPolicy: Delete`. Switch precious classes to `Retain`, enable VolumeSnapshots/AWS Backup, and restrict PVC delete via RBAC.

**M4 - Two Pods need the same files; mount fails.**

> RWO can't be shared across nodes. Use **EFS (RWX)** for shared filesystems.

### Hard

**H1 - A node dies; the database StatefulSet comes back but serves stale/empty data.**

> Either local storage (data lost) or the DB needs replication/leader re-election Kubernetes can't do. Use networked storage + ≥3 replicas with app replication; verify failover at the DB layer, not just Pod restart.

**H2 - An AZ outage takes down 2 of 3 quorum members.**

> Replicas weren't AZ-spread (or 2 shared an AZ). Enforce `topologySpreadConstraints` across `topology.kubernetes.io/zone` with `maxSkew: 1`, and size quorum so one AZ loss leaves majority. EBS volumes follow their replicas per AZ.

**H3 - StatefulSet rollout corrupted the cluster.**

> RollingUpdate cycled Pods faster than re-sync. Switch to `OnDelete`, upgrade one member at a time after confirming sync/health, and snapshot before upgrades.

**H4 - Cross-AZ data-transfer bill spikes for a replicated datastore.**

> Replication traffic crossing AZs (unavoidable for HA) plus clients not reading AZ-local. Use topology-aware routing for reads, accept replication cost as the price of HA, and right-size replica count.

**H5 - PVCs keep accumulating and EBS spend climbs.**

> `Retain` volumes orphaned after StatefulSet deletion, or no `persistentVolumeClaimRetentionPolicy`. Reconcile orphaned PVs, set retention policy, tag + lifecycle-audit EBS volumes.

[⬆ Back to top](#table-of-contents)

---

## 6. Diagnostic Commands

```bash
kubectl get sts,pods,pvc,pv -o wide
kubectl describe pvc <pvc>                       # bound? events?
kubectl describe pod mydb-0 | sed -n '/Events/,$p' # mount/attach errors
kubectl get pv <pv> -o jsonpath='{.spec.nodeAffinity}'   # AZ pin
kubectl get volumeattachment                      # which node holds the volume
kubectl get storageclass
# AWS side:
# aws ec2 describe-volumes --filters Name=tag:kubernetes.io/created-for/pvc/name,Values=<pvc>
```

[⬆ Back to top](#table-of-contents)

---

## 7. Runbooks

### Runbook: stuck volume mount / Multi-Attach

1. `kubectl describe pod` → confirm attach/Multi-Attach error.
2. `kubectl get volumeattachment` → which node still holds it.
3. If that node is dead/gone, allow detach (or force-detach the EBS volume in EC2).
4. Confirm only one Pod references the RWO PVC.
5. Pod reschedules and mounts; verify data integrity.

### Runbook: safe database StatefulSet upgrade

1. Snapshot all volumes (VolumeSnapshot / AWS Backup).
2. Set `updateStrategy: OnDelete` (or partitioned RollingUpdate).
3. Delete/upgrade one Pod; wait for Ready + DB replication caught up.
4. Repeat per member; never proceed until the prior is healthy.
5. Validate cluster health and failover before declaring done.

[⬆ Back to top](#table-of-contents)

---

## 8. One-Line Recap

> **StatefulSet = stable identity + sticky per-Pod PVC + headless DNS + ordered ops - but it's persistence, not HA. EBS = RWO/zonal (use WaitForFirstConsumer + AZ spread); EFS = RWX/multi-AZ. Replication ≠ backup (snapshot!). Upgrade DBs with OnDelete. The smoking gun for mount issues is `describe pod` events.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [01 - Security & RBAC Guide](01%20-%20Security%20%26%20RBAC%20Guide.md).
