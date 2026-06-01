### StatefulSets, Persistent Volumes, and What “Stateful” Really Means in Kubernetes

Stateless is easy: kill it, replace it, nobody cares. Stateful is… a diva. It cares about identity, ordering, storage, and sometimes even which rack it woke up in. Kubernetes can handle stateful workloads, but only if you understand the contract it’s actually offering.

Here’s the deep dive: StatefulSet mechanics, PV/PVC/StorageClass, how failover really works, and the classic traps.

#### 1) The core problem: “state” needs identity + stable storage

A normal Deployment gives you “N interchangeable replicas.” That’s perfect for web servers, terrible for databases.

Stateful workloads typically need:

- Stable identity (replica 0 is replica 0, not “some pod”)
- Stable storage that persists across restarts/reschedules
- Often stable network identity (so peers can find each other consistently)
- Sometimes ordered startup/shutdown (to avoid chaos)

That’s exactly what StatefulSet is for.

#### 2) StatefulSet: what it guarantees

A StatefulSet gives each pod:

- A stable name: `mydb-0`, `mydb-1`, `mydb-2`
- A stable DNS name (via a **Headless Service**):  
   `mydb-0.mydb-headless.default.svc.cluster.local`
- Stable storage via per-pod PVCs (usually created automatically)
- Controlled rollout semantics (more on that soon)

What it does _not_ magically guarantee:

- Data correctness (that’s your database’s job)
- Automatic leader election correctness (unless your app does it)
- Multi-region disaster recovery (you still need backups/replication)

So Kubernetes provides the _platform primitives_; your app provides the _distributed systems sanity_.

#### 3) Headless Service: the secret sauce for stable discovery

StatefulSets almost always use a **Headless Service** (`clusterIP: None`).

What headless means:

- DNS returns **pod IPs directly**, not a single ClusterIP.
- That enables stable per-pod addressing:
  - `mydb-0` resolves to the IP of pod 0
  - `mydb-1` resolves to pod 1, etc.

This is how clustered databases often form their peer lists.

#### 4) Storage in Kubernetes: PV, PVC, StorageClass

Storage is where most “it seemed fine until it wasn’t” stories come from.

- **StorageClass**: “how to provision storage” (type, parameters, reclaim policy, binding mode)
- **PVC (PersistentVolumeClaim)**: “I want X GiB with these properties”
- **PV (PersistentVolume)**: “an actual piece of storage backing a claim”

In many clusters, PVCs are **dynamically provisioned**:

- you create a PVC
- a CSI driver provisions a disk/file share
- a PV appears and binds to that PVC

#### 5) StatefulSet + volumeClaimTemplates: per-pod disks, automatically

StatefulSet typically uses `volumeClaimTemplates`, which means:

- pod `mydb-0` gets PVC `data-mydb-0`
- pod `mydb-1` gets PVC `data-mydb-1`  
   …and those PVC names remain tied to those pod identities.

This is the killer feature: if `mydb-1` is rescheduled, it should reattach `data-mydb-1` and continue.

#### 6) The hardest truth: “reschedule” depends on the volume type

Whether a stateful pod can move freely depends heavily on the storage backend.

Common patterns:

**A) Network-attached storage (portable)**

- Examples: many cloud block volumes, NFS, Ceph, EFS-like systems
- Pod can move to another node and reattach/mount the same volume
- Usually what you want for StatefulSets

**B) Local storage (sticky to a node)**

- Local SSDs, local PVs, hostPath (dangerous)
- If the node dies, the data may be inaccessible
- Scheduling becomes constrained: the pod is basically married to that node

This is why “local PV + StatefulSet” is a deliberate tradeoff: performance vs mobility.

#### 7) Access modes: RWO vs RWX, and why it matters

PVCs have access modes like:

- **RWO** (ReadWriteOnce): mounted read-write by a single node at a time (common for block volumes)
- **RWX** (ReadWriteMany): mounted read-write by multiple nodes (file shares)

Most databases use RWO per replica. RWX is great for shared filesystems, not necessarily for DB data directories (depends on DB).

If you try to run a single PVC mounted by multiple pods with RWO, Kubernetes will block it, or you’ll get mount failures.

#### 8) Ordering and rollout behavior: why `-0` is “special”

By default (classic behavior), StatefulSets do things in order:

- Create: `-0` then `-1` then `-2`
- Delete: reverse order
- Updates: often one-at-a-time (depending on policy)

This matters for systems like ZooKeeper, etcd, some DB clusters, where bootstrapping order matters.

Also, StatefulSet has an update strategy:

- **RollingUpdate**: updates pods gradually (often reverse ordinal by default)
- **OnDelete**: you control exactly when each pod updates (manual, safer for some DBs)

A typical “safe-ish” approach for databases:

- Use OnDelete or very cautious RollingUpdate
- Coordinate upgrades with the database’s own upgrade procedure

#### 9) Failure modes: what really happens when a node dies

Let’s say `mydb-1` is on Node A and Node A dies.

What Kubernetes does:

- Node controller marks Node A NotReady after timeouts
- Pod `mydb-1` becomes unavailable
- Eventually, Kubernetes tries to recreate `mydb-1` elsewhere

What can block recovery:

- The volume can’t detach from the dead node (cloud provider delays)
- The volume is local to the dead node
- Scheduling constraints prevent placement (affinity, taints, insufficient resources)
- PDBs and disruption rules complicate voluntary moves (less relevant for involuntary failure, but can matter during maintenance)

Important nuance:  
Even if Kubernetes brings the pod back, your database may need to re-elect leaders, catch up replicas, replay logs, etc. Kubernetes doesn’t understand your replication protocol.

#### 10) “Stateful” is not “highly available” by default

A single replica StatefulSet is still a single point of failure. StatefulSet gives you persistence and identity, not HA.

HA requires:

- multiple replicas
- app-level replication
- proper anti-affinity / topology spread so replicas aren’t on the same node/zone
- readiness probes that reflect “can serve” (not merely “process alive”)
- backup/restore strategy (because replication ≠ backup)

#### 11) The classic traps (you’ll see these in production)

- **Using hostPath for database data**: works in dev, hurts in prod.
- **Assuming Kubernetes will failover a primary cleanly**: it will restart pods, but the DB must handle leadership.
- **Readiness probe that says “ready” before the DB can serve**: causes client errors during warmup.
- **No PodAntiAffinity/topology spread**: all replicas land on one node/zone, then one failure wipes them.
- **PVC reclaim policy misunderstandings**: you delete a claim and accidentally delete the underlying disk (or the opposite: disks accumulate forever).

#### 12) Quick commands that reveal what’s happening

To see the identity/storage mapping:

```bash
kubectl get sts
kubectl get pods -l app=mydb -o wide
kubectl get pvc | grep mydb
kubectl describe pvc data-mydb-0
kubectl describe pod mydb-0
```

If mounts/attachments fail, the Events section of `describe pod` is usually the smoking gun.

---
