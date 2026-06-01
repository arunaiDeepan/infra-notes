# AWS Management Console - Exam Scenarios

> Exam focus: sign-in identities (root/IAM/Identity Center/federation), MFA, console=CLI=API IAM, and ConsoleLogin auditing. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - AWS Management Console Intro bits & bytes](01%20-%20AWS%20Management%20Console%20Intro%20bits%20%26%20bytes.md) · [02 - AWS Management Console Deep Dive](02%20-%20AWS%20Management%20Console%20Deep%20Dive.md) · [04 - AWS Management Console SRE Operations](04%20-%20AWS%20Management%20Console%20SRE%20Operations.md) · [06 - IAM Identity Center & Organizations](06%20-%20IAM%20Identity%20Center%20%26%20Organizations.md)

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

- **Identity Center/federation > IAM users** for workforce console access.
- **Root** only for root-only tasks; **MFA** everywhere.
- Console = CLI = API (**same IAM, same CloudTrail**).
- **Switch Role** for cross-account console access.
- **ConsoleLogin** auditing; alarm on root/failed logins.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                              | Points to                        |
| :-------------------------------------------------- | :------------------------------- |
| "workforce sign-in across many accounts"            | **IAM Identity Center (SSO)**    |
| "use existing corporate IdP to access console"      | **SAML/OIDC federation**         |
| "temporary console credentials"                     | **Federation / Identity Center** |
| "access another account's console without re-login" | **Switch Role (cross-account)**  |
| "audit who logged into the console"                 | **CloudTrail ConsoleLogin**      |
| "secure root / human sign-in"                       | **MFA**                          |
| "repeatable infrastructure"                         | **IaC, not console**             |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Creating **IAM users per account** when **Identity Center** is the scalable answer.
- Using **root** for daily work.
- Believing the console has **different permissions** than the CLI.
- Doing **repeatable** infra in the console instead of IaC.
- Sharing a **single login** among people.

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **"Workforce/many accounts sign-in"** → Identity Center/federation.
2. **"Existing IdP"** → SAML/OIDC federation.
3. **"Cross-account console"** → Switch Role.
4. **"Audit logins"** → CloudTrail ConsoleLogin.
5. **"Repeatable"** → IaC (not console).

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** 500 employees need console access across 25 accounts with central control.
**Options:** A) IAM users per account B) IAM Identity Center (SSO) C) Root D) Shared login
**Correct:** B
**Explanation:** Identity Center scales workforce access org-wide.

### Q2

**Scenario:** Use the company's existing Okta/AD to sign in to the console.
**Options:** A) IAM users B) SAML/OIDC federation C) Root D) Access keys
**Correct:** B
**Explanation:** Federation uses the corporate IdP.

### Q3

**Scenario:** Does a console click have more authority than a CLI call?
**Options:** A) Yes B) No — same IAM/API/CloudTrail C) Only for root D) Only S3
**Correct:** B
**Explanation:** Same permissions and audit.

### Q4

**Scenario:** Access account B's console from account A without a second login.
**Options:** A) New user B) Switch Role (cross-account) C) Root D) Keys
**Correct:** B
**Explanation:** Switch Role assumes a role in B.

### Q5

**Scenario:** Audit who signed into the console and whether MFA was used.
**Options:** A) Config B) CloudTrail ConsoleLogin C) Budgets D) VPC Flow Logs
**Correct:** B
**Explanation:** ConsoleLogin events capture sign-in detail.

### Q6

**Scenario:** Secure the root user.
**Options:** A) Daily use B) Enable MFA, lock away, use only for root-only tasks C) Share it D) Access keys
**Correct:** B
**Explanation:** Root hygiene.

### Q7

**Scenario:** Repeatable, reviewable environment setup.
**Options:** A) Console clicks B) CloudFormation/IaC C) Mobile app D) CloudShell
**Correct:** B
**Explanation:** IaC for repeatability.

### Q8

**Scenario:** Quick CLI from the browser, no local setup.
**Options:** A) Local install B) CloudShell C) Mobile app D) SSH
**Correct:** B
**Explanation:** CloudShell is pre-authenticated.

### Q9

**Scenario:** Monitor alarms/health from a phone, take limited action.
**Options:** A) Not possible B) AWS Console Mobile App C) CLI only D) CloudShell
**Correct:** B
**Explanation:** Mobile app for on-the-go.

### Q10

**Scenario:** Friendly sign-in URL instead of account number.
**Options:** A) Not possible B) Account alias C) Federation only D) Root
**Correct:** B
**Explanation:** Account alias.

### Q11

**Scenario:** Require MFA for sensitive console actions.
**Options:** A) Password only B) IAM condition aws:MultiFactorAuthPresent C) Disable MFA D) Root
**Correct:** B
**Explanation:** Enforce MFA via condition.

### Q12

**Scenario:** Temporary console credentials with no long-lived password.
**Options:** A) IAM user password B) Federation/Identity Center (STS) C) Root D) Access keys
**Correct:** B
**Explanation:** Federated sessions are temporary.

### Q13

**Scenario:** Cap what a console user can do regardless of their policy.
**Options:** A) Nothing B) SCP / permissions boundary C) Bigger role D) Root
**Correct:** B
**Explanation:** SCP/boundary set the ceiling.

### Q14

**Scenario:** Alert when the root user logs in.
**Options:** A) Monthly B) CloudWatch metric filter/EventBridge on root ConsoleLogin C) Config D) Budgets
**Correct:** B
**Explanation:** Alarm on root sign-in.

### Q15

**Scenario:** One human, one identity (no sharing).
**Options:** A) Shared admin B) Individual IAM/Identity Center identities C) Root for all D) One key
**Correct:** B
**Explanation:** Never share credentials.

### Q16

**Scenario:** Control how long a console session lasts.
**Options:** A) Fixed forever B) Permission set / role session duration C) Not possible D) Root only
**Correct:** B
**Explanation:** Session duration is configurable.

### Q17

**Scenario:** Build a custom portal that logs users into the console without IAM users.
**Options:** A) Impossible B) Federation broker: STS + console sign-in URL C) Share root D) Keys
**Correct:** B
**Explanation:** Custom federation generates sign-in URLs.

### Q18

**Scenario:** Cost of using the console.
**Options:** A) Per click B) Free (pay for resources) C) Per session D) Per user
**Correct:** B
**Explanation:** Console is free.

### Q19

**Scenario:** Reduce click-driven misconfiguration in prod.
**Options:** A) More clicking B) IaC + restrict prod console changes C) Root D) Bigger team
**Correct:** B
**Explanation:** IaC + guardrails reduce human error.

### Q20

**Scenario:** Passwordless/strong console MFA option.
**Options:** A) SMS only B) Hardware key / passkey MFA C) None D) Email
**Correct:** B
**Explanation:** Hardware/passkey MFA strengthens sign-in.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** A 2,000-employee enterprise with 60 accounts wants single sign-on to the console using their existing IdP, least-privilege per account, no long-lived passwords, and full sign-in audit.
**Options:** A) IAM users everywhere B) **IAM Identity Center** federated to the corporate IdP, **permission sets** per account (least privilege), temporary sessions, **CloudTrail** ConsoleLogin audit C) Shared admin D) Root
**Correct:** B
**Explanation:** Identity Center + IdP federation + permission sets gives scalable, least-privilege, passwordless, audited console access.

### H2

**Scenario:** Security must be alerted instantly whenever the root user signs in to the console.
**Options:** A) Monthly review B) Org **CloudTrail** → CloudWatch metric filter / EventBridge on `ConsoleLogin` where `userIdentity.type=Root` → SNS C) Config D) Budgets
**Correct:** B
**Explanation:** Real-time root sign-in alerting via CloudTrail-driven alarm/EventBridge.

### H3

**Scenario:** An app must let external users open the AWS console scoped to a role, without giving them IAM users.
**Options:** A) Share IAM creds B) **Custom federation broker**: app calls STS AssumeRole, then builds a console **sign-in URL** (getSigninToken) C) Root D) Access keys
**Correct:** B
**Explanation:** The federation endpoint produces a temporary console sign-in URL from STS credentials.

### H4

**Scenario:** Operators keep making inconsistent prod changes via the console, causing drift.
**Options:** A) More training only B) Make **IaC** the source of truth; restrict mutating console actions in prod via **SCP/permissions**; detect drift with **Config** C) Ban console D) Manual reviews
**Correct:** B
**Explanation:** Governance: IaC source of truth + restrict console writes + drift detection.

### H5

**Scenario:** Compliance requires MFA proof for any privileged console action.
**Options:** A) Password policy B) Enforce **MFA** (hardware/passkey) + IAM condition `aws:MultiFactorAuthPresent` on privileged actions; ConsoleLogin shows MFA used C) SMS only D) Root
**Correct:** B
**Explanation:** MFA enforcement + condition keys + audit evidences privileged-action MFA.

### H6

**Scenario:** Engineers need to move between many org accounts' consoles quickly and safely.
**Options:** A) Separate logins B) **Identity Center portal** (or **Switch Role**) for seamless cross-account assumption with per-account permission sets C) Shared admin D) Root
**Correct:** B
**Explanation:** Identity Center/Switch Role provide seamless, least-privilege cross-account console access.

### H7

**Scenario:** A regulated org must ensure even powerful console users can't exceed an organizational ceiling.
**Options:** A) Trust policies B) **SCPs** (and permissions boundaries) cap console users regardless of their attached policies C) Bigger roles D) Root
**Correct:** B
**Explanation:** SCPs/boundaries set the hard ceiling on any console identity.

### H8

**Scenario:** On-call engineers need to acknowledge alarms and stop a runaway instance from their phones at night.
**Options:** A) Laptop only B) **AWS Console Mobile App** for alarms/Health + limited actions (stop instance) C) CLI only D) Not possible
**Correct:** B
**Explanation:** The mobile app supports monitoring and limited actions for on-call.

### H9

**Scenario:** After an incident, investigators need to know exactly who signed in, from where, with MFA, around the event.
**Options:** A) Ask the team B) **CloudTrail ConsoleLogin** events (identity, source IP, MFA, success/failure) correlated with other CloudTrail activity C) Config D) VPC Flow Logs
**Correct:** B
**Explanation:** ConsoleLogin events provide the sign-in forensic detail.

### H10

**Scenario:** Leadership asks whether the console or CLI is "more secure" for the same admin task.
**Options:** A) Console is safer B) **Neither** — same IAM/API/audit; security comes from identity (MFA, least privilege, federation), not the interface C) CLI is safer D) Root is fine
**Correct:** B
**Explanation:** Authority/audit are identical; security derives from how the identity is authenticated and scoped.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Console = web front door; same IAM/API/CloudTrail as CLI. Workforce sign-in at scale → Identity Center/federation (temporary creds). Root → emergency only + MFA. Cross-account → Switch Role. Audit → ConsoleLogin. Repeatable work → IaC, not clicks.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - AWS Management Console SRE Operations](04%20-%20AWS%20Management%20Console%20SRE%20Operations.md).
