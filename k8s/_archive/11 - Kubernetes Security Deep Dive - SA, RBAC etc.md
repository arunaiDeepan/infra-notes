### Kubernetes Security Deep Dive: ServiceAccounts, RBAC, Admission Control, and Least Privilege

Kubernetes security is mostly about one question: “Who is allowed to ask the API server to do what?” Because in k8s, _the API is the control plane_. If something can talk to the API with powerful credentials, it can rewrite reality.

So we’ll build the full mental model: identities (ServiceAccounts), permissions (RBAC), how pods get credentials, and the policy layer (admission). Then we’ll land on practical least-privilege patterns and the common footguns.

#### 1) The security center of gravity: kube-apiserver

Everything runs through the API server:

- creating pods
- listing secrets
- attaching to nodes
- exec into containers
- changing RBAC
- deploying workloads

So “k8s security” is basically:

- authenticate who you are
- authorize what you can do
- enforce policies on objects being created/updated

---

## Identity: Authentication and ServiceAccounts

#### 2) Authentication: how the API server knows “who you are”

Common auth methods:

- Client certificates (common for admins)
- Bearer tokens (ServiceAccount tokens)
- OIDC (SSO integration)
- Webhook auth (external auth systems)

For workloads running inside the cluster, the identity is usually a **ServiceAccount**.

#### 3) ServiceAccount: the in-cluster identity for pods

A ServiceAccount (SA) is:

- a namespaced identity object
- used by pods to authenticate to the API server

When a pod runs with a ServiceAccount, Kubernetes can mount a token into the pod that the pod can use to call the API.

Important reality check:

- If a pod never needs to call the Kubernetes API, it should not have powerful API permissions-and ideally shouldn’t even have a token mounted.

#### 4) How pods get ServiceAccount credentials

By default:

- each namespace has a `default` ServiceAccount
- pods that don’t specify one use it

Historically, Kubernetes auto-created a long-lived secret token for SAs. Modern clusters typically use **Bound ServiceAccount Tokens**:

- tokens are short-lived
- audience-bound
- rotated automatically
- mounted into pods via a projected volume

This is much safer, but it’s still a credential in the pod.

Control knobs:

- `spec.serviceAccountName` in Pod/Deployment
- `automountServiceAccountToken: false` to prevent token mounting when not needed

---

## Permissions: Authorization and RBAC

#### 5) Authorization: RBAC decides what you can do

After authentication, the API server asks: “Are you allowed?”

RBAC objects:

- **Role**: permissions within a namespace
- **ClusterRole**: permissions cluster-wide (or reusable)
- **RoleBinding**: binds a Role/ClusterRole to a subject in a namespace
- **ClusterRoleBinding**: binds a ClusterRole cluster-wide

Subjects:

- Users
- Groups
- ServiceAccounts

RBAC rules are expressed as:

- API groups (e.g., `""` for core, `apps`, `batch`)
- resources (pods, secrets, deployments)
- verbs (get, list, watch, create, update, patch, delete)

Key verbs:

- `get` = read one object
- `list` = list many
- `watch` = stream changes (often needed by controllers)
- `patch` = small updates (common in automation)

#### 6) The #1 RBAC footgun: “list secrets” is basically god mode

Secrets often contain:

- DB passwords
- cloud creds
- tokens  
   If a ServiceAccount can `list`/`get` secrets in a namespace, it can often escalate.

Even worse:

- if it can create pods, it can mount secrets and exfiltrate them
- if it can bind roles, it can grant itself more permissions

So least privilege matters.

#### 7) “kubectl auth can-i”: the truth serum

This command answers: “Can this identity do X?”

```bash
kubectl auth can-i get pods
kubectl auth can-i list secrets -n default
kubectl auth can-i create clusterrolebinding
```

To test a ServiceAccount:

```bash
kubectl auth can-i --as=system:serviceaccount:default:my-sa list pods -n default
```

---

## Policy: Admission Control (and why it’s different from RBAC)

#### 8) Admission controllers: the bouncer after RBAC

Even if RBAC says “yes,” admission can still say “no” (or “yes, but I’ll modify it first”).

Two types:

- **Mutating admission**: can change the object (inject sidecars, default labels, add tolerations)
- **Validating admission**: can accept or reject (deny privileged pods, require labels, enforce image registry rules)

Built-in examples:

- NamespaceLifecycle, NodeRestriction, LimitRanger, ResourceQuota, etc.

External policy engines:

- OPA Gatekeeper (ConstraintTemplates/Constraints)
- Kyverno (policy-as-YAML with mutation/validation)
- Custom validating webhook

Admission is where org-wide rules live:

- “No privileged containers”
- “Must set resource requests”
- “Images must come from approved registry”
- “No hostPath mounts”
- “Require non-root user”
- “Require readOnlyRootFilesystem”

RBAC answers: “Are you allowed to ask?”  
Admission answers: “Even if you’re allowed, do we permit _this kind_ of request?”

---

## Pod Security: controlling what pods are allowed to do

#### 9) Pod Security Standards (PSS): baseline/restricted/etc

Modern clusters often use Pod Security Admission (PSA) to enforce Pod Security Standards:

- **privileged** (anything goes)
- **baseline** (blocks the worst stuff)
- **restricted** (strict: non-root, no privilege escalation, etc.)

Enforcement is usually per-namespace via labels.

This reduces “oops I ran privileged and mounted the host” accidents.

---

## Least privilege patterns that actually work

#### 10) Give each workload its own ServiceAccount

Don’t reuse `default` for everything.

- `api-sa`, `worker-sa`, `cron-sa` etc.

Then:

- bind only the exact permissions needed
- ideally namespace-scoped Roles

#### 11) Prefer Roles over ClusterRoles

If your app only needs to read ConfigMaps in its namespace, don’t grant cluster-wide anything.

A safe-ish pattern:

- Role: read configmaps, maybe endpoints
- RoleBinding: binds to the app’s SA

#### 12) Don’t mount SA tokens unless needed

If the app doesn’t call the API:

- set `automountServiceAccountToken: false`  
   That removes a whole class of “pod got compromised → token stolen → API abused.”

#### 13) Avoid wildcard verbs/resources

Avoid rules like:

- resources: `*`
- verbs: `*`  
   Those are “future permission bugs”: they grant power over new resources added later.

---

## Classic escalation paths to watch for

#### 14) Pods + secrets + exec = easy data theft

If an attacker can:

- exec into a pod OR create a pod in a namespace  
   and that pod can access secrets,  
   they can exfiltrate secrets.

So protect:

- who can `create pods`
- who can `exec` into pods (`pods/exec`)
- who can read secrets

#### 15) Node-level permissions are nuclear

Permissions like:

- `nodes/proxy`
- `nodes`
- `pods` with hostPath + privileged  
   can become host compromise paths.

Lock down:

- privileged mode
- hostPath
- hostNetwork
- CAP_SYS_ADMIN and similar Linux capabilities

---

## Practical debugging / auditing commands

What ServiceAccount does a pod use?

```bash
kubectl get pod <pod> -o jsonpath='{.spec.serviceAccountName}{"\n"}'
```

What roles are bound to a ServiceAccount?

```bash
kubectl get rolebinding,clusterrolebinding -A | grep my-sa
```

What can it do?

```bash
kubectl auth can-i --as=system:serviceaccount:<ns>:my-sa list pods -n <ns>
```

---

## The clean mental model

- Identity (authn): ServiceAccount token says “I am X”
- Permission (authz): RBAC says “X can do Y”
- Policy (admission): “Even if X can do Y, do we allow this specific object?”

If you internalize that triangle, Kubernetes security stops being mystical.

---
