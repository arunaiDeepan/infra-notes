# Scheduling & Resources - Scenarios & SRE Ops

> Diagnosing the "Pod randomly died/got slow" class of problems. Frequently tested concepts, CKA/CKAD tasks, interview questions, EKS production scenarios, fast diagnostic commands, and runbooks. Pair with [01 - Scheduling & Resources Guide](01%20-%20Scheduling%20%26%20Resources%20Guide.md).

See also: [01 - Scheduling & Resources Guide](01%20-%20Scheduling%20%26%20Resources%20Guide.md) · [02 - Autoscaling Scenarios & SRE Ops](02%20-%20Autoscaling%20Scenarios%20%26%20SRE%20Ops.md) · [02 - Workload Resilience Scenarios & SRE Ops](02%20-%20Workload%20Resilience%20Scenarios%20%26%20SRE%20Ops.md)

---

## Table of Contents

- [1. Frequently Tested Concepts](#1-frequently-tested-concepts)
- [2. Keywords → Cause](#2-keywords--cause)
- [3. CKA/CKAD Practical Tasks](#3-ckackad-practical-tasks)
- [4. Interview Questions](#4-interview-questions)
- [5. EKS Production Scenarios](#5-eks-production-scenarios)
- [6. Fast Diagnostic Commands](#6-fast-diagnostic-commands)
- [7. Runbooks](#7-runbooks)
- [8. One-Line Recap](#8-one-line-recap)

---

## 1. Frequently Tested Concepts

- **Scheduler uses requests; runtime enforces limits.**
- **CPU over-limit → throttled; memory over-limit → OOMKilled (137).**
- **QoS**: Guaranteed (req==lim) > Burstable > BestEffort (evicted first).
- **OOMKilled = container/limit; Evicted = node pressure.**
- **Overcommit** (tiny requests + huge limits) → OOM/eviction storms under load.
- **Requests should reflect reality** - they're your eviction baseline.
- EKS: **allocatable < capacity** (kubelet/OS/CNI reserved).

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords → Cause

| Phrase                                  | Points to                         |
| :-------------------------------------- | :-------------------------------- |
| "exit code 137 / OOMKilled"             | Memory limit exceeded             |
| "Pod status Evicted"                    | Node MemoryPressure/DiskPressure  |
| "slow but healthy / latency spikes"     | CPU throttling                    |
| "Pending: Insufficient cpu/memory"      | Requests don't fit any node       |
| "fine until traffic hit"                | Overcommit (requests ≪ limits)    |
| "DiskPressure / ephemeral-storage"      | Logs/temp filling node disk       |
| "scheduled on crowded node, dies first" | Too-low memory request, Burstable |

[⬆ Back to top](#table-of-contents)

---

## 3. CKA/CKAD Practical Tasks

**T1 - Identify QoS class:**

```bash
kubectl get pod <pod> -o jsonpath='{.status.qosClass}{"\n"}'
```

**T2 - See requests/limits in one view:**

```bash
kubectl get pod <pod> -o jsonpath='{range .spec.containers[*]}{.name}{" req="}{.resources.requests}{" lim="}{.resources.limits}{"\n"}{end}'
```

**T3 - Confirm OOMKill:**

```bash
kubectl describe pod <pod> | grep -A3 "Last State"   # Reason: OOMKilled, Exit Code: 137
```

**T4 - Check node pressure + allocatable:**

```bash
kubectl describe node <node> | grep -E "Pressure|Allocatable" -A2
kubectl top nodes ; kubectl top pods --containers
```

**T5 - Schedule a Pod onto a specific node pool (taint/toleration):**

```yaml
tolerations:
  - key: "dedicated"
    operator: "Equal"
    value: "gpu"
    effect: "NoSchedule"
nodeSelector: { node-type: gpu }
```

[⬆ Back to top](#table-of-contents)

---

## 4. Interview Questions

**Q1: Difference between a request and a limit?**

> Request = scheduling reservation (placement math). Limit = runtime ceiling (cgroups). Scheduler reads requests; kubelet/kernel enforce limits.

**Q2: Why is CPU throttled but memory OOMKilled?**

> CPU is compressible - the kernel just hands out fewer slices. Memory is non-compressible - you can't "slow down" RAM, so the kernel kills the process.

**Q3: How are QoS classes computed and why do they matter?**

> From requests/limits: req==lim (both resources) → Guaranteed; partial → Burstable; none → BestEffort. They set eviction order under node pressure.

**Q4: A service is slow but CPU/memory look fine and nothing crashed. Hypothesis?**

> CPU throttling from a tight CPU limit (latency without restarts), or an IO-bound bottleneck. Check `container_cpu_cfs_throttled_periods`. Loosen the limit or scale out.

**Q5: What's the danger of unset requests/limits?**

> BestEffort QoS (evicted first), bad scheduling decisions, and noisy-neighbor risk. Under pressure your Pod is the first casualty.

**Q6: How do you make a Pod survive an AZ failure on EKS?**

> `topologySpreadConstraints` across `topology.kubernetes.io/zone`, ≥3 replicas, PDB, and multi-AZ node groups.

[⬆ Back to top](#table-of-contents)

---

## 5. EKS Production Scenarios

### Medium

**M1 - A Java app is OOMKilled repeatedly though heap looks fine.**

> JVM doesn't see the cgroup limit (old JDK) or off-heap/metaspace overflows the container limit. Use a container-aware JVM (`-XX:MaxRAMPercentage`), raise the memory limit above heap+overhead.

**M2 - Pods Pending: `Insufficient cpu` despite low cluster utilization.**

> Requests too high (or a few large Pods can't bin-pack). Right-size requests; let Karpenter pick a fitting instance; check for stranded capacity across AZs.

**M3 - Nodes hitting `DiskPressure`, Pods evicted at night.**

> Log/temp files fill the EBS root volume. Set `ephemeral-storage` limits, ship logs off-node (Fluent Bit → CloudWatch), enlarge root volume, or use a separate log volume.

**M4 - After adding CPU limits "for safety," p99 latency doubled.**

> CFS throttling. Remove or raise CPU limits on latency-sensitive services; keep requests for scheduling. Validate with throttling metrics.

### Hard

**H1 - Cascading meltdown: a traffic spike throttles Pods, readiness fails, traffic concentrates, more Pods fail.**

> The throttling→readiness→concentration loop. Short-term: raise CPU limits / scale out manually. Long-term: HPA on RPS (not just CPU), looser CPU limits, decouple readiness from heavy work. See [01 - Autoscaling Guide](01%20-%20Autoscaling%20Guide.md).

**H2 - Overcommitted node group OOM-storms only at peak.**

> Requests ≪ limits → scheduler over-packs → peak bursts exhaust node memory. Tighten requests toward real peak memory, set Guaranteed QoS for critical Pods, add headroom, reserve node resources.

**H3 - A batch job with no limits (BestEffort) starves a critical service on the same node.**

> Noisy neighbor + BestEffort. Give the batch job requests/limits, give the critical service a higher PriorityClass and Guaranteed QoS, or isolate workloads onto separate node pools via taints.

**H4 - Spot interruptions cause repeated eviction of stateful Pods.**

> Stateful workloads on spot. Run them on on-demand nodes (taint spot, don't tolerate for stateful), use PDBs, and handle the 2-minute spot rebalance signal to drain gracefully.

[⬆ Back to top](#table-of-contents)

---

## 6. Fast Diagnostic Commands

```bash
# Who got OOMKilled / restarted?
kubectl get pods -o wide
kubectl describe pod <pod> | grep -A3 "Last State"

# Node pressure + capacity
kubectl describe node <node> | grep -E "MemoryPressure|DiskPressure|Allocatable" -A2

# Actual vs requested (needs metrics-server)
kubectl top nodes
kubectl top pods --containers

# QoS + requests/limits at a glance
kubectl get pod <pod> -o jsonpath='{.status.qosClass}{"\n"}'

# Throttling (Prometheus / cAdvisor)
# rate(container_cpu_cfs_throttled_periods_total[5m]) / rate(container_cpu_cfs_periods_total[5m])
```

[⬆ Back to top](#table-of-contents)

---

## 7. Runbooks

### Runbook: triage "Pod keeps restarting"

1. `kubectl describe pod` → Last State reason. OOMKilled (137)? → memory.
2. Compare usage (`kubectl top`) to the limit; check for leaks/heap.
3. Raise limit or fix the leak; set realistic requests.
4. If load-driven growth → add HPA. Confirm restart count stops climbing.

### Runbook: triage "everything on this node is unhappy"

1. `kubectl describe node` → MemoryPressure/DiskPressure/PIDPressure?
2. `kubectl top pods --all-namespaces --sort-by=memory` → find the hog.
3. DiskPressure → find log/temp offenders; ship logs off-node.
4. Add capacity (Karpenter/CA) or evict the noisy neighbor with limits.
5. Add reserved resources so the kubelet/OS keep headroom.

[⬆ Back to top](#table-of-contents)

---

## 8. One-Line Recap

> **Requests schedule, limits enforce. CPU throttles (slow), memory OOMKills (137). QoS = Guaranteed>Burstable>BestEffort decides who's evicted. OOMKilled is container/limit; Evicted is node pressure. Make requests reflect reality, avoid tight CPU limits on latency paths, spread across AZs, and reserve node headroom.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [01 - Autoscaling Guide](01%20-%20Autoscaling%20Guide.md).
