# Amazon OpenSearch Troubleshooting (SRE) - SAA-C03 Deep Dive

> SRE-style runbook for OpenSearch: cluster **yellow/red** status, **JVM memory pressure** / circuit breakers, **hot-node skew**, **master instability**, **disk watermark / full storage**, **slow queries**, and **blue/green** failures — each as symptom → metric → root cause → fix → prevention.

See also: [01 - OpenSearch Intro & Core Concepts](01%20-%20OpenSearch%20Intro%20%26%20Core%20Concepts.md) · [02 - OpenSearch Architecture Deep Dive](02%20-%20OpenSearch%20Architecture%20Deep%20Dive.md) · [03 - OpenSearch Best Practices & Examples](03%20-%20OpenSearch%20Best%20Practices%20%26%20Examples.md) · [04 - OpenSearch Scenario Questions](04%20-%20OpenSearch%20Scenario%20Questions.md) · [06 - OpenSearch Important Facts & Cheat Sheet](06%20-%20OpenSearch%20Important%20Facts%20%26%20Cheat%20Sheet.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md)

---

## Table of Contents

- [Cluster Yellow or Red Status](#cluster-yellow-or-red-status)
- [JVM Memory Pressure and Circuit Breakers](#jvm-memory-pressure-and-circuit-breakers)
- [Hot-Node Skew](#hot-node-skew)
- [Master-Node Instability](#master-node-instability)
- [Disk Watermark and Storage Full](#disk-watermark-and-storage-full)
- [Slow Queries](#slow-queries)
- [Blue/Green Change Failures](#bluegreen-change-failures)
- [Summary: Key Takeaways](#summary-key-takeaways)

---

## Cluster Yellow or Red Status

| Field          | Detail                                                                                                                                                                                                          |
| :------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Symptom**    | `ClusterStatus.yellow` or `ClusterStatus.red` alarm; some shards unavailable                                                                                                                                    |
| **Metric**     | `ClusterStatus` (green/yellow/red), `Shards.unassigned`                                                                                                                                                         |
| **Root cause** | **Yellow** = replica shards unassigned (data safe, no redundancy). **Red** = at least one **primary** shard unassigned (data unavailable) — often a node loss, no space, or too few nodes for the replica count |
| **Fix**        | For yellow: add nodes or lower replica count so replicas can allocate. For red: free up disk, restore the lost node, or **restore from snapshot**; check `_cluster/allocation/explain`                          |
| **Prevention** | Multi-AZ (with Standby), proper replica count, disk headroom, and monitoring on `ClusterStatus`                                                                                                                 |

> **Exam Tip:** **Yellow = replicas unassigned (still functional)**; **Red = a primary is missing (data loss/unavailable)**. Red is urgent.

[⬆ Back to top](#table-of-contents)

---

## JVM Memory Pressure and Circuit Breakers

| Field          | Detail                                                                                                                               |
| :------------- | :----------------------------------------------------------------------------------------------------------------------------------- |
| **Symptom**    | Rejected requests, `CircuitBreakerException`, node drops, slow indexing                                                              |
| **Metric**     | `JVMMemoryPressure` (alert > 80%; > 95% triggers node-level protection)                                                              |
| **Root cause** | Heap exhausted — **oversharding** (too many shards), huge aggregations, large bulk requests, or fielddata on high-cardinality fields |
| **Fix**        | Reduce shard count (consolidate/reindex), scale up instance type (more heap), simplify queries/aggregations, clear fielddata caches  |
| **Prevention** | Keep **≤ ~25 shards/GB heap**, size shards ~10–50 GB, scale before sustained > 80% pressure                                          |

> **Trap:** Throwing more storage at JVM pressure won't help — it's a **heap/RAM** problem. Fix sharding or scale the **instance type**.

[⬆ Back to top](#table-of-contents)

---

## Hot-Node Skew

| Field          | Detail                                                                                                                                         |
| :------------- | :--------------------------------------------------------------------------------------------------------------------------------------------- |
| **Symptom**    | One data node has far higher CPU/disk/latency than its peers                                                                                   |
| **Metric**     | Per-node `CPUUtilization`, `JVMMemoryPressure`, `FreeStorageSpace` diverge                                                                     |
| **Root cause** | Uneven shard distribution — e.g. all primaries for the active index landed on one node ("hot shard"), or a single huge index/shard             |
| **Fix**        | Rebalance shards, increase shard count for the hot index (reindex), enable shard allocation awareness, use time-based indices so writes spread |
| **Prevention** | Even shard sizing, **zone-aware** allocation, rollover indices for time-series data                                                            |

> **Exam Tip:** Hot-node skew usually traces back to **shard design** — spread shards evenly across nodes/AZs.

[⬆ Back to top](#table-of-contents)

---

## Master-Node Instability

| Field          | Detail                                                                                                                                             |
| :------------- | :------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Symptom**    | Frequent leader re-elections, "no master" errors, cluster intermittently unresponsive                                                              |
| **Metric**     | `MasterReachableFromNode`, `MasterCPUUtilization`, `MasterJVMMemoryPressure`                                                                       |
| **Root cause** | **No dedicated managers** (data load starves management), an **even/2-node** manager count (split-brain risk), or **undersized** manager instances |
| **Fix**        | Add **dedicated cluster-manager nodes**, use an **odd number ≥ 3**, and size the manager type to the **data-node count**                           |
| **Prevention** | Always run **3 dedicated managers** in production; scale manager type as data nodes grow                                                           |

> **Exam Tip:** "Cluster keeps losing its master / split-brain" → **odd ≥ 3 dedicated cluster-manager nodes**.

[⬆ Back to top](#table-of-contents)

---

## Disk Watermark and Storage Full

| Field          | Detail                                                                                                                             |
| :------------- | :--------------------------------------------------------------------------------------------------------------------------------- |
| **Symptom**    | Indexing blocked, `cluster_block_exception` (read-only-allow-delete), shards won't allocate                                        |
| **Metric**     | `FreeStorageSpace` low; disk crosses **low/high/flood-stage watermarks**                                                           |
| **Root cause** | Data growth outpaced storage; at the **flood-stage watermark** OpenSearch sets indices **read-only** to protect the cluster        |
| **Fix**        | Free space (delete/aged indices, move to UltraWarm/cold), **grow EBS** (blue/green), then clear the `read_only_allow_delete` block |
| **Prevention** | Alarm on `FreeStorageSpace`, ISM lifecycle to tier/delete old data, leave growth headroom                                          |

> **Trap:** After hitting flood stage, freeing space alone may not lift the **read-only block** — you must reset the index block setting too.

[⬆ Back to top](#table-of-contents)

---

## Slow Queries

| Field          | Detail                                                                                                                          |
| :------------- | :------------------------------------------------------------------------------------------------------------------------------ |
| **Symptom**    | High search latency, timeouts under load                                                                                        |
| **Metric**     | `SearchLatency`, `SearchRate`, `ThreadpoolSearchQueue`, `ThreadpoolSearchRejected`                                              |
| **Root cause** | Heavy aggregations, wildcard/regex queries, too few replicas for read volume, undersized nodes, or oversharding fan-out         |
| **Fix**        | Add **replica shards** (read scale), tune queries (avoid leading wildcards), scale data nodes, cache results, right-size shards |
| **Prevention** | Use the **slow log**, load-test, provision replicas for read-heavy workloads                                                    |

> **Exam Tip:** **More read throughput → add replica shards** (and/or scale data nodes). Replicas can change live; primaries cannot.

[⬆ Back to top](#table-of-contents)

---

## Blue/Green Change Failures

| Field          | Detail                                                                                                                                             |
| :------------- | :------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Symptom**    | Config change (resize, upgrade, encryption) stuck "Processing" or fails/rolls back                                                                 |
| **Metric**     | Domain status events; `FreeStorageSpace`, `JVMMemoryPressure` during migration                                                                     |
| **Root cause** | Insufficient **capacity headroom** — blue/green temporarily needs extra nodes/storage; a near-full or pressured domain can't spin up the green env |
| **Fix**        | Free space / reduce load, then retry the change; do it during **off-peak**; split large changes into steps                                         |
| **Prevention** | Maintain capacity headroom, schedule changes **off-peak**, snapshot before major upgrades                                                          |

> **Exam Tip:** Config changes use **blue/green** and temporarily need extra capacity — leave headroom and run them **off-peak**.

[⬆ Back to top](#table-of-contents)

---

## Summary: Key Takeaways

- **Yellow** = replicas unassigned (OK); **Red** = primary missing (urgent, data unavailable).
- **JVMMemoryPressure** high → fix **sharding** / scale instance type, not storage.
- **Hot-node skew** → rebalance / fix **shard design**; use zone awareness + time-based indices.
- **Master instability** → **odd ≥ 3 dedicated managers**, sized to data-node count.
- **FreeStorageSpace** low → flood-stage **read-only block**; free space, grow EBS, clear the block.
- **Slow queries** → add **replicas**, tune queries, scale data nodes.
- **Blue/green failures** → need **capacity headroom**, run **off-peak**.

[⬆ Back to top](#table-of-contents)
