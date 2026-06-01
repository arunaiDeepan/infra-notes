# Redshift Important Facts & Cheat Sheet - SAA-C03 Deep Dive

> Rapid-fire reference: OLAP vs OLTP, node types, distribution and sort keys, Spectrum vs Concurrency Scaling, key features, security/encryption, and 20+ exam facts. Remember: Redshift = analytics only.

See also: [01 - Redshift Intro & Core Concepts](01%20-%20Redshift%20Intro%20%26%20Core%20Concepts.md) · [02 - Redshift Architecture Deep Dive](02%20-%20Redshift%20Architecture%20Deep%20Dive.md) · [03 - Redshift Best Practices & Examples](03%20-%20Redshift%20Best%20Practices%20%26%20Examples.md) · [04 - Redshift Scenario Questions](04%20-%20Redshift%20Scenario%20Questions.md) · [05 - Redshift Troubleshooting (SRE)](05%20-%20Redshift%20Troubleshooting%20%28SRE%29.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md) · [01 - RDS Intro & Core Concepts](01%20-%20RDS%20Intro%20%26%20Core%20Concepts.md)

---

## Table of Contents

- [OLAP vs OLTP](#olap-vs-oltp)
- [Node Types - RA3 vs DC2](#node-types---ra3-vs-dc2)
- [Distribution Styles](#distribution-styles)
- [Sort Key Types](#sort-key-types)
- [Spectrum vs Concurrency Scaling](#spectrum-vs-concurrency-scaling)
- [Key Features Quick Table](#key-features-quick-table)
- [Security and Encryption Facts](#security-and-encryption-facts)
- [Rapid-Fire Exam Facts](#rapid-fire-exam-facts)

---

## OLAP vs OLTP

|          | OLAP (Redshift)           | OLTP (RDS / Aurora / DynamoDB) |
| :------- | :------------------------ | :----------------------------- |
| Workload | Analytics, BI, reporting  | Transactions, app operations   |
| Storage  | **Columnar**              | Row-based / key-value          |
| Queries  | Few, large, complex scans | Many, small, fast              |
| Writes   | Bulk load (COPY)          | High-frequency single-row      |
| Latency  | Seconds–minutes           | Single-digit ms                |
| Scale    | TB–PB                     | GB–TB                          |

> [!tip] Exam Tip
> The #1 Redshift fact: **Redshift is OLAP, not OLTP.** Transactional/low-latency/single-record → not Redshift.

[⬆ Back to top](#table-of-contents)

---

## Node Types - RA3 vs DC2

|              | RA3                                                              | DC2                                  |
| :----------- | :--------------------------------------------------------------- | :----------------------------------- |
| Storage      | **Managed storage (RMS)**, S3-backed, **decoupled** from compute | Local SSD, **coupled** to compute    |
| Scale        | Storage and compute **independently**                            | Add nodes to add storage             |
| Data sharing | **Yes**                                                          | No                                   |
| Best for     | Large/growing data; modern default                               | Small datasets (< ~1 TB), low cost   |
| Legacy       | —                                                                | DS2 (HDD) is legacy → migrate to RA3 |

> [!tip] Exam Tip
> "Decouple storage & compute / data growing fast" → **RA3**. "Small dataset, cheap, fast SSD" → **DC2**.

[⬆ Back to top](#table-of-contents)

---

## Distribution Styles

| Style    | Placement                   | Use when                                        |
| :------- | :-------------------------- | :---------------------------------------------- |
| **KEY**  | Same key value → same slice | Large tables joined on a common key (co-locate) |
| **ALL**  | Full copy on every node     | Small dimension/lookup tables joined often      |
| **EVEN** | Round-robin                 | No clear join key                               |
| **AUTO** | Redshift decides            | Default / unsure                                |

> [!tip] Exam Tip
> ALL = small dims, KEY = big-table joins, EVEN = no key, AUTO = default. Bad KEY → **data skew**.

[⬆ Back to top](#table-of-contents)

---

## Sort Key Types

| Type                   | Behavior                                            | Use when                                          |
| :--------------------- | :-------------------------------------------------- | :------------------------------------------------ |
| **Compound** (default) | Sorts by columns in order; great for prefix filters | One dominant filter/join column (e.g., date)      |
| **Interleaved**        | Equal weight to each column; higher VACUUM cost     | Queries filter on different columns unpredictably |

> [!tip] Exam Tip
> Sort key powers **zone-map pruning** (skip blocks). Compound for a dominant column; interleaved only for multi-column unpredictable filtering.

[⬆ Back to top](#table-of-contents)

---

## Spectrum vs Concurrency Scaling

|                | Redshift Spectrum                    | Concurrency Scaling                      |
| :------------- | :----------------------------------- | :--------------------------------------- |
| Problem solved | Query **S3 data without loading** it | Bursts of **concurrent queries** queuing |
| Compute        | Separate Spectrum fleet              | Transient added clusters                 |
| Data location  | S3 (external tables)                 | Existing cluster data                    |
| Billing        | Per **TB scanned**                   | Per second beyond free daily credits     |
| Trigger        | External table query                 | WLM queue / read burst                   |

> [!tip] Exam Tip
> Cold data in S3 → **Spectrum**. Too many simultaneous users → **Concurrency Scaling**. Don't swap them.

[⬆ Back to top](#table-of-contents)

---

## Key Features Quick Table

| Feature                    | What it does                                                     |
| :------------------------- | :--------------------------------------------------------------- |
| **Leader node**            | Parses, plans, coordinates, aggregates; free; one per cluster    |
| **Compute nodes / slices** | Store data, run query fragments in parallel (MPP)                |
| **Redshift Spectrum**      | SQL over S3 external tables, separate compute                    |
| **Concurrency Scaling**    | Auto transient clusters for read bursts                          |
| **WLM** (auto/manual)      | Query queues, memory, concurrency; SQA, QMR                      |
| **Materialized views**     | Cache expensive aggregation results                              |
| **Data sharing** (RA3)     | Live cross-cluster/account/Region read access, no copy           |
| **Snapshots**              | Incremental backups to S3; automated + manual; cross-Region copy |
| **AQUA**                   | Hardware-accelerated query cache for some RA3                    |
| **Redshift Serverless**    | No clusters; capacity in **RPUs**; pay per use; auto-scale       |
| **COPY / UNLOAD**          | Parallel bulk load from / export to S3                           |
| **VACUUM / ANALYZE**       | Reclaim+resort / refresh statistics                              |

> [!tip] Exam Tip
> Serverless capacity unit = **RPU**. Bulk load = **COPY** (parallel, split files), never row INSERTs.

[⬆ Back to top](#table-of-contents)

---

## Security and Encryption Facts

| Topic          | Fact                                                                                              |
| :------------- | :------------------------------------------------------------------------------------------------ |
| Network        | Runs in a **VPC**; security groups; **Enhanced VPC Routing** keeps COPY/UNLOAD traffic in the VPC |
| Private access | **Redshift-managed VPC endpoints** / PrivateLink                                                  |
| At rest        | **KMS** or **CloudHSM** encryption (blocks + snapshots)                                           |
| In transit     | **SSL/TLS** to the cluster                                                                        |
| Auth/authz     | IAM roles for COPY/UNLOAD/Spectrum; DB users/groups; IdP/SSO federation                           |
| Auditing       | Audit logging to S3 / CloudWatch                                                                  |
| Fine-grained   | Column-level and row-level security                                                               |

> [!tip] Exam Tip
> "Control encryption keys" → **KMS/CloudHSM**. "Keep load traffic private" → **Enhanced VPC Routing**. "Use roles not keys for S3" → IAM role on COPY/UNLOAD.

[⬆ Back to top](#table-of-contents)

---

## Rapid-Fire Exam Facts

1. Redshift is a **petabyte-scale OLAP data warehouse**, not OLTP.
2. It uses **columnar storage + MPP + compression** for fast analytics.
3. SQL dialect is **based on PostgreSQL** but it is **not** a transactional DB.
4. **Leader node** plans/coordinates (free); **compute nodes** + **slices** do the work in parallel.
5. **RA3** decouples storage/compute via **Redshift Managed Storage (RMS)**; **DC2** is local SSD for small data.
6. **Distribution styles:** KEY, EVEN, ALL, AUTO.
7. **DISTSTYLE ALL** = small dimension tables; **KEY** = big-table joins; bad KEY = **skew**.
8. **Sort keys:** compound (default) vs interleaved; power **zone-map** block pruning.
9. **Redshift Spectrum** queries **S3** directly (external tables, Glue Data Catalog), billed **per TB scanned**.
10. **Concurrency Scaling** auto-adds transient clusters for read bursts (free daily credits).
11. **WLM** manages queues/memory/concurrency; **Automatic WLM** recommended; **SQA** for short queries.
12. **Materialized views** cache expensive aggregations.
13. **Data sharing** (RA3) shares live data across clusters/accounts/Regions, no copy.
14. **Snapshots** are incremental, stored in **S3**; automated + manual; **cross-Region copy** for DR.
15. Automated snapshots are **deleted with the cluster** — take a **final manual snapshot**.
16. **Bulk load with COPY** from S3 (split files for parallelism); avoid frequent **INSERTs**.
17. **UNLOAD** exports query results to S3 in parallel.
18. **VACUUM** reclaims space + re-sorts; **ANALYZE** refreshes planner statistics.
19. **Redshift Serverless** = no cluster management, capacity in **RPUs**, pay per use, scales to near-zero.
20. **Cost:** Reserved Instances + RA3 for steady; **pause/resume** or **Serverless** for part-time; **Spectrum** for cold S3 data.
21. **Encryption** via **KMS/CloudHSM**; **SSL/TLS** in transit; runs in a **VPC**.
22. **Enhanced VPC Routing** forces COPY/UNLOAD traffic through the VPC.
23. **AQUA** accelerates scan-heavy queries on supported RA3 nodes.
24. **Offload analytics from OLTP** (RDS/Aurora) to Redshift to stop reporting from slowing the app.
25. **Athena** is the serverless alternative for SQL-on-S3 when no cluster is wanted.
26. **OLTP / transactional / low-latency single-record** scenarios → **NOT Redshift** (use RDS/Aurora/DynamoDB).

> [!tip] Exam Tip
> If you remember one thing: **Redshift = analytics (OLAP) only.** Match BI/reporting/petabyte-aggregation to Redshift; match transactions to RDS/Aurora/DynamoDB.

[⬆ Back to top](#table-of-contents)
