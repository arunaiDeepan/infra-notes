# AWS License Manager - Exam Scenarios

> Exam focus: BYOL compliance, hard vs soft enforcement, Dedicated Hosts for license-bound software, and cross-account tracking. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - AWS License Manager Intro bits & bytes](01%20-%20AWS%20License%20Manager%20Intro%20bits%20%26%20bytes.md) · [02 - AWS License Manager Deep Dive](02%20-%20AWS%20License%20Manager%20Deep%20Dive.md) · [04 - AWS License Manager SRE Operations](04%20-%20AWS%20License%20Manager%20SRE%20Operations.md) · [06 - IAM Identity Center & Organizations](06%20-%20IAM%20Identity%20Center%20%26%20Organizations.md)

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

- **BYOL tracking + enforcement** by vCPU/core/socket/instance.
- **Hard** (block) vs **soft** (alert) enforcement.
- **Dedicated Hosts** for licenses needing physical isolation/core visibility.
- **Organizations** cross-account license tracking.
- It manages **licenses**, not performance/cost sizing.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                                  | Points to                                  |
| :------------------------------------------------------ | :----------------------------------------- |
| "BYOL", "track software licenses", "license compliance" | **License Manager**                        |
| "prevent exceeding license limit on launch"             | **Hard enforcement**                       |
| "allow but alert when over license"                     | **Soft enforcement**                       |
| "license requires physical cores/sockets / dedicated"   | **Dedicated Hosts (Host Resource Groups)** |
| "track licenses across all accounts"                    | **Organizations integration**              |
| "avoid audit penalties for over-deployment"             | **License Manager**                        |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Using License Manager for **right-sizing/cost** (that's Compute Optimizer/Cost Explorer).
- Choosing **license-included** when **BYOL** tracking is required (and vice versa).
- Forgetting **Dedicated Hosts** for core/socket-bound licenses.
- Manual spreadsheets for compliance instead of automated tracking.
- Soft enforcement when the scenario demands **guaranteed** compliance (use hard).

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **"BYOL / license compliance / track licenses"** → License Manager.
2. **"Never exceed"** → hard enforcement; **"allow + alert"** → soft.
3. **"Physical cores/sockets/isolation required"** → Dedicated Hosts.
4. **"Across accounts"** → Organizations integration.
5. **"Right-size/cost"** → not License Manager (Compute Optimizer/Cost Explorer).

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** Track BYOL SQL Server usage and prevent exceeding owned cores.
**Options:** A) Manual B) License Manager with hard enforcement C) Compute Optimizer D) Budgets
**Correct:** B
**Explanation:** BYOL tracking + hard enforcement.

### Q2

**Scenario:** Allow launches but alert when over the license limit.
**Options:** A) Hard B) Soft enforcement C) No tracking D) Dedicated Hosts
**Correct:** B
**Explanation:** Soft enforcement alerts without blocking.

### Q3

**Scenario:** A BYOL license requires physical-core visibility and isolation.
**Options:** A) Shared tenancy B) Dedicated Hosts (Host Resource Groups) C) Spot D) Compute Optimizer
**Correct:** B
**Explanation:** Dedicated Hosts provide physical isolation/core visibility.

### Q4

**Scenario:** Track license consumption across 20 accounts centrally.
**Options:** A) Per account B) Organizations integration C) Budgets D) Config
**Correct:** B
**Explanation:** Org integration centralizes tracking.

### Q5

**Scenario:** Automatically count usage as instances launch from a BYOL AMI.
**Options:** A) Manual count B) Associate a license configuration with the AMI C) Tag only D) Budgets
**Correct:** B
**Explanation:** Association enables automatic counting.

### Q6

**Scenario:** Avoid audit penalties for accidental over-deployment.
**Options:** A) Spreadsheet B) License Manager hard enforcement C) Compute Optimizer D) Trusted Advisor
**Correct:** B
**Explanation:** Hard enforcement prevents breach.

### Q7

**Scenario:** Right-size instances to cut cost.
**Options:** A) License Manager B) Compute Optimizer C) Budgets D) Config
**Correct:** B
**Explanation:** Right-sizing is Compute Optimizer, not licenses.

### Q8

**Scenario:** Manage Dedicated Hosts automatically for license-bound workloads.
**Options:** A) Manual host allocation B) License Manager Host Resource Groups C) Spot D) ASG
**Correct:** B
**Explanation:** Host Resource Groups automate Dedicated Hosts.

### Q9

**Scenario:** Distribute Marketplace licenses to accounts programmatically.
**Options:** A) Email keys B) License Manager managed entitlements C) S3 D) Budgets
**Correct:** B
**Explanation:** Managed entitlements distribute seller licenses.

### Q10

**Scenario:** Counting basis for socket-licensed software.
**Options:** A) vCPU B) Sockets C) Instances D) GB
**Correct:** B
**Explanation:** Configure socket counting.

### Q11

**Scenario:** Discover software (incl. on-prem) for license tracking.
**Options:** A) Manual B) Systems Manager inventory + License Manager C) Budgets D) Config only
**Correct:** B
**Explanation:** SSM inventory feeds license tracking.

### Q12

**Scenario:** Audit changes to a license configuration.
**Options:** A) Config B) CloudTrail C) Budgets D) None
**Correct:** B
**Explanation:** CloudTrail logs the API calls.

### Q13

**Scenario:** Notify when nearing a license limit.
**Options:** A) None B) CloudWatch/SNS via License Manager C) Config D) Budgets
**Correct:** B
**Explanation:** Usage alarms/notifications.

### Q14

**Scenario:** Software is fully license-included by AWS.
**Options:** A) Track in License Manager B) No BYOL tracking needed C) Dedicated Hosts D) Soft enforce
**Correct:** B
**Explanation:** License-included needs no BYOL tracking.

### Q15

**Scenario:** Guarantee compliance even if it blocks a launch.
**Options:** A) Soft B) Hard enforcement C) No tracking D) Tag
**Correct:** B
**Explanation:** Hard enforcement blocks over-limit.

### Q16

**Scenario:** Share license configs across accounts.
**Options:** A) Copy B) Organizations + RAM sharing C) Email D) Budgets
**Correct:** B
**Explanation:** RAM/Org sharing.

### Q17

**Scenario:** Reclaim wasted unused licenses.
**Options:** A) Ignore B) Track under-utilization in License Manager C) Compute Optimizer D) Budgets
**Correct:** B
**Explanation:** Usage tracking surfaces under-use.

### Q18

**Scenario:** Enforce dedicated tenancy required by a license.
**Options:** A) Shared B) License configuration tenancy rule + Dedicated Hosts C) Spot D) ASG
**Correct:** B
**Explanation:** Tenancy rules + Dedicated Hosts.

### Q19

**Scenario:** Associate licensing with a launch template.
**Options:** A) Not possible B) Attach the license configuration to the launch template/AMI C) Tag only D) Budgets
**Correct:** B
**Explanation:** Associate with launch artifacts.

### Q20

**Scenario:** Cost driver for some BYOL setups.
**Options:** A) License Manager fees B) Dedicated Hosts C) CloudTrail D) Config
**Correct:** B
**Explanation:** Dedicated Hosts cost; License Manager is free.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** An enterprise runs BYOL Oracle/SQL Server and faces a vendor audit; they must prove they never exceed owned cores and isolate workloads on physical cores.
**Options:** A) Spreadsheet B) License Manager **core-counting** configs with **hard enforcement** on **Dedicated Hosts** (Host Resource Groups), centralized via Organizations; CloudTrail audit C) Soft enforce only D) Compute Optimizer
**Correct:** B
**Explanation:** Core counting + hard enforcement + Dedicated Hosts + central tracking gives provable, isolated compliance.

### H2

**Scenario:** Blocking launches would harm availability during peak, but the team still needs license visibility and remediation.
**Options:** A) Hard enforce B) **Soft enforcement** with alerts + a remediation process to bring usage back under limit C) No tracking D) Delete licenses
**Correct:** B
**Explanation:** Soft enforcement preserves availability while alerting; remediate over-use promptly.

### H3

**Scenario:** Across 30 accounts, license usage is invisible and teams keep over-deploying.
**Options:** A) Per-account spreadsheets B) **Organizations** integration: centralize license configs, share via RAM, track consumption org-wide, enforce per policy C) Manual D) Budgets
**Correct:** B
**Explanation:** Org integration gives the central, enforceable, cross-account license picture.

### H4

**Scenario:** Marketplace ISV must grant/revoke software entitlements to customer accounts programmatically.
**Options:** A) Email keys B) License Manager **managed entitlements** (seller-issued) to distribute/revoke C) IAM only D) S3
**Correct:** B
**Explanation:** Managed entitlements handle programmatic distribution/revocation.

### H5

**Scenario:** Finance suspects the company over-bought licenses; they want to reclaim unused entitlements.
**Options:** A) Renew everything B) Use License Manager **consumption tracking** to find under-utilization; reclaim/avoid renewing unused C) Compute Optimizer D) Budgets
**Correct:** B
**Explanation:** Usage data reveals over-buying for reclamation.

### H6

**Scenario:** License-bound instances must always land on compliant Dedicated Hosts without manual host management.
**Options:** A) Manual allocation B) **Host Resource Groups** in License Manager auto-allocate/manage Dedicated Hosts with the right affinity/tenancy C) Shared tenancy D) Spot
**Correct:** B
**Explanation:** Host Resource Groups automate compliant host placement.

### H7

**Scenario:** A hybrid estate (on-prem + AWS) needs one license-compliance view.
**Options:** A) Two systems B) **Systems Manager inventory** discovers on-prem + EC2 usage feeding License Manager for a unified view C) Manual D) Config only
**Correct:** B
**Explanation:** SSM inventory extends license tracking to on-prem.

### H8

**Scenario:** Auditors want proof of who changed license limits and when.
**Options:** A) License Manager only B) **CloudTrail** records license config/consumption API changes for audit C) Budgets D) Config snapshot
**Correct:** B
**Explanation:** CloudTrail provides the change audit trail.

### H9

**Scenario:** A team confuses License Manager with cost optimization and expects it to right-size instances.
**Options:** A) It does B) Clarify scope: License Manager governs **licenses/compliance**; use **Compute Optimizer/Cost Explorer** for right-sizing/cost C) Disable it D) Budgets
**Correct:** B
**Explanation:** Different domains — licenses vs sizing/cost.

### H10

**Scenario:** A regulated workload must guarantee compliance AND record every enforcement decision for evidence.
**Options:** A) Soft + memory B) **Hard enforcement** (guarantee) + **CloudTrail** + License Manager reports for evidence; central via Organizations C) Spreadsheet D) Config only
**Correct:** B
**Explanation:** Hard enforcement guarantees; CloudTrail + reports provide auditable evidence.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **BYOL track + enforce by vCPU/core/socket/instance → License Manager. Never exceed → hard enforcement; allow + alert → soft. Physical-core/isolation licenses → Dedicated Hosts (Host Resource Groups). Cross-account → Organizations. It governs licenses, not sizing/cost.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - AWS License Manager SRE Operations](04%20-%20AWS%20License%20Manager%20SRE%20Operations.md).
