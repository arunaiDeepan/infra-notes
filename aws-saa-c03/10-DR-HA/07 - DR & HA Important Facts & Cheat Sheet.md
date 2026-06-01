# DR & HA Important Facts & Cheat Sheet - SAA-C03 Deep Dive

> Rapid-revision sheet for the day before the exam: the must-know facts, the strategy comparison, per-service HA/DR mechanisms, and the keyword→answer map. If you only reread one DR/HA note, make it this one.

See also: [00 - DR & HA Overview & Exam Guide](00%20-%20DR%20%26%20HA%20Overview%20%26%20Exam%20Guide.md) · [01 - HA, Fault Tolerance & Core Concepts](01%20-%20HA%2C%20Fault%20Tolerance%20%26%20Core%20Concepts.md) · [02 - High Availability Building Blocks](02%20-%20High%20Availability%20Building%20Blocks.md) · [03 - The Four DR Strategies](03%20-%20The%20Four%20DR%20Strategies.md) · [04 - Cross-Region, Backup & Data Replication](04%20-%20Cross-Region%2C%20Backup%20%26%20Data%20Replication.md) · [05 - DR & HA Scenario Questions](05%20-%20DR%20%26%20HA%20Scenario%20Questions.md) · [06 - DR & HA Troubleshooting (SRE)](06%20-%20DR%20%26%20HA%20Troubleshooting%20%28SRE%29.md)

---

## Table of Contents

- [Core Definitions](#core-definitions)
- [The Four DR Strategies One-Liner](#the-four-dr-strategies-one-liner)
- [HA Building Blocks One-Liner](#ha-building-blocks-one-liner)
- [Per-Service HA and DR Mechanisms](#per-service-ha-and-dr-mechanisms)
- [Replication Facts](#replication-facts)
- [AWS Backup Facts](#aws-backup-facts)
- [Route 53 Routing for HA-DR](#route-53-routing-for-ha-dr)
- [Must-Know Numbers](#must-know-numbers)
- [Keyword to Answer Map](#keyword-to-answer-map)
- [Top 15 Gotchas](#top-15-gotchas)

---

## Core Definitions

| Term                | One-liner                                     |
| :------------------ | :-------------------------------------------- |
| **RTO**             | Max downtime tolerated (recovery **time**).   |
| **RPO**             | Max data loss tolerated (recovery **point**). |
| **Availability**    | Can I reach it now? (redundancy)              |
| **Durability**      | Is the data safe? (copies)                    |
| **HA**              | Minimise downtime, brief blip OK (Multi-AZ).  |
| **Fault Tolerance** | Zero interruption (S3, DynamoDB, Aurora).     |
| **DR**              | Recover from Region/site disaster.            |

[⬆ Back to top](#table-of-contents)

---

## The Four DR Strategies One-Liner

| Strategy             | DR Region runs              | RTO        | RPO     | Cost | Trigger phrase                     |
| :------------------- | :-------------------------- | :--------- | :------ | :--- | :--------------------------------- |
| **Backup & Restore** | Backups only                | Hours      | Hours   | $    | "cheapest", "tolerate hours"       |
| **Pilot Light**      | Data layer only             | 10s of min | Minutes | $$   | "core/DB always on, start compute" |
| **Warm Standby**     | Full stack, scaled **down** | Minutes    | Sec–min | $$$  | "scaled-down full copy running"    |
| **Active/Active**    | Full stack, **full** scale  | ~0         | ~0      | $$$$ | "zero downtime", "active-active"   |

> [!tip] Exam Tip
> Pick the **cheapest** strategy that still meets the **stated RTO/RPO**. Pilot Light vs Warm Standby = **data-only** vs **whole-stack-but-small**.

[⬆ Back to top](#table-of-contents)

---

## HA Building Blocks One-Liner

| Block                  | HA role                                                  |
| :--------------------- | :------------------------------------------------------- |
| **Multiple AZs**       | Default answer to "survive an AZ failure."               |
| **Auto Scaling Group** | Self-heal + scale; use **ELB health checks**; `min ≥ 2`. |
| **ELB (ALB/NLB)**      | Routes only to healthy targets across AZs.               |
| **Route 53**           | DNS-level failover/latency routing + health checks.      |
| **Per-AZ NAT GW**      | Avoids the single-NAT SPOF.                              |
| **Stateless tier**     | Session in ElastiCache/DynamoDB → ASG/ELB work cleanly.  |
| **SQS**                | Decouple tiers so downstream failure doesn't lose work.  |

[⬆ Back to top](#table-of-contents)

---

## Per-Service HA and DR Mechanisms

| Service            | In-Region HA                               | Cross-Region DR                                         |
| :----------------- | :----------------------------------------- | :------------------------------------------------------ |
| **EC2**            | ASG across AZs + ELB                       | AMI copy + relaunch (Backup/Pilot Light)                |
| **RDS**            | **Multi-AZ** (sync standby, auto failover) | Cross-Region **read replica** (promote) / snapshot copy |
| **Aurora**         | 6 copies / 3 AZs                           | **Global Database** (~1s, < 1 min RTO)                  |
| **DynamoDB**       | 3 AZs automatic                            | **Global Tables** (active-active)                       |
| **S3**             | ≥3 AZs (Standard)                          | **Cross-Region Replication**                            |
| **S3 One Zone-IA** | **Single AZ** (SPOF)                       | —                                                       |
| **EBS**            | Single AZ (snapshot→S3)                    | Snapshot **cross-Region copy**                          |
| **EFS**            | Multi-AZ (Standard)                        | **EFS Replication**                                     |
| **ElastiCache**    | Redis Multi-AZ failover                    | Redis **Global Datastore**                              |
| **Anything**       | —                                          | **AWS Backup** cross-Region/account copy                |

> [!tip] Exam Tip
> **Multi-AZ = HA (in-Region). Multi-Region = DR.** RDS **Multi-AZ standby is not readable** (read scaling = read replica). Aurora Global DB = **single-writer**; DynamoDB Global Tables = **multi-writer**.

[⬆ Back to top](#table-of-contents)

---

## Replication Facts

- **Synchronous** (RDS Multi-AZ standby) → RPO 0, in-Region only.
- **Asynchronous** (read replicas, Aurora Global DB, S3 CRR, DynamoDB Global Tables) → small lag, works cross-Region.
- **S3 replication requires versioning** on both buckets and only copies **new** objects (existing → **Batch Replication**).
- **Aurora Global DB:** up to **5 secondary Regions**, < 1s lag, sub-minute failover, minimal primary overhead.
- **DynamoDB Global Tables:** multi-active, needs **Streams**, last-writer-wins.
- Cross-Region restores often fail on **KMS key availability** in the DR Region.

[⬆ Back to top](#table-of-contents)

---

## AWS Backup Facts

- **Centralised, policy-driven** backups across EBS, EC2, RDS, Aurora, DynamoDB, EFS, FSx, Storage Gateway, S3, and more.
- **Backup plans** = frequency + retention/lifecycle + window.
- **Cross-Region and cross-account** copy for DR/isolation.
- **Backup Vault Lock = WORM/immutable** — even root can't delete during retention.
- Integrates with **Organizations** for org-wide policies; tag-based selection.

> [!tip] Exam Tip
> "Centralised, automated, compliant backups across services/accounts" → **AWS Backup**. "Immutable backups" → **Vault Lock**.

[⬆ Back to top](#table-of-contents)

---

## Route 53 Routing for HA-DR

| Policy            | Use                                                                |
| :---------------- | :----------------------------------------------------------------- |
| **Failover**      | Active-passive Region cutover (primary/secondary + health checks). |
| **Latency-based** | Send users to lowest-latency Region (active-active).               |
| **Weighted**      | Gradual/blue-green/percentage split.                               |
| **Geolocation**   | Route by user location (compliance/residency).                     |
| **Geoproximity**  | Distance-based with bias to shift load.                            |
| **Multi-value**   | Multiple healthy IPs (basic redundancy).                           |
| **Simple**        | Single record, **no health check**.                                |

> [!tip] Exam Tip
> Keep **TTL low (≈60s)** on failover records or clients keep resolving the dead endpoint. Prefer **Alias** records for AWS resources.

[⬆ Back to top](#table-of-contents)

---

## Must-Know Numbers

| Fact                               | Value                      |
| :--------------------------------- | :------------------------- |
| S3 Standard durability             | 11 nines (99.999999999%)   |
| S3 Standard availability           | 99.99%                     |
| S3 One Zone-IA                     | 11 nines durable, **1 AZ** |
| Aurora storage copies / AZs        | 6 copies across 3 AZs      |
| Aurora Global DB lag / RTO         | ~1s / < 1 min              |
| Aurora Global DB secondary Regions | up to 5                    |
| RDS cross-Region read replicas     | supported (promote for DR) |
| Four-nines downtime                | ~52 min/year               |
| Five-nines downtime                | ~5 min/year                |
| Recommended failover DNS TTL       | ~60s                       |

[⬆ Back to top](#table-of-contents)

---

## Keyword to Answer Map

| Phrase                                                 | Answer                                                  |
| :----------------------------------------------------- | :------------------------------------------------------ |
| "survive an AZ failure", "automatic failover"          | Multi-AZ (RDS Multi-AZ / ASG+ELB across AZs)            |
| "survive a Region failure"                             | Multi-Region (CRR, Aurora Global DB, Route 53 failover) |
| "most cost-effective DR", "tolerate hours"             | Backup & Restore                                        |
| "core/DB always replicated, start compute on failover" | Pilot Light                                             |
| "scaled-down full copy always running"                 | Warm Standby                                            |
| "zero downtime", "active-active", "lowest RTO/RPO"     | Multi-Site Active/Active                                |
| "relational, cross-Region, RPO ~1s, fast failover"     | Aurora Global Database                                  |
| "multi-Region active-active NoSQL"                     | DynamoDB Global Tables                                  |
| "automatically replace unhealthy instances"            | ASG + **ELB** health checks                             |
| "route users away from failed Region"                  | Route 53 Failover + health checks                       |
| "lowest-latency Region for global users"               | Route 53 Latency-based routing                          |
| "protect S3 objects from Region loss"                  | S3 CRR (+ versioning)                                   |
| "centralised/compliant backups across services"        | AWS Backup                                              |
| "immutable backups / WORM"                             | AWS Backup Vault Lock                                   |
| "private instances lost internet when AZ failed"       | Per-AZ NAT Gateway                                      |
| "users logged out on scale-in"                         | Externalise session state (ElastiCache/DynamoDB)        |
| "static IP load balancer / extreme throughput"         | NLB                                                     |
| "shared file system, cross-Region DR"                  | EFS Replication                                         |

[⬆ Back to top](#table-of-contents)

---

## Top 15 Gotchas

1. **RTO = downtime; RPO = data loss.** Don't swap them.
2. **Availability ≠ durability.** Reachable vs not-lost.
3. **Multi-AZ = HA; Multi-Region = DR.** Don't over-engineer to multi-Region.
4. **RDS Multi-AZ standby is NOT readable** — read scaling = read replica.
5. **RDS Multi-AZ is HA, not zero-downtime** — there's a brief failover blip.
6. **Pilot Light = data only on; Warm Standby = whole stack small.**
7. Pick the **cheapest strategy meeting the stated RTO/RPO**.
8. **Single NAT Gateway** is an AZ-bound SPOF → one per AZ.
9. **S3 One Zone-IA** lives in one AZ → only for reproducible data.
10. **S3 replication needs versioning** + copies only **new** objects (Batch Replication for old).
11. **Aurora Global DB = single-writer; DynamoDB Global Tables = multi-writer.**
12. **Cross-Region replication is async** → never a true 0 RPO.
13. **DNS failover speed is limited by TTL** → keep it ~60s.
14. **Use ELB health checks** on the ASG, not just EC2 status checks.
15. **An untested backup/DR plan is a risk** → run restores and game-days; watch **KMS** for cross-Region restores.

[⬆ Back to top](#table-of-contents)
