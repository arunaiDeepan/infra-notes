# Neptune Troubleshooting (SRE) - SAA-C03 Deep Dive

> SRE-oriented troubleshooting for Neptune: diagnosing replica lag, failover and endpoint misuse, slow traversals, bulk-load failures, memory pressure on large traversals, connection handling, and query-language mismatches.

See also: [01 - Neptune Intro & Core Concepts](01%20-%20Neptune%20Intro%20%26%20Core%20Concepts.md) · [02 - Neptune Architecture Deep Dive](02%20-%20Neptune%20Architecture%20Deep%20Dive.md) · [03 - Neptune Best Practices & Examples](03%20-%20Neptune%20Best%20Practices%20%26%20Examples.md) · [04 - Neptune Scenario Questions](04%20-%20Neptune%20Scenario%20Questions.md) · [06 - Neptune Important Facts & Cheat Sheet](06%20-%20Neptune%20Important%20Facts%20%26%20Cheat%20Sheet.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md) · [01 - Aurora Intro & Core Concepts](01%20-%20Aurora%20Intro%20%26%20Core%20Concepts.md)

---

## Table of Contents

- [Replica Lag](#replica-lag)
- [Failover & Endpoint Usage](#failover--endpoint-usage)
- [Slow Traversals](#slow-traversals)
- [Bulk-Load Failures](#bulk-load-failures)
- [Memory Pressure on Large Traversals](#memory-pressure-on-large-traversals)
- [Connection Handling](#connection-handling)
- [Query-Language Mismatch](#query-language-mismatch)
- [Key Metrics to Watch](#key-metrics-to-watch)
- [Exam Tips & Traps](#exam-tips--traps)

---

## Replica Lag

**Symptom:** Reads via the reader endpoint return stale data shortly after a write.

| Cause                        | Diagnosis                                          | Remediation                                                 |
| :--------------------------- | :------------------------------------------------- | :---------------------------------------------------------- |
| Heavy write burst            | `VolumeWriteIOPs` high, `NeptuneReplicaLag` spikes | Smooth write load; scale writer instance                    |
| Undersized replicas          | High CPU on replicas                               | Use larger replica instance class                           |
| Read-after-write expectation | App reads its own write from a replica             | Route read-after-write to the **cluster (writer) endpoint** |

> [!note]
> Replica lag is normally tens of milliseconds because replicas share storage with the writer. Sustained high lag signals overloaded compute, not storage replication.

[⬆ Back to top](#table-of-contents)

---

## Failover & Endpoint Usage

**Symptom:** After a failover, the app keeps failing writes or connects to a now-read-only instance.

- **Root cause:** the app cached an **instance endpoint/IP** instead of resolving the **cluster endpoint** DNS, or has a long DNS TTL cache.
- **Fix:** always connect via the **cluster endpoint** for writes and **reader endpoint** for reads; implement **reconnect-on-error** logic; respect DNS TTL (don't pin IPs).
- **HA gap:** if the cluster had **no replicas**, failover means recreating the primary (slower). Keep at least one replica in another AZ.

[⬆ Back to top](#table-of-contents)

---

## Slow Traversals

**Symptom:** Certain Gremlin/openCypher/SPARQL queries are slow or time out.

| Cause                               | Remediation                                                               |
| :---------------------------------- | :------------------------------------------------------------------------ |
| Full graph scan (no anchored start) | Start traversal from a **specific, indexed property/node**                |
| Unbounded depth                     | Limit hops; add early `where`/`MATCH` constraints and `limit`             |
| Supernode hotspots                  | Re-model to avoid vertices with millions of edges                         |
| Reads hitting the writer            | Move read traversals to the **reader endpoint**                           |
| Inefficient query shape             | Use the **Gremlin/openCypher explain & profile** APIs to inspect the plan |

> [!tip]
> Use Neptune's `explain` and `profile` endpoints to see how a traversal executes and where it fans out.

[⬆ Back to top](#table-of-contents)

---

## Bulk-Load Failures

**Symptom:** `POST /loader` job fails or stalls.

| Cause                                     | Fix                                                                   |
| :---------------------------------------- | :-------------------------------------------------------------------- |
| Missing/incorrect **IAM role** on cluster | Attach an IAM role with S3 read permission                            |
| No **S3 VPC endpoint**                    | Create an S3 gateway VPC endpoint so the private cluster can reach S3 |
| Malformed source data                     | Validate CSV/RDF format and headers; check loader error feed          |
| Wrong S3 region/path                      | Ensure bucket region/path match loader request                        |
| Concurrent load conflicts                 | Serialize or use the loader's queueing/parallelism options            |

Monitor with the **loader status endpoint** (`GET /loader/<loadId>`) for per-error detail.

[⬆ Back to top](#table-of-contents)

---

## Memory Pressure on Large Traversals

**Symptom:** Queries fail with out-of-memory errors or the instance shows high memory use during big traversals.

| Cause                                                | Remediation                                                                   |
| :--------------------------------------------------- | :---------------------------------------------------------------------------- |
| Traversal materializes huge intermediate result sets | Add `limit`, paginate, narrow patterns                                        |
| Instance too small for working set                   | Scale up instance class (more RAM) or use **Serverless** with higher max NCUs |
| Unbounded path/`repeat()` expansion                  | Bound depth; avoid Cartesian fan-out                                          |
| Buffer/cache contention                              | Isolate heavy analytics on a **custom endpoint**/dedicated replica            |

> [!warning]
> Graph queries can explode combinatorially. Always bound depth and result size for deep or recommendation-style traversals.

[⬆ Back to top](#table-of-contents)

---

## Connection Handling

**Symptom:** Connection exhaustion, throttling, or dropped WebSocket sessions (Gremlin).

- Use **connection pooling**; reuse connections instead of opening one per request.
- For Gremlin **WebSocket** connections, handle idle timeouts and reconnect gracefully.
- Spread reads across replicas via the **reader endpoint** to avoid overloading the writer.
- Back off and retry on transient throttling; respect server capacity (scale instances/NCUs if sustained).

[⬆ Back to top](#table-of-contents)

---

## Query-Language Mismatch

**Symptom:** Queries error out or return nothing.

- **Root cause:** running **SPARQL** against **property-graph** data, or **Gremlin/openCypher** against **RDF** data — the model and language must match.
- **Fix:** confirm the dataset model: property graph → **Gremlin or openCypher**; RDF → **SPARQL**. Use the matching endpoint for the language.
- Gremlin vs openCypher both read the property graph but have different syntax/semantics — don't mix them in one query.

[⬆ Back to top](#table-of-contents)

---

## Key Metrics to Watch

| CloudWatch metric                                                             | Tells you                                   |
| :---------------------------------------------------------------------------- | :------------------------------------------ |
| `NeptuneReplicaLag`                                                           | Replica staleness                           |
| `CPUUtilization`                                                              | Compute saturation on writer/replicas       |
| `MainRequestQueuePendingRequests`                                             | Requests queuing (overload)                 |
| `GremlinRequestsPerSec` / `SparqlRequestsPerSec` / `OpenCypherRequestsPerSec` | Query throughput by language                |
| `VolumeBytesUsed`                                                             | Storage growth                              |
| `BufferCacheHitRatio`                                                         | Cache effectiveness (low = more disk reads) |
| `NCUUtilization` (Serverless)                                                 | Serverless capacity headroom                |

[⬆ Back to top](#table-of-contents)

---

## Exam Tips & Traps

- Writes must use the **cluster endpoint**; reads use the **reader endpoint** — endpoint misuse is the classic failover trap.
- Bulk-load failures usually mean a **missing IAM role or S3 VPC endpoint**.
- Slow/expensive traversals → anchor at an indexed node, bound depth, avoid **supernodes**, use **explain/profile**.
- Memory blow-ups come from **unbounded traversals** — add limits/pagination or scale up.
- Language must match the model: **SPARQL↔RDF**, **Gremlin/openCypher↔property graph**.
- No replicas = no fast failover and no read scaling.

[⬆ Back to top](#table-of-contents)
