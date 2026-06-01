### Requests, Limits, QoS Classes, Eviction, and OOMKills

This is the other half of “why Kubernetes behaves like it’s possessed.” Networking explains “why I can’t reach my pod.” Resources explain “why my pod randomly got slow/killed even though nothing ‘changed’.” Under the hood, it’s Linux cgroups (resource control groups) plus Kubernetes scheduling/eviction rules.

---

#### 1) Requests vs Limits: what they actually mean

In a Pod spec you set resources per container:

- **requests**: “I need at least this much to run properly.”
  - Used by the **scheduler** to decide placement.
  - Think: reservation for scheduling math.

- **limits**: “I’m not allowed to exceed this.”
  - Enforced by the **kubelet + kernel cgroups** at runtime.
  - Think: hard ceiling.

So:

- Scheduler uses **requests** to pack Pods onto nodes.
- Runtime enforces **limits**.

If you set no requests/limits, Kubernetes has to guess your importance later (and it guesses in a way that tends to hurt).

---

#### 2) CPU vs Memory enforcement: totally different physics

**CPU limits**

- CPU is “compressible.” If you try to use more than your CPU limit, you get **throttled** (slowed down), not killed.
- Symptoms: latency spikes, timeouts, “it’s slow” while everything looks “healthy.”

**Memory limits**

- Memory is “non-compressible.” If you exceed memory limit, you get **OOMKilled** (the kernel kills your process).
- Symptoms: container restarts, exit code 137, Pod events mention OOMKill.

This difference is huge:

- CPU limit mistakes cause “mysterious slowness.”
- Memory limit mistakes cause “sudden death and restarts.”

---

#### 3) QoS classes: Kubernetes’ priority tiers for eviction

Kubernetes assigns each Pod a QoS class based on requests/limits:

1. **Guaranteed**

- Every container has requests == limits for CPU and memory (and both are set).
- Highest protection from eviction.

1. **Burstable**

- Requests set, but limits are higher (or only some resources set).
- Middle protection. Can burst up to limits.

1. **BestEffort**

- No requests and no limits at all.
- Lowest protection. Gets evicted first when node is under pressure.

Why you care:  
When the node gets tight on memory/disk, eviction happens. QoS class heavily influences who gets kicked out.

---

#### 4) Scheduling: why your pod landed on that node

Scheduler checks node capacity against the sum of **requests** (not limits).

Example:

- Node has 4 CPU, 16Gi RAM
- Existing pods request 3 CPU, 12Gi
- Your pod requests 1 CPU, 2Gi  
   → scheduler says “fits!”

But if everyone sets tiny requests and huge limits, you can get **overcommit**:

- scheduler packs pods because requests fit
- at runtime, pods can try to use up to limits
- node runs out of memory → evictions/OOM storms

That’s the classic “it was fine until traffic hit.”

---

#### 5) Two kinds of “killed”: OOMKilled vs Evicted

They look similar (pod dies), but causes and fixes differ.

**A) OOMKilled (container-level)**

- Cause: container exceeded its **memory limit**
- Killer: Linux kernel OOM killer inside cgroup boundary
- Clues:
  - `kubectl describe pod` shows `OOMKilled`
  - container restart count increases
  - last state shows OOMKilled / exit code 137

Fix:

- increase memory limit
- reduce memory usage/leaks
- set realistic requests so it lands on a node with room

- use HPA scaling if memory grows with load

**B) Evicted (pod-level)**

- Cause: node is under resource pressure (memory/disk/inodes, etc.)
- Killer: kubelet eviction manager (it chooses victims)
- Clues:
  - Pod status becomes `Evicted`
  - events show eviction reason like `MemoryPressure`, `DiskPressure`, `ephemeral-storage`

Fix:

- give nodes more capacity / autoscale nodes
- set requests/limits so scheduling is sane
- reduce log/ephemeral storage usage
- fix noisy neighbors (limit them)

---

#### 6) Eviction manager: how kubelet chooses who dies

When the node is stressed (especially memory), kubelet starts evicting Pods to protect the node.
Eviction priority is influenced by:

- QoS class (BestEffort first, then Burstable, then Guaranteed)
- Pod priority (PriorityClass)
- Actual usage relative to requests (especially for Burstable)
- Whether the pod is critical/system

So a Burstable pod that uses way more memory than it requested is a prime target.

This is why “requests should reflect reality.” Under pressure, Kubernetes uses them as your “promised baseline.”

---

#### 7) CPU throttling: the silent performance killer

If CPU limit is too low:

- your container hits the cgroup CPU quota
- it gets throttled
- latency increases
- probes may start failing → pod removed from endpoints → cascading failure

This produces a nasty chain:  
CPU throttling → slow responses → readiness fails → traffic shifts to fewer pods → more CPU pressure → more throttling → meltdown.

Fix patterns:

- set CPU requests/limits based on measured load
- avoid overly tight CPU limits for latency-sensitive services
- use HPA on CPU, but ensure the app can scale horizontally

---

#### 8) Memory requests: what they protect you from

Memory requests don’t cap usage; they influence:

- scheduling placement
- eviction priority
- node packing safety

If you request too little memory:

- you get scheduled onto crowded nodes
- you get evicted sooner under pressure (especially Burstable using > request)

If you request too much:

- scheduler struggles to place you (Pending pods)
- cluster becomes underutilized

So it’s a balancing act, ideally driven by metrics.

---

#### 9) Practical commands to diagnose resource issues fast

**A) See restarts and OOMKilled**

```bash
kubectl get pods -o wide
kubectl describe pod <pod>
```

Look for:

- `Last State: Terminated` with `Reason: OOMKilled`
- Events mentioning OOM

**B) Check node pressure**

```bash
kubectl describe node <node>
```

Look for:

- MemoryPressure / DiskPressure conditions
- Allocatable vs capacity
- Events about eviction

**C) See resource requests/limits in one view**

```bash
kubectl get pod <pod> -o jsonpath='{range .spec.containers[*]}{.name}{"\n  requests: "}{.resources.requests}{"\n  limits: "}{.resources.limits}{"\n\n"}{end}'
```

**D) If metrics-server is installed**

```bash
kubectl top pods
kubectl top nodes
```

This helps you compare actual usage vs requests.

---

#### 10) A sane “starter” policy for many teams

For typical web services:

- Always set **memory requests + limits**
- Set **CPU requests**; consider being careful with tight CPU limits (depends on workload)
- Use **HPA** for CPU or custom metrics
- Give critical services a higher **PriorityClass**
- Keep probes realistic (don’t make them ultra-strict)

Not universal, but it avoids 80% of common production pain.

---
