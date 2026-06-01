# Reliability Architectures - Scenarios & SRE Ops

> Turning the blueprint into design decisions and catching the interaction deadlocks. Frequently tested concepts, design tasks, interview/architecture questions, EKS production scenarios, and runbooks. Pair with [01 - Reliability Architectures Guide](01%20-%20Reliability%20Architectures%20Guide.md).

See also: [01 - Reliability Architectures Guide](01%20-%20Reliability%20Architectures%20Guide.md) · [02 - Workload Resilience Scenarios & SRE Ops](02%20-%20Workload%20Resilience%20Scenarios%20%26%20SRE%20Ops.md) · [02 - Incident Response Scenarios & SRE Ops](02%20-%20Incident%20Response%20Scenarios%20%26%20SRE%20Ops.md)

---

## Table of Contents

- [1. Frequently Tested Concepts](#1-frequently-tested-concepts)
- [2. Keywords → Decision](#2-keywords--decision)
- [3. Design Tasks](#3-design-tasks)
- [4. Interview / Architecture Questions](#4-interview--architecture-questions)
- [5. EKS Production Scenarios](#5-eks-production-scenarios)
- [6. Runbooks](#6-runbooks)
- [7. One-Line Recap](#7-one-line-recap)

---

## 1. Frequently Tested Concepts

- **Reliability = many boring decisions**, layered (foundations → ops).
- **Multi-AZ + node pools by purpose** (system/apps/batch/stateful).
- **Stateless: probes + graceful shutdown + HPA + PDB + spread.**
- **Workers scale on queue depth (KEDA), not CPU.**
- **Prefer managed data** (RDS/Aurora/ElastiCache/SQS).
- **The deadlock list**: `maxUnavailable:0` no surge, strict PDB, readiness coupled to DB, default-deny no DNS, tight CPU limits.
- **GitOps + SLO alerts + game days** = ops muscle.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords → Decision

| Phrase                          | Decision                                      |
| :------------------------------ | :-------------------------------------------- |
| "batch job melted DNS"          | Separate node pools (system vs batch)         |
| "survive an AZ failure"         | Multi-AZ nodes + topology spread + PDB        |
| "scale workers correctly"       | KEDA on queue depth                           |
| "don't drop capacity on deploy" | `maxUnavailable: 0` + surge + readiness gates |
| "DB hiccup caused total outage" | Decouple readiness from downstream            |
| "configs drift across clusters" | GitOps                                        |
| "no static cloud keys"          | IRSA/Pod Identity + external secrets          |
| "should I self-host the DB?"    | Prefer managed (RDS/Aurora)                   |

[⬆ Back to top](#table-of-contents)

---

## 3. Design Tasks

**T1 - Spread a Deployment across AZs:**

```yaml
topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: DoNotSchedule
    labelSelector: { matchLabels: { app: web-api } }
```

**T2 - Protect system add-ons from eviction:**

```yaml
# high PriorityClass + PDB on CoreDNS / ingress controller
priorityClassName: system-cluster-critical
```

**T3 - Isolate batch onto its own (spot) pool:**

```yaml
tolerations:
  [{ key: "workload", operator: "Equal", value: "batch", effect: "NoSchedule" }]
nodeSelector: { workload: batch }
```

**T4 - Zero-downtime rollout settings:** `maxUnavailable: 0`, `maxSurge: 1`, `minReadySeconds`, `preStop` sleep, ALB readiness gate + deregistration delay.

[⬆ Back to top](#table-of-contents)

---

## 4. Interview / Architecture Questions

**Q1: Design a reliable web + workers platform on EKS.**

> Multi-AZ cluster; node pools (system/apps/batch); ALB ingress; stateless web (probes, graceful shutdown, HPA on RPS, PDB, AZ spread); workers via KEDA on SQS depth; managed RDS/Aurora + ElastiCache; quotas/LimitRange/NetworkPolicy/PSA; IRSA secrets; observability + SLO alerts; GitOps. See [01 - Reliability Architectures Guide](01%20-%20Reliability%20Architectures%20Guide.md).

**Q2: Why separate node pools?**

> Blast-radius + resource isolation: a runaway batch job or noisy CI can't starve DNS/ingress/system components, and you can use spot for batch while keeping system on-demand.

**Q3: How do you make rollouts safe by design?**

> Accurate readiness, `maxUnavailable: 0` + surge, `minReadySeconds`, progress deadline + alerting, PDB, AZ spread, preStop + deregistration delay, and progressive delivery (canary) for risky changes.

**Q4: Self-host the database or use RDS/Aurora?**

> Prefer managed - it handles HA, backups, patching, multi-AZ failover. Self-hosting a DB on Kubernetes adds StatefulSet/storage/backup/leader-election burden for rarely-worth-it control.

**Q5: Name three "everything's configured but nothing moves" deadlocks.**

> `maxUnavailable:0` with no surge capacity; PDB too strict blocking drains; readiness coupled to a fragile DB emptying all endpoints. (Also default-deny without DNS allow, tight CPU limits cascading.)

[⬆ Back to top](#table-of-contents)

---

## 5. EKS Production Scenarios

### Medium

**M1 - A nightly CI job degrades production DNS/ingress.**

> Shared node pool. Move batch/CI to a tainted batch pool (spot ok); keep system components on dedicated nodes with high priority + PDBs.

**M2 - Rollout stuck Pending with `maxUnavailable: 0`.**

> No surge capacity. Ensure cluster headroom (Karpenter) or set `maxSurge` appropriately; the setting needs room to add new pods before removing old.

**M3 - A DB blip took the whole API down.**

> Readiness probe checks the DB. Decouple: readiness = "can serve," degrade gracefully; let the DB layer handle its own HA. See [01 - Services & Networking Guide](01%20-%20Services%20%26%20Networking%20Guide.md).

**M4 - Workers fall behind despite low CPU.**

> CPU HPA on an IO-bound worker. Switch to KEDA on queue depth; tune min replicas for cold-start.

### Hard

**H1 - Single-AZ node group + AZ outage = major incident.**

> Capacity was AZ-pinned. Move to multi-AZ node groups (or Karpenter across zones), enforce topology spread + PDBs, and keep stateful data multi-AZ (Aurora). One EKS cluster already spans AZs - use it.

**H2 - Cluster upgrade caused a multi-hour outage.**

> No safe choreography. Adopt: control plane → add-ons → node pools (one AZ at a time, PDBs honored), with verification gates; consider cluster-as-a-unit canary for big jumps. See [01 - Control Plane Reliability Guide](01%20-%20Control%20Plane%20Reliability%20Guide.md).

**H3 - Scaling looks "random" under load.**

> Broken autoscaling chain: wrong CPU requests (HPA math), Pods can't fit (node autoscaler), or PDBs block scale-down. Right-size requests, use Karpenter, loosen PDBs. See [01 - Autoscaling Guide](01%20-%20Autoscaling%20Guide.md).

**H4 - Drift: prod behaves differently from staging, nobody knows why.**

> No GitOps. Adopt Argo CD/Flux with platform+apps repos and per-cluster overlays; gate changes via PRs; diff to surface drift.

**H5 - A region outage is a real risk for a Tier-1 service.**

> Single-region. Add a second-region EKS (active/passive), Aurora Global / DynamoDB Global Tables, Route 53 / Global Accelerator failover, ECR replication, GitOps to both, and tested game-day failover. See [01 - Multi-Cluster Guide](01%20-%20Multi-Cluster%20Guide.md).

[⬆ Back to top](#table-of-contents)

---

## 6. Runbooks

### Runbook: production-ready namespace bundle

1. Namespace + labels (PSA `restricted`).
2. ResourceQuota + LimitRange.
3. Default-deny NetworkPolicy + allow-DNS + ingress allow + explicit app flows.
4. Per-workload SAs + IRSA roles; disable token automount where unused.
5. Deployments with probes + graceful shutdown + PDB + HPA/KEDA + topology spread.
6. Dashboards + SLO burn alerts; runbooks linked.

### Runbook: reliability review of an existing service

1. Replicas ≥ 2 across AZs? Topology spread + PDB present and sane?
2. Readiness reflects "can serve" and isn't coupled to fragile deps?
3. Requests/limits set; not BestEffort; CPU limits not throttling?
4. Rollout settings safe (surge/unavailable/minReadySeconds/preStop)?
5. Autoscaling chain intact (metrics + node capacity + drainable)?
6. Data managed/backed-up; secrets via IRSA; NetworkPolicy in place?

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Reliability = layered boring decisions: multi-AZ foundations, purpose node pools, HA platform services, well-behaved workloads (probes + graceful shutdown + HPA/KEDA + PDB + spread), guardrails (quota/PSA/NetworkPolicy/IRSA), and ops muscle (SLO alerts + GitOps + game days). Prefer managed data. Memorize the deadlock list. On EKS, one multi-AZ cluster + managed services gets you most of the way.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [01 - LLM Inference Guide](01%20-%20LLM%20Inference%20Guide.md).
