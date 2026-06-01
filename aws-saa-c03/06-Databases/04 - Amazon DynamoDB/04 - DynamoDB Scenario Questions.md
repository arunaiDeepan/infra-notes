# DynamoDB Scenario Questions - SAA-C03 Deep Dive

> Ten exam-style scenarios with answers and explanations, drilling the highest-yield DynamoDB decisions: serverless key-value at scale, DAX vs ElastiCache, Global Tables, GSI, Streams + Lambda, TTL, on-demand mode, fixing throughput throttling, consistency choices, and ACID transactions.

See also: [01 - DynamoDB Intro & Core Concepts](01%20-%20DynamoDB%20Intro%20%26%20Core%20Concepts.md) · [02 - DynamoDB Architecture Deep Dive](02%20-%20DynamoDB%20Architecture%20Deep%20Dive.md) · [03 - DynamoDB Best Practices & Examples](03%20-%20DynamoDB%20Best%20Practices%20%26%20Examples.md) · [05 - DynamoDB Troubleshooting (SRE)](05%20-%20DynamoDB%20Troubleshooting%20%28SRE%29.md) · [06 - DynamoDB Important Facts & Cheat Sheet](06%20-%20DynamoDB%20Important%20Facts%20%26%20Cheat%20Sheet.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md) · [01 - ElastiCache Intro & Core Concepts](01%20-%20ElastiCache%20Intro%20%26%20Core%20Concepts.md)

---

## Table of Contents

- [Scenario 1: Massive-Scale Serverless Key-Value](#scenario-1-massive-scale-serverless-key-value)
- [Scenario 2: Microsecond Reads](#scenario-2-microsecond-reads)
- [Scenario 3: Multi-Region Active-Active](#scenario-3-multi-region-active-active)
- [Scenario 4: Query by a Non-Key Attribute](#scenario-4-query-by-a-non-key-attribute)
- [Scenario 5: Trigger on Item Change (CDC)](#scenario-5-trigger-on-item-change-cdc)
- [Scenario 6: Auto-Expire Session Data](#scenario-6-auto-expire-session-data)
- [Scenario 7: Spiky Unpredictable Traffic](#scenario-7-spiky-unpredictable-traffic)
- [Scenario 8: ProvisionedThroughputExceeded Fix](#scenario-8-provisionedthroughputexceeded-fix)
- [Scenario 9: Strongly vs Eventually Consistent](#scenario-9-strongly-vs-eventually-consistent)
- [Scenario 10: ACID Requirements](#scenario-10-acid-requirements)
- [Summary: Key Takeaways for SAA-C03](#summary-key-takeaways-for-saa-c03)

---

## Scenario 1: Massive-Scale Serverless Key-Value

**Scenario:** A gaming startup needs a database for player profiles and game state. Traffic could grow to millions of requests per second, the team is tiny, and they want zero server management with consistent low-latency lookups by player ID.

**Answer:** **Amazon DynamoDB** with `PlayerId` as the partition key.

**Why:** DynamoDB is **serverless, fully managed**, scales horizontally to millions of req/sec, and gives **single-digit-ms** key-value lookups. RDS/Aurora would require capacity management and do not scale as cleanly for simple key-value access.

> **Exam Tip:** "Serverless NoSQL", "key-value", "millions of requests", "no server management", "single-digit-ms" -> **DynamoDB**.

[⬆ Back to top](#table-of-contents)

---

## Scenario 2: Microsecond Reads

**Scenario:** A DynamoDB-backed product catalog is read-heavy; the same hot items are read constantly. Latency must drop from single-digit-ms to **microseconds** with minimal code change.

**Answer:** Add **DynamoDB Accelerator (DAX)** in front of the table.

**Why:** DAX is a DynamoDB-aware, write-through **in-memory cache** delivering **microsecond** reads, API-compatible (minimal code change). **ElastiCache** is a distractor - it works but requires app-managed cache logic and is the answer for general caching, not DynamoDB-specific microsecond reads.

> **Exam Tip:** "DynamoDB + microseconds + read-heavy" -> **DAX**, not ElastiCache.

[⬆ Back to top](#table-of-contents)

---

## Scenario 3: Multi-Region Active-Active

**Scenario:** A global app needs users in the US, Europe, and Asia to read and write with **local low latency**, and the database must survive a full Region outage.

**Answer:** **DynamoDB Global Tables**.

**Why:** Global Tables provide **multi-Region, multi-active** replication - every Region accepts reads and writes locally, with automatic cross-Region replication and DR. Conflicts use **last-writer-wins**.

> **Exam Tip:** "Active-active multi-Region, local low latency, survive Region failure" -> **Global Tables**. Not RDS read replicas (single-writer) and not a single-Region table.

[⬆ Back to top](#table-of-contents)

---

## Scenario 4: Query by a Non-Key Attribute

**Scenario:** A users table has `UserId` as the partition key, but the app must also look up users by **email address** efficiently. Scans are too slow and costly.

**Answer:** Create a **Global Secondary Index (GSI)** with `Email` as the partition key.

**Why:** A **GSI** allows queries on a **different attribute** with its own capacity. It can be **added after table creation**. An LSI cannot - it must use the same PK and be created with the table.

> **Exam Tip:** "Query/efficiently look up by an attribute that is not the primary key" -> **GSI**. Avoid the Scan distractor.

[⬆ Back to top](#table-of-contents)

---

## Scenario 5: Trigger on Item Change (CDC)

**Scenario:** Whenever a new order is inserted into a DynamoDB table, the system must send a confirmation email and index the order in a search service - in near real time.

**Answer:** Enable **DynamoDB Streams** and attach an **AWS Lambda** trigger.

**Why:** Streams capture item-level changes (24h retention); Lambda reacts to each change to call SES and OpenSearch. This is the canonical **event-driven / CDC** pattern.

> **Exam Tip:** "Trigger/react when an item is created/updated/deleted" -> **Streams + Lambda**.

[⬆ Back to top](#table-of-contents)

---

## Scenario 6: Auto-Expire Session Data

**Scenario:** A web app stores user **session data** in DynamoDB. Sessions should be automatically removed 30 minutes after creation with no extra write cost and no cleanup job.

**Answer:** Enable **TTL** on a `ExpiresAt` attribute (Unix epoch seconds).

**Why:** **TTL** deletes expired items automatically in the background, **consuming no WCU** and requiring no cron/cleanup code. Deletion is eventual (within ~48h of expiry).

> **Exam Tip:** "Automatically expire/clean up session or temporary data at no extra cost" -> **TTL**.

[⬆ Back to top](#table-of-contents)

---

## Scenario 7: Spiky Unpredictable Traffic

**Scenario:** A new marketing app launches with **unknown, highly unpredictable** traffic - occasional viral spikes followed by quiet periods. The team cannot forecast capacity and must avoid throttling.

**Answer:** Use **On-Demand** capacity mode.

**Why:** On-Demand scales instantly with no capacity planning and charges per request - ideal for **unpredictable/spiky** workloads. Provisioned + Auto Scaling reacts too slowly for sudden viral spikes.

> **Exam Tip:** "Unpredictable / spiky / unknown traffic" -> **On-Demand**.

[⬆ Back to top](#table-of-contents)

---

## Scenario 8: ProvisionedThroughputExceeded Fix

**Scenario:** A provisioned table intermittently returns **ProvisionedThroughputExceededException** during traffic bursts, even though average utilization is moderate. The partition key is `userId`.

**Answer:** Enable **Auto Scaling** (or switch to **On-Demand**); if a single key is hot, **redesign the key / write-shard**.

**Why:** Throttling on a moderately utilized table usually means **bursts exceed provisioned capacity** or a **hot partition** concentrates load. Auto Scaling/On-Demand handle bursts; adaptive capacity helps but cannot exceed **3000 RCU/1000 WCU per partition** - so a single hot key needs **sharding**. Adding exponential-backoff retries in the SDK also mitigates transient throttles.

> **Exam Tip:** Throttling = under-provisioned **or** hot partition. Fix: On-Demand / Auto Scaling for capacity, key redesign / sharding for hot partitions, SDK retries with backoff for transients.

[⬆ Back to top](#table-of-contents)

---

## Scenario 9: Strongly vs Eventually Consistent

**Scenario:** After writing a new value, the application **immediately** reads it back and must always see the just-written data. Reads currently sometimes return stale values.

**Answer:** Use a **strongly consistent read** (`ConsistentRead=true`).

**Why:** The default is **eventually consistent**, which can return stale data right after a write. Strong consistency reads the leader replica and reflects all prior writes - at **2x the RCU cost** of eventual. Note: a **GSI cannot serve strongly consistent reads**, so read from the base table or use an LSI.

> **Exam Tip:** "Must read the value just written / read-after-write" -> **strongly consistent read**. If they want it on a GSI -> impossible; use base table or LSI.

[⬆ Back to top](#table-of-contents)

---

## Scenario 10: ACID Requirements

**Scenario:** An e-commerce checkout must **atomically** debit inventory and create an order record - if either fails, neither should apply.

**Answer:** Use **DynamoDB transactions** (`TransactWriteItems`).

**Why:** Transactions give **ACID, all-or-nothing** guarantees across multiple items/tables in one Region. Both writes commit together or roll back. They cost **2x** the normal WCU.

> **Exam Tip:** "Atomic / all-or-nothing across multiple items or tables" -> **DynamoDB transactions** (single-Region, 2x cost).

[⬆ Back to top](#table-of-contents)

---

## Summary: Key Takeaways for SAA-C03

- Serverless key-value at massive scale -> **DynamoDB**.
- Microsecond DynamoDB reads -> **DAX** (not ElastiCache).
- Multi-Region active-active -> **Global Tables** (last-writer-wins).
- Query by non-key attribute -> **GSI** (add anytime; eventually consistent).
- React to item changes -> **Streams + Lambda**.
- Auto-expire data -> **TTL** (free, eventual).
- Spiky/unknown traffic -> **On-Demand**.
- Throttling -> capacity (On-Demand/Auto Scaling) or hot-key redesign + sharding + SDK backoff.
- Read-after-write -> **strongly consistent read** (not available on GSIs).
- Atomic multi-item -> **transactions** (2x cost, single-Region).

[⬆ Back to top](#table-of-contents)
