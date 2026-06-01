# Amazon EventBridge - Scenarios, Best Practices & SRE Troubleshooting (SAA-C03)

> Scenario drills + production troubleshooting. The exam loves "which service routes/schedules/glues this?" - EventBridge is often the right answer over SNS/SQS when content routing, AWS-service events, SaaS, scheduling, or replay are involved.

See also: [01 - EventBridge Fundamentals & Deep Dive](01%20-%20EventBridge%20Fundamentals%20%26%20Deep%20Dive.md) · [02 - EventBridge Architecture & Examples](02%20-%20EventBridge%20Architecture%20%26%20Examples.md) · [03 - SNS Scenarios, Best Practices & Troubleshooting](03%20-%20SNS%20Scenarios%2C%20Best%20Practices%20%26%20Troubleshooting.md)

---

## Table of Contents

- [1. Scenario-Based Questions](#1-scenario-based-questions)
- [2. Best Practices](#2-best-practices)
- [3. Common Errors & Troubleshooting (SRE View)](#3-common-errors--troubleshooting-sre-view)
- [4. Key CloudWatch Metrics](#4-key-cloudwatch-metrics)
- [5. Decision Guide: EventBridge vs Alternatives](#5-decision-guide-eventbridge-vs-alternatives)
- [6. Rapid-Fire Facts](#6-rapid-fire-facts)

---

## 1. Scenario-Based Questions

**Q1.** Route order events to different processors based on the order amount and type, with no custom routing code.
**A.** **EventBridge rules with event patterns** (content-based routing) to different targets.

---

**Q2.** Run a Lambda every weeknight at 7 pm India time to shut down dev instances.
**A.** **EventBridge Scheduler** with a cron expression and `Asia/Kolkata` time zone.

---

**Q3.** Automatically isolate an EC2 instance when GuardDuty raises a high-severity finding.
**A.** **EventBridge rule** matching the GuardDuty finding → **Lambda/SSM Automation** to quarantine; SNS to alert.

---

**Q4.** Ingest events directly from a third-party SaaS (e.g., Shopify) into AWS without building a webhook server.
**A.** **EventBridge partner event source / partner event bus.**

---

**Q5.** After fixing a consumer bug, reprocess all events from the last 3 days.
**A.** **EventBridge archive + replay** (SNS/SQS can't replay arbitrary history).

---

**Q6.** A target Lambda is occasionally down; events must not be lost.
**A.** Configure target **retry policy** (up to 24h) + an **SQS DLQ** on the target.

---

**Q7.** Developers need typed objects matching event structures for an undocumented stream of events.
**A.** **Schema registry with schema discovery** → generate code bindings.

---

**Q8.** Connect DynamoDB Streams to a workflow with filtering and enrichment, minimizing custom code.
**A.** **EventBridge Pipes** (source = DynamoDB Streams, enrich via Lambda, target = Step Functions).

---

**Q9.** Central security account must receive specific events from 100 member accounts.
**A.** Member accounts `PutEvents` to the central bus via a **bus resource policy**; central rules route them.

---

**Q10.** Need the absolute lowest latency, highest throughput fan-out to many subscribers.
**A.** **SNS** (not EventBridge) - EventBridge has higher latency/lower throughput.

[⬆ Back to top](#table-of-contents)

---

## 2. Best Practices

| Area                          | Best Practice                                                                  |
| :---------------------------- | :----------------------------------------------------------------------------- |
| **Specific patterns**         | Make event patterns as narrow as possible to avoid over-triggering targets.    |
| **DLQ on targets**            | Always attach an SQS DLQ for critical rules.                                   |
| **Custom buses per domain**   | Isolate teams/domains rather than overloading the default bus.                 |
| **Archive critical buses**    | Enable archive for replay/audit.                                               |
| **Least-privilege roles**     | Scope the EventBridge invocation role to specific target ARNs.                 |
| **Idempotent targets**        | Delivery is at-least-once; targets may see duplicates.                         |
| **Use Scheduler for cron**    | Prefer EventBridge Scheduler over legacy scheduled rules for scale/time zones. |
| **Input transformer**         | Reshape events to exactly what targets expect; avoid leaking full event.       |
| **Monitor FailedInvocations** | Alarm on delivery failures + DLQ depth.                                        |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Errors & Troubleshooting (SRE View)

| Symptom                            | Likely Cause                                              | Resolution                                                                      |
| :--------------------------------- | :-------------------------------------------------------- | :------------------------------------------------------------------------------ |
| **Rule never triggers**            | Event pattern doesn't match (case-sensitive, wrong field) | Test with the console "Sandbox"; verify `source`/`detail-type`/`detail` exactly |
| **Events on wrong bus**            | Custom events sent to default bus or wrong `EventBusName` | Set `EventBusName` on `PutEvents` and the rule                                  |
| **Target not invoked**             | Missing IAM **invocation role** permission for the target | Grant the EventBridge role permission to invoke the target                      |
| **`FailedInvocations` rising**     | Target throttled/erroring; bad permissions                | Check target health; add DLQ; verify role/resource policies                     |
| **Lambda target gets duplicates**  | At-least-once delivery                                    | Make the function idempotent                                                    |
| **Cross-account PutEvents denied** | Bus **resource policy** missing source account            | Add account/org to the bus policy                                               |
| **API destination 4xx/throttle**   | Bad auth or rate-limit too high                           | Fix connection auth; set invocation rate limit                                  |
| **Scheduled job didn't run**       | Wrong cron/time zone; `?` vs `*` day fields               | Validate expression; remember 6-field cron with `?`                             |
| **Events silently dropped**        | No matching rule (unmatched events are discarded)         | Add a catch-all rule to a log/DLQ for visibility                                |
| **Schema not discovered**          | Discovery not enabled on the bus                          | Enable schema discovery                                                         |

**SRE note:** Unmatched events are **dropped silently** - there's no "dead bus." For observability, add a broad catch-all rule routing to CloudWatch Logs or an SQS queue during rollout, and alarm on `FailedInvocations` and `DeadLetterInvocations`.

[⬆ Back to top](#table-of-contents)

---

## 4. Key CloudWatch Metrics

| Metric                  | Tells You                           |
| :---------------------- | :---------------------------------- |
| `Invocations`           | Successful target invocations       |
| `FailedInvocations`     | Target invocation failures (alarm)  |
| `TriggeredRules`        | How often rules matched             |
| `MatchedEvents`         | Events matching any rule on the bus |
| `DeadLetterInvocations` | Events sent to a target DLQ         |
| `ThrottledRules`        | Rules throttled (raise limits)      |

[⬆ Back to top](#table-of-contents)

---

## 5. Decision Guide: EventBridge vs Alternatives

| If the requirement is…                      | Choose                         |
| :------------------------------------------ | :----------------------------- |
| Content-based routing of events             | **EventBridge**                |
| AWS-service events (EC2, GuardDuty, Config) | **EventBridge** (native)       |
| SaaS partner event ingestion                | **EventBridge partner bus**    |
| Serverless cron/scheduling                  | **EventBridge Scheduler**      |
| Replay historical events                    | **EventBridge archive/replay** |
| Highest-throughput, lowest-latency fan-out  | **SNS**                        |
| Durable work queue / buffering              | **SQS**                        |
| Orchestrate multi-step workflow with state  | **Step Functions**             |
| One source → one target + enrich            | **EventBridge Pipes**          |

[⬆ Back to top](#table-of-contents)

---

## 6. Rapid-Fire Facts

- Bus + rule (pattern/schedule) + up to **5 targets** per rule.
- Three buses: **default** (AWS), **custom** (your app), **partner** (SaaS).
- Retries up to **24 hours**; attach **SQS DLQ** to targets.
- At-least-once delivery → make targets **idempotent**.
- **Archive + replay** = reprocess past events (unique vs SNS/SQS).
- **Schema registry/discovery** → code bindings.
- **Pipes** = point-to-point with filter/enrich/transform.
- **Scheduler** = serverless cron with time zones, 270+ API targets.
- Unmatched events are **dropped silently**.
- Higher latency than SNS - SNS wins for raw fan-out throughput.

[⬆ Back to top](#table-of-contents)
