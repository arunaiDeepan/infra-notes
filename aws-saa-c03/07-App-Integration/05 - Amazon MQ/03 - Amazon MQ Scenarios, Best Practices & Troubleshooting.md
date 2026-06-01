# Amazon MQ - Scenarios, Best Practices & SRE Troubleshooting (SAA-C03)

> The exam tests one decision repeatedly: **Amazon MQ vs SQS/SNS**. Master that plus the HA model and you're covered.

See also: [01 - Amazon MQ Fundamentals & Deep Dive](01%20-%20Amazon%20MQ%20Fundamentals%20%26%20Deep%20Dive.md) · [02 - Amazon MQ Architecture & Examples](02%20-%20Amazon%20MQ%20Architecture%20%26%20Examples.md) · [03 - SQS Scenarios, Best Practices & Troubleshooting](03%20-%20SQS%20Scenarios%2C%20Best%20Practices%20%26%20Troubleshooting.md)

---

## Table of Contents

- [1. Scenario-Based Questions](#1-scenario-based-questions)
- [2. Best Practices](#2-best-practices)
- [3. Common Errors & Troubleshooting (SRE View)](#3-common-errors--troubleshooting-sre-view)
- [4. Key CloudWatch Metrics](#4-key-cloudwatch-metrics)
- [5. The Decision Table](#5-the-decision-table)
- [6. Rapid-Fire Facts](#6-rapid-fire-facts)

---

## 1. Scenario-Based Questions

**Q1.** A company is migrating an on-prem app that uses **Apache ActiveMQ with JMS** to AWS and wants minimal code changes.
**A.** **Amazon MQ (ActiveMQ engine)** - speaks JMS natively; just repoint the endpoint.

---

**Q2.** A new, cloud-native app needs a simple, infinitely scalable queue.
**A.** **SQS** (not Amazon MQ). Amazon MQ is for migrations/standard protocols.

---

**Q3.** The migrated broker must survive an AZ failure.
**A.** **ActiveMQ active/standby Multi-AZ** (shared EFS) or **RabbitMQ 3-node cluster**.

---

**Q4.** An IoT fleet publishes telemetry over **MQTT**; the app must run on AWS.
**A.** **Amazon MQ** supports MQTT (or AWS IoT Core for IoT-native). Standard protocol → Amazon MQ.

---

**Q5.** They want to trigger a Lambda whenever a message lands on the existing RabbitMQ broker.
**A.** **Lambda event source mapping for Amazon MQ** (or **EventBridge Pipes** with MQ source).

---

**Q6.** Compliance requires encryption at rest with a customer-managed key and TLS in transit.
**A.** Enable **KMS CMK** at-rest encryption + TLS endpoints on the broker.

---

**Q7.** Throughput needs to grow far beyond a single broker's capacity, with spiky load.
**A.** Reconsider the design - **Amazon MQ scales vertically**. For unlimited scale, modernize to **SQS/SNS** (or bridge MQ → SQS).

[⬆ Back to top](#table-of-contents)

---

## 2. Best Practices

| Area                 | Best Practice                                                                       |
| :------------------- | :---------------------------------------------------------------------------------- |
| **Right tool**       | Use Amazon MQ only for migration/standard protocols; prefer SQS/SNS for new builds. |
| **HA**               | Always use active/standby (ActiveMQ) or cluster (RabbitMQ) in production.           |
| **Private brokers**  | Deploy in private subnets; avoid `publiclyAccessible = true`.                       |
| **Failover clients** | Use failover transport URLs so clients reconnect automatically.                     |
| **Right-size**       | Pick an instance type matching throughput; monitor and scale vertically.            |
| **Encryption**       | TLS + KMS CMK; rotate broker credentials (store in Secrets Manager).                |
| **Patching window**  | Set a maintenance window; AWS patches the broker engine.                            |
| **Monitor depth**    | Alarm on queue depth and broker CPU/heap to catch consumer lag.                     |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Errors & Troubleshooting (SRE View)

| Symptom                          | Likely Cause                             | Resolution                                                           |
| :------------------------------- | :--------------------------------------- | :------------------------------------------------------------------- |
| **Clients drop during failover** | Single endpoint, no failover transport   | Use **failover URL** with both broker endpoints                      |
| **Connection refused / timeout** | Security group or subnet misconfig       | Open the protocol port (e.g., 61617) from client SG; check route/VPN |
| **High broker CPU / heap, lag**  | Under-sized instance or slow consumers   | Scale instance vertically; speed up/scale consumers                  |
| **Messages piling up**           | Consumers down or too slow               | Check consumer health; add consumers; inspect DLQ                    |
| **TLS handshake failures**       | Client not using TLS / wrong port        | Use `ssl://` endpoint and correct TLS port                           |
| **Auth failures**                | Wrong broker user/LDAP config            | Verify broker users / LDAP; rotate via Secrets Manager               |
| **Throughput plateau**           | Hit single-broker ceiling                | Vertical scale or modernize to SQS/SNS                               |
| **Storage full (ActiveMQ)**      | EFS/EBS storage limit reached            | Increase storage; expire/clear old messages                          |
| **Failover slow**                | Standby promotion + client reconnect lag | Expected brief pause; ensure clients auto-reconnect                  |

**SRE note:** Amazon MQ is **not serverless** - you own capacity planning. The two recurring incidents are **failover handling** (clients must use failover URLs) and **vertical scaling ceilings** (a single broker can't absorb unbounded spikes like SQS). For workloads that outgrow a broker, bridge to SQS/SNS or modernize.

[⬆ Back to top](#table-of-contents)

---

## 4. Key CloudWatch Metrics

| Metric                       | Tells You                                |
| :--------------------------- | :--------------------------------------- |
| `CpuUtilization`             | Broker CPU pressure (scale signal)       |
| `HeapUsage`                  | JVM heap (ActiveMQ) saturation           |
| `QueueSize` / `MessageCount` | Backlog per queue                        |
| `ConsumerCount`              | Active consumers (0 = nothing draining)  |
| `NetworkIn/Out`              | Traffic volume                           |
| `StorePercentUsage`          | Broker storage usage (alarm before full) |

[⬆ Back to top](#table-of-contents)

---

## 5. The Decision Table

| If the question says…                                                     | Answer                                      |
| :------------------------------------------------------------------------ | :------------------------------------------ |
| "Migrate existing broker app", "JMS/AMQP/MQTT/STOMP", "without rewriting" | **Amazon MQ**                               |
| "New", "serverless", "unlimited scale", "decouple", "fan-out"             | **SQS / SNS**                               |
| "Highly available broker across AZs"                                      | **Active/standby** or **cluster**           |
| "Trigger Lambda from existing broker"                                     | **Lambda event source / EventBridge Pipes** |
| "Both queues and pub/sub in one system, standard protocol"                | **Amazon MQ**                               |

[⬆ Back to top](#table-of-contents)

---

## 6. Rapid-Fire Facts

- Managed **ActiveMQ** and **RabbitMQ** brokers.
- Reason to exist: **migrate** apps using **standard protocols** (JMS, AMQP, MQTT, STOMP, OpenWire, WebSocket) with **no rewrite**.
- **Not serverless** - you size broker instances; scales **vertically**.
- HA: ActiveMQ **active/standby (EFS, 2 AZ)**; RabbitMQ **3-node cluster**.
- One broker offers **both queues and topics**.
- Runs **in your VPC**; secure with SG, TLS, KMS, broker/LDAP auth.
- New cloud-native messaging → **SQS/SNS** instead.

[⬆ Back to top](#table-of-contents)
