# DocumentDB Troubleshooting (SRE) - SAA-C03 Deep Dive

> An SRE-oriented runbook for Amazon DocumentDB: diagnosing replica lag, failover and driver reconnection, connection limits, slow queries from missing indexes, MongoDB feature-compatibility gaps, storage scaling, and backup/restore issues.

See also: [01 - DocumentDB Intro & Core Concepts](01%20-%20DocumentDB%20Intro%20%26%20Core%20Concepts.md) · [02 - DocumentDB Architecture Deep Dive](02%20-%20DocumentDB%20Architecture%20Deep%20Dive.md) · [03 - DocumentDB Best Practices & Examples](03%20-%20DocumentDB%20Best%20Practices%20%26%20Examples.md) · [04 - DocumentDB Scenario Questions](04%20-%20DocumentDB%20Scenario%20Questions.md) · [06 - DocumentDB Important Facts & Cheat Sheet](06%20-%20DocumentDB%20Important%20Facts%20%26%20Cheat%20Sheet.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md) · [01 - Aurora Intro & Core Concepts](01%20-%20Aurora%20Intro%20%26%20Core%20Concepts.md) · [01 - DynamoDB Intro & Core Concepts](01%20-%20DynamoDB%20Intro%20%26%20Core%20Concepts.md)

---

## Table of Contents

- [Replica Lag](#replica-lag)
- [Failover & Driver Reconnection](#failover--driver-reconnection)
- [Connection Limits](#connection-limits)
- [Slow Queries & Missing Indexes](#slow-queries--missing-indexes)
- [MongoDB Compatibility Gaps](#mongodb-compatibility-gaps)
- [Storage Scaling](#storage-scaling)
- [Backup & Restore Issues](#backup--restore-issues)
- [Key Metrics & Alarms](#key-metrics--alarms)
- [Exam Tips & Traps](#exam-tips--traps)

---

## Replica Lag

**Symptoms:** Reads via the reader endpoint return stale data; `DBClusterReplicaLagMaximum` rises.

| Cause                           | Fix                                                                      |
| :------------------------------ | :----------------------------------------------------------------------- |
| Heavy write volume on primary   | Scale up primary instance class; reduce write burst                      |
| Replica under-provisioned       | Use the same/larger instance class as the primary                        |
| Read-after-write expectation    | Read from the **primary** (cluster endpoint / `primary` read preference) |
| Long-running queries on replica | Optimize queries / add indexes                                           |

> [!note]
> Replica reads are **eventually consistent.** Lag is normally milliseconds but spikes under write pressure. Design for it or read from the primary when consistency is required.

[⬆ Back to top](#table-of-contents)

---

## Failover & Driver Reconnection

**Symptoms:** Brief write errors during a failover; app keeps writing to the old primary.

Runbook:

1. Connect via the **cluster endpoint** (not an instance endpoint) so DNS auto-tracks the new primary.
2. Use the **reader endpoint** for reads so they spread across surviving replicas.
3. Configure the driver in **replica-set mode** (`replicaSet=rs0`) so it discovers topology changes.
4. Set **`retryWrites=false`** (DocumentDB requirement) and **implement application-level retry** with backoff for transient errors during promotion.
5. Lower the driver's **server-selection / socket timeouts** so it fails fast and reconnects to the new primary.

> [!warning]
> Hardcoding an **instance endpoint** breaks HA — after failover that instance may be a replica or be replaced. Always use the cluster/reader endpoints.

[⬆ Back to top](#table-of-contents)

---

## Connection Limits

**Symptoms:** `connection refused` / "too many connections"; `DatabaseConnections` near the instance ceiling.

| Cause                                   | Fix                                                                             |
| :-------------------------------------- | :------------------------------------------------------------------------------ |
| No connection pooling                   | Use a pooled driver; cap pool size per app instance                             |
| Lambda fan-out opening many connections | Use **RDS Proxy-style pooling** patterns / reuse connections; limit concurrency |
| Too-small instance                      | Larger instance classes allow more connections                                  |
| Idle connections not released           | Tune driver idle timeouts; close on shutdown                                    |

DocumentDB's **max connections scale with instance memory** (set via the `connections` parameter / instance class). Spread read connections across replicas via the reader endpoint.

[⬆ Back to top](#table-of-contents)

---

## Slow Queries & Missing Indexes

**Symptoms:** High latency, high `ReadIOPS`, low `BufferCacheHitRatio`; queries scanning whole collections.

Runbook:

1. Run **`explain()`** on the slow query; look for **`COLLSCAN`** (full scan) vs **`IXSCAN`** (index scan).
2. **Create an index** matching the filter/sort (compound index, correct field order).
3. Use the **profiler / slow-query logs** (export to CloudWatch Logs) to find offenders.
4. Ensure the **working set + indexes fit in memory** (BufferCacheHitRatio high); otherwise scale up.

```javascript
db.orders.find({ status: "OPEN" }).explain(); // shows COLLSCAN if no index
db.orders.createIndex({ status: 1 }); // fix: add the index
```

[⬆ Back to top](#table-of-contents)

---

## MongoDB Compatibility Gaps

**Symptoms:** A query/operator that works on native MongoDB returns an "unsupported" error on DocumentDB.

| Cause                               | Fix                                                                             |
| :---------------------------------- | :------------------------------------------------------------------------------ |
| Using an unsupported operator/stage | Rewrite the query; consult **functional-differences** docs                      |
| Targeting a newer MongoDB feature   | Choose a higher DocumentDB compatibility version (e.g., 5.0) if it adds support |
| App assumes full MongoDB semantics  | Run the **DocumentDB compatibility tool** before migrating                      |
| Feature truly unavailable           | Handle in app, or evaluate self-managed MongoDB / MongoDB Atlas                 |

> [!warning]
> The driver connecting successfully does **not** guarantee feature parity. Validate the actual operations in a test cluster before production cutover.

[⬆ Back to top](#table-of-contents)

---

## Storage Scaling

**Symptoms:** Concern about running out of space; rising `VolumeBytesUsed`.

- Storage **auto-grows** in 10 GB increments up to **64 TiB** — no manual action.
- If approaching **64 TiB** on a standard cluster, you must **archive/delete data** or move to **Elastic Clusters** (sharding) for petabyte scale.
- Use **TTL indexes** to expire old documents and control growth.
- Storage does not shrink instantly after deletes; reclamation happens over time.

[⬆ Back to top](#table-of-contents)

---

## Backup & Restore Issues

**Symptoms:** Need to recover data or roll back a bad change.

| Situation                             | Action                                                                            |
| :------------------------------------ | :-------------------------------------------------------------------------------- |
| Recover to a point before an incident | **PITR** within the 1–35 day retention window                                     |
| Recover from older state              | Restore from a **manual snapshot**                                                |
| Cross-Region recovery                 | Restore a **copied snapshot** in the target Region, or use **Global Clusters**    |
| Restore behavior                      | Always creates a **new cluster** — plan endpoint/DNS cutover and re-point the app |

> [!note]
> You cannot restore "in place." After a restore, update the app to the **new cluster endpoint** (or swap DNS).

[⬆ Back to top](#table-of-contents)

---

## Key Metrics & Alarms

| CloudWatch metric            | Watch for                                        |
| :--------------------------- | :----------------------------------------------- |
| `CPUUtilization`             | Sustained high → scale up / offload reads        |
| `DatabaseConnections`        | Near ceiling → pooling / bigger instance         |
| `DBClusterReplicaLagMaximum` | High → write pressure / under-sized replicas     |
| `BufferCacheHitRatio`        | Low → working set exceeds memory                 |
| `ReadIOPS` / `WriteIOPS`     | Spikes → missing indexes / I/O cost              |
| `VolumeBytesUsed`            | Approaching 64 TiB → archive or Elastic Clusters |
| `FreeableMemory`             | Low → scale up instance class                    |

[⬆ Back to top](#table-of-contents)

---

## Exam Tips & Traps

- Stale reads → **replica lag** (eventually consistent); read from **primary** for consistency.
- Failover → use **cluster/reader endpoints**, `replicaSet` mode, **`retryWrites=false`** + app retries.
- "Too many connections" → **connection pooling** and/or bigger instance.
- Slow queries / high I/O → **missing index** (check `explain()` for `COLLSCAN`).
- Unsupported MongoDB feature → **compatibility gap**; validate before migrating.
- Storage maxes at **64 TiB** → **Elastic Clusters** for more.
- Restores always create a **new cluster** (no in-place restore).

[⬆ Back to top](#table-of-contents)
