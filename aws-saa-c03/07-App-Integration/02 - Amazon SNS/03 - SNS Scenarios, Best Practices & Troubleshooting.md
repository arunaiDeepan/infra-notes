# Amazon SNS - Scenarios, Best Practices & SRE Troubleshooting (SAA-C03)

> Scenario drills + production troubleshooting for SNS. Pairs with the SQS troubleshooting file since they're almost always tested together.

See also: [01 - SNS Fundamentals & Deep Dive](01%20-%20SNS%20Fundamentals%20%26%20Deep%20Dive.md) · [02 - SNS Architecture & Examples](02%20-%20SNS%20Architecture%20%26%20Examples.md) · [03 - SQS Scenarios, Best Practices & Troubleshooting](03%20-%20SQS%20Scenarios%2C%20Best%20Practices%20%26%20Troubleshooting.md)

---

## Table of Contents

- [1. Scenario-Based Questions](#1-scenario-based-questions)
- [2. Best Practices](#2-best-practices)
- [3. Common Errors & Troubleshooting (SRE View)](#3-common-errors--troubleshooting-sre-view)
- [4. Key CloudWatch Metrics](#4-key-cloudwatch-metrics)
- [5. Rapid-Fire Facts](#5-rapid-fire-facts)

---

## 1. Scenario-Based Questions

**Q1.** An order event must trigger fulfillment, analytics, and an audit log - each independent and resilient to the others failing.
**A.** **SNS topic → 3 SQS queues** (fan-out). Each consumer drains its own queue.

---

**Q2.** A single S3 `ObjectCreated` event must start both a thumbnail job and a virus scan, but S3 only allows one destination per event type.
**A.** **S3 → SNS → two SQS queues** (or two Lambdas). Fan out via SNS.

---

**Q3.** From one topic, the "EU" subscriber should only get EU messages and "US" only US, without separate topics.
**A.** **Message filtering** - filter policies on each subscription (`region` attribute).

---

**Q4.** Notifications to an HTTP endpoint are being lost when the endpoint is briefly down.
**A.** Attach a **subscription DLQ** (SQS) to capture undeliverable messages, and/or fan out via **SQS** for durability. Configure the **HTTP retry policy**.

---

**Q5.** Compliance needs every published notification archived in S3 for 7 years and queryable.
**A.** Subscribe **Kinesis Data Firehose** to the topic → deliver to **S3** (lifecycle to Glacier).

---

**Q6.** Downstream consumers require strict ordering and no duplicates across multiple queues.
**A.** **SNS FIFO topic → SQS FIFO queues**, using `MessageGroupId`.

---

**Q7.** A central security account must receive alerts published by 50 member accounts.
**A.** Central **SNS topic with an access policy** allowing member accounts to `sns:Publish` (or member topics → central). Cross-account fan-in.

---

**Q8.** Publishing must not traverse the public internet for a private workload.
**A.** Use a **VPC interface endpoint (PrivateLink)** for SNS.

---

**Q9.** A CloudWatch alarm must email on-call AND trigger an auto-remediation Lambda.
**A.** Alarm → **SNS** with two subscriptions: email + Lambda.

[⬆ Back to top](#table-of-contents)

---

## 2. Best Practices

| Area                      | Best Practice                                                                               |
| :------------------------ | :------------------------------------------------------------------------------------------ |
| **Durability**            | Fan out to **SQS** or attach a **subscription DLQ**; SNS alone is transient.                |
| **Filtering**             | Use **filter policies** instead of many topics to reduce sprawl.                            |
| **Raw message delivery**  | Enable for SQS/HTTP to drop the SNS JSON envelope when subscribers expect the bare payload. |
| **Encryption**            | SSE-KMS for sensitive data; CMK for audit of key usage.                                     |
| **Least privilege**       | Scope topic access policy by `aws:SourceArn`/account; avoid `Principal: *`.                 |
| **Retry/DLQ**             | Always configure a DLQ on critical subscriptions.                                           |
| **FIFO only when needed** | FIFO topics have lower throughput; default to Standard.                                     |
| **Confirm subscriptions** | HTTP/Email subscriptions are inactive until confirmed - monitor for unconfirmed.            |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Errors & Troubleshooting (SRE View)

| Symptom                                           | Likely Cause                                            | Resolution                                                                     |
| :------------------------------------------------ | :------------------------------------------------------ | :----------------------------------------------------------------------------- |
| **SQS subscriber gets nothing**                   | Queue **access policy** doesn't allow SNS `SendMessage` | Add queue policy with `Service: sns.amazonaws.com` + `aws:SourceArn` condition |
| **Messages lost when endpoint down**              | SNS retries exhausted; no DLQ                           | Attach **subscription DLQ**; fan out via SQS for buffering                     |
| **Subscriber gets too much / irrelevant traffic** | No or wrong **filter policy**                           | Add/fix filter policy; check `FilterPolicyScope` (attributes vs body)          |
| **Double SNS JSON envelope in SQS**               | Raw message delivery off                                | Enable **RawMessageDelivery** on the subscription                              |
| **HTTP subscription stuck "PendingConfirmation"** | Endpoint never confirmed token                          | Re-send confirmation; ensure endpoint returns the `SubscribeURL` request       |
| **`AuthorizationError` on Publish**               | IAM/topic policy missing `sns:Publish`                  | Grant publisher permission; check cross-account access policy                  |
| **`KMS` errors / no delivery on encrypted topic** | Subscriber (e.g., SQS) or service can't use the CMK     | Grant the service principal `kms:Decrypt`/`GenerateDataKey` on the key policy  |
| **FIFO topic throttling**                         | Exceeding FIFO throughput                               | Batch publishes; spread `MessageGroupId`s                                      |
| **CloudWatch alarm fires but no email**           | Subscription unconfirmed / wrong address / in spam      | Confirm subscription; verify endpoint                                          |

**SRE note:** SNS is fire-and-forget from the publisher's view. Build observability with `NumberOfNotificationsFailed` and **DLQs** - otherwise silent drops are invisible. For anything that must not be lost, **terminate fan-out into SQS**.

[⬆ Back to top](#table-of-contents)

---

## 4. Key CloudWatch Metrics

| Metric                               | Tells You                           |
| :----------------------------------- | :---------------------------------- |
| `NumberOfMessagesPublished`          | Publish volume                      |
| `NumberOfNotificationsDelivered`     | Successful deliveries               |
| `NumberOfNotificationsFailed`        | Delivery failures (alarm on this)   |
| `NumberOfNotificationsFilteredOut`   | Messages dropped by filter policies |
| `NumberOfNotificationsRedrivenToDlq` | Messages sent to subscription DLQ   |
| `PublishSize`                        | Message size distribution           |

[⬆ Back to top](#table-of-contents)

---

## 5. Rapid-Fire Facts

- **Push** pub/sub; SQS is **pull**. SNS doesn't persist messages long-term.
- **Fan-out** = SNS → multiple SQS for durable independent processing.
- **Message filtering** via filter policies on attributes or body.
- **FIFO topic** → `.fifo`, ordered + dedup, pairs with **SQS FIFO**.
- **Subscription DLQ** captures undeliverable messages.
- **Raw message delivery** strips the SNS envelope for SQS/HTTP.
- Authorize service/cross-account publish with the **topic access policy**.
- A2A = SQS/Lambda/HTTP/Firehose; A2P = SMS/email/mobile push.
- Encrypt at rest with SSE-KMS; private publish via **PrivateLink**.

[⬆ Back to top](#table-of-contents)
