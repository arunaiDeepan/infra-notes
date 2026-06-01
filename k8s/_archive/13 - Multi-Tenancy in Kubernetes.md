### Multi-Tenancy in Kubernetes: Practical Isolation (Soft) and Safer Isolation (Hard)

You asked for #2 first, so here’s the full multi-tenancy deep dive, then we’ll roll straight into the “expert tier” topics: audit logging + policy engines, then supply chain security (signing/SBOM/admission).

---

## Part 1: Multi-Tenancy and Namespace Isolation

#### 1) Start with the blunt truth: namespaces are not a security boundary by themselves

Namespaces give you:

- name separation
- a convenient RBAC scope
- quota/limit scoping
- policy scoping (PSA labels)

Namespaces do not automatically give you:

- network isolation
- CPU/memory fairness
- protection from cluster-scoped resource abuse
- protection from node/kernel-level escape attempts

So multi-tenancy is a _bundle_ of controls, not a single feature.

---

### 2) The “soft multi-tenancy” baseline (most real companies)

Goal: prevent accidents and contain blast radius between teams who are not actively malicious.

You want four pillars:

**Pillar A: RBAC boundaries**

- Team can manage resources in their namespace.
- Team cannot create/modify cluster-scoped resources:
  - `ClusterRole`, `ClusterRoleBinding`, `CRD`, `StorageClass`, `Node`, `Namespace` (often)
- Team cannot access `kube-system` or other teams’ namespaces.
- Strongly restrict powerful subresources:
  - `pods/exec`, `pods/attach`, `pods/portforward`, `secrets`

Practical pattern:

- Give “admin within namespace” (a Role/RoleBinding), not cluster-admin.
- Separate roles: deployers vs viewers vs operators.

**Pillar B: Resource governance (Quotas + Limits)**

- **ResourceQuota** caps total usage per namespace:
  - CPU/memory requests & limits
  - number of pods
  - services/loadbalancers
  - PVC/storage consumption

- **LimitRange** enforces per-pod/container defaults:
  - default requests/limits (prevents BestEffort chaos)
  - min/max (prevents a single pod requesting the moon)

Why it matters:

- prevents one tenant from starving the cluster
- makes scheduling and HPA behavior more predictable

**Pillar C: Network isolation (NetworkPolicy)**  
If you don’t enforce NetworkPolicy, assume “east-west is open.”

Baseline model:

- Default deny ingress + egress in each tenant namespace
- Allow:
  - egress to DNS (CoreDNS)
  - ingress from the ingress-controller namespace
  - egress to approved shared services (DB, metrics, logging) explicitly

This turns networking into explicit contracts.

**Pillar D: Pod security (PSA / restricted)**  
Use Pod Security Admission labels:

- tenant namespaces: `restricted`
- shared/system namespaces: `baseline` or carefully `privileged` only when unavoidable

This blocks the classic escape hammers:

- privileged pods
- hostPath mounts
- hostNetwork
- dangerous Linux capabilities
- running as root (in restricted profile)

---

### 3) The “hard multi-tenancy” warning label (untrusted tenants)

If tenants are truly untrusted, Kubernetes on a shared Linux kernel has a big attack surface.

Harder isolation options:

- separate clusters per tenant (cleanest)
- separate node pools per tenant + strict scheduling (taints/tolerations + affinity) + strict PSA + locked RBAC
- sandboxed runtimes (e.g., Kata Containers) to add VM-like isolation per pod
- strict egress controls + service mesh mTLS + zero trust policies
- very strong auditing/monitoring and rapid response

Rule of thumb:

- If you must assume malicious code, prefer cluster separation or sandboxed runtimes.

---

### 4) Multi-tenancy “gotchas” that cause real outages

- Shared labels cause PDBs or NetworkPolicies to match more than intended.
- Default ServiceAccount token automounted everywhere.
- Teams can exec into pods in prod → secrets exfiltration becomes easy.
- No quotas → one CI job creates 500 pods and melts the node pool.
- No topology spread → “isolated tenants” still share the same node and fight for cache/IO.

---

### 5) A concrete baseline checklist (what good looks like)

- Namespace per team/env (`team-a-dev`, `team-a-prod`)
- Dedicated ServiceAccounts per workload; disable token automount unless needed
- RBAC: namespace-admin only; no cluster-admin; restrict exec/attach/portforward
- ResourceQuota + LimitRange in every namespace
- Default-deny NetworkPolicies + explicit allows
- PSA restricted for tenant namespaces
- Separate system components (ingress, DNS, logging) into guarded namespace
- Audit logging enabled; alert on RBAC and admission denials

---

## Part 2: Audit Logs + Policy Engines (catching escalation attempts)

#### 1) Kubernetes audit logs: what they are

Audit logs record API server events:

- who did what (user/serviceaccount)
- what resource
- from where
- whether it was allowed/denied
- request/response metadata (depending on level)

This is your forensic record and your “tripwire” source.

Why it matters:  
Most serious attacks and misconfigs involve the API server:

- someone creates a privileged pod
- someone reads secrets
- someone binds cluster-admin  
   Audit tells you.

#### 2) Audit policy levels (how much you log)

Typical levels:

- Metadata: logs request metadata only (safer, smaller)
- Request: includes request body (bigger, can include sensitive fields)
- RequestResponse: huge, sensitive, rarely used broadly

Best practice vibe:

- log metadata broadly
- selectively log request bodies for high-risk actions (RBAC changes, admissions, etc.)

#### 3) What to alert on (high-signal events)

- creation of `ClusterRoleBinding` / `RoleBinding` granting high privileges
- use of `pods/exec`, `pods/attach`, `pods/portforward` in prod namespaces
- reads of secrets (especially list)
- creation of privileged pods / hostPath / hostNetwork
- failed admission due to policy (often indicates someone tried something forbidden)
- creation/modification of webhook configurations (policy tampering)

#### 4) Policy engines: Gatekeeper / Kyverno

These enforce “how resources must look” at admission time.

Great for:

- require requests/limits
- require non-root + readOnlyRootFilesystem
- deny `latest` tag images
- allow only approved registries
- require signed images (with external verifiers)
- deny hostPath except approved paths
- enforce NetworkPolicy existence per namespace

Kyverno is popular because it’s Kubernetes-native YAML and can mutate too.  
Gatekeeper is popular because it’s OPA/Rego-powered and very expressive.

---

## Part 3: Supply Chain Security: signing, SBOMs, scanning, and admission gates

This is the “don’t let poisoned artifacts enter” layer.

#### 1) The threat: your container image is code shipped from a factory

Risks:

- someone pushes a malicious image to your registry
- dependency compromise (typosquatting, compromised upstream)
- “latest” tag drift
- image built without provenance (who built it? from what source?)
- vulnerable libraries baked in

#### 2) The three big controls

**A) Image immutability**

- Prefer pinned digests (`image@sha256:...`) in prod
- Avoid `:latest`
- Use immutable tags or tag policies

**B) Image scanning + SBOM**

- Scan images for known CVEs
- Generate SBOM (Software Bill of Materials): inventory of packages/components in the image
- Use this for:
  - vulnerability management
  - impact analysis when a library is disclosed

**C) Signature + provenance (the “who built this?” question)**

- Sign images and/or attest provenance
- Enforce signature verification at admission time  
   This prevents “random image with the right name” from being deployed.

Even if scanning misses a zero-day, provenance can stop untrusted builds.

#### 3) Admission as the enforcement point

You can enforce:

- only images from allowed registries
- only signed images
- only images with certain attestations (built by CI, from main branch, etc.)
- block high severity CVEs above threshold (careful: can block emergency deploys)

This is where policy engines + admission webhooks shine.

#### 4) Practical supply-chain “starter kit”

- Disallow `:latest`
- Allow only your registries
- Require digest pinning in prod (or enforce at least for critical workloads)
- Scan in CI and in registry
- Generate SBOM on build
- Sign images built by CI
- Admission gate: only signed images can run in prod namespaces
- Monitor for drift: alert if unsigned/unscanned images appear

---
