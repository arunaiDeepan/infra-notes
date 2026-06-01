# AWS CloudTrail - Exam Scenarios

> Exam focus: CloudTrail vs CloudWatch vs Config, data events off-by-default, org/multi-region trails, log integrity, and detecting tampering. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - AWS CloudTrail Intro bits & bytes](01%20-%20AWS%20CloudTrail%20Intro%20bits%20%26%20bytes.md) · [02 - AWS CloudTrail Deep Dive](02%20-%20AWS%20CloudTrail%20Deep%20Dive.md) · [04 - AWS CloudTrail SRE Operations](04%20-%20AWS%20CloudTrail%20SRE%20Operations.md) · [24 - AWS Config & Audit Manager](24%20-%20AWS%20Config%20%26%20Audit%20Manager.md)

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

- "Who did what" → CloudTrail (vs health=CloudWatch, config=Config).
- **Data events off by default** (S3 object-level, Lambda invoke).
- **Multi-region organization trail** for full-coverage, tamper-resistant audit.
- **Log file validation + S3 Object Lock + SSE-KMS** for compliance.
- Detecting/preventing **StopLogging/DeleteTrail** (SCP + alarm).
- Real-time reaction via **EventBridge**; alerting via **CloudWatch metric filter + alarm**.
- 90-day Event History vs durable trail.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                                            | Points to                                         |
| :---------------------------------------------------------------- | :------------------------------------------------ |
| "who deleted/created/modified", "which user/role", "from what IP" | **CloudTrail**                                    |
| "object-level S3 access", "track GetObject/PutObject"             | **S3 data events** (enable on trail)              |
| "all accounts in the organization", "central audit"               | **Organization trail** (multi-region)             |
| "prove logs weren't tampered with"                                | **Log file validation** (+ Object Lock)           |
| "logs must be immutable / WORM / 7 years"                         | **S3 Object Lock + lifecycle**                    |
| "alert when someone disables logging"                             | **EventBridge / CloudWatch alarm on StopLogging** |
| "query years of activity with SQL"                                | **CloudTrail Lake**                               |
| "react in real time to an API call"                               | **EventBridge**                                   |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Choosing **CloudWatch** or **Config** when the question asks "who/which principal."
- Forgetting **data events are off by default**.
- Relying on **Event History** for long-term/cross-account (only 90 days, mgmt only).
- Using a single-region trail when "all regions" is required.
- Thinking CloudTrail is real-time (use EventBridge for fast reaction).
- VPC Flow Logs offered for API auditing (that's network traffic).

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **"Who/which principal/from where"** → CloudTrail. Eliminate CloudWatch/Config/Flow Logs.
2. **"Object-level / invoke-level"** → enable data events.
3. **"All accounts / central / can't be disabled by members"** → organization trail.
4. **"Tamper-proof / immutable / prove integrity"** → log validation + Object Lock + SSE-KMS.
5. **"Real-time"** → EventBridge; **"alert on a specific call"** → CloudWatch metric filter + alarm.

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** Security needs to know which IAM principal terminated an EC2 instance and from what IP.
**Options:** A) CloudWatch B) CloudTrail C) Config D) Flow Logs
**Correct:** B
**Explanation:** CloudTrail's `userIdentity` + `sourceIPAddress` for `TerminateInstances`.

### Q2

**Scenario:** Audit every object read on a sensitive S3 bucket.
**Options:** A) Enable S3 server access logs only B) Enable S3 data events on a trail C) CloudWatch metric D) Config rule
**Correct:** B
**Explanation:** Object-level reads are **data events**, off by default.

### Q3

**Scenario:** One immutable audit log across 30 accounts and all regions.
**Options:** A) Per-account trails B) Multi-region organization trail to a central bucket C) Event History D) Config aggregator
**Correct:** B
**Explanation:** Org trail centralizes and members can't disable it.

### Q4

**Scenario:** Auditors require proof logs weren't altered.
**Options:** A) Versioning only B) CloudTrail log file validation (+ Object Lock) C) Encryption only D) MFA
**Correct:** B
**Explanation:** Digest files prove integrity; Object Lock enforces WORM.

### Q5

**Scenario:** Alert within minutes if anyone calls StopLogging.
**Options:** A) Daily S3 review B) Stream to CloudWatch Logs metric filter + alarm, or EventBridge rule C) Config D) Athena weekly
**Correct:** B
**Explanation:** Metric filter/alarm or EventBridge gives near-real-time alerting.

### Q6

**Scenario:** Need API activity older than 90 days.
**Options:** A) Event History B) A trail to S3 (or CloudTrail Lake) C) CloudWatch D) Config
**Correct:** B
**Explanation:** Event History is only 90 days; durable retention needs a trail/Lake.

### Q7

**Scenario:** Query years of CloudTrail with SQL without building a pipeline.
**Options:** A) Athena setup B) CloudTrail Lake C) CloudWatch Insights D) Config
**Correct:** B
**Explanation:** Lake is a managed, immutable SQL store.

### Q8

**Scenario:** Trigger a Lambda the moment a security group rule is changed.
**Options:** A) Poll CloudTrail S3 B) EventBridge rule on the management event C) Daily Athena D) Config snapshot
**Correct:** B
**Explanation:** EventBridge reacts in real time to the API event.

### Q9

**Scenario:** Detect "is this resource compliant with config policy?"
**Options:** A) CloudTrail B) Config C) CloudWatch D) Flow Logs
**Correct:** B
**Explanation:** Configuration/compliance is Config, not CloudTrail.

### Q10

**Scenario:** Encrypt CloudTrail logs and control who can decrypt.
**Options:** A) SSE-S3 B) SSE-KMS with a key policy C) Client-side only D) No encryption
**Correct:** B
**Explanation:** SSE-KMS lets you govern decryption via key policy.

### Q11

**Scenario:** Reduce data-event cost while still auditing a sensitive prefix.
**Options:** A) Log all buckets B) Advanced event selectors scoped to the prefix C) Disable data events D) Use Event History
**Correct:** B
**Explanation:** Advanced selectors log only what you need.

### Q12

**Scenario:** Centralize and protect logs from member-account tampering.
**Options:** A) Trail per account B) Organization trail in a dedicated log-archive account C) Email logs D) Event History
**Correct:** B
**Explanation:** Org trail + dedicated account isolates and protects logs.

### Q13

**Scenario:** Feed threat detection from API activity.
**Options:** A) Manual review B) GuardDuty (consumes CloudTrail) C) CloudWatch dashboard D) Config
**Correct:** B
**Explanation:** GuardDuty analyzes CloudTrail (and DNS/VPC) for threats.

### Q14

**Scenario:** Activity in an unused region went unaudited.
**Options:** A) Single-region trail B) Multi-region trail C) Event History D) Flow Logs
**Correct:** B
**Explanation:** Multi-region trails capture all regions.

### Q15

**Scenario:** Where are IAM/STS (global) events logged?
**Options:** A) Every region duplicated B) A designated region; captured by a multi-region trail C) Not logged D) Only us-west-2
**Correct:** B
**Explanation:** Global service events are logged in a designated region; multi-region trail captures them.

### Q16

**Scenario:** Long-term archive of logs at lowest storage cost.
**Options:** A) Keep in CloudWatch Logs B) S3 with lifecycle to Glacier C) Lake forever D) Event History
**Correct:** B
**Explanation:** S3 lifecycle to Glacier minimizes archive cost.

### Q17

**Scenario:** Investigate a failed (denied) API attempt.
**Options:** A) Not logged B) CloudTrail records errorCode AccessDenied C) Config D) CloudWatch
**Correct:** B
**Explanation:** Failed attempts are recorded with `errorCode`.

### Q18

**Scenario:** Tie an action to the human who assumed a role.
**Options:** A) Only shows role B) userIdentity.sessionContext / role session name C) Not possible D) Flow Logs
**Correct:** B
**Explanation:** `sessionContext` and the role session name attribute the action.

### Q19

**Scenario:** Real-time-ish alarm when root account is used.
**Options:** A) Monthly report B) CloudWatch metric filter on `userIdentity.type=Root` + alarm C) Config D) Athena
**Correct:** B
**Explanation:** Metric filter + alarm on root usage is a classic control.

### Q20

**Scenario:** A managed, cross-account immutable store you can also ingest external activity into.
**Options:** A) S3 only B) CloudTrail Lake C) CloudWatch Logs D) Config aggregator
**Correct:** B
**Explanation:** Lake supports cross-account, immutability, and external events.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** An attacker who compromised an admin role disabled the regional trail, acted, then re-enabled it. The org must make this impossible and be alerted instantly.
**Options:** A) More IAM B) **Organization trail** (members/most roles can't stop it) + **SCP deny** `cloudtrail:StopLogging`/`DeleteTrail` + EventBridge alarm on those events C) Daily review D) Encrypt logs
**Correct:** B
**Explanation:** Org trail removes member ability to disable; SCP blocks the API even for local admins; EventBridge alerts on attempts. Defense in depth.

### H2

**Scenario:** Compliance demands 7-year, demonstrably tamper-proof API logs across all accounts, queryable for audits, at controlled cost.
**Options:** A) Event History B) Multi-region org trail → S3 with **Object Lock (WORM)** + **log file validation** + SSE-KMS, lifecycle to Glacier; query via Athena (or Lake for frequent queries) C) CloudWatch Logs 7y D) Per-account trails
**Correct:** B
**Explanation:** Object Lock + validation = immutable & provable; S3 lifecycle controls cost; Athena/Lake for querying.

### H3

**Scenario:** Data-event logging for all S3 buckets blew the budget, but security still needs object-level audit on regulated data.
**Options:** A) Disable all data events B) Use **advanced event selectors** to log data events only for the regulated buckets/prefixes (and only write events if reads aren't required) C) Switch to Config D) Event History
**Correct:** B
**Explanation:** Scope data events precisely; high-volume buckets are excluded, cost drops, audit need is met.

### H4

**Scenario:** A multi-account SIEM needs all API activity in near-real-time for correlation, plus durable archive.
**Options:** A) Daily S3 pull B) Org trail → S3 (archive) **and** CloudWatch Logs/EventBridge → SIEM forwarder (near-real-time); or Security Lake C) Event History export D) Manual
**Correct:** B
**Explanation:** S3 for archive, EventBridge/CloudWatch (or Security Lake) for streaming to the SIEM.

### H5

**Scenario:** Investigators must determine whether a specific access key was used maliciously over the last 6 months across regions.
**Options:** A) Event History (90d) B) Query the trail's S3 logs with **Athena** (or **CloudTrail Lake**) filtering on `userIdentity.accessKeyId` across regions/time C) CloudWatch D) Config
**Correct:** B
**Explanation:** Event History is too short; Athena/Lake over the multi-region trail covers 6 months and all regions.

### H6

**Scenario:** A company sees suspicious _spikes_ in API call rates but doesn't know which calls; they want automatic anomaly detection.
**Options:** A) Manual graphs B) Enable **CloudTrail Insights** to detect unusual management/API activity rates C) GuardDuty only D) Config
**Correct:** B
**Explanation:** Insights surfaces unusual _rates_ of activity automatically (complements GuardDuty's threat focus).

### H7

**Scenario:** Logs must be encrypted such that even the log-archive account admins can't read them without separate key authorization.
**Options:** A) SSE-S3 B) SSE-KMS with a **key policy** controlled by a separate security team; bucket in log-archive account C) Client encrypt manually D) No encryption
**Correct:** B
**Explanation:** Separating the KMS key authority from bucket ownership enforces dual control over decryption.

### H8

**Scenario:** After enabling an org trail, a team complains their previously-existing per-account trail now double-bills and duplicates logs.
**Options:** A) Keep both B) Consolidate to the org trail; remove redundant account trails (first management-events copy is free, extra trails are charged) C) Disable org trail D) Ignore
**Correct:** B
**Explanation:** Multiple trails capturing the same management events incur extra cost; consolidate.

### H9

**Scenario:** A regulator asks for proof that a particular sequence of changes (who → what → when) led to a breach, with non-repudiation.
**Options:** A) Screenshots B) CloudTrail events (userIdentity incl. sessionContext) + **log file validation digests** to prove non-repudiation, correlated in Athena/Lake C) CloudWatch D) Config timeline only
**Correct:** B
**Explanation:** CloudTrail provides who/what/when; validation digests provide tamper-evidence/non-repudiation. (Config adds the configuration timeline as supporting evidence.)

### H10

**Scenario:** The security team wants automatic remediation: if a public S3 bucket is created, revert it within seconds.
**Options:** A) CloudTrail alone B) EventBridge rule on the relevant API event → Lambda/SSM Automation remediation (and/or Config rule with auto-remediation) C) Daily Athena D) Manual
**Correct:** B
**Explanation:** CloudTrail/EventBridge gives the trigger; Lambda/SSM (or Config remediation) performs the fix. CloudTrail records _who did what_; the automation reverts it.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Who-did-what → CloudTrail. Object/invoke audit → enable data events (off by default). All accounts/regions, tamper-resistant → multi-region org trail. Immutable proof → log validation + Object Lock + SSE-KMS. Real-time → EventBridge. Alert on a call → CloudWatch metric filter. Don't confuse with Config (config state) or CloudWatch (health).**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - AWS CloudTrail SRE Operations](04%20-%20AWS%20CloudTrail%20SRE%20Operations.md).
