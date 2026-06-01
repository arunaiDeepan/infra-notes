# ElastiCache Scenario Questions - SAA-C03 Deep Dive

> Ten exam-style scenarios covering offloading RDS reads, externalised sessions, leaderboards, Memcached vs Redis selection, Multi-AZ HA + persistence, cross-Region reads with Global Datastore, the DAX-vs-ElastiCache trap for DynamoDB, and choosing a caching strategy — each with the correct answer and why the distractors fail.

See also: [01 - ElastiCache Intro & Core Concepts](01%20-%20ElastiCache%20Intro%20%26%20Core%20Concepts.md) · [02 - ElastiCache Architecture Deep Dive](02%20-%20ElastiCache%20Architecture%20Deep%20Dive.md) · [03 - ElastiCache Best Practices & Examples](03%20-%20ElastiCache%20Best%20Practices%20%26%20Examples.md) · [05 - ElastiCache Troubleshooting (SRE)](05%20-%20ElastiCache%20Troubleshooting%20%28SRE%29.md) · [06 - ElastiCache Important Facts & Cheat Sheet](06%20-%20ElastiCache%20Important%20Facts%20%26%20Cheat%20Sheet.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md) · [01 - DynamoDB Intro & Core Concepts](01%20-%20DynamoDB%20Intro%20%26%20Core%20Concepts.md)

---

## Table of Contents

- [Q1 Reduce Read Load on RDS](#q1-reduce-read-load-on-rds)
- [Q2 Session Store for a Stateless Web Tier](#q2-session-store-for-a-stateless-web-tier)
- [Q3 Real-Time Leaderboard](#q3-real-time-leaderboard)
- [Q4 Simple Horizontal Object Cache No HA](#q4-simple-horizontal-object-cache-no-ha)
- [Q5 HA Cache with Failover and Persistence](#q5-ha-cache-with-failover-and-persistence)
- [Q6 Cross-Region Low-Latency Reads](#q6-cross-region-low-latency-reads)
- [Q7 DynamoDB Microsecond Reads Trap](#q7-dynamodb-microsecond-reads-trap)
- [Q8 Choosing a Caching Strategy](#q8-choosing-a-caching-strategy)
- [Q9 Cache Rejecting Writes When Full](#q9-cache-rejecting-writes-when-full)
- [Q10 Spiky Unpredictable Cache Traffic](#q10-spiky-unpredictable-cache-traffic)

---

## Q1 Reduce Read Load on RDS

**Scenario:** A read-heavy product-catalog app sends the same `SELECT` queries to its RDS MySQL primary repeatedly. CPU is high and latency is rising. Reduce DB load with minimal app changes.

- A. Vertically scale the RDS instance to a larger class
- B. Add an **ElastiCache** layer and cache query results (lazy loading + TTL) ✅
- C. Migrate to DynamoDB
- D. Enable RDS storage autoscaling

**Answer: B.** An in-memory cache serves repeated reads from RAM, dramatically cutting RDS CPU/IOPS. Scaling up (A) is costly and temporary; DynamoDB (C) is a rewrite; storage autoscaling (D) addresses disk space, not read load.

> [!tip] Exam Tip
> "Same reads hitting RDS repeatedly, high DB CPU" → **ElastiCache** in front of the DB. Read replicas also help but the cache gives **microsecond** latency and the biggest offload for hot data.

[⬆ Back to top](#table-of-contents)

---

## Q2 Session Store for a Stateless Web Tier

**Scenario:** Web servers run behind an ALB in an Auto Scaling group. When instances scale in, users lose their sessions. You want a stateless web tier.

- A. Enable ALB sticky sessions
- B. Store sessions in **ElastiCache for Redis** ✅
- C. Store sessions on each instance's local disk
- D. Use a larger instance type

**Answer: B.** Externalising session state to Redis (replicated, Multi-AZ) lets any instance serve any user and survives scale-in/instance loss. Sticky sessions (A) reduce balancing flexibility and still lose state when the pinned instance dies; local disk (C) is the root cause; (D) is irrelevant.

> [!tip] Exam Tip
> Stateless tier + shared, durable session state → **ElastiCache for Redis**. Memcached could hold sessions but offers no replication/failover.

[⬆ Back to top](#table-of-contents)

---

## Q3 Real-Time Leaderboard

**Scenario:** A mobile game needs a real-time global leaderboard updated thousands of times per second, returning top-N players and a user's rank instantly.

- A. RDS with `ORDER BY score LIMIT 10` per request
- B. DynamoDB scan sorted in the app
- C. **ElastiCache for Redis sorted sets (ZSET)** ✅
- D. Athena queries over S3

**Answer: C.** Redis sorted sets maintain order by score with O(log N) updates and instant rank/top-N reads. Relational `ORDER BY` (A) and DynamoDB scans (B) do not scale to this rate; Athena (D) is for analytics, not real-time.

> [!tip] Exam Tip
> "Real-time ranking / leaderboard" → **Redis sorted sets**. Reliable keyword.

[⬆ Back to top](#table-of-contents)

---

## Q4 Simple Horizontal Object Cache No HA

**Scenario:** A stateless service needs a **simple key/value object cache** that scales **horizontally** across many cores, where cached data loss is fully acceptable and **no failover/persistence is required**. Lowest complexity wanted.

- A. ElastiCache for Redis cluster mode enabled
- B. **ElastiCache for Memcached** ✅
- C. DynamoDB
- D. ElastiCache Global Datastore

**Answer: B.** Memcached is multi-threaded (uses all cores), scales out by adding nodes, and is the simplest fit when persistence/HA are not needed. Redis (A) adds unneeded features; (C) is a database; (D) is cross-Region Redis.

> [!tip] Exam Tip
> "Simple, multi-threaded, scale out, no persistence/HA needed" → **Memcached**. Any HA/persistence requirement flips the answer to **Redis/Valkey**.

[⬆ Back to top](#table-of-contents)

---

## Q5 HA Cache with Failover and Persistence

**Scenario:** A cache must survive an **Availability Zone failure** with **automatic failover** and must support **backups/restore** of its data.

- A. Memcached with multiple nodes
- B. **ElastiCache for Redis with Multi-AZ + automatic failover and snapshots** ✅
- C. Single-node Redis
- D. Memcached with Auto Discovery

**Answer: B.** Only Redis/Valkey provides replication, Multi-AZ automatic failover, and snapshots. Memcached (A, D) has none of these; single-node Redis (C) lacks failover (no replica).

> [!tip] Exam Tip
> "Cache + AZ resilience + automatic failover + backups" → **Redis Multi-AZ with replicas + snapshots**. Multi-AZ requires **≥1 read replica**.

[⬆ Back to top](#table-of-contents)

---

## Q6 Cross-Region Low-Latency Reads

**Scenario:** A global app caches data in us-east-1 but European users see high cache-read latency. You need **low-latency local reads** in Europe with managed cross-Region replication and the option of regional DR.

- A. Read replica of RDS in eu-west-1
- B. **ElastiCache Redis Global Datastore with a secondary cluster in eu-west-1** ✅
- C. CloudFront in front of the cache
- D. Memcached cluster in eu-west-1

**Answer: B.** Global Datastore replicates a Redis/Valkey cluster cross-Region (sub-second lag) for local reads and lets you promote a secondary for DR. RDS replicas (A) do not provide microsecond cache reads; CloudFront (C) caches HTTP, not arbitrary cache keys; Memcached (D) cannot replicate cross-Region.

> [!tip] Exam Tip
> "Cross-Region low-latency cache reads / cache-layer DR" → **ElastiCache Global Datastore** (Redis/Valkey only).

[⬆ Back to top](#table-of-contents)

---

## Q7 DynamoDB Microsecond Reads Trap

**Scenario:** A **DynamoDB**-backed app needs **microsecond** read latency for an eventually-consistent, read-heavy workload with the **least** application change.

- A. ElastiCache for Redis in front of DynamoDB
- B. **DynamoDB Accelerator (DAX)** ✅
- C. ElastiCache for Memcached in front of DynamoDB
- D. Global Datastore

**Answer: B.** **DAX** is the purpose-built, DynamoDB-API-compatible, in-memory cache delivering microsecond reads with essentially **no app changes** (it sits transparently in front of DynamoDB). ElastiCache (A, C) would require you to build cache-aside logic yourself; (D) is unrelated.

> [!tip] Exam Tip
> **DynamoDB + microsecond reads + minimal code change → DAX, not ElastiCache.** This is the classic trap. ElastiCache caches DynamoDB only if you write your own cache-aside layer.

[⬆ Back to top](#table-of-contents)

---

## Q8 Choosing a Caching Strategy

**Scenario:** A reporting cache shows **stale numbers** for up to an hour after the source DB updates. Reads vastly outnumber writes. Fix staleness with minimal write overhead.

- A. Switch to write-through on every read
- B. **Add/lower a TTL on cached keys (lazy loading + TTL)**, optionally invalidate on write ✅
- C. Disable caching entirely
- D. Move to Memcached

**Answer: B.** A shorter **TTL** bounds how stale data can be while keeping the simple lazy-loading model; invalidating the key on write makes it immediate. Write-through (A) adds write cost and still needs TTL for cold data; disabling (C) defeats the purpose; engine swap (D) is irrelevant.

> [!tip] Exam Tip
> "Stale cached data" → **TTL** (lower it) and/or **invalidate on write**. For always-fresh-after-write → **write-through**.

[⬆ Back to top](#table-of-contents)

---

## Q9 Cache Rejecting Writes When Full

**Scenario:** A Redis cache has filled memory and is now **returning errors on new writes** (OOM). It should instead evict old data to make room.

- A. Set `maxmemory-policy` to **`noeviction`**
- B. Set `maxmemory-policy` to **`allkeys-lru`** (and/or scale the node / add a shard) ✅
- C. Disable backups
- D. Lower the number of replicas

**Answer: B.** `noeviction` is exactly what causes write errors when full; switching to an LRU/LFU `allkeys-*` policy lets Redis evict stale keys. Scaling up or sharding adds capacity. (C) and (D) do not address memory pressure.

> [!tip] Exam Tip
> Write errors on a full cache = `noeviction`. For a cache, use **`allkeys-lru`/`allkeys-lfu`**, and watch the **`Evictions`** metric.

[⬆ Back to top](#table-of-contents)

---

## Q10 Spiky Unpredictable Cache Traffic

**Scenario:** A new app has **unpredictable, spiky** cache traffic. The team wants high availability with **zero capacity planning** and pay-for-use pricing.

- A. Over-provision a large fixed Redis cluster
- B. **ElastiCache Serverless** ✅
- C. Single-node Memcached
- D. Schedule manual scaling

**Answer: B.** ElastiCache Serverless scales compute/memory automatically in seconds, is multi-AZ HA by default, and bills per use — ideal for spiky/unknown load. Over-provisioning (A) wastes money; single node (C) is neither HA nor elastic; manual scheduling (D) cannot track unpredictable spikes.

> [!tip] Exam Tip
> "Unpredictable/spiky load + no capacity management + HA by default" → **ElastiCache Serverless**.

[⬆ Back to top](#table-of-contents)
