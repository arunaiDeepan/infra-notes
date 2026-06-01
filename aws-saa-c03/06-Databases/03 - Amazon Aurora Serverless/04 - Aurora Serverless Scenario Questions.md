# Aurora Serverless Scenario Questions - SAA-C03 Deep Dive

> Exam-style scenarios for Aurora Serverless. Each gives a realistic prompt, the **correct answer**, **why it wins**, and **why the distractors lose**. Master the trigger phrases: _unpredictable/spiky relational_ → **v2**; _dev/test idle to ~$0_ → **v1 auto-pause**; _Lambda HTTP SQL_ → **Data API**; _serverless + replicas/Global DB_ → **v2 only**.

See also: [01 - Aurora Serverless Intro & Core Concepts](01%20-%20Aurora%20Serverless%20Intro%20%26%20Core%20Concepts.md) · [02 - Aurora Serverless Architecture Deep Dive](02%20-%20Aurora%20Serverless%20Architecture%20Deep%20Dive.md) · [03 - Aurora Serverless Best Practices & Examples](03%20-%20Aurora%20Serverless%20Best%20Practices%20%26%20Examples.md) · [05 - Aurora Serverless Troubleshooting (SRE)](05%20-%20Aurora%20Serverless%20Troubleshooting%20%28SRE%29.md) · [06 - Aurora Serverless Important Facts & Cheat Sheet](06%20-%20Aurora%20Serverless%20Important%20Facts%20%26%20Cheat%20Sheet.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md) · [01 - Aurora Intro & Core Concepts](01%20-%20Aurora%20Intro%20%26%20Core%20Concepts.md)

---

## Table of Contents

- [Q1 - Unpredictable Spiky Relational Workload](#q1---unpredictable-spiky-relational-workload)
- [Q2 - Dev/Test DB That Costs ~0 When Idle](#q2---devtest-db-that-costs-0-when-idle)
- [Q3 - Serverless App Needs HTTP SQL Access](#q3---serverless-app-needs-http-sql-access)
- [Q4 - Need Read Replicas + Global Database](#q4---need-read-replicas--global-database)
- [Q5 - Migrating Provisioned Aurora to Serverless](#q5---migrating-provisioned-aurora-to-serverless)
- [Q6 - Max Capacity Cost Control](#q6---max-capacity-cost-control)
- [Q7 - Steady High Load 24/7](#q7---steady-high-load-247)
- [Q8 - Multi-Tenant SaaS Bursty Tenants](#q8---multi-tenant-saas-bursty-tenants)
- [Q9 - Mixed Steady Writes Bursty Reads](#q9---mixed-steady-writes-bursty-reads)
- [Q10 - Lambda Connection Storm](#q10---lambda-connection-storm)
- [Exam Tips & Traps](#exam-tips--traps)
- [Summary](#summary)

---

## Q1 - Unpredictable Spiky Relational Workload

**Scenario:** A new web app uses a PostgreSQL-compatible database. Traffic is highly **variable and unpredictable** - quiet for hours, then sudden spikes. The team wants to avoid over-provisioning for peak yet handle bursts, with high availability.

**Answer:** **Aurora Serverless v2** (PostgreSQL-compatible).

**Why:** v2 scales compute **in fine-grained 0.5-ACU steps within seconds** to track spikes, and supports **Multi-AZ** for HA - you pay for capacity used, not peak.

**Distractors:** _Provisioned Aurora sized for peak_ - wasteful and slow to react. _Serverless v1_ - coarse scaling, no Multi-AZ, can stall at scaling points. _DynamoDB_ - it's a relational/PostgreSQL workload.

[⬆ Back to top](#table-of-contents)

---

## Q2 - Dev/Test DB That Costs ~0 When Idle

**Scenario:** A QA team needs a MySQL-compatible database for testing. It is **only used during business hours** and sits idle nights and weekends. They want **near-zero cost when idle** and can tolerate a brief delay on first use.

**Answer:** **Aurora Serverless v1 with auto-pause** enabled.

**Why:** v1 **auto-pauses to 0 ACU** after the inactivity timeout, so you pay **storage only** when idle; it resumes (with a cold start) on the next connection - acceptable for dev/test.

**Distractors:** _Serverless v2_ - does not have v1's auto-pause-to-zero model. _Provisioned Aurora stopped manually_ - max 7-day stop then auto-starts; not automatic on idle. _RDS Single-AZ_ - still billed while idle.

[⬆ Back to top](#table-of-contents)

---

## Q3 - Serverless App Needs HTTP SQL Access

**Scenario:** A fleet of **Lambda functions** must run SQL against an Aurora database. The team wants to **avoid managing database connections, drivers, and VPC networking** in the functions.

**Answer:** Use the **RDS Data API** against Aurora Serverless.

**Why:** The Data API exposes SQL over **HTTPS**, authenticated with **IAM** and credentials in **Secrets Manager** - no persistent connections, no connection pool, no VPC plumbing in Lambda.

**Distractors:** _Embed a connection pool in each Lambda_ - causes connection storms. _Run a bastion/proxy EC2_ - operational overhead. _Switch to DynamoDB_ - changes the data model unnecessarily.

[⬆ Back to top](#table-of-contents)

---

## Q4 - Need Read Replicas + Global Database

**Scenario:** A serverless Aurora cluster must add **read replicas** for read scaling and a **cross-Region Aurora Global Database** for DR. The current cluster runs **Aurora Serverless v1**.

**Answer:** Migrate to **Aurora Serverless v2** (which supports replicas, Multi-AZ, and Global Database).

**Why:** **v1 cannot have read replicas, Multi-AZ, or Global Database.** Only **v2** supports these features.

**Distractors:** _Add replicas to the v1 cluster_ - not supported. _Use DynamoDB Global Tables_ - wrong data model. _Cross-Region snapshot copy_ - DR via snapshots is not continuous like Global DB.

[⬆ Back to top](#table-of-contents)

---

## Q5 - Migrating Provisioned Aurora to Serverless

**Scenario:** A company runs a **provisioned Aurora PostgreSQL** cluster with steady writes but **highly bursty reads**. They want serverless elasticity for reads with **minimal downtime**.

**Answer:** Create a **mixed-configuration cluster** - keep the provisioned writer and add **Serverless v2 reader** instances; route reads to the reader endpoint.

**Why:** v2 supports **mixing provisioned and serverless instances** in one cluster, enabling gradual, low-downtime adoption with serverless readers that scale to read bursts.

**Distractors:** _Recreate everything as Serverless v1_ - no replicas, requires migration/downtime. _Snapshot and restore to a new cluster_ - more downtime than adding readers in place.

[⬆ Back to top](#table-of-contents)

---

## Q6 - Max Capacity Cost Control

**Scenario:** Finance is worried that an Aurora Serverless v2 database could scale up indefinitely during a traffic surge and **blow the budget**. They want a **hard cost ceiling** while still allowing normal scaling.

**Answer:** Set an appropriate **maximum ACU** in the `serverlessv2_scaling_configuration`.

**Why:** Max ACU caps how high compute (and therefore cost) can scale. Set it above normal peak but at a level finance accepts.

**Distractors:** _Lower the min ACU_ - controls idle floor, not the ceiling. _Disable auto-scaling_ - not how serverless works; you'd lose elasticity. _Use Reserved Instances_ - applies to provisioned, not serverless ACUs.

[⬆ Back to top](#table-of-contents)

---

## Q7 - Steady High Load 24/7

**Scenario:** An application has a **constant, predictable, high** transaction rate around the clock. The team wants the **most cost-effective** Aurora option.

**Answer:** **Provisioned Aurora** with **Reserved Instances** (not serverless).

**Why:** For flat, always-on load, a right-sized provisioned instance (with RIs) is cheaper than paying per-ACU at a continuously high level. Serverless shines on **variable** load, not steady peaks.

**Distractors:** _Serverless v2 at high min ACU_ - effectively always-on but at on-demand pricing. _Serverless v1_ - also not cost-optimal for steady high load.

[⬆ Back to top](#table-of-contents)

---

## Q8 - Multi-Tenant SaaS Bursty Tenants

**Scenario:** A SaaS platform provisions a database per tenant. Tenants have **wildly uneven, bursty** usage; many are idle most of the time. The provider wants to **minimise cost** without manual capacity management.

**Answer:** **Aurora Serverless v2** per tenant (or shared clusters with serverless), letting each scale to its own demand.

**Why:** v2 auto-scales each database to its actual load, so idle tenants cost little and busy tenants get capacity - no manual right-sizing across hundreds of DBs.

**Distractors:** _Fixed provisioned instances per tenant_ - massive waste for idle tenants. _Serverless v1_ - coarser scaling, no replicas/HA for active tenants.

[⬆ Back to top](#table-of-contents)

---

## Q9 - Mixed Steady Writes Bursty Reads

**Scenario:** Write volume is **steady and predictable**; read volume **spikes** during reporting windows. The team wants cost efficiency and read elasticity in one cluster.

**Answer:** **Provisioned writer + Serverless v2 readers** (mixed cluster).

**Why:** A provisioned writer (cheap with RIs for steady writes) plus serverless v2 readers that scale up only during read spikes is the cost-optimal pattern.

**Distractors:** _All-serverless v2_ - readers fine, but writer pays on-demand for steady load. _All-provisioned with many readers_ - readers idle outside reporting windows waste money.

[⬆ Back to top](#table-of-contents)

---

## Q10 - Lambda Connection Storm

**Scenario:** During spikes, thousands of concurrent **Lambda** invocations open connections to Aurora and **exhaust the connection limit**, causing errors. The team wants a managed fix.

**Answer:** Put **RDS Proxy** in front of Aurora Serverless v2 (or use the **Data API** for HTTP/SQL access).

**Why:** RDS Proxy pools and multiplexes connections, absorbing Lambda concurrency. The Data API avoids persistent connections entirely. Both eliminate connection exhaustion.

**Distractors:** _Raise max_connections manually_ - brittle, doesn't scale with Lambda concurrency. _Move to v1_ - doesn't solve connection storms and loses features.

[⬆ Back to top](#table-of-contents)

---

## Exam Tips & Traps

- **"Variable / unpredictable / spiky" relational → Serverless v2.** Reflex answer.
- **"Idle dev/test, ~$0 when not used" → Serverless v1 auto-pause.**
- **"Lambda + SQL without connections" → Data API.** "Connection storm" → **RDS Proxy** (v2) or Data API.
- **"Serverless needs replicas / Multi-AZ / Global DB" → v2 only.** v1 can't.
- **"Steady high 24/7" → provisioned + Reserved Instances**, NOT serverless.
- **Cost ceiling → set max ACU.** Idle cost → set min ACU.
- **"Migrate provisioned with minimal downtime" → mixed cluster (add serverless v2 readers).**

[⬆ Back to top](#table-of-contents)

---

## Summary

| Scenario Trigger                  | Answer                           |
| :-------------------------------- | :------------------------------- |
| Unpredictable/spiky relational    | Serverless v2                    |
| Idle dev/test, near-zero cost     | Serverless v1 auto-pause         |
| Lambda HTTP/SQL, no connections   | Data API                         |
| Serverless + replicas/Global DB   | v2 only                          |
| Migrate provisioned, low downtime | Mixed cluster (v2 readers)       |
| Hard cost ceiling                 | Set max ACU                      |
| Steady high 24/7                  | Provisioned + Reserved Instances |
| Connection storm from Lambda      | RDS Proxy (v2) / Data API        |

[⬆ Back to top](#table-of-contents)
