# AWS CloudFormation - Exam Scenarios

> Exam focus for CloudFormation: StackSets vs nested vs cross-stack, drift, replacement/deletion policies, custom resources, and IaC tool selection. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - AWS CloudFormation Intro bits & bytes](01%20-%20AWS%20CloudFormation%20Intro%20bits%20%26%20bytes.md) · [02 - AWS CloudFormation Deep Dive](02%20-%20AWS%20CloudFormation%20Deep%20Dive.md) · [04 - AWS CloudFormation SRE Operations](04%20-%20AWS%20CloudFormation%20SRE%20Operations.md) · [01 - AWS Service Catalog Intro bits & bytes](01%20-%20AWS%20Service%20Catalog%20Intro%20bits%20%26%20bytes.md)

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

- **StackSets** for multi-account/multi-region; **service-managed** + auto-deploy with Organizations.
- **Nested stacks** (reuse) vs **cross-stack exports** (`!ImportValue`, can't delete while imported).
- **Change sets** to preview, **Replacement** risk on stateful resources.
- **`DeletionPolicy`/`UpdateReplacePolicy`** = `Retain`/`Snapshot` to protect data.
- **Drift detection** vs continuous tracking with Config.
- **Custom resources** (Lambda) for unsupported actions; must signal back.
- **Dynamic references** for SSM/Secrets Manager.
- Tool choice: CloudFormation vs CDK vs Terraform vs Service Catalog.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                                                     | Points to                                      |
| :------------------------------------------------------------------------- | :--------------------------------------------- |
| "deploy to all accounts in the organization", "new accounts automatically" | **Service-managed StackSets** (auto-deploy)    |
| "same template in multiple regions/accounts"                               | **StackSets**                                  |
| "preview changes before applying"                                          | **Change set**                                 |
| "don't lose the database when the stack is deleted"                        | **DeletionPolicy: Snapshot/Retain**            |
| "detect manual changes outside the template"                               | **Drift detection** (or Config for continuous) |
| "provision something CloudFormation doesn't support"                       | **Custom resource** (Lambda-backed)            |
| "reusable infrastructure component"                                        | **Nested stack**                               |
| "share VPC ID with another team's stack"                                   | **Export + !ImportValue**                      |
| "infrastructure in Python/TypeScript"                                      | **CDK**                                        |
| "self-service catalog for end users"                                       | **Service Catalog**                            |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Using **cross-stack export** when the answer is **nested stack** (reuse) — and vice versa.
- Forgetting **service-managed** StackSets when Organizations is mentioned.
- Choosing CLI scripts for "repeatable infrastructure."
- Ignoring **Replacement** risk; not using a change set on stateful stacks.
- Thinking drift detection is **continuous** (it's on-demand).
- Using **CodeDeploy/CodePipeline** as the IaC engine (they orchestrate; CFN provisions).

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **"All accounts in the org" / "auto for new accounts"** → service-managed StackSets.
2. **"Protect data on delete/replace"** → DeletionPolicy / UpdateReplacePolicy.
3. **"Preview impact"** → change set.
4. **"Manual change detection"** → drift (on-demand) or Config (continuous).
5. **"Unsupported resource / run logic during deploy"** → custom resource.
6. **Tool wording**: native AWS → CFN; programming language → CDK; multi-cloud → Terraform; curated self-service → Service Catalog.

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** Deploy an identical security baseline to 50 accounts in an AWS Organization, including future accounts.
**Options:** A) Run a template per account B) Service-managed StackSet with auto-deploy C) Nested stacks D) Terraform per account
**Correct:** B
**Explanation:** Service-managed StackSets use Organizations and auto-deploy to new accounts in target OUs.

### Q2

**Scenario:** Preview exactly what an update will change before applying.
**Options:** A) Just update B) Change set C) Drift detection D) Rollback
**Correct:** B
**Explanation:** Change sets show adds/modifies/replacements pre-execution.

### Q3

**Scenario:** Stack deletion must not destroy the production RDS database.
**Options:** A) Termination protection only B) DeletionPolicy: Snapshot/Retain on the DB C) Stack policy D) Nested stack
**Correct:** B
**Explanation:** DeletionPolicy controls resource fate on delete; Snapshot/Retain preserve data.

### Q4

**Scenario:** A team made manual console changes to a stack's resources; you need to detect them.
**Options:** A) Change set B) Drift detection C) Rollback D) Export
**Correct:** B
**Explanation:** Drift detection compares live config to the template.

### Q5

**Scenario:** Reuse a standard VPC definition across many application stacks as a building block.
**Options:** A) Copy-paste B) Nested stack C) CLI D) Mapping
**Correct:** B
**Explanation:** Nested stacks package reusable components.

### Q6

**Scenario:** Stack A must use the VPC ID created by independently-managed stack B.
**Options:** A) Hardcode B) Export in B + !ImportValue in A C) Nested stack D) Parameter file
**Correct:** B
**Explanation:** Cross-stack export/import shares values across independent stacks.

### Q7

**Scenario:** Provision a third-party SaaS object during stack creation that CloudFormation can't natively manage.
**Options:** A) Manual step B) Custom resource (Lambda) C) Mapping D) Output
**Correct:** B
**Explanation:** Custom resources run Lambda logic during stack ops.

### Q8

**Scenario:** Inject a database password without putting it in the template.
**Options:** A) Plaintext parameter B) Dynamic reference to Secrets Manager C) Mapping D) Output
**Correct:** B
**Explanation:** `{{resolve:secretsmanager:...}}` keeps secrets out of templates.

### Q9

**Scenario:** Infrastructure team wants Python with loops and reusable classes for IaC on AWS.
**Options:** A) CloudFormation YAML B) CDK C) Terraform D) Shell
**Correct:** B
**Explanation:** CDK uses real languages and synthesises CloudFormation.

### Q10

**Scenario:** Provide non-technical teams a governed, self-service way to launch approved stacks.
**Options:** A) Give console admin B) Service Catalog products C) Share templates D) StackSets
**Correct:** B
**Explanation:** Service Catalog wraps CloudFormation templates as curated products with constraints.

### Q11

**Scenario:** An exported output can't be deleted; the stack update fails.
**Options:** A) Force delete B) Remove the import in the consuming stack first C) Ignore D) Recreate org
**Correct:** B
**Explanation:** You can't modify/delete an export while another stack imports it.

### Q12

**Scenario:** Prevent accidental deletion of a critical production stack.
**Options:** A) Stack policy B) Termination protection C) DeletionPolicy D) IAM only
**Correct:** B
**Explanation:** Termination protection blocks whole-stack deletion.

### Q13

**Scenario:** Prevent a specific resource from being updated during stack updates.
**Options:** A) DeletionPolicy B) Stack policy C) Termination protection D) Drift
**Correct:** B
**Explanation:** Stack policies allow/deny update actions per resource.

### Q14

**Scenario:** A template needs different AMIs per region automatically.
**Options:** A) Hardcode B) Mappings + !FindInMap (or SSM public parameter) C) Outputs D) Conditions only
**Correct:** B
**Explanation:** Region→AMI mapping (or the SSM public AMI parameter) selects per region.

### Q15

**Scenario:** A stack is stuck because a custom resource never responded.
**Options:** A) Wait forever B) Ensure the Lambda sends SUCCESS/FAILED to the response URL C) Delete org D) Add parameter
**Correct:** B
**Explanation:** Custom resources hang until they signal back (or time out).

### Q16

**Scenario:** Enforce that no non-compliant resource is created during deployment, proactively.
**Options:** A) Config rule (detective) B) CloudFormation Hooks (proactive) C) Drift D) Stack policy
**Correct:** B
**Explanation:** Hooks run proactive pre-provision checks; Config is detective (after the fact).

### Q17

**Scenario:** Same template, 4 regions, one account, single operation.
**Options:** A) 4 manual deploys B) Self-managed StackSet across regions C) Nested stacks D) Export
**Correct:** B
**Explanation:** StackSets handle multi-region from one operation (self-managed works without Organizations).

### Q18

**Scenario:** A failed create left no resources and the stack rolled back automatically. Expected?
**Options:** A) Bug B) Yes — default rollback on failure C) Must enable rollback D) Need a stack policy
**Correct:** B
**Explanation:** Rollback to last good state is default behaviour.

### Q19

**Scenario:** You hit the 500-resources-per-stack limit.
**Options:** A) Impossible B) Split into nested/layered stacks C) Use Terraform D) Raise to 5000
**Correct:** B
**Explanation:** Decompose into nested or layered stacks.

### Q20

**Scenario:** CI/CD should deploy infra changes with an approval gate after previewing changes.
**Options:** A) CLI apply B) CodePipeline with CloudFormation create-change-set + manual approval + execute C) Console D) StackSet
**Correct:** B
**Explanation:** Pipeline change-set + approval + execute is the governed IaC delivery pattern.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** A property change to a production RDS instance via stack update unexpectedly created a brand-new empty database and deleted the old one.
**Options:** A) CloudFormation bug B) The change caused a **Replacement**; review change sets and set `UpdateReplacePolicy: Snapshot`/`Retain` to protect data C) Add termination protection D) Use nested stacks
**Correct:** B
**Explanation:** Certain property changes force **Replacement** (new physical resource). Change sets reveal it; `UpdateReplacePolicy` protects data when replacement happens.

### H2

**Scenario:** An org wants every new account (auto-vended) to receive a security baseline within minutes of creation, with no manual step.
**Options:** A) Self-managed StackSet + manual add B) Service-managed StackSet with **auto-deployment** targeting the OU C) Lambda that copies templates D) Per-account CLI
**Correct:** B
**Explanation:** Service-managed StackSets with auto-deploy push the baseline to accounts as they join the target OU. Pairs with Account Factory → [01 - AWS Account Factory and Landing Zone Intro bits & bytes](01%20-%20AWS%20Account%20Factory%20and%20Landing%20Zone%20Intro%20bits%20%26%20bytes.md).

### H3

**Scenario:** Two teams share a VPC via export/import. Team A needs to change the VPC CIDR (which changes the export), but the update fails.
**Options:** A) Force it B) Coordinate: remove/relink the import in Team B's stack first (or restructure to a parameter/SSM lookup), then update A C) Delete both D) Use drift detection
**Correct:** B
**Explanation:** Exports are locked while imported. Decouple consumers first, or replace tight export/import with a looser pattern (SSM parameter lookup).

### H4

**Scenario:** A stack update failed and is stuck in `UPDATE_ROLLBACK_FAILED`.
**Options:** A) Delete the org B) Use **ContinueUpdateRollback** (skipping the resources that can't roll back after fixing them manually), or roll back to the last known good template C) Recreate account D) Ignore
**Correct:** B
**Explanation:** `UPDATE_ROLLBACK_FAILED` requires fixing the offending resource then `ContinueUpdateRollback` (optionally skipping specific resources). See [04 - AWS CloudFormation SRE Operations](04%20-%20AWS%20CloudFormation%20SRE%20Operations.md).

### H5

**Scenario:** Security requires that operators can deploy stacks but cannot grant themselves extra IAM permissions through templates.
**Options:** A) Give operators admin B) Deploy via a least-privilege **service role**; operators only have `cloudformation:*` on specific stacks and **iam:PassRole** to that constrained role C) No IAM in templates D) Manual review only
**Correct:** B
**Explanation:** A scoped service role + `iam:PassRole` decouples operator permissions from what the stack can create, preventing privilege escalation.

### H6

**Scenario:** Drift keeps reappearing because an external automation modifies a security group out-of-band; the team wants continuous detection and auto-remediation.
**Options:** A) Manual drift runs B) **AWS Config** rule (continuous) + remediation (SSM Automation), and ideally restrict who can modify the SG C) Stack policy D) Termination protection
**Correct:** B
**Explanation:** CloudFormation drift is on-demand; **Config** gives continuous detection with automatic remediation. Also fix the root cause (restrict the out-of-band actor). See [24 - AWS Config & Audit Manager](24%20-%20AWS%20Config%20%26%20Audit%20Manager.md).

### H7

**Scenario:** A large template (>51 KB) fails to deploy directly from the CLI.
**Options:** A) Shrink by deleting resources B) Upload the template to **S3** and reference by URL (supports larger templates), and/or split into nested stacks C) Use JSON D) Use a parameter file
**Correct:** B
**Explanation:** Templates over the direct body limit must be referenced from S3; decomposition also helps.

### H8

**Scenario:** A multi-region active/active app must deploy identical infra to 3 regions and keep a per-region AMI and certificate.
**Options:** A) One stack with hardcoded values B) StackSet across regions + region-specific values via SSM public parameters / Mappings; per-region ACM cert referenced regionally C) Cross-stack export across regions D) Single global stack
**Correct:** B
**Explanation:** StackSets handle the fan-out; region-specific resolution (SSM/Mappings) supplies AMI/cert per region. (Exports are region-scoped, so cross-region import isn't available.)

### H9

**Scenario:** A custom resource Lambda occasionally times out, leaving stacks stuck for an hour before failing.
**Options:** A) Increase stack timeout B) Make the Lambda **idempotent**, always send a response (success/failure) even on error paths, and add a heartbeat/longer timeout for long work C) Remove the custom resource D) Use nested stacks
**Correct:** B
**Explanation:** Custom resources must always signal back; robust handlers send FAILED on exceptions and use the response mechanism to avoid the full timeout.

### H10

**Scenario:** A regulated enterprise wants developers to self-serve approved infrastructure, with enforced tagging, region limits, and no ability to alter the underlying template.
**Options:** A) Share raw templates B) **Service Catalog** products (backed by CloudFormation) with **launch constraints**, **template constraints**, and a launch role; governed via Organizations C) Give CloudFormation access D) StackSets only
**Correct:** B
**Explanation:** Service Catalog adds governance (constraints, launch roles, curated versions) on top of CloudFormation for safe self-service. See [01 - AWS Service Catalog Intro bits & bytes](01%20-%20AWS%20Service%20Catalog%20Intro%20bits%20%26%20bytes.md).

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Many accounts/regions → StackSets (service-managed + auto-deploy with Organizations). Reuse → nested stacks. Share values → export/ImportValue (locked while imported). Preview → change set. Protect data → DeletionPolicy/UpdateReplacePolicy. Manual changes → drift (on-demand) or Config (continuous). Unsupported → custom resource. Self-service → Service Catalog.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - AWS CloudFormation SRE Operations](04%20-%20AWS%20CloudFormation%20SRE%20Operations.md).
