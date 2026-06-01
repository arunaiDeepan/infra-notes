# ElastiCache Important Facts & Cheat Sheet - SAA-C03 Deep Dive

> Rapid-fire revision: Redis/Valkey vs Memcached comparison, cluster-mode facts, Multi-AZ and Global Datastore facts, the caching-strategy table, eviction policies, key CloudWatch metrics, the critical DAX-vs-ElastiCache distinction, and 20+ exam facts.

See also: [01 - ElastiCache Intro & Core Concepts](01%20-%20ElastiCache%20Intro%20%26%20Core%20Concepts.md) · [02 - ElastiCache Architecture Deep Dive](02%20-%20ElastiCache%20Architecture%20Deep%20Dive.md) · [03 - ElastiCache Best Practices & Examples](03%20-%20ElastiCache%20Best%20Practices%20%26%20Examples.md) · [04 - ElastiCache Scenario Questions](04%20-%20ElastiCache%20Scenario%20Questions.md) · [05 - ElastiCache Troubleshooting (SRE)](05%20-%20ElastiCache%20Troubleshooting%20%28SRE%29.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md) · [01 - DynamoDB Intro & Core Concepts](01%20-%20DynamoDB%20Intro%20%26%20Core%20Concepts.md)

---

## Table of Contents

- [Redis vs Memcached Comparison](#redis-vs-memcached-comparison)
- [Cluster Mode Facts](#cluster-mode-facts)
- [Multi-AZ and Global Datastore Facts](#multi-az-and-global-datastore-facts)
- [Caching Strategy Table](#caching-strategy-table)
- [Eviction Policies](#eviction-policies)
- [Key Metrics](#key-metrics)
- [DAX vs ElastiCache for the Exam](#dax-vs-elasticache-for-the-exam)
- [Rapid-Fire Facts](#rapid-fire-facts)

---

## Redis vs Memcached Comparison

| Feature                         | Redis OSS / Valkey                                                   | Memcached                                  |
| :------------------------------ | :------------------------------------------------------------------- | :----------------------------------------- |
| Threading                       | Single-threaded per shard                                            | **Multi-threaded**                         |
| Data types                      | Strings, hashes, lists, sets, **sorted sets**, streams, geo, bitmaps | Simple key/value                           |
| Replication / read replicas     | Yes (up to 5/shard)                                                  | No                                         |
| Multi-AZ + auto failover        | Yes                                                                  | No                                         |
| Sharding                        | Built-in (cluster mode enabled)                                      | Client-side only                           |
| Persistence (RDB/AOF)           | Yes                                                                  | No                                         |
| Snapshots / backup / restore    | Yes (to S3)                                                          | No                                         |
| Cross-Region replication        | Yes (Global Datastore)                                               | No                                         |
| Pub/Sub, transactions, Lua      | Yes                                                                  | No                                         |
| Encryption in-transit / at-rest | Yes / Yes                                                            | Yes / Limited                              |
| AUTH / RBAC / IAM auth          | Yes                                                                  | Limited                                    |
| Best for                        | HA, durability, rich data, sessions, leaderboards                    | Simple, large, multi-threaded object cache |

> [!tip] Exam Tip
> Need **persistence, HA/failover, replication, cross-Region, or sorted sets/pub-sub** → **Redis/Valkey**. Need **simple + multi-threaded + scale-out + no HA** → **Memcached**.

[⬆ Back to top](#table-of-contents)

---

## Cluster Mode Facts

| Fact                 | Disabled         | Enabled                    |
| :------------------- | :--------------- | :------------------------- |
| Shards (node groups) | 1                | Up to 500                  |
| Replicas per shard   | 0–5              | 0–5                        |
| Sharding             | No               | Yes (16,384 hash slots)    |
| Endpoint             | Primary + reader | **Configuration endpoint** |
| Scale reads          | Add replicas     | Add replicas               |
| Scale writes/memory  | Scale up node    | **Add shards (scale out)** |
| Online resharding    | N/A              | Yes                        |

> [!tip] Exam Tip
> Big dataset / more write throughput → **cluster mode enabled**. More read throughput / simple HA → **cluster mode disabled + replicas + Multi-AZ**.

[⬆ Back to top](#table-of-contents)

---

## Multi-AZ and Global Datastore Facts

- **Multi-AZ** needs **≥1 read replica** in another AZ; enables **automatic failover** in seconds to ~1 minute.
- Failover updates the **primary endpoint DNS** — clients reconnect; endpoint name is unchanged.
- Replicas are **asynchronous** → possible slight read staleness.
- **Global Datastore** = cross-Region Redis/Valkey replication: **1 primary Region (read/write)** + up to **2 secondary Regions (read-only)**, **sub-second** lag, promote a secondary for DR.
- Memcached: **none** of the above (no replication/failover/cross-Region).

> [!tip] Exam Tip
> Cross-Region cache reads or cache-layer DR → **Global Datastore**. AZ resilience within a Region → **Multi-AZ with auto failover**.

[⬆ Back to top](#table-of-contents)

---

## Caching Strategy Table

| Strategy                       | Cache written on | Pro                                             | Con                                                  | Pair with          |
| :----------------------------- | :--------------- | :---------------------------------------------- | :--------------------------------------------------- | :----------------- |
| **Lazy loading (cache-aside)** | Read miss        | Caches only requested data; survives cache loss | First-read miss; can go stale                        | TTL                |
| **Write-through**              | Every write      | Always fresh; no first-read miss                | Extra write hop; caches unread data; cold-start gaps | Lazy loading + TTL |
| **TTL**                        | (expiry rule)    | Bounds staleness; frees memory                  | Too short = misses; too long = stale                 | Both strategies    |

> [!tip] Exam Tip
> Default = **lazy loading + TTL**. Need fresh-after-write = **write-through**. Stale data = **lower TTL / invalidate on write**.

[⬆ Back to top](#table-of-contents)

---

## Eviction Policies

| `maxmemory-policy`                   | Behaviour                                              |
| :----------------------------------- | :----------------------------------------------------- |
| `noeviction`                         | Reject writes when full (OOM errors) — bad for a cache |
| `allkeys-lru`                        | LRU across all keys — common cache default             |
| `volatile-lru`                       | LRU among keys with a TTL                              |
| `allkeys-lfu` / `volatile-lfu`       | Least-frequently-used variants                         |
| `allkeys-random` / `volatile-random` | Random eviction                                        |
| `volatile-ttl`                       | Evict nearest-to-expiry first                          |

> [!tip] Exam Tip
> Cache rejecting writes when full = `noeviction`. For caches use **`allkeys-lru`/`allkeys-lfu`**; watch the **`Evictions`** metric.

[⬆ Back to top](#table-of-contents)

---

## Key Metrics

| Metric                            | Meaning / use                                                  |
| :-------------------------------- | :------------------------------------------------------------- |
| **CacheHitRate**                  | Cache effectiveness; low = ineffective                         |
| **Evictions**                     | Memory pressure — node too small                               |
| **EngineCPUUtilization**          | **Redis** engine-thread CPU (the real Redis bottleneck signal) |
| **CPUUtilization**                | All-vCPU CPU; primary signal for **Memcached**                 |
| **SwapUsage**                     | Should be ~0; non-zero = under-provisioned memory              |
| **FreeableMemory**                | RAM headroom                                                   |
| **DatabaseMemoryUsagePercentage** | Closeness to `maxmemory`                                       |
| **CurrConnections**               | Connection load / pooling issues                               |
| **ReplicationLag**                | Replica staleness                                              |

> [!tip] Exam Tip
> For Redis CPU use **`EngineCPUUtilization`** (single-threaded engine); for Memcached use **`CPUUtilization`** (multi-threaded). **`SwapUsage` ≈ 0** always.

[⬆ Back to top](#table-of-contents)

---

## DAX vs ElastiCache for the Exam

|                   | **DAX**                                                | **ElastiCache**                                   |
| :---------------- | :----------------------------------------------------- | :------------------------------------------------ |
| Caches for        | **DynamoDB only**                                      | RDS/Aurora/any data, sessions, general cache      |
| API               | **DynamoDB-compatible** (drop-in, minimal code change) | Redis/Memcached protocol (you build cache-aside)  |
| Latency           | Microseconds                                           | Microseconds                                      |
| Cache-aside logic | Built-in / transparent                                 | You implement it                                  |
| Use case keyword  | "DynamoDB + microsecond reads, minimal change"         | "Offload RDS reads / session store / leaderboard" |

> [!tip] Exam Tip
> **DynamoDB + microsecond reads + least code change = DAX.** ElastiCache is the answer for **non-DynamoDB** caching (RDS offload, sessions, leaderboards) or when you explicitly build your own DynamoDB cache-aside layer.

[⬆ Back to top](#table-of-contents)

---

## Rapid-Fire Facts

1. ElastiCache = fully managed **in-memory** cache; **microsecond** latency.
2. Engines: **Redis OSS, Valkey, Memcached** (Valkey is the open fork, wire-compatible, often cheaper).
3. Runs **in your VPC**; no public endpoint; secured by **security groups**.
4. **Redis = feature-rich** (HA, persistence, data structures); **Memcached = simple + multi-threaded**.
5. Memcached has **no replication, no failover, no persistence, no backups**.
6. **Multi-AZ + auto failover** needs **≥1 read replica**; failover in **seconds to ~1 min**.
7. **Cluster mode enabled** shards data across up to **500 node groups** (16,384 hash slots).
8. Cluster mode enabled clients use the **configuration endpoint**.
9. Cluster mode disabled clients use **primary** (writes) and **reader** (reads) endpoints.
10. Up to **5 read replicas per shard**; replicas are **asynchronous** (slightly stale reads).
11. **Snapshots** (`.rdb`) stored in **S3**; automatic or manual; used to restore/migrate/reshard.
12. **AOF** persistence exists but is **not on cluster-mode-enabled**; AWS prefers **Multi-AZ** for durability.
13. **Global Datastore** = cross-Region Redis/Valkey, 1 primary + up to 2 read-only secondary Regions, sub-second lag.
14. **Sorted sets** → real-time **leaderboards**; **pub/sub** → lightweight messaging.
15. **Session store for stateless web tier** → **ElastiCache for Redis**.
16. Caching strategies: **lazy loading (cache-aside)** and **write-through**, both with **TTL**.
17. **Stale data** → lower the **TTL** / invalidate on write.
18. Eviction default for caches: **`allkeys-lru`**; **`noeviction`** causes write errors when full.
19. **Encryption** in-transit (TLS) and at-rest; **Redis AUTH / RBAC / IAM auth**; at-rest must be set **at creation**.
20. Redis CPU signal = **`EngineCPUUtilization`** (single-threaded); Memcached = **`CPUUtilization`**.
21. **`SwapUsage`** should be ~0; **`Evictions`** rising = memory pressure.
22. **ElastiCache Serverless** = auto-scaling, multi-AZ HA, pay-per-use (data GB-hours + ECPUs) for spiky load.
23. **Reserved Nodes** = cheapest for steady, predictable load.
24. **DynamoDB microsecond cache = DAX**, not ElastiCache (the classic trap).
25. Default ports: **Redis 6379**, **Memcached 11211**.
26. **Data tiering** (Redis on **R6gd** nodes) tiers data DRAM + **NVMe SSD**; ideal when only **~20%** of data is hot; scales to **1 PB**/cluster; cold data moved to SSD **asynchronously**.
27. **Compliance:** Redis/Valkey supports **PCI DSS, HIPAA, FedRAMP**; Memcached lacks strong auth/encryption → keep in **private subnets, no public access**.
28. **Subnet planning:** a **cache subnet group** with enough usable IPs (driven by **subnet CIDR**) is required; too few IPs blocks node scale-out.

[⬆ Back to top](#table-of-contents)
