# Amazon Timestream Scenario Questions - SAA-C03 Deep Dive

> Seven exam-style scenarios that drill the time-series trigger: choosing Timestream over RDS/DynamoDB/Redshift, auto-expiring old data with retention, and recognizing the InfluxDB-compatibility case.

See also: [01 - Timestream Intro & Core Concepts](01%20-%20Timestream%20Intro%20%26%20Core%20Concepts.md) · [02 - Timestream Architecture Deep Dive](02%20-%20Timestream%20Architecture%20Deep%20Dive.md) · [03 - Timestream Best Practices & Examples](03%20-%20Timestream%20Best%20Practices%20%26%20Examples.md) · [05 - Timestream Troubleshooting (SRE)](05%20-%20Timestream%20Troubleshooting%20%28SRE%29.md) · [06 - Timestream Important Facts & Cheat Sheet](06%20-%20Timestream%20Important%20Facts%20%26%20Cheat%20Sheet.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md)

---

## Table of Contents

- [Scenario 1 Massive IoT Sensor Data Over Time](#scenario-1-massive-iot-sensor-data-over-time)
- [Scenario 2 DevOps and Application Metrics Analytics](#scenario-2-devops-and-application-metrics-analytics)
- [Scenario 3 Cheaper and Faster Than RDS for Time-Series](#scenario-3-cheaper-and-faster-than-rds-for-time-series)
- [Scenario 4 Auto-Expire Old Data](#scenario-4-auto-expire-old-data)
- [Scenario 5 DynamoDB vs Timestream Trap](#scenario-5-dynamodb-vs-timestream-trap)
- [Scenario 6 InfluxDB Compatibility Required](#scenario-6-influxdb-compatibility-required)
- [Scenario 7 Recent vs Historical Query Tiers](#scenario-7-recent-vs-historical-query-tiers)
- [Exam Tips and Traps](#exam-tips-and-traps)

---

## Scenario 1 Massive IoT Sensor Data Over Time

**Scenario:** A manufacturer collects readings from millions of IoT sensors, generating billions of time-stamped data points daily. They need to store and run time-range analytics with minimal operational overhead.

**Answer:** **Amazon Timestream (LiveAnalytics).** It is a serverless time-series database that scales to trillions of events/day and runs SQL time-series analytics.

**Why not others:** RDS/Aurora can't economically scale to this volume; DynamoDB lacks built-in time-series analytics; Redshift is a warehouse, not an ingest-optimized time-series store.

> **Exam Tip:** "Millions of sensors" + "time-stamped" + "minimal ops" = Timestream.

[⬆ Back to top](#table-of-contents)

---

## Scenario 2 DevOps and Application Metrics Analytics

**Scenario:** A SaaS team wants to store CPU/latency/error metrics from thousands of microservices and query trends, anomalies, and moving averages over time.

**Answer:** **Amazon Timestream**, using its built-in **interpolation/smoothing** functions and **scheduled queries** for rollups, visualized in **Managed Grafana**.

**Why:** Purpose-built for high-volume metrics with native time-series analytics in SQL.

[⬆ Back to top](#table-of-contents)

---

## Scenario 3 Cheaper and Faster Than RDS for Time-Series

**Scenario:** A company stores time-series telemetry in a relational database but faces high cost and slow time-windowed queries. They want a managed, lower-cost, faster solution.

**Answer:** Migrate to **Amazon Timestream** — up to **1/10th the cost** and **1000x faster** for time-series queries, fully managed.

**Why not:** Scaling up the RDS instance only raises cost; the workload is fundamentally time-series.

[⬆ Back to top](#table-of-contents)

---

## Scenario 4 Auto-Expire Old Data

**Scenario:** Telemetry must be kept hot for 24 hours and retained for 1 year, then automatically deleted. The team wants no custom cleanup jobs.

**Answer:** Use Timestream **retention policies** — set **memory-store retention = 24 hours** and **magnetic-store retention = 1 year**. Data tiers and **expires automatically**.

**Why not:** A Lambda/cron deletion job is unnecessary operational overhead; Timestream handles lifecycle natively.

> **Exam Tip:** "Automatically delete old data after N days/years" = magnetic-store retention setting.

[⬆ Back to top](#table-of-contents)

---

## Scenario 5 DynamoDB vs Timestream Trap

**Scenario:** A solutions architect proposes DynamoDB with a `device_id` partition key and timestamp sort key for IoT analytics needing trend/aggregation queries over arbitrary time ranges across all devices.

**Answer:** **Amazon Timestream** is the better fit. DynamoDB excels at known-key lookups but is poor for **ad-hoc time-range analytics across many devices** and has no built-in time-series functions.

**Trap:** NoSQL ≠ automatically right for IoT. The **analytics-over-time** requirement points to Timestream.

[⬆ Back to top](#table-of-contents)

---

## Scenario 6 InfluxDB Compatibility Required

**Scenario:** A team runs an existing application built on **InfluxDB** (InfluxQL/Flux) needing single-digit-millisecond queries and wants a managed AWS service without rewriting the app.

**Answer:** **Amazon Timestream for InfluxDB** — managed InfluxDB compatible with existing InfluxDB tooling and low-latency point queries.

**Why not LiveAnalytics:** It uses SQL, not InfluxQL/Flux; choosing it would require an app rewrite.

> **Exam Tip:** Explicit **InfluxDB** mention = Timestream for InfluxDB. Otherwise LiveAnalytics.

[⬆ Back to top](#table-of-contents)

---

## Scenario 7 Recent vs Historical Query Tiers

**Scenario:** Operators need millisecond lookups of the **latest** sensor value, while analysts run **monthly** trend reports over a year of history. Costs must stay low.

**Answer:** One Timestream table: keep a modest **memory-store retention** for fast recent/point-in-time queries, and a long **magnetic-store retention** for cheap historical analytics. The engine federates queries across both tiers automatically.

**Why:** Tiered storage serves both access patterns without separate databases.

[⬆ Back to top](#table-of-contents)

---

## Exam Tips and Traps

- Time-series trigger words → **Timestream**.
- "Auto-delete old data" → **magnetic-store retention**.
- "Cheaper/faster than RDS for time-series" → **Timestream**.
- NoSQL is **not** automatically right — analytics-over-time → Timestream, not DynamoDB.
- **InfluxDB** keyword → Timestream **for InfluxDB**.
- Recent (memory) vs historical (magnetic) tiers handle mixed access patterns in one table.

[⬆ Back to top](#table-of-contents)
