# LLM Inference on Kubernetes - Scenarios & SRE Ops

> Operating GPU serving: cold-start spikes, KV-cache misses, OOMs, and GPU scheduling. Frequently tested concepts, design tasks, interview questions, EKS production scenarios, and runbooks. Pair with [01 - LLM Inference Guide](01%20-%20LLM%20Inference%20Guide.md).

See also: [01 - LLM Inference Guide](01%20-%20LLM%20Inference%20Guide.md) · [02 - Autoscaling Scenarios & SRE Ops](02%20-%20Autoscaling%20Scenarios%20%26%20SRE%20Ops.md) · [02 - Scheduling & Resources Scenarios & SRE Ops](02%20-%20Scheduling%20%26%20Resources%20Scenarios%20%26%20SRE%20Ops.md)

---

## Table of Contents

- [1. Frequently Tested Concepts](#1-frequently-tested-concepts)
- [2. Keywords → Cause](#2-keywords--cause)
- [3. Design / Practical Tasks](#3-design--practical-tasks)
- [4. Interview Questions](#4-interview-questions)
- [5. EKS Production Scenarios](#5-eks-production-scenarios)
- [6. Runbooks](#6-runbooks)
- [7. One-Line Recap](#7-one-line-recap)

---

## 1. Frequently Tested Concepts

- **One model per pod**; GPU memory is the constraint.
- **Sticky routing at the router** for KV-cache reuse.
- **Scale on queue depth / GPU util / latency**, never CPU.
- **GPU nodes provision slowly** → warm pools + baseline capacity.
- **Prefetch weights to node-local NVMe** (versioned).
- **MIG/whole-GPU** for latency; time-slicing for dev/batch.
- **Backpressure with 429/503 + Retry-After.**
- EKS: NVIDIA device plugin + DCGM; `nvidia.com/gpu`; taints on GPU nodes.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords → Cause

| Phrase                                      | Points to                                              |
| :------------------------------------------ | :----------------------------------------------------- |
| "spike → minutes of errors"                 | GPU node cold start; need warm pool                    |
| "latency jumps mid-conversation"            | KV-cache miss; need session affinity                   |
| "GPU OOM / CUDA out of memory"              | Model + KV cache exceeds GPU mem; reduce batch/context |
| "pods Pending: insufficient nvidia.com/gpu" | No GPU capacity / device plugin missing                |
| "non-GPU pods landed on GPU nodes"          | Missing taints on GPU pool                             |
| "startup takes 10 min"                      | Cold-pulling weights from S3                           |
| "unpredictable tail latency when sharing"   | Time-slicing instead of MIG                            |
| "queue melts into timeouts"                 | No backpressure/load shedding                          |

[⬆ Back to top](#table-of-contents)

---

## 3. Design / Practical Tasks

**T1 - Request a GPU + keep others off the pool:**

```yaml
spec:
  nodeSelector: { node-type: gpu-inference }
  tolerations:
    [{ key: "nvidia.com/gpu", operator: "Exists", effect: "NoSchedule" }]
  containers:
    - name: vllm
      resources: { limits: { nvidia.com/gpu: 1 } }
```

**T2 - Verify GPU scheduling + device plugin:**

```bash
kubectl get nodes -o json | jq '.items[].status.allocatable["nvidia.com/gpu"]'
kubectl -n kube-system get ds nvidia-device-plugin-daemonset
kubectl describe node <gpu-node> | grep nvidia.com/gpu
```

**T3 - KEDA scale on queue depth (vLLM behind a queue / metric):**

```yaml
triggers:
  - type: prometheus
    metadata:
      serverAddress: http://prometheus.observability.svc:9090
      query: sum(vllm_num_requests_waiting)
      threshold: "5"
```

**T4 - Spread GPU replicas across AZs/nodes:**

```yaml
topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: ScheduleAnyway
    labelSelector: { matchLabels: { app: model-a } }
```

[⬆ Back to top](#table-of-contents)

---

## 4. Interview Questions

**Q1: Why can't you scale LLM serving on CPU?**

> The bottleneck is GPU compute/memory and request queue, not CPU. Scale on GPU utilization, in-flight/waiting requests, tokens/sec, or p99 latency (KEDA/custom metrics).

**Q2: Why an inference router separate from Ingress?**

> Ingress only does L7 path/host routing. The router understands GPU queue depth, model residency, and KV-cache affinity - it does sticky routing, load shedding, and backpressure that Ingress can't.

**Q3: How do you avoid 10-minute outages on traffic spikes?**

> GPU nodes provision slowly and are scarce. Keep baseline capacity + warm pools + predictive/scheduled scaling; never rely purely on reactive node autoscaling.

**Q4: What's KV-cache affinity and why does it matter?**

> Continuing a conversation reuses the KV cache on the pod that served earlier tokens. Without sticky routing you hit a cold pod and re-pay prefill cost → latency spike. Pin sessions at the router.

**Q5: MIG vs time-slicing?**

> MIG carves a GPU into isolated hardware partitions (predictable latency) - good for serving. Time-slicing shares by time (flexible, unpredictable tail) - fine for dev/batch.

**Q6: How do weights get onto nodes without killing startup?**

> Prefetch to node-local NVMe via a DaemonSet (versioned + checksummed); pods load from local disk. Don't cold-pull 100GB from S3 per pod start.

[⬆ Back to top](#table-of-contents)

---

## 5. EKS Production Scenarios

### Medium

**M1 - vLLM pods `Pending: 0/x nodes available: insufficient nvidia.com/gpu`.**

> No GPU capacity or device plugin missing. Verify the NVIDIA device-plugin DaemonSet, add/scale GPU nodes (Karpenter GPU NodePool), check instance GPU count.

**M2 - Non-GPU workloads scheduled onto expensive GPU nodes.**

> GPU pool not tainted. Taint GPU nodes (`nvidia.com/gpu:NoSchedule`); only inference pods tolerate it.

**M3 - Model pods take 8 minutes to become Ready.**

> Cold-pulling weights from S3 at startup. Add a prefetch DaemonSet to node-local NVMe; mount read-only; version directories.

**M4 - Tail latency degrades for returning users.**

> KV-cache misses from round-robin routing. Add session affinity at the router so conversations stick to the same backend.

### Hard

**H1 - Black-Friday-style spike → minutes of 5xx while GPU nodes provision.**

> Reactive-only scaling on scarce GPUs. Maintain warm baseline + over-provision buffer (low-priority placeholder pods preempted on demand) + scheduled scaling; backpressure with 429/Retry-After meanwhile. See [01 - Autoscaling Guide](01%20-%20Autoscaling%20Guide.md).

**H2 - `CUDA out of memory` under load.**

> Model + KV cache exceeds GPU memory at high concurrency/context. Cap max concurrent sequences/context length, tune vLLM `gpu-memory-utilization` / max-num-seqs, use a bigger GPU or MIG slice sizing, and shed load before OOM.

**H3 - A new model version regressed p99 but "looked fine" in canary.**

> Canary traffic too small / wrong metrics. Canary at the router with real p95/p99 + GPU memory + quality metrics; expand gradually; roll back **by routing** (keep v1 warm). See [01 - Workload Resilience Guide](01%20-%20Workload%20Resilience%20Guide.md).

**H4 - One tenant's burst starves everyone on shared GPUs.**

> No per-tenant limits. Enforce gateway quotas + concurrency caps per tenant; consider dedicated model deployments/node pools for noisy tenants; backpressure per tenant.

**H5 - Spot GPU interruptions kill in-flight long generations.**

> Long requests on spot. Run latency-critical serving on on-demand GPUs (taint spot for batch only), handle interruption signals to drain, and design clients to retry idempotently. See [01 - Scheduling & Resources Guide](01%20-%20Scheduling%20%26%20Resources%20Guide.md).

[⬆ Back to top](#table-of-contents)

---

## 6. Runbooks

### Runbook: GPU capacity incident (pods Pending)

1. `kubectl describe pod` → `insufficient nvidia.com/gpu`?
2. Device plugin DaemonSet healthy on GPU nodes?
3. Karpenter/CA provisioning GPU nodes? (check logs; GPU instances are capacity-constrained per region/AZ).
4. Short-term: shed load (429), prioritize critical tenants; serve from warm pool.
5. Long-term: raise baseline, reserve capacity, multi-AZ/instance-type GPU NodePools.

### Runbook: latency regression

1. Identify layer via traces (router queue vs prefill vs decode vs downstream).
2. Check GPU utilization/memory (DCGM), batch sizes, queue time.
3. KV-cache affinity working? Recent model/version change? Roll back by routing.
4. Mitigate: scale pods (if GPU headroom), shed load, cap concurrency/context.
5. Add/verify metrics + alerts on p99, queue time, GPU memory.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **LLM serving = GPU-aware platform: one model per pod, sticky routing for KV cache, scale on queue/GPU/latency (not CPU) with warm pools (GPUs provision slowly), prefetch weights to node-local NVMe, MIG/whole-GPU for latency, backpressure with 429s, canary + rollback by routing. On EKS: NVIDIA device plugin + DCGM, taint GPU pools, Karpenter for GPU nodes, on-demand for latency-critical.**

[⬆ Back to top](#table-of-contents)

---

Related: [01 - LLM Inference Guide](01%20-%20LLM%20Inference%20Guide.md) · [01 - Autoscaling Guide](01%20-%20Autoscaling%20Guide.md) · [01 - Scheduling & Resources Guide](01%20-%20Scheduling%20%26%20Resources%20Guide.md) · [01 - Reliability Architectures Guide](01%20-%20Reliability%20Architectures%20Guide.md) · [01 - Observability Guide](01%20-%20Observability%20Guide.md)
