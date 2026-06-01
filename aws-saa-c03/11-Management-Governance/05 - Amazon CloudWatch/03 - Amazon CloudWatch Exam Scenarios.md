# Amazon CloudWatch - Exam Scenarios

> Exam focus: agent for memory/disk, detailed monitoring, EC2 recover, metric filters on logs, alarm actions, log retention cost, and the CloudWatch/CloudTrail/Config split. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - Amazon CloudWatch Intro bits & bytes](01%20-%20Amazon%20CloudWatch%20Intro%20bits%20%26%20bytes.md) · [02 - Amazon CloudWatch Deep Dive](02%20-%20Amazon%20CloudWatch%20Deep%20Dive.md) · [04 - Amazon CloudWatch SRE Operations](04%20-%20Amazon%20CloudWatch%20SRE%20Operations.md) · [01 - AWS CloudTrail Intro bits & bytes](01%20-%20AWS%20CloudTrail%20Intro%20bits%20%26%20bytes.md)

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

- **Memory/disk metrics → CloudWatch Agent** (not default).
- **Basic 5-min vs detailed 1-min** monitoring.
- **EC2 `recover` alarm** for hardware failure keeping ID/IP.
- **Metric filter on logs → alarm** (e.g. error counts, root login).
- **Alarm actions**: SNS, Auto Scaling, EC2, SSM.
- **Log retention** defaults to never-expire (cost trap); archive to S3.
- **Subscription filters** for real-time log streaming/centralization.
- **Cross-account observability** monitoring account.
- CloudWatch vs CloudTrail vs Config.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                             | Points to                                                |
| :------------------------------------------------- | :------------------------------------------------------- |
| "memory / RAM / disk space utilization"            | **CloudWatch Agent**                                     |
| "1-minute granularity"                             | **Detailed monitoring**                                  |
| "recover the instance automatically, keep same IP" | **EC2 recover alarm**                                    |
| "alert when ERROR appears in logs"                 | **Metric filter + alarm**                                |
| "notify on-call when CPU high"                     | **Alarm → SNS**                                          |
| "scale out when..."                                | **Alarm → Auto Scaling**                                 |
| "logs cost keeps growing"                          | **Set log retention / archive to S3**                    |
| "stream logs to OpenSearch/S3 in real time"        | **Subscription filter (Firehose)**                       |
| "one dashboard across accounts/regions"            | **Cross-account observability / cross-region dashboard** |
| "trace request across microservices"               | **X-Ray / Application Signals** (not CloudWatch metrics) |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Expecting memory/disk by default (needs agent).
- Choosing CloudTrail/Config for health/performance.
- Using an alarm where **EventBridge** (event-driven/schedule) is correct, or vice versa.
- Forgetting **log retention** in cost questions.
- Streaming **all** logs to CloudWatch when a metric filter suffices.
- Picking `terminate` when `recover` is meant.

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **Health/performance/metric/alarm** → CloudWatch. **Who-did-what** → CloudTrail. **Config/compliance** → Config.
2. **OS-level metric** (mem/disk) → agent required.
3. **"Recover single instance, same identity"** → EC2 recover action.
4. **Pattern in logs** → metric filter + alarm.
5. **Cost + logs** → retention + S3 archive.
6. **Real-time event reaction/schedule** → EventBridge, not an alarm.

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** EC2 memory utilization isn't visible in CloudWatch.
**Options:** A) Enable detailed monitoring B) Install the CloudWatch Agent C) Use CloudTrail D) Use Config
**Correct:** B
**Explanation:** Memory is a guest-OS metric; the agent publishes it.

### Q2

**Scenario:** Need 1-minute EC2 metrics instead of 5-minute.
**Options:** A) CloudWatch Agent B) Enable detailed monitoring C) Custom metric D) X-Ray
**Correct:** B
**Explanation:** Detailed monitoring gives 1-minute native metrics.

### Q3

**Scenario:** Automatically recover a single instance after host hardware failure, keeping its private IP.
**Options:** A) Terminate action B) Recover action alarm C) Auto Scaling D) Reboot
**Correct:** B
**Explanation:** The `recover` action rebuilds on healthy hardware keeping ID/IP.

### Q4

**Scenario:** Alarm when "ERROR" appears more than 5 times/min in app logs.
**Options:** A) Logs Insights schedule B) Metric filter + alarm C) Config rule D) CloudTrail
**Correct:** B
**Explanation:** Metric filter turns the pattern into a metric to alarm on.

### Q5

**Scenario:** Scale out a fleet when average CPU exceeds 70%.
**Options:** A) EventBridge B) CloudWatch alarm → Auto Scaling policy (or target tracking) C) Lambda cron D) Config
**Correct:** B
**Explanation:** Alarms drive Auto Scaling.

### Q6

**Scenario:** CloudWatch Logs bill grows every month.
**Options:** A) Delete account B) Set log group retention + archive old logs to S3 C) More log groups D) Disable logging
**Correct:** B
**Explanation:** Default never-expire retention is the cause.

### Q7

**Scenario:** Stream application logs to OpenSearch in near-real-time.
**Options:** A) Manual export B) Subscription filter → Firehose → OpenSearch C) Metric filter D) Dashboard
**Correct:** B
**Explanation:** Subscription filters provide real-time delivery.

### Q8

**Scenario:** Notify on-call when an alarm triggers.
**Options:** A) Email log group B) Alarm action → SNS topic C) Config D) Dashboard
**Correct:** B
**Explanation:** SNS is the standard alarm notification target.

### Q9

**Scenario:** One operations dashboard spanning 3 regions.
**Options:** A) Three consoles B) Cross-region CloudWatch dashboard C) Config D) CloudTrail
**Correct:** B
**Explanation:** Dashboards can render multi-region metrics.

### Q10

**Scenario:** Reduce alarm noise: only page when DB is down AND app errors spike.
**Options:** A) Two SNS topics B) Composite alarm (AND) C) Anomaly detection D) More periods
**Correct:** B
**Explanation:** Composite alarms combine conditions logically.

### Q11

**Scenario:** Seasonal metric makes static thresholds noisy.
**Options:** A) Higher threshold B) Anomaly detection band C) Disable alarm D) Longer period
**Correct:** B
**Explanation:** Anomaly detection learns the normal band.

### Q12

**Scenario:** Run a Lambda every hour on a schedule.
**Options:** A) CloudWatch alarm B) EventBridge scheduled rule (rate/cron) C) Metric filter D) Canary
**Correct:** B
**Explanation:** EventBridge schedules; alarms watch metrics.

### Q13

**Scenario:** Proactively detect a public-facing API is down before customers do.
**Options:** A) Metric filter B) CloudWatch Synthetics canary C) Config D) CloudTrail
**Correct:** B
**Explanation:** Canaries probe endpoints externally on a schedule.

### Q14

**Scenario:** Centralize metrics/logs from 20 accounts into one viewing account.
**Options:** A) Copy data B) CloudWatch cross-account observability (monitoring account) C) Per-account dashboards D) Athena
**Correct:** B
**Explanation:** Cross-account observability links source accounts to a monitoring account.

### Q15

**Scenario:** Avoid alarm flapping on brief spikes.
**Options:** A) Lower threshold B) Use M datapoints of N evaluation periods C) Delete alarm D) Higher resolution
**Correct:** B
**Explanation:** M-of-N requires sustained breach.

### Q16

**Scenario:** Monitor ECS/EKS container-level metrics and logs.
**Options:** A) Basic monitoring B) Container Insights C) X-Ray D) Config
**Correct:** B
**Explanation:** Container Insights is purpose-built for clusters.

### Q17

**Scenario:** App needs a custom business metric (orders/min) in CloudWatch.
**Options:** A) Detailed monitoring B) PutMetricData custom metric (or agent/EMF) C) CloudTrail D) Config
**Correct:** B
**Explanation:** Publish custom metrics via the API/agent/Embedded Metric Format.

### Q18

**Scenario:** Identify top contributors (e.g. heaviest callers) from logs.
**Options:** A) Metric filter B) Contributor Insights C) Dashboard D) Config
**Correct:** B
**Explanation:** Contributor Insights surfaces top-N from log data.

### Q19

**Scenario:** Alarm should treat missing data as not breaching for a batch job that sleeps.
**Options:** A) breaching B) Treat missing data = notBreaching C) ignore only D) Delete alarm
**Correct:** B
**Explanation:** Configure missing-data handling appropriately.

### Q20

**Scenario:** Encrypt sensitive logs at rest with a customer-managed key.
**Options:** A) Not possible B) Associate a KMS key with the log group C) S3 only D) Client only
**Correct:** B
**Explanation:** CloudWatch Logs supports KMS encryption per log group.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** A fleet behind an ALB must scale on _requests per target_ and also page humans if error rate (5xx/total) exceeds 2% for 5 minutes.
**Options:** A) CPU alarm only B) Target tracking on RequestCountPerTarget for scaling + a **metric-math** alarm (5xx/requests) → SNS for paging C) Config D) Canary only
**Correct:** B
**Explanation:** Scaling and alerting are separate concerns: target tracking for capacity, metric-math alarm for the SLO breach.

### H2

**Scenario:** A single legacy stateful instance must auto-recover from underlying hardware failure without changing its IP or requiring re-registration, but must NOT be replaced by a new instance.
**Options:** A) Auto Scaling group of 1 B) CloudWatch **recover** action alarm on StatusCheckFailed*System C) Terminate action D) Reboot action
**Correct:** B
**Explanation:** `recover` rebuilds on new hardware keeping identity; an ASG would launch a \_new* instance (new identity), unsuitable here.

### H3

**Scenario:** Security wants near-real-time alerting on root logins and CloudTrail StopLogging across the org, centrally.
**Options:** A) Daily report B) Org CloudTrail → CloudWatch Logs in a security account → **metric filters + alarms** (root login, StopLogging) → SNS; or EventBridge rules C) Config D) Manual
**Correct:** B
**Explanation:** Metric filters on the CloudTrail log stream feed alarms; EventBridge is an alternative real-time path. Central security account aggregates.

### H4

**Scenario:** Logs cost is dominated by verbose debug logging from thousands of Lambdas, but you still need errors searchable for 1 year.
**Options:** A) Keep everything 1y B) Lower log level; set short retention on noisy groups; **subscription filter** errors to S3/OpenSearch for 1-year searchable archive; sample debug C) Disable logging D) Infinite retention
**Correct:** B
**Explanation:** Separate cheap short-retention operational logs from a curated, longer-retention error archive; cut volume at the source.

### H5

**Scenario:** A team needs SLO-style latency p99 and an automatic service map across microservices.
**Options:** A) CPU metrics B) **Application Signals** (APM) with OpenTelemetry + SLO tracking; X-Ray for traces C) Metric filters D) Dashboards only
**Correct:** B
**Explanation:** Latency percentiles, service maps, and SLOs are APM territory (Application Signals/X-Ray), not basic infra metrics.

### H6

**Scenario:** Alarms flap during deploys when instances briefly report no data, paging the team needlessly.
**Options:** A) Delete alarms during deploy manually B) Set **treat-missing-data** appropriately + M-of-N datapoints + composite alarms gated on deploy state C) Higher threshold D) Longer period only
**Correct:** B
**Explanation:** Missing-data handling + M-of-N + composite gating eliminates deploy-time false pages.

### H7

**Scenario:** A monitoring account must view metrics, logs, and traces from 50 source accounts without duplicating storage, governed by Organizations.
**Options:** A) Export data nightly B) **CloudWatch cross-account observability**: link source accounts to the monitoring account via Organizations C) One mega account D) Separate dashboards
**Correct:** B
**Explanation:** Cross-account observability provides a single pane over source-account telemetry without copying it.

### H8

**Scenario:** A custom high-cardinality metric (per-customer) is exploding CloudWatch metric costs.
**Options:** A) Keep as metrics B) Use **Embedded Metric Format**/Contributor Insights or log-based analytics instead of millions of distinct metric dimensions; aggregate C) High-resolution D) More dashboards
**Correct:** B
**Explanation:** High-cardinality dimensions multiply metric cost; use logs/EMF/Contributor Insights for per-entity analysis.

### H9

**Scenario:** A batch pipeline must trigger remediation automation when a specific resource configuration event occurs, not on a metric threshold.
**Options:** A) CloudWatch alarm B) **EventBridge** rule on the event (from CloudTrail/Config) → SSM Automation/Lambda C) Metric filter D) Canary
**Correct:** B
**Explanation:** Event-driven (not threshold) → EventBridge to automation, distinct from metric alarms.

### H10

**Scenario:** A regulated workload requires logs encrypted with a key the app team cannot decrypt, retained 7 years immutably, yet operationally searchable for 30 days.
**Options:** A) One log group forever B) 30-day retention in CloudWatch Logs (KMS key controlled by security) for operations + **export/subscription to S3** with Object Lock + lifecycle to Glacier for 7-year immutable archive C) Infinite CW retention D) No encryption
**Correct:** B
**Explanation:** Tiered: short searchable retention in Logs; immutable long-term archive in S3 (Object Lock); key authority separated from the app team.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Health/metrics/alarms → CloudWatch. Memory/disk → agent. 1-min → detailed monitoring. Recover single instance → EC2 recover. Log pattern → metric filter + alarm. Real-time log stream → subscription filter. Cost → set retention + archive to S3. Event/schedule → EventBridge. Trace → X-Ray/App Signals.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - Amazon CloudWatch SRE Operations](04%20-%20Amazon%20CloudWatch%20SRE%20Operations.md).
