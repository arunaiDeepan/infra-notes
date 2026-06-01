# AWS Account Factory & Landing Zone - Exam Scenarios

> Exam focus: Control Tower landing zone, guardrail types, account vending, and when to use Control Tower vs DIY/LZA. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - AWS Account Factory and Landing Zone Intro bits & bytes](01%20-%20AWS%20Account%20Factory%20and%20Landing%20Zone%20Intro%20bits%20%26%20bytes.md) · [02 - AWS Account Factory and Landing Zone Deep Dive](02%20-%20AWS%20Account%20Factory%20and%20Landing%20Zone%20Deep%20Dive.md) · [04 - AWS Account Factory and Landing Zone SRE Operations](04%20-%20AWS%20Account%20Factory%20and%20Landing%20Zone%20SRE%20Operations.md) · [07 - AWS Control Tower](07%20-%20AWS%20Control%20Tower.md)

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

- **Landing zone** = secure multi-account baseline; **Account Factory** = vending.
- Built on **Organizations + Config + SCPs + Service Catalog + Identity Center**.
- **Guardrails**: preventive (SCP), detective (Config), proactive (Hooks).
- **Log Archive** + **Audit** accounts.
- Control Tower vs DIY vs LZA; **AFT** for Terraform.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                              | Points to                        |
| :-------------------------------------------------- | :------------------------------- |
| "set up a secure multi-account environment quickly" | **Control Tower landing zone**   |
| "automatically create new accounts with guardrails" | **Account Factory**              |
| "centralized logging account"                       | **Log Archive account**          |
| "prevent disallowed actions org-wide"               | **Preventive guardrail (SCP)**   |
| "detect non-compliant configurations"               | **Detective guardrail (Config)** |
| "block non-compliant resources at deploy"           | **Proactive guardrail (Hooks)**  |
| "account vending via Terraform/GitOps"              | **AFT**                          |
| "highly regulated, complex baseline"                | **Landing Zone Accelerator**     |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Using Account Factory to provision **in-account resources** (it vends accounts; use Service Catalog/CloudFormation for resources).
- Choosing DIY when **Control Tower** is the quick managed answer.
- Confusing **preventive (SCP)** with **detective (Config)** guardrails.
- Forgetting the **Log Archive/Audit** accounts.
- Thinking Control Tower applies SCPs to the **management account** (SCPs don't affect it).

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **"Multi-account secure baseline fast"** → Control Tower landing zone.
2. **"Vend accounts with baseline"** → Account Factory (AFT if Terraform).
3. **"Block vs detect"** → SCP (block) vs Config (detect) vs Hooks (deploy-time block).
4. **"Highly regulated/complex"** → LZA.
5. **"In-account resources"** → Service Catalog/CloudFormation, not Account Factory.

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** Quickly stand up a secure, governed multi-account AWS environment.
**Options:** A) DIY scripts B) AWS Control Tower (landing zone) C) One big account D) IAM only
**Correct:** B
**Explanation:** Control Tower is the managed landing zone.

### Q2

**Scenario:** Automatically provision new accounts pre-configured with guardrails and SSO.
**Options:** A) Manual CreateAccount B) Account Factory C) StackSet only D) Budgets
**Correct:** B
**Explanation:** Account Factory vends baseline-compliant accounts.

### Q3

**Scenario:** Where do org-wide CloudTrail/Config logs centralize?
**Options:** A) Management account B) Log Archive account C) Each account D) Audit only
**Correct:** B
**Explanation:** Log Archive account centralizes logs.

### Q4

**Scenario:** Block disabling of CloudTrail across all accounts.
**Options:** A) Detective B) Preventive guardrail (SCP) C) Proactive D) Budget
**Correct:** B
**Explanation:** Preventive = SCP blocks the action.

### Q5

**Scenario:** Detect (not block) S3 buckets without encryption.
**Options:** A) SCP B) Detective guardrail (Config) C) Hook D) Budget
**Correct:** B
**Explanation:** Detective guardrails are Config rules.

### Q6

**Scenario:** Block non-compliant resources before they're created in a stack.
**Options:** A) Config B) Proactive guardrail (CloudFormation Hooks) C) SCP only D) Budget
**Correct:** B
**Explanation:** Proactive = Hooks at deploy time.

### Q7

**Scenario:** Vend accounts via Terraform/GitOps.
**Options:** A) Console only B) Account Factory for Terraform (AFT) C) StackSet D) Budgets
**Correct:** B
**Explanation:** AFT is the Terraform vending pipeline.

### Q8

**Scenario:** Highly regulated org needs a complex, specialized baseline beyond Control Tower defaults.
**Options:** A) Control Tower only B) Landing Zone Accelerator C) Single account D) IAM
**Correct:** B
**Explanation:** LZA targets complex/regulated baselines.

### Q9

**Scenario:** Which service underlies Account Factory?
**Options:** A) Lambda B) Service Catalog C) Step Functions D) Config
**Correct:** B
**Explanation:** Account Factory is a Service Catalog product.

### Q10

**Scenario:** New accounts should auto-receive higher quotas.
**Options:** A) Manual B) Quota request templates (Service Quotas) C) SCP D) Budgets
**Correct:** B
**Explanation:** Templates apply to new accounts.

### Q11

**Scenario:** Apply custom CloudFormation/SCPs automatically to vended accounts.
**Options:** A) Manual B) Customizations for Control Tower (CfCT) C) Budgets D) IAM
**Correct:** B
**Explanation:** CfCT extends the vending lifecycle.

### Q12

**Scenario:** Where does workforce access to accounts come from?
**Options:** A) IAM users per account B) IAM Identity Center (SSO) C) Root D) Keys
**Correct:** B
**Explanation:** Identity Center provides SSO.

### Q13

**Scenario:** Detect drift when someone modifies a managed OU/SCP.
**Options:** A) Nothing B) Control Tower drift detection C) Budgets D) CloudTrail only
**Correct:** B
**Explanation:** Control Tower flags drift for repair.

### Q14

**Scenario:** Isolate prod and non-prod per workload.
**Options:** A) One account B) Separate accounts in a Workloads OU C) IAM only D) Tags only
**Correct:** B
**Explanation:** Account-per-workload/env isolation.

### Q15

**Scenario:** Consolidated billing benefit of multi-account org.
**Options:** A) None B) Volume discounts + shared RIs/Savings Plans C) Higher cost D) Per-account billing only
**Correct:** B
**Explanation:** Consolidated billing aggregates discounts.

### Q16

**Scenario:** SCP guardrails affect the management account?
**Options:** A) Yes B) No — SCPs don't apply to the management account C) Only prod D) Only sandbox
**Correct:** B
**Explanation:** Management account is exempt from SCPs.

### Q17

**Scenario:** Enroll an existing account into the landing zone.
**Options:** A) Impossible B) Enroll into Control Tower/OU C) Recreate it D) Budgets
**Correct:** B
**Explanation:** Existing accounts can be enrolled.

### Q18

**Scenario:** Restrict which AWS regions can be used org-wide.
**Options:** A) Per user B) Region-deny guardrail (SCP) C) Budgets D) Config only
**Correct:** B
**Explanation:** A preventive region guardrail.

### Q19

**Scenario:** Provision resources inside an account for self-service.
**Options:** A) Account Factory B) Service Catalog products C) Organizations D) Budgets
**Correct:** B
**Explanation:** Account Factory vends accounts; Service Catalog vends in-account resources.

### Q20

**Scenario:** Standard accounts a Control Tower landing zone creates.
**Options:** A) Just management B) Management + Log Archive + Audit C) One per region D) None
**Correct:** B
**Explanation:** Three foundational accounts.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** A company is migrating to AWS and wants, from day one, multi-account isolation, central logging, SSO, guardrails, and self-service account creation — with minimal build effort.
**Options:** A) DIY everything B) **AWS Control Tower** landing zone (Log Archive + Audit + Organizations + Identity Center + guardrails) and **Account Factory** for vending C) One account + IAM D) LZA
**Correct:** B
**Explanation:** Control Tower delivers the whole baseline + vending with the least effort for a standard org.

### H2

**Scenario:** Every newly-vended account must get the company's network baseline, security tooling, and required tags automatically.
**Options:** A) Manual post-setup B) **CfCT** (or AFT) deploying CloudFormation/StackSets + SCPs as part of the Account Factory lifecycle C) Email runbook D) Budgets
**Correct:** B
**Explanation:** Customizations (CfCT/AFT) apply baseline resources/policies automatically at vend time.

### H3

**Scenario:** A bank needs a baseline mapped to a specific compliance framework with extensive custom controls Control Tower can't express.
**Options:** A) Control Tower only B) **Landing Zone Accelerator (LZA)** for the complex/regulated baseline C) Single account D) Manual
**Correct:** B
**Explanation:** LZA targets highly regulated, complex baselines beyond Control Tower's opinionated defaults.

### H4

**Scenario:** Teams want to request accounts via pull requests with review/approval, fully in Terraform.
**Options:** A) Console Account Factory B) **Account Factory for Terraform (AFT)** GitOps pipeline C) Manual CreateAccount D) StackSets only
**Correct:** B
**Explanation:** AFT provides PR-driven, Terraform-based account vending with approvals.

### H5

**Scenario:** Security must guarantee no account can be used in unapproved regions or disable CloudTrail, and wants violations of encryption settings reported.
**Options:** A) Trust teams B) **Preventive guardrails (SCPs)** for region/CloudTrail; **detective guardrails (Config)** for encryption reporting; optionally **proactive Hooks** C) Budgets D) Manual audits
**Correct:** B
**Explanation:** Layer preventive (block) + detective (report) + proactive (deploy-time) guardrails.

### H6

**Scenario:** New accounts immediately hit low default limits during initial deployments.
**Options:** A) Raise per account manually B) **Quota request templates** so vended accounts auto-receive higher limits C) Bigger instances D) Ignore
**Correct:** B
**Explanation:** Quota templates baseline limits at vend time. See [01 - AWS Service Quotas Intro bits & bytes](01%20-%20AWS%20Service%20Quotas%20Intro%20bits%20%26%20bytes.md).

### H7

**Scenario:** Someone manually edited a Control Tower-managed SCP and now governance is inconsistent.
**Options:** A) Leave it B) Control Tower flags **drift**; re-register/repair the landing zone and restrict who can modify managed resources C) Delete the account D) New org
**Correct:** B
**Explanation:** Use Control Tower drift detection to repair; prevent out-of-band changes to managed resources.

### H8

**Scenario:** Leadership worries an SCP guardrail might lock the org out via the management account.
**Options:** A) It applies everywhere B) **SCPs don't apply to the management account** — design break-glass access and avoid running workloads there C) Disable SCPs D) Root only
**Correct:** B
**Explanation:** The management account is exempt from SCPs; keep it minimal with break-glass access.

### H9

**Scenario:** A 200-account enterprise wants consistent security tooling (GuardDuty/Security Hub) enabled in every account, including future ones.
**Options:** A) Per-account manual B) Delegated admin + **org-enabled** security services + Control Tower guardrails/CfCT so new accounts inherit C) One account D) Budgets
**Correct:** B
**Explanation:** Org-level enablement + Control Tower customizations ensure all (incl. future) accounts are covered.

### H10

**Scenario:** Finance wants per-account/OU cost control and volume discounts across the org from the start.
**Options:** A) Separate bills B) **Consolidated billing** (volume discounts, shared RIs/SP) + **Budgets** per account/OU + cost allocation tags C) One account D) Manual
**Correct:** B
**Explanation:** Org consolidated billing aggregates discounts; Budgets + tags give per-account/OU governance.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Secure multi-account baseline → landing zone (Control Tower = managed; LZA = complex/regulated). Vend accounts → Account Factory (Service Catalog; AFT for Terraform). Guardrails: SCP=block, Config=detect, Hooks=deploy-time block. Central Log Archive + Audit accounts. SCPs don't touch the management account.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - AWS Account Factory and Landing Zone SRE Operations](04%20-%20AWS%20Account%20Factory%20and%20Landing%20Zone%20SRE%20Operations.md).
