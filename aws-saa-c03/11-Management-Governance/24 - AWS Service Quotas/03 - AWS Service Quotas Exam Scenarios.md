# AWS Service Quotas - Exam Scenarios

> Exam focus: soft vs hard limits, the "ASG won't scale / Lambda throttles" pattern, templates for new accounts, and TA-warns/SQ-raises. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - AWS Service Quotas Intro bits & bytes](01%20-%20AWS%20Service%20Quotas%20Intro%20bits%20%26%20bytes.md) · [02 - AWS Service Quotas Deep Dive](02%20-%20AWS%20Service%20Quotas%20Deep%20Dive.md) · [04 - AWS Service Quotas SRE Operations](04%20-%20AWS%20Service%20Quotas%20SRE%20Operations.md) · [01 - AWS Trusted Advisor Intro bits & bytes](01%20-%20AWS%20Trusted%20Advisor%20Intro%20bits%20%26%20bytes.md)

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

- **Soft limits → request increase**; hard limits → architect around.
- **vCPU quota** is the real ceiling for EC2/ASG scaling.
- **Templates** auto-apply increases to new org accounts.
- **CloudWatch utilization alarms** + **Trusted Advisor** for early warning.
- Per service / per Region / per account scope.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                                        | Points to                                          |
| :------------------------------------------------------------ | :------------------------------------------------- |
| "hit a limit", "can't launch more", "request more"            | **Service Quotas increase**                        |
| "ASG won't scale past N" / "Lambda throttling at concurrency" | **vCPU / concurrency quota**                       |
| "automatically raise limits for new accounts"                 | **Quota request templates**                        |
| "warn before reaching a limit"                                | **Trusted Advisor / CloudWatch utilization alarm** |
| "limit can't be increased"                                    | **Hard limit → architect around**                  |
| "per region/account"                                          | **Quota scope**                                    |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Blaming the **ASG max** when the **account vCPU quota** is the cause.
- Thinking all limits are raisable (some are **hard**).
- Using Trusted Advisor to **raise** a limit (it only warns).
- Forgetting **per-region** scope (raised in one region ≠ another).
- Ignoring **templates** for multi-account.

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **"Need more of X / launch failing"** → soft limit → Service Quotas increase.
2. **"Can't be raised"** → hard limit → spread across accounts/regions.
3. **"Warn me early"** → CloudWatch utilization alarm / Trusted Advisor.
4. **"New accounts"** → quota request templates.
5. **Region matters** — confirm the quota is raised in the right region.

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** ASG stops at 20 instances though max=50 and demand is high; activity shows launch failures.
**Options:** A) Raise max again B) Request EC2 vCPU quota increase (Service Quotas) C) Add AZ D) Smaller instances
**Correct:** B
**Explanation:** Account vCPU soft limit caps launches; raise it.

### Q2

**Scenario:** Lambda functions throttle under load at a concurrency ceiling.
**Options:** A) More memory B) Request concurrency quota increase C) New account D) Bigger functions
**Correct:** B
**Explanation:** Concurrency is a soft quota.

### Q3

**Scenario:** Auto-apply standard quota increases to every new org account.
**Options:** A) Manual per account B) Quota request templates C) SCP D) Budget
**Correct:** B
**Explanation:** Templates apply org-wide to new accounts.

### Q4

**Scenario:** Be warned at 80% of a quota.
**Options:** A) Nothing B) CloudWatch utilization alarm (and/or Trusted Advisor) C) Config D) CloudTrail
**Correct:** B
**Explanation:** Utilization metrics → alarm.

### Q5

**Scenario:** A limit "cannot be increased."
**Options:** A) Open a case anyway B) Hard limit — architect across accounts/regions C) Ignore D) Use root
**Correct:** B
**Explanation:** Hard limits require design changes.

### Q6

**Scenario:** Who warns vs who raises a limit?
**Options:** A) Both Trusted Advisor B) TA warns, Service Quotas raises C) Config D) CloudTrail
**Correct:** B
**Explanation:** Division of roles.

### Q7

**Scenario:** Raised the EC2 quota in us-east-1 but eu-west-1 still fails.
**Options:** A) Bug B) Quotas are per-region; raise in eu-west-1 too C) Raise globally D) New account
**Correct:** B
**Explanation:** Quotas are per-region.

### Q8

**Scenario:** Programmatically submit an increase.
**Options:** A) Console only B) request-service-quota-increase API C) CloudTrail D) Budget
**Correct:** B
**Explanation:** API supports automation.

### Q9

**Scenario:** Avoid surprise spend after raising limits.
**Options:** A) Nothing B) Pair with Budgets/alerts C) Lower max D) Disable scaling
**Correct:** B
**Explanation:** Higher limits enable more chargeable resources.

### Q10

**Scenario:** Can't create another VPC in a region.
**Options:** A) Hard limit always B) VPCs-per-region soft quota — request increase C) New account only D) Delete subnets
**Correct:** B
**Explanation:** VPCs-per-region is adjustable.

### Q11

**Scenario:** Track approval status of a quota request.
**Options:** A) Guess B) list-requested-service-quota-change-history C) CloudWatch D) Config
**Correct:** B
**Explanation:** Request history API.

### Q12

**Scenario:** Some increases apply instantly, others take time.
**Options:** A) Bug B) Auto-approval vs Support review C) Region issue D) IAM
**Correct:** B
**Explanation:** Approval path varies by quota.

### Q13

**Scenario:** Central team manages quotas without management-account daily use.
**Options:** A) Root B) Delegated administration C) IAM user D) Per account
**Correct:** B
**Explanation:** Delegated admin supported.

### Q14

**Scenario:** EIP allocation fails at limit.
**Options:** A) Hard limit B) EIP soft quota — request increase (or release unused) C) New region D) Nothing
**Correct:** B
**Explanation:** EIPs are a soft quota.

### Q15

**Scenario:** Cost of using Service Quotas.
**Options:** A) Per request B) Free C) Per quota D) Per region
**Correct:** B
**Explanation:** The service is free.

### Q16

**Scenario:** Where to see current usage vs limit.
**Options:** A) CloudTrail B) Service Quotas (+ CloudWatch utilization) C) Config D) Budgets
**Correct:** B
**Explanation:** Service Quotas shows applied value; CloudWatch shows utilization.

### Q17

**Scenario:** Pre-empt a big launch event needing many instances.
**Options:** A) React on failure B) Request vCPU increase ahead of time C) Add AZs only D) Smaller instances
**Correct:** B
**Explanation:** Proactive increase avoids launch failures.

### Q18

**Scenario:** Standardize limits across a landing zone.
**Options:** A) Manual B) Quota templates + Account Factory C) SCP D) CloudTrail
**Correct:** B
**Explanation:** Templates baseline new accounts.

### Q19

**Scenario:** Audit who requested a quota increase.
**Options:** A) Config B) CloudTrail C) CloudWatch D) Budgets
**Correct:** B
**Explanation:** API calls are in CloudTrail.

### Q20

**Scenario:** Restrict who can raise quotas.
**Options:** A) Everyone B) IAM least-privilege on servicequotas actions C) Root only D) Open
**Correct:** B
**Explanation:** Scope quota actions via IAM.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** A Black Friday event needs to triple EC2 capacity for 24 hours. The ASG is configured but the team fears hitting limits mid-event.
**Options:** A) Hope it scales B) **Proactively request the EC2 vCPU quota increase** (in the right regions) days ahead; set a **CloudWatch utilization alarm**; validate with a scale test C) Raise ASG max only D) Smaller instances
**Correct:** B
**Explanation:** vCPU quota is the true ceiling; raise it ahead of time (per region), alarm on utilization, and test.

### H2

**Scenario:** A workload needs far more of a resource than any single account's hard limit allows.
**Options:** A) Open more cases B) The limit is **hard** — distribute across **multiple accounts/regions** (and use Organizations to manage) C) Wait D) Use root
**Correct:** B
**Explanation:** Hard limits can't be raised; horizontal distribution across accounts/regions is the architecture.

### H3

**Scenario:** A landing zone vends dozens of accounts; each needs higher default limits without manual requests.
**Options:** A) Manual per account B) **Quota request templates** applied org-wide so new accounts auto-request increases C) SCP D) Budgets
**Correct:** B
**Explanation:** Templates automate per-account increases at vend time. See [01 - AWS Account Factory and Landing Zone Intro bits & bytes](01%20-%20AWS%20Account%20Factory%20and%20Landing%20Zone%20Intro%20bits%20%26%20bytes.md).

### H4

**Scenario:** The team wants automatic increase requests when utilization crosses 80%, with approval tracking.
**Options:** A) Manual checks B) CloudWatch alarm on `AWS/Usage` → Lambda calls `request-service-quota-increase` → track via history API → notify C) Trusted Advisor only D) Nothing
**Correct:** B
**Explanation:** Event-driven auto-request + history tracking automates quota management.

### H5

**Scenario:** Raising a quota in production caused unexpected spend as teams launched far more resources.
**Options:** A) Lower the quota again B) Keep the needed limit but add **Budgets/anomaly alerts** and SCP/tag guardrails so higher limits don't mean uncontrolled spend C) Block scaling D) Manual approvals for all launches
**Correct:** B
**Explanation:** Limits enable capacity; cost control is a separate guardrail (Budgets/SCP), not lowering needed quotas.

### H6

**Scenario:** Multi-region active/active app fails to scale in the secondary region during failover.
**Options:** A) Assume same as primary B) **Quotas are per-region** — ensure the secondary region's vCPU/EIP/etc. quotas are raised to match before relying on failover C) New account D) Smaller instances
**Correct:** B
**Explanation:** Per-region quotas must be pre-raised in DR/secondary regions or failover capacity is capped.

### H7

**Scenario:** Security wants only a central platform team to raise quotas, audited.
**Options:** A) Everyone B) IAM least-privilege on `servicequotas:RequestServiceQuotaIncrease` to the platform role; **CloudTrail** audit C) Root D) Open access
**Correct:** B
**Explanation:** Scope the action via IAM and audit via CloudTrail.

### H8

**Scenario:** A quota increase request is stuck pending and the event is imminent.
**Options:** A) Wait indefinitely B) Escalate via **AWS Support** (Business/Enterprise) for the Support-reviewed quota; meanwhile mitigate (spread regions/types) C) Ignore D) Use root
**Correct:** B
**Explanation:** Some quotas need Support review; escalate and mitigate in parallel.

### H9

**Scenario:** Leadership wants a dashboard of utilization vs limits across critical quotas org-wide.
**Options:** A) Manual spreadsheet B) CloudWatch **AWS/Usage** utilization metrics (per account/region) aggregated into a dashboard (e.g. central observability/Grafana) C) Trusted Advisor only D) Config
**Correct:** B
**Explanation:** Utilization metrics feed dashboards for proactive capacity governance.

### H10

**Scenario:** A team repeatedly hits the same limits across many services right before incidents.
**Options:** A) React each time B) Establish a **proactive quota program**: utilization alarms at 80%, standard templates, scheduled reviews before known peaks, automation for requests C) Bigger instances D) Ignore
**Correct:** B
**Explanation:** Operationalize quota management (alarms + templates + cadence + automation) to prevent recurring limit incidents.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Hit a limit → soft quota → request increase in Service Quotas (per region!). Can't raise → hard limit → spread across accounts/regions. New accounts → quota templates. Warn early → CloudWatch utilization alarm / Trusted Advisor. ASG won't scale → check vCPU quota first.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - AWS Service Quotas SRE Operations](04%20-%20AWS%20Service%20Quotas%20SRE%20Operations.md).
