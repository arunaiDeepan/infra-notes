# AWS Service Catalog - Exam Scenarios

> Exam focus: self-service without broad IAM (launch role), template constraints, org sharing, and the Catalog/CloudFormation/Control Tower split. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - AWS Service Catalog Intro bits & bytes](01%20-%20AWS%20Service%20Catalog%20Intro%20bits%20%26%20bytes.md) · [02 - AWS Service Catalog Deep Dive](02%20-%20AWS%20Service%20Catalog%20Deep%20Dive.md) · [04 - AWS Service Catalog SRE Operations](04%20-%20AWS%20Service%20Catalog%20SRE%20Operations.md) · [01 - AWS CloudFormation Intro bits & bytes](01%20-%20AWS%20CloudFormation%20Intro%20bits%20%26%20bytes.md)

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

- **Self-service launch without the underlying IAM** (launch role).
- **Template constraints** to limit sizes/regions/parameters.
- **Portfolio sharing** across accounts/OUs (org sharing).
- **TagOptions** for enforced tagging.
- **StackSet constraint** for multi-account provisioning.
- Service Catalog vs CloudFormation vs Control Tower.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                                      | Points to                           |
| :---------------------------------------------------------- | :---------------------------------- |
| "self-service", "approved/curated products", "standardized" | **Service Catalog**                 |
| "without granting users permission to create the resources" | **Launch role / launch constraint** |
| "restrict instance types / regions users can pick"          | **Template constraint**             |
| "distribute approved products across accounts"              | **Portfolio org sharing**           |
| "enforce mandatory tags at launch"                          | **TagOptions**                      |
| "deploy product to many accounts/regions"                   | **StackSet constraint**             |
| "app store for infrastructure"                              | **Service Catalog**                 |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Granting users `cloudformation:*` + `ec2:*` directly instead of launch-only via a launch role.
- Using IAM policies alone to "limit instance size" (template constraint is cleaner/intended).
- Choosing Control Tower when the need is curated **products** (Control Tower governs the org baseline, not the product catalog).
- Plain CloudFormation when **non-admin self-service** is required.

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **"Self-service + standardized + no broad IAM"** → Service Catalog with launch role.
2. **"Limit what users can choose"** → template constraint.
3. **"Across many accounts"** → org-shared portfolio (+ StackSet constraint).
4. **"Enforce tags"** → TagOptions.
5. If it's just an infra team writing IaC → plain CloudFormation/CDK.

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** Developers must launch a compliant RDS+EC2 stack but must NOT have rds/ec2 create permissions.
**Options:** A) Grant ec2/rds B) Service Catalog product with launch constraint (launch role) C) Bastion D) Console admin
**Correct:** B
**Explanation:** Launch role provisions; user has launch-only IAM.

### Q2

**Scenario:** Stop users picking instance types larger than t3.small.
**Options:** A) IAM deny per type B) Template constraint limiting parameter values C) SCP D) Budget
**Correct:** B
**Explanation:** Template constraints restrict allowed parameters.

### Q3

**Scenario:** Distribute approved products to all accounts in the org.
**Options:** A) Email templates B) Share the portfolio org-wide via Organizations C) Copy per account D) StackSet only
**Correct:** B
**Explanation:** Org portfolio sharing scales distribution.

### Q4

**Scenario:** Enforce mandatory CostCenter tag on every launched product.
**Options:** A) Manual B) TagOptions on the portfolio/product C) IAM D) Config
**Correct:** B
**Explanation:** TagOptions enforce tags at launch.

### Q5

**Scenario:** Launch the same product in 10 accounts and 2 regions.
**Options:** A) Manual B) StackSet constraint C) Nested stacks D) Export
**Correct:** B
**Explanation:** StackSet constraint provisions across accounts/regions.

### Q6

**Scenario:** Curated, versioned set of approved architectures for many teams.
**Options:** A) Wiki of templates B) Service Catalog products/portfolios C) S3 of YAML D) Control Tower
**Correct:** B
**Explanation:** Catalog provides curation + versioning + access.

### Q7

**Scenario:** What engine actually provisions a product?
**Options:** A) Terraform only B) CloudFormation C) CodeDeploy D) SSM
**Correct:** B
**Explanation:** Products are CloudFormation templates (Terraform products also supported).

### Q8

**Scenario:** Notify a team on every product launch.
**Options:** A) Manual B) Notification constraint (SNS) C) Config D) Budget
**Correct:** B
**Explanation:** Notification constraint sends SNS on events.

### Q9

**Scenario:** Roll users to a new approved template version safely.
**Options:** A) Recreate B) Update provisioned products to the new version C) Delete all D) New portfolio
**Correct:** B
**Explanation:** Version lifecycle + provisioned-product update.

### Q10

**Scenario:** Vend new accounts with a baseline (Control Tower).
**Options:** A) Manual account creation B) Account Factory (a Service Catalog product) C) StackSet only D) SCP
**Correct:** B
**Explanation:** Account Factory is a Service Catalog product.

### Q11

**Scenario:** Limit which regions a product can be launched in.
**Options:** A) IAM only B) Template constraint on region parameter (+ SCP region guardrail) C) Budget D) Tag
**Correct:** B
**Explanation:** Template constraints restrict region choices; SCP enforces org-wide.

### Q12

**Scenario:** Cleanly remove a user's launched resources.
**Options:** A) Delete stack manually B) Terminate the provisioned product C) Remove portfolio D) IAM deny
**Correct:** B
**Explanation:** Terminate deletes the underlying stack.

### Q13

**Scenario:** Integrate self-service provisioning with the company's ServiceNow.
**Options:** A) Not possible B) Service Catalog ServiceNow connector C) Email D) Manual
**Correct:** B
**Explanation:** Service Catalog integrates with ServiceNow.

### Q14

**Scenario:** Detect if a launched product's resources later drift from compliance.
**Options:** A) Service Catalog alone B) AWS Config C) Budget D) CloudTrail only
**Correct:** B
**Explanation:** Config detects drift/compliance post-launch.

### Q15

**Scenario:** Track spend per product/portfolio.
**Options:** A) Manual B) Associate Budgets to products/portfolios C) Config D) CloudTrail
**Correct:** B
**Explanation:** Budgets can be associated to catalog items.

### Q16

**Scenario:** Give a contractor access to launch only one specific product.
**Options:** A) Admin B) Grant access to the portfolio/product only C) ec2:\* D) Root
**Correct:** B
**Explanation:** Scope access to the product; launch role does the work.

### Q17

**Scenario:** Standardize a golden VPC across the org.
**Options:** A) Copy templates B) Org-shared portfolio with a VPC product C) Manual D) Per-team wikis
**Correct:** B
**Explanation:** Shared portfolio standardizes the product.

### Q18

**Scenario:** Who manages the template the user launches?
**Options:** A) The user edits it B) The platform team; users can't edit C) Anyone D) AWS
**Correct:** B
**Explanation:** Users launch but don't edit the template.

### Q19

**Scenario:** Audit who provisioned/terminated products.
**Options:** A) Config B) CloudTrail C) Budget D) Inventory
**Correct:** B
**Explanation:** CloudTrail logs provision/update/terminate.

### Q20

**Scenario:** Offer a Terraform-based product through the catalog.
**Options:** A) Not supported B) Service Catalog supports external/Terraform product types C) CloudFormation only D) CDK only
**Correct:** B
**Explanation:** Terraform products are supported.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** A platform team must let 200 developers across 30 accounts launch a compliant data platform (RDS, S3, IAM) with mandatory tags and only in two regions — without any developer holding rds/s3/iam create permissions.
**Options:** A) Grant scoped IAM to all B) Service Catalog: product (CFN) + **launch role** (creation perms) + **template constraint** (region) + **TagOptions** (tags), portfolio **shared org-wide**; developers get launch-only IAM C) CloudFormation per team D) Control Tower guardrails only
**Correct:** B
**Explanation:** Launch role decouples permissions; template constraint limits regions; TagOptions enforce tags; org sharing distributes — all without broad developer IAM.

### H2

**Scenario:** Security needs to guarantee resources are launched _only_ through the catalog (no off-catalog creation), org-wide.
**Options:** A) Trust developers B) Catalog for provisioning **+ SCPs** that deny direct create actions (except via the launch role) so the only path is the catalog C) IAM per user D) Config alarms
**Correct:** B
**Explanation:** Service Catalog provides the path; **SCPs** close the off-catalog path so creation must go through approved launch roles.

### H3

**Scenario:** A new compliant AMI/template version is approved; 500 already-provisioned products must move to it on a controlled schedule.
**Options:** A) Terminate and relaunch all B) Add the new **provisioning artifact (version)**, mark old as deprecated, **update provisioned products** to the new version in batches C) Edit each stack D) New portfolio
**Correct:** B
**Explanation:** Version lifecycle + batched provisioned-product updates roll the fleet forward safely.

### H4

**Scenario:** Cross-account launch fails because the launch role doesn't exist in target accounts.
**Options:** A) Use admin B) Use a **local launch role name** (role with the same name pre-created in each account, e.g. via StackSet baseline) so the constraint resolves locally C) Share keys D) One central role only
**Correct:** B
**Explanation:** For shared portfolios, a **local launch role** (same-named role per account) avoids cross-account role ARN problems; deploy it as part of the account baseline.

### H5

**Scenario:** Finance wants per-product spend visibility and a hard alert if a product's monthly cost exceeds a threshold.
**Options:** A) CUR only B) Enforce **TagOptions** (cost-allocation tags) + associate **Budgets** to the product/portfolio with alerts/actions C) Manual review D) Config
**Correct:** B
**Explanation:** Consistent tags enable allocation; product-associated budgets alert/act on overspend.

### H6

**Scenario:** Developers complain the catalog is too rigid and they can't tweak needed parameters; security still needs guardrails.
**Options:** A) Give full CFN access B) Loosen **template constraints** to expose safe parameters within allowed ranges; keep launch role + tag enforcement C) Remove the catalog D) Manual approvals
**Correct:** B
**Explanation:** Template constraints can expose a _bounded_ set of choices — balance flexibility and governance without abandoning the model.

### H7

**Scenario:** An enterprise with ServiceNow wants developers to request infrastructure in ServiceNow and have it provisioned in AWS, governed.
**Options:** A) Manual tickets B) **Service Catalog + ServiceNow connector**: requests in ServiceNow map to catalog products provisioned via launch roles C) Email D) Custom portal from scratch
**Correct:** B
**Explanation:** The ServiceNow integration fronts Service Catalog so ITSM requests provision governed products.

### H8

**Scenario:** Account Factory (Control Tower) needs to vend accounts with a standardized baseline; where does Service Catalog fit?
**Options:** A) Unrelated B) Account Factory **is** a Service Catalog product; customizing the vended baseline = customizing that product/blueprint C) Replace with CFN D) Manual
**Correct:** B
**Explanation:** Control Tower's Account Factory is implemented as a Service Catalog product. See [01 - AWS Account Factory and Landing Zone Intro bits & bytes](01%20-%20AWS%20Account%20Factory%20and%20Landing%20Zone%20Intro%20bits%20%26%20bytes.md).

### H9

**Scenario:** Provisioned products' resources are being modified out-of-band, breaking compliance; the org wants detection and (ideally) remediation.
**Options:** A) Service Catalog alone detects drift B) Use **AWS Config** rules (detective) + SSM Automation remediation on the provisioned resources; restrict who can modify them C) Re-launch products nightly D) CloudTrail only
**Correct:** B
**Explanation:** Service Catalog governs provisioning, not ongoing drift; Config + remediation handles post-launch compliance.

### H10

**Scenario:** A regulated org must prove every production resource came from an approved, versioned template, with full audit and least-privilege creation.
**Options:** A) Trust process B) Service Catalog products (versioned approved templates) + launch roles (least-privilege) + CloudTrail (provision audit) + SCPs (no off-catalog create) + Config (ongoing compliance) C) IAM only D) Manual change board
**Correct:** B
**Explanation:** The layered model — curated versioned products, least-privilege launch roles, SCP enforcement, CloudTrail/Config audit — gives provable provenance and governance.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Self-service of approved infra without broad IAM → Service Catalog (launch role does the creating). Limit choices → template constraints. Enforce tags → TagOptions. Distribute → org-shared portfolios. Engine = CloudFormation. Close the off-catalog path with SCPs; detect post-launch drift with Config.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - AWS Service Catalog SRE Operations](04%20-%20AWS%20Service%20Catalog%20SRE%20Operations.md).
