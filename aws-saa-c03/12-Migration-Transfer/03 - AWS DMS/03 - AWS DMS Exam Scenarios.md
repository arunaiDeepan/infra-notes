# AWS Database Migration Service (DMS) - Exam Scenarios

> Exam focus: recognise _database migration with minimal downtime (full load + CDC)_, _heterogeneous → SCT + DMS_, special targets (S3/Redshift/Kinesis/DynamoDB), Multi-AZ/Serverless, and DMS vs MGN/DataSync. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - AWS DMS Intro bits & bytes](01%20-%20AWS%20DMS%20Intro%20bits%20%26%20bytes.md) · [02 - AWS DMS Deep Dive](02%20-%20AWS%20DMS%20Deep%20Dive.md) · [04 - AWS DMS SRE Operations](04%20-%20AWS%20DMS%20SRE%20Operations.md) · [00 - Migration & Transfer Overview](00%20-%20Migration%20%26%20Transfer%20Overview.md)

---

## Table of Contents

- [1. Frequently Tested Concepts](#1-frequently-tested-concepts)
- [2. Keywords AWS Uses](#2-keywords-aws-uses)
- [3. Common Distractors](#3-common-distractors)
- [4. Elimination Technique](#4-elimination-technique)
- [5. Medium Scenario Questions (1-20)](#5-medium-scenario-questions-1-20)
- [6. Hard Scenario Questions (1-10)](#6-hard-scenario-questions-1-10)
- [7. One-Line Recap](#7-one-line-recap)

---

## 1. Frequently Tested Concepts

- **Minimal-downtime DB migration** → **full load + CDC**.
- **Heterogeneous** (engine change) → **SCT** (schema/code) + **DMS** (data).
- **Homogeneous** → DMS alone.
- **Continuous replication** → CDC only (DR, analytics feed, consolidation).
- **Special targets**: S3 (data lake), Redshift, Kinesis/MSK, DynamoDB, OpenSearch.
- **Multi-AZ** replication instance for resilience; **Serverless** for variable load.
- Enable source logging (binlog/WAL/supplemental) for CDC.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                                      | Points to                         |
| :---------------------------------------------------------- | :-------------------------------- |
| "migrate database with minimal/near-zero downtime"          | **DMS full load + CDC**           |
| "different/heterogeneous database engine"                   | **SCT + DMS**                     |
| "same engine"                                               | **DMS alone**                     |
| "keep replicating / ongoing sync between DBs"               | **DMS CDC only**                  |
| "feed operational data to a data lake / Redshift / Kinesis" | **DMS to S3/Redshift/Kinesis**    |
| "resilient long-running replication"                        | **Multi-AZ replication instance** |
| "auto-scale replication, no instance to manage"             | **DMS Serverless**                |
| "assessment of conversion effort"                           | **SCT assessment report**         |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Forgetting **SCT** for **heterogeneous** migrations (DMS moves data, not schema across engines).
- Choosing **MGN** for a database migration (MGN = servers).
- Choosing **DataSync** for a database (DataSync = files/objects).
- Single-AZ for **long-running production** replication (use Multi-AZ).
- Forgetting **CDC prerequisites** (binlog/WAL/supplemental logging).
- Ignoring **data validation** before cutover.

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **It's a database?** → DMS (else MGN/DataSync).
2. **Engine change?** → add **SCT**.
3. **Minimal downtime?** → **full load + CDC**.
4. **Ongoing replication only?** → **CDC only**.
5. **Target is analytics/stream/NoSQL?** → DMS special target (S3/Redshift/Kinesis/DynamoDB).
6. **Long-running/production?** → **Multi-AZ** (or Serverless for variable load).

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** Migrate on-prem MySQL to Aurora MySQL with minimal downtime.
**Options:** A) MGN B) DMS full load + CDC C) DataSync D) Snowball
**Correct:** B
**Explanation:** Same-engine DB, minimal downtime → DMS (no SCT needed).

### Q2

**Scenario:** Migrate Oracle to Aurora PostgreSQL (different engine).
**Options:** A) DMS alone B) SCT to convert schema/code + DMS for data C) DataSync D) MGN
**Correct:** B
**Explanation:** Heterogeneous → SCT + DMS.

### Q3

**Scenario:** What keeps downtime minimal?
**Options:** A) Full load only B) Full load + CDC (continuous changes) C) Manual dump D) Stop the DB
**Correct:** B
**Explanation:** CDC keeps target current until cutover.

### Q4

**Scenario:** Continuously replicate a production DB to a reporting copy.
**Options:** A) Full load only B) DMS CDC C) DataSync D) Snowball
**Correct:** B
**Explanation:** Ongoing replication → CDC.

### Q5

**Scenario:** Feed CDC changes from RDS into a Kinesis stream for real-time analytics.
**Options:** A) Not possible B) DMS with Kinesis target C) DataSync D) MGN
**Correct:** B
**Explanation:** DMS supports streaming targets (Kinesis/MSK).

### Q6

**Scenario:** Land operational data as Parquet in a data lake.
**Options:** A) DMS to S3 target B) MGN C) DataSync DB D) Snowball
**Correct:** A
**Explanation:** DMS can write to S3 (e.g., Parquet).

### Q7

**Scenario:** Long-running replication must survive an AZ failure.
**Options:** A) Single-AZ B) Multi-AZ replication instance C) Bigger storage D) Two tasks
**Correct:** B
**Explanation:** Multi-AZ provides standby + failover.

### Q8

**Scenario:** Variable, unpredictable replication load; no desire to size instances.
**Options:** A) Largest instance B) DMS Serverless C) Single-AZ small D) Snowball
**Correct:** B
**Explanation:** Serverless auto-scales capacity.

### Q9

**Scenario:** Estimate how hard converting an Oracle schema to PostgreSQL will be.
**Options:** A) Guess B) SCT assessment report C) CloudWatch D) Trusted Advisor
**Correct:** B
**Explanation:** SCT produces an assessment with complexity ratings.

### Q10

**Scenario:** CDC isn't capturing changes from MySQL.
**Options:** A) Bigger instance B) Enable binary logging (binlog) on the source C) New endpoint D) DataSync
**Correct:** B
**Explanation:** CDC needs source logging (binlog/WAL/supplemental).

### Q11

**Scenario:** Verify the target matches the source before cutover.
**Options:** A) Trust it B) Enable DMS data validation C) Manual counts only D) None
**Correct:** B
**Explanation:** DMS data validation compares rows and reports mismatches.

### Q12

**Scenario:** Store DB credentials securely for endpoints.
**Options:** A) Hardcode B) Secrets Manager referenced by the endpoint C) Plaintext file D) Env var on laptop
**Correct:** B
**Explanation:** Endpoints can pull credentials from Secrets Manager.

### Q13

**Scenario:** Encrypt migrated data at rest on the target.
**Options:** A) None B) KMS encryption on target C) Only SSL D) Client app
**Correct:** B
**Explanation:** KMS for at-rest; SSL for in-transit.

### Q14

**Scenario:** Reach an on-prem source privately for migration.
**Options:** A) Public DB B) Direct Connect/VPN to the replication instance's VPC C) Email dumps D) Snowball only
**Correct:** B
**Explanation:** Private connectivity to reach on-prem.

### Q15

**Scenario:** Migrate only specific tables and rename a schema in flight.
**Options:** A) All tables B) Table mappings + transformations C) New DB D) Manual
**Correct:** B
**Explanation:** Selection/transformation rules in the task.

### Q16

**Scenario:** Large BLOB columns are slowing the migration.
**Options:** A) Ignore B) Tune LOB mode (limited/full/inline) C) Drop the table D) Bigger bucket
**Correct:** B
**Explanation:** LOB handling mode is a key performance lever.

### Q17

**Scenario:** Which three migration types does DMS offer?
**Options:** A) Hot/Warm/Cold B) Full load / Full load + CDC / CDC only C) Push/Pull/Sync D) Online/Offline/Hybrid
**Correct:** B
**Explanation:** The standard DMS migration types.

### Q18

**Scenario:** Migrate MongoDB to DynamoDB.
**Options:** A) Not supported B) DMS (MongoDB source → DynamoDB target) C) DataSync D) MGN
**Correct:** B
**Explanation:** DMS supports NoSQL source/target combos.

### Q19

**Scenario:** Reduce DMS cost after cutover.
**Options:** A) Keep instance running B) Decommission the replication instance (or use Serverless) C) Upsize D) Multi-AZ forever
**Correct:** B
**Explanation:** Stop paying for the instance once migration completes.

### Q20

**Scenario:** Migrate whole application servers, not just the DB.
**Options:** A) DMS B) MGN (servers) C) DataSync D) SCT
**Correct:** B
**Explanation:** Servers → MGN; DMS is database-only.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** A bank must migrate a 10 TB Oracle OLTP to Aurora PostgreSQL with near-zero downtime, validated, and resilient to an AZ failure during the multi-week migration.
**Options:** A) Dump/restore B) **SCT** to convert schema/code → **DMS full load + CDC** on a **Multi-AZ** instance with **data validation**; cut over at CDC≈0 C) MGN D) DataSync
**Correct:** B
**Explanation:** Heterogeneous (SCT) + minimal downtime (CDC) + resilience (Multi-AZ) + confidence (validation).

### H2

**Scenario:** The source DB is on-prem with a slow link and 8 TB of history; ongoing changes are modest. They want to avoid weeks of online full load.
**Options:** A) Online full load over the slow link B) Seed the initial data via **Snowball/DataSync to the target**, then run **DMS CDC-only** to apply ongoing changes online C) Snowball only D) MGN
**Correct:** B
**Explanation:** Offline-seed the bulk, then catch up with CDC online - a documented hybrid pattern.

### H3

**Scenario:** Real-time analytics need every change from an operational MySQL reflected into Redshift and a data-lake (S3) simultaneously.
**Options:** A) Nightly ETL B) **DMS CDC** to **Redshift** and to **S3** targets (and/or Kinesis) for streaming analytics C) DataSync D) Manual exports
**Correct:** B
**Explanation:** DMS streams CDC to analytics targets continuously.

### H4

**Scenario:** Heterogeneous migration shows many stored procedures SCT can't auto-convert.
**Options:** A) Abandon B) Use the **SCT assessment report** to scope manual rewrites; convert what auto-converts, rewrite the rest, then DMS the data C) DMS alone D) MGN
**Correct:** B
**Explanation:** SCT flags manual items; plan the rework, then migrate data.

### H5

**Scenario:** CDC latency keeps climbing under peak write load, threatening the cutover window.
**Options:** A) Ignore B) Scale up the replication instance / use **Serverless**, tune **parallel apply** and LOB mode, ensure target isn't the bottleneck C) Stop CDC D) Smaller storage
**Correct:** B
**Explanation:** Right-size compute and tune task/target to keep CDC latency low.

### H6

**Scenario:** Security mandates no public exposure, credentials never in config, and encryption end to end.
**Options:** A) Public endpoints B) Replication instance in **private subnets** + **DX/VPN**, **Secrets Manager** credentials, **SSL** endpoints, **KMS** at rest C) Plaintext creds D) Internet + no SSL
**Correct:** B
**Explanation:** Private networking + Secrets Manager + SSL + KMS covers all mandates.

### H7

**Scenario:** Post-migration validation shows row mismatches on a few tables.
**Options:** A) Ship anyway B) Use DMS **data validation** + **table statistics** to pinpoint tables; investigate transformations/LOB truncation; re-migrate affected tables C) Delete tables D) Ignore
**Correct:** B
**Explanation:** Validation/stats localise the issue (often LOB/limited-LOB or filters) for targeted re-migration.

### H8

**Scenario:** A consolidation merges 12 regional MySQL DBs into one Aurora cluster with minimal downtime.
**Options:** A) One giant dump B) Multiple **DMS tasks** (one per source) with **table mappings**/schema prefixes into the consolidated target, full load + CDC, validate, cut over per source C) MGN D) DataSync
**Correct:** B
**Explanation:** Parallel tasks with mappings consolidate sources with minimal downtime.

### H9

**Scenario:** They want continuous DR replication of a primary DB to another region indefinitely.
**Options:** A) One-time full load B) **DMS CDC-only** cross-region (or native engine replication) on a **Multi-AZ** instance, monitored on latency C) DataSync D) Snowball
**Correct:** B
**Explanation:** Ongoing cross-region replication via CDC (Multi-AZ for resilience).

### H10

**Scenario:** Costs spiked because a one-time migration's replication instance was left running for months.
**Options:** A) Bigger instance B) **Decommission** the instance after cutover; for variable/ongoing needs use **Serverless**; alarm on idle replication instances C) Multi-AZ always D) Ignore
**Correct:** B
**Explanation:** Idle replication instances bill continuously - decommission or go Serverless.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Migrate/replicate databases with minimal downtime → DMS (full load + CDC). Different engine → SCT (schema/code) + DMS (data). Ongoing sync → CDC only. Analytics/stream targets → DMS to S3/Redshift/Kinesis/DynamoDB. Resilient long-running → Multi-AZ; variable load → Serverless. Servers → MGN, files → DataSync.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - AWS DMS SRE Operations](04%20-%20AWS%20DMS%20SRE%20Operations.md).
