K8s for LLM inference is basically “a GPU-aware serving platform” where the hard problems are (1) scheduling expensive GPUs sanely, (2) keeping tail latency under control, and (3) scaling without cold-start pain. The architecture ends up looking like a few specialized layers: edge routing, model serving pods on GPU nodes, model artifact distribution, and a control plane of autoscalers + observability + policies.

Here’s a solid, real-world reference architecture.

**1) Request path and routing (the “front door”)**

Clients → (optional API gateway) → Ingress/Gateway → “router” service → model servers

- **Ingress / Gateway API**: terminates TLS, enforces basic limits, routes `/v1/chat/completions` etc.
- **API gateway** (optional but common): auth (JWT/API keys), quotas, per-tenant limits, request/response logging, abuse protection.
- **Inference router** (highly recommended): this is a lightweight stateless service that decides _where_ to send a request:
  - picks a model (and sometimes a version) based on endpoint/tenant
  - implements load shedding, backpressure, retries (carefully), and request hedging (rarely)
  - does “sticky” routing if you use KV-cache affinity (explained below)
  - can do batching coordination if your backend doesn’t handle it well

Why this layer exists: Ingress only knows L7 routing rules; it doesn’t understand GPU queue depth, model residency, or “this request must stick to the pod that already has the KV cache.”

**2) Model serving layer (GPU pods)**

This is the heart. Typical serving stacks:

- **vLLM** (popular for high-throughput decoding with paged attention / efficient KV cache)
- **NVIDIA Triton** (general inference server; can serve ensembles; often used with TensorRT-LLM)
- **Text Generation Inference (TGI)** (Hugging Face)
- **TensorRT-LLM** based servers (when squeezing max performance)

Each model server pod typically includes:

- the model server process
- a sidecar (optional) for metrics/log shipping
- a “model loader” init container (optional) to stage weights locally

Key design choice: **one model per pod** vs **multi-model per pod**  
For LLMs, “one model per pod” is the common reliability/perf choice because GPU memory is the constraint and mixing models often causes cache thrash.

**3) GPU node pools and scheduling (where k8s needs help)**

You almost always want separate node pools:

- **gpu-inference**: GPU nodes dedicated to serving
- **system**: ingress, dns, metrics, logging, controllers
- **cpu-services**: routers, gateways, misc services
- (optional) **gpu-batch**: offline jobs / fine-tuning / embedding backfills

Scheduling controls that matter:

- **node affinity**: model pods only land on gpu-inference nodes
- **taints/tolerations**: keep non-GPU workloads off GPU nodes
- **GPU resource requests**: `nvidia.com/gpu: 1` (or MIG slices if you use MIG)
- **Pod anti-affinity / topology spread**: spread replicas across nodes/zones
- **priority classes**: protect inference pods from eviction vs best-effort batch

For sharing GPUs, you have two main patterns:

- **MIG (Multi-Instance GPU)**: slice GPUs into fixed partitions; k8s schedules slices like resources. Great for predictability.
- **Time-slicing / sharing**: more flexible but trickier for latency predictability.

**4) Model artifacts: how weights get onto nodes without pain**

LLM weights are huge, so “just pull from S3 at startup” can be a latency and reliability disaster.

Common patterns:

- **Warm local NVMe cache per node**:
  - a DaemonSet prefetches model weights to node-local disk
  - model pods mount that path (read-only) using hostPath or a local PV (careful, but common)
  - startup becomes “load from local disk,” not “download 40–200GB”
- **Shared high-throughput storage**:
  - NFS-like RWX can be too slow
  - object store is fine for distribution but not always for direct mmap-style reads
- **Image baking** (sometimes):
  - build weights into the container image (often too big and slow to distribute)

Pragmatic best practice: **prefetch to node-local disk + checksum + versioned directories**.

**5) KV cache, batching, and tail latency (the performance dragon)**

LLM inference performance is dominated by:

- **prefill** (processing prompt tokens)
- **decode** (generating tokens)
- and **KV cache** behavior (memory + reuse)

Modern serving systems do:

- **continuous batching**: dynamically batch requests during decode
- **token-level scheduling**: fair sharing between requests
- **prefill/decode separation** (sometimes): different pods or different queues

Routing implications:

- If you benefit from **KV cache reuse** (same conversation continuing), you want **session affinity**:
  - router pins a conversation/session to the same backend pod
  - otherwise you lose cache and pay prefill cost again
- For multi-replica model serving, implement sticky routing at the **router**, not at Ingress.

Backpressure:

- When GPU queue is deep, do not keep accepting requests until everything times out.
- Prefer explicit **429/503 with Retry-After**, or “shed load” policies per tenant.

**6) Autoscaling: HPA isn’t enough (you need queue/latency signals and node scaling)**

For LLM inference, scaling on CPU is usually meaningless. Better signals:

- **in-flight requests**
- **GPU utilization**
- **tokens/sec**, **queue depth**
- **p95/p99 latency**
- **prefill queue time** / **decode queue time**

Scaling layers:

- **Pod scaling**: HPA on custom metrics or **KEDA** (great for queue-based scaling)
- **Node scaling**: **Cluster Autoscaler** adds GPU nodes when pods are Pending
- **Warm pools** (very important): keep some GPU capacity idle or pre-warmed to avoid multi-minute cold starts

Reality check: GPU nodes are slow to provision. If you rely purely on reactive scaling, you’ll have “traffic spike → 10 minute outage.” The fix is a baseline capacity + predictive scaling (scheduled scaling, or scale based on leading indicators).

**7) Rollouts and model versioning (don’t nuke performance mid-day)**

Recommended pattern:

- **blue/green or canary at the router level**
  - run v1 and v2 model deployments side by side
  - router sends 1% traffic to v2, then 5%, then 25%…
- Keep an eye on:
  - latency distribution (p95/p99)
  - output quality metrics (if you measure)
  - GPU memory headroom and OOM rates
- Roll back by routing, not by deleting pods.

**8) Observability for inference (what to measure)**

You want metrics at three layers:

Model-server metrics:

- tokens/sec (prefill + decode)
- queue time (prefill/decode)
- batch sizes over time
- GPU memory usage, OOM count
- request cancellations and timeouts

Router metrics:

- request rate per tenant/model
- routing decisions (which backend)
- rejections (429/503), retry counts
- end-to-end latency histograms

Cluster metrics:

- GPU utilization, GPU memory, throttling
- pod pending reasons (insufficient GPUs)
- node provisioning time
- network throughput (weights pulls can saturate)

Tracing is super useful if you include “router → backend → streaming tokens” spans.

**9) Security and multi-tenancy (LLM serving is a juicy target)**

- Strong authn/authz at gateway (tenant identity)
- Per-tenant quotas and concurrency caps
- NetworkPolicy: deny-by-default, allow only required flows
- Separate namespaces per tenant or per environment
- RBAC: workloads should not read arbitrary secrets
- Secret management: external secrets + workload identity (no static cloud keys)
- Admission policies: enforce resource requests, disallow privileged pods on GPU nodes

**10) A concrete “gold standard” topology**

- `ingress` namespace: Ingress/Gateway + cert-manager
- `llm-routing` namespace: router service (stateless), auth gateway
- `llm-serving` namespace:
  - `model-a-v1` Deployment (GPU)
  - `model-a-v2` Deployment (GPU)
  - `model-b` Deployment (GPU)
  - PDBs, topology spread, strict requests/limits
- `platform` namespace: observability, policy engines
- GPU node pool with taints; system node pool separate
- DaemonSet on GPU nodes: model prefetcher + NVIDIA device plugin (+ DCGM exporter for GPU metrics)

---
