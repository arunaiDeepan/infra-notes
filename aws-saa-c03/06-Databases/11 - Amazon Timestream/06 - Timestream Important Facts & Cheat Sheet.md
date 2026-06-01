# Amazon Timestream Important Facts & Cheat Sheet - SAA-C03 Deep Dive

> Dense, exam-ready reference: tier comparison, retention/append-only/timestamp facts, encryption, LiveAnalytics vs InfluxDB, Timestream vs DynamoDB/RDS/Redshift, integrations, and 18+ rapid-fire facts.

See also: [01 - Timestream Intro & Core Concepts](01%20-%20Timestream%20Intro%20%26%20Core%20Concepts.md) · [02 - Timestream Architecture Deep Dive](02%20-%20Timestream%20Architecture%20Deep%20Dive.md) · [03 - Timestream Best Practices & Examples](03%20-%20Timestream%20Best%20Practices%20%26%20Examples.md) · [04 - Timestream Scenario Questions](04%20-%20Timestream%20Scenario%20Questions.md) · [05 - Timestream Troubleshooting (SRE)](05%20-%20Timestream%20Troubleshooting%20%28SRE%29.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md)

---

## Table of Contents

- [One-Liner](#one-liner)
- [Memory Store vs Magnetic Store](#memory-store-vs-magnetic-store)
- [Retention Append-Only and Timestamp Facts](#retention-append-only-and-timestamp-facts)
- [Encryption Facts](#encryption-facts)
- [LiveAnalytics vs InfluxDB](#liveanalytics-vs-influxdb)
- [Timestream vs Other Databases](#timestream-vs-other-databases)
- [Integrations](#integrations)
- [Rapid-Fire Facts](#rapid-fire-facts)
- [Exam Tips and Traps](#exam-tips-and-traps)

---

## One-Liner

**Amazon Timestream** = fully managed, **serverless time-series database** for IoT/metrics/sensor/clickstream data; tiered storage (memory + magnetic), append-only, SQL with built-in time-series analytics, encrypted by default.

[⬆ Back to top](#table-of-contents)

---

## Memory Store vs Magnetic Store

| Aspect        | Memory store                                               | Magnetic store                                |
| :------------ | :--------------------------------------------------------- | :-------------------------------------------- |
| Holds         | Recent data                                                | Older data                                    |
| Optimized for | Fast writes, **point-in-time / latency-sensitive** queries | **Analytical** queries over long ranges       |
| Cost          | Higher per GB                                              | Lower (cost-optimized)                        |
| Retention     | Hours–days (memory retention)                              | Days up to **200 years** (magnetic retention) |
| Transition    | Data tiers **out to magnetic** on expiry                   | Data **deleted** on expiry                    |

[⬆ Back to top](#table-of-contents)

---

## Retention Append-Only and Timestamp Facts

| Fact                      | Detail                                                                     |
| :------------------------ | :------------------------------------------------------------------------- |
| **Append-only**           | No direct UPDATE/DELETE; removal via retention expiry only                 |
| **Two retention windows** | Memory (→ magnetic) and magnetic (→ delete)                                |
| **Timestamp**             | **Mandatory** on every record; decides tier placement                      |
| **Late data**             | Past memory retention is rejected unless **magnetic store writes** enabled |
| **Auto-expire**           | Set magnetic-store retention — no cleanup jobs needed                      |
| **Total history**         | Memory retention + magnetic retention                                      |

[⬆ Back to top](#table-of-contents)

---

## Encryption Facts

| Fact        | Detail                                                          |
| :---------- | :-------------------------------------------------------------- |
| At rest     | **Encrypted by default**                                        |
| Key options | AWS-owned/managed KMS key **or** customer-managed KMS key (CMK) |
| In transit  | TLS                                                             |
| Audit       | CloudTrail; metrics via CloudWatch                              |

[⬆ Back to top](#table-of-contents)

---

## LiveAnalytics vs InfluxDB

|          | Timestream for LiveAnalytics          | Timestream for InfluxDB                |
| :------- | :------------------------------------ | :------------------------------------- |
| Model    | Serverless, tiered, SQL               | Managed InfluxDB (InfluxQL/Flux)       |
| Scale    | Trillions of events/day               | App-scale, single-digit-ms queries     |
| Use when | New large-scale time-series workloads | Existing InfluxDB apps / compatibility |
| Ops      | No instances to manage                | Managed InfluxDB instance              |

> **Exam Tip:** Default to **LiveAnalytics**; pick **InfluxDB** only when InfluxDB compatibility is stated.

[⬆ Back to top](#table-of-contents)

---

## Timestream vs Other Databases

| Need                                                        | Best service     |
| :---------------------------------------------------------- | :--------------- |
| High-volume **time-series** analytics, serverless           | **Timestream**   |
| Key-value / document lookups, single-digit-ms at scale      | **DynamoDB**     |
| Relational/transactional (OLTP), joins, SQL constraints     | **RDS / Aurora** |
| Data warehouse, complex analytics across many tables (OLAP) | **Redshift**     |
| In-memory caching                                           | **ElastiCache**  |

> **Trap:** Time-stamped data alone doesn't mean DynamoDB or RDS — **time-range analytics at scale** = Timestream.

[⬆ Back to top](#table-of-contents)

---

## Integrations

- **AWS IoT Core** — rule actions route device messages into Timestream.
- **Kinesis** (Data Streams / Managed Service for Apache Flink) — streaming ingestion.
- **Amazon Managed Grafana** — native data source for operational/IoT dashboards.
- **Amazon QuickSight** — BI and ad-hoc analytics.
- **SDK/API** — `WriteRecords` for direct ingestion; `Query` for SQL.

[⬆ Back to top](#table-of-contents)

---

## Rapid-Fire Facts

1. Fully managed, **serverless** time-series database.
2. Use cases: IoT telemetry, app/DevOps metrics, sensor + clickstream data.
3. Scales to **trillions of events per day**.
4. Up to **1/10th the cost** of relational DBs for time-series.
5. Up to **1000x faster** time-series queries than relational DBs.
6. **No instances** to choose or manage (LiveAnalytics).
7. **Standard SQL** with built-in time-series analytics.
8. **Interpolation** and **smoothing** functions for trends/anomalies.
9. **Encrypted by default** (AWS-managed or customer-managed KMS key).
10. **Tiered storage**: memory store + magnetic store.
11. Memory store = recent, **latency-sensitive / point-in-time** queries.
12. Magnetic store = older, **analytical** queries, cost-optimized.
13. Data moves between tiers **automatically** per retention policy.
14. **Append-only**: no direct update or delete.
15. **Timestamp is a mandatory dimension** on every record.
16. Removal handled by **retention-policy expiry** (memory + magnetic).
17. Magnetic retention can be set up to **200 years**.
18. Two engines: **LiveAnalytics** (serverless) and **InfluxDB** (managed InfluxDB).
19. Ingest via **SDK/API, IoT Core, Kinesis**.
20. Visualize with **Managed Grafana** and **QuickSight**.
21. Query cost is based on **data scanned** — filter by time + dimensions.
22. **Scheduled queries** pre-aggregate to cut cost/latency.
23. Enable **magnetic store writes** to accept late-arriving data.
24. Dimensions = metadata/filters; measures = the values analyzed.

[⬆ Back to top](#table-of-contents)

---

## Exam Tips and Traps

- Time-series trigger ("IoT", "metrics over time", "time-stamped events at scale") → **Timestream**.
- **Serverless** for LiveAnalytics; **InfluxDB** flavor only when compatibility is required.
- **Append-only**; expire data via **magnetic-store retention**, not DML.
- **Two tiers**: memory (recent/point-in-time) vs magnetic (historical/analytical).
- **Cost** = data scanned → time-range + dimension filters + scheduled queries.
- **KMS CMK** for customer-managed encryption.
- Don't default to DynamoDB/RDS for time-range analytics at scale.

[⬆ Back to top](#table-of-contents)
