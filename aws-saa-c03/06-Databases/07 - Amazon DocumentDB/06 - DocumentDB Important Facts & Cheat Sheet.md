# DocumentDB Important Facts & Cheat Sheet - SAA-C03 Deep Dive

> A rapid-reference sheet for Amazon DocumentDB: architecture numbers, endpoints, Elastic and Global Clusters, MongoDB-compatibility caveats, the DocumentDB-vs-DynamoDB comparison, key metrics, and 15+ fast facts for the SAA-C03 exam.

See also: [01 - DocumentDB Intro & Core Concepts](01%20-%20DocumentDB%20Intro%20%26%20Core%20Concepts.md) · [02 - DocumentDB Architecture Deep Dive](02%20-%20DocumentDB%20Architecture%20Deep%20Dive.md) · [03 - DocumentDB Best Practices & Examples](03%20-%20DocumentDB%20Best%20Practices%20%26%20Examples.md) · [04 - DocumentDB Scenario Questions](04%20-%20DocumentDB%20Scenario%20Questions.md) · [05 - DocumentDB Troubleshooting (SRE)](05%20-%20DocumentDB%20Troubleshooting%20%28SRE%29.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md) · [01 - Aurora Intro & Core Concepts](01%20-%20Aurora%20Intro%20%26%20Core%20Concepts.md) · [01 - DynamoDB Intro & Core Concepts](01%20-%20DynamoDB%20Intro%20%26%20Core%20Concepts.md)

---

## Table of Contents

- [Architecture Facts](#architecture-facts)
- [Endpoints](#endpoints)
- [Elastic Clusters](#elastic-clusters)
- [Global Clusters](#global-clusters)
- [MongoDB Compatibility Caveats](#mongodb-compatibility-caveats)
- [DocumentDB vs DynamoDB](#documentdb-vs-dynamodb)
- [Key Metrics](#key-metrics)
- [Rapid-Fire Facts](#rapid-fire-facts)
- [Exam Tips & Traps](#exam-tips--traps)

---

## Architecture Facts

| Fact                           | Value                                                       |
| :----------------------------- | :---------------------------------------------------------- |
| Data copies                    | **6 copies across 3 AZs** (2 per AZ)                        |
| Write quorum / read quorum     | 4 of 6 / 3 of 6                                             |
| Max instances                  | **1 primary + up to 15 replicas**                           |
| Storage max (standard cluster) | **64 TiB**, auto-grows in 10 GB increments                  |
| Failover (with a replica)      | Typically **~30 seconds**                                   |
| Backup                         | Continuous to S3; **PITR 1–35 days**                        |
| Encryption                     | **KMS** at rest (set at creation); **TLS** in transit       |
| Port                           | **27017**                                                   |
| Engine                         | MongoDB-compatible (re-implemented on Aurora-style storage) |

[⬆ Back to top](#table-of-contents)

---

## Endpoints

| Endpoint              | Targets                      | Use                                 |
| :-------------------- | :--------------------------- | :---------------------------------- |
| **Cluster endpoint**  | Current **primary**          | Writes; auto-follows failover       |
| **Reader endpoint**   | Balanced across **replicas** | Scale reads                         |
| **Instance endpoint** | One instance                 | Diagnostics (don't hardcode for HA) |

[⬆ Back to top](#table-of-contents)

---

## Elastic Clusters

- **Sharding** for horizontal scale: **millions of reads/writes per second**, **petabyte** storage.
- Managed sharding via a **shard key**; scale shards out/in without downtime.
- Use when a standard cluster (single writer, 64 TiB) is insufficient.

[⬆ Back to top](#table-of-contents)

---

## Global Clusters

- **Cross-Region** replication: 1 primary Region + up to **5 secondary** (read-only) Regions.
- Storage-level replication, typically **< 1 second** lag.
- For **disaster recovery** (promote a secondary) and **low-latency global reads**.

[⬆ Back to top](#table-of-contents)

---

## MongoDB Compatibility Caveats

- Emulates MongoDB **3.6 / 4.0 / 5.0** wire protocols (as of 2024–2025).
- **Not** the MongoDB engine — some operators, index types, and features are unsupported.
- **`retryWrites=false`** is required in the connection string.
- Driver connecting ≠ full feature parity — **validate before migrating** (compatibility tool / functional-differences docs).

[⬆ Back to top](#table-of-contents)

---

## DocumentDB vs DynamoDB

| Dimension   | DocumentDB                             | DynamoDB                                |
| :---------- | :------------------------------------- | :-------------------------------------- |
| Model       | Document (MongoDB API)                 | Key-value + document                    |
| API         | **MongoDB** drivers/query language     | AWS SDK / PartiQL                       |
| Management  | Managed, **instance-based**            | Managed, **serverless**                 |
| Scaling     | Replicas + Elastic Clusters            | Automatic, near-infinite                |
| Consistency | Strong (primary) / eventual (replicas) | Eventual or strong (per request)        |
| Best for    | **Migrating/keeping MongoDB**          | New serverless apps, key-value at scale |
| Pricing     | Instance-hours + storage + I/O         | On-demand / provisioned capacity        |

[⬆ Back to top](#table-of-contents)

---

## Key Metrics

| Metric                       | Meaning                             |
| :--------------------------- | :---------------------------------- |
| `CPUUtilization`             | Instance compute load               |
| `DatabaseConnections`        | Active connections vs limit         |
| `DBClusterReplicaLagMaximum` | Replica staleness                   |
| `BufferCacheHitRatio`        | Working set in memory (high = good) |
| `ReadIOPS` / `WriteIOPS`     | I/O volume (indexes, cost)          |
| `VolumeBytesUsed`            | Storage toward 64 TiB               |
| `FreeableMemory`             | Available instance memory           |

[⬆ Back to top](#table-of-contents)

---

## Rapid-Fire Facts

1. DocumentDB is **fully managed and MongoDB-compatible** (API/wire protocol).
2. It is built on an **Aurora-style** distributed storage architecture, not the MongoDB engine.
3. Storage is replicated **6 ways across 3 AZs**.
4. Up to **15 replica instances** per cluster.
5. Storage auto-grows to **64 TiB** (Aurora is 128 TiB — different number).
6. **Cluster endpoint** = writer; **reader endpoint** = balanced reads.
7. Failover with a replica is typically **~30 seconds**.
8. Default port is **27017** (same as MongoDB).
9. **TLS** in transit by default; clients use the **`global-bundle.pem`** CA file.
10. **KMS** encryption at rest must be enabled **at creation** (snapshot-copy-restore to add later).
11. **PITR** within a **1–35 day** retention window; continuous backup to **S3**.
12. **Restores always create a new cluster** (no in-place restore).
13. **Elastic Clusters** add **sharding** for millions of ops/sec and **petabyte** scale.
14. **Global Clusters** give **cross-Region** DR + low-latency reads (up to 5 secondary Regions).
15. Connection string must use **`retryWrites=false`**.
16. Replica reads are **eventually consistent**; read from the primary for consistency.
17. Use **AWS DMS** for minimal-downtime MongoDB migration; **mongodump/mongorestore** for offline.
18. Choose **DocumentDB** when you must keep MongoDB; choose **DynamoDB** when serverless/no MongoDB need.

[⬆ Back to top](#table-of-contents)

---

## Exam Tips & Traps

- "Managed **MongoDB-compatible** document DB / keep MongoDB drivers" → **DocumentDB**.
- **6 copies / 3 AZs**, **64 TiB**, **15 replicas**, **~30s failover** — memorize these.
- Don't confuse the **64 TiB** (DocumentDB) cap with Aurora's **128 TiB**.
- **Cluster endpoint = writes**, **reader endpoint = reads**; never hardcode instance endpoints for HA.
- **Encryption at rest** is creation-time only (snapshot-copy-restore otherwise).
- **Elastic Clusters** = sharding for huge scale; **Global Clusters** = cross-Region DR.
- DocumentDB requires **`retryWrites=false`**; MongoDB feature gaps exist — validate first.

[⬆ Back to top](#table-of-contents)
