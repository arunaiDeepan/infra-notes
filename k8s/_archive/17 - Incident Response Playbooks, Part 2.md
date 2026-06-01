## Incident Response Playbooks, Part 2: More Real-World “Oh No” Scenarios (and Calm Fixes)

---

## Playbook G: Image pulls failing (ErrImagePull / ImagePullBackOff)

Symptoms:

- pods stuck Pending/ContainerCreating
- events show pull errors

Checks:

```bash
kubectl describe pod <pod>
```

Look for:

- auth failures (registry creds)
- tag not found
- rate limits
- TLS/cert issues

Mitigations:

- roll back to known-good image tag/digest
- fix imagePullSecrets / registry permissions
- use digest pinning for prod (`image@sha256:...`)
- if rate-limited: enable registry mirror/caching, reduce parallel rollouts, use private registry

Root causes:

- “latest” tag drift
- deleted tags
- registry outage
- misconfigured pull secret

---

## Playbook H: Volume mount / attach failures (stateful apps down)

Symptoms:

- pods stuck `ContainerCreating`
- events: `FailedMount`, `AttachVolume.Attach failed`, timeouts

Checks:

```bash
kubectl describe pod <pod>
kubectl describe pvc <pvc>
kubectl get pv
```

Mitigations (pattern-driven):

- if cloud volume “stuck attached” to dead node: detach/force detach (provider-specific)
- check CSI controller/node pods health
- if StorageClass misconfigured: fix SC or PVC parameters
- if multi-attach error: ensure you aren’t trying to mount RWO volume from multiple nodes

Root causes:

- CSI driver upgrade/regression
- node failure leaving volume attachment in limbo
- storage backend outage/quotas

---

## Playbook I: NetworkPolicy-induced outage (accidental self-DDoS by denial)

Symptoms:

- services time out but pods look healthy
- DNS resolution fails in some namespaces
- only certain traffic paths broken (ingress works, internal calls fail, etc.)

Checks:

- verify endpoints exist and pods are Ready
- test from debug pod:

```bash
kubectl run tmp --rm -it --image=curlimages/curl -- sh
# inside:
nslookup <svc>
curl -v http://<svc>.<ns>.svc.cluster.local:<port>/
```

- list policies:

```bash
kubectl get netpol -A
kubectl describe netpol -n <ns> <policy>
```

Mitigations:

- temporarily apply an “allow” policy for critical paths (DNS, ingress-to-app, app-to-db)
- rollback policy change if it correlates with incident
- add canary namespace for policy testing next time

Root causes:

- default deny without required allow rules
- forgetting DNS egress allow (UDP/TCP 53)
- selector mismatch that blocks everything

---

## Playbook J: Ingress outage (routing/TLS/timeouts)

Symptoms:

- 404/502/503 from ingress
- TLS handshake failures
- only external traffic broken; in-cluster service works

Checks:

```bash
kubectl describe ingress <ing>
kubectl -n <ingress-ns> logs deploy/<controller> --tail=200
kubectl get endpointslices -l kubernetes.io/service-name=<backend-svc> -o wide
```

Interpretation:

- 404: rule mismatch (host/path)
- 502/503: backend unreachable/no endpoints/readiness failing
- TLS errors: secret/cert mismatch, SNI host mismatch, cert renewal failure

Mitigations:

- rollback ingress annotation/config change
- fix service port mapping (ingress references svc port; svc maps to targetPort)
- ensure forwarded headers config if app depends on it
- re-issue cert / fix cert-manager issues

---

## Playbook K: Certificate/expiry incidents (the slow-motion disaster)

Symptoms:

- sudden TLS failures at a specific time
- clients reject cert chain

Checks:

- ingress controller logs
- cert-manager resources (if used)
- verify secret contains expected cert

Mitigations:

- renew/reissue cert
- ensure DNS challenge or HTTP challenge path works
- add expiry alerts well before deadline

Root causes:

- cert-manager failing silently
- DNS provider changes
- rate limits from CA

---

## Playbook L: “Stuck terminating” pods / namespaces (finalizers)

Symptoms:

- pod or namespace sits in Terminating forever
- drains never finish

Checks:

```bash
kubectl get pod <pod> -o yaml | grep -i finalizer -n
kubectl get ns <ns> -o json | grep -i finalizer -n
kubectl describe pod <pod>
```

Mitigations:

- fix the controller responsible for removing the finalizer (best)
- last resort: remove finalizer manually (dangerous; can leak resources)

Root causes:

- operator/controller down
- webhook blocking cleanup
- external resource cleanup failing

---

## Playbook M: “Everything is slow” (mystery latency)

This is the most common “high ambiguity” incident.

Fast triage flow:

1. Is it one service or many?
2. Is CPU throttling happening?
3. Is the DB/cache slow?
4. Is DNS slow?
5. Is node pressure high?
6. Is the control plane lagging?

High-signal checks:

- `kubectl top pods/nodes`
- p95 latency graphs
- error rate graphs
- trace breakdown (slow span)
- CoreDNS latency metrics (if you have them)
- node MemoryPressure/DiskPressure

Mitigations:

- scale out stateless tiers
- shed load / rate limit
- rollback recent change
- if CPU throttling: raise CPU limits/requests, or reduce concurrency

---

# Large Cluster Performance and Scalability: Watch Storms, APF, CRD Bloat, and Controller Backpressure

Now the “above topic”: why large clusters melt down, and how to keep them sane.

The performance story in Kubernetes is mostly about:

- API server load (LIST/WATCH)
- etcd write amplification
- too many objects (especially Pods/Endpoints)
- controllers doing too much work too fast
- CRDs that create massive object churn

If you can keep API + etcd happy, clusters stay calm.

---

## 1) The LIST/WATCH model: Kubernetes’ nervous system

Controllers and kubelets usually use:

- LIST to get initial state
- WATCH to subscribe to changes

This is efficient when well-behaved.  
It becomes a disaster when:

- too many clients watch too many resources
- clients repeatedly LIST in tight loops
- controllers resync too aggressively
- large objects cause big payloads
- Endpoint updates are extremely frequent

This is how you get “watch storms.”

Symptoms:

- API server CPU high
- lots of open watch connections
- API latency increases
- controllers fall behind
- nodes may go NotReady (secondary cascade)

Mitigations:

- reduce churn (especially endpoints)
- reduce client polling/listing
- ensure controllers use watches properly
- tune resync periods (avoid tiny resync loops)
- optimize overly chatty operators

---

## 2) Endpoints/EndpointSlices scale pain (services with huge backends)

Classic scaling issue:

- a Service selecting thousands of Pods
- frequent readiness flaps
- endpoints update constantly
- API writes skyrocket

EndpointSlices were introduced to help by sharding endpoints into slices, but churn can still be enormous.

Mitigations:

- reduce backend size per Service (shard services)
- stabilize readiness (avoid flapping probes)
- consider topology-aware routing/hints
- avoid per-request pod churn (don’t make pods too ephemeral)

---

## 3) etcd write pressure: the silent bottleneck

etcd struggles when:

- too many writes/sec (events, endpoints, status updates)
- large objects are stored frequently
- disk is slow

Common write-heavy sources:

- events spam (CrashLoop storms)
- endpoints updates
- custom controllers writing status too frequently
- jobs creating/destroying pods rapidly

Mitigations:

- stabilize workloads (reduce crash loops)
- tune event generation/retention (and fix root causes)
- ensure fast disks for etcd (if self-managed)
- review operators that update status too often

---

## 4) APF: API Priority and Fairness (keeping the API from being hogged)

In big clusters, one noisy client can ruin the API for everyone.

APF lets the API server:

- classify requests into priority levels
- queue and rate limit fairly
- prevent one tenant/controller from starving others

This is a key multi-tenant control-plane protection feature.

Practical use:

- give system components higher priority than user bulk jobs
- keep interactive kubectl usable during load

---

## 5) CRD bloat and operator overload

CRDs are powerful, but they can explode object counts and churn.

Failure patterns:

- CRD objects with huge status fields updated frequently
- operators watching the world and reconciling too often
- webhook latencies affecting every create/update

Mitigations:

- keep CRD schemas lean
- avoid giant status blobs
- rate limit reconciliation loops
- set webhooks timeouts and make them HA
- consider whether every “thing” needs to be a CRD object

---

## 6) Controller backpressure: when reconciliation can’t keep up

When controllers fall behind:

- desired state drifts longer
- rollouts slow
- autoscaling lags
- garbage collection piles up

Signs:

- queue depth metrics (if you have them)
- long reconcile durations
- API server throttling responses
- increased workqueue retries

Mitigations:

- scale controllers (where supported)
- shard controllers by namespace or responsibility
- reduce reconcile frequency and object churn
- improve controller efficiency

---

## 7) Practical “large cluster hygiene”

- Avoid massive single namespaces with extreme pod churn
- Avoid services selecting enormous, flappy backends
- Use ResourceQuota/LimitRange to prevent runaway object creation
- Use APF to protect the API server
- Keep admission webhooks fast and resilient
- Monitor:
  - API latency
  - etcd latency and disk IO
  - watch counts
  - endpoints update rate
  - event rate
  - controller workqueue depths

---

## 8) The clean big-cluster mental model

- API server is your shared bottleneck
- etcd is your write bottleneck
- endpoints/events/status updates create churn
- churn creates load
- load creates latency
- latency breaks leader election/heartbeats
- then the cluster “fails weirdly” rather than “fails cleanly”

Preventing weird failure is mostly about preventing churn and protecting the API.

---
