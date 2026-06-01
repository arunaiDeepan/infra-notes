# DynamoDB Important Facts & Cheat Sheet - SAA-C03 Deep Dive

> Last-minute revision: RCU/WCU formulas with worked examples, hard limits, GSI vs LSI table, consistency table, Streams/TTL/PITR facts, DAX vs ElastiCache, capacity-mode table, and 25+ rapid-fire facts.

See also: [01 - DynamoDB Intro & Core Concepts](01%20-%20DynamoDB%20Intro%20%26%20Core%20Concepts.md) · [02 - DynamoDB Architecture Deep Dive](02%20-%20DynamoDB%20Architecture%20Deep%20Dive.md) · [03 - DynamoDB Best Practices & Examples](03%20-%20DynamoDB%20Best%20Practices%20%26%20Examples.md) · [04 - DynamoDB Scenario Questions](04%20-%20DynamoDB%20Scenario%20Questions.md) · [05 - DynamoDB Troubleshooting (SRE)](05%20-%20DynamoDB%20Troubleshooting%20%28SRE%29.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md) · [01 - ElastiCache Intro & Core Concepts](01%20-%20ElastiCache%20Intro%20%26%20Core%20Concepts.md)

---

## Table of Contents

- [RCU and WCU Formulas with Worked Examples](#rcu-and-wcu-formulas-with-worked-examples)
- [Hard Limits](#hard-limits)
- [GSI vs LSI](#gsi-vs-lsi)
- [Consistency Models](#consistency-models)
- [Capacity Modes](#capacity-modes)
- [Streams, TTL, and PITR Facts](#streams-ttl-and-pitr-facts)
- [DAX vs ElastiCache](#dax-vs-elasticache)
- [Rapid-Fire Facts](#rapid-fire-facts)
- [Summary: Key Takeaways for SAA-C03](#summary-key-takeaways-for-saa-c03)

---

## RCU and WCU Formulas with Worked Examples

**Formulas:**

- **1 RCU** = 1 **strongly consistent** read/sec of up to **4 KB** = **2 eventually consistent** reads/sec of up to 4 KB.
- **Transactional read** = **2 RCU** per 4 KB read.
- **1 WCU** = 1 **standard** write/sec of up to **1 KB**.
- **Transactional write** = **2 WCU** per 1 KB write.
- Item size rounds **up**: reads to the next **4 KB**, writes to the next **1 KB**.

| Workload                                 | Calculation                       | Answer      |
| :--------------------------------------- | :-------------------------------- | :---------- |
| 100 reads/s, 8 KB, strongly consistent   | ceil(8/4)=2 RCU x 100             | **200 RCU** |
| 100 reads/s, 8 KB, eventually consistent | (2/2)=1 RCU x 100                 | **100 RCU** |
| 50 reads/s, 6 KB, strongly consistent    | ceil(6/4)=2 RCU x 50              | **100 RCU** |
| 50 writes/s, 2.5 KB                      | ceil(2.5/1)=3 WCU x 50            | **150 WCU** |
| 10 transactional writes/s, 1 KB          | 2 WCU x 10                        | **20 WCU**  |
| 200 reads/s, 1 KB, eventually consistent | ceil(1/4)=1 -> /2 = 0.5 RCU x 200 | **100 RCU** |

> **Exam Tip:** Always check the consistency model: eventual = **half** the read cost; transactional = **double** read/write cost.

[⬆ Back to top](#table-of-contents)

---

## Hard Limits

| Limit                       | Value                                      |
| :-------------------------- | :----------------------------------------- |
| Max item size               | **400 KB** (item + all attributes)         |
| Partition key length        | 1 - 2048 bytes                             |
| Sort key length             | 1 - 1024 bytes                             |
| Per-partition throughput    | **3000 RCU** and **1000 WCU**              |
| Per-partition size          | **10 GB**                                  |
| GSIs per table              | **20** (default soft limit)                |
| LSIs per table              | **5** (hard, create-time only)             |
| Items per LSI partition key | <= **10 GB** collection size               |
| Transaction limit           | **100 items / 4 MB** per TransactWrite/Get |
| BatchGetItem                | 100 items / 16 MB                          |
| BatchWriteItem              | 25 items / 16 MB                           |
| Query/Scan result page      | **1 MB** (then paginate)                   |
| Streams retention           | **24 hours**                               |
| PITR window                 | **35 days**                                |
| Mode switch frequency       | once per **24 hours**                      |

> **Exam Tip:** Memorize **400 KB item**, **3000 RCU/1000 WCU per partition**, **5 LSIs (create-time only)**, **24h Streams**, **35-day PITR**.

[⬆ Back to top](#table-of-contents)

---

## GSI vs LSI

| Feature         | **GSI**                                         | **LSI**                            |
| :-------------- | :---------------------------------------------- | :--------------------------------- |
| Partition key   | Different from base                             | **Same** as base                   |
| Sort key        | Any attribute (optional)                        | Alternate sort key                 |
| Created         | **Any time**                                    | **Table creation only**            |
| Capacity        | **Own** RCU/WCU                                 | **Shares** base table capacity     |
| Consistency     | **Eventual only**                               | **Strong or eventual**             |
| Max per table   | 20                                              | 5                                  |
| Size constraint | None                                            | 10 GB per partition-key collection |
| Throttle impact | Under-provisioned GSI throttles **base writes** | Bounded by base capacity           |

> **Exam Tip:** Default to **GSI**; pick **LSI** only for strong-consistency alternate sort created with the table.

[⬆ Back to top](#table-of-contents)

---

## Consistency Models

| Model                     | Freshness              | Cost           | Notes                               |
| :------------------------ | :--------------------- | :------------- | :---------------------------------- |
| **Eventually consistent** | May be stale (default) | 0.5 RCU / 4 KB | Cheapest; GSI only supports this    |
| **Strongly consistent**   | Latest committed value | 1 RCU / 4 KB   | Base table & LSI only (**not GSI**) |
| **Transactional**         | ACID across items      | 2 RCU / 2 WCU  | All-or-nothing, single Region       |

> **Exam Tip:** **GSIs are eventually consistent only.** Cross-Region (Global Tables) is also eventually consistent (last-writer-wins).

[⬆ Back to top](#table-of-contents)

---

## Capacity Modes

|                  | **On-Demand**       | **Provisioned**                       |
| :--------------- | :------------------ | :------------------------------------ |
| Specify capacity | No                  | Yes (RCU/WCU)                         |
| Billing          | Per request         | Per provisioned hour                  |
| Best for         | Spiky / unknown     | Steady / predictable                  |
| Scaling          | Automatic / instant | Manual or **Auto Scaling** (reactive) |
| Throttling       | Minimal             | If exceeded (minus burst/adaptive)    |
| Cost at scale    | Higher per unit     | Cheaper                               |
| Idle cost        | Near zero           | Pay for provisioned capacity          |

> **Exam Tip:** Unpredictable -> **On-Demand**. Steady + cost-sensitive -> **Provisioned + Auto Scaling**. Switch limited to once / 24h.

[⬆ Back to top](#table-of-contents)

---

## Streams, TTL, and PITR Facts

| Feature                               | Key facts                                                                                                                                          |
| :------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Streams**                           | CDC log, **24h** retention, ordered per partition key, views KEYS_ONLY/NEW/OLD/NEW_AND_OLD; consumed by **Lambda**; required for **Global Tables** |
| **Kinesis Data Streams for DynamoDB** | Alternative CDC with up to **1 year** retention, higher fan-out                                                                                    |
| **TTL**                               | Auto-delete by epoch-seconds attribute; **free** (no WCU); eventual (within ~48h); deletions appear in Streams                                     |
| **PITR**                              | Continuous backup, restore to any second in **35 days**; restore creates a **new table**                                                           |
| **On-demand backups**                 | Full snapshots, retained until deleted; integrates with **AWS Backup**                                                                             |
| **Export to S3**                      | No RCU consumed, no performance impact; query with **Athena**                                                                                      |

> **Exam Tip:** TTL + Streams + Lambda + S3 = archive-on-expiry pattern. PITR = **35 days**; Streams = **24 hours**.

[⬆ Back to top](#table-of-contents)

---

## DAX vs ElastiCache

|             | **DAX**                            | **ElastiCache**                            |
| :---------- | :--------------------------------- | :----------------------------------------- |
| Purpose     | DynamoDB-specific cache            | General-purpose in-memory cache            |
| Latency     | **Microseconds**                   | **Microseconds / sub-ms**                  |
| Caches      | Item cache + query cache           | Anything (app-managed)                     |
| Write model | **Write-through** (DynamoDB-aware) | App manages population/invalidation        |
| Code change | Minimal (API-compatible)           | More (cache-aside logic)                   |
| Consistency | Eventually consistent reads        | App-defined                                |
| Use when    | DynamoDB read-heavy microsecond    | Sessions, leaderboards, pub/sub, any store |

> **Exam Tip:** "DynamoDB + microsecond reads + minimal change" -> **DAX**. General caching / session store / leaderboard -> **ElastiCache** (see [01 - ElastiCache Intro & Core Concepts](01%20-%20ElastiCache%20Intro%20%26%20Core%20Concepts.md)).

[⬆ Back to top](#table-of-contents)

---

## Rapid-Fire Facts

1. DynamoDB is **serverless, fully managed NoSQL** (key-value + document).
2. Latency: **single-digit-ms**; **microseconds** with DAX.
3. Data replicated across **3 AZs** automatically within a Region.
4. **Encryption at rest is always on** (cannot disable); only key type is configurable.
5. Primary key = **partition (hash)** or **partition + sort (composite)**.
6. Partition key is **hashed** to choose the partition.
7. Sort key enables **range queries** (begins_with, between, >, <).
8. Max item size = **400 KB**; large objects -> **S3 + pointer**.
9. Per-partition cap = **3000 RCU / 1000 WCU / 10 GB**.
10. **1 RCU** = 1 strong read of 4 KB/s = **2** eventual; **1 WCU** = 1 write of 1 KB/s.
11. Transactions cost **2x** RCU/WCU.
12. **Eventually consistent** is the default read mode.
13. **GSI** = different PK, own capacity, **eventually consistent**, add anytime (20 max).
14. **LSI** = same PK + alt sort key, **create-time only**, strong-consistency option (5 max).
15. Under-provisioned **GSI throttles base-table writes**.
16. **Streams** = 24h CDC -> Lambda triggers.
17. **TTL** auto-expires items, **no WCU**, eventual (~48h).
18. **DAX** = write-through microsecond read cache (item + query).
19. **Global Tables** = multi-Region **multi-active**, **last-writer-wins**, eventually consistent.
20. **PITR** = restore to any second in **35 days** (new table).
21. **On-demand backups** for long-term retention; integrate with **AWS Backup**.
22. **Export to S3** consumes **no RCU**; query with **Athena**.
23. **On-Demand** for spiky/unknown; **Provisioned + Auto Scaling** for steady.
24. Auto Scaling is **reactive**; burst capacity covers ~**300s** of unused throughput.
25. **Adaptive capacity** auto-rebalances throughput to hot partitions (cannot exceed per-partition cap).
26. **Query** is efficient; **Scan** reads the whole table - avoid for cost.
27. `ProvisionedThroughputExceededException` = under-provisioned or **hot partition**.
28. Fine-grained access via **`dynamodb:LeadingKeys`** (per-user row access).
29. **Standard-IA table class** lowers storage cost for infrequently accessed data.
30. DynamoDB is **regional**; cross-Region needs **Global Tables**.

> **Exam Tip:** If you remember only five things: **400 KB item**, **3000/1000 per partition**, **GSI = eventual / different PK / add anytime**, **LSI = strong / same PK / create-time only**, **DAX for microsecond DynamoDB reads**.

[⬆ Back to top](#table-of-contents)

---

## Summary: Key Takeaways for SAA-C03

- Know the **RCU/WCU math** cold (eventual = half, transactional = double).
- Memorize **hard limits**: 400 KB item, 3000 RCU/1000 WCU/10 GB per partition, 5 LSIs, 20 GSIs, 24h Streams, 35-day PITR.
- **GSI vs LSI** and **consistency** tables are the highest-yield comparisons.
- **On-Demand vs Provisioned** maps to spiky vs steady traffic.
- **Streams/TTL/PITR/Export-to-S3** cover the event-driven, lifecycle, and analytics patterns.
- **DAX vs ElastiCache**: DAX for DynamoDB microsecond reads, ElastiCache for general caching.

[⬆ Back to top](#table-of-contents)
