# Secrets Management in Kubernetes: Secrets, Encryption, External Stores, and Workload Identity

Kubernetes “Secrets” are… fine. They’re not magical vaults. They’re more like: “a convenient API object for sensitive bytes” that you must wrap in real operational security. Let’s go from baseline to robust setups.

#### 1) What a Kubernetes Secret actually is

A Secret is stored in etcd and delivered to Pods via:

- mounted files (volume)
- environment variables
- pulled by the API from inside the cluster (apps using k8s API)

Important: Secret data is **base64-encoded**, not encrypted by default. Base64 is just “bytes-to-text,” not security.

So the real security questions are:

- who can read secrets via the API?
- are secrets encrypted at rest in etcd?
- how are secrets injected into pods?
- can we avoid static secrets entirely?

#### 2) The threat model you should assume

If an attacker gets:

- a ServiceAccount with `get/list secrets` → they can read secrets

- exec access into a pod that has secrets mounted → they can steal them

- access to etcd backups/snapshots → they can extract secrets unless encrypted-at-rest is enabled

- node access → they can often read pod volumes and credentials

So secrets management is tied to RBAC, node security, and supply-chain controls.

#### 3) Encryption at rest (etcd): the minimum serious step

Kubernetes supports encrypting certain resources (including Secrets) at rest in etcd using an encryption provider configuration (commonly AES-GCM), with optional key rotation.

What it protects against:

- someone reading etcd data or backups directly

What it doesn’t protect against:

- someone with permission to read the Secret via the API
- someone inside a compromised pod where the secret is mounted

Still, encryption-at-rest is a baseline for regulated environments.

#### 4) How secrets get into pods: choose the least-bad method

**A) Environment variables**  
Pros:

- simple  
   Cons:
- can leak via process dumps, logs, debug endpoints, or `kubectl describe`-style exposure patterns in some tooling
- doesn’t rotate cleanly (process must restart to get new env vars)

**B) Mounted as files (secret volume)**  
Pros:

- can update (Kubernetes can refresh the volume content)
- apps can re-read without restart (if designed)  
   Cons:
- still present on node disk/memory paths; pod compromise can read it

**C) CSI Secret Store (mount from external vault)**  
Pros:

- avoid storing secret value in Kubernetes at all (or keep it minimal)
- can integrate with rotation patterns  
   Cons:
- adds components and operational complexity

Rule of thumb:

- If you care about rotation and reducing blast radius, prefer file mounts or external stores over env vars.

#### 5) External secret stores: don’t make Kubernetes your vault

Common approaches:

- HashiCorp Vault
- AWS Secrets Manager / Parameter Store
- GCP Secret Manager
- Azure Key Vault

Typical patterns:  
**Pattern 1: External Secrets Operator**

- Operator reads from external store and creates Kubernetes Secrets.
- Nice UX, but secrets still end up in Kubernetes (so RBAC matters).

**Pattern 2: Secrets Store CSI Driver**

- Pods mount secrets directly from external store via CSI.
- Optionally sync to Kubernetes Secret (you can disable syncing if you want to keep k8s “blind”).

This is often the best “enterprise” model: external vault as source of truth, Kubernetes as delivery mechanism.

#### 6) Workload identity: kill static cloud keys

Static cloud access keys inside Secrets are one of the worst recurring problems.

Workload identity means:

- Pods get short-lived credentials based on their identity (ServiceAccount) without storing long-lived keys.

Examples by cloud:

- AWS: IRSA (IAM Roles for Service Accounts)
- GCP: Workload Identity
- Azure: Workload Identity (federated identity)

Benefits:

- no long-lived cloud keys in Secrets
- easier rotation (it’s automatic)
- tighter scoping: IAM role per workload

This is the modern gold standard: use identity federation instead of embedding credentials.

#### 7) Rotation: the part everyone forgets

A secret that never rotates is a liability that grows with time.

Rotation options:

- external store rotates, pods read dynamically (best if app supports reload)
- external store rotates, operator updates k8s Secret, then rollout restart the deployment
- short-lived tokens by design (workload identity, Vault dynamic secrets)

Operational reality:

- many apps can’t hot-reload secrets, so rotation implies restart → plan for it (PDBs + rolling updates + readiness).

#### 8) Practical least-privilege rules for secrets

- Most apps should NOT have API permission to list/get arbitrary Secrets.
- Prefer mounting only the secrets needed by that pod.
- Disable SA token automount if not needed.
- Use separate namespaces/SA per environment.
- Limit who can `pods/exec` in prod; exec is basically “shell access.”

---

### Multi-Tenancy and Namespace Isolation: Quotas, RBAC Boundaries, NetworkPolicy, and “Soft vs Hard Walls”

Kubernetes is not a perfect multi-tenant OS by default. Namespaces are a strong organizational tool, but isolation depends on configuration. The real question is: are you doing “multiple teams” (soft multi-tenancy) or “mutually untrusting tenants” (hard multi-tenancy)? The second one is much harder.

#### 1) Namespaces: what they isolate and what they don’t

Namespaces isolate:

- names of objects (you can have `svc/foo` in multiple namespaces)
- many RBAC scopes
- quotas/limits per namespace
- some policy settings (Pod Security Admission via labels)

Namespaces do NOT automatically isolate:

- network traffic (without NetworkPolicy)
- node-level resources (noisy neighbor problems)
- cluster-wide objects (CRDs, nodes, storage classes, clusterroles)
- the Kubernetes API itself unless RBAC is tight

So a namespace is a boundary only if you enforce it.

#### 2) RBAC boundaries: the first isolation layer

Good multi-tenant RBAC rules:

- teams can manage their namespace resources (deployments, services, configmaps)
- teams cannot read secrets outside their namespace
- teams cannot create cluster-scoped objects (ClusterRoleBinding, CRDs, StorageClasses)
- teams cannot access nodes or kube-system
- restrict `pods/exec`, `pods/attach`, `portforward` in production

Common footgun:

- giving teams “edit” cluster-wide or binding `cluster-admin` for convenience. That ends multi-tenancy instantly.

#### 3) Resource governance: ResourceQuota + LimitRange

To prevent one namespace from eating the cluster:

**ResourceQuota**

- caps total CPU/memory requests/limits
- caps object counts (pods, services, load balancers)
- can cap storage consumption

**LimitRange**

- sets defaults and min/max per pod/container
- ensures requests/limits exist (a big reliability win)

This prevents accidental “1000 pods” and improves scheduling fairness.

#### 4) NetworkPolicy: you don’t have isolation without it

Without NetworkPolicy enforcement, pods can often talk to each other freely across namespaces (depends on CNI defaults).

A common multi-tenant baseline:

- default deny ingress and egress per namespace
- allow egress to DNS
- allow ingress only via ingress controller namespace or specific allowed sources
- allow necessary cross-namespace traffic explicitly

This turns networking into an explicit contract instead of an accident.

#### 5) Pod Security Admission (PSA): keep tenants from escaping the sandbox

Use PSA profiles per namespace:

- `restricted` for tenant workloads
- `baseline` where needed
- keep `privileged` only for system namespaces

This blocks:

- privileged containers
- hostPath mounts
- hostNetwork
- dangerous capabilities
- running as root (in restricted)

It reduces “tenant can become node admin” risks.

#### 6) “Soft walls vs hard walls”

**Soft multi-tenancy (most common)**

- teams are trusted-ish
- isolation is to prevent accidents
- namespaces + RBAC + quotas + network policy is usually enough

**Hard multi-tenancy (untrusted tenants)**

- assume malicious workloads
- you need stronger isolation:
  - separate clusters, or
  - virtualization layers (KubeVirt/Kata), or
  - dedicated node pools per tenant + strict policies, or
  - separate control planes (rare/complex)  
     Kubernetes alone is not a perfect hostile-tenant isolation system because the kernel is shared and the attack surface is large.

#### 7) Practical multi-tenant baseline checklist

- per-team namespace(s)
- per-team ServiceAccounts, no shared admin tokens
- RBAC: namespace-scoped roles, no cluster-admin
- ResourceQuota + LimitRange everywhere
- NetworkPolicy default deny + explicit allows
- PSA restricted for tenant namespaces
- isolate “system” components in separate namespaces/node pools
- audit logs enabled; monitor RBAC changes

---
