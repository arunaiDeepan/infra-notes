# Redshift Scenario Questions - SAA-C03 Deep Dive

> Exam-style scenarios mapping real problems to the right Redshift (or non-Redshift) answer: offloading analytics, petabyte BI, querying S3, spiky concurrency, decoupled scaling, cross-Region DR, and the OLTP trap.

See also: [01 - Redshift Intro & Core Concepts](01%20-%20Redshift%20Intro%20%26%20Core%20Concepts.md) · [02 - Redshift Architecture Deep Dive](02%20-%20Redshift%20Architecture%20Deep%20Dive.md) · [03 - Redshift Best Practices & Examples](03%20-%20Redshift%20Best%20Practices%20%26%20Examples.md) · [05 - Redshift Troubleshooting (SRE)](05%20-%20Redshift%20Troubleshooting%20%28SRE%29.md) · [06 - Redshift Important Facts & Cheat Sheet](06%20-%20Redshift%20Important%20Facts%20%26%20Cheat%20Sheet.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md) · [01 - RDS Intro & Core Concepts](01%20-%20RDS%20Intro%20%26%20Core%20Concepts.md)

---

## Table of Contents

- [Scenario 1 - Analytics Slowing the Production OLTP Database](#scenario-1---analytics-slowing-the-production-oltp-database)
- [Scenario 2 - Petabyte-Scale BI and Reporting](#scenario-2---petabyte-scale-bi-and-reporting)
- [Scenario 3 - Query Data in S3 Without Loading It](#scenario-3---query-data-in-s3-without-loading-it)
- [Scenario 4 - Spiky Concurrent BI Users](#scenario-4---spiky-concurrent-bi-users)
- [Scenario 5 - Decouple Storage and Compute](#scenario-5---decouple-storage-and-compute)
- [Scenario 6 - Cross-Region Disaster Recovery](#scenario-6---cross-region-disaster-recovery)
- [Scenario 7 - The OLTP Transactional Trap](#scenario-7---the-oltp-transactional-trap)
- [Scenario 8 - Intermittent Analytics](#scenario-8---intermittent-analytics)
- [Scenario 9 - Repeated Expensive Aggregations](#scenario-9---repeated-expensive-aggregations)
- [Scenario 10 - Share Data Across Teams Without Copies](#scenario-10---share-data-across-teams-without-copies)

---

## Scenario 1 - Analytics Slowing the Production OLTP Database

**Scenario:** A company's analysts run heavy reporting queries directly against the production RDS/Aurora database. These queries consume resources and slow down customer transactions.

**Answer:** Offload analytics to **Amazon Redshift**. Replicate/ETL the data into Redshift (via AWS Glue, DMS, or scheduled `COPY` from S3 exports) and point BI tools at Redshift. The OLTP database serves transactions; Redshift serves analytics.

> [!tip] Why
> Separating OLAP from OLTP is the core use case. A read replica could help simple read scaling, but **complex analytical aggregation** belongs in a columnar data warehouse, not on the transactional engine.

[⬆ Back to top](#table-of-contents)

---

## Scenario 2 - Petabyte-Scale BI and Reporting

**Scenario:** An enterprise needs a managed data warehouse to consolidate petabytes of historical data from many sources and serve BI dashboards with complex SQL aggregations.

**Answer:** **Amazon Redshift** (RA3 cluster or Serverless), feeding **QuickSight/Tableau**. Use columnar storage + MPP for fast aggregation at petabyte scale; use RA3 managed storage to scale storage.

> [!tip] Why
> "Petabyte-scale data warehouse" + "complex analytical/BI queries" is the textbook Redshift signal.

[⬆ Back to top](#table-of-contents)

---

## Scenario 3 - Query Data in S3 Without Loading It

**Scenario:** Most data already sits in an **S3 data lake** (Parquet). The team wants to run SQL analytics joining it with warehouse tables, **without** the cost/time of loading everything into the cluster.

**Answer:** **Redshift Spectrum** — define external tables over S3 and query in place; join S3 data with local Redshift tables. (If they want a fully serverless, cluster-independent query engine, **Amazon Athena** is the alternative.)

> [!tip] Why
> Spectrum queries S3 directly on a separate compute fleet, billed per TB scanned — no loading required. Keep hot data in-cluster, cold data in S3.

[⬆ Back to top](#table-of-contents)

---

## Scenario 4 - Spiky Concurrent BI Users

**Scenario:** Each morning hundreds of analysts open dashboards at once; queries **queue** and slow down. Off-peak, the cluster is underutilized. They don't want to pay for a permanently larger cluster.

**Answer:** Enable **Concurrency Scaling** on the WLM queue. Transient clusters spin up to absorb the burst and spin down afterward; free daily credits often cover it.

> [!tip] Why
> The problem is **concurrency at peak**, not raw size. Concurrency Scaling adds temporary read capacity automatically without permanent over-provisioning.

[⬆ Back to top](#table-of-contents)

---

## Scenario 5 - Decouple Storage and Compute

**Scenario:** A warehouse's **data is growing fast**, but query compute needs are stable. On older nodes, adding storage forces adding compute (and cost) they don't need.

**Answer:** Use **RA3 nodes with Redshift Managed Storage (RMS)**. Storage scales independently in S3-backed managed storage; you size compute purely for performance.

> [!tip] Why
> RA3 **decouples storage and compute** — the defining reason to choose RA3 over DC2. Grow data without buying compute.

[⬆ Back to top](#table-of-contents)

---

## Scenario 6 - Cross-Region Disaster Recovery

**Scenario:** Compliance requires the data warehouse to be recoverable in a **second Region** if the primary Region fails.

**Answer:** Enable **automated snapshots** and **cross-Region snapshot copy** to the DR Region; restore a snapshot into a new cluster there during a disaster.

> [!tip] Why
> Snapshots are stored in S3 and incremental; cross-Region copy provides an off-Region recovery point. Restore creates a new cluster.

[⬆ Back to top](#table-of-contents)

---

## Scenario 7 - The OLTP Transactional Trap

**Scenario:** A new e-commerce app needs a database for **order processing**: many small, low-latency reads and writes per second, ACID transactions, single-record lookups.

**Answer:** **NOT Redshift.** Use **Amazon RDS/Aurora** (relational/ACID) or **DynamoDB** (key-value, single-digit-ms). Redshift is OLAP and performs poorly on high-frequency single-row writes.

> [!tip] Why
> This is the classic distractor. "Transactional", "low-latency", "per-record", "shopping cart/orders" → OLTP → **not** a data warehouse. Picking Redshift here is the trap.

[⬆ Back to top](#table-of-contents)

---

## Scenario 8 - Intermittent Analytics

**Scenario:** A startup runs analytics only **a few times a week**, with unpredictable volume, and doesn't want to size or pay for an idle cluster.

**Answer:** **Redshift Serverless** — pay per RPU-hour, auto-scales with the workload, scales to near-zero when idle. No node sizing or cluster management.

> [!tip] Why
> Intermittent/unpredictable + "no capacity planning, pay for what you use" → **Serverless**. A pausable provisioned cluster is an alternative but Serverless is the cleanest fit.

[⬆ Back to top](#table-of-contents)

---

## Scenario 9 - Repeated Expensive Aggregations

**Scenario:** A dashboard reruns the same costly multi-table aggregation every few minutes, straining the cluster.

**Answer:** Create a **materialized view** that precomputes the aggregation; the dashboard reads the stored result and the view is refreshed (auto or scheduled).

> [!tip] Why
> Materialized views cache expensive results, cutting repeated compute. Pair with Concurrency Scaling if many users hit it simultaneously.

[⬆ Back to top](#table-of-contents)

---

## Scenario 10 - Share Data Across Teams Without Copies

**Scenario:** Several teams (and accounts) need **read access** to the same warehouse data, but maintaining ETL copies for each is costly and error-prone.

**Answer:** Use **Redshift data sharing** (RA3) to share **live** data across clusters/workgroups, accounts (via AWS RAM), and Regions — no copying or ETL duplication.

> [!tip] Why
> Data sharing provides live, read-only access without data movement, isolating each consumer's compute. Requires RA3.

[⬆ Back to top](#table-of-contents)
