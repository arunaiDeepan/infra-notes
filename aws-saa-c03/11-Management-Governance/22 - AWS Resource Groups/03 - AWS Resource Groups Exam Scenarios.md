# AWS Resource Groups - Exam Scenarios

> Exam focus: tag-based vs stack-based groups, SSM targeting by group, Tag Editor for bulk tagging, and groups vs tags vs Organizations. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - AWS Resource Groups Intro bits & bytes](01%20-%20AWS%20Resource%20Groups%20Intro%20bits%20%26%20bytes.md) · [02 - AWS Resource Groups Deep Dive](02%20-%20AWS%20Resource%20Groups%20Deep%20Dive.md) · [04 - AWS Resource Groups SRE Operations](04%20-%20AWS%20Resource%20Groups%20SRE%20Operations.md) · [01 - AWS Tagging Strategies Intro bits & bytes](01%20-%20AWS%20Tagging%20Strategies%20Intro%20bits%20%26%20bytes.md)

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

- **Tag-based (dynamic)** vs **stack-based** groups.
- Target **Systems Manager** operations by group/tag.
- **Tag Editor** + Tagging API for bulk tag management.
- Groups depend on a **tagging strategy**; same tags drive **ABAC** and **cost allocation**.
- Free; operational (not billing) construct.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                          | Points to                                       |
| :---------------------------------------------- | :---------------------------------------------- |
| "operate on a set of resources as a unit"       | **Resource Group**                              |
| "patch/run command on all instances with tag X" | **Resource Group + SSM**                        |
| "bulk add/fix tags across services"             | **Tag Editor / Tagging API**                    |
| "resources of a specific stack"                 | **Stack-based group**                           |
| "membership updates automatically when tagged"  | **Tag-based (dynamic) group**                   |
| "cost grouping/allocation"                      | **Cost allocation tags** (not the group itself) |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Treating Resource Groups as a **billing** feature (use cost allocation tags).
- Using explicit instance IDs when **tag/group targeting** is cleaner and dynamic.
- Confusing groups (resources) with **Organizations** (accounts/OUs).
- Forgetting **Tag Editor** for bulk remediation.
- Manual tagging when the **Tagging API** would scale.

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **"Act on a set of resources together"** → Resource Group (+ SSM).
2. **"Bulk tag fix"** → Tag Editor / Tagging API.
3. **"Stack's resources"** → stack-based group.
4. **"Cost grouping"** → cost allocation tags + Cost Explorer.
5. **"Accounts/OUs"** → Organizations, not Resource Groups.

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** Patch every instance tagged `Tier=web` as a unit, dynamically.
**Options:** A) List IDs manually B) Tag-based Resource Group + SSM Patch Manager C) Stack group D) Budgets
**Correct:** B
**Explanation:** Dynamic tag group targeted by SSM.

### Q2

**Scenario:** Bulk-correct inconsistent tags across many services and Regions.
**Options:** A) Edit each B) Tag Editor / Tagging API C) Config D) SCP
**Correct:** B
**Explanation:** Tag Editor does cross-service bulk edits.

### Q3

**Scenario:** Group exactly the resources created by one CloudFormation stack.
**Options:** A) Tag query B) Stack-based Resource Group C) Organizations D) Manual list
**Correct:** B
**Explanation:** Stack-based membership.

### Q4

**Scenario:** Membership should update as new resources get the tag.
**Options:** A) Static list B) Tag-based dynamic group C) Stack group D) Manual
**Correct:** B
**Explanation:** Tag-based groups are dynamic.

### Q5

**Scenario:** Cost grouping for chargeback.
**Options:** A) Resource Group billing B) Cost allocation tags + Cost Explorer/CUR C) Stack group D) Tag Editor only
**Correct:** B
**Explanation:** Cost grouping is via cost allocation tags.

### Q6

**Scenario:** Give a team a focused view of just their resources.
**Options:** A) Admin console B) Resource Group by their tag C) New account D) SCP
**Correct:** B
**Explanation:** Group scoped by team tag.

### Q7

**Scenario:** Programmatically find all resources with a tag.
**Options:** A) Scrape consoles B) Tagging API GetResources C) CloudTrail D) Config only
**Correct:** B
**Explanation:** GetResources queries by tag/type.

### Q8

**Scenario:** Cost of Resource Groups.
**Options:** A) Per group B) Free C) Per resource D) Per API
**Correct:** B
**Explanation:** Free.

### Q9

**Scenario:** Run a command on a dynamic set without updating IDs.
**Options:** A) Static targets B) SSM target = tag/Resource Group C) Lambda loop D) Manual
**Correct:** B
**Explanation:** Tag/group targeting stays current.

### Q10

**Scenario:** Manage accounts and OUs.
**Options:** A) Resource Groups B) Organizations C) Tag Editor D) Stack group
**Correct:** B
**Explanation:** Accounts/OUs are Organizations.

### Q11

**Scenario:** Use the same labels for access control and grouping.
**Options:** A) Separate systems B) Tags for both ABAC and Resource Groups C) IAM users D) SCP only
**Correct:** B
**Explanation:** Tags drive ABAC and groups.

### Q12

**Scenario:** Start/stop all dev resources nightly.
**Options:** A) Per resource B) Tag-based group + scheduled automation C) Stack only D) Budgets
**Correct:** B
**Explanation:** Group + automation toggles dev fleets.

### Q13

**Scenario:** Per-application metric view across services.
**Options:** A) Separate dashboards B) Resource Group insights / grouped CloudWatch C) Config D) CloudTrail
**Correct:** B
**Explanation:** Group-level views.

### Q14

**Scenario:** Ensure groups stay accurate as resources are created.
**Options:** A) Manual re-tagging B) Enforce required tags (tag policies/Config) C) Static lists D) Ignore
**Correct:** B
**Explanation:** Tag enforcement keeps dynamic groups correct.

### Q15

**Scenario:** Resource Group scope.
**Options:** A) Global accounts B) Regional resources (Tag Editor cross-Region for tags) C) Only EC2 D) Only S3
**Correct:** B
**Explanation:** Resources are regional; Tag Editor manages tags cross-Region.

### Q16

**Scenario:** Audit tag changes.
**Options:** A) Config/CloudTrail B) Resource Group only C) Budgets D) Tag Editor logs
**Correct:** A
**Explanation:** CloudTrail/Config track tag changes.

### Q17

**Scenario:** Avoid manual instance lists in patch jobs.
**Options:** A) Spreadsheet B) Target a Resource Group/tag in SSM C) Hardcode D) Manual
**Correct:** B
**Explanation:** Dynamic targeting.

### Q18

**Scenario:** Apply tags to thousands of resources programmatically.
**Options:** A) Console one-by-one B) TagResources API C) SCP D) Budgets
**Correct:** B
**Explanation:** Tagging API scales.

### Q19

**Scenario:** Group resources by both app and environment.
**Options:** A) One tag only B) Tag query combining App and Env C) Stack only D) Manual
**Correct:** B
**Explanation:** Multi-tag query.

### Q20

**Scenario:** Tooling that turns a tagging strategy into operations.
**Options:** A) Budgets B) Resource Groups + Tag Editor + SSM C) CloudTrail D) Config only
**Correct:** B
**Explanation:** Groups operationalize tags.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** A fleet's instances churn constantly (Auto Scaling). Ops needs reliable patch targeting that never goes stale.
**Options:** A) Maintain instance-ID lists B) **Tag-based Resource Group** (e.g. `Patch=group-a`) targeted by **SSM Patch Manager** — dynamic membership tracks churn C) Stack group D) Manual
**Correct:** B
**Explanation:** Dynamic tag groups stay correct as instances are added/removed by Auto Scaling.

### H2

**Scenario:** After an acquisition, tags are wildly inconsistent across thousands of resources, breaking grouping, cost allocation, and ABAC.
**Options:** A) Recreate resources B) Use **Tag Editor / Tagging API** to bulk-standardize tags, then enforce with **tag policies/Config**; rebuild groups C) Manual D) Ignore
**Correct:** B
**Explanation:** Bulk remediation + enforcement restores grouping, cost allocation, and access integrity.

### H3

**Scenario:** Security wants engineers to access only resources tagged with their team, and ops wants to operate on the same sets.
**Options:** A) Separate systems B) One tag scheme drives **ABAC IAM** (access) **and** **Resource Groups** (operations) C) Per-resource policies D) New accounts
**Correct:** B
**Explanation:** A single, governed tag taxonomy powers both access control and operational grouping. See [17 - ABAC (Attribute-Based Access Control)](17%20-%20ABAC%20%28Attribute-Based%20Access%20Control%29.md).

### H4

**Scenario:** FinOps cost reports and ops grouping disagree because they use different tags.
**Options:** A) Two taxonomies B) Converge on **one tagging standard**; activate the keys as **cost allocation tags** and use them for Resource Groups C) Manual mapping D) Ignore
**Correct:** B
**Explanation:** Shared tags align cost allocation and operational grouping.

### H5

**Scenario:** A team wants nightly stop of all non-prod compute across many services to cut cost, robust to new resources.
**Options:** A) Per-resource schedules B) Tag-based group (`Env=dev`) + scheduled **automation** (EventBridge → SSM/Lambda) to stop/start C) Manual D) Delete resources
**Correct:** B
**Explanation:** Dynamic group + scheduled automation toggles non-prod cost reliably.

### H6

**Scenario:** Dynamic groups are missing resources because some are launched untagged.
**Options:** A) Accept gaps B) Enforce **tag-on-create** (tag policies/SCP/Config remediation; IaC default tags) so everything is tagged → groups stay complete C) Manual sweeps D) Static lists
**Correct:** B
**Explanation:** Enforce mandatory tagging at creation so dynamic membership is reliable.

### H7

**Scenario:** A regulated org must prove which resources belong to a sensitive application for an audit.
**Options:** A) Memory B) A governed **tag scheme** + Resource Group defining the app; Config rules verify required tags; Tagging API exports the membership C) Screenshots D) Manual list
**Correct:** B
**Explanation:** Tag-defined group + Config verification + API export gives auditable app membership.

### H8

**Scenario:** Patch jobs must differ by environment (prod weekly, dev daily) without per-instance config.
**Options:** A) One baseline B) Separate **tag-based patch groups** (Env=prod / Env=dev) with different baselines/Maintenance Windows C) Manual D) Stack only
**Correct:** B
**Explanation:** Tag-based patch groups segment schedules dynamically. See [01 - AWS Systems Manager Intro bits & bytes](01%20-%20AWS%20Systems%20Manager%20Intro%20bits%20%26%20bytes.md).

### H9

**Scenario:** Leadership wants a per-application operational dashboard spanning EC2, RDS, and ELB.
**Options:** A) Three consoles B) Resource Group for the app → grouped CloudWatch/insights view C) CloudTrail D) Budgets
**Correct:** B
**Explanation:** Group-based views unify cross-service resources for one app.

### H10

**Scenario:** A platform team wants groups aligned exactly to IaC ownership for clean teardown and tracking.
**Options:** A) Tag guesswork B) **Stack-based Resource Groups** so membership mirrors each CloudFormation stack's resources C) Manual D) Organizations
**Correct:** B
**Explanation:** Stack-based groups track IaC boundaries precisely.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Operate on a set of resources as a unit → Resource Group (tag-based dynamic, or stack-based). Bulk tag fix → Tag Editor/Tagging API. Target ops → SSM by group/tag. Same tags power ABAC + cost allocation. It's operational, not a billing feature.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - AWS Resource Groups SRE Operations](04%20-%20AWS%20Resource%20Groups%20SRE%20Operations.md).
