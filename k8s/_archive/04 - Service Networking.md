Now we turn this into a repeatable “prove each hop” workflow: what to check, what output should look like, and what it means when it doesn’t. This is the stuff that makes you look like a wizard (but really you’re just methodical and slightly annoying to entropy).

I’ll assume:

- Namespace: `default` (swap as needed)
- Host: `app.example.com`
- Ingress name: `app-ing`
- Service name: `app-svc`
- Deployment name: `app`
- Port: `80 -> 8080` (example)

## 0) Start from the desired destination and work inward

First rule: don’t start by staring at pods. Start from the entry point and walk step-by-step.

### A) DNS → should point at your external IP/hostname

From your laptop (outside cluster):

- `nslookup app.example.com` or `dig app.example.com`

You expect:

- an A record (IP) or CNAME to your cloud LB hostname.

If it’s wrong:

- you’re debugging the wrong cluster or the wrong LB. Fix DNS first.

---

## 1) Ingress is being implemented by an actual controller

### A) See the ingress object + status

```bash
kubectl get ingress app-ing
kubectl describe ingress app-ing
```

You expect:

- rules for host/path are present
- backend service name/port matches
- in `describe`, events are not all errors
- `status.loadBalancer` may show an address (depends on setup)

If it’s missing an address:

- either your controller doesn’t publish status, or it’s not watching this Ingress class.

### B) Check ingressClass (common failure)

```bash
kubectl get ingressclass
kubectl get ingress app-ing -o yaml | grep -E "ingressClassName|kubernetes.io/ingress.class"
```

If your controller expects a specific class and your Ingress doesn’t match, it will ignore it.

### C) Verify the controller is running

Common namespaces: `ingress-nginx`, `kube-system`, etc.

```bash
kubectl get pods -A | grep -i ingress
kubectl get deploy -A | grep -i ingress
```

Then:

```bash
kubectl -n <controller-ns> get pods
kubectl -n <controller-ns> logs deploy/<controller-deploy-name> --tail=200
```

You’re looking for:

- “configuration loaded / synced” vibes, not crash loops

- errors about invalid backend service, missing endpoints, bad annotations, etc.

---

## 2) Service wiring: selector → endpoints → ready pods

This is the highest-yield check in Kubernetes.

### A) Does the Service select the right pods?

```bash
kubectl get svc app-svc -o wide
kubectl describe svc app-svc
kubectl get svc app-svc -o yaml
```

In the YAML, check:

- `.spec.selector` labels
- `.spec.ports[*].port` and `.spec.ports[*].targetPort`

Now compare to your Pods’ labels:

```bash
kubectl get pods --show-labels
```

If Service selector labels don’t match pod labels:

- Service will have **zero endpoints**. No amount of “network debugging” fixes that. 🙂

### B) Endpoints / EndpointSlices (truth for “will traffic reach pods?”)

```bash
kubectl get endpoints app-svc
kubectl get endpointslices -l kubernetes.io/service-name=app-svc -o wide
```

You expect:

- at least one endpoint IP listed
- they correspond to your pod IPs
- slices show endpoints as ready

If endpoints are empty:

- either selector mismatch, or pods aren’t Ready, or they’re in a different namespace.

If endpoints exist but traffic fails:

- move to NetworkPolicy / kube-proxy / CNI checks.

---

## 3) Pod health: Ready means “in endpoints and can receive traffic”

### A) Quick health overview

```bash
kubectl get deploy app
kubectl get rs -l app=app -o wide
kubectl get pods -l app=app -o wide
```

You want:

- Deployment AVAILABLE matches desired replicas
- Pods show `READY 1/1` (or `2/2` if sidecars)
- No restarts storm

### B) Inspect one pod deeply

```bash
kubectl describe pod <pod-name>
```

Check:

- Readiness probe results
- Events near the bottom: image pull errors, crash loops, probe failures
- “Ready” condition

### C) Validate container is actually listening on expected port

This catches “app binds to localhost” or wrong port issues.

```bash
kubectl exec -it <pod-name> -- sh -c "ss -lntp || netstat -lntp"
```

You want to see it listening on `0.0.0.0:8080` (or appropriate).

If it’s listening only on `127.0.0.1:8080`:

- Service traffic won’t reach it. Bind to `0.0.0.0`.

---

## 4) Prove in-cluster routing without involving the outside world

Before blaming the LB, test from inside the cluster.

### A) Run a temporary debug pod and curl the service DNS

```bash
kubectl run tmp-curl --rm -it --image=curlimages/curl -- sh
```

Inside:

```sh
nslookup app-svc.default.svc.cluster.local
curl -v http://app-svc:80/health
```

If DNS fails:

- CoreDNS / network issue.

If DNS works but curl fails:

- service endpoints missing, networkpolicy blocking, or app broken.

### B) Curl a Pod IP directly (bypasses Service load balancing)

From that same debug pod:

```sh
kubectl get pods -l app=app -o wide
# take a Pod IP:
curl -v http://<pod-ip>:8080/health
```

Interpretation:

- Pod IP works but Service fails → kube-proxy / Service rules / endpoints mismatch.
- Pod IP fails too → app not listening, CNI, or NetworkPolicy.

---

## 5) NetworkPolicy: the silent assassin

If your cluster uses NetworkPolicy enforcement (Calico/Cilium/etc), check:

```bash
kubectl get netpol -A
kubectl describe netpol -n default <name>
```

Typical failure:

- You allowed ingress only from certain namespaces/labels, but forgot the Ingress controller namespace/labels.
- Or you blocked DNS (UDP/TCP 53) so name resolution breaks.

Quick sanity: allow DNS egress to kube-dns and allow ingress from ingress controller pods.

---

## 6) Node-level plumbing: kube-proxy / dataplane sanity

Only do this after endpoints exist and pods are Ready.

### A) Is kube-proxy healthy (if used)?

```bash
kubectl -n kube-system get ds | grep -i proxy
kubectl -n kube-system get pods -l k8s-app=kube-proxy
kubectl -n kube-system logs -l k8s-app=kube-proxy --tail=200
```

If your CNI replaces kube-proxy, this won’t apply (and you’ll look for that CNI’s agent pods/logs instead).

### B) Check service rules exist on a node (advanced)

On a node, you’d inspect iptables/IPVS rules, but that requires node access:

- iptables: `iptables -t nat -L -n | grep <clusterIP>`
- ipvs: `ipvsadm -Ln`

Not always available in managed clusters. Use it when you can.

---

## 7) External path: LB → NodePort → Ingress

Once inside-cluster curl works, now you prove the outside chain.

### A) Service type and external entry

If you’re using a Service of type LoadBalancer (common for ingress controller):

```bash
kubectl -n <controller-ns> get svc
kubectl -n <controller-ns> describe svc <ingress-svc>
```

You expect:

- `Type: LoadBalancer`
- an EXTERNAL-IP / hostname assigned
- NodePorts allocated

If EXTERNAL-IP is pending:

- cloud controller integration isn’t working (permissions, provider, annotations).

### B) Confirm node health targets (cloud-specific)

This part depends on cloud provider, but the symptom is:

- DNS resolves to LB
- LB exists
- but you get timeouts because no healthy backends

That typically means:

- health check path/port mismatch
- security group/firewall blocks nodeport
- `externalTrafficPolicy: Local` but not enough nodes have ingress pods

---

# A “decision tree” you can memorize

- If Service has **no endpoints** → it’s labels or readiness (not networking).

- If endpoints exist and Pod IP curl works but Service curl fails → kube-proxy / dataplane / Service port mapping.

- If in-cluster Service curl works but outside fails → LB / NodePort / Ingress exposure issue.

- If DNS in-cluster fails → CoreDNS or NetworkPolicy blocking DNS.

---

## The 10 commands I’d keep on a sticky note

```bash
kubectl get ingress,svc,ep,endpointslices,pods -o wide
kubectl describe ingress <ing>
kubectl describe svc <svc>
kubectl get endpointslices -l kubernetes.io/service-name=<svc> -o wide
kubectl describe pod <pod>
kubectl logs <pod> --tail=200
kubectl run tmp-curl --rm -it --image=curlimages/curl -- sh
# inside tmp-curl: nslookup <svc>; curl -v http://<svc>:<port>/health
kubectl get netpol -A
kubectl -n kube-system logs -l k8s-app=kube-proxy --tail=200
```
