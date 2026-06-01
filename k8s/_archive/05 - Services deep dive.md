Let’s go full “under the hood”: how **ClusterIP Services** actually work at the packet level, why **SNAT/hairpin** gets weird, and how **iptables vs IPVS vs eBPF** changes the story. This is the part where Kubernetes stops feeling like YAML magic and starts feeling like Linux networking wearing a trench coat.

## 1) The weird truth: a ClusterIP isn’t a real IP on an interface

A Service `ClusterIP` looks like an IP (say `10.96.12.34`), but no network interface actually owns it.

Instead, packets destined to that IP are intercepted by **node-level dataplane rules** (traditionally programmed by **kube-proxy**). Those rules rewrite/steer traffic to real Pod IPs.

So “Service discovery” is:

- DNS returns the ClusterIP
- dataplane rewrites ClusterIP → one of the endpoint Pod IPs

## 2) iptables mode: the classic kube-proxy implementation

In iptables mode, kube-proxy creates a bunch of NAT rules in the node.

Conceptually:

1. Your Pod sends a packet to `10.96.12.34:80` (ClusterIP:port).
2. On the node, iptables sees destination matches a Service IP/port.
3. iptables jumps into a chain for that Service.
4. It probabilistically picks an endpoint (Pod IP:targetPort).
5. It does DNAT: destination changes from `ClusterIP:80` → `PodIP:8080`.
6. Connection tracking (conntrack) remembers this mapping so return traffic works.

Key properties:

- Load balancing is done by iptables rules with random/probability matching.
- It’s simple but can get heavy with huge numbers of services/endpoints (lots of rules).
- Debugging often involves reading iptables chains, which is… character-building.

### Where does SNAT happen in iptables mode?

Often, kube-proxy also uses SNAT (“masquerade”) in specific cases to make return traffic reliable. The main trigger is: **when the chosen endpoint is on a different node** and routing symmetry might be weird.

So packets might be rewritten like:

- Source IP becomes the node IP (SNAT)
- Destination IP becomes the Pod IP (DNAT)

This is why apps sometimes don’t see the original client Pod IP.

## 3) IPVS mode: a more “real load balancer” approach

IPVS is a Linux kernel load balancer. In IPVS mode, kube-proxy programs virtual services and real servers into IPVS rather than huge iptables rule sets.

Conceptually:

- Service ClusterIP:port becomes an IPVS “virtual service”
- Each endpoint Pod IP:port becomes a “real server”
- IPVS picks a backend using algorithms (round-robin, least connections, etc.)

Pros:

- Scales better with lots of services/endpoints
- More predictable performance than giant iptables tables

Still uses iptables for some plumbing (like getting packets into IPVS), but the balancing is in IPVS.

## 4) Hairpin traffic: when a Pod calls a Service that sends it back… to itself

Hairpin is the “snake eating its own tail” scenario.

Example:

- Pod A sends request to Service S (ClusterIP).
- kube-proxy load-balances and picks… Pod A itself as the endpoint.
- Now Pod A is effectively calling itself through the Service abstraction.

This can break if the network doesn’t allow a packet to:

- leave the pod veth
- hit NAT/load balancing
- come back into the same pod through the bridge/veth

Symptoms:

- Pod can reach other pods through Service but not itself via Service
- or random timeouts when only one replica exists (so it always hairpins)

Fixes/requirements depend on CNI:

- enable hairpin mode on bridge/veth
- correct kubelet/CNI settings
- some CNIs handle it cleanly; some require explicit config

Why you should care:

- single-replica services + readiness checks + service-based calls can trip on hairpin issues

## 5) ExternalTrafficPolicy and client IP preservation (SNAT trade-offs)

For traffic coming from outside via NodePort/LoadBalancer:

### `externalTrafficPolicy: Cluster` (default-ish)

- Any node can accept traffic and forward to endpoints on any node.
- But SNAT is common, so the backend may see source IP as a node IP.
- Pros: better load distribution and resilience
- Cons: client IP often not preserved

### `externalTrafficPolicy: Local`

- Node only forwards to endpoints local to that node.
- Preserves client IP more often (less SNAT needed).
- Pros: better for logs/security that depend on real client IP
- Cons: you must ensure endpoints exist on enough nodes, or some nodes will drop traffic (LB health checks matter)

This is why “preserve client IP” is never free. It’s paid for with scheduling constraints and LB health logic.

## 6) eBPF CNIs (Cilium etc.): same semantics, different machinery

eBPF-based dataplanes often replace kube-proxy and iptables-heavy NAT with eBPF programs attached to hooks in the kernel.

What changes:

- Fewer giant iptables rule sets
- More direct, efficient load balancing in-kernel
- Often better observability (flow logs, drops, policy decisions)
- NetworkPolicy enforcement can also be eBPF-based and faster

What doesn’t change:

- Service still maps ClusterIP → endpoints
- readiness still controls endpoints
- traffic still traverses node dataplane, just implemented differently

Net effect:

- performance and debugging improve
- fewer “iptables spaghetti” moments
- but you now debug using the CNI’s tooling (e.g., cilium monitor)

## 7) “Why does my app see weird source IPs?”

There are two different “source IP stories” depending on layer:

### L4 story (TCP/UDP forwarding)

If it’s pure forwarding (no L7 proxy), source IP might be preserved _unless SNAT happens_.

SNAT happens due to:

- cross-node forwarding requirements
- NodePort behaviors
- certain kube-proxy masquerade rules
- cloud LB behavior

### L7 story (Ingress controller / reverse proxy)

Ingress usually terminates and re-initiates connections:

- client → ingress (connection 1)
- ingress → backend (connection 2)

Backends often see the ingress pod IP as source IP.  
Client IP is carried in headers like:

- `X-Forwarded-For`
- `X-Real-IP`  
   or via PROXY protocol if configured.

So if you’re behind an Ingress: rely on forwarded headers, not raw TCP source IP.

## 8) What you can check in practice (without node SSH vs with it)

### Without node access (managed cluster friendly)

- Check endpoints:
  - `kubectl get endpointslices -l kubernetes.io/service-name=<svc> -o wide`
- Check if pods are Ready:
  - `kubectl get pods -l app=...`
- Prove Service works from inside:
  - run temp curl pod and curl service + pod IP
- Check kube-proxy logs/health (if kube-proxy exists)

### With node access (deep debugging)

- iptables NAT chains: look for KUBE-SVC / KUBE-SEP rules
- conntrack entries (why is return traffic broken?)
- IPVS tables if in IPVS mode
- CNI routes/encapsulation state

## 9) The “one replica gotcha” (very common)

If you have a Service with only 1 Pod replica:

- every request to the Service will go to that same Pod
- if hairpin is broken, the Pod may fail calling itself via the Service
- readiness checks that call the Service can deadlock (“I’m not ready until I can call myself through the Service that only points to me”)

Fix: call `localhost` for self-checks, or ensure hairpin support, or use more replicas.

---
