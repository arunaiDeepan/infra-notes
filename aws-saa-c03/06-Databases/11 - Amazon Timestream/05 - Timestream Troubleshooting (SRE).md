# Amazon Timestream Troubleshooting (SRE) - SAA-C03 Deep Dive

> SRE-style symptom → cause → fix → prevention for Timestream: rejected writes from late data, missing/expired data, runaway query cost, ingestion throttling, retention misconfiguration causing data loss, and timestamp/dimension errors.

See also: [01 - Timestream Intro & Core Concepts](01%20-%20Timestream%20Intro%20%26%20Core%20Concepts.md) · [02 - Timestream Architecture Deep Dive](02%20-%20Timestream%20Architecture%20Deep%20Dive.md) · [03 - Timestream Best Practices & Examples](03%20-%20Timestream%20Best%20Practices%20%26%20Examples.md) · [04 - Timestream Scenario Questions](04%20-%20Timestream%20Scenario%20Questions.md) · [06 - Timestream Important Facts & Cheat Sheet](06%20-%20Timestream%20Important%20Facts%20%26%20Cheat%20Sheet.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md)

---

## Table of Contents

- [Rejected Writes Late-Arriving Data](#rejected-writes-late-arriving-data)
- [Missing Data in Query Results](#missing-data-in-query-results)
- [High Query Cost](#high-query-cost)
- [Ingestion Throttling](#ingestion-throttling)
- [Retention Misconfiguration Causing Data Loss](#retention-misconfiguration-causing-data-loss)
- [Timestamp and Dimension Errors](#timestamp-and-dimension-errors)
- [Monitoring and Observability](#monitoring-and-observability)
- [Exam Tips and Traps](#exam-tips-and-traps)

---

## Rejected Writes Late-Arriving Data

- **Symptom:** `WriteRecords` returns rejected records; ingestion partially fails.
- **Cause:** Record **timestamp is older than the memory-store retention** window (late/out-of-order data), or a duplicate with a lower/equal version.
- **Fix:** Enable **magnetic store writes** on the table to accept late-arriving data directly into the magnetic tier; or increase memory-store retention; bump the record **version** for intended upserts.
- **Prevention:** Size memory retention to cover expected lateness; enable magnetic store writes for batch/backfill pipelines; monitor rejected-record reasons.

[⬆ Back to top](#table-of-contents)

---

## Missing Data in Query Results

- **Symptom:** A query returns fewer rows than expected, or older data "disappears."
- **Cause:** Data has **expired** (past magnetic-store retention), or the query's **time range** doesn't cover where the data now lives (it tiered to magnetic), or a too-narrow time predicate.
- **Fix:** Widen the **time-range predicate**; verify retention settings vs the data's age; confirm data wasn't expired.
- **Prevention:** Set magnetic-store retention to meet your longest reporting horizon; document retention windows; alert before retention boundaries.

> **Exam Tip:** "Old data is gone" is usually **retention expiry**, not a bug. Removal is by policy, not DML.

[⬆ Back to top](#table-of-contents)

---

## High Query Cost

- **Symptom:** Query bills spike; dashboards are expensive.
- **Cause:** Queries **scan the magnetic tier over wide time ranges**, use `SELECT *`, or lack dimension filters — query cost is based on **data scanned**.
- **Fix:** Add tight **`WHERE time BETWEEN ...`** predicates and **dimension filters**; select only needed columns; serve dashboards from **scheduled-query** pre-aggregated tables.
- **Prevention:** Pre-aggregate with scheduled queries; educate teams on scan-based pricing; review query patterns.

[⬆ Back to top](#table-of-contents)

---

## Ingestion Throttling

- **Symptom:** Throttling errors / `ThrottlingException` during high-volume writes.
- **Cause:** Write request rate or record size patterns exceed soft limits; many tiny single-measure records.
- **Fix:** **Batch** records per `WriteRecords` call; use **multi-measure records**; implement exponential backoff and retries; distribute writes.
- **Prevention:** Design for batching; consolidate measures; request service-quota increases where applicable; smooth bursty ingestion via Kinesis.

[⬆ Back to top](#table-of-contents)

---

## Retention Misconfiguration Causing Data Loss

- **Symptom:** Data deleted earlier than the business expected.
- **Cause:** **Magnetic-store retention set too low**, or memory retention too short so data ages out before being read.
- **Fix:** Increase magnetic-store retention to the required horizon (up to **200 years**); note that **shortening** retention deletes data that already exceeds the new window.
- **Prevention:** Treat retention changes as **destructive**; review before lowering; align retention with compliance and reporting needs.

> **Exam Tip:** Lowering magnetic retention can **immediately expire** data — review carefully.

[⬆ Back to top](#table-of-contents)

---

## Timestamp and Dimension Errors

- **Symptom:** Validation errors on write; records rejected for schema reasons.
- **Cause:** **Missing/invalid timestamp** (it is mandatory), wrong **time unit/precision**, mismatched **measure value type**, or inconsistent dimension naming.
- **Fix:** Ensure every record has a valid timestamp with the correct unit (e.g., milliseconds); match the declared **measure value type**; keep dimension names consistent.
- **Prevention:** Validate payloads at the producer; standardize timestamp units and schema across producers.

[⬆ Back to top](#table-of-contents)

---

## Monitoring and Observability

- **CloudWatch metrics** for write/query system errors and ingestion volume.
- **CloudTrail** for API-level auditing of management and data actions.
- Inspect **rejected-record reasons** returned by `WriteRecords`.
- Track query **bytes scanned** to manage cost.

[⬆ Back to top](#table-of-contents)

---

## Exam Tips and Traps

- **Rejected writes** = late data past memory retention → enable **magnetic store writes**.
- **Missing old data** = **retention expiry** or too-narrow time range, not a defect.
- **High query cost** = wide scans → add time/dimension filters, pre-aggregate.
- **Throttling** = batch + multi-measure + backoff.
- **Lowering retention is destructive** — can delete data immediately.
- **Timestamp is mandatory**; mismatched value types/units cause rejects.

[⬆ Back to top](#table-of-contents)
