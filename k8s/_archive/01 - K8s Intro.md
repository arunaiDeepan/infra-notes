## K8s architecture

Kubernetes (k8s) architecture is basically a distributed control system for running containers. Think: “desired state” + “reconciliation loops” + “lots of small components that each do one job.” You tell it what you want, and it keeps nudging reality until reality matches.

K8s has **two** big halves:

- the Control Plane (the brain)
- the Worker Nodes (the muscle)

**CONTROL PLANE COMPONENTS**

### 1. **kube-apiserver** (the front door)

    The Kubernetes API server. Everything talks to this. kubectl, controllers, nodes, users, CI/CD, the dashboard, you name it.

**What it’s for:**

- Exposes the Kubernetes API (REST over HTTPS)
- Validates requests (schema validation + admission)
- Authenticates and authorizes
- Persists/reads state via etcd
- Acts like a hub: other control-plane components “watch” it for changes

**How it’s controlled:**

- Runs as a static pod or systemd service depending on setup (kubeadm typically uses static pods)
- Secured with TLS
- Access controlled by:
  - Authentication: certs, tokens, OIDC, etc.
  - Authorization: RBAC (most common), ABAC (rare), webhook
  - Admission controllers: mutating/validating policies (built-ins + custom webhooks)
- You “control” it by configuring:
  - API server flags
  - RBAC policies
  - Admission policies (and in modern clusters, Policy tools like Gatekeeper/Kyverno)

### 2. etcd (the cluster’s memory)

    A distributed key-value store.

**What it’s for:**

- Stores the entire cluster state: objects like Pods, Deployments, Secrets, ConfigMaps, Nodes, etc.
- Source of truth for desired state

**How it’s controlled:**

- Only kube-apiserver should talk to it directly
- Runs as a static pod/service
- Controlled via:
  - etcd cluster membership (quorum matters)
  - TLS auth between apiserver and etcd
  - Backups and compaction/defrag are operational controls

**Important mental model:**
If etcd is unhealthy, Kubernetes is basically amnesiac.

### 3. kube-scheduler (the matchmaker)

    The component that assigns Pods to Nodes.

**What it’s for:**

- Watches for Pods that have no node assigned yet

- Picks the best Node based on:
  - Resource requests/limits (CPU/mem)
  - Node taints/tolerations
  - Affinity/anti-affinity
  - Topology spread constraints
  - Pod priority and preemption
  - Custom scheduling plugins (framework)

How it’s controlled:

- Its decisions are expressed by writing a “binding” back to the API server (Pod -> Node assignment)
- You control scheduling via Pod specs:
  - requests/limits
  - nodeSelector / nodeAffinity
  - taints & tolerations
  - priorityClass
  - topologySpreadConstraints
- Also by cluster config:
  - scheduler policies/plugins (advanced)

### 4. kube-controller-manager (the “fixer” of desired state)

    A bundle of controllers, each a reconciliation loop.

**What it’s for:**  
Controllers watch the API for objects and continuously try to make the real world match desired state. Examples:

- **Deployment controller:** ensures correct ReplicaSets exist
- **ReplicaSet controller:** ensures correct number of Pods exist
- Node controller: marks nodes NotReady if they stop heart beating
- Job controller: runs Pods until completion
- Endpoints/EndpointSlice controller: keeps service endpoints updated
- Namespace controller: handles namespace cleanup
- ServiceAccount controller: default SAs, tokens, etc.

**How it’s controlled:**

- Controlled indirectly by the objects you create:
  - If you create a Deployment, the Deployment controller starts acting.
- Each controller has its own logic and uses the API server to read/write.
- You can extend this model with your own controllers/operators (custom reconciliation loops using CRDs).

### 5. cloud-controller-manager (cloud glue, optional)

    Controllers that integrate Kubernetes with a cloud provider (AWS/GCP/Azure/etc).

**What it’s for:**

- Node lifecycle management in cloud
- Creating LoadBalancers for Services of type LoadBalancer
- Attaching volumes / routes / etc (depends on provider)

**How it’s controlled:**

- By cloud provider config/credentials and Service/Volume objects you create
- In many modern setups, pieces are handled by separate “out-of-tree” controllers (like AWS Load Balancer Controller, external-dns, CSI drivers)

WORKER NODE COMPONENTS

Each worker node runs the pieces that actually run your containers.

1. kubelet (node agent)

   The agent on each node that talks to the API server.

What it’s for:

- Watches for Pods assigned to its node
- Creates/starts/stops containers via the container runtime
- Mounts volumes
- Runs liveness/readiness/startup probes
- Reports status back (Node status, Pod status)

How it’s controlled:

- Controlled by the API server’s PodSpecs (the desired pod definition)
- Configuration via:
  - kubelet config file/flags
  - Node-level settings (cgroups, sysctls, etc.)
- Security boundaries:
  - kubelet has a client cert to authenticate to apiserver
  - kubelet often exposes a local API; access should be locked down (historically a security footgun if open)

1. container runtime (runs containers)

   Software that actually runs containers.

Examples:

- containerd (very common)
- CRI-O (common)  
   Kubernetes talks to it via CRI (Container Runtime Interface).

What it’s for:

- Pull images
- Create containers
- Manage container lifecycle
- Provide logs, exec, etc.

How it’s controlled:

- kubelet issues CRI calls to the runtime
- You control it via:
  - Pod specs (images, commands, resources)
  - Runtime configuration (registries, sandboxes)
  - Image policies and admission rules upstream

1. kube-proxy (service networking rules)  
   A node-level network component that implements Service virtual IPs and load balancing.

What it’s for:

- Watches Services and EndpointSlices
- Programs traffic rules so that:
  - ClusterIP Services route to the right Pods
  - NodePort works
  - LoadBalancer backends work  
     Implementation styles:
- iptables mode (classic)
- IPVS mode (more scalable in some cases)  
   Some modern CNI plugins can replace parts of kube-proxy (“kube-proxy replacement”), but the concept remains: Services need routing/load-balancing.

How it’s controlled:

- Controlled by Service/EndpointSlice objects in the API server
- Operationally configured by kube-proxy config and the chosen mode

NETWORKING LAYER (CNI + DNS)

1. CNI plugin (pod networking)

   Kubernetes doesn’t ship a full networking implementation; it relies on CNI (Container Network Interface) plugins like:

- Calico
- Cilium
- Flannel
- Weave
- Antrea

What it’s for:

- Gives each Pod an IP address
- Ensures Pod-to-Pod connectivity (usually across nodes)
- Often enforces NetworkPolicies (depending on plugin)

How it’s controlled:

- Controlled via:
  - CNI plugin config (daemonsets, CRDs)
  - Kubernetes NetworkPolicy objects (if the plugin supports enforcement)
- If you apply NetworkPolicy, the CNI plugin enforces it at dataplane level (iptables/eBPF/etc depending on plugin)

1. CoreDNS (cluster DNS)

   DNS service for the cluster (usually deployed as a Deployment).

What it’s for:

- Service discovery:
  - myservice.myns.svc.cluster.local -> ClusterIP
- Pod DNS resolution rules
- Often forwards external queries upstream

How it’s controlled:

- Controlled by ConfigMap (CoreDNS config)
- Controlled indirectly by Services/Pods/Namespaces (it reads from the API)

ADD-ON / EXTENSION COMPONENTS (VERY COMMON)

1. Ingress Controller / Gateway API controller

   Ingress is an API object; it does nothing by itself. An Ingress Controller (nginx, HAProxy, Traefik, etc.) actually implements it. Newer approach: Gateway API.

What it’s for:

- HTTP(S) routing into the cluster
- TLS termination
- Virtual hosting, path-based routing

How it’s controlled:

- Ingress / Gateway / HTTPRoute resources you apply
- Controller config (ConfigMaps/CRDs)
- Often integrates with cert-manager for TLS

1. CSI drivers (storage)

   CSI (Container Storage Interface) drivers let Kubernetes provision/mount volumes.

What it’s for:

- Dynamic provisioning of PersistentVolumes
- Attaching/mounting block/file storage
- Snapshots, expansion (depending on driver)

How it’s controlled:

- StorageClass + PVCs (PersistentVolumeClaims)
- CSI driver controllers + node plugins run in the cluster
- Cloud credentials / driver configuration

1. Metrics and Autoscaling (metrics-server, HPA/VPA/Cluster Autoscaler)  
   What it is:

- metrics-server provides resource metrics for HPA
- HPA scales Pods based on CPU/mem/custom metrics
- Cluster Autoscaler adds/removes nodes (cloud)
- VPA adjusts requests/limits (with caution)

How it’s controlled:

- HPA objects, custom metrics adapters
- Cluster Autoscaler config and cloud provider integration

HOW “CONTROL” WORKS IN K8S (THE CORE IDEA)

Kubernetes is control loops all the way down.

1. You submit desired state to kube-apiserver (YAML/JSON).
2. The desired state is stored in etcd.
3. Controllers watch the API and reconcile:
   - “I see a Deployment wants 5 replicas”
   - “I will ensure a ReplicaSet exists”
   - “ReplicaSet will ensure 5 Pods exist”
4. Scheduler assigns Pods to nodes.
5. Kubelets on nodes create containers and report status.
6. Network/storage controllers wire connectivity and volumes.
7. System keeps reconciling forever, because reality loves drifting.

OBJECTS YOU USE TO CONTROL BEHAVIOR (QUICK MAP)

- **Pod:** smallest runnable unit (one or more containers sharing network + volumes)
- Deployment: manages stateless replicas, rolling updates
- StatefulSet: stable identity + storage for stateful apps
- DaemonSet: one Pod per node (agents, CNI, logging)
- Job/CronJob: run-to-completion tasks
- Service: stable virtual IP + load balancing to Pods
- Ingress/Gateway: HTTP routing from outside
- ConfigMap/Secret: configuration injection
- PVC/PV/StorageClass: persistent storage
- Namespace: isolation boundary
- RBAC: who can do what
- NetworkPolicy: allowed network flows
- ResourceQuota/LimitRange: resource governance

SECURITY AND GOVERNANCE CONTROL POINTS

- RBAC: permissions (users/service accounts)
- Admission controllers: enforce rules at API write-time (validate/mutate)
- Pod Security (or PSP legacy): restrict privilege levels (hostNetwork, privileged, etc.)
- NetworkPolicy: block/allow east-west traffic
- Runtime security: seccomp, AppArmor/SELinux, read-only FS, non-root users
- Image policy: restrict registries/tags/signing (via admission)

A “MENTAL DIAGRAM” IN WORDS

- The API server is the brain stem: everything passes through it.
- etcd is memory.
- controllers are tiny robotic custodians.
- scheduler decides “where”.
- kubelet makes it real on each node.
- CNI + kube-proxy make networking behave.
- DNS makes it usable.
- add-ons handle the “real world” edges (LBs, storage, ingress, scaling).
