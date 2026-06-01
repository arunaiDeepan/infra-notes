# ElastiCache Troubleshooting (SRE) - SAA-C03 Deep Dive

> An SRE-oriented runbook for ElastiCache: low hit-rate / cache misses, eviction storms, memory pressure (SwapUsage / FreeableMemory), CPU saturation (EngineCPUUtilization vs CPUUtilization), failover events and client reconnection, thundering herd / cache stampede, stale data, hot keys, and connection-limit exhaustion.

See also: [01 - ElastiCache Intro & Core Concepts](01%20-%20ElastiCache%20Intro%20%26%20Core%20Concepts.md) · [02 - ElastiCache Architecture Deep Dive](02%20-%20ElastiCache%20Architecture%20Deep%20Dive.md) · [03 - ElastiCache Best Practices & Examples](03%20-%20ElastiCache%20Best%20Practices%20%26%20Examples.md) · [04 - ElastiCache Scenario Questions](04%20-%20ElastiCache%20Scenario%20Questions.md) · [06 - ElastiCache Important Facts & Cheat Sheet](06%20-%20ElastiCache%20Important%20Facts%20%26%20Cheat%20Sheet.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md) · [01 - DynamoDB Intro & Core Concepts](01%20-%20DynamoDB%20Intro%20%26%20Core%20Concepts.md)

---

## Table of Contents

- [Key Metrics to Watch](#key-metrics-to-watch)
- [Low Hit-Rate and Cache Misses](#low-hit-rate-and-cache-misses)
- [Eviction Storms](#eviction-storms)
- [Memory Pressure SwapUsage and FreeableMemory](#memory-pressure-swapusage-and-freeablememory)
- [CPU Saturation EngineCPU vs CPU](#cpu-saturation-enginecpu-vs-cpu)
- [Failover Events and Client Reconnection](#failover-events-and-client-reconnection)
- [Thundering Herd Cache Stampede](#thundering-herd-cache-stampede)
- [Stale Data and TTL Tuning](#stale-data-and-ttl-tuning)
- [Hot Keys](#hot-keys)
- [Connection Limit Exhaustion](#connection-limit-exhaustion)

---

## Key Metrics to Watch

| CloudWatch metric                    | What it tells you                                                                   |
| :----------------------------------- | :---------------------------------------------------------------------------------- |
| **CacheHitRate**                     | % of gets served from cache; low = ineffective caching                              |
| **CacheHits / CacheMisses**          | Raw hit/miss counts                                                                 |
| **Evictions**                        | Keys evicted due to `maxmemory` — memory pressure indicator                         |
| **EngineCPUUtilization**             | CPU of the **Redis process thread** (the one that matters for Redis)                |
| **CPUUtilization**                   | CPU across **all vCPUs** on the node (most meaningful for multi-threaded Memcached) |
| **FreeableMemory**                   | RAM available before swap                                                           |
| **SwapUsage**                        | Memory swapped to disk — should be near 0; high = trouble                           |
| **DatabaseMemoryUsagePercentage**    | How close Redis is to `maxmemory`                                                   |
| **CurrConnections / NewConnections** | Connection load                                                                     |
| **ReplicationLag**                   | Replica staleness behind primary                                                    |

> [!tip] Exam Tip
> For **Redis** CPU, watch **`EngineCPUUtilization`** (the engine is single-threaded per shard, so total `CPUUtilization` can look low while the engine thread is pegged). For **Memcached** (multi-threaded), **`CPUUtilization`** is the right signal.

[⬆ Back to top](#table-of-contents)

---

## Low Hit-Rate and Cache Misses

**Symptom:** `CacheHitRate` low; DB load not reduced; latency high.

Likely causes and fixes:

- **TTL too short** → keys expire before reuse. Lengthen TTL for stable data.
- **Cold cache** (new/restarted/failed-over node) → expected briefly; pre-warm hot keys.
- **High eviction** pushing out hot data → see eviction storms (scale memory / better policy).
- **Cache keys too granular / not reused** → redesign keys for reuse.
- **Lazy loading only, never populated for hot path** → add write-through for hot data.

> [!tip] Exam Tip
> Low hit rate after a TTL change = TTL too short. Low hit rate with high `Evictions` = memory pressure, not TTL.

[⬆ Back to top](#table-of-contents)

---

## Eviction Storms

**Symptom:** `Evictions` metric spiking; hot keys disappearing; hit rate dropping.

Cause: dataset > `maxmemory`, so Redis evicts to make room (or, with `noeviction`, **writes fail** with OOM errors).

Runbook:

1. Check `DatabaseMemoryUsagePercentage` and `Evictions`.
2. **Scale up** the node type (more RAM) or **scale out** with cluster mode enabled (more shards).
3. Verify `maxmemory-policy` is an LRU/LFU policy suited to a cache (`allkeys-lru`/`allkeys-lfu`), not `noeviction`.
4. **Lower TTLs** / remove never-read keys to shrink the working set.
5. Reserve overhead memory (avoid 100% utilisation causing swap).

> [!tip] Exam Tip
> Rising **`Evictions`** = the node is too small for the working set. Fix = bigger node, more shards, shorter TTLs, or eviction-policy tuning.

[⬆ Back to top](#table-of-contents)

---

## Memory Pressure SwapUsage and FreeableMemory

**Symptom:** `SwapUsage` rising, `FreeableMemory` low, latency spikes.

- Redis using more memory than RAM forces **swap to disk**, destroying microsecond latency.
- Causes: working set too large, no/poor eviction policy, large `reserved-memory` not configured, big snapshot/replication memory spikes.

Runbook:

1. Alarm on **`SwapUsage` > 0** and low **`FreeableMemory`**.
2. Set **`reserved-memory-percent`** so the OS/replication has headroom.
3. Scale up or shard out.
4. Snapshot from a **replica** to avoid the primary's fork/copy memory spike.

> [!tip] Exam Tip
> **`SwapUsage` should be ~0.** Non-zero swap on ElastiCache = under-provisioned memory → scale or tune `reserved-memory`.

[⬆ Back to top](#table-of-contents)

---

## CPU Saturation EngineCPU vs CPU

**Symptom:** Commands slowing under load.

- **Redis** processes commands on a **single thread per shard** → watch **`EngineCPUUtilization`**. If it nears 100%, the engine thread is the bottleneck even if node `CPUUtilization` looks moderate.
- **Memcached** is multi-threaded → **`CPUUtilization`** across vCPUs is the right metric.

Fixes for Redis engine CPU saturation:

1. **Scale out** (cluster mode enabled) to spread load across shards' engine threads.
2. Add **read replicas** + reader endpoint to offload reads.
3. Eliminate **expensive O(N) commands** (`KEYS *`, large `SORT`, big range ops) and **hot keys**.
4. Use larger/newer node generation.

> [!tip] Exam Tip
> Classic trap: "Redis node CPU is only 30% but it is slow." → check **`EngineCPUUtilization`**; the single engine thread can be saturated. Scale out / add replicas / kill `KEYS`-style commands.

[⬆ Back to top](#table-of-contents)

---

## Failover Events and Client Reconnection

**Symptom:** Brief write errors / connection resets during a failover or maintenance.

- On primary failure with **Multi-AZ + auto failover**, ElastiCache promotes a replica and updates the **primary endpoint DNS** — typically seconds to ~1 minute.
- Clients must **reconnect** and **re-resolve DNS** (some clients cache DNS too long).

Runbook / best practice:

1. Connect by **endpoint**, never node IP.
2. Configure client **retry with backoff** and short DNS TTL handling.
3. Use cluster-aware clients for cluster mode enabled.
4. Subscribe to ElastiCache **events** (SNS) to observe failovers.

> [!tip] Exam Tip
> Transient errors during failover are expected; the cure is **client-side retry/reconnect logic** and connecting by **endpoint**, not extra AWS config.

[⬆ Back to top](#table-of-contents)

---

## Thundering Herd Cache Stampede

**Symptom:** A popular key expires (or the cache is cold) and thousands of requests **simultaneously miss** and hammer the DB.

Mitigations:

- **Request coalescing / locking**: first miss takes a lock to repopulate; others wait or serve stale.
- **Staggered/jittered TTLs** so many keys do not expire at the same instant.
- **Pre-warming** the cache before traffic.
- Serve **stale-while-revalidate** during repopulation.

> [!tip] Exam Tip
> "DB spikes every time a hot cache key expires" = **thundering herd / cache stampede**. Fix with **TTL jitter, locking/coalescing, or pre-warming** — not by removing the cache.

[⬆ Back to top](#table-of-contents)

---

## Stale Data and TTL Tuning

**Symptom:** Cached values lag the source of truth.

- **Lazy loading** caches at miss time, so a later DB update is not reflected until the key expires → bound with a **TTL** and/or **invalidate the key on write**.
- **Write-through** keeps it fresh on every write but a cold node is missing data until rewritten.

> [!tip] Exam Tip
> Stale data = TTL too long or no invalidation. **Lower the TTL** or **invalidate on write**; for always-fresh reads use **write-through** (plus lazy loading for cold-start).

[⬆ Back to top](#table-of-contents)

---

## Hot Keys

**Symptom:** One key/shard gets disproportionate traffic, saturating a single shard's engine thread while others are idle.

Mitigations:

- **Replicate the hot key** across multiple keys/shards (key suffixing) and read randomly.
- Add **read replicas** to spread reads of the hot key.
- Use **client-side caching** for ultra-hot keys.
- Re-check the sharding/key design so load distributes evenly.

> [!tip] Exam Tip
> A single shard hot while others idle = **hot key**. Adding shards does not help if all traffic targets one key — you must spread the **key** itself or add replicas.

[⬆ Back to top](#table-of-contents)

---

## Connection Limit Exhaustion

**Symptom:** New connections refused; `CurrConnections` near the node limit; `NewConnections` churning.

Causes and fixes:

- **No connection pooling** → each request opens a new connection. Use a **pool** and reuse connections.
- **Connection leaks** → ensure clients close/return connections.
- Lambda or large fleets opening many short-lived connections → use pooling/proxy patterns and reuse across invocations.
- Scale the node type (limits scale with size) if genuinely needed.

> [!tip] Exam Tip
> "Cache refusing new connections / connection errors under load" → first suspect **missing connection pooling / leaks**, then node sizing. Watch **`CurrConnections`**.

[⬆ Back to top](#table-of-contents)
