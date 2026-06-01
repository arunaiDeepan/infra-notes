# AWS Trusted Advisor - Exam Scenarios

> Exam focus: the support-plan gating, the 5 categories, service-limit warnings, and TA vs Well-Architected vs Config vs Compute Optimizer. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - AWS Trusted Advisor Intro bits & bytes](01%20-%20AWS%20Trusted%20Advisor%20Intro%20bits%20%26%20bytes.md) · [02 - AWS Trusted Advisor Deep Dive](02%20-%20AWS%20Trusted%20Advisor%20Deep%20Dive.md) · [04 - AWS Trusted Advisor SRE Operations](04%20-%20AWS%20Trusted%20Advisor%20SRE%20Operations.md) · [01 - AWS Well-Architected Tool Intro bits & bytes](01%20-%20AWS%20Well-Architected%20Tool%20Intro%20bits%20%26%20bytes.md)

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

- **Support-plan gating**: full checks/API/EventBridge need **Business/Enterprise**; Basic/Developer get **core** (incl. all service-limit checks).
- The **5 categories** (cost, performance, security, fault tolerance, service limits).
- **Service-limit early warning** (paired with Service Quotas).
- **Organizational view** (Enterprise) for org-wide findings.
- TA (automated checks) vs Well-Architected (review) vs Config (custom compliance) vs Compute Optimizer (right-sizing).

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                            | Points to                                         |
| :------------------------------------------------ | :------------------------------------------------ |
| "automated best-practice checks", "no setup"      | **Trusted Advisor**                               |
| "full set of checks / API access / notifications" | **Business or Enterprise Support**                |
| "approaching service limit/quota"                 | **TA Service Limits** (+ Service Quotas to raise) |
| "across all accounts in the org"                  | **Organizational view (Enterprise)**              |
| "idle/unattached/underutilized resources"         | **TA Cost Optimization**                          |
| "public S3 / open security group / root MFA"      | **TA Security**                                   |
| "structured architecture review"                  | **Well-Architected Tool** (not TA)                |
| "custom compliance rule"                          | **Config** (not TA)                               |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Expecting **full** checks on Basic/Developer support.
- Choosing TA for **custom compliance rules** (that's Config).
- Choosing TA for a **structured review** (that's Well-Architected).
- Choosing TA to **raise** a quota (TA warns; Service Quotas raises).
- Using TA for **deep right-sizing** (Compute Optimizer).

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **"Full checks/API/EventBridge"** → needs Business/Enterprise support.
2. **"Near a limit"** → TA Service Limits warns; **Service Quotas** raises.
3. **"Custom rule / continuous compliance"** → Config, not TA.
4. **"Architecture review"** → Well-Architected Tool.
5. **"Right-size instance"** → Compute Optimizer.

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** Get the full set of Trusted Advisor checks plus API access.
**Options:** A) Basic B) Business/Enterprise Support C) Developer D) Free tier
**Correct:** B
**Explanation:** Full checks + API/EventBridge require Business/Enterprise.

### Q2

**Scenario:** On Basic support, which checks are available?
**Options:** A) All B) Core (limited security + all service-limit checks) C) None D) Cost only
**Correct:** B
**Explanation:** Basic/Developer get core checks.

### Q3

**Scenario:** Warn when nearing the EC2 vCPU limit.
**Options:** A) Cost category B) Service Limits category C) Performance D) Security
**Correct:** B
**Explanation:** Service Limits checks approaching quotas.

### Q4

**Scenario:** Find idle load balancers and unattached EBS to cut cost.
**Options:** A) Security B) Cost Optimization category C) Performance D) Fault Tolerance
**Correct:** B
**Explanation:** Cost Optimization surfaces idle/unused resources.

### Q5

**Scenario:** Detect S3 buckets open to the public.
**Options:** A) Cost B) Security category C) Performance D) Limits
**Correct:** B
**Explanation:** Security checks include public S3 exposure.

### Q6

**Scenario:** Identify single-AZ RDS lacking Multi-AZ.
**Options:** A) Cost B) Fault Tolerance category C) Security D) Limits
**Correct:** B
**Explanation:** Fault Tolerance flags resilience gaps.

### Q7

**Scenario:** Aggregate findings across 40 accounts centrally.
**Options:** A) Per account B) Organizational view (Enterprise) C) Config D) Manual
**Correct:** B
**Explanation:** Org view rolls up findings (Enterprise Support).

### Q8

**Scenario:** Auto-notify when a security check turns red.
**Options:** A) Daily login B) EventBridge event → SNS/Lambda (Business/Enterprise) C) Manual D) Config
**Correct:** B
**Explanation:** TA emits EventBridge events on Business/Enterprise.

### Q9

**Scenario:** Need a structured architecture review against the framework.
**Options:** A) Trusted Advisor B) Well-Architected Tool C) Config D) Compute Optimizer
**Correct:** B
**Explanation:** Reviews are the Well-Architected Tool.

### Q10

**Scenario:** Enforce a custom org-specific compliance rule continuously.
**Options:** A) Trusted Advisor B) AWS Config rules C) Well-Architected D) Budgets
**Correct:** B
**Explanation:** Config supports custom rules; TA's checks are fixed.

### Q11

**Scenario:** Actually increase a quota TA flagged.
**Options:** A) Trusted Advisor B) Service Quotas request C) Config D) Budgets
**Correct:** B
**Explanation:** TA warns; Service Quotas raises.

### Q12

**Scenario:** Right-size an EC2 instance type with ML.
**Options:** A) Trusted Advisor B) Compute Optimizer C) Well-Architected D) Config
**Correct:** B
**Explanation:** Deep right-sizing is Compute Optimizer.

### Q13

**Scenario:** Verify root account has MFA enabled.
**Options:** A) Performance B) Security category C) Cost D) Limits
**Correct:** B
**Explanation:** Security includes root MFA check.

### Q14

**Scenario:** Reduce noise from an accepted public bucket (a static website).
**Options:** A) Disable TA B) Exclude/suppress the resource from the check C) Delete bucket D) Change support
**Correct:** B
**Explanation:** Resources can be excluded from checks.

### Q15

**Scenario:** Weekly summary of findings to the team.
**Options:** A) Manual B) Notification preferences (weekly email) C) Config D) CloudTrail
**Correct:** B
**Explanation:** TA sends weekly email summaries.

### Q16

**Scenario:** Programmatically pull check results into a dashboard.
**Options:** A) Scrape console B) Support API (Business/Enterprise) C) Config D) CloudTrail
**Correct:** B
**Explanation:** The Support API exposes check results.

### Q17

**Scenario:** Find underutilized RIs / low Savings Plans coverage.
**Options:** A) Security B) Cost Optimization checks C) Performance D) Limits
**Correct:** B
**Explanation:** Cost category covers commitment utilization.

### Q18

**Scenario:** Detect security groups with unrestricted access.
**Options:** A) Cost B) Security category C) Fault Tolerance D) Limits
**Correct:** B
**Explanation:** Open SGs are a security check.

### Q19

**Scenario:** Check S3 versioning/backup posture.
**Options:** A) Security B) Fault Tolerance category C) Cost D) Limits
**Correct:** B
**Explanation:** Backup/versioning posture is fault tolerance.

### Q20

**Scenario:** Lowest-cost way to get all service-limit warnings.
**Options:** A) Enterprise support B) Even Basic/Developer includes service-limit checks C) Pay per check D) Config
**Correct:** B
**Explanation:** Service-limit checks are in the core set on all plans.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** A 60-account org wants centralized, automated detection of public S3 and near-limit accounts, with auto-ticketing — at the lowest support spend that still enables this.
**Options:** A) Business support per account B) **Enterprise Support** (org view + API/EventBridge) in the management account; EventBridge → Lambda → ticketing; org-view reports C) Basic everywhere D) Config only
**Correct:** B
**Explanation:** Org view + API/EventBridge require Enterprise; automation pipes findings to tickets. (Config could complement for custom rules.)

### H2

**Scenario:** The team wants custom compliance rules (e.g. "all buckets must have a specific tag and KMS key") that Trusted Advisor doesn't check.
**Options:** A) Wait for TA to add it B) Use **AWS Config** custom/managed rules (+ conformance packs) for the custom policy; keep TA for broad best practices C) Manual audit D) Well-Architected
**Correct:** B
**Explanation:** TA checks are fixed; **Config** handles custom continuous compliance. Use both.

### H3

**Scenario:** Trusted Advisor flags approaching the EIP limit during a scaling event; the app then fails to launch instances.
**Options:** A) Ignore TA B) Heed the **Service Limits** warning early and request increases via **Service Quotas** (proactively, before peak) C) Add more accounts D) Disable the check
**Correct:** B
**Explanation:** TA is the early warning; Service Quotas raises the limit — act before the limit blocks scaling. See [01 - AWS Service Quotas Intro bits & bytes](01%20-%20AWS%20Service%20Quotas%20Intro%20bits%20%26%20bytes.md).

### H4

**Scenario:** Leadership wants a quantified, org-wide monthly cost-savings opportunity report from idle resources.
**Options:** A) Manual tally B) **Organizational view** cost checks exported (CSV/JSON), summarized monthly; pair with Compute Optimizer/Cost Explorer for depth C) CloudTrail D) Budgets only
**Correct:** B
**Explanation:** Org-view cost findings give the breadth; Compute Optimizer/Cost Explorer add right-sizing/forecast depth.

### H5

**Scenario:** Security team is overwhelmed by repeat findings on intentionally-public assets (a CDN origin bucket fronted by OAC).
**Options:** A) Disable security checks B) **Exclude** those specific resources from the relevant check (documented exception) so real issues stand out C) Lower support tier D) Ignore all
**Correct:** B
**Explanation:** Suppress accepted exceptions per-resource to reduce alert fatigue without blinding the check.

### H6

**Scenario:** A regulated org needs both broad posture checks AND a documented, periodic architecture review with risk tracking.
**Options:** A) Trusted Advisor only B) **Trusted Advisor** for continuous checks **+ Well-Architected Tool** for the periodic structured review (HRI tracking) C) Config only D) Compute Optimizer
**Correct:** B
**Explanation:** They serve different functions: automated checks vs structured review. See [01 - AWS Well-Architected Tool Intro bits & bytes](01%20-%20AWS%20Well-Architected%20Tool%20Intro%20bits%20%26%20bytes.md).

### H7

**Scenario:** The team wants TA findings to drive automated remediation, not just alerts.
**Options:** A) TA remediates itself B) EventBridge on TA status change → **SSM Automation/Lambda** remediation (e.g. close an open SG); audit via CloudTrail C) Manual D) Config snapshot
**Correct:** B
**Explanation:** TA detects; EventBridge + automation remediates. (Config remediation is an alternative for config-rule-based issues.)

### H8

**Scenario:** After downgrading from Business to Basic support to save money, dashboards lose most checks and API calls fail.
**Options:** A) AWS bug B) Expected — full checks + API require Business/Enterprise; only core checks remain on Basic C) Re-enable in console D) Region issue
**Correct:** B
**Explanation:** Check breadth and API access are support-plan-gated.

### H9

**Scenario:** A FinOps program wants to track whether flagged idle resources actually get cleaned up over time.
**Options:** A) Screenshots B) Pull TA cost checks via API on a schedule → time-series in a dashboard; correlate with Cost Explorer actuals C) Manual list D) Budgets only
**Correct:** B
**Explanation:** Scheduled API pulls build a trend of open vs resolved findings and realized savings.

### H10

**Scenario:** An enterprise wants a single security view combining Trusted Advisor security checks, GuardDuty, and Inspector findings.
**Options:** A) TA console only B) **Security Hub** to aggregate findings (incl. TA security checks) into one posture view with standards C) Config only D) Manual
**Correct:** B
**Explanation:** Security Hub centralizes findings across services; TA is one input. See [25 - GuardDuty Inspector Macie Security Hub](25%20-%20GuardDuty%20Inspector%20Macie%20Security%20Hub.md).

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Automated 5-pillar best-practice checks → Trusted Advisor. Full checks/API/EventBridge → Business/Enterprise; core (incl. all limits) → Basic/Developer. Near a limit → TA warns, Service Quotas raises. Custom compliance → Config. Architecture review → Well-Architected. Right-size → Compute Optimizer.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - AWS Trusted Advisor SRE Operations](04%20-%20AWS%20Trusted%20Advisor%20SRE%20Operations.md).
