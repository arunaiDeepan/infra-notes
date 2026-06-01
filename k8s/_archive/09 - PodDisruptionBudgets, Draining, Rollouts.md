### PodDisruptionBudgets, Draining, Rollouts, and Why “Safe” Upgrades Sometimes Never Finish

This is where Kubernetes becomes a grown-up: it’s not just “run my containers,” it’s “change the system without breaking users.” The catch is that “don’t break users” is a constraint, and constraints can deadlock. PodDisruptionBudgets (PDBs) are a prime example: they protect availability, but they can also block rollouts and cluster scale-down if set too strictly.

---

#### 1) Disruptions: voluntary vs involuntary

Kubernetes distinguishes between:

**Involuntary disruptions**

- node crashes, kernel panic, power outage
- OOMKills, hardware failure  
   Kubernetes can’t ask permission here. Stuff just dies.

**Voluntary disruptions**

- you drain a node
- Cluster Autoscaler wants to remove a node
- you upgrade nodes
- you delete a pod during maintenance

PDBs only control _voluntary_ disruptions.

So if your node explodes, PDB won’t save you. PDB is about controlled maintenance.

---

#### 2) PodDisruptionBudget (PDB): what it is and what it protects

A PDB is a policy like:

- “Keep at least N pods available” (`minAvailable`)  
   or
- “Allow at most N pods unavailable” (`maxUnavailable`)

It targets pods by label selector.

What “available” means here:

- Basically “Ready” (plus a few details), i.e., pods that would be considered serving traffic.

So PDB is glued to readiness. Bad readiness signals can make PDB overly strict.

Control knobs:

- choose `minAvailable` / `maxUnavailable`
- choose selector that matches exactly the workload pods you intend

---

#### 3) Node drain: what actually happens

When you run:

```bash
kubectl drain <node> --ignore-daemonsets
```

Kubernetes tries to safely evict pods from that node.

Under the hood:

1. It marks the node unschedulable (cordon).
2. It attempts to evict pods one by one using the Eviction API.
3. For each eviction, the API server checks:
   - Is there a PDB that applies?
   - If yes, does evicting this pod violate the disruption budget?

4. If allowed, the pod is deleted.
5. Controllers recreate pods elsewhere, scheduler places them.

If PDB says “no,” eviction is blocked, and the drain hangs.

Important: DaemonSet pods are typically not evicted by drain (they’re expected to exist on every node).

---

#### 4) Cluster Autoscaler scale-down is basically “drain lite”

When Cluster Autoscaler wants to remove a node, it must:

- move pods elsewhere
- respect PDBs
- respect node selectors/affinities/taints
- respect local storage constraints

So the same blockers that break `kubectl drain` break CA scale-down.

That’s why teams sometimes notice: “we scale up fine, but we never scale down.” It’s usually PDBs + constraints.

---

#### 5) Rollouts are not the same as drains

A Deployment rollout (rolling update) works by:

- creating new pods (new ReplicaSet)
- waiting for them to become Ready
- then terminating old pods gradually

This is _controller-driven_ replacement, not eviction-driven drain.

Do PDBs affect rollouts?

- Historically, PDBs primarily gate **voluntary evictions** (drain/evict).
- Rollouts delete old pods as part of controller updates, which isn’t always treated the same as “eviction.”
- Practically though: even if the API doesn’t block the delete, a strict availability requirement still shows up as a rollout that effectively can’t progress because new pods never become ready, or because surge/unavailable settings prevent progress.

The more direct “rollout safety” levers are:

- `maxUnavailable`
- `maxSurge`
- readiness probes
- progress deadline

But PDBs strongly influence maintenance operations and node upgrades, and those interact with rollouts in real life.

---

#### 6) The most common “stuck forever” scenarios

Here are the classics (you will meet them in the wild):

**Scenario A: Single replica + PDB minAvailable: 1**

- You have 1 pod.
- PDB says at least 1 must be available.
- Drain tries to evict it → denied.  
   Result: node cannot drain; node upgrade blocks; scale-down blocks.

Fix: Either run ≥2 replicas, or loosen PDB (or temporarily disable during maintenance).

**Scenario B: PDB selector matches more than you think**

- You intended to protect one Deployment.
- Selector matches multiple workloads (shared labels like `app=api` across services).  
   Result: PDB becomes way stricter than expected and blocks unrelated evictions.

Fix: Use precise labels (include component/version/role labels).

**Scenario C: Readiness is failing, so “available” count is low**

- Pods exist but aren’t Ready (bad probe, dependency down).
- PDB thinks you already have fewer available than required.
- It blocks evicting anything.  
   Result: drains and maintenance freeze exactly when you need them most.

Fix: Fix readiness, or adjust PDB strategy so it doesn’t deadlock your recovery.

**Scenario D: Strict topology / affinity prevents rescheduling**

- PDB allows eviction, but scheduler can’t place replacement pods elsewhere due to:
  - node affinity
  - taints/tolerations mismatch
  - insufficient resources
  - topology spread constraints too strict  
     Result: drain proceeds partially then stalls; CA scale-down impossible.

Fix: relax constraints, add capacity, or use multiple node groups/zones.

**Scenario E: Pod uses local storage**

- Pods with local PVs or certain hostPath patterns can’t be moved freely.  
   Result: CA won’t remove the node; drain may need special handling.

Fix: use networked storage (CSI), or accept reduced mobility.

---

#### 7) A practical way to set PDBs without self-sabotage

For stateless services:

- If replicas ≥ 2: `maxUnavailable: 1` is often sane.
- If replicas are large: `maxUnavailable: 10%` can be nicer.
  For critical services:
- Ensure enough replicas across zones/nodes.
- Pair with topology spread so losing a node doesn’t take out too many replicas.
  For single-replica stateful things:
- PDB often can’t save you; availability requires replication at the application/storage level.

Key idea: PDB is meaningful only if you actually run enough replicas to survive a disruption.

---

#### 8) How to debug “why won’t this drain/scale down?”

**A) See PDBs and their current allowed disruptions**

```bash
kubectl get pdb -A
kubectl describe pdb -n <ns> <pdb>
```

Look for:

- `DisruptionsAllowed`
- current healthy vs desired healthy

If `DisruptionsAllowed: 0`, eviction is blocked.

**B) Try an eviction and see the denial**  
Drains will show messages like “cannot evict pod as it would violate the pod’s disruption budget.”

**C) Check why replacement pods can’t schedule**

```bash
kubectl describe pod <pending-pod>
```

You’ll see the scheduler’s reasons: insufficient resources, affinity mismatch, etc.

---

#### 9) Rollout deadlocks: maxSurge/maxUnavailable + readiness

A rollout can “freeze” if:

- new pods never become Ready (probe issue, dependency issue)
- `maxSurge: 0` and `maxUnavailable: 0` (you told Kubernetes: “change nothing while changing everything”)
- there isn’t enough cluster capacity for surge pods
- PDBs + constraints mean no room to maneuver during maintenance

A very practical rule:

- Don’t set both surge and unavailable to zero unless you have a separate blue/green strategy.

---

#### 10) The clean mental model

- **PDB**: “don’t voluntarily reduce availability below this line.”
- **Drain/CA scale-down**: voluntary evictions, strictly PDB-governed.
- **Rollouts**: controller replacement, governed by rollout strategy + readiness, and indirectly impacted by PDBs/capacity/constraints.
- **Deadlocks** happen when you demand high availability but don’t supply enough replicas/capacity/placement flexibility.

---
