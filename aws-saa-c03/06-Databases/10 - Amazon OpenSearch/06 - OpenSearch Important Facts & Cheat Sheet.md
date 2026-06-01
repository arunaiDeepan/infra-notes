# Amazon OpenSearch Important Facts & Cheat Sheet - SAA-C03 Deep Dive

> Dense, exam-ready reference: node types, the **odd ≥ 3 managers** rule, storage tiers, access/auth, encryption, ingestion sources, OpenSearch-vs-alternatives, key metrics, and 20+ rapid-fire facts.

See also: [01 - OpenSearch Intro & Core Concepts](01%20-%20OpenSearch%20Intro%20%26%20Core%20Concepts.md) · [02 - OpenSearch Architecture Deep Dive](02%20-%20OpenSearch%20Architecture%20Deep%20Dive.md) · [03 - OpenSearch Best Practices & Examples](03%20-%20OpenSearch%20Best%20Practices%20%26%20Examples.md) · [04 - OpenSearch Scenario Questions](04%20-%20OpenSearch%20Scenario%20Questions.md) · [05 - OpenSearch Troubleshooting (SRE)](05%20-%20OpenSearch%20Troubleshooting%20%28SRE%29.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md)

---

## Table of Contents

- [Node Types](#node-types)
- [Dedicated Manager Sizing Rule](#dedicated-manager-sizing-rule)
- [Storage Tiers](#storage-tiers)
- [Access and Authentication](#access-and-authentication)
- [Encryption](#encryption)
- [Ingestion Sources](#ingestion-sources)
- [OpenSearch vs Alternatives](#opensearch-vs-alternatives)
- [Key CloudWatch Metrics](#key-cloudwatch-metrics)
- [Rapid-Fire Facts](#rapid-fire-facts)
- [Summary: Key Takeaways](#summary-key-takeaways)

---

## Node Types

| Node Type                    | Role                                                  | Serves Data? |
| :--------------------------- | :---------------------------------------------------- | :----------- |
| **Cluster manager (master)** | Cluster state, shard allocation, leader election      | No           |
| **Data (hot)**               | Stores active shards, runs index/search               | Yes          |
| **UltraWarm**                | Holds read-only S3-backed warm indices                | Read-only    |
| **Coordinating**             | Routes/aggregates requests (any data node by default) | Routing      |

[⬆ Back to top](#table-of-contents)

---

## Dedicated Manager Sizing Rule

| Rule                              | Value                                                      |
| :-------------------------------- | :--------------------------------------------------------- |
| **Production manager count**      | **Odd, minimum 3** (avoid split-brain)                     |
| **Quorum**                        | `floor(n/2) + 1` → 3 managers tolerate loss of 1           |
| **Never use**                     | 2 managers (no tie-break); even counts                     |
| **Manager type ~1–10 data nodes** | `m5.large.search` / `m6g.large.search`                     |
| **Dev/test**                      | Dedicated managers optional (a data node assumes the role) |

> **Exam Tip:** Default production answer = **3 dedicated cluster-manager nodes**.

[⬆ Back to top](#table-of-contents)

---

## Storage Tiers

| Tier          | Backing                            | Access            | Use                                   |
| :------------ | :--------------------------------- | :---------------- | :------------------------------------ |
| **Hot**       | EBS / instance store on data nodes | Read + write      | Active data, fastest                  |
| **UltraWarm** | **S3 + local cache**               | Read-only         | Cheap, still searchable older indices |
| **Cold**      | **S3** (detached)                  | Reattach to query | Archival, lowest cost                 |

[⬆ Back to top](#table-of-contents)

---

## Access and Authentication

| Concern               | Option                                                                             |
| :-------------------- | :--------------------------------------------------------------------------------- |
| **Network**           | **VPC** (private, security groups) or **public** (set at creation, not switchable) |
| **API auth**          | **IAM** (SigV4-signed)                                                             |
| **Granular authz**    | **Fine-Grained Access Control** (index/document/field-level + dashboard roles)     |
| **Dashboard sign-in** | **Amazon Cognito** or **SAML**                                                     |

[⬆ Back to top](#table-of-contents)

---

## Encryption

| Layer                          | Mechanism                                                  |
| :----------------------------- | :--------------------------------------------------------- |
| **At rest**                    | **AWS KMS** (AWS-managed or customer-managed keys)         |
| **In transit (client)**        | **TLS / HTTPS** (can enforce HTTPS)                        |
| **In transit (intra-cluster)** | **Node-to-node encryption**                                |
| **FGAC prerequisite**          | Requires encryption at rest + node-to-node + enforce HTTPS |

[⬆ Back to top](#table-of-contents)

---

## Ingestion Sources

| Source                                  | Notes                                                           |
| :-------------------------------------- | :-------------------------------------------------------------- |
| **Kinesis Data Firehose**               | Serverless streaming load, optional Lambda transform, S3 backup |
| **CloudWatch Logs**                     | Subscription filter streams logs into OpenSearch                |
| **OpenSearch Ingestion (Data Prepper)** | Managed pipelines, OTel/trace processing                        |
| **Logstash**                            | Self-managed ingestion/ETL                                      |
| **Index API / SDK**                     | Direct document indexing from apps                              |

[⬆ Back to top](#table-of-contents)

---

## OpenSearch vs Alternatives

| Need                                                        | Service                          |
| :---------------------------------------------------------- | :------------------------------- |
| **Full-text / relevance search, log analytics, dashboards** | **Amazon OpenSearch Service**    |
| **Petabyte structured SQL / OLAP, BI**                      | Amazon Redshift                  |
| **Ad-hoc serverless SQL over S3, pay-per-query**            | Amazon Athena                    |
| **Quick queries within CloudWatch Logs**                    | CloudWatch Logs Insights         |
| **OLTP relational**                                         | Amazon RDS / Aurora              |
| **Spiky search/analytics, no capacity planning**            | OpenSearch **Serverless** (OCUs) |

[⬆ Back to top](#table-of-contents)

---

## Key CloudWatch Metrics

| Metric                              | Watch For                                                              |
| :---------------------------------- | :--------------------------------------------------------------------- |
| **ClusterStatus**                   | green / **yellow** (replica unassigned) / **red** (primary unassigned) |
| **JVMMemoryPressure**               | Alert > **80%**; > 95% triggers protection / rejections                |
| **FreeStorageSpace**                | Low → disk watermarks → **read-only** block                            |
| **CPUUtilization**                  | Hot-node skew / undersized nodes                                       |
| **MasterReachableFromNode**         | Master instability / split-brain                                       |
| **SearchLatency / IndexingLatency** | Slow queries / write bottlenecks                                       |
| **ThreadpoolSearchRejected**        | Saturated search queue → add replicas/scale                            |

[⬆ Back to top](#table-of-contents)

---

## Rapid-Fire Facts

1. Formerly **Amazon Elasticsearch Service**, renamed **OpenSearch Service** (2021).
2. OpenSearch & OpenSearch Dashboards are **open-source forks** of Elasticsearch & Kibana.
3. **Domain** = the managed cluster + its config.
4. Production needs **odd ≥ 3 dedicated managers**; quorum avoids **split-brain**.
5. **Managers don't serve data**; size them to **data-node count**.
6. **Primary shard count is fixed at index creation** — change requires **reindex**.
7. **Replica shards** add HA + **read** throughput, changeable any time.
8. Aim **~10–50 GB per shard**; avoid oversharding (JVM pressure).
9. **Multi-AZ with Standby** = best resilience, consistent failover, near-zero RPO.
10. Storage tiers: **Hot → UltraWarm (S3+cache) → Cold (S3)**; warm/cold are read-only.
11. **ISM** policies automate tiering and deletion of aging indices.
12. **VPC vs public** access is set at creation and **not switchable**.
13. **FGAC** = index/document/field-level permissions + dashboard roles.
14. Dashboard sign-in: **Cognito** or **SAML** only.
15. Encryption: **KMS** at rest, **TLS** + **node-to-node** in transit.
16. Config changes (resize/upgrade/encryption) use **blue/green** — do **off-peak** with headroom.
17. **Snapshots to S3**: automated (recovery) + manual (migration / long-term / cross-Region).
18. **Kinesis Data Firehose** = serverless ingestion with **S3 backup**.
19. **Serverless** uses **OCUs**, auto-scales, ideal for spiky workloads.
20. **Yellow** = replica unassigned (functional); **Red** = primary missing (data unavailable).
21. **Flood-stage watermark** sets indices **read-only**; clear the block after freeing space.
22. Pick **Redshift** for OLAP SQL, **Athena** for ad-hoc S3 SQL, **OpenSearch** for search + live log dashboards.

[⬆ Back to top](#table-of-contents)

---

## Summary: Key Takeaways

- Managed search/analytics engine, **formerly Amazon Elasticsearch Service**; forks of Elasticsearch/Kibana.
- **Odd ≥ 3 dedicated managers**; **primaries fixed at creation**, replicas flexible.
- Tiers **Hot/UltraWarm/Cold** (S3-backed) cut log-retention cost via **ISM**.
- Security stack: **VPC + KMS + node-to-node TLS + FGAC**; dashboards via **Cognito/SAML**.
- **Blue/green** for config changes (off-peak); **snapshots to S3** for recovery/migration.
- Choose **OpenSearch** for search & log analytics; **Redshift** for OLAP; **Athena** for S3 SQL.

[⬆ Back to top](#table-of-contents)
