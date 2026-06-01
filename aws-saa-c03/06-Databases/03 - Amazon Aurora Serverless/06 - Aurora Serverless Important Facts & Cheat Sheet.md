# Aurora Serverless Important Facts & Cheat Sheet - SAA-C03 Deep Dive

> Last-minute, high-density recall sheet for Aurora Serverless: the **v1 vs v2 comparison**, **ACU ranges**, **auto-pause** facts, **Data API** facts, **capacity metrics**, and **15+ rapid-fire facts** for the exam.

See also: [01 - Aurora Serverless Intro & Core Concepts](01%20-%20Aurora%20Serverless%20Intro%20%26%20Core%20Concepts.md) · [02 - Aurora Serverless Architecture Deep Dive](02%20-%20Aurora%20Serverless%20Architecture%20Deep%20Dive.md) · [03 - Aurora Serverless Best Practices & Examples](03%20-%20Aurora%20Serverless%20Best%20Practices%20%26%20Examples.md) · [04 - Aurora Serverless Scenario Questions](04%20-%20Aurora%20Serverless%20Scenario%20Questions.md) · [05 - Aurora Serverless Troubleshooting (SRE)](05%20-%20Aurora%20Serverless%20Troubleshooting%20%28SRE%29.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md) · [01 - Aurora Intro & Core Concepts](01%20-%20Aurora%20Intro%20%26%20Core%20Concepts.md)

---

## Table of Contents

- [v1 vs v2 Comparison Table](#v1-vs-v2-comparison-table)
- [ACU Ranges & Scaling](#acu-ranges--scaling)
- [Auto-Pause Facts](#auto-pause-facts)
- [Data API Facts](#data-api-facts)
- [Capacity Metrics](#capacity-metrics)
- [Trigger-Phrase Map](#trigger-phrase-map)
- [Rapid-Fire Facts](#rapid-fire-facts)
- [Summary](#summary)

---

## v1 vs v2 Comparison Table

| Feature                    | Serverless v1                        | Serverless v2                   |
| :------------------------- | :----------------------------------- | :------------------------------ |
| **Status**                 | Legacy                               | Modern default                  |
| **Scaling**                | Coarse steps at scaling points       | Fine-grained 0.5-ACU, in place  |
| **Scaling speed**          | Seconds–minutes; can stall           | Near-instant                    |
| **Auto-pause to ~$0**      | **Yes**                              | No (v1-style pause unavailable) |
| **Cold start**             | Yes (on resume)                      | No                              |
| **Read replicas**          | No                                   | Yes                             |
| **Multi-AZ**               | No                                   | Yes                             |
| **Global Database**        | No                                   | Yes                             |
| **Blue/Green**             | No                                   | Yes                             |
| **RDS Proxy**              | Limited                              | Yes                             |
| **Mixed with provisioned** | No                                   | Yes                             |
| **Data API**               | Yes                                  | Yes (supported versions)        |
| **Engine versions**        | Older MySQL/PostgreSQL               | Current Aurora MySQL/PostgreSQL |
| **Best for**               | Intermittent dev/test, scale-to-zero | Variable/spiky production       |

[⬆ Back to top](#table-of-contents)

---

## ACU Ranges & Scaling

| Item             | Fact                                                                                |
| :--------------- | :---------------------------------------------------------------------------------- |
| **1 ACU**        | ≈ **2 GiB memory** + proportional CPU/network                                       |
| **v2 range**     | **0.5 → 256 ACU** (min can be **0** on supported engine versions)                   |
| **v2 increment** | **0.5 ACU**, applied **in place**, no failover, no endpoint change                  |
| **v1 range**     | Fixed steps (e.g. 1,2,4,8…256); min can be **0** (paused)                           |
| **v1 scaling**   | Doubles/halves at a **scaling point** (no blocking txn/locks/temp tables)           |
| **Set on v2**    | `serverlessv2_scaling_configuration` (min/max) + instance class **`db.serverless`** |
| **Set on v1**    | `engine_mode = "serverless"` + `scaling_configuration`                              |

[⬆ Back to top](#table-of-contents)

---

## Auto-Pause Facts

- **v1 only.** v2 has no auto-pause-to-zero model.
- Pauses compute to **0 ACU** after a configurable **inactivity timeout** (default ~5 minutes).
- While paused you pay **storage only** (and backups) - **$0 compute**.
- Next connection **resumes** with a **cold-start latency** (seconds to ~30s+).
- `timeout_action = ForceApplyCapacityChange` forces scaling at the timeout, **dropping blocking connections**.
- Ideal for **dev/test/QA**; **avoid for latency-sensitive production**.

[⬆ Back to top](#table-of-contents)

---

## Data API Facts

- Run SQL over **HTTPS** - no persistent connection, no driver, no VPC plumbing on the caller.
- Auth via **IAM**; DB credentials stored in **AWS Secrets Manager**.
- Solves **Lambda connection storms**; great for serverless callers.
- Originally for **v1**; later **supported on Serverless v2** (and provisioned) on supported Aurora versions.
- Has **request-size and throughput limits** → can throttle (**429**) at high TPS; for sustained high TPS use **RDS Proxy** + normal connections.
- Enable with `enable_http_endpoint` (v1) / supported-version flag (v2); includes a **Query Editor** in the console.

[⬆ Back to top](#table-of-contents)

---

## Capacity Metrics

| Metric                                   | Use                                              |
| :--------------------------------------- | :----------------------------------------------- |
| **ServerlessDatabaseCapacity**           | Current ACUs in use; watch for pinning at max    |
| **ACUUtilization**                       | % of max ACU used; sustained ~100% → raise max   |
| **CPUUtilization**                       | Scale-up driver; saturation = under-capacity     |
| **DatabaseConnections**                  | Connection pressure; storms → RDS Proxy/Data API |
| **FreeableMemory / BufferCacheHitRatio** | Low → min ACU too small (cache thrash)           |

[⬆ Back to top](#table-of-contents)

---

## Trigger-Phrase Map

| Phrase in Question                                 | Answer                                                            |
| :------------------------------------------------- | :---------------------------------------------------------------- |
| "Unpredictable / variable / spiky" relational      | **Serverless v2**                                                 |
| "Intermittent / idle dev-test, ~$0 when idle"      | **Serverless v1 auto-pause**                                      |
| "Lambda + SQL without managing connections"        | **Data API**                                                      |
| "Connection storm / too many connections"          | **RDS Proxy** (v2) / Data API                                     |
| "Serverless needs replicas / Multi-AZ / Global DB" | **v2 only**                                                       |
| "Steady high 24/7, cheapest"                       | **Provisioned + Reserved Instances**                              |
| "Hard cost ceiling"                                | **Set max ACU**                                                   |
| "Steady writes + bursty reads, low downtime"       | **Mixed cluster: provisioned writer + v2 readers**                |
| "Reach serverless DB from outside its VPC"         | **Data API** or **EC2/Lambda in the same VPC** (no public access) |

[⬆ Back to top](#table-of-contents)

---

## Rapid-Fire Facts

1. Aurora Serverless makes **compute** serverless; **storage is the same 6-copy/3-AZ Aurora volume** (durability unchanged).
2. **1 ACU ≈ 2 GiB memory**.
3. **v2 ACU range: 0.5–256**, scales in **0.5 increments**, **in place**, within seconds.
4. **v2** supports **read replicas, Multi-AZ, Global Database, Blue/Green, RDS Proxy** - **v1 does not**.
5. **Auto-pause to $0 is v1-only**; first query after pause has a **cold start**.
6. **v1 scales at scaling points**; long transactions/locks can **stall** scaling.
7. **Data API** = HTTPS SQL + **IAM** + **Secrets Manager**; avoids connection management.
8. Data API has **size/throughput limits**; high TPS → **RDS Proxy**.
9. **Min ACU** = idle cost floor and memory floor; too low → **cache thrash**.
10. **Max ACU** = cost ceiling and scale limit; too low → **throttling**.
11. Both are **relational** (MySQL/PostgreSQL-compatible) - **not** a NoSQL/DynamoDB substitute.
12. **v2 IaC**: `serverlessv2_scaling_configuration` + `db.serverless`; **v1 IaC**: `engine_mode = "serverless"` + `scaling_configuration`.
13. **Mixed clusters** (provisioned + serverless v2) are supported - great for migration.
14. For **steady high 24/7** load, **provisioned + Reserved Instances** is usually cheaper than serverless.
15. **v1→v2 is not an in-place toggle** - use snapshot/restore or Blue/Green; may need engine upgrade.
16. v2 **readers** can have their own ACU range and scale independently of the writer.
17. Encryption, IAM DB auth, backups, and **Performance Insights** work on serverless (v2 most fully).
18. **No public access** (unlike classic RDS) - connect via the **Data API** or **EC2/Lambda in the same VPC**.

[⬆ Back to top](#table-of-contents)

---

## Summary

| Concept      | Must-Know                                                |
| :----------- | :------------------------------------------------------- |
| **Default**  | v2 for new/variable workloads                            |
| **v1 niche** | Scale-to-zero auto-pause for dev/test                    |
| **ACU**      | ≈2 GiB; v2 = 0.5–256, fine-grained, in place             |
| **Data API** | HTTP SQL, IAM + Secrets Manager, beats connection storms |
| **Metrics**  | ServerlessDatabaseCapacity, ACUUtilization               |
| **Not for**  | Steady high 24/7 (use provisioned + RIs); NoSQL needs    |

[⬆ Back to top](#table-of-contents)
