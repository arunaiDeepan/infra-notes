# AWS CLI - Exam Scenarios

> Exam focus for the CLI: it is mostly tested as the **credentials/automation** surface. Keywords, distractors, elimination technique, and **20 medium + 10 hard** scenarios.

See also: [01 - AWS CLI Intro bits & bytes](01%20-%20AWS%20CLI%20Intro%20bits%20%26%20bytes.md) · [02 - AWS CLI Deep Dive](02%20-%20AWS%20CLI%20Deep%20Dive.md) · [04 - AWS CLI SRE Operations](04%20-%20AWS%20CLI%20SRE%20Operations.md) · [13 - STS & Federation](13%20-%20STS%20%26%20Federation.md)

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

- Credentials on EC2 → **instance profile**, never keys.
- Cross-account access → **role assumption** (STS), named profiles, or Identity Center.
- Key-free human access at scale → **IAM Identity Center SSO**.
- CI/CD without static secrets → **OIDC role assumption**.
- Audit CLI activity → **CloudTrail**.
- Run-commands on fleets without SSH → **Systems Manager**, not CLI+SSH.
- Imperative CLI vs declarative IaC.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                              | Points to                                 |
| :-------------------------------------------------- | :---------------------------------------- |
| "script running on EC2 needs to call S3"            | **IAM role / instance profile**           |
| "access multiple accounts from one laptop"          | **AssumeRole profiles / Identity Center** |
| "no long-term credentials", "temporary credentials" | **STS / roles / SSO**                     |
| "CI pipeline needs AWS access without storing keys" | **OIDC → IAM role**                       |
| "who ran this command / API call"                   | **CloudTrail**                            |
| "run a command on 500 instances, audited, no SSH"   | **SSM Run Command**                       |
| "repeatable, version-controlled infrastructure"     | **CloudFormation/IaC** (not CLI scripts)  |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- "Store access keys in the AMI / user data / S3" — always wrong; use roles.
- "Embed keys in the CI config" — wrong; use OIDC role assumption.
- "Use the CLI to provision infrastructure repeatably" — IaC is the better answer.
- "CLI bypasses IAM" — false; same IAM as the console.
- "Use root access keys for automation" — never.

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **Any mention of stored/long-lived keys** → eliminate; the answer involves **roles/STS/Identity Center**.
2. **EC2/ECS/Lambda needs AWS access** → role attached to the compute (instance profile / task role / execution role).
3. **"Repeatable infrastructure"** → IaC, not imperative CLI.
4. **"Audit"** → CloudTrail.
5. **"Fleet operations / no SSH"** → Systems Manager.

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** A script on EC2 uses the CLI to read S3. How should it authenticate?
**Options:** A) Keys in user data B) Instance profile (IAM role) C) Keys in the AMI D) Root keys
**Correct:** B
**Explanation:** Attach an IAM role; the credential chain finds it via IMDS, with automatic rotation.

### Q2

**Scenario:** An engineer must run CLI commands as an admin role in a different account.
**Options:** A) Share admin keys B) Named profile with role_arn + source_profile (AssumeRole) C) Create a duplicate user D) Use root
**Correct:** B
**Explanation:** Role assumption via STS is the cross-account pattern.

### Q3

**Scenario:** 200 developers need key-free CLI access across many accounts.
**Options:** A) IAM users per account B) IAM Identity Center SSO profiles C) Shared keys D) Root
**Correct:** B
**Explanation:** `aws configure sso` with Identity Center issues short-lived credentials centrally.

### Q4

**Scenario:** A GitHub Actions pipeline needs to deploy to AWS without storing secrets.
**Options:** A) Store keys as repo secrets B) OIDC federation to an IAM role C) Hardcode in workflow D) Email keys
**Correct:** B
**Explanation:** GitHub OIDC → `AssumeRoleWithWebIdentity`; no static keys.

### Q5

**Scenario:** Security needs to know who deleted a DynamoDB table via CLI.
**Options:** A) CloudWatch B) CloudTrail C) Config D) VPC Flow Logs
**Correct:** B
**Explanation:** CloudTrail records the `DeleteTable` API call and the caller identity.

### Q6

**Scenario:** Run a patch command on 500 instances, audited, no SSH keys.
**Options:** A) CLI + SSH loop B) SSM Run Command C) Bastion host D) User data
**Correct:** B
**Explanation:** Systems Manager Run Command is agent-based, IAM-gated, CloudTrail-logged.

### Q7

**Scenario:** A team wants repeatable, reviewable infrastructure across environments.
**Options:** A) CLI scripts B) CloudFormation C) Console D) Manual runbook
**Correct:** B
**Explanation:** Declarative IaC gives versioning, drift detection, idempotency.

### Q8

**Scenario:** CLI calls suddenly fail with signature/time errors on one host.
**Options:** A) Rotate keys B) Fix system clock (NTP) C) Change region D) Reinstall CLI
**Correct:** B
**Explanation:** SigV4 includes a timestamp; clock skew invalidates the signature.

### Q9

**Scenario:** A bulk `describe` script fails intermittently with ThrottlingException.
**Options:** A) Increase IAM perms B) Add retries/backoff and lower page size C) Use root D) Switch to console
**Correct:** B
**Explanation:** Respect API rate limits with exponential backoff and pagination.

### Q10

**Scenario:** Need to extract just instance IDs from a describe call in a script.
**Options:** A) grep raw JSON B) `--query` JMESPath / `--output text` C) Manual copy D) Console
**Correct:** B
**Explanation:** `--query` filters client-side; `--output text` pipes cleanly.

### Q11

**Scenario:** Keep CLI-to-API traffic off the public internet inside a VPC.
**Options:** A) NAT only B) VPC interface endpoint (PrivateLink) + endpoint policy C) Public subnet D) Internet gateway
**Correct:** B
**Explanation:** Interface endpoints route API calls privately.

### Q12

**Scenario:** A user must provide MFA for sensitive CLI actions.
**Options:** A) Password only B) STS GetSessionToken with MFA / IAM condition aws:MultiFactorAuthPresent C) Disable MFA D) Root
**Correct:** B
**Explanation:** Obtain an MFA-backed session; enforce via IAM condition.

### Q13

**Scenario:** Quick authenticated CLI from a browser without installing anything.
**Options:** A) CloudShell B) Local install C) SSH to a server D) Lambda
**Correct:** A
**Explanation:** CloudShell is pre-authenticated with your console identity.

### Q14

**Scenario:** A profile assumes a role but the session keeps expiring after an hour during chaining.
**Options:** A) Bug — open a ticket B) Expected: chained roles max 1 hour C) Increase to 12h D) Use root
**Correct:** B
**Explanation:** Role chaining caps session duration at 1 hour.

### Q15

**Scenario:** Lambda function uses the SDK/CLI tooling to call SQS. Credentials?
**Options:** A) Env keys B) Execution role C) Instance profile D) Hardcoded
**Correct:** B
**Explanation:** Lambda uses its execution role via the provider chain.

### Q16

**Scenario:** ECS task needs AWS API access.
**Options:** A) Keys in image B) Task role C) Instance profile of host D) Root
**Correct:** B
**Explanation:** Use the ECS **task role**, not the host's instance profile.

### Q17

**Scenario:** A script must wait until an instance is running before continuing.
**Options:** A) sleep 60 B) `aws ec2 wait instance-running` C) Loop describe manually D) Console refresh
**Correct:** B
**Explanation:** Waiters poll the correct state cleanly.

### Q18

**Scenario:** Reduce data transferred when listing millions of objects.
**Options:** A) Client-side `--query` only B) Server-side filters + `--page-size` C) Download all D) No pagination
**Correct:** B
**Explanation:** Server-side filtering and pagination limit payload.

### Q19

**Scenario:** Compliance requires FIPS 140-2 validated endpoints for CLI traffic.
**Options:** A) Default endpoints B) FIPS endpoints (`*-fips`) C) Dual-stack D) Custom URL
**Correct:** B
**Explanation:** Use FIPS endpoints for validated crypto.

### Q20

**Scenario:** A developer accidentally committed access keys to GitHub.
**Options:** A) Ignore B) Immediately deactivate/delete the keys, rotate, and move to roles/SSO C) Change region D) Add MFA later
**Correct:** B
**Explanation:** Treat as compromised: revoke now, then eliminate static keys entirely.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** A multi-account org wants every CI pipeline to deploy into target accounts with least privilege, no static keys, and full auditability of which pipeline did what.
**Options:** A) Shared admin keys per account B) Pipeline assumes a per-account deploy role via OIDC; CloudTrail records the role session name; SCPs cap the role C) Root keys D) IAM users per pipeline
**Correct:** B
**Explanation:** OIDC + per-account roles (with a meaningful **session name**) gives least privilege, no secrets, and CloudTrail attribution; SCP guardrails cap the blast radius.

### H2

**Scenario:** A CLI script on EC2 intermittently picks up the _wrong_ credentials — sometimes env vars left by a previous job, sometimes the instance profile.
**Options:** A) Random AWS bug B) Provider-chain precedence: env vars outrank the instance profile — unset them or pin a profile C) Reinstall CLI D) Change region
**Correct:** B
**Explanation:** The chain is ordered; stale `AWS_*` env vars take precedence over the instance profile. Unset them or explicitly select the source.

### H3

**Scenario:** An attacker on a compromised EC2 web app retrieved the instance role credentials via SSRF against the metadata service.
**Options:** A) Rotate keys B) Enforce **IMDSv2** (HttpTokens=required) and limit hop count; scope the role tightly C) Remove the role D) Disable CLI
**Correct:** B
**Explanation:** IMDSv2's session-token requirement defeats most SSRF credential theft; least-privilege limits damage.

### H4

**Scenario:** Bulk operations across thousands of resources cause cascading ThrottlingExceptions that also impact the team's console.
**Options:** A) Raise IAM perms B) Adaptive retry mode + jitter + smaller page size + spread over time; request quota increase if structural C) Use root D) Ignore
**Correct:** B
**Explanation:** API rate limits are account/region-scoped; throttle-aware clients plus quota increases are the fix.

### H5

**Scenario:** A regulated workload must guarantee CLI/API traffic never traverses the public internet and only specific APIs are reachable.
**Options:** A) NAT gateway B) VPC interface endpoints (PrivateLink) with restrictive endpoint policies + SCP denying calls without aws:SourceVpce C) Public subnet D) Proxy
**Correct:** B
**Explanation:** PrivateLink keeps traffic private; endpoint policies + `aws:SourceVpce` SCP conditions constrain which APIs and enforce the private path.

### H6

**Scenario:** A break-glass admin must use the CLI only with MFA, and the org must prove MFA was present for any privileged action.
**Options:** A) Password policy B) STS session acquired with MFA + IAM condition `aws:MultiFactorAuthPresent=true` on privileged actions; CloudTrail shows the MFA-authenticated session C) Hardware token only D) Root
**Correct:** B
**Explanation:** Enforce MFA via condition keys; the MFA-backed STS session is auditable in CloudTrail.

### H7

**Scenario:** Cross-account role chaining for a deployment tool keeps failing after 1 hour during long deployments.
**Options:** A) Increase session to 12h B) Avoid chaining: assume the target role **directly** from the source identity (not role→role) so a longer duration applies, or refresh credentials C) Use root D) Disable STS
**Correct:** B
**Explanation:** **Chained** roles are hard-capped at 1 hour; assuming directly (or refreshing) avoids the cap.

### H8

**Scenario:** A script must run identically in dev, staging, and prod accounts without code changes.
**Options:** A) Hardcode account IDs B) Parameterise via named profiles/env + assume per-env roles; keep the logic identical C) Separate scripts D) Manual edits
**Correct:** B
**Explanation:** Externalise identity/region via profiles/roles so the same script targets any environment.

### H9

**Scenario:** Teams keep drifting infrastructure because some changes are made via ad-hoc CLI and some via CloudFormation.
**Options:** A) Ban the CLI B) Make CloudFormation the source of truth, restrict mutating CLI in prod via SCP/permissions, use Config drift detection C) More documentation D) Manual reviews
**Correct:** B
**Explanation:** Governance fix: IaC as source of truth, restrict imperative changes, detect drift with Config.

### H10

**Scenario:** An auditor needs to confirm that a specific automated job — not a human — performed a sensitive deletion.
**Options:** A) Check IAM users B) CloudTrail event shows the assumed-role ARN + role session name used by the job; correlate to the automation C) Ask the team D) VPC Flow Logs
**Correct:** B
**Explanation:** Distinct **role session names** per job make CloudTrail attribute actions to the automation rather than a person.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **No stored keys — ever. EC2/ECS/Lambda → role on the compute. Cross-account → AssumeRole. Humans at scale → Identity Center. CI → OIDC. Audit → CloudTrail. Fleet ops → Systems Manager. Repeatable infra → IaC, not scripts.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - AWS CLI SRE Operations](04%20-%20AWS%20CLI%20SRE%20Operations.md).
