# Keyspaces Important Facts & Cheat Sheet - SAA-C03 Deep Dive

> Rapid-fire revision for Amazon Keyspaces — serverless and Cassandra/CQL compatibility, 3-AZ replication, capacity modes (RRU/WRU vs RCU/WCU), PITR and encryption, Multi-Region active-active, a Keyspaces vs DynamoDB table, key CloudWatch metrics, and 15+ exam facts.

See also: [01 - Keyspaces Intro & Core Concepts](01%20-%20Keyspaces%20Intro%20%26%20Core%20Concepts.md) · [02 - Keyspaces Architecture Deep Dive](02%20-%20Keyspaces%20Architecture%20Deep%20Dive.md) · [03 - Keyspaces Best Practices & Examples](03%20-%20Keyspaces%20Best%20Practices%20%26%20Examples.md) · [04 - Keyspaces Scenario Questions](04%20-%20Keyspaces%20Scenario%20Questions.md) · [05 - Keyspaces Troubleshooting (SRE)](05%20-%20Keyspaces%20Troubleshooting%20%28SRE%29.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md) · [01 - DynamoDB Intro & Core Concepts](01%20-%20DynamoDB%20Intro%20%26%20Core%20Concepts.md)

---

## Table of Contents

- [Service Snapshot](#service-snapshot)
- [Capacity and Limits Cheat Sheet](#capacity-and-limits-cheat-sheet)
- [Durability, Backup, and Security](#durability-backup-and-security)
- [Keyspaces vs DynamoDB](#keyspaces-vs-dynamodb)
- [Key CloudWatch Metrics](#key-cloudwatch-metrics)
- [15+ Rapid-Fire Facts](#15-rapid-fire-facts)

---

## Service Snapshot

| Attribute        | Value                                                           |
| :--------------- | :-------------------------------------------------------------- |
| Service          | Amazon Keyspaces (for Apache Cassandra)                         |
| Type             | Serverless, fully managed **wide-column NoSQL**                 |
| API              | **CQL** (Cassandra Query Language)                              |
| Compatibility    | Apache Cassandra **3.11 / 4.x** drivers, `cqlsh`, DSBulk        |
| Servers/clusters | **None** — serverless                                           |
| Connection       | **TLS port 9142** + **SigV4** (or service-specific credentials) |
| Scaling          | Automatic (on-demand) or auto scaling (provisioned)             |

[⬆ Back to top](#table-of-contents)

---

## Capacity and Limits Cheat Sheet

| Item                        | Value                                                                |
| :-------------------------- | :------------------------------------------------------------------- |
| Capacity modes              | **On-demand** (RRU/WRU) and **Provisioned** (RCU/WCU) + auto scaling |
| Write unit                  | 1 WCU/WRU = **1 KB** write                                           |
| Read unit                   | 1 RCU/RRU = **4 KB** `LOCAL_QUORUM` read; **half** for `LOCAL_ONE`   |
| Max row (item) size         | **1 MB**                                                             |
| Consistency levels          | `LOCAL_QUORUM` (strong), `LOCAL_ONE` (eventual, cheaper)             |
| PITR retention              | **Up to 35 days**                                                    |
| Replication (single Region) | **3 copies across multiple AZs**                                     |
| Multi-Region                | Active-active (multi-active), last-writer-wins                       |

> [!tip] Exam Tip
> Memorize the units: **write = 1 KB**, **read = 4 KB** (half for eventual), **row max = 1 MB**, **PITR = 35 days**. These mirror DynamoDB.

[⬆ Back to top](#table-of-contents)

---

## Durability, Backup, and Security

| Control                | Detail                                                                   |
| :--------------------- | :----------------------------------------------------------------------- |
| Durability             | **3 copies / multi-AZ**, automatic, no config                            |
| Region fault tolerance | **Multi-Region replication** (active-active)                             |
| Backup / restore       | **PITR** continuous backups, up to **35 days**, restore to **new table** |
| Encryption at rest     | **Always on**; AWS-owned key or **customer-managed KMS key**             |
| Encryption in transit  | **TLS** (port 9142), required                                            |
| AuthN                  | IAM via **SigV4 plugin** or service-specific credentials                 |
| AuthZ                  | **IAM policies** scoped to keyspaces/tables/actions                      |
| Private network        | **Interface VPC endpoint (PrivateLink)**                                 |
| Audit                  | **AWS CloudTrail** (control plane)                                       |

[⬆ Back to top](#table-of-contents)

---

## Keyspaces vs DynamoDB

| Dimension             | Amazon Keyspaces                         | Amazon DynamoDB                          |
| :-------------------- | :--------------------------------------- | :--------------------------------------- |
| Data model            | **Wide-column (Cassandra)**              | Key-value / document                     |
| API / query language  | **CQL**                                  | DynamoDB API (PartiQL optional)          |
| Best when             | **Existing Cassandra/CQL** workload      | Greenfield AWS-native NoSQL              |
| Serverless            | Yes                                      | Yes                                      |
| Durability            | 3-AZ, automatic                          | 3-AZ, automatic                          |
| Capacity modes        | On-demand / Provisioned (+ auto scaling) | On-demand / Provisioned (+ auto scaling) |
| Global / multi-Region | **Multi-Region replication**             | **Global tables**                        |
| PITR                  | Up to 35 days                            | Up to 35 days                            |
| In-memory cache       | n/a                                      | **DAX**                                  |
| Change stream         | n/a (use app-side)                       | **DynamoDB Streams**                     |

> [!tip] Exam Tip
> The single deciding question: **is there a Cassandra/CQL requirement?** Yes → Keyspaces. No (new AWS NoSQL app) → DynamoDB ([01 - DynamoDB Intro & Core Concepts](01%20-%20DynamoDB%20Intro%20%26%20Core%20Concepts.md)).

[⬆ Back to top](#table-of-contents)

---

## Key CloudWatch Metrics

| Metric                                                           | What it tells you                                                     |
| :--------------------------------------------------------------- | :-------------------------------------------------------------------- |
| `ConsumedReadCapacityUnits` / `ConsumedWriteCapacityUnits`       | Throughput consumption vs provisioned                                 |
| `ProvisionedReadCapacityUnits` / `ProvisionedWriteCapacityUnits` | Configured capacity (provisioned mode)                                |
| `ReadThrottleEvents` / `WriteThrottleEvents`                     | Throttled reads/writes — capacity or hot-partition pressure           |
| `PerConnectionRequestRateExceeded`                               | A single connection exceeded its request rate (pool more connections) |
| `SuccessfulRequestLatency`                                       | Server-side request latency                                           |
| `SystemErrors` / `UserErrors`                                    | Server-side vs client-side (e.g., 4xx) errors                         |

> [!tip] Exam Tip
> Throttle events with high consumption → scale capacity; throttle events with low overall consumption → hot partition. `PerConnectionRequestRateExceeded` → add connections / pool.

[⬆ Back to top](#table-of-contents)

---

## 15+ Rapid-Fire Facts

1. Keyspaces is **serverless, fully managed, Apache Cassandra-compatible** — no nodes or clusters.
2. It uses **CQL** and works with standard **Cassandra drivers** and **`cqlsh`**.
3. Data is replicated **3 times across multiple AZs** in a Region automatically.
4. Two capacity modes: **on-demand (RRU/WRU)** and **provisioned + auto scaling (RCU/WCU)**.
5. **Write unit = 1 KB**; **read unit = 4 KB** (`LOCAL_QUORUM`); `LOCAL_ONE` reads cost **half**.
6. Maximum **row (item) size is 1 MB** — store large blobs in **S3** with a reference.
7. **PITR** provides continuous backups for **up to 35 days**; restore creates a **new table**.
8. **Encryption at rest is always on** (AWS-owned or **customer-managed KMS key**).
9. **Encryption in transit is TLS**, on **port 9142**, and required.
10. Authenticate with the **SigV4 plugin** or **service-specific credentials**; authorize with **IAM**.
11. **Multi-Region replication** is **active-active** (multi-active), last-writer-wins — Cassandra analog of DynamoDB global tables.
12. Reach Keyspaces privately via an **interface VPC endpoint (PrivateLink)**.
13. **Hot partitions** cause throttling even at low overall utilization — fix with **partition-key redesign / write sharding**.
14. Ideal for **high-volume time-series / IoT** with a **bounded composite partition key + time clustering column**.
15. Choose Keyspaces over DynamoDB when there is an **existing Cassandra/CQL requirement**.
16. Operational tasks (patching, repairs, compaction, scaling, node replacement) are **handled by AWS**.
17. **CloudTrail** logs control-plane API activity for auditing.
18. On-demand suits **spiky/unpredictable** traffic; provisioned + auto scaling suits **steady/predictable** traffic.

> [!tip] Exam Tip
> If you see **Cassandra, CQL, cqlsh, keyspace, partition key + clustering column**, or "managed/serverless Cassandra", the answer is **Amazon Keyspaces**.

[⬆ Back to top](#table-of-contents)
