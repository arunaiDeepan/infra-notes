# Neptune Important Facts & Cheat Sheet - SAA-C03 Deep Dive

> Rapid-fire reference for Amazon Neptune: query languages, graph models, Aurora-like architecture facts, use-case keywords, Streams/Serverless/ML, key metrics, and 15+ exam facts.

See also: [01 - Neptune Intro & Core Concepts](01%20-%20Neptune%20Intro%20%26%20Core%20Concepts.md) · [02 - Neptune Architecture Deep Dive](02%20-%20Neptune%20Architecture%20Deep%20Dive.md) · [03 - Neptune Best Practices & Examples](03%20-%20Neptune%20Best%20Practices%20%26%20Examples.md) · [04 - Neptune Scenario Questions](04%20-%20Neptune%20Scenario%20Questions.md) · [05 - Neptune Troubleshooting (SRE)](05%20-%20Neptune%20Troubleshooting%20%28SRE%29.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md) · [01 - Aurora Intro & Core Concepts](01%20-%20Aurora%20Intro%20%26%20Core%20Concepts.md)

---

## Table of Contents

- [Query Languages & Models](#query-languages--models)
- [Architecture Facts](#architecture-facts)
- [Use-Case Keyword Map](#use-case-keyword-map)
- [Streams, Serverless & ML](#streams-serverless--ml)
- [Key Metrics](#key-metrics)
- [Rapid-Fire Facts](#rapid-fire-facts)
- [Exam Tips & Traps](#exam-tips--traps)

---

## Query Languages & Models

| Language       | Data Model     | Standard         | Pick when                                          |
| :------------- | :------------- | :--------------- | :------------------------------------------------- |
| **Gremlin**    | Property graph | Apache TinkerPop | Imperative traversals; TinkerPop apps              |
| **openCypher** | Property graph | openCypher       | Declarative `MATCH` patterns; Cypher/Neo4j-style   |
| **SPARQL**     | **RDF**        | **W3C**          | Triples, linked data, ontologies, knowledge graphs |

| Property Graph             | RDF                                          |
| :------------------------- | :------------------------------------------- |
| Nodes + edges + properties | Subject-Predicate-Object **triples**         |
| Gremlin / openCypher       | SPARQL                                       |
| Operational graphs         | Semantic / interoperable / standardized data |

[⬆ Back to top](#table-of-contents)

---

## Architecture Facts

| Fact                 | Value                                                                                                                    |
| :------------------- | :----------------------------------------------------------------------------------------------------------------------- |
| Storage copies       | **6 copies across 3 AZs**                                                                                                |
| Self-healing storage | Yes, automatic                                                                                                           |
| Storage auto-grow    | Starts at **10 GB**, grows to **64 TiB / 128 TiB** (version-dependent), 10 GB increments; storage decoupled from compute |
| Writer               | **1 primary** max (writes + reads); scales **vertically only**                                                           |
| Read replicas        | Up to **15**; scale **vertically or horizontally**; AWS recommends **≥ 1**                                               |
| Caches               | **Buffer cache** (~2/3 of memory), **lookup cache** (R5d/NVMe, default on), **query results cache** (Gremlin read-only)  |
| Backup               | Continuous to **S3** + **PITR** (1–35 days)                                                                              |
| Encryption           | **KMS** at rest, **TLS** in transit                                                                                      |
| Auth                 | **IAM database authentication** (SigV4)                                                                                  |
| Network              | Runs in a **VPC**                                                                                                        |
| Endpoints            | Cluster (write), Reader (read), Instance, Custom                                                                         |
| Global Database      | 1 primary + up to **5** secondary Regions, < 1s lag                                                                      |
| ACID                 | Yes (on writer)                                                                                                          |

[⬆ Back to top](#table-of-contents)

---

## Use-Case Keyword Map

| Keyword in question                                                                     | Answer                       |
| :-------------------------------------------------------------------------------------- | :--------------------------- |
| Highly connected data / relationships / graph                                           | **Neptune**                  |
| Social network / friends-of-friends                                                     | **Neptune**                  |
| Recommendation engine                                                                   | **Neptune** (+ ML)           |
| Fraud detection / fraud ring                                                            | **Neptune**                  |
| Knowledge graph                                                                         | **Neptune**                  |
| Identity graph                                                                          | **Neptune**                  |
| Network / IT topology, dependency mapping                                               | **Neptune**                  |
| Map cloud-infra relationships / who uses an IAM role / find overpermissive IAM policies | **Neptune**                  |
| RDF / SPARQL / W3C / triples / linked data                                              | **Neptune (RDF)**            |
| Gremlin / openCypher                                                                    | **Neptune (property graph)** |
| JOINs/recursive queries too slow for deep relationships                                 | **Neptune**                  |
| Predict missing links / classify nodes via ML                                           | **Neptune ML**               |

[⬆ Back to top](#table-of-contents)

---

## Streams, Serverless & ML

| Feature                | What it does                                                                           | Keyword                                      |
| :--------------------- | :------------------------------------------------------------------------------------- | :------------------------------------------- |
| **Neptune Streams**    | Ordered change-capture log of graph mutations (via REST)                               | "capture/replicate graph changes"            |
| **Neptune Serverless** | Auto-scales compute via **NCUs** (min/max)                                             | "variable / unpredictable graph load"        |
| **Neptune ML**         | **GNN** predictions via **SageMaker**: link prediction, node classification/regression | "ML predictions on a graph"                  |
| **Global Database**    | Multi-Region read + DR                                                                 | "low-latency global reads / cross-Region DR" |
| **Bulk Loader**        | Fast import from **S3** (CSV/RDF) via `/loader`                                        | "load large dataset into graph"              |

[⬆ Back to top](#table-of-contents)

---

## Key Metrics

| Metric                                                                        | Meaning                   |
| :---------------------------------------------------------------------------- | :------------------------ |
| `NeptuneReplicaLag`                                                           | Replica staleness         |
| `CPUUtilization`                                                              | Compute load              |
| `MainRequestQueuePendingRequests`                                             | Overload / queuing        |
| `GremlinRequestsPerSec` / `SparqlRequestsPerSec` / `OpenCypherRequestsPerSec` | Query throughput          |
| `VolumeBytesUsed`                                                             | Storage consumed          |
| `BufferCacheHitRatio`                                                         | Cache hit effectiveness   |
| `NCUUtilization`                                                              | Serverless capacity usage |

[⬆ Back to top](#table-of-contents)

---

## Rapid-Fire Facts

1. Neptune is a **fully managed graph database** for highly connected data.
2. Supports **3 query languages**: Gremlin, openCypher, SPARQL.
3. **Gremlin + openCypher** = property graph; **SPARQL** = RDF.
4. RDF is a **W3C standard** based on **triples** (subject-predicate-object).
5. Storage keeps **6 copies across 3 AZs**, self-healing.
6. Storage **auto-grows** in 10 GB increments (to 64/128 TiB).
7. **1 writer + up to 15 read replicas**.
8. **Cluster (writer) endpoint** = writes; **reader endpoint** = reads (**round-robin** across replicas). Reader balances connections only — **no instance-level load balancing**; the app must distribute reads.
9. **Automatic failover** promotes a replica (seconds); old writer rejoins as a replica. A **no-replica cluster** can be **down a few minutes** while the writer restarts.
10. **Continuous backup to S3** with **PITR** (1–35 days).
11. **KMS** at rest, **TLS** in transit, **IAM auth** (SigV4), runs in a **VPC**.
12. **Neptune Streams** = ordered change capture.
13. **Neptune Serverless** auto-scales via **NCUs**.
14. **Neptune ML** uses **GNNs via SageMaker** (link prediction, node classification).
15. **Global Database** = up to 5 secondary Regions, < 1s lag, cross-Region DR.
16. **Bulk Loader** imports from **S3** (needs IAM role + S3 VPC endpoint).
17. **ACID** transactions on the writer.
18. Three caches: **buffer** (~2/3 of instance memory), **lookup** (R5d/NVMe SSD, default on), **query results** (Gremlin read-only; clear via TTL/per-query/full).
19. **Not** for key-value scale (that is DynamoDB) or tabular SQL (that is RDS/Aurora).

[⬆ Back to top](#table-of-contents)

---

## Exam Tips & Traps

- Any relationship/connection/graph keyword → **Neptune**.
- **SPARQL/RDF/W3C** → RDF model; **Gremlin/openCypher** → property graph.
- Storage signature shared with Aurora: **6 copies / 3 AZs**, auto-grow, self-healing.
- Writes → cluster endpoint; reads → reader endpoint (failover trap).
- **Streams** = change capture, **Serverless** = NCU auto-scale, **ML** = GNN/SageMaker, **Global DB** = multi-Region.
- Bulk import → **S3 Bulk Loader** (IAM role + S3 VPC endpoint).
- Don't confuse with **DynamoDB** (key-value) or **RDS/Aurora** (relational).

[⬆ Back to top](#table-of-contents)
