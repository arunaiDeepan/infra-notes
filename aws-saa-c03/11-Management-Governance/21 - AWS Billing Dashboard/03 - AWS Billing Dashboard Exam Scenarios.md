# AWS Billing Dashboard - Exam Scenarios

> Exam focus: consolidated billing + shared discounts, billing alarm in us-east-1, IAM access to billing, Cost Categories, and which cost tool for which job. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - AWS Billing Dashboard Intro bits & bytes](01%20-%20AWS%20Billing%20Dashboard%20Intro%20bits%20%26%20bytes.md) · [02 - AWS Billing Dashboard Deep Dive](02%20-%20AWS%20Billing%20Dashboard%20Deep%20Dive.md) · [04 - AWS Billing Dashboard SRE Operations](04%20-%20AWS%20Billing%20Dashboard%20SRE%20Operations.md) · [01 - AWS Budgets Fundamentals & Architecture](01%20-%20AWS%20Budgets%20Fundamentals%20%26%20Architecture.md)

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

- **Consolidated billing** → one bill + **aggregated volume discounts** + **shared RIs/SP**.
- **Billing alarm only in us-east-1**.
- Activate **IAM access to billing** (don't use root).
- **Cost Categories** group accounts/tags for reporting without re-tagging.
- Billing Dashboard (hub) vs Budgets (alert/act) vs Cost Explorer (analyze) vs CUR (raw).

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                                          | Points to                                          |
| :-------------------------------------------------------------- | :------------------------------------------------- |
| "one bill for all accounts", "volume discounts across accounts" | **Consolidated billing**                           |
| "share Reserved Instances/Savings Plans across accounts"        | **Consolidated billing (discount sharing)**        |
| "alarm when estimated charges exceed $X"                        | **CloudWatch billing alarm (us-east-1)** / Budgets |
| "let finance see billing without root"                          | **Activate IAM billing access**                    |
| "group accounts/teams for cost reporting without re-tagging"    | **Cost Categories**                                |
| "break down cost by tag"                                        | **Cost allocation tags**                           |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Creating a billing alarm in the **wrong region** (must be us-east-1).
- Using **root** for billing access instead of delegating via IAM.
- Choosing the **Billing Dashboard** for threshold _actions_ (that's Budgets).
- Expecting members to see the **consolidated** bill (they see their own).
- Re-tagging resources when **Cost Categories** would group them.

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **"One bill + discounts across accounts"** → consolidated billing.
2. **"Alarm on charges"** → billing alarm in us-east-1 / Budgets.
3. **"Finance access without root"** → activate IAM billing access.
4. **"Group for reporting, no re-tag"** → Cost Categories.
5. **"Alert/act vs analyze vs raw"** → Budgets / Cost Explorer / CUR.

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** One bill and combined volume discounts across 20 accounts.
**Options:** A) Separate billing B) Consolidated billing via Organizations C) Cost Explorer D) Budgets
**Correct:** B
**Explanation:** Consolidated billing aggregates usage/discounts.

### Q2

**Scenario:** Share Savings Plans discounts across member accounts.
**Options:** A) Per-account only B) Consolidated billing discount sharing C) CUR D) Cost Categories
**Correct:** B
**Explanation:** Commitments apply org-wide under consolidated billing.

### Q3

**Scenario:** Alarm when estimated charges exceed $1,000.
**Options:** A) Any region B) CloudWatch billing alarm in us-east-1 (or Budgets) C) Config D) CloudTrail
**Correct:** B
**Explanation:** Billing metrics are in us-east-1.

### Q4

**Scenario:** Let the finance team view billing without using root.
**Options:** A) Share root B) Activate IAM access to billing + IAM policy C) New account D) SCP
**Correct:** B
**Explanation:** Delegate billing via IAM.

### Q5

**Scenario:** Report costs grouped as "Platform" vs "Customer" without re-tagging.
**Options:** A) Re-tag all B) Cost Categories C) Budgets D) CUR only
**Correct:** B
**Explanation:** Cost Categories group via rules.

### Q6

**Scenario:** Alert AND stop resources at a spend threshold.
**Options:** A) Billing Dashboard B) Budgets (with budget actions) C) Cost Explorer D) CUR
**Correct:** B
**Explanation:** Budgets does alerts + actions.

### Q7

**Scenario:** Analyze 12-month cost trends and forecast.
**Options:** A) Billing Dashboard B) Cost Explorer C) Budgets D) CUR
**Correct:** B
**Explanation:** Cost Explorer analyzes/forecasts.

### Q8

**Scenario:** Feed granular line items into a BI tool.
**Options:** A) Billing Dashboard B) Cost & Usage Report (CUR) C) Budgets D) Cost Explorer
**Correct:** B
**Explanation:** CUR is the raw data source.

### Q9

**Scenario:** Member account wants to see the org's total bill.
**Options:** A) They can B) They can't — only the payer sees consolidated C) Via CUR D) Via Budgets
**Correct:** B
**Explanation:** Members see their own costs, not the consolidated bill.

### Q10

**Scenario:** Break down spend by CostCenter tag.
**Options:** A) Cost Categories only B) Activate the CostCenter cost allocation tag C) Budgets D) CUR raw only
**Correct:** B
**Explanation:** Cost allocation tag activation enables tag breakdown.

### Q11

**Scenario:** Re-bill internal teams at custom rates (MSP/enterprise).
**Options:** A) Cost Explorer B) AWS Billing Conductor C) Budgets D) CUR
**Correct:** B
**Explanation:** Billing Conductor does custom chargeback rates.

### Q12

**Scenario:** Receive PDF invoices automatically.
**Options:** A) Not possible B) Billing preferences / invoice config C) Budgets D) Config
**Correct:** B
**Explanation:** Configure in billing preferences.

### Q13

**Scenario:** Track Free Tier usage and get warned near limits.
**Options:** A) Cost Explorer B) Free Tier usage alerts (Billing) C) CUR D) Config
**Correct:** B
**Explanation:** Free Tier alerts live in Billing.

### Q14

**Scenario:** Per-account budgets across the org.
**Options:** A) One global budget B) Budgets per account/OU (filtered) C) CUR D) Cost Categories only
**Correct:** B
**Explanation:** Budgets can scope per account/OU.

### Q15

**Scenario:** Why didn't last quarter's tag breakdown appear after activating tags?
**Options:** A) Bug B) Cost allocation tags aren't retroactive C) Wrong region D) Need CUR
**Correct:** B
**Explanation:** Activation isn't retroactive.

### Q16

**Scenario:** Protect the payer account.
**Options:** A) Share widely B) Minimal use, MFA on root, least-privilege billing IAM C) Run workloads there D) Open access
**Correct:** B
**Explanation:** Payer/management account hygiene.

### Q17

**Scenario:** Combined S3 usage reaches lower price tiers faster.
**Options:** A) Per account B) Consolidated billing aggregates usage for tiering C) CUR D) Budgets
**Correct:** B
**Explanation:** Tiered pricing on combined usage.

### Q18

**Scenario:** Where to start to enable billing alarms.
**Options:** A) CloudTrail B) Billing preferences: "Receive Billing Alerts" C) Config D) Budgets only
**Correct:** B
**Explanation:** Enable alerts in billing preferences first.

### Q19

**Scenario:** Separate invoices per linked account.
**Options:** A) Not possible B) Invoice configuration for org members C) CUR D) Budgets
**Correct:** B
**Explanation:** Invoice config supports per-account invoicing where available.

### Q20

**Scenario:** Forecasted (not just actual) overspend alert.
**Options:** A) Billing alarm only B) Budgets with forecasted threshold C) CUR D) Cost Categories
**Correct:** B
**Explanation:** Budgets supports forecasted thresholds.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** A 40-account enterprise wants one bill, maximum discount leverage, per-team chargeback, and budget alerts — without re-tagging everything.
**Options:** A) Separate accounts/bills B) **Consolidated billing** (shared RIs/SP, volume tiers) + **Cost Categories** (team grouping) + **cost allocation tags** where available + **Budgets** per category C) Manual D) CUR only
**Correct:** B
**Explanation:** Consolidated billing maximizes discounts; Cost Categories enable chargeback without re-tagging; Budgets alert per group.

### H2

**Scenario:** A billing alarm created in eu-west-1 never fires despite overspend.
**Options:** A) AWS bug B) Billing metrics publish **only in us-east-1** — create the alarm there (and enable billing alerts) C) Wrong threshold D) Use Config
**Correct:** B
**Explanation:** `EstimatedCharges` is us-east-1 only.

### H3

**Scenario:** Finance needs billing visibility but the company forbids root usage for daily work.
**Options:** A) Share root B) **Activate IAM access to billing** and grant least-privilege billing/cost policies to FinOps roles C) New account D) SCP
**Correct:** B
**Explanation:** Delegate billing via IAM rather than using root.

### H4

**Scenario:** An MSP must re-bill customers at custom rates different from AWS's actual charges, per billing group.
**Options:** A) Cost Explorer exports B) **AWS Billing Conductor** to apply custom rates and produce pro-forma invoices per group C) CUR math D) Budgets
**Correct:** B
**Explanation:** Billing Conductor is purpose-built for custom chargeback/re-billing.

### H5

**Scenario:** Leadership wants both proactive alerts and the ability to halt non-prod spend automatically at a threshold.
**Options:** A) Billing alarm only B) **Budgets** with alerts **and budget actions** (apply restrictive SCP/IAM or stop resources) C) Cost Explorer D) CUR
**Correct:** B
**Explanation:** Budgets actions enforce; the dashboard/alarm only observes. See [01 - AWS Budgets Fundamentals & Architecture](01%20-%20AWS%20Budgets%20Fundamentals%20%26%20Architecture.md).

### H6

**Scenario:** Per-team cost breakdown is impossible because tags weren't activated and many resources are untagged.
**Options:** A) Give up B) Activate **cost allocation tags** now (not retroactive), bulk-tag via Tag Editor, use **Cost Categories** for grouping, reconstruct history from **CUR** where feasible C) Estimate D) Re-tag history
**Correct:** B
**Explanation:** Combine activation + remediation + Cost Categories + CUR for attribution going forward and partial history.

### H7

**Scenario:** A member-account owner complains they can't see the organization's total spend.
**Options:** A) Grant them payer access B) **By design** — members see their own costs; consolidated view is the payer's; share reports if needed C) Bug D) New org
**Correct:** B
**Explanation:** Consolidated billing visibility is the payer's; share curated reports to members.

### H8

**Scenario:** A regulated org needs auditable, separated invoices per business unit account and controlled billing access.
**Options:** A) One invoice B) **Invoice configuration** per linked account + **IAM-delegated** billing access + Cost Categories for BU reporting C) Manual splitting D) CUR only
**Correct:** B
**Explanation:** Per-account invoicing + delegated access + categories meet audit/separation needs.

### H9

**Scenario:** The company wants combined Savings Plans coverage but some teams fear another team will "use up" their discount.
**Options:** A) Per-account SP only B) Consolidated billing shares SP/RI by default; **toggle discount sharing** off for specific accounts if isolation is required C) No commitments D) CUR
**Correct:** B
**Explanation:** Discount sharing is configurable per account when isolation is needed.

### H10

**Scenario:** Leadership wants a single monthly executive view: spend by product line, trend, forecast, and anomalies.
**Options:** A) Raw invoices B) **Cost Categories** (product-line grouping) feeding **Cost Explorer** (trend/forecast) + **Cost Anomaly Detection**; Budgets for guardrails C) CUR spreadsheets D) Billing Dashboard only
**Correct:** B
**Explanation:** Categories organize, Cost Explorer/anomaly detection analyze, Budgets guard — the dashboard is the hub tying them together.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **One bill + shared discounts across accounts → consolidated billing (payer sees all; members see own). Billing alarm → us-east-1 only. Delegate billing → activate IAM access (not root). Group for reporting without re-tagging → Cost Categories. Alert/act → Budgets; analyze → Cost Explorer; raw → CUR.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - AWS Billing Dashboard SRE Operations](04%20-%20AWS%20Billing%20Dashboard%20SRE%20Operations.md).
