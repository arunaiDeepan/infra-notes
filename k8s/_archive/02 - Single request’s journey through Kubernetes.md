Imagine you apply two manifests: a `Deployment` and a `Service`.

### 1) `kubectl apply -f deploy.yaml`

What happens:

Your `kubectl` doesn’t “create containers.” It just sends an HTTP request to the **kube-apiserver** (the only doorway).

The API server then does, in order:

1. **Authentication**: “Who are you?” (cert/token/OIDC)
2. **Authorization**: “Are you allowed?” (RBAC)
3. **Admission**: “Do we accept/mutate/deny this object?”
   - Built-in admission controllers + optional webhook policies remember: _this is where org guardrails live_.
4. **Validation + defaulting**: checks schema, fills defaults
5. **Persist**: stores the object in **etcd**

At this moment, your Deployment exists as _desired state_ in etcd. Nothing is running yet.

Control point: You control this stage via kubeconfig creds, RBAC roles/bindings, and admission policies.

---

### 2) Controllers notice: Deployment → ReplicaSet → Pods

Now the fun part: controllers are basically nerdy robots running “watch + reconcile” loops.

- The **Deployment controller** (in kube-controller-manager) is watching the API. It sees a new Deployment and creates a **ReplicaSet** matching that Deployment’s template.
- The **ReplicaSet controller** sees a ReplicaSet that wants, say, 3 replicas and creates **3 Pod objects** (not containers-just Pod specs stored in etcd).

These Pods will initially be in a “Pending” state with no assigned node.

Control point: You control what gets created by the Deployment spec (replicas, pod template, update strategy). The controllers do the boring-but-critical bookkeeping.

---

### 3) Scheduler assigns each Pod to a Node

The **kube-scheduler** watches for Pods that have no `.spec.nodeName`.

For each unscheduled Pod it runs a two-phase logic:

- **Filtering**: which nodes are even eligible?
  - enough CPU/memory vs requests
  - nodeSelector/nodeAffinity match?
  - taints tolerated?
  - required topology constraints satisfied?
  - volumes possible to mount? (important with some storage)

- **Scoring**: among eligible nodes, which is “best”?
  - spread load
  - honor preferred affinities
  - pack vs spread policies, etc.

Then it writes back to the API server: `Pod.spec.nodeName = chosen-node`.

Control point: You steer scheduling with requests/limits, taints/tolerations, affinity/anti-affinity, topology spread, priority classes.

---

### 4) Kubelet on that node makes the Pod real

Each node’s **kubelet** watches the API server for Pods assigned to _it_.
When it sees one:

1. **Pull images** via the container runtime (containerd/CRI-O)
2. **Set up sandbox / namespaces / cgroups**
3. **Mount volumes**
   - ConfigMaps/Secrets (as files or env vars)
   - PVC volumes via CSI driver
4. **Create containers** + start them
5. **Run probes**
   - startupProbe (optional): “is app booted yet?”
   - readinessProbe: “is it ready to receive traffic?”
   - livenessProbe: “is it stuck/dead and needs restart?”
6. **Report status** back to the API server: Pod phase, container statuses, readiness, events

Control point: You control container behavior via Pod spec (image, command, env, volumes, securityContext, probes, resources). The kubelet is the enforcer.

---

### 5) Networking gets wired: CNI assigns Pod IP

When a Pod is created on a node, the kubelet calls the **CNI plugin** to set up networking:

- assigns the Pod an IP
- sets routes / NAT / overlay (depending on plugin)
- attaches it to the node’s network so other Pods can reach it

If you define **NetworkPolicy**, your CNI plugin may enforce it (some plugins don’t enforce policies; most serious ones do).

Control point: You control allowed traffic with NetworkPolicy; you control the networking model by which CNI plugin is installed.

---

### 6) Service becomes reachable: kube-proxy (or eBPF replacement) programs rules

A **Service** gives you a stable virtual IP (ClusterIP) and a consistent name in DNS.

How it’s implemented:

- Kubernetes also maintains **EndpointSlices** for a Service: lists of ready Pod IPs that match the Service selector.
- The **EndpointSlice controller** watches Pods and Services and updates EndpointSlices whenever Pods become ready/unready.

Then, on each node:

- **kube-proxy** watches Services + EndpointSlices.
- It programs node-level rules (iptables or IPVS) so traffic to the Service IP/port is load-balanced across the current ready Pod IPs.

Key subtlety:  
Readiness matters. A Pod that isn’t “Ready” generally won’t be added to endpoints, so it won’t receive Service traffic.

Control point: You control service selection (labels/selectors), ports, and readiness behavior. kube-proxy just makes reality match.

---

### 7) DNS makes it human-usable: CoreDNS updates names

**CoreDNS** watches the API server and serves DNS records like:

- `myservice.myns.svc.cluster.local` → Service ClusterIP
- sometimes per-pod / headless service records too

Inside Pods, the resolver uses the cluster DNS service by default.

Control point: You control names by the Service/Namespace you create; CoreDNS config via a ConfigMap.

---

### 8) Traffic from outside: Ingress / Gateway route to Services

This is where many people get tripped up:

- **Ingress** (or **Gateway API**) is just a _desired-state object_.
- The “real” work is done by an **Ingress Controller** (nginx/traefik/haproxy/etc) or a Gateway controller.

Typical flow:

Internet → cloud LB / node port → Ingress controller → Service → Pod

Steps:

1. You create an Ingress pointing host/path → a Service.
2. Ingress Controller watches the API, notices the Ingress.
3. It updates its own config (routes, TLS, etc).
4. It receives traffic and forwards it to the backend Service.
5. Service rules load-balance to Pods.

Control point: You control routes via Ingress/Gateway objects, TLS via cert-manager or secrets, and exposure via Service type (LoadBalancer/NodePort) or cloud-specific controllers.

---

## Now the “drama arcs”: scaling, failure, and updates

### Scaling up replicas

You run: `kubectl scale deploy myapp --replicas=10`

- API server stores new replica count.
- Deployment controller updates RS desired replicas.
- ReplicaSet controller creates more Pod objects.
- Scheduler assigns them to nodes.
- Kubelets run them
- EndpointSlices update as they become Ready.
- Service load balancing automatically includes them.

No human touches load balancers or config files. It’s reconciliation loops all the way down.

### A Pod dies

Say a container crashes.

- Kubelet notices container exit → restarts it if restartPolicy allows (usually yes in Deployments).
- If the whole Pod is gone (node failure / eviction), ReplicaSet notices actual < desired → creates replacement Pod → scheduler reschedules elsewhere.

Important split:

- Container-level restarts: kubelet.
- Pod replica count replacement: ReplicaSet controller.
- Node failure detection: Node controller (via heartbeats).

### A node goes down

- Kubelet stops reporting.
- Node controller marks it NotReady after grace periods.
- Pods on that node become unavailable; endpoints removed.
- Eventually Pods are rescheduled to healthy nodes (exact timing depends on node eviction settings).

### Rolling update (the classic “ship it” moment)

You change the Deployment image tag.

- Deployment controller creates a _new_ ReplicaSet (new pod template hash).
- It gradually scales up new RS and scales down old RS according to:
  - `maxSurge` (how many extra Pods allowed temporarily)
  - `maxUnavailable` (how many can be down during rollout)
- Readiness gates traffic: new Pods only join endpoints when Ready.
- If something goes wrong:
  - rollout pauses/fails based on progress deadline settings
  - you can `kubectl rollout undo` (it just re-points desired state back)

Control point: Update strategy + probes matter a ton. The “safety” of rolling updates is mostly “readiness done right.”

---

## “Who controls what” cheat-map (very practical)

- **API Server**: gatekeeper (authn/authz/admission). Stores desired state (via etcd).
- **etcd**: truth store (if it’s broken, everything is sad).
- **Controllers**: ensure objects’ relationships match desired state (Deployment→RS→Pods, endpoints, nodes, jobs, etc.).
- **Scheduler**: picks a node.
- **Kubelet + runtime**: actually runs containers; enforces probes/resources.
- **CNI**: gives Pod IP + connectivity + (maybe) NetworkPolicy enforcement.
- **kube-proxy**: implements Services (unless replaced by eBPF dataplane).
- **CoreDNS**: service discovery.
- **Ingress/Gateway controller**: edge routing from outside.

---
