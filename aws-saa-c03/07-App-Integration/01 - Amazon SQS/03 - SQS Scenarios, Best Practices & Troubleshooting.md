# Amazon SQS - Scenarios, Best Practices & SRE Troubleshooting (SAA-C03)

> Exam-style scenario drills + a production SRE troubleshooting playbook. If you can answer every scenario here without peeking, you own SQS for the exam.

See also: [01 - SQS Fundamentals & Deep Dive](01%20-%20SQS%20Fundamentals%20%26%20Deep%20Dive.md) · [02 - SQS Architecture & Examples](02%20-%20SQS%20Architecture%20%26%20Examples.md) · [03 - SNS Scenarios, Best Practices & Troubleshooting](03%20-%20SNS%20Scenarios%2C%20Best%20Practices%20%26%20Troubleshooting.md)

---

## Table of Contents

- [1. Scenario-Based Questions](#1-scenario-based-questions)
- [2. Best Practices](#2-best-practices)
- [3. Common Errors & Troubleshooting (SRE View)](#3-common-errors--troubleshooting-sre-view)
- [4. Key CloudWatch Metrics](#4-key-cloudwatch-metrics)
- [5. SQS vs SNS vs EventBridge vs Kinesis](#5-sqs-vs-sns-vs-eventbridge-vs-kinesis)
- [6. Rapid-Fire Facts](#6-rapid-fire-facts)

---

## 1. Scenario-Based Questions

**Q1.** An image site's processing service can't keep up with upload spikes, causing dropped uploads. Most cost-effective fix?
**A.** Put an **SQS queue** between the web tier and processing workers; scale workers on queue depth. Queue absorbs spikes; no uploads dropped.

---

**Q2.** Messages are being processed **twice**, causing duplicate charges. The queue is Standard. Two fixes?
**A.** (1) Make the consumer **idempotent**. (2) If a message reappears mid-processing, the **visibility timeout is too short** - raise it above max processing time or heartbeat with `ChangeMessageVisibility`. For guaranteed exactly-once, switch to a **FIFO** queue.

---

**Q3.** Order of operations matters - debits/credits must apply in sequence per account, but the system must still scale to millions of accounts.
**A.** **FIFO queue** with `MessageGroupId = accountId`. Order preserved per account; parallelism across accounts.

---

**Q4.** A single malformed message keeps failing and blocks throughput as it's retried endlessly.
**A.** Configure a **DLQ** with `maxReceiveCount` (e.g., 3). After 3 failed receives the poison message moves to the DLQ; inspect, fix, and **redrive**.

---

**Q5.** SQS costs are high due to thousands of empty `ReceiveMessage` responses per minute.
**A.** Enable **long polling** (`ReceiveMessageWaitTimeSeconds` 1-20) and **batch** up to 10 messages per call.

---

**Q6.** A Lambda function consuming an SQS queue intermittently reprocesses messages even though it succeeded.
**A.** The **queue visibility timeout is too low relative to Lambda timeout**. Set visibility timeout ≥ **6× the function timeout**. Use `ReportBatchItemFailures` so only genuinely failed messages are retried.

---

**Q7.** One event must trigger three independent pipelines, each resilient to the others being down.
**A.** **SNS fan-out to three SQS queues**. Each pipeline drains its own queue independently.

---

**Q8.** Messages can be up to 50 MB. How to send through SQS?
**A.** **SQS Extended Client**: store the body in **S3**, send an S3 pointer (256 KB limit otherwise).

---

**Q9.** Sensitive PII flows through the queue; compliance needs customer-managed keys and an audit trail of key usage.
**A.** **SSE-KMS** with a customer-managed CMK; KMS logs key usage to CloudTrail.

---

**Q10.** A spike of writes overwhelms RDS during flash sales.
**A.** Buffer writes in **SQS**; workers drain at a rate RDS can sustain (load leveling).

[⬆ Back to top](#table-of-contents)

---

## 2. Best Practices

| Area                          | Best Practice                                                                                                        |
| :---------------------------- | :------------------------------------------------------------------------------------------------------------------- |
| **Idempotency**               | Design consumers to tolerate duplicates (Standard is at-least-once). Use a dedup key/check.                          |
| **Visibility timeout**        | Set slightly above worst-case processing; heartbeat for long jobs.                                                   |
| **Long polling**              | Enable everywhere to cut cost and empty responses.                                                                   |
| **Batching**                  | Send/receive in batches of 10 to reduce request count and cost.                                                      |
| **DLQ**                       | Always configure one; set long retention (14 days) and alarm on `ApproximateNumberOfMessagesVisible > 0` on the DLQ. |
| **Delete after success only** | Never delete before the work is confirmed done.                                                                      |
| **Right queue type**          | Default to Standard; use FIFO only when order/dedup is required (lower throughput).                                  |
| **Encryption**                | SSE-SQS by default; SSE-KMS for compliance.                                                                          |
| **Least privilege**           | Scope IAM to specific queue ARNs and actions.                                                                        |
| **Scaling signal**            | Scale consumers on backlog-per-instance, not CPU.                                                                    |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Errors & Troubleshooting (SRE View)

| Symptom                                       | Likely Cause                                                    | Resolution                                                             |
| :-------------------------------------------- | :-------------------------------------------------------------- | :--------------------------------------------------------------------- |
| **Duplicate processing**                      | Visibility timeout < processing time; or Standard at-least-once | Increase timeout / heartbeat; make consumer idempotent; or FIFO        |
| **Messages "disappear" but aren't processed** | Consumer received then crashed before delete; reappear later    | Check consumer health/logs; ensure delete only after success           |
| **Queue depth climbing, never draining**      | Consumers down, under-scaled, or throttled; poison messages     | Check consumer health, scale out, inspect DLQ                          |
| **`ApproximateAgeOfOldestMessage` rising**    | Backlog growing faster than processing                          | Add consumers; check for stuck/poison messages                         |
| **All receives return empty**                 | Short polling sampling subset; or queue genuinely empty         | Enable long polling; verify producers are sending                      |
| **`AccessDenied` on SendMessage from SNS/S3** | Missing SQS **resource policy** allowing the service principal  | Add access policy granting `sqs:SendMessage` to the source ARN/service |
| **FIFO throughput throttling**                | Exceeding 300/3,000 msg/s                                       | Enable **high-throughput FIFO**; spread across more `MessageGroupId`s  |
| **Lambda reprocessing despite success**       | Visibility timeout too low vs function timeout                  | Set visibility ≥ 6× Lambda timeout                                     |
| **`KMS.ThrottlingException`**                 | SSE-KMS key request rate too high                               | Increase **data key reuse period**; request KMS quota increase         |
| **Messages lost after 4 days**                | Default 4-day retention expired                                 | Increase `MessageRetentionPeriod` (up to 14 days); scale consumers     |

**SRE first-response checklist when a queue backs up:**

1. Is `ApproximateNumberOfMessagesVisible` climbing? → consumers aren't keeping up.
2. Is `NumberOfMessagesDeleted` ~0 while `Received` is high? → consumers failing after receive (crashes/exceptions).
3. Is the DLQ filling? → poison messages; inspect a sample.
4. Check consumer logs, error rates, and downstream dependency (DB/API) latency.
5. Scale consumers and/or fix the failing dependency; redrive DLQ once fixed.

[⬆ Back to top](#table-of-contents)

---

## 4. Key CloudWatch Metrics

| Metric                                      | Tells You                                                  |
| :------------------------------------------ | :--------------------------------------------------------- |
| `ApproximateNumberOfMessagesVisible`        | Backlog waiting to be processed (scaling signal)           |
| `ApproximateNumberOfMessagesNotVisible`     | In-flight (received, not yet deleted)                      |
| `ApproximateAgeOfOldestMessage`             | How long the oldest message has waited (SLA/health signal) |
| `NumberOfMessagesSent / Received / Deleted` | Throughput and whether consumers complete work             |
| `NumberOfEmptyReceives`                     | High value → enable long polling                           |
| DLQ `ApproximateNumberOfMessagesVisible`    | Poison messages accumulating (alarm on > 0)                |

[⬆ Back to top](#table-of-contents)

---

## 5. SQS vs SNS vs EventBridge vs Kinesis

|               | **SQS**                    | **SNS**               | **EventBridge**                | **Kinesis Data Streams**        |
| :------------ | :------------------------- | :-------------------- | :----------------------------- | :------------------------------ |
| **Model**     | Queue (pull)               | Pub/Sub (push)        | Event bus + routing (push)     | Streaming (pull, shards)        |
| **Consumers** | One logical consumer group | Many subscribers      | Many rule targets              | Many, replay by position        |
| **Ordering**  | FIFO option                | FIFO topic option     | No                             | Per-shard                       |
| **Retention** | Up to 14 days              | None (transient)      | Archive/replay feature         | 1-365 days                      |
| **Replay**    | No (re-drive DLQ only)     | No                    | Yes (archive replay)           | Yes (by sequence number)        |
| **Best for**  | Decoupling, work queues    | Fan-out notifications | Routing/SaaS events, schedules | High-volume analytics/streaming |

[⬆ Back to top](#table-of-contents)

---

## 6. Rapid-Fire Facts

- Message size **256 KB**; retention **60 s - 14 days** (default 4 days).
- Visibility timeout default **30 s**, max **12 h**.
- Long poll wait max **20 s**; batch max **10** messages.
- Delay queue / per-message delay max **15 min**.
- FIFO needs **`.fifo`** suffix; dedup window **5 min**; ordering per `MessageGroupId`.
- DLQ type must **match** source (FIFO↔FIFO).
- Lambda + SQS: visibility timeout **≥ 6× function timeout**.
- Cross-account / service send → **SQS resource (access) policy**.
- Scale consumers on **queue depth / backlog per instance**, not CPU.

[⬆ Back to top](#table-of-contents)
