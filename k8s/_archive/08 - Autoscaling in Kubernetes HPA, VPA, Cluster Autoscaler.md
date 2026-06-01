### Autoscaling in Kubernetes: HPA, VPA, Cluster Autoscaler, and the Gotchas That Bite

Autoscaling is Kubernetes doing what it does best: “keep nudging the world toward a target.” Except now the target is _performance under load_, and the world includes not just Pods, but sometimes Nodes too. The trap is that there are multiple scalers with overlapping powers, and if you combine them carelessly they’ll wrestle in the mud.

---

#### 1) Horizontal Pod Autoscaler (HPA): scales number of Pods

What it does:

- Adjusts `.spec.replicas` on a Deployment/ReplicaSet/StatefulSet based on metrics.

Most common metric:

- CPU utilization (percentage of requested CPU)
  - This is crucial: HPA CPU scaling uses **usage / request**, not usage / limit.

So if you set CPU request too low:

- utilization looks high
- HPA scales aggressively
- you might over-scale and waste money

If you set CPU request too high:

- utilization looks low
- HPA barely scales
- you might under-scale and get slow

Other metrics:

- Memory utilization (less ideal for many apps)
- Custom metrics (QPS, latency, queue depth) via Prometheus adapter or other metrics pipelines

How it works (loop):

1. Read metrics (metrics-server or custom metrics API).
2. Compute desired replicas:
   - roughly: currentReplicas \* (currentMetric / targetMetric)

3. Apply stabilization rules and scale limits
4. Write new replica count to API server
5. Controllers create/destroy pods → scheduler places them

Key controls:

- `minReplicas`, `maxReplicas`
- target thresholds
- scaling behavior (stabilization windows, scale-up/down rates)

---

#### 2) Metrics-server: the fuel HPA needs

HPA needs metrics. The simplest source is **metrics-server**:

- scrapes kubelet summaries
- provides CPU/memory metrics through the Metrics API

Common pain:

- metrics-server missing or broken → HPA shows “unknown metrics” and doesn’t scale
- kubelet TLS/certs issues in some setups

If you want to scale on application metrics (requests/sec, queue length), you need:

- Prometheus (or similar)
- a metrics adapter (Prometheus Adapter, KEDA, etc.)

---

#### 3) The single biggest HPA gotcha: scaling on CPU for IO-bound apps

CPU is a decent proxy for “work” only if your bottleneck is CPU.
If your app is IO-bound (DB waits, network waits):

- CPU may stay low even while latency is awful
- HPA won’t scale
- users suffer, dashboards lie

Better targets for many services:

- request rate per pod (RPS)
- queue depth (Kafka lag, SQS visible messages)
- p95 latency (careful: feedback loops can get unstable)
- concurrent requests

This is why KEDA exists: it scales based on event sources and queues.

---

#### 4) Stabilization windows: preventing “yo-yo scaling”

Without smoothing, HPA can oscillate:  
load spike → scale up → load drops → scale down → spike again → repeat

Kubernetes supports behavior tuning:

- scale-up quickly but not infinitely fast
- scale-down slowly to avoid flapping

Practical vibe:

- fast scale-up, slow scale-down
- set reasonable minReplicas so you always have baseline capacity

---

#### 5) Vertical Pod Autoscaler (VPA): changes requests/limits

What it does:

- Recommends or automatically adjusts CPU/memory requests (and sometimes limits) for pods based on observed usage.

Modes:

- Off (recommendations only)
- Initial (set requests at pod creation)
- Auto (can evict/recreate pods to apply new requests)

Big gotcha:

- VPA and HPA can conflict on CPU.
- HPA depends on CPU request (utilization = usage/request).
- If VPA changes requests frequently, HPA’s “utilization” math shifts under its feet.

Typical safe combinations:

- HPA on custom metrics + VPA on CPU/memory can be okay.
- HPA on CPU + VPA Auto for CPU is usually a bad idea unless you know exactly what you’re doing.

Where VPA shines:

- memory tuning (reduce OOMs and overprovisioning)
- workloads that don’t scale horizontally (some stateful/legacy services)

---

#### 6) Cluster Autoscaler (CA): adds/removes Nodes

What it does:

- Watches for pods that are Pending due to insufficient resources.
- If pods can’t be scheduled, it adds nodes (via cloud provider / node group).
- If nodes are underutilized and pods can move elsewhere, it removes nodes.

How it decides to scale up:

- “Are there pending pods unschedulable due to CPU/memory/constraints?”
- “If I add one node in this node group, would that allow scheduling?”

How it decides to scale down:

- “Can I drain this node and reschedule its pods elsewhere?”
- Respects:
  - PodDisruptionBudgets (PDBs)
  - daemonsets (they complicate draining)
  - local storage, some affinity rules, etc.

Classic gotchas:

- Strict node affinity / topology constraints prevent rescheduling → scale-down never happens
- Big pods don’t fit on any single node type → they remain Pending forever
- PDB too strict → CA can’t drain nodes → no scale-down

---

#### 7) Putting it together: the “full autoscaling chain”

A common “elastic” setup:

1. Load increases.
2. HPA scales pods from, say, 5 → 20.
3. Scheduler places pods.
4. If nodes run out of allocatable resources, some pods stay Pending.
5. Cluster Autoscaler detects pending unschedulable pods and adds nodes.
6. New nodes join, scheduler places remaining pods.
7. Load drops.
8. HPA scales down pods slowly.
9. Nodes become underutilized.
10. Cluster Autoscaler drains and removes nodes (subject to PDBs and constraints).

If any link breaks, scaling looks “random.”

---

#### 8) KEDA: event-driven autoscaling (worth knowing)

KEDA (Kubernetes Event-driven Autoscaling) scales workloads based on external signals:

- queue length (SQS, Kafka, RabbitMQ)
- Prometheus queries
- cron schedules
- many others

It can even scale to zero cleanly for event-driven jobs/services.

This is often better than CPU HPA for worker systems.

---

#### 9) How to debug autoscaling when it “does nothing”

These checks usually reveal the culprit fast:

**A) Is HPA getting metrics?**

```bash
kubectl get hpa
kubectl describe hpa <name>
```

Look for:

- current metrics vs target
- events about failing to fetch metrics

**B) Are pods Pending? Why?**

```bash
kubectl get pods
kubectl describe pod <pending-pod>
```

Look for:

- “Insufficient cpu/memory”
- affinity/taint issues

**C) Is Cluster Autoscaler running and logging scale decisions?**

```bash
kubectl get pods -A | grep -i autoscaler
kubectl -n <ns> logs deploy/<cluster-autoscaler> --tail=200
```

**D) Requests/limits sanity**  
If CPU requests are tiny, HPA will overreact.  
If requests are huge, nothing schedules.

---

#### 10) A simple “don’t shoot yourself” autoscaling recipe

For stateless web APIs:

- HPA on CPU _or_ (better) HPA on RPS/latency via custom metrics
- reasonable `minReplicas` (avoid cold-start pain)
- Cluster Autoscaler enabled
- keep PDBs sane (allow at least 1 disruption if you have >1 replica)
- set requests based on reality; avoid absurdly tight CPU limits
- use readiness probes so new pods only take traffic when actually ready

For queue workers:

- KEDA on queue depth
- Cluster Autoscaler for nodes
- consider scaling to zero if acceptable

---
