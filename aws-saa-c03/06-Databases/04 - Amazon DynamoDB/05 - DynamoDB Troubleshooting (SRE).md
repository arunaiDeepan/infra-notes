# DynamoDB Troubleshooting (SRE) - SAA-C03 Deep Dive

> An SRE-style runbook for DynamoDB problems: throttling and ProvisionedThroughputExceededException, hot-partition diagnosis, adaptive capacity, GSI throttling backpressure, scan cost/latency, the 400 KB item limit, Streams iterator-age / Lambda lag, DAX cache staleness, and Global Tables conflict resolution. Each issue is framed as symptom -> CloudWatch metric -> root cause -> fix -> prevention.

See also: [01 - DynamoDB Intro & Core Concepts](01%20-%20DynamoDB%20Intro%20%26%20Core%20Concepts.md) · [02 - DynamoDB Architecture Deep Dive](02%20-%20DynamoDB%20Architecture%20Deep%20Dive.md) · [03 - DynamoDB Best Practices & Examples](03%20-%20DynamoDB%20Best%20Practices%20%26%20Examples.md) · [04 - DynamoDB Scenario Questions](04%20-%20DynamoDB%20Scenario%20Questions.md) · [06 - DynamoDB Important Facts & Cheat Sheet](06%20-%20DynamoDB%20Important%20Facts%20%26%20Cheat%20Sheet.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md) · [01 - ElastiCache Intro & Core Concepts](01%20-%20ElastiCache%20Intro%20%26%20Core%20Concepts.md)

---

## Table of Contents

- [Throttling and ProvisionedThroughputExceededException](#throttling-and-provisionedthroughputexceededexception)
- [Hot-Partition Diagnosis](#hot-partition-diagnosis)
- [Adaptive Capacity](#adaptive-capacity)
- [GSI Throttling Backpressure](#gsi-throttling-backpressure)
- [Scan Cost and Latency](#scan-cost-and-latency)
- [Large Item Limit (400 KB)](#large-item-limit-400-kb)
- [Streams Iterator Age and Lambda Lag](#streams-iterator-age-and-lambda-lag)
- [DAX Cache Staleness](#dax-cache-staleness)
- [Global Tables Conflict Resolution](#global-tables-conflict-resolution)
- [Summary: Key Takeaways for SAA-C03](#summary-key-takeaways-for-saa-c03)

---

## Throttling and ProvisionedThroughputExceededException

| Step                  | Detail                                                                                                                                               |
| :-------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Symptom**           | `ProvisionedThroughputExceededException`; elevated latency; 400 errors; dropped requests                                                             |
| **CloudWatch metric** | `ReadThrottleEvents`, `WriteThrottleEvents`, `ThrottledRequests`; compare `ConsumedRead/WriteCapacityUnits` vs `ProvisionedRead/WriteCapacityUnits`  |
| **Root cause**        | Sustained demand exceeds provisioned capacity, or a burst outruns burst/adaptive capacity, or a single hot partition                                 |
| **Fix**               | Raise provisioned RCU/WCU; enable **Auto Scaling**; switch to **On-Demand**; add **SDK exponential-backoff retries**; for a hot key, **write-shard** |
| **Prevention**        | Right-size with Auto Scaling target utilization (~70%); use On-Demand for spiky traffic; design high-cardinality keys                                |

> **Exam Tip:** The SDKs retry throttled requests automatically with exponential backoff. Persistent throttling means **capacity** (raise/auto-scale/On-Demand) or **hot partition** (redesign key).

[⬆ Back to top](#table-of-contents)

---

## Hot-Partition Diagnosis

| Step                  | Detail                                                                                                                                                 |
| :-------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Symptom**           | Throttling despite total consumed capacity well below provisioned                                                                                      |
| **CloudWatch metric** | Throttle events present while aggregate `ConsumedCapacity` is low; use **CloudWatch Contributor Insights for DynamoDB** to find the most-accessed keys |
| **Root cause**        | One/few partition-key values absorb disproportionate traffic (low-cardinality key, or a celebrity/viral key)                                           |
| **Fix**               | **Write-shard** the hot key (suffix `#0..#N`); raise cardinality (composite key); cache hot reads with **DAX**                                         |
| **Prevention**        | Choose **high-cardinality** partition keys; avoid `status`/`date`/boolean keys                                                                         |

> **Exam Tip:** "Throttling but plenty of unused capacity" = **hot partition**. Per-partition ceiling is **3000 RCU / 1000 WCU**; no amount of total provisioning fixes a single overloaded key - shard it.

[⬆ Back to top](#table-of-contents)

---

## Adaptive Capacity

| Step                  | Detail                                                                                                              |
| :-------------------- | :------------------------------------------------------------------------------------------------------------------ |
| **Symptom**           | Occasional brief throttles during uneven access, mostly self-healing                                                |
| **CloudWatch metric** | Transient `ThrottledRequests` that subside as throughput is reallocated                                             |
| **Root cause**        | Uneven key access; adaptive capacity is rebalancing throughput toward the hot partition                             |
| **Fix**               | Usually automatic - adaptive capacity moves unused throughput to hot partitions instantly and bursts up to **300s** |
| **Prevention**        | Still design good keys; adaptive capacity **cannot exceed the 3000 RCU/1000 WCU per-partition limit**               |

> **Exam Tip:** Adaptive capacity is automatic, free, and instant - but it is a safety net, **not** a license to use bad partition keys.

[⬆ Back to top](#table-of-contents)

---

## GSI Throttling Backpressure

| Step                  | Detail                                                                                                                                |
| :-------------------- | :------------------------------------------------------------------------------------------------------------------------------------ |
| **Symptom**           | Base-table **writes** throttle/fail even though base capacity is sufficient                                                           |
| **CloudWatch metric** | `WriteThrottleEvents` on the **GSI** dimension; `OnlineIndexConsumedWriteCapacity`                                                    |
| **Root cause**        | The GSI is **under-provisioned**; in provisioned mode a GSI that cannot keep up applies **backpressure to base-table writes**         |
| **Fix**               | Increase the **GSI's** WCU (or enable Auto Scaling on the GSI; or use On-Demand); reduce projected attributes to lower GSI write cost |
| **Prevention**        | Provision GSIs at least as generously as the base table for the projected workload; project only needed attributes                    |

> **Exam Tip:** An **under-provisioned GSI throttles base-table writes**. This is a favorite trap - always scale GSIs alongside the base table.

[⬆ Back to top](#table-of-contents)

---

## Scan Cost and Latency

| Step                  | Detail                                                                                                                                                          |
| :-------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Symptom**           | High latency and high RCU spend on read-heavy reporting/list operations                                                                                         |
| **CloudWatch metric** | Spikes in `ConsumedReadCapacityUnits`; `ScannedCount` >> `Count` (filtering reads far more than it returns)                                                     |
| **Root cause**        | **Scan** reads the entire table and filters client-side - you pay RCU for every item read, even filtered-out ones                                               |
| **Fix**               | Replace Scan with **Query** (add a **GSI** to enable it); for analytics use **Export to S3 + Athena**; use **parallel scan** + `Limit` if a scan is unavoidable |
| **Prevention**        | Design access patterns with indexes so scans are never needed in hot paths                                                                                      |

> **Exam Tip:** A large gap between `ScannedCount` and `Count` signals wasteful scanning. The cost fix is **Query/GSI** or **Export to S3 + Athena**, never "scan faster".

[⬆ Back to top](#table-of-contents)

---

## Large Item Limit (400 KB)

| Step                  | Detail                                                                                                                             |
| :-------------------- | :--------------------------------------------------------------------------------------------------------------------------------- |
| **Symptom**           | `ValidationException: Item size has exceeded the maximum allowed size`; failed PutItem                                             |
| **CloudWatch metric** | Application-level write errors (not a dedicated metric)                                                                            |
| **Root cause**        | Item (all attributes combined) exceeds the **400 KB** hard limit                                                                   |
| **Fix**               | Store the large payload in **S3**, keep the **S3 key/pointer** in DynamoDB; split the item; compress; or use vertical partitioning |
| **Prevention**        | Keep items small; never store blobs/media inline                                                                                   |

> **Exam Tip:** **400 KB max item size.** Large objects -> S3 + pointer in DynamoDB. This appears in both troubleshooting and design questions.

[⬆ Back to top](#table-of-contents)

---

## Streams Iterator Age and Lambda Lag

| Step                  | Detail                                                                                                                                                                    |
| :-------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Symptom**           | Downstream processing lags behind writes; events processed late; risk of loss past 24h retention                                                                          |
| **CloudWatch metric** | **`IteratorAge`** rising on the Streams/Lambda event source; Lambda `Errors`/`Throttles`, growing `Duration`                                                              |
| **Root cause**        | Lambda cannot keep up (slow code, downstream throttling, errors causing retries that block the shard)                                                                     |
| **Fix**               | Optimize/parallelize Lambda; raise **parallelization factor** and reserved concurrency; tune batch size/window; add a **DLQ / on-failure destination** for poison records |
| **Prevention**        | Make consumers **idempotent** (at-least-once delivery); alarm on `IteratorAge`; process within the **24h** retention window                                               |

> **Exam Tip:** **Rising `IteratorAge`** = consumer falling behind. A poison record can block an ordered shard - use a **DLQ/bisect-on-error** and idempotent handlers.

[⬆ Back to top](#table-of-contents)

---

## DAX Cache Staleness

| Step                  | Detail                                                                                                                                                                                 |
| :-------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Symptom**           | Reads via DAX return stale values after an update                                                                                                                                      |
| **CloudWatch metric** | DAX `ItemCacheHits/Misses`, `QueryCacheHits/Misses`; compare with direct-table reads                                                                                                   |
| **Root cause**        | Item/query cache TTL not yet expired, or data was written **directly to DynamoDB bypassing DAX** (so DAX's write-through never updated the cache)                                      |
| **Fix**               | Route writes **through DAX** (write-through); lower cache TTL; for must-be-fresh reads, read the **base table with strong consistency** (DAX does not serve strongly consistent reads) |
| **Prevention**        | Keep all writes on the DAX path; reserve DAX for data that tolerates slight staleness                                                                                                  |

> **Exam Tip:** DAX serves **eventually consistent** cached reads. If a write bypasses DAX or you need read-after-write, go to the **table with `ConsistentRead`**, not DAX.

[⬆ Back to top](#table-of-contents)

---

## Global Tables Conflict Resolution

| Step                  | Detail                                                                                                                                              |
| :-------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Symptom**           | An update made in one Region appears to be "lost" or overwritten by another Region's write                                                          |
| **CloudWatch metric** | `ReplicationLatency`, `PendingReplicationCount` per replica/Region                                                                                  |
| **Root cause**        | Concurrent writes to the **same item in different Regions**; Global Tables resolve via **last-writer-wins** (highest timestamp)                     |
| **Fix**               | Design to avoid same-item concurrent multi-Region writes (route a given entity to a home Region); accept LWW; use conditional writes where possible |
| **Prevention**        | Partition write ownership by Region/entity; monitor `ReplicationLatency`; understand cross-Region replication is **eventually consistent**          |

> **Exam Tip:** Global Tables = **last-writer-wins**, eventually consistent across Regions. There is **no cross-Region strong consistency** - flag any answer that claims otherwise.

[⬆ Back to top](#table-of-contents)

---

## Summary: Key Takeaways for SAA-C03

- **Throttling**: check `ReadThrottleEvents`/`WriteThrottleEvents`; fix with Auto Scaling / On-Demand / SDK backoff; if hot key, **shard**.
- **Hot partition**: throttling with low total consumption -> use **Contributor Insights**, shard the key; per-partition cap is **3000 RCU/1000 WCU**.
- **Adaptive capacity** auto-rebalances + bursts 300s but cannot exceed per-partition limits.
- **Under-provisioned GSI throttles base-table writes** - scale GSIs with the base table.
- **Scan**: `ScannedCount >> Count` = wasteful; use **Query/GSI** or **Export to S3 + Athena**.
- **400 KB** item limit -> store blobs in **S3 + pointer**.
- **Rising `IteratorAge`** = Streams consumer lag; idempotent Lambdas, DLQ, watch the 24h window.
- **DAX staleness** -> writes must go through DAX; read base table with strong consistency for fresh data.
- **Global Tables** -> last-writer-wins, eventually consistent; partition write ownership to avoid conflicts.

[⬆ Back to top](#table-of-contents)
