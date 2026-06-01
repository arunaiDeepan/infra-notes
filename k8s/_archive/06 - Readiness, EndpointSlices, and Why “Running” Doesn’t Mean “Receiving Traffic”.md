### Readiness, EndpointSlices, and Why “Running” Doesn’t Mean “Receiving Traffic”

Kubernetes will happily show a Pod as `Running` while also refusing to send it a single packet. That’s not a bug; it’s a safety feature. The traffic gate is **readiness**, and the mechanism that carries readiness into networking is **Endpoints/EndpointSlices**.

A quick glossary so the rest makes sense:

- **Pod phase (`Running`)**: “containers started” (roughly)
- **Pod condition `Ready`**: “this pod should receive traffic”
- **Service**: stable virtual IP + selection rules
- **EndpointSlice**: the _current list of backend IPs_ for a Service (with readiness flags)
- **kube-proxy / eBPF dataplane**: uses EndpointSlices to program load balancing

---

#### 1) Pod lifecycle signals: Phase vs Conditions

A Pod has a high-level `status.phase`:

- Pending → Running → Succeeded/Failed (plus Unknown)

But traffic decisions are based on **conditions**, especially:

- `Initialized`
- `ContainersReady`
- `Ready`
- `PodScheduled`

A Pod can be:

- `Running` but **not Ready** (common during startup)
- `Ready` then become **not Ready** (readiness probe fails or readiness gates fail)
- restarting containers while still `Running` (phase stays Running)

What controls these?

- The **kubelet** sets conditions based on container state and probes.
- Your **Pod spec** defines probes and readiness gates.

---

#### 2) The three probes and what they really mean

These are often confused:

**startupProbe**: “am I done booting?”

- Purpose: prevent liveness/readiness from flapping during slow startups.
- Behavior: while startupProbe is failing, kubelet won’t run liveness/readiness (depending on config), so you get a calm warm-up period.

**readinessProbe**: “should I receive traffic?”

- Purpose: traffic gate. If it fails, the Pod is removed from Service endpoints.
- Behavior: container keeps running; it’s just taken out of load balancing.

**livenessProbe**: “am I stuck and should be restarted?”

- Purpose: restart deadlocked apps.
- Behavior: if it fails enough times, kubelet restarts the container.

Control knob summary:

- Readiness controls traffic.
- Liveness controls restarts.
- Startup prevents premature restarts/traffic gating during boot.

---

#### 3) How readiness becomes “no traffic”: EndpointSlices

When you create a Service with a selector, Kubernetes continuously computes which Pods are “behind” it.

The pipeline looks like this:

1. **Service selector** matches a set of Pods (by labels).
2. The **EndpointSlice controller** watches:
   - Services
   - Pods
   - Readiness status
3. It produces **EndpointSlice objects**, each containing:
   - endpoint IPs (Pod IPs)
   - ports
   - a readiness condition per endpoint (ready/not ready)
4. **kube-proxy** (or eBPF equivalent) watches EndpointSlices and programs the node dataplane accordingly.

So if your Pod is `Running` but not `Ready`, what happens?

- It may still match the Service selector (labels match)
- But EndpointSlice controller marks it not ready (or excludes it)
- kube-proxy won’t load-balance to it
- Result: no traffic reaches it through the Service

This is why “my pod is running but my service is down” is usually a readiness/endpoints story.

---

#### 4) Show me the truth: the commands that prove it

These commands tell you exactly what the cluster believes.

**A) Is the Pod Ready?**

```bash
kubectl get pods -l app=app
kubectl describe pod <pod>
```

Look for:

- `Ready: True/False`

- readiness probe failures in Events

**B) Does the Service have endpoints?**

```bash
kubectl describe svc app-svc
kubectl get endpoints app-svc
kubectl get endpointslices -l kubernetes.io/service-name=app-svc -o wide
```

If EndpointSlices show zero endpoints or all not-ready:

- the Service will appear “dead” even though Pods are Running.

**C) Prove routing from inside the cluster**

```bash
kubectl run tmp-curl --rm -it --image=curlimages/curl -- sh
# inside:
curl -v http://app-svc:80/health
```

If that fails, check EndpointSlices next.

---

#### 5) The common failure patterns (and what they look like)

**Pattern 1: Selector mismatch**

- Pods exist and might even be Ready.
- Service has **zero endpoints**.  
   Cause:

- `.spec.selector` labels don’t match Pod labels.

**Pattern 2: Readiness probe is wrong**

- Pods are Running.
- Readiness fails, so endpoints are empty/not-ready.  
   Classic causes:
- probe hits wrong path (`/health` vs `/healthz`)
- wrong port (container listens on 8080, probe checks 80)
- probe expects 200 but app returns 401/302
- app binds to `127.0.0.1` only

**Pattern 3: Readiness depends on something it can’t reach yet**  
Example: readiness checks a downstream dependency (DB, cache).

- DB is slow → Pods never become Ready → Service has no endpoints → outage.  
   Fix:
- readiness should usually check “can I serve requests?” not “is the entire universe perfect?”

**Pattern 4: Single replica hairpin weirdness**

- Only one pod exists.
- Pod calls the Service name, which routes back to itself.
- If hairpin mode is broken, it fails.  
   Fix:
- call localhost for self-tests or fix hairpin config / use >1 replica.

---

#### 6) Readiness gates: extra traffic blockers you can add

Kubernetes supports **readinessGates**: extra conditions that must be true before a Pod is marked Ready.

These are often used with operators or controllers that need to perform setup before traffic is allowed (e.g., attach something, warm cache, register externally).

So even if readinessProbe is passing, Pod may stay NotReady if a readiness gate condition isn’t met.

Control:

- readinessGates in Pod spec
- some controller is responsible for setting the custom condition

---

#### 7) How rolling updates rely on readiness (and fail without it)

During a Deployment rollout:

- new Pods are created
- they are _not_ added to endpoints until Ready
- old Pods stay serving until new ones are Ready
- then old ones are scaled down

If readiness is too “optimistic” (returns ready too early):

- traffic hits a half-started app → errors  
   If readiness is too “strict” (never returns ready):
- rollout stalls and you never replace old pods

So readiness is your “ship-it safely” lever.

---

#### 8) Best-practice mental model for probes

- startupProbe: “let me boot without being judged”
- readinessProbe: “I can handle traffic right now”
- livenessProbe: “I’m not wedged”

And keep readiness independent of fragile dependencies when possible. You want your service to degrade gracefully, not disappear entirely because one dependency is having a bad day.

---
