# AWS Health Dashboard - Exam Scenarios

> Exam focus: Health vs CloudWatch, personalized account events, EC2 retirement automation, API/org-view support gating. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - AWS Health Dashboard Intro bits & bytes](01%20-%20AWS%20Health%20Dashboard%20Intro%20bits%20%26%20bytes.md) · [02 - AWS Health Dashboard Deep Dive](02%20-%20AWS%20Health%20Dashboard%20Deep%20Dive.md) · [04 - AWS Health Dashboard SRE Operations](04%20-%20AWS%20Health%20Dashboard%20SRE%20Operations.md) · [01 - Amazon CloudWatch Intro bits & bytes](01%20-%20Amazon%20CloudWatch%20Intro%20bits%20%26%20bytes.md)

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

- **AWS Health = AWS-side events affecting your resources** (issue/scheduledChange/accountNotification).
- **Account Health Dashboard** is personalized; SHD is public.
- **EventBridge** automation for retirements/maintenance.
- **Health API + org view** require Business/Enterprise support.
- Health vs CloudWatch (your app) vs CloudTrail (who did what).

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                                       | Points to                            |
| :----------------------------------------------------------- | :----------------------------------- |
| "your instance scheduled for retirement / hardware degraded" | **AWS Health (account)**             |
| "is AWS having an issue affecting my resources"              | **AWS Health**                       |
| "scheduled maintenance notification"                         | **AWS Health scheduledChange**       |
| "automatically respond to a health event"                    | **EventBridge → automation**         |
| "across all accounts in the org"                             | **Health organizational view**       |
| "programmatic access to health events"                       | **Health API (Business/Enterprise)** |
| "is my application slow / erroring"                          | **CloudWatch** (not Health)          |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Choosing **CloudWatch** for AWS-side/maintenance events.
- Choosing the **public SHD** when the personalized **account** view is needed.
- Expecting **API/org view** on Basic support.
- Manual polling instead of **EventBridge** automation.
- Confusing required-action notices with CloudWatch alarms.

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **"AWS issue / maintenance / retirement affecting me"** → AWS Health.
2. **"Automate the response"** → EventBridge → Lambda/SSM.
3. **"All accounts"** → org view (Organizations).
4. **"Programmatic"** → Health API (Business/Enterprise).
5. **"My app metrics"** → CloudWatch (eliminate Health).

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** You get notice your EC2 instance is scheduled for retirement. Which service?
**Options:** A) CloudWatch B) AWS Health (account) C) CloudTrail D) Config
**Correct:** B
**Explanation:** Resource-specific required-action notices come from AWS Health.

### Q2

**Scenario:** Determine if a regional service disruption is AWS-side and affects your resources.
**Options:** A) CloudWatch B) AWS Health C) Trusted Advisor D) Budgets
**Correct:** B
**Explanation:** Health shows AWS-side issues scoped to you.

### Q3

**Scenario:** Automatically replace an instance before its retirement date.
**Options:** A) Manual B) Health event → EventBridge → SSM Automation/Lambda C) CloudWatch alarm D) Config rule
**Correct:** B
**Explanation:** Event-driven automation handles retirements.

### Q4

**Scenario:** Central visibility of health events across 25 accounts.
**Options:** A) Per account B) Health organizational view C) CloudWatch D) Trusted Advisor
**Correct:** B
**Explanation:** Org view aggregates events.

### Q5

**Scenario:** Programmatic retrieval of health events for a custom dashboard.
**Options:** A) Scrape SHD B) Health API (Business/Enterprise) C) CloudTrail D) Config
**Correct:** B
**Explanation:** Health API requires Business/Enterprise.

### Q6

**Scenario:** Your app's latency is high; which tool?
**Options:** A) AWS Health B) CloudWatch C) CloudTrail D) Trusted Advisor
**Correct:** B
**Explanation:** App performance is CloudWatch.

### Q7

**Scenario:** Notify on-call when an AWS issue affects your region.
**Options:** A) Manual B) Health → EventBridge → SNS C) Config D) Budget
**Correct:** B
**Explanation:** Route Health events to SNS via EventBridge.

### Q8

**Scenario:** RDS scheduled maintenance is coming; you want owners notified.
**Options:** A) CloudWatch B) Health scheduledChange → EventBridge → SNS C) CloudTrail D) Config
**Correct:** B
**Explanation:** scheduledChange events drive notifications.

### Q9

**Scenario:** Public general status of S3 across all customers.
**Options:** A) Account Health Dashboard B) Service Health Dashboard C) Health API D) CloudWatch
**Correct:** B
**Explanation:** SHD is the public status page.

### Q10

**Scenario:** Personalized list of events affecting your resources.
**Options:** A) SHD B) Account/Personal Health Dashboard C) CloudWatch D) Config
**Correct:** B
**Explanation:** The account dashboard is personalized.

### Q11

**Scenario:** Certificate rotation required on a managed resource — where surfaced?
**Options:** A) CloudWatch B) AWS Health accountNotification C) CloudTrail D) Trusted Advisor
**Correct:** B
**Explanation:** Action-required notices are Health account notifications.

### Q12

**Scenario:** Trigger failover when a region issue appears.
**Options:** A) Manual B) Health issue event → automation (Route 53 failover) C) Config D) Budget
**Correct:** B
**Explanation:** Event-driven failover from Health events.

### Q13

**Scenario:** Delegated central team should manage org health without using the management account daily.
**Options:** A) Share root B) Delegated administrator for Health org view C) IAM user D) Per account
**Correct:** B
**Explanation:** Delegated admin supports org-view operations.

### Q14

**Scenario:** Which event type is planned maintenance?
**Options:** A) issue B) scheduledChange C) accountNotification D) alarm
**Correct:** B
**Explanation:** scheduledChange = planned.

### Q15

**Scenario:** Which event type is a service disruption?
**Options:** A) issue B) scheduledChange C) accountNotification D) metric
**Correct:** A
**Explanation:** issue = disruption.

### Q16

**Scenario:** Cost of the Health dashboards?
**Options:** A) Per event B) Free (API/org needs Business/Enterprise) C) Per account D) Per region
**Correct:** B
**Explanation:** Dashboards free; API/org gated by support.

### Q17

**Scenario:** Identify which specific resources an event affects.
**Options:** A) SHD B) DescribeAffectedEntities (Health API) / account dashboard C) CloudWatch D) Config
**Correct:** B
**Explanation:** Health surfaces affected entities.

### Q18

**Scenario:** Avoid surprise downtime from hardware degradation.
**Options:** A) Wait B) Act on Health proactive notifications before the deadline C) CloudWatch alarm only D) Ignore
**Correct:** B
**Explanation:** Proactive handling prevents downtime.

### Q19

**Scenario:** Open a ticket automatically per health event.
**Options:** A) Manual B) EventBridge → Lambda/ITSM integration C) Config D) Budget
**Correct:** B
**Explanation:** EventBridge to ticketing automates intake.

### Q20

**Scenario:** Who made a change to a resource — Health or CloudTrail?
**Options:** A) Health B) CloudTrail C) CloudWatch D) Trusted Advisor
**Correct:** B
**Explanation:** API attribution is CloudTrail.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** An org of 40 accounts wants a single, automated pipeline that opens tickets and pages on-call for any AWS issue or scheduled change affecting any account.
**Options:** A) Per-account email B) **Health organizational view** + **org EventBridge** rules → Lambda → ITSM + SNS; delegated admin runs it C) CloudWatch only D) Manual SHD checks
**Correct:** B
**Explanation:** Org view + org EventBridge centralizes detection; automation handles intake/paging.

### H2

**Scenario:** Hundreds of EC2 instances are scheduled for retirement over a month; manual handling is impractical.
**Options:** A) Replace by hand B) Health accountNotification → EventBridge → **SSM Automation** to stop/start (new hardware) or ASG-drain/replace, batched before deadlines C) Ignore D) CloudWatch recover
**Correct:** B
**Explanation:** Automate retirement handling at scale via Health → SSM; stop/start moves to healthy hardware, or replace via ASG.

### H3

**Scenario:** During a regional AWS issue, the team needs automatic DNS failover and a customer status update.
**Options:** A) Wait for AWS B) Health **issue** event → automation: Route 53 failover + update status page/notify C) CloudWatch alarm only D) Manual
**Correct:** B
**Explanation:** Health issue events can drive failover and comms automatically (complementing health-check-based failover).

### H4

**Scenario:** A custom internal portal must show live AWS health for the company's resources.
**Options:** A) Embed SHD B) Build on the **Health API** (Business/Enterprise) querying events + affected entities C) Screenshot D) CloudWatch dashboard
**Correct:** B
**Explanation:** The Health API powers custom dashboards with resource-level detail (requires Business/Enterprise).

### H5

**Scenario:** App is erroring; the team blames AWS but isn't sure.
**Options:** A) Assume AWS B) Check **AWS Health** (is there an AWS-side issue affecting these resources?) and **CloudWatch** (app metrics) together to localize C) Open a ticket immediately D) Restart everything
**Correct:** B
**Explanation:** Health answers "is it AWS?"; CloudWatch answers "is it my app?" — use both to triage.

### H6

**Scenario:** After downgrading to Basic support, the team's Health API integration stops working.
**Options:** A) Bug B) Expected — the **Health API** requires Business/Enterprise; the dashboards still work C) Wrong region D) Re-enable in console
**Correct:** B
**Explanation:** API access is support-gated; dashboards remain free.

### H7

**Scenario:** Central ops wants a delegated security/ops account (not the management account) to run org-wide health automation.
**Options:** A) Use management account always B) Configure a **delegated administrator** for AWS Health org view C) Share root D) Per-account only
**Correct:** B
**Explanation:** Delegated admin lets a non-management account operate org health.

### H8

**Scenario:** Scheduled RDS maintenance will cause a brief failover; stakeholders must be informed with timing in advance.
**Options:** A) React after B) Health **scheduledChange** event → EventBridge → SNS to stakeholders with the window; plan around it C) CloudWatch D) Config
**Correct:** B
**Explanation:** Proactive scheduledChange notifications give lead time to communicate/plan.

### H9

**Scenario:** The team wants to correlate AWS-side events with their own incident timeline for postmortems.
**Options:** A) Memory B) Pull Health events (API) + CloudWatch/CloudTrail into the incident record for an accurate timeline C) SHD screenshots D) Guess
**Correct:** B
**Explanation:** Combining Health (AWS-side), CloudWatch (impact), and CloudTrail (changes) builds a complete postmortem timeline.

### H10

**Scenario:** A regulated org must prove it acted on every required-action AWS notification within SLA.
**Options:** A) Trust process B) Health accountNotification → EventBridge → ticket with timestamp; track to closure; retain records for audit C) Manual log D) Ignore minor ones
**Correct:** B
**Explanation:** Automated intake + tracked closure + retained records evidence SLA compliance on required actions.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **AWS-side issues / scheduled maintenance / required actions affecting your resources → AWS Health (Account Health Dashboard). Automate via EventBridge → SSM/Lambda/SNS. API + org view need Business/Enterprise. Your app's health → CloudWatch; who-did-what → CloudTrail.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - AWS Health Dashboard SRE Operations](04%20-%20AWS%20Health%20Dashboard%20SRE%20Operations.md).
