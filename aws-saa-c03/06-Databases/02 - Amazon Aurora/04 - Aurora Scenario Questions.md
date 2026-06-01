# Aurora Scenario Questions - SAA-C03 Deep Dive

> Exam-style scenarios covering global reads, cross-Region DR, read scaling, Backtrack recovery, cloning, RDS-to-Aurora migration, Aurora vs RDS choice, and the I/O-Optimized cost decision.

See also: [01 - Aurora Intro & Core Concepts](01%20-%20Aurora%20Intro%20%26%20Core%20Concepts.md) · [02 - Aurora Architecture Deep Dive](02%20-%20Aurora%20Architecture%20Deep%20Dive.md) · [03 - Aurora Best Practices & Examples](03%20-%20Aurora%20Best%20Practices%20%26%20Examples.md) · [05 - Aurora Troubleshooting (SRE)](05%20-%20Aurora%20Troubleshooting%20%28SRE%29.md) · [06 - Aurora Important Facts & Cheat Sheet](06%20-%20Aurora%20Important%20Facts%20%26%20Cheat%20Sheet.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md) · [01 - RDS Intro & Core Concepts](01%20-%20RDS%20Intro%20%26%20Core%20Concepts.md)

---

## Table of Contents

- [Scenario 1 - Global Low-Latency Reads](#scenario-1---global-low-latency-reads)
- [Scenario 2 - Sub-Minute Cross-Region DR](#scenario-2---sub-minute-cross-region-dr)
- [Scenario 3 - Scale Reads Without App Changes](#scenario-3---scale-reads-without-app-changes)
- [Scenario 4 - Recover from a Bad Write Quickly](#scenario-4---recover-from-a-bad-write-quickly)
- [Scenario 5 - Instant Prod-Like Test Environment](#scenario-5---instant-prod-like-test-environment)
- [Scenario 6 - Migrate from RDS MySQL](#scenario-6---migrate-from-rds-mysql)
- [Scenario 7 - Choosing Aurora vs RDS](#scenario-7---choosing-aurora-vs-rds)
- [Scenario 8 - I/O-Optimized Cost Decision](#scenario-8---io-optimized-cost-decision)
- [Scenario 9 - Connection Storm from Lambda](#scenario-9---connection-storm-from-lambda)
- [Scenario 10 - Encrypt an Existing Cluster](#scenario-10---encrypt-an-existing-cluster)
- [Exam Tips & Traps](#exam-tips--traps)

---

## Scenario 1 - Global Low-Latency Reads

**Scenario:** A SaaS app has users in the US, Europe, and Asia. Read latency for non-US users is poor. Writes still happen in us-east-1.

**Answer:** Use **Aurora Global Database** with secondary Regions in Europe and Asia. Route local read traffic to in-Region read replicas; replication lag is **< 1s**. Optionally enable **write forwarding** so secondary-Region apps can still write to the primary.

**Why not others:** Cross-Region RDS read replicas have higher lag and weaker DR; CloudFront caches static content, not relational reads.

[⬆ Back to top](#table-of-contents)

---

## Scenario 2 - Sub-Minute Cross-Region DR

**Scenario:** Compliance requires a DR Region with **RPO of seconds** and **RTO under 1 minute** for a relational database.

**Answer:** **Aurora Global Database**. RPO ~1s, RTO < 1 min via managed/unplanned promotion of the secondary Region to primary.

**Trap:** Restoring from cross-Region snapshot copies meets neither RPO nor RTO. A self-built cross-Region read replica gives higher RPO/RTO than Global Database.

[⬆ Back to top](#table-of-contents)

---

## Scenario 3 - Scale Reads Without App Changes

**Scenario:** Read traffic is growing; the team wants to add read capacity without modifying connection logic.

**Answer:** Add **Aurora Replicas** (up to 15) and point reads at the **reader endpoint**, which load-balances automatically. Enable **Aurora Auto Scaling** to add replicas on CPU/connections.

**Trap:** Pointing apps at **instance endpoints** does not load-balance and breaks on failover.

[⬆ Back to top](#table-of-contents)

---

## Scenario 4 - Recover from a Bad Write Quickly

**Scenario:** A bad migration ran a faulty `UPDATE` 20 minutes ago on an **Aurora MySQL** cluster. The team needs the data back fast with minimal downtime.

**Answer:** Use **Backtrack** to rewind the cluster in place to just before the bad write (within the configured backtrack window). No new cluster, recovery in seconds–minutes.

**Trap:** If it were **Aurora PostgreSQL**, Backtrack is unavailable — use **PITR** instead. Snapshot restore creates a new cluster and is slower.

[⬆ Back to top](#table-of-contents)

---

## Scenario 5 - Instant Prod-Like Test Environment

**Scenario:** QA needs a copy of the 5 TB production database to test a schema change, available within minutes, without impacting prod.

**Answer:** Use **fast database cloning (copy-on-write)**. The clone is ready in minutes regardless of size and only consumes extra storage for changed pages.

**Trap:** Snapshot-and-restore of 5 TB is far slower and more expensive.

[⬆ Back to top](#table-of-contents)

---

## Scenario 6 - Migrate from RDS MySQL

**Scenario:** An existing **RDS for MySQL** database must move to Aurora MySQL with minimal effort and downtime.

**Answer:** Create an **Aurora Read Replica of the RDS MySQL** instance (or restore an RDS snapshot into Aurora), let it sync, then **promote** it / cut over the app. For near-zero downtime across heterogeneous engines, use **AWS DMS**.

**Trap:** You don't need to dump/reload manually; Aurora supports snapshot migration and the Aurora-read-replica promotion path.

[⬆ Back to top](#table-of-contents)

---

## Scenario 7 - Choosing Aurora vs RDS

**Scenario:** A team needs a managed PostgreSQL-compatible DB with high read scalability and fast failover but is unsure between RDS PostgreSQL and Aurora PostgreSQL.

**Answer:** Choose **Aurora PostgreSQL** for **15 low-lag replicas, 6-copy/3-AZ durability, fast failover, and Global Database**. Choose **RDS PostgreSQL** only if you need a specific PG version/extension Aurora lacks or want lower cost at small scale.

**Trap:** "SQL Server / Oracle / MariaDB" requirements rule Aurora out entirely (not supported) — use RDS.

[⬆ Back to top](#table-of-contents)

---

## Scenario 8 - I/O-Optimized Cost Decision

**Scenario:** An I/O-heavy Aurora cluster's bill shows I/O requests are ~35% of total Aurora cost. The team wants lower, more predictable spend.

**Answer:** Switch to **Aurora I/O-Optimized** — no per-request I/O charges, predictable pricing, often cheaper when I/O exceeds **~25%** of the bill.

**Trap:** For a low-I/O workload, I/O-Optimized's higher compute/storage rates would cost more — stay on **Standard**. Remember switching back to Standard is rate-limited.

[⬆ Back to top](#table-of-contents)

---

## Scenario 9 - Connection Storm from Lambda

**Scenario:** A Lambda-based API opens thousands of short-lived connections to Aurora, causing "too many connections" errors and rough failovers.

**Answer:** Put **RDS Proxy** in front of Aurora. It pools/multiplexes connections, smooths failover, and integrates with IAM auth + Secrets Manager.

**Trap:** Just increasing `max_connections` treats the symptom; the connection churn from Lambda still overwhelms the DB.

[⬆ Back to top](#table-of-contents)

---

## Scenario 10 - Encrypt an Existing Cluster

**Scenario:** An unencrypted production Aurora cluster must be encrypted at rest with a customer-managed KMS key.

**Answer:** You **cannot** enable encryption in place. Take a **snapshot**, **copy the snapshot with encryption enabled** (choose the KMS key), then **restore** the encrypted snapshot to a new cluster and cut over.

**Trap:** There is no "modify → enable encryption" toggle for an existing unencrypted cluster.

[⬆ Back to top](#table-of-contents)

---

## Exam Tips & Traps

- Global reads + sub-minute DR → **Aurora Global Database** (RPO ~1s, RTO < 1 min, write forwarding).
- Scale reads, no app change → **reader endpoint** + more replicas + Auto Scaling.
- Quick undo of a bad write (MySQL) → **Backtrack**; PostgreSQL → **PITR**.
- Instant prod-like env → **fast cloning (copy-on-write)**.
- RDS MySQL → Aurora: **Aurora read replica / snapshot migration** or **DMS**.
- Unsupported engine (SQL Server/Oracle/MariaDB) → **RDS**, not Aurora.
- I/O > ~25% of bill → **I/O-Optimized**.
- Lambda connection storms → **RDS Proxy**.
- Encrypt existing cluster → **snapshot → copy with encryption → restore**.

[⬆ Back to top](#table-of-contents)
