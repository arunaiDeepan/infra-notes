# AWS Tagging Strategies - Exam Scenarios

> Exam focus: tag policies vs SCP enforcement, cost allocation tags (not retroactive), ABAC, and tag-on-create. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - AWS Tagging Strategies Intro bits & bytes](01%20-%20AWS%20Tagging%20Strategies%20Intro%20bits%20%26%20bytes.md) · [02 - AWS Tagging Strategies Deep Dive](02%20-%20AWS%20Tagging%20Strategies%20Deep%20Dive.md) · [04 - AWS Tagging Strategies SRE Operations](04%20-%20AWS%20Tagging%20Strategies%20SRE%20Operations.md) · [17 - ABAC (Attribute-Based Access Control)](17%20-%20ABAC%20%28Attribute-Based%20Access%20Control%29.md)

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

- Tags drive **cost allocation, ABAC, automation, grouping**.
- **Tag Policies standardize/report; SCPs enforce** (deny untagged creates).
- **Cost allocation tags must be activated** and are **not retroactive**.
- **ABAC** uses `aws:ResourceTag`/`aws:PrincipalTag`.
- **Config required-tags** detects/remediates; IaC for tag-on-create.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                             | Points to                                           |
| :------------------------------------------------- | :-------------------------------------------------- |
| "allocate costs by team/project"                   | **Cost allocation tags**                            |
| "prevent creating resources without required tags" | **SCP with aws:RequestTag**                         |
| "standardize tag keys/values org-wide and report"  | **Tag Policies**                                    |
| "grant access based on matching tags"              | **ABAC**                                            |
| "find/fix resources missing tags"                  | **Config required-tags + remediation / Tag Editor** |
| "costs not showing for past months after tagging"  | **Cost allocation tags not retroactive**            |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Using **Tag Policies** to _block_ creates (they standardize/report; **SCP** blocks).
- Expecting **retroactive** cost breakdowns.
- Forgetting to **activate** cost allocation tags.
- ABAC without controlling **who can set the governing tags**.
- Manual tagging instead of **tag-on-create**/Config remediation.

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **"Block untagged creates"** → SCP with tag conditions.
2. **"Standardize/report tags"** → Tag Policies.
3. **"Cost by team"** → activate cost allocation tags (early).
4. **"Access by tag"** → ABAC (+ control tag-setting).
5. **"Fix existing untagged"** → Config required-tags + remediation / Tag Editor.

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** Break down monthly spend by CostCenter.
**Options:** A) Resource Groups B) Activate CostCenter cost allocation tag → Cost Explorer C) SCP D) Config
**Correct:** B
**Explanation:** Cost allocation tags drive cost breakdowns.

### Q2

**Scenario:** Prevent launching EC2 without a `CostCenter` tag.
**Options:** A) Tag Policy B) SCP denying RunInstances without aws:RequestTag/CostCenter C) Config only D) Budget
**Correct:** B
**Explanation:** SCP hard-blocks untagged creates.

### Q3

**Scenario:** Standardize tag keys/values across the org and report drift.
**Options:** A) SCP B) Tag Policies C) Budgets D) IAM
**Correct:** B
**Explanation:** Tag Policies standardize and report.

### Q4

**Scenario:** Grant engineers access only to resources tagged with their team.
**Options:** A) Per-resource policy B) ABAC with aws:ResourceTag/aws:PrincipalTag C) SCP D) New accounts
**Correct:** B
**Explanation:** ABAC matches principal/resource tags.

### Q5

**Scenario:** After tagging, last quarter's costs still aren't split by tag.
**Options:** A) Bug B) Cost allocation tags aren't retroactive C) Wrong region D) Need SCP
**Correct:** B
**Explanation:** Only post-activation spend is broken down.

### Q6

**Scenario:** Find all resources missing a required tag.
**Options:** A) Manual B) Config required-tags rule / Tag Editor C) Budgets D) CloudTrail
**Correct:** B
**Explanation:** Detection via Config/Tag Editor.

### Q7

**Scenario:** Ensure resources are tagged automatically when created via IaC.
**Options:** A) Manual after B) CloudFormation/Terraform default tags C) SCP only D) Budgets
**Correct:** B
**Explanation:** IaC applies tags at creation.

### Q8

**Scenario:** Select resources for backup by tag.
**Options:** A) Manual list B) AWS Backup tag-based plan C) SCP D) Config
**Correct:** B
**Explanation:** Backup plans select by tag.

### Q9

**Scenario:** Max tags per resource.
**Options:** A) 10 B) 50 C) 100 D) Unlimited
**Correct:** B
**Explanation:** 50 tags per resource.

### Q10

**Scenario:** `Env` and `env` both appear; reports are messy.
**Options:** A) Ignore B) Standardize case via Tag Policies + Tag Editor fix C) New account D) SCP only
**Correct:** B
**Explanation:** Case-sensitivity requires standardization.

### Q11

**Scenario:** Auto-remediate resources missing tags.
**Options:** A) Manual B) Config rule → SSM Automation remediation C) Budgets D) CloudTrail
**Correct:** B
**Explanation:** Config + remediation fixes drift.

### Q12

**Scenario:** Stop all dev resources nightly by label.
**Options:** A) Per resource B) Tag-based group + scheduled automation C) SCP D) Budgets
**Correct:** B
**Explanation:** Tag-driven automation.

### Q13

**Scenario:** Risk: users retag to grant themselves access under ABAC.
**Options:** A) Accept B) Restrict who can set the governing tags (tag permissions) C) Remove ABAC D) SCP only
**Correct:** B
**Explanation:** Control tag-setting for trusted ABAC.

### Q14

**Scenario:** Per-project budget alerts.
**Options:** A) Untagged B) Activate Project tag + Budget filtered by it C) SCP D) Config
**Correct:** B
**Explanation:** Budgets filter by cost allocation tags.

### Q15

**Scenario:** Group resources for an app across services.
**Options:** A) Manual B) Tag-based Resource Group C) SCP D) Budget
**Correct:** B
**Explanation:** Tags → Resource Groups.

### Q16

**Scenario:** AWS-managed tag prefix you can't set.
**Options:** A) user: B) aws: C) cost: D) env:
**Correct:** B
**Explanation:** `aws:` is reserved.

### Q17

**Scenario:** Cost of tagging.
**Options:** A) Per tag B) Free C) Per resource D) Per API
**Correct:** B
**Explanation:** Tags are free.

### Q18

**Scenario:** Tag thousands of existing resources programmatically.
**Options:** A) Console B) Resource Groups Tagging API C) SCP D) Budgets
**Correct:** B
**Explanation:** Tagging API scales.

### Q19

**Scenario:** Drive security controls by data sensitivity.
**Options:** A) No tags B) DataClassification tag + policies/ABAC C) SCP only D) Budget
**Correct:** B
**Explanation:** Classification tag gates controls.

### Q20

**Scenario:** Make new accounts inherit tag standards.
**Options:** A) Manual B) Tag Policies attached at OU/org C) IAM D) Budgets
**Correct:** B
**Explanation:** Tag Policies apply org/OU-wide.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** A company wants accurate per-team chargeback but half the resources are untagged and finance can't attribute ~30% of spend.
**Options:** A) Estimate B) **Tag Editor/Tagging API** to bulk-tag existing resources, **activate** CostCenter as a cost allocation tag, enforce **tag-on-create** (SCP) going forward; use **Cost Categories** for roll-ups C) Ignore D) New accounts
**Correct:** B
**Explanation:** Remediate existing tags, activate cost tags, and hard-enforce future tagging to close the attribution gap.

### H2

**Scenario:** Security wants engineers to manage only their team's resources without writing per-resource policies, at scale.
**Options:** A) One policy per resource B) **ABAC**: `aws:PrincipalTag/Team` must equal `aws:ResourceTag/Team`; control who can set the Team tag C) Admin for all D) SCP only
**Correct:** B
**Explanation:** ABAC scales access by matching tags; tag-setting must be restricted to keep it trustworthy.

### H3

**Scenario:** Leadership mandates that NO resource can be created org-wide without `Environment` and `Owner` tags.
**Options:** A) Tag Policies alone B) **SCPs** denying create actions when `aws:RequestTag/Environment` or `aws:RequestTag/Owner` is absent, plus **Tag Policies** for value standardization and **Config** to catch gaps C) Email policy D) Manual review
**Correct:** B
**Explanation:** SCPs enforce at create; Tag Policies standardize values; Config detects residual gaps — layered enforcement.

### H4

**Scenario:** Cost reports are inconsistent because teams use `Project`, `project`, and `proj`.
**Options:** A) Accept B) **Tag Policies** define the canonical key/values; **Tag Editor** remediates existing; SCP blocks non-conforming creates C) Manual mapping D) Ignore
**Correct:** B
**Explanation:** Standardize the key via Tag Policies, fix history, and prevent recurrence.

### H5

**Scenario:** A team activated cost allocation tags today but needs last 6 months split by team for an audit.
**Options:** A) It'll appear B) Cost allocation tags are **not retroactive**; reconstruct history from **CUR** (which has resource/tag detail) where possible, and activate going forward C) Re-tag retroactively D) New report
**Correct:** B
**Explanation:** Activation isn't retroactive; CUR's granular data may allow partial historical reconstruction.

### H6

**Scenario:** Backups must be selected automatically by data criticality with no manual per-resource setup.
**Options:** A) Manual selection B) `BackupPolicy`/`DataClassification` tags + **AWS Backup tag-based** backup plans C) Snapshots manually D) Config only
**Correct:** B
**Explanation:** Tag-based Backup plans select resources dynamically by tag. See [01 - AWS Backup Intro bits & bytes](01%20-%20AWS%20Backup%20Intro%20bits%20%26%20bytes.md).

### H7

**Scenario:** ABAC is in place but an engineer escalated privileges by changing a resource's Team tag.
**Options:** A) Remove ABAC B) **Restrict tag-modification permissions** (deny changing governing tags except by a trusted role); keep ABAC C) Admin for all D) Per-resource policies
**Correct:** B
**Explanation:** Trusted ABAC requires controlling who can set/modify the tags that govern access.

### H8

**Scenario:** A regulated org must prove every production resource is tagged with required compliance metadata, continuously.
**Options:** A) One-time audit B) **Config `required-tags`** (continuous) + remediation, **Tag Policies** for standardization, **SCP** to block untagged creates; reports for audit C) Manual D) Budgets
**Correct:** B
**Explanation:** Continuous detection + enforcement + standardization gives provable, ongoing tag compliance.

### H9

**Scenario:** New accounts in a landing zone keep launching untagged resources.
**Options:** A) Per-account fixes B) Attach **Tag Policies + SCPs** at the OU so every new account inherits enforcement; IaC default tags in baselines C) Manual D) Ignore
**Correct:** B
**Explanation:** Org/OU-level tag governance + IaC defaults ensure new accounts are compliant from day one.

### H10

**Scenario:** FinOps wants flexible cost roll-ups (e.g. group several tag values into "Platform") without re-tagging resources.
**Options:** A) Re-tag everything B) Use **Cost Categories** to define billing groupings/rules over existing tags/accounts C) New tags D) SCP
**Correct:** B
**Explanation:** Cost Categories build reporting roll-ups over existing tags/accounts without changing resource tags.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Tags power cost allocation, ABAC, automation, and grouping. Standardize/report → Tag Policies; enforce (block untagged creates) → SCP; detect/remediate existing → Config/Tag Editor. Activate cost allocation tags early — they're not retroactive. Control who can set governing tags for trusted ABAC.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - AWS Tagging Strategies SRE Operations](04%20-%20AWS%20Tagging%20Strategies%20SRE%20Operations.md).
