### Kubernetes Observability Deep Dive: Logs, Metrics, Traces, Events, and Debugging Like a Calm Scientist

Observability in Kubernetes is basically: “figure out what’s happening in a distributed system where everything is ephemeral and lying by omission.” The trick is to combine five signals:

1. Metrics (numbers over time)
2. Logs (text with context)
3. Traces (request journeys)
4. Events (what Kubernetes thinks happened)
5. Resource state (what the API says exists right now)

If you wire these together well, debugging becomes boring-in the best way.

---

## 1) Metrics: the cluster’s vital signs

Metrics answer: “Is it getting worse, when, and where?”

You typically have:

- Node metrics: CPU, memory, disk, network, pressure
- Pod/container metrics: usage, throttling, restarts
- Kubernetes object metrics: desired vs available replicas, HPA status, etc.
- Application metrics: RPS, latency, error rates, queue depth

### What metrics to watch first (high signal)

For a service:

- Request rate (RPS/QPS)
- Error rate (5xx, exceptions)
- Latency (p50/p95/p99)
- Saturation (CPU throttling, memory usage, thread pools, queue depth)

For the platform:

- Node MemoryPressure / DiskPressure counts
- Pod restart rate
- CPU throttling (containers hitting CPU quota)
- etcd / API server latency (if you run the control plane)

### Kubernetes-specific “gotchas” in metrics

- CPU throttling can cause probe failures → endpoints removed → cascading outages.
- Memory usage close to limit + spikes → OOMKills (sudden restarts).
- HPA uses usage/request; if requests are wrong, scaling is wrong.

### Quick commands (if metrics-server exists)

```bash
kubectl top nodes
kubectl top pods -A
```

---

## 2) Logs: the narrative, but only if you add context

Logs answer: “What exactly failed and why?”

Kubernetes logs live at container stdout/stderr (unless you do something fancy). A cluster logging stack typically:

- collects logs via DaemonSet agent (Fluent Bit, Vector, etc.)
- ships to storage/search (Elasticsearch, Loki, cloud logging)
- indexes with labels/metadata

### The #1 logging rule in k8s

Emit structured logs with:

- timestamp
- request_id / trace_id
- user/session (if applicable)
- service name + version
- namespace/pod/node metadata (often injected automatically)  
   Then you can correlate logs to metrics and traces.

### “kubectl logs” is for triage, not your long-term strategy

```bash
kubectl logs <pod> --tail=200
kubectl logs <pod> -c <container> --tail=200
kubectl logs <pod> --previous --tail=200   # after restart
```

If the pod is gone, centralized logs are the only memory.

---

## 3) Traces: the request’s passport stamps

Traces answer: “Where did time go across services?”

A trace shows a request’s path:

- gateway/ingress → service A → service B → DB → cache …  
   Each hop is a span with timing.

Why traces matter in Kubernetes:

- you can’t debug latency in microservices using logs alone without losing years of your life
- traces reveal whether you’re CPU-bound, IO-bound, stuck on locks, or waiting on dependencies

Typical setup:

- OpenTelemetry SDK in apps
- OpenTelemetry Collector in cluster
- backend: Jaeger/Tempo/Zipkin/Cloud APM

### The one correlation that turns chaos into sense

Put the same `trace_id` into:

- logs (as a field)
- traces (as the trace id)  
   Then a single click takes you from “error spike” → “the exact request path” → “the exact log lines.”

---

## 4) Kubernetes Events: the platform’s own diary

Events answer: “What did Kubernetes try to do?”

They’re incredibly useful for:

- scheduling failures (Insufficient CPU/mem, taints)
- image pull errors
- mount/attach errors (CSI)
- probe failures
- eviction reasons
- rollout progress issues

Commands:

```bash
kubectl get events --sort-by=.lastTimestamp
kubectl describe pod <pod>
kubectl describe node <node>
kubectl describe deploy <deploy>
```

Events are ephemeral and can be rotated away, so serious setups ship them to a logging backend too.

---

## 5) State: what the API says is true right now

This is “ground truth” for desired and observed state:

- are endpoints present?
- are pods ready?
- is HPA scaling?
- are nodes pressured?
- did the rollout stall?

High-yield checks:

```bash
kubectl get deploy,rs,pods -o wide
kubectl get svc,ep,endpointslices -o wide
kubectl get hpa
kubectl describe hpa <name>
kubectl describe deploy <name>
```

---

# A practical debugging playbook (SRE-flavored)

Here’s the calm, repeatable flow that prevents “random poking.”

### Step 1: Confirm the symptom in metrics

- Is it error rate, latency, or availability?
- When did it start?
- Is it global or one AZ/node?

### Step 2: Check rollout/change correlation

Most outages are change-related.

- Did a Deployment roll?
- Did config change?
- Did node pool scale/upgrade?

Check:

```bash
kubectl rollout status deploy/<name>
kubectl describe deploy/<name>
kubectl get rs
```

### Step 3: Check endpoints and readiness

“Pods Running but service down” is often endpoints.

```bash
kubectl get endpointslices -l kubernetes.io/service-name=<svc> -o wide
kubectl get pods -l app=<app>
kubectl describe pod <pod>
```

### Step 4: Check node pressure and eviction signals

```bash
kubectl describe node <node>
kubectl get pods -A | grep Evicted
```

### Step 5: Inspect logs with correlation ids

- Find an error trace_id/request_id
- Follow it through services
- Confirm where the failure originates

### Step 6: Use traces for latency mysteries

- Identify the slow span
- Decide if it’s compute, network, downstream dependency, lock contention, or saturation

---

## Golden signals + SLOs (how pros avoid surprises)

The classic “golden signals”:

- Latency
- Traffic
- Errors
- Saturation

Turn these into SLOs:

- “99.9% of requests < 300ms”
- “<0.1% 5xx”  
   Then alert on burn rate, not on “CPU is 80%” (CPU alerts are usually noise unless tied to saturation/throttling).

---

## k8s-specific observability gotchas

- CPU throttling doesn’t look like failure until probes/timeouts happen.
- Pod restarts hide root cause unless you check `--previous` logs and events.
- Without tracing, “who is slow?” becomes politics.
- NetworkPolicy drops look like “random timeouts” unless you have flow logs (Cilium helps here).
- Ingress hides client IP unless forwarded headers are logged.

---

## Recommended “minimum viable observability stack” (conceptually)

- Metrics: Prometheus + Alertmanager (or cloud equivalent)
- Dashboards: Grafana
- Logs: Fluent Bit/Vector → Loki/Elasticsearch/cloud logs
- Traces: OpenTelemetry Collector → Jaeger/Tempo/cloud APM
- Events: ship to logs
- Correlation: trace_id in logs

---
