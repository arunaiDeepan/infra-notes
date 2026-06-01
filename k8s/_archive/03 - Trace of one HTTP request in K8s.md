Let’s trace one real HTTP request all the way through the beast: from “some human on the internet” → your container → response back.

Assume you have:

- A `Deployment` of Pods (your app)
- A `Service` (ClusterIP) in front of them
- An `Ingress` (or Gateway API) exposing it externally
- An Ingress Controller (like nginx/traefik) running inside the cluster
- A cloud Load Balancer (or some external LB) in front

### The cast of characters for this request

- Client: browser / curl
- External Load Balancer: “public entry point”
- Node(s): worker machines
- Ingress Controller Pod: reverse proxy inside the cluster
- Service: stable virtual IP + port
- EndpointSlices: list of ready Pod IPs
- kube-proxy: programs data-plane rules (iptables/IPVS), unless replaced
- CNI plugin: the Pod network plumbing
- Your app Pod: the final destination

Now the story.

## 1) Client resolves DNS and connects

Client asks DNS: `app.example.com` → gets an IP address (usually the external LB’s public IP).

Then TCP handshake happens (and TLS handshake too if HTTPS). At this point you’re on the internet and nothing “Kubernetes-y” has happened yet.

Control knobs here:

- DNS provider config
- TLS cert config (often via cert-manager → secret used by Ingress)

## 2) External Load Balancer receives the connection

The public LB (cloud LB, metalLB, F5, nginx outside the cluster, etc.) accepts the connection and forwards it to the cluster.

There are two common ways it forwards:

A) To a NodePort on worker nodes (super common)

- The LB targets: `nodeIP:nodePort`

B) Directly to Ingress Controller Pods (less common unless using special integrations)

- LB targets Pod IPs (requires networking support)

Let’s take the common path: LB → NodePort.

Control knobs:

- `Service` type `LoadBalancer` and provider integration determine LB creation/behavior
- health checks decide which nodes get traffic

## 3) Node receives traffic on the NodePort

Traffic hits a worker node’s network interface on the NodePort (say 30xxx). Now Kubernetes networking begins.

The node must forward this to the Ingress Controller that is “responsible” for that service.

How that’s implemented depends on the dataplane:

- Classic: kube-proxy programs **iptables** or **IPVS**
- Modern: some CNIs use **eBPF** and may replace kube-proxy logic

But conceptually it’s the same: “traffic to this NodePort goes to some backend endpoint.”

Two subtly different NodePort behaviors exist:

- **Cluster-wide load balancing** (can send to any backend Pod on any node)
- **Local-only** (`externalTrafficPolicy: Local`) keeps traffic on nodes that actually have an ingress pod, preserving client source IP more easily

So at this step, the node’s dataplane chooses a backend for the NodePort service.

Control knobs:

- `externalTrafficPolicy: Cluster` vs `Local`
- kube-proxy mode (iptables/IPVS)
- CNI/eBPF replacement behavior

## 4) Traffic gets to the Ingress Controller Pod

Now the packet is forwarded to the Ingress Controller Pod IP and port (usually 80/443 inside the cluster, or whatever it listens on).

How does it get there?

- The node routes to the destination Pod IP using routes created by the CNI plugin (overlay, BGP, VXLAN, native routing-depends on CNI).
- If the Pod is on the same node, it’s basically local bridging + veth pair.
- If it’s on another node, it goes across the cluster network according to CNI’s routing/encapsulation rules.

At the destination node, the packet enters the Pod network namespace via the veth interface attached to that Pod.

Ingress Controller receives it and now behaves like a reverse proxy:

- picks a route based on host/path (`Host: app.example.com`, `/api`, etc.)
- optionally terminates TLS and re-issues HTTP to backend
- can do rate limits, auth, rewrites, gzip, etc.

Control knobs:

- Ingress/Gateway objects (routing rules)
- Ingress controller config (timeouts, headers, TLS, etc.)

## 5) Ingress Controller forwards to your Service (ClusterIP)

Here’s a key concept: an Ingress usually forwards to a Kubernetes **Service**. The Service has a stable virtual IP (ClusterIP). That IP is not “a real interface.” It’s virtual, implemented by dataplane rules.

So the Ingress Controller makes an outbound connection to something like:

- `myapp.default.svc.cluster.local:8080`  
   DNS resolves that to the **Service ClusterIP**.

Now the Ingress Controller sends packets to the ClusterIP.

Control knobs:

- Service ports/targetPorts

- DNS naming (namespace, service name)

## 6) ClusterIP is load-balanced to a backend Pod

This is where **EndpointSlices + kube-proxy** (or eBPF replacement) do their magic.

- EndpointSlice controller keeps an updated list of “ready endpoints” (Pod IPs) for the Service.
- kube-proxy watches those slices and programs rules:

So traffic to `ClusterIP:port` gets rewritten/forwarded to one of the endpoint Pod IPs (and often a Node-level decision picks which endpoint).

Important: only Pods that are “Ready” usually appear as endpoints. That’s how readiness probes become traffic safety.

Control knobs:

- readinessProbe correctness (massively important)
- session affinity (`ClientIP`) if enabled
- topology hints / traffic policy (where supported)

## 7) Packet travels to the chosen Pod IP

Now the packet is heading to your app Pod.

If the Pod is on the same node:

- it’s basically a short hop: node → veth → pod namespace

If the Pod is on a different node:

- node routes it over the cluster network (possibly encapsulated) to the other node
- other node delivers it to the Pod’s veth interface

At the Pod:

- your container’s process receives the request (through the Pod’s network namespace)
- app responds
- response packets go back along the established connection path

## 8) Return path (responses)

Return traffic usually “just works” because it follows connection tracking (conntrack) and NAT rules in the node.

But this is where the famous “why is my client IP lost?” question lives.

### Client IP preservation: why it changes

There are a few spots where source IP can be NAT’d:

- External LB may SNAT
- NodePort forwarding may SNAT depending on policy/mode
- Some ingress setups terminate and re-originate connections (L7 proxy), which changes what the backend sees unless headers are used (e.g., `X-Forwarded-For`)

If you need real client IP at the app:

- Ingress usually adds `X-Forwarded-For` and friends
- You may configure `externalTrafficPolicy: Local` to avoid certain SNATs (tradeoff: fewer nodes eligible for traffic)
- Some LBs support proxy protocol

Control knobs:

- `externalTrafficPolicy`
- Ingress controller real-ip / forwarded headers config
- LB settings (proxy protocol / preserve client IP)

---

# A brutally practical “debug mental checklist” for this path

When traffic fails, it’s almost always one of these:

1. DNS points to wrong place (wrong LB IP / stale record)
2. LB health checks failing (no nodes marked healthy)
3. NodePort not reachable (security groups/firewalls)
4. Ingress controller not running/ready
5. Ingress rule mismatch (host/path wrong)
6. Service selector wrong (no endpoints)
7. Pods not Ready (readiness probe failing)
8. NetworkPolicy blocking
9. App listening on wrong port / wrong interface
10. TLS mismatch (cert/hostname)

If you run `kubectl get endpointslices` and you see zero endpoints, the problem is not “networking” yet; it’s labels/readiness.

---

## Common variants (same movie, different camera angles)

### Variant A: No Ingress, just Service type LoadBalancer

Client → cloud LB → node → Service → Pod  
Ingress controller step disappears. Everything else is the same.

### Variant B: Service mesh (Istio/Linkerd)

Now you have sidecars:  
Ingress → Service → (sidecar proxy) → app container  
Routing, retries, mTLS, etc. happen at the sidecar layer.

### Variant C: eBPF dataplane (Cilium etc.)

Conceptually identical, but instead of iptables/IPVS, the forwarding and LB rules happen in eBPF programs. Often faster and easier to observe, but still the same objects: Service → endpoints → load balance.

### Variant D: HostNetwork or HostPort

Pods share node network namespace (hostNetwork), so Pod IP behavior changes a lot. Often used for low-level networking components, not typical apps.

---
