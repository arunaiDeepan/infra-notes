# Multi-Cluster - Scenarios & SRE Ops

> Designing failover that actually works and avoiding "multi-cluster theater." Frequently tested concepts, CKA/CKAD-adjacent tasks, interview questions, EKS production scenarios, and runbooks. Pair with [01 - Multi-Cluster Guide](01%20-%20Multi-Cluster%20Guide.md).

See also: [01 - Multi-Cluster Guide](01%20-%20Multi-Cluster%20Guide.md) · [02 - Control Plane Reliability Scenarios & SRE Ops](02%20-%20Control%20Plane%20Reliability%20Scenarios%20%26%20SRE%20Ops.md) · [02 - Reliability Architectures Scenarios & SRE Ops](02%20-%20Reliability%20Architectures%20Scenarios%20%26%20SRE%20Ops.md)

---

## Table of Contents

- [1. Frequently Tested Concepts](#1-frequently-tested-concepts)
- [2. Keywords → Pattern](#2-keywords--pattern)
- [3. Practical Tasks](#3-practical-tasks)
- [4. Interview Questions](#4-interview-questions)
- [5. EKS Production Scenarios](#5-eks-production-scenarios)
- [6. Runbooks](#6-runbooks)
- [7. One-Line Recap](#7-one-line-recap)

---

## 1. Frequently Tested Concepts

- **No native multi-cluster Service** - steer at DNS/LB/mesh.
- **Active/Passive simpler; Active/Active = data-consistency boss fight.**
- **GitOps (Argo/Flux)** prevents config drift across clusters.
- **The bottleneck is data**, not the app layer.
- **RTO/RPO** define the DR target; **test with game days**.
- EKS: single cluster already **multi-AZ**; multi-cluster is for **region**/isolation/canary.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords → Pattern

| Phrase                                   | Points to                                     |
| :--------------------------------------- | :-------------------------------------------- |
| "survive a region outage"                | Active/Passive or Active/Active + global data |
| "upgrade safely, whole-cluster rollback" | Cluster-as-a-unit canary                      |
| "keep dev/stage/prod consistent"         | GitOps + per-cluster overlays                 |
| "DB can't fail over"                     | Multi-cluster theater - fix data layer        |
| "failover takes too long (DNS TTL)"      | Use Global Accelerator                        |
| "configs drifted between clusters"       | Adopt GitOps                                  |
| "AZ failure" (not region)                | Single multi-AZ cluster suffices              |

[⬆ Back to top](#table-of-contents)

---

## 3. Practical Tasks

**T1 - Switch kube-contexts across clusters:**

```bash
kubectl config get-contexts
kubectl config use-context arn:aws:eks:us-west-2:...:cluster/prod-west
aws eks update-kubeconfig --name prod-west --region us-west-2
```

**T2 - Bootstrap GitOps (Argo CD) for multi-cluster:**

```bash
argocd cluster add arn:aws:eks:us-west-2:...:cluster/prod-west
argocd app create platform-west --repo <git> --path overlays/prod-west --dest-name prod-west
```

**T3 - Verify drift between clusters:**

```bash
argocd app diff platform-east
argocd app diff platform-west     # should both be in sync with Git
```

**T4 - Route 53 health-checked failover (concept):**

```text
Primary record  -> ALB(east)  [health check on /healthz]
Secondary record-> ALB(west)  [failover routing policy]
```

[⬆ Back to top](#table-of-contents)

---

## 4. Interview Questions

**Q1: Why is there no built-in multi-cluster Service?**

> Each cluster has its own API/etcd/network. Cross-cluster routing is done at the edge (DNS/global LB) or via a service mesh - Kubernetes deliberately keeps clusters independent.

**Q2: Active/Passive vs Active/Active - trade-offs?**

> Passive: simpler, one writer, slower failover, standby must stay synced. Active/Active: best availability/latency but data consistency + split-brain are hard; fits stateless/eventually-consistent workloads.

**Q3: What makes a multi-region DR plan "theater"?**

> App redundancy without a failable data layer. If the DB can't promote/replicate safely within RPO, the standby cluster can't actually serve correct data.

**Q4: How do you keep many clusters consistent?**

> GitOps: Git as source of truth, Argo CD/Flux reconciling each cluster, platform+apps repos with per-cluster overlays, secrets via external store references.

**Q5: On EKS, do I need multi-cluster for high availability?**

> Not for AZ failure - one EKS cluster spans 3 AZs. Multi-cluster is for region failure, hard isolation, or upgrade canaries. Don't pay multi-cluster cost to solve an AZ problem.

[⬆ Back to top](#table-of-contents)

---

## 5. EKS Production Scenarios

### Medium

**M1 - Configs drifted: staging works, prod doesn't, nobody knows why.**

> No GitOps. Adopt Argo CD/Flux; make Git the source of truth; diff to surface drift; gate changes via PRs.

**M2 - Failover tested and traffic took 5+ minutes to move.**

> DNS TTL/caching. Use **Global Accelerator** (anycast, fast health-based failover) or lower TTLs; pre-warm the standby.

**M3 - Standby region couldn't pull images during failover.**

> Images only in the primary region's ECR. Enable **ECR cross-region replication**; verify pull from the standby regularly.

**M4 - Secrets missing in the DR cluster.**

> Secrets weren't replicated. Use Secrets Manager multi-region + External Secrets Operator in both clusters.

### Hard

**H1 - Region outage: app failed over but data was 20 minutes stale (RPO breach).**

> Replication lag / async DB. Move to **Aurora Global** (low-lag) or DynamoDB Global Tables; define and monitor RPO; alert on replication lag; decide write-failover policy.

**H2 - Active/Active split-brain: both regions accepted conflicting writes.**

> Single-primary semantics violated. Use a globally consistent store or strict write-region routing (one writer), with the other region read-only; add conflict detection/fencing.

**H3 - A bad release hit all clusters at once via GitOps.**

> No progressive rollout across clusters. Stage GitOps sync: canary cluster first → soak → promote; use Argo CD sync waves / app-of-apps with manual promotion gates.

**H4 - DR plan never tested; real outage exposed broken runbooks.**

> Untested DR. Institute **game days**: simulate region/control-plane/dependency failures quarterly; measure RTO/RPO; fix runbooks; automate failover steps.

**H5 - Cost doubled after going multi-cluster with no clear benefit.**

> Multi-cluster without a goal. Re-evaluate: if the need was AZ resilience, collapse to one multi-AZ cluster; reserve multi-cluster for genuine region/isolation/canary needs.

[⬆ Back to top](#table-of-contents)

---

## 6. Runbooks

### Runbook: region failover (active/passive)

1. Confirm primary-region impact (SLO burn, AWS Health) - avoid false failover.
2. Promote the data layer (Aurora Global failover / verify replica lag within RPO).
3. Shift traffic (Route 53 failover / Global Accelerator endpoint weights).
4. Scale up standby capacity (it was warm, not full); verify health.
5. Confirm secrets/images/config present (GitOps already synced).
6. Validate end-to-end; communicate; later, plan controlled failback.

### Runbook: onboard a new cluster via GitOps

1. Stamp the cluster (Terraform/EKS Blueprints) identical to peers.
2. Register with Argo CD/Flux; apply platform overlay (CNI/DNS/ingress/policies).
3. Sync apps overlay; verify no drift (`argocd app diff`).
4. Replicate secrets (ESO) and images (ECR replication).
5. Add to traffic management only after health checks pass.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Multi-cluster is a menu (env-split / active-passive / active-active / cluster-canary) and the bottleneck is always data. No native multi-cluster Service - steer at Route 53 / Global Accelerator. GitOps prevents drift. On EKS one cluster is already multi-AZ; go multi-cluster for region/isolation/canary, let Aurora Global / DynamoDB Global own data, and test DR with game days.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [01 - Incident Response Guide](01%20-%20Incident%20Response%20Guide.md).
