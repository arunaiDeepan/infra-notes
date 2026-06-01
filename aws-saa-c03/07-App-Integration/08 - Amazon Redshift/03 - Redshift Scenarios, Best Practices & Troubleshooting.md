# Amazon Redshift - Scenarios, Best Practices & SRE Troubleshooting (SAA-C03)

> Scenario drills + a real performance-tuning/SRE playbook. The exam keeps asking "Redshift vs Athena vs RDS vs EMR" and "how do I make this query/cluster faster?"

See also: [01 - Redshift Fundamentals & Deep Dive](01%20-%20Redshift%20Fundamentals%20%26%20Deep%20Dive.md) · [02 - Redshift Architecture & Examples](02%20-%20Redshift%20Architecture%20%26%20Examples.md)

---

## Table of Contents

- [1. Scenario-Based Questions](#1-scenario-based-questions)
- [2. Best Practices](#2-best-practices)
- [3. Common Errors & Troubleshooting (SRE View)](#3-common-errors--troubleshooting-sre-view)
- [4. Performance Tuning Checklist](#4-performance-tuning-checklist)
- [5. Key Metrics](#5-key-metrics)
- [6. Service Selection Guide](#6-service-selection-guide)
- [7. Rapid-Fire Facts](#7-rapid-fire-facts)

---

## 1. Scenario-Based Questions

**Q1.** A company needs to run complex BI aggregations over 5 years of structured sales data, refreshed nightly, for dashboards.
**A.** **Amazon Redshift** data warehouse (OLAP). Not RDS (OLTP) or Athena (ad-hoc).

---

**Q2.** Analysts query data in S3 only a few times a month and don't want to manage any infrastructure.
**A.** **Amazon Athena** (serverless, pay-per-query). Not Redshift (a cluster would sit idle).

---

**Q3.** They must query petabytes of historical data in S3 **and** join it with current warehouse tables.
**A.** **Redshift Spectrum**.

---

**Q4.** Every morning, 100 analysts run dashboards and queries queue badly for 30 minutes.
**A.** Enable **Concurrency Scaling** to absorb the burst.

---

**Q5.** Joins between two large tables are slow due to heavy data redistribution across nodes.
**A.** Set a **DISTKEY** on the join column (KEY distribution) so matching rows are co-located; use **ALL** for small dimension tables.

---

**Q6.** Date-range queries scan the whole table and are slow.
**A.** Add a **SORTKEY** on the date column (zone maps skip non-matching blocks).

---

**Q7.** Loading data with millions of single-row `INSERT`s is extremely slow.
**A.** Use **`COPY`** from S3 with split files for parallel load.

---

**Q8.** Workload is spiky and unpredictable; they don't want to size or manage clusters.
**A.** **Redshift Serverless**.

---

**Q9.** Need storage to grow to petabytes while keeping compute modest.
**A.** **RA3 nodes** (managed storage scales independently of compute).

---

**Q10.** Share live warehouse data with another business unit's cluster without copying/ETL.
**A.** **Redshift Data Sharing**.

---

**Q11.** Analytics must not impact the production Aurora OLTP database.
**A.** **Federated query** or **Aurora zero-ETL to Redshift** (offload analytics from OLTP).

---

**Q12.** DR requires the warehouse recoverable in another region.
**A.** **Cross-region automated snapshot copy** (restore there if needed).

[⬆ Back to top](#table-of-contents)

---

## 2. Best Practices

| Area             | Best Practice                                                                           |
| :--------------- | :-------------------------------------------------------------------------------------- |
| **Loading**      | Use `COPY` from S3 with files = multiple of slice count; avoid row `INSERT`.            |
| **Distribution** | KEY for big joins, ALL for small dims, AUTO when unsure.                                |
| **Sort keys**    | Sort on common filter/range columns (often date).                                       |
| **Compression**  | Let `COPY`/`ANALYZE COMPRESSION` pick encodings.                                        |
| **Maintenance**  | Run `VACUUM`/`ANALYZE` (or rely on auto) to reclaim space & update stats.               |
| **WLM**          | Use **Automatic WLM** + query priorities + **Concurrency Scaling** for mixed workloads. |
| **Cost**         | Use **RA3/Serverless**, pause/resume idle clusters, Reserved nodes for steady use.      |
| **Spectrum**     | Keep cold data in S3 (Parquet, partitioned) instead of loading everything.              |
| **Security**     | KMS at rest, TLS in transit, VPC-private, column/row-level security.                    |
| **DR**           | Automated + cross-region snapshots; consider RA3 Multi-AZ.                              |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Errors & Troubleshooting (SRE View)

| Symptom                              | Likely Cause                                                   | Resolution                                                |
| :----------------------------------- | :------------------------------------------------------------- | :-------------------------------------------------------- |
| **Slow joins / high "DS_BCAST"**     | Tables not co-located; broadcast/redistribution                | Set proper **DISTKEY**; ALL for small dims                |
| **Queries scan whole table**         | No/poor **sort key**                                           | Add SORTKEY on filter columns                             |
| **Disk full / `Disk Full` errors**   | Bloat from updates/deletes; skewed distribution; spill to disk | `VACUUM`; fix skewed DISTKEY; add nodes; resize/RA3       |
| **Slow `COPY`**                      | Single large file / row INSERTs                                | Split files for parallel COPY; use COPY not INSERT        |
| **Queries queue at peak**            | WLM concurrency limits                                         | Enable **Concurrency Scaling**; tune WLM                  |
| **Data skew (one node hot)**         | Bad DISTKEY (low cardinality)                                  | Choose higher-cardinality key or EVEN                     |
| **`COPY` permission denied to S3**   | Missing IAM role on cluster                                    | Attach IAM role with `s3:GetObject`; reference in COPY    |
| **Stale query plans**                | Out-of-date stats                                              | Run `ANALYZE` (or rely on auto-analyze)                   |
| **Spectrum slow/costly**             | Unpartitioned, row formats                                     | Partition + columnar (Parquet) in S3                      |
| **Cluster unavailable (AZ failure)** | Single-AZ classic cluster                                      | Restore snapshot / relocate AZ; use RA3 Multi-AZ          |
| **High cost, low usage**             | Cluster idle                                                   | Pause/resume; move to **Serverless**; Reserved for steady |

**SRE note:** ~80% of Redshift performance incidents trace back to **physical design** - wrong **distribution key** (causing data redistribution/skew) or missing **sort key** (causing full scans). Before scaling out hardware, check the query plan (`EXPLAIN`) for broadcasts/redistribution and verify `COPY` parallelism. Disk-full incidents are usually **skew or bloat**, fixed by VACUUM + redesign, not just adding nodes.

[⬆ Back to top](#table-of-contents)

---

## 4. Performance Tuning Checklist

1. **`EXPLAIN`** the slow query - look for `DS_BCAST_INNER`/`DS_DIST_*` (redistribution).
2. Fix **distribution**: KEY on join columns, ALL for small dimensions.
3. Set/verify **sort keys** on common filters.
4. Ensure **stats are fresh** (`ANALYZE`) and tables not bloated (`VACUUM`).
5. Check for **data skew** (uneven rows per slice).
6. Use **`COPY`** with split files; confirm compression encodings.
7. Enable **Concurrency Scaling** + tune **WLM** for concurrency spikes.
8. Offload cold data to **S3 + Spectrum**; use **materialized views** for repeated aggregations.

[⬆ Back to top](#table-of-contents)

---

## 5. Key Metrics

| Metric                                        | Tells You                              |
| :-------------------------------------------- | :------------------------------------- |
| `CPUUtilization`                              | Cluster compute pressure               |
| `PercentageDiskSpaceUsed`                     | Storage saturation (alarm before full) |
| `QueryDuration` / `QueriesCompletedPerSecond` | Query performance/throughput           |
| `WLMQueueLength` / `WLMQueueWaitTime`         | Queuing → enable concurrency scaling   |
| `ConcurrencyScalingActiveClusters`            | Burst scaling in use                   |
| `ReadIOPS` / `ReadLatency`                    | I/O behavior (scan efficiency)         |

[⬆ Back to top](#table-of-contents)

---

## 6. Service Selection Guide

| If the question says…                                           | Answer                  |
| :-------------------------------------------------------------- | :---------------------- |
| "Data warehouse", "BI", "complex analytics", "petabyte", "OLAP" | **Redshift**            |
| "Ad-hoc", "occasional", "serverless SQL on S3", "pay per query" | **Athena**              |
| "Transactions", "OLTP", "app database", "single-row"            | **RDS / Aurora**        |
| "Key-value", "millisecond", "massive scale"                     | **DynamoDB**            |
| "Spark", "Hadoop", "Hive", "custom big-data framework"          | **EMR**                 |
| "Query S3 from the warehouse without loading"                   | **Redshift Spectrum**   |
| "Don't manage clusters / variable load"                         | **Redshift Serverless** |

[⬆ Back to top](#table-of-contents)

---

## 7. Rapid-Fire Facts

- **OLAP** warehouse: columnar + compression + **MPP** (leader/compute/slices).
- **RA3** = separate compute/storage; **DC2** = SSD; **Serverless** = no clusters.
- Performance = **distribution style** (KEY/ALL/EVEN/AUTO) + **sort keys**.
- **`COPY`** from S3 (parallel) to load; **`UNLOAD`** to export.
- **Spectrum** queries S3 directly; **Concurrency Scaling** for bursts; **Data Sharing** without copies.
- **Snapshots** to S3 + **cross-region copy**; RA3 **Multi-AZ** for HA.
- KMS at rest, TLS in transit, VPC-private, column/row-level security.
- vs **Athena** (ad-hoc S3), **RDS/Aurora** (OLTP), **EMR** (Spark/Hadoop).

[⬆ Back to top](#table-of-contents)
