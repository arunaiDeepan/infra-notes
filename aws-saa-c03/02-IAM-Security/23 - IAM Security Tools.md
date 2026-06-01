# IAM Security Tools

> The full inspection / governance / hardening toolkit around IAM: account-level guardrails (SCPs, Permissions Boundaries), analysis tools (Access Analyzer, Credential Report, Access Advisor), and the non-negotiable foundational practices (password policy, MFA, root lockdown). High-yield for the SAA-C03 Security domain.

See also: [08 - SCP](08%20-%20SCP.md) · [09 - RCP](09%20-%20RCP.md) · [11 - Permissions Boundaries](11%20-%20Permissions%20Boundaries.md) · [10 - Declarative Policies](10%20-%20Declarative%20Policies.md) · [06 - IAM Identity Center & Organizations](06%20-%20IAM%20Identity%20Center%20%26%20Organizations.md) · [01 - IAM Intro bits & bytes](01%20-%20IAM%20Intro%20bits%20%26%20bytes.md)

---

## Table of Contents

- [Part 1: Account-Level Guardrails (The Big Filters)](#part-1-account-level-guardrails-the-big-filters)
- [Part 2: User & Resource Level Tools (Analysis & Visibility)](#part-2-user--resource-level-tools-analysis--visibility)
- [Part 3: Foundational Best Practices (The Golden Rules)](#part-3-foundational-best-practices-the-golden-rules)
- [Summary: The Security Maturity Model](#summary-the-security-maturity-model)

---

This documents cover the tools and best practices at three levels:

1. **Account Level (Guardrails):** Service Control Policies (SCPs) and Permissions Boundaries.
2. **User/Resource Level (Analysis & Auditing):** IAM Access Analyzer, IAM Credential Report, and Access Advisor.
3. **Foundational Best Practices (The "Golden Rules"):** Password policies, MFA enforcement, and Root user protection.

---

## Part 1: Account-Level Guardrails (The Big Filters)

These tools operate across many users or even entire AWS Organizations. They define the _maximum_ permissions possible.

### 🛡️ Service Control Policies (SCPs)

An **SCP** is a policy attached to an AWS Organization account, Organizational Unit (OU), or Root. It defines the **maximum permissions** for _all_ IAM users and roles in those accounts.

**How they work (The "Filter" Analogy):**
Imagine permissions as water flowing down a pipe.

- **IAM Policies** (inside an account) decide how much water a specific user can drink.
- **SCPs** (at the organization level) decide the maximum diameter of the pipe feeding that account.

If an SCP **denies** `s3:DeleteBucket`, even a user with the `AdministratorAccess` IAM policy **cannot** delete an S3 bucket.

**Key Concepts & Inheritance:**

- **Deny Overrides Allow:** If an SCP explicitly denies an action, no policy lower down can allow it.
- **Inheritance is Intersection:** If the Root allows A, B, C and an OU allows C, D, E – the effective permission for the account is only **C** (the intersection). Permissions are filtered at every level.
- **No Permissions Granted:** SCPs never _grant_ permissions. They only filter what IAM policies _can_ grant.

**Strategies:**

- **Deny-List Strategy (Easier to start):** Start with `FullAWSAccess` attached everywhere. Then attach specific SCPs to _deny_ dangerous actions (e.g., `Deny ec2:TerminateInstances`).
- **Allow-List Strategy (Stricter):** Remove `FullAWSAccess`. Create SCPs that explicitly _allow_ only specific services (e.g., only EC2 and S3). Everything else is implicitly denied.

### 🔒 Permissions Boundaries

A **Permissions Boundary** is an advanced feature that sets the **maximum permissions** for a _single_ IAM user or role (not an entire account).

- **Use Case:** Delegating administration. You can allow a developer to "create IAM roles," but use a Boundary to ensure those new roles cannot access billing or delete logs.
- **Effect:** A user's effective permissions are the intersection of their identity-based policy and their permissions boundary.

---

## Part 2: User & Resource Level Tools (Analysis & Visibility)

These tools help you look _inside_ the account to analyze specific users, roles, or policies.

### 📊 IAM Credential Report (Account Level)

A **Credential Report** is a CSV/JSON file that lists **all users** in your account and the status of their various credentials (password, access keys, MFA).

- **How to use:** Generate it from the IAM console. It shows `password_last_used`, `access_key_1_last_used_date`, `mfa_active`, etc.
- **Why it matters:** It is your "source of truth" for identifying unused credentials. If a user hasn't used their console password in 90 days and has no active access keys, you should disable or delete them.

### 🔎 IAM Access Analyzer

This is a suite of tools for continuous evaluation and policy refinement.

#### 1. Unused Access Analyzer

- **What it does:** Identifies unused IAM roles, users, access keys, and passwords.
- **Best Practice:** Run this regularly. If a key hasn't been used in your tracking window, rotate or revoke it.

#### 2. Policy Generation (Least Privilege)

- **What it does:** Analyzes AWS CloudTrail logs to see exactly which actions a user or role _actually_ performed over a specific time (e.g., 7 days). It then generates a policy granting _only those specific actions_.
- **How to use:** Navigate to IAM > Users > Select a user > "Access Advisor" tab > "Generate policy" based on past activity.
- **Result:** You get a fine-grained policy allowing only the APIs they touched, removing wildcard (`*`) permissions.

#### 3. Policy Validation

- **What it does:** Checks your JSON policies against AWS best practices (over 100 checks). It flags security warnings, errors, and suggestions (e.g., "This action is deprecated" or "You allowed `*` on a sensitive action").

### 💡 Access Advisor (Last Accessed Data)

This is a tab on the IAM User/Role/Policy page. It shows the **last time** a specific service was accessed using this entity's permissions.

- **Use Case:** You see an EC2 role has `s3:*` and `dynamodb:*`. Access Advisor shows "S3: Used 2 hours ago" but "DynamoDB: Not Accessed in 30 days." You can confidently remove DynamoDB permissions.

---

## Part 3: Foundational Best Practices (The Golden Rules)

These are the non-negotiable configurations for every AWS account.

### 1. Password Policy

Don't rely on the default AWS password policy (which allows weak passwords). Enforce a **custom policy**:

- **Minimum Length:** 14 characters.
- **Complexity:** Require uppercase, lowercase, numbers, and symbols.
- **Rotation:** Expire passwords every 90 days (`MaxPasswordAge`).
- **Reuse Prevention:** Prevent reuse of the last 24 passwords (`PasswordReusePrevention`).

### 2. MFA Enforcement (The "Emergency Brake")

Passwords are stolen constantly (phishing, keyloggers). MFA stops a stolen password from being useful.

**How to enforce it:**
Do not just "ask nicely" for MFA. **Enforce it with a policy**.
Attach this policy to any group or user requiring MFA (e.g., Admins, Developers):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "BoolIfExists": {
          "aws:MultiFactorAuthPresent": "false"
        }
      }
    }
  ]
}
```

_Effect:_ If the user logs in without an MFA code, they are denied access to **everything**.

### 3. Root User Protection

The Root user cannot be restricted by any policy. It is a "backdoor" that must be locked down.

- **Rule 1:** Never use the Root user for daily tasks.
- **Rule 2:** Apply the strongest MFA device you have (hardware key or virtual MFA).
- **Rule 3:** Do not create Root Access Keys. If they exist, delete them immediately.
- **Rule 4:** Use the Root user only for account closure, support plan changes, or restoring IAM admin access.

### 4. Guarding Against Long-Term Keys

The #1 cause of AWS security incidents is **exposed long-term access keys** (hardcoded in code, uploaded to GitHub).

- **Detection:** Use **Amazon Q Developer** (code scanning) and **AWS Trusted Advisor** (public repo checks) to find exposed keys.
- **Prevention:** Use an SCP to **block the creation of access keys** entirely for human users, forcing them to use Identity Center (SSO) which provides temporary credentials.

### 5. Data Perimeter (Network Guardrails)

Even if a key is stolen, you can stop its use if it comes from the wrong network.
You can deploy an SCP that denies access to APIs unless the request comes from your **Corporate VPN IP range** or your **Managed VPC**.

---

## Summary: The Security Maturity Model

| Level                    | Focus                  | Tools Used                                                       |
| :----------------------- | :--------------------- | :--------------------------------------------------------------- |
| **Level 1 (Basic)**      | Identity Hygiene       | Password Policy, MFA Enforcement, Root User Lockdown             |
| **Level 2 (Visibility)** | Auditing & Cleanup     | Credential Reports, Access Advisor, IAM Access Analyzer (Unused) |
| **Level 3 (Refinement)** | Least Privilege        | Access Analyzer (Policy Generation), CloudTrail logs             |
| **Level 4 (Guardrails)** | Organizational Control | SCPs (Deny-List / Allow-List), Permissions Boundaries            |
