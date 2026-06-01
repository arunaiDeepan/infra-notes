# Security & RBAC - Scenarios & SRE Ops

> Auditing "who can do what," finding escalation paths, and securing secrets. Frequently tested concepts, CKA/CKAD tasks, interview questions, EKS production scenarios, the `can-i` truth serum, and runbooks. Pair with [01 - Security & RBAC Guide](01%20-%20Security%20%26%20RBAC%20Guide.md).

See also: [01 - Security & RBAC Guide](01%20-%20Security%20%26%20RBAC%20Guide.md) · [02 - Multi-Tenancy Scenarios & SRE Ops](02%20-%20Multi-Tenancy%20Scenarios%20%26%20SRE%20Ops.md) · [02 - Incident Response Scenarios & SRE Ops](02%20-%20Incident%20Response%20Scenarios%20%26%20SRE%20Ops.md)

---

## Table of Contents

- [1. Frequently Tested Concepts](#1-frequently-tested-concepts)
- [2. Keywords → Cause](#2-keywords--cause)
- [3. CKA/CKAD Practical Tasks](#3-ckackad-practical-tasks)
- [4. Interview Questions](#4-interview-questions)
- [5. EKS Production Scenarios](#5-eks-production-scenarios)
- [6. The `can-i` Truth Serum & Audit Commands](#6-the-can-i-truth-serum--audit-commands)
- [7. Runbooks](#7-runbooks)
- [8. One-Line Recap](#8-one-line-recap)

---

## 1. Frequently Tested Concepts

- **AuthN → AuthZ (RBAC) → Admission** pipeline.
- **Secrets are base64, not encrypted** by default.
- **`list secrets` = read secret values** = near god mode.
- **Role/RoleBinding (ns) vs ClusterRole/ClusterRoleBinding (cluster).**
- **`automountServiceAccountToken: false`** when no API access needed.
- **PSA restricted** blocks privileged/hostPath/root.
- EKS: **IRSA/Pod Identity** > static keys; **KMS** encrypts secrets at rest; **IAM↔RBAC** via access entries.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords → Cause

| Phrase                                      | Points to                               |
| :------------------------------------------ | :-------------------------------------- |
| "Unauthorized / cannot list resource"       | RBAC missing (or IAM not mapped on EKS) |
| "pod can read all secrets"                  | Over-broad Role on secrets              |
| "compromised pod stole node role"           | Pod reached IMDS → block it / use IRSA  |
| "secret visible in `kubectl describe`/logs" | Secret as env var                       |
| "privileged container ran in prod"          | No PSA `restricted` / admission policy  |
| "static AWS keys in a Secret"               | Use IRSA/Pod Identity instead           |
| "etcd backup leaked secrets"                | No KMS encryption at rest               |
| "team gave themselves more access"          | `bind`/`escalate` verbs not locked      |

[⬆ Back to top](#table-of-contents)

---

## 3. CKA/CKAD Practical Tasks

**T1 - Create a least-privilege Role + binding for an SA (CKA staple):**

```bash
kubectl create sa api-sa
kubectl create role pod-reader --verb=get,list,watch --resource=pods
kubectl create rolebinding api-sa-reader --role=pod-reader --serviceaccount=default:api-sa
```

**T2 - What SA does a Pod use, and what can it do?**

```bash
kubectl get pod <pod> -o jsonpath='{.spec.serviceAccountName}{"\n"}'
kubectl auth can-i --as=system:serviceaccount:<ns>:api-sa list secrets -n <ns>
```

**T3 - Disable token automount:**

```yaml
spec:
  automountServiceAccountToken: false
```

**T4 - Enforce restricted Pod Security on a namespace:**

```bash
kubectl label ns app pod-security.kubernetes.io/enforce=restricted
```

**T5 - Harden a container securityContext:**

```yaml
securityContext:
  runAsNonRoot: true
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities: { drop: ["ALL"] }
  seccompProfile: { type: RuntimeDefault }
```

[⬆ Back to top](#table-of-contents)

---

## 4. Interview Questions

**Q1: Walk through RBAC vs admission.**

> RBAC = "is this identity allowed to perform this verb on this resource?" Admission = "given it's allowed, is _this specific object_ acceptable?" (e.g., RBAC permits creating a Pod; admission rejects it for being privileged).

**Q2: Why is `list secrets` dangerous?**

> `list`/`get` returns secret _contents_ (base64). A SA with it can read every credential in scope - and with `create pods` can mount+exfiltrate. It's effective god mode.

**Q3: How do Pods authenticate to the API, and how to reduce risk?**

> Via a bound (short-lived, projected) ServiceAccount token. Reduce risk: one SA per workload, least-privilege Roles, and `automountServiceAccountToken: false` when no API access is needed.

**Q4: How do Pods get AWS permissions on EKS without static keys?**

> IRSA (OIDC-federated role per SA) or EKS Pod Identity - short-lived, auto-rotated, least-privilege per workload. Block IMDS so Pods can't grab the node role.

**Q5: Are Kubernetes Secrets encrypted?**

> Only base64-encoded by default. Enable **KMS encryption at rest** (etcd), restrict RBAC reads, prefer external stores via CSI, and avoid env-var injection.

**Q6: How do you stop privileged containers cluster-wide?**

> PSA `restricted` per namespace + a validating policy (Kyverno/Gatekeeper) denying `privileged`, hostPath, hostNetwork, and root.

[⬆ Back to top](#table-of-contents)

---

## 5. EKS Production Scenarios

### Medium

**M1 - New IAM role gets `Unauthorized` from the cluster.**

> Not mapped. Add an EKS **access entry** (or `aws-auth` entry) binding it to a group/Role. Verify `aws sts get-caller-identity`.

**M2 - App needs S3 access; someone wants to put keys in a Secret.**

> Use **IRSA/Pod Identity**: create an IAM role scoped to the bucket, associate it with the app's SA. No static keys.

**M3 - Security review flags secrets readable in `kubectl describe pod`.**

> Secrets injected as env vars. Switch to file mounts or Secrets Store CSI; restrict who can `describe`/`exec`.

**M4 - etcd snapshot in a backup bucket contains plaintext secrets.**

> KMS encryption at rest not enabled. Enable secrets encryption with a CMK; rotate the key; tighten backup-bucket access.

### Hard

**H1 - Post-incident: a compromised app Pod made AWS API calls as the node role.**

> Pod reached **IMDS** and used the node instance profile. Fix: enforce IMDSv2 + hop limit 1 (or block IMDS CIDR via NetworkPolicy), move app perms to **IRSA**, scope the node role to the minimum, and alert on unexpected role usage (CloudTrail/GuardDuty).

**H2 - A namespaced team escalated to cluster-admin.**

> They had `bind`/`escalate` or could create ClusterRoleBindings. Remove those verbs, audit all ClusterRoleBindings, enforce that teams can't create cluster-scoped objects, and alert on RBAC changes via audit logs.

**H3 - A poisoned image with a crypto-miner ran in prod.**

> No image provenance controls. Restrict to ECR + approved registries via admission, enable ECR scanning + Inspector, require signature verification (cosign/Kyverno), and PSA `restricted` to limit blast radius.

**H4 - Secret rotation requires app restarts but the team fears downtime.**

> Most apps can't hot-reload env secrets. Rotate in the external store → ESO/CSI updates → trigger a **rolling restart** guarded by **PDB + readiness** so rotation is zero-downtime. See [01 - Workload Resilience Guide](01%20-%20Workload%20Resilience%20Guide.md).

**H5 - Audit shows a wildcard ClusterRole (`resources: *`, `verbs: *`) bound to a controller SA.**

> Future-proof footgun granting power over new CRDs automatically. Replace with explicit resource/verb lists; re-audit after every CRD install.

[⬆ Back to top](#table-of-contents)

---

## 6. The `can-i` Truth Serum & Audit Commands

```bash
# Can I / can this SA do X?
kubectl auth can-i get pods
kubectl auth can-i list secrets -n default
kubectl auth can-i --as=system:serviceaccount:ns:my-sa create pods -n ns
kubectl auth can-i --list --as=system:serviceaccount:ns:my-sa -n ns   # full matrix

# What binds to an SA / who has cluster-admin?
kubectl get rolebinding,clusterrolebinding -A -o wide | grep my-sa
kubectl get clusterrolebinding -o json | jq '.items[]|select(.roleRef.name=="cluster-admin")|.subjects'

# What SA does a Pod use, and is a token mounted?
kubectl get pod <pod> -o jsonpath='{.spec.serviceAccountName} {.spec.automountServiceAccountToken}{"\n"}'

# EKS IAM mapping
kubectl -n kube-system get configmap aws-auth -o yaml   # legacy
aws eks list-access-entries --cluster-name <cluster>     # modern
```

[⬆ Back to top](#table-of-contents)

---

## 7. Runbooks

### Runbook: RBAC access review

1. Enumerate ClusterRoleBindings; flag any binding to `cluster-admin` or wildcard roles.
2. For each tenant SA: `kubectl auth can-i --list` to see effective permissions.
3. Confirm no team can read cross-namespace secrets or create cluster-scoped objects.
4. Verify `bind`/`escalate`/`pods/exec`/secret-read are restricted in prod.
5. Alert on future RBAC changes via audit logs.

### Runbook: suspected Pod compromise

1. Cordon the node; capture the Pod (logs, `kubectl describe`, process list) before deleting.
2. Determine the SA + its permissions (`auth can-i --list`); check if IMDS was reachable.
3. Rotate any credentials the Pod could access (secrets, IRSA role trust if needed).
4. Check CloudTrail/GuardDuty for AWS API calls from the node/role.
5. Patch the image, tighten RBAC/IMDS/PSA, redeploy; post-mortem.

[⬆ Back to top](#table-of-contents)

---

## 8. One-Line Recap

> **AuthN → RBAC → Admission. Secrets are base64, not encrypted - enable KMS, restrict reads, avoid env vars. `list secrets` + `create pods` + `exec` are the escalation paths. One least-privilege SA per workload, no wildcards, no `cluster-admin`. On EKS use IRSA/Pod Identity (not static keys), block IMDS, enforce PSA restricted.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [01 - Multi-Tenancy Guide](01%20-%20Multi-Tenancy%20Guide.md).
