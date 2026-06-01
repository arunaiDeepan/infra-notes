# AWS Systems Manager - Exam Scenarios

> Exam focus: Session Manager vs bastion, Patch Manager, Parameter Store vs Secrets Manager, private connectivity via endpoints, and Automation for remediation. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - AWS Systems Manager Intro bits & bytes](01%20-%20AWS%20Systems%20Manager%20Intro%20bits%20%26%20bytes.md) · [02 - AWS Systems Manager Deep Dive](02%20-%20AWS%20Systems%20Manager%20Deep%20Dive.md) · [04 - AWS Systems Manager SRE Operations](04%20-%20AWS%20Systems%20Manager%20SRE%20Operations.md) · [22 - Secrets Manager vs SSM Parameter Store](22%20-%20Secrets%20Manager%20vs%20SSM%20Parameter%20Store.md)

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

- **Session Manager** = keyless, portless, audited shell → replaces bastion hosts.
- **Run Command** = fleet-wide execution, IAM-gated, no SSH.
- **Patch Manager + Maintenance Windows** = scheduled compliant patching.
- **Parameter Store** (free config/secrets) vs **Secrets Manager** (auto-rotation).
- **Private subnets** need **interface endpoints** (ssm, ssmmessages, ec2messages).
- **Automation** for self-healing / Config remediation.
- Managed-node prerequisites (agent + instance profile + connectivity).

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                                         | Points to                                |
| :------------------------------------------------------------- | :--------------------------------------- |
| "access instances without SSH keys / open ports / bastion"     | **Session Manager**                      |
| "audit/log all shell access"                                   | **Session Manager → S3/CloudWatch Logs** |
| "patch hundreds of instances on a schedule, report compliance" | **Patch Manager + Maintenance Windows**  |
| "run a command/script across the fleet, controlled"            | **Run Command**                          |
| "store config / DB string centrally, low cost"                 | **Parameter Store**                      |
| "automatically rotate the database password"                   | **Secrets Manager**                      |
| "private subnet, no internet, still use SSM"                   | **Interface VPC endpoints**              |
| "auto-remediate / self-heal a resource"                        | **Automation runbook**                   |
| "manage on-prem servers too"                                   | **Hybrid Activations**                   |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Bastion host / open SSH when **Session Manager** is the secure answer.
- **Parameter Store** for "auto-rotation" (that's Secrets Manager).
- Forgetting **interface endpoints** for private-subnet SSM.
- Using **NAT/bastion** when endpoints are cheaper/more secure.
- Custom SSH automation when **Run Command** is meant.
- Lambda for an ops task that **Automation** runbooks handle natively.

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **"No SSH / no port / no bastion / audited"** → Session Manager.
2. **"Patch + schedule + compliance"** → Patch Manager + Maintenance Windows.
3. **"Auto-rotate secret"** → Secrets Manager; else cheap config → Parameter Store.
4. **"Private subnet + SSM"** → interface endpoints.
5. **"Self-heal / remediate"** → Automation (often via EventBridge/Config).

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** Engineers need shell access to private EC2 with no SSH keys, no open ports, fully logged.
**Options:** A) Bastion host B) Session Manager C) VPN + SSH D) Public IP
**Correct:** B
**Explanation:** Session Manager is keyless, portless, audited.

### Q2

**Scenario:** Patch 500 instances monthly with compliance reporting.
**Options:** A) Manual B) Patch Manager + Maintenance Windows C) Run Command only D) Lambda
**Correct:** B
**Explanation:** Patch baselines on a scheduled window with compliance.

### Q3

**Scenario:** Store DB credentials that must auto-rotate every 30 days.
**Options:** A) Parameter Store SecureString B) Secrets Manager C) S3 D) Env var
**Correct:** B
**Explanation:** Built-in rotation is Secrets Manager.

### Q4

**Scenario:** Cheap centralized app configuration, hundreds of keys.
**Options:** A) Secrets Manager B) Parameter Store standard tier C) DynamoDB D) S3
**Correct:** B
**Explanation:** Parameter Store standard tier is free.

### Q5

**Scenario:** Private-subnet instances (no internet) must be SSM-managed.
**Options:** A) NAT only B) Interface endpoints for ssm/ssmmessages/ec2messages C) Public subnet D) Bastion
**Correct:** B
**Explanation:** Interface endpoints give the private path.

### Q6

**Scenario:** Run a one-off script on all instances tagged Env=prod.
**Options:** A) SSH loop B) Run Command targeting the tag C) State Manager D) Automation
**Correct:** B
**Explanation:** Run Command targets by tag, IAM-gated.

### Q7

**Scenario:** Keep the SSM agent installed and config applied continuously.
**Options:** A) Run Command once B) State Manager (desired state) C) Patch Manager D) Inventory
**Correct:** B
**Explanation:** State Manager enforces desired state on a schedule.

### Q8

**Scenario:** Auto-remediate a noncompliant resource flagged by Config.
**Options:** A) Manual B) SSM Automation runbook as the remediation C) CloudTrail D) Budgets
**Correct:** B
**Explanation:** Config remediation invokes Automation docs.

### Q9

**Scenario:** Manage on-prem Linux servers with the same tooling.
**Options:** A) Not possible B) Hybrid Activations → managed nodes C) Direct Connect only D) Bastion
**Correct:** B
**Explanation:** Hybrid Activations onboard non-EC2 servers.

### Q10

**Scenario:** Tunnel to a private RDS through an instance without exposing it.
**Options:** A) Public RDS B) Session Manager port forwarding C) Bastion with public IP D) Open SG
**Correct:** B
**Explanation:** Port forwarding tunnels privately.

### Q11

**Scenario:** Reference a parameter in a CloudFormation template at deploy time.
**Options:** A) Hardcode B) `{{resolve:ssm:/path}}` dynamic reference C) Output D) Mapping
**Correct:** B
**Explanation:** Dynamic references pull from Parameter Store.

### Q12

**Scenario:** Instance isn't a managed node.
**Options:** A) Wrong region only B) Check agent, instance profile perms, connectivity to SSM C) Reboot D) New AMI
**Correct:** B
**Explanation:** The three prerequisites: agent, IAM, network.

### Q13

**Scenario:** Restrict who can start sessions to specific tagged instances with MFA.
**Options:** A) Not possible B) IAM policy conditions on tags + aws:MultiFactorAuthPresent C) Bastion ACL D) SG
**Correct:** B
**Explanation:** IAM conditions gate Session Manager access.

### Q14

**Scenario:** Collect software inventory across the fleet.
**Options:** A) Manual audit B) SSM Inventory (State Manager) C) Config only D) CloudTrail
**Correct:** B
**Explanation:** Inventory gathers installed software/config.

### Q15

**Scenario:** Different patch schedules for web vs db tiers.
**Options:** A) One baseline B) Patch groups (tags) with separate baselines/windows C) Manual D) Lambda
**Correct:** B
**Explanation:** Patch groups segment fleets.

### Q16

**Scenario:** Encrypt a stored secret value in Parameter Store.
**Options:** A) String B) SecureString with KMS C) StringList D) Plaintext
**Correct:** B
**Explanation:** SecureString uses KMS.

### Q17

**Scenario:** Remove bastion and NAT cost for SSM-only access.
**Options:** A) Keep both B) Interface endpoints + Session Manager C) Public IPs D) VPN
**Correct:** B
**Explanation:** Endpoints + Session Manager eliminate bastion/NAT for management.

### Q18

**Scenario:** Build/patch a golden AMI on a schedule.
**Options:** A) Manual B) SSM Automation (or Image Builder) C) Run Command only D) State Manager
**Correct:** B
**Explanation:** Automation runbooks orchestrate AMI build/patch.

### Q19

**Scenario:** Trigger a remediation runbook when a security event fires.
**Options:** A) Poll B) EventBridge rule → SSM Automation C) Cron on a server D) Config snapshot
**Correct:** B
**Explanation:** EventBridge invokes Automation in real time.

### Q20

**Scenario:** Parameter policy to expire a temporary parameter automatically.
**Options:** A) Standard tier B) Advanced tier parameter policy (expiration) C) Secrets Manager D) Manual delete
**Correct:** B
**Explanation:** Parameter policies require the advanced tier.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** A regulated bank must give operators shell access to thousands of private instances with **no inbound ports**, full keystroke audit, MFA, and per-team restriction — and remove all bastions.
**Options:** A) Hardened bastions B) **Session Manager** with interface endpoints, S3/CloudWatch session logging (keystroke logging on), IAM tag-based access + MFA conditions; decommission bastions C) VPN + SSH D) Public IPs with SG rules
**Correct:** B
**Explanation:** Session Manager satisfies no-ports, audit, MFA, and per-team IAM scoping; endpoints serve private subnets; bastions become unnecessary.

### H2

**Scenario:** Private subnets with no NAT; instances must be patched (download patches) and managed, at minimal cost.
**Options:** A) Add NAT B) Interface endpoints for ssm/ssmmessages/ec2messages + S3 gateway endpoint (patch downloads) + logs endpoint C) Public subnet D) Bastion
**Correct:** B
**Explanation:** SSM endpoints for control, **S3 gateway endpoint** for patch content, logs endpoint for logging — no NAT needed.

### H3

**Scenario:** App config and secrets are sprawled across env vars and files; the team wants central config (cheap) but DB creds with automatic rotation.
**Options:** A) All in Secrets Manager B) **Parameter Store** for general config (free) + **Secrets Manager** for the rotating DB credentials; apps read both via IAM C) All in Parameter Store D) Hardcode
**Correct:** B
**Explanation:** Use the cheap store for config and the rotating store for managed credentials — right tool per need.

### H4

**Scenario:** Security wants every Config noncompliance (e.g. public SG) auto-remediated within minutes, audited.
**Options:** A) Manual ticket B) Config rule → **automatic remediation** via SSM **Automation** runbook (least-privilege assume role); CloudTrail audits C) Daily script D) Lambda cron
**Correct:** B
**Explanation:** Config + Automation remediation is the native auto-heal pattern, fully audited.

### H5

**Scenario:** A patch rollout must never take down more than 10% of a fleet at once and must pause outside an approved change window.
**Options:** A) Patch all at once B) Patch Manager via **Maintenance Window** with concurrency/error thresholds + **Change Calendar** to block outside approved windows C) Manual D) Run Command ad hoc
**Correct:** B
**Explanation:** Maintenance Window concurrency limits bound blast radius; Change Calendar enforces the freeze window.

### H6

**Scenario:** At scale, the app throttles on `GetParameter` for a heavily-read SecureString.
**Options:** A) Add IAM perms B) Cache locally / batch with `GetParametersByPath`, use the parameters cache/agent, or raise throughput tier; reduce per-request calls C) Switch to plaintext D) More KMS keys
**Correct:** B
**Explanation:** Reduce call volume via caching/batching (and higher throughput tier) — throttling is a request-rate issue.

### H7

**Scenario:** Operators occasionally need emergency access but the org wants approvals and a record for each privileged session.
**Options:** A) Standing admin B) **Change Manager** (approval workflow) + Session Manager with logging; break-glass role assumed only after approval C) Shared key D) Bastion
**Correct:** B
**Explanation:** Change Manager adds approval/audit around privileged operations; sessions are logged.

### H8

**Scenario:** A hybrid estate (EC2 + on-prem + another cloud) needs unified patching and inventory.
**Options:** A) Separate tools B) **Hybrid Activations** register non-EC2 servers as managed nodes; Patch Manager + Inventory apply uniformly C) Manual per environment D) Bastions
**Correct:** B
**Explanation:** Hybrid Activations bring non-AWS servers under the same SSM management plane.

### H9

**Scenario:** A self-healing requirement: when an instance fails its app health check, automatically capture logs, attempt restart, and replace if still failing — with an audit trail.
**Options:** A) Manual runbook B) CloudWatch alarm/EventBridge → **SSM Automation** runbook (collect logs → restart → conditionally replace), least-privilege role, CloudTrail audit C) Lambda only D) Cron
**Correct:** B
**Explanation:** Automation runbooks chain the steps with branching; events trigger them; CloudTrail records execution.

### H10

**Scenario:** A multi-account org wants standardized SSM access policy, logging, and endpoints in every account without per-team setup.
**Options:** A) Manual per account B) Deploy SSM logging config, endpoints, and IAM baselines via **CloudFormation StackSets**; enforce with SCPs; centralize session logs in a log-archive account C) Email instructions D) One shared account
**Correct:** B
**Explanation:** StackSets standardize the SSM baseline org-wide; SCPs enforce; central logging aggregates audit. See [01 - AWS CloudFormation Intro bits & bytes](01%20-%20AWS%20CloudFormation%20Intro%20bits%20%26%20bytes.md).

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Keyless audited shell → Session Manager (kills bastions). Fleet commands → Run Command. Scheduled compliant patching → Patch Manager + Maintenance Windows. Cheap config → Parameter Store; auto-rotation → Secrets Manager. Private subnet → interface endpoints. Self-heal/remediate → Automation.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - AWS Systems Manager SRE Operations](04%20-%20AWS%20Systems%20Manager%20SRE%20Operations.md).
