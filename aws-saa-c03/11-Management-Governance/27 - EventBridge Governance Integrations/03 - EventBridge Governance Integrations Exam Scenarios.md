# EventBridge Governance Integrations - Exam Scenarios

> Exam focus: event-driven auto-remediation, EventBridge vs CloudWatch alarms, cross-account centralization, and scheduled governance. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - EventBridge Governance Integrations Intro bits & bytes](01%20-%20EventBridge%20Governance%20Integrations%20Intro%20bits%20%26%20bytes.md) · [02 - EventBridge Governance Integrations Deep Dive](02%20-%20EventBridge%20Governance%20Integrations%20Deep%20Dive.md) · [04 - EventBridge Governance Integrations SRE Operations](04%20-%20EventBridge%20Governance%20Integrations%20SRE%20Operations.md) · [24 - AWS Config & Audit Manager](24%20-%20AWS%20Config%20%26%20Audit%20Manager.md)

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

- **Event-driven** reaction (vs metric-threshold = CloudWatch alarm).
- **Auto-remediation**: event → Lambda/SSM Automation.
- **Cross-account/org** event centralization to a security account.
- **Scheduled rules / Scheduler** for periodic governance.
- Sources: CloudTrail, Config, Health, Security Hub, GuardDuty.
- DLQ + idempotency + archive/replay for reliability.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                              | Points to                                  |
| :-------------------------------------------------- | :----------------------------------------- |
| "automatically remediate when X is created/changed" | **EventBridge rule → Lambda/SSM**          |
| "react in real time to an API call / finding"       | **EventBridge**                            |
| "centralize events from all accounts"               | **Cross-account/org event bus**            |
| "run a task on a schedule"                          | **Scheduled rule / EventBridge Scheduler** |
| "when a metric exceeds a threshold"                 | **CloudWatch alarm** (not EventBridge)     |
| "ensure failed events aren't lost"                  | **DLQ**                                    |
| "re-run past events after a fix"                    | **Archive & replay**                       |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Using EventBridge for a **metric threshold** (use CloudWatch alarm).
- Polling CloudTrail S3 instead of an **EventBridge rule** for real-time.
- Forgetting **DLQ/idempotency** (lost or duplicated remediation).
- Per-account handling when **cross-account centralization** is intended.
- Confusing Config's own remediation with the EventBridge routing layer.

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **"Event happened → do something"** → EventBridge rule + target.
2. **"Metric threshold"** → CloudWatch alarm.
3. **"All accounts centrally"** → cross-account/org bus.
4. **"On a schedule"** → scheduled rule/Scheduler.
5. **"Don't lose failures / re-run"** → DLQ + archive/replay; idempotent targets.

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** Automatically revert any newly-created public S3 bucket within seconds.
**Options:** A) Daily scan B) EventBridge rule on the API event → Lambda/SSM remediation C) Budget D) Manual
**Correct:** B
**Explanation:** Event-driven remediation.

### Q2

**Scenario:** React immediately when someone calls StopLogging on CloudTrail.
**Options:** A) Poll S3 B) EventBridge rule → SNS/Lambda C) Config D) Athena
**Correct:** B
**Explanation:** Real-time event routing.

### Q3

**Scenario:** Run drift detection every night.
**Options:** A) Alarm B) EventBridge scheduled rule (cron) → Lambda C) Config D) Manual
**Correct:** B
**Explanation:** Scheduled rule triggers periodic tasks.

### Q4

**Scenario:** Centralize security events from 30 accounts.
**Options:** A) Per account B) Cross-account/org event bus to a security account C) Budget D) CUR
**Correct:** B
**Explanation:** Central bus consolidates events.

### Q5

**Scenario:** Trigger remediation when Config marks a resource NON_COMPLIANT.
**Options:** A) Manual B) EventBridge rule on Config compliance change → SSM Automation (or Config remediation) C) Budget D) Athena
**Correct:** B
**Explanation:** Config event → remediation runbook.

### Q6

**Scenario:** Alert when CPU exceeds 80%.
**Options:** A) EventBridge B) CloudWatch alarm C) Config D) GuardDuty
**Correct:** B
**Explanation:** Metric threshold = CloudWatch alarm.

### Q7

**Scenario:** Ensure events that fail to deliver aren't lost.
**Options:** A) Ignore B) Configure a DLQ on the target C) More retries only D) Bigger Lambda
**Correct:** B
**Explanation:** DLQ captures failed deliveries.

### Q8

**Scenario:** Respond to a GuardDuty high-severity finding automatically.
**Options:** A) Email weekly B) EventBridge rule → isolate/remediate via Lambda/SSM C) Config D) Budget
**Correct:** B
**Explanation:** Findings route to automated response.

### Q9

**Scenario:** Replace an instance scheduled for retirement (Health) automatically.
**Options:** A) Manual B) EventBridge rule on Health event → SSM Automation C) Alarm D) Config
**Correct:** B
**Explanation:** Health event → automation.

### Q10

**Scenario:** Re-run remediation for past events after fixing a Lambda bug.
**Options:** A) Impossible B) EventBridge archive & replay C) Re-create resources D) CUR
**Correct:** B
**Explanation:** Replay archived events.

### Q11

**Scenario:** Notify on-call and open a ticket for an event.
**Options:** A) Manual B) Rule → SNS + Lambda/ITSM C) Config D) Budget
**Correct:** B
**Explanation:** Fan-out to notification/ticketing.

### Q12

**Scenario:** A rule must only match specific eventNames.
**Options:** A) All events B) Event pattern filtering on detail.eventName C) Tag D) Budget
**Correct:** B
**Explanation:** Event-pattern content filtering.

### Q13

**Scenario:** Reduce noise/cost from a broad rule.
**Options:** A) More targets B) Narrow the event pattern C) Bigger Lambda D) New bus
**Correct:** B
**Explanation:** Precise patterns cut volume.

### Q14

**Scenario:** Multi-step approval + remediation workflow.
**Options:** A) One Lambda B) Rule → Step Functions C) SQS only D) Budget
**Correct:** B
**Explanation:** Step Functions orchestrates multi-step flows.

### Q15

**Scenario:** Buffer bursts of events for downstream processing.
**Options:** A) Direct Lambda B) Target SQS C) SNS only D) Budget
**Correct:** B
**Explanation:** SQS buffers/decouples.

### Q16

**Scenario:** Target needs permission to act.
**Options:** A) None B) IAM role for the target (least privilege) C) Root D) Open
**Correct:** B
**Explanation:** Targets assume a scoped role.

### Q17

**Scenario:** A target may receive duplicate events.
**Options:** A) Impossible B) Design idempotent targets (at-least-once delivery) C) Disable retries D) Ignore
**Correct:** B
**Explanation:** Idempotency handles duplicates.

### Q18

**Scenario:** Schedule stop of dev resources nightly at scale.
**Options:** A) Per resource B) EventBridge Scheduler → Lambda/SSM C) Alarm D) Config
**Correct:** B
**Explanation:** Scheduler handles cron at scale.

### Q19

**Scenario:** Feed all governance events to a SIEM.
**Options:** A) Manual B) Central bus → SQS/Firehose/Lambda → SIEM C) Budget D) CUR
**Correct:** B
**Explanation:** Route to a forwarder/stream.

### Q20

**Scenario:** Auto-remediate vs just detect a public bucket — which adds the action?
**Options:** A) Config detects; EventBridge/Config remediation acts B) Budgets C) CloudTrail D) Athena
**Correct:** A
**Explanation:** Detection (Config/CloudTrail) + EventBridge/remediation = action.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** A security team wants org-wide, automatic remediation of public S3 buckets and open security groups within seconds, centrally managed and audited.
**Options:** A) Per-account cron B) Member accounts forward CloudTrail/Config events to a **central security bus**; rules → **SSM Automation** remediation runbooks (least-privilege); CloudTrail audits; DLQ for failures C) Daily Athena D) Manual
**Correct:** B
**Explanation:** Cross-account bus + event-driven SSM remediation + audit + DLQ is the scalable governance pattern.

### H2

**Scenario:** Remediation Lambda occasionally fails and those events vanish, leaving resources non-compliant.
**Options:** A) Add retries only B) Attach a **DLQ** to capture failed deliveries; alarm on DLQ depth; make the Lambda **idempotent**; replay after fixing C) Bigger Lambda D) Ignore
**Correct:** B
**Explanation:** DLQ + idempotency + replay ensure no silent loss and safe reprocessing.

### H3

**Scenario:** The team confuses why a "CPU > 90%" condition won't trigger an EventBridge rule.
**Options:** A) Bug B) EventBridge reacts to **events**, not metric thresholds — use a **CloudWatch alarm** (which can then notify/EventBridge) C) New rule D) Bigger bus
**Correct:** B
**Explanation:** Metric thresholds are CloudWatch alarms; EventBridge routes events.

### H4

**Scenario:** Config flags NON_COMPLIANT resources but remediation must include an approval step for production.
**Options:** A) Auto-fix everything B) EventBridge rule → **Step Functions** workflow with a manual-approval state before remediation in prod C) Lambda only D) Manual
**Correct:** B
**Explanation:** Step Functions adds approval/branching around remediation.

### H5

**Scenario:** After a remediation bug, the team needs to re-process the last week's security events.
**Options:** A) Recreate events B) **Archive & replay** the events through the corrected rules/targets C) Restore from backup D) Manual
**Correct:** B
**Explanation:** EventBridge archive/replay reprocesses historical events.

### H6

**Scenario:** A high-volume custom event stream is driving up cost and triggering expensive targets unnecessarily.
**Options:** A) Disable EventBridge B) **Narrow event patterns** (content filtering), filter before targets, and only invoke costly targets for relevant events C) Bigger targets D) Ignore
**Correct:** B
**Explanation:** Precise patterns reduce both noise and per-event/target cost.

### H7

**Scenario:** GuardDuty findings must auto-isolate a compromised instance and notify on-call, with a record.
**Options:** A) Manual B) EventBridge rule on the finding → **SSM Automation** (isolate SG/snapshot) + **SNS** notify; CloudTrail records the actions C) Email only D) Config
**Correct:** B
**Explanation:** Event-driven isolation + notification + audit is the incident-response pattern.

### H8

**Scenario:** Critical remediation must keep working even if one Region's EventBridge is impaired.
**Options:** A) Single Region B) **Replicate rules/targets across Regions** (or forward events) for the critical automation C) Bigger bus D) Ignore
**Correct:** B
**Explanation:** EventBridge is regional; replicate critical rules for resilience.

### H9

**Scenario:** Leadership wants periodic (not event-driven) governance: nightly drift detection across thousands of stacks and dev shutdown.
**Options:** A) Many cron servers B) **EventBridge Scheduler** → Lambda/SSM at scale for the scheduled tasks C) Alarms D) Manual
**Correct:** B
**Explanation:** Scheduler handles large-scale cron/rate governance tasks.

### H10

**Scenario:** A central security account must receive events from member accounts without those accounts having broad access to the central account.
**Options:** A) Cross-account admin B) Configure the central bus **resource policy** to accept events from the org; members only **PutEvents**/forward — least privilege C) Share keys D) One account
**Correct:** B
**Explanation:** Bus resource policy + org-scoped forwarding centralizes events with least privilege.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Event happened → react → EventBridge rule → Lambda/SSM/Step Functions/SNS. Metric threshold → CloudWatch alarm. All accounts → central bus. On a schedule → Scheduler. Don't lose failures → DLQ + idempotent targets + archive/replay. It's the automation glue turning detection (CloudTrail/Config/Health/GuardDuty) into action.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - EventBridge Governance Integrations SRE Operations](04%20-%20EventBridge%20Governance%20Integrations%20SRE%20Operations.md).
