# IAM Access - Authentication, Roles & Developer Tools

> Having understood **who** (Users/Roles) and **what** (Policies), this file covers **how we secure the keys to the kingdom**, **how services get their permissions**, and **how you (and your code) actually talk to AWS**.

See also: [01 - IAM Intro bits & bytes](01%20-%20IAM%20Intro%20bits%20%26%20bytes.md) · [02 - IAM Components](02%20-%20IAM%20Components.md) · [03 - IAM Policy Structure](03%20-%20IAM%20Policy%20Structure.md) · [13 - STS & Federation](13%20-%20STS%20%26%20Federation.md) · [06 - IAM Identity Center & Organizations](06%20-%20IAM%20Identity%20Center%20%26%20Organizations.md)

---

## Table of Contents

- [Part 1: IAM Password Policy & MFA (Securing the User)](#part-1-iam-password-policy--mfa-securing-the-user)
- [Part 2: IAM Roles for Services (The "Doers")](#part-2-iam-roles-for-services-the-doers)
- [Part 3: The Developer's Toolbox (CLI, SDK, CloudShell)](#part-3-the-developers-toolbox-cli-sdk-cloudshell)
- [Summary: The "Golden Path" of AWS Access](#summary-the-golden-path-of-aws-access)

---

## Overview

This file covers the three interconnected pillars:

1. **Authentication (Are you who you say you are?):** Password Policies & MFA.
2. **Authorization for Machines (What can a service do?):** IAM Roles for AWS Services.
3. **The Developer's Interface (How do you give commands?):** AWS CLI, SDK (Python), & CloudShell.

---

## Part 1: IAM Password Policy & MFA (Securing the User)

Before we give anyone a password, we must enforce *how* passwords are created and add a second layer of defense.

### 🔐 IAM Password Policy

The **Account Password Policy** is a set of rules applied to *all* IAM users in your AWS account that use a password to log into the console.

**Key Settings (Best Practices):**

- **Minimum Password Length:** AWS allows 1-128 characters. **Best practice is 14 or more**.
- **Character Types:** Require at least one each of uppercase, lowercase, number, and non-alphanumeric symbol (`!@#$%^&*`).
- **Password Reuse Prevention:** AWS remembers your previous passwords. CIS benchmark recommends preventing reuse of the **last 24 passwords**.
- **Maximum Password Age:** Force users to rotate passwords. **90 days** is standard.
- **Allow Users to Change Password:** Always "Yes." (You don't want to be the password manager for 500 developers).

**Why it matters:**

- **Brute Force Protection:** Length stops automated bots.
- **Compliance:** Satisfies CIS AWS Foundations Benchmark controls (IAM.15, IAM.16).
- **Automation:** You can enforce this across 100s of accounts using **CloudFormation StackSets** (which deploy a Lambda to call the `update-account-password-policy` API).

### 📱 Multi-Factor Authentication (MFA)

MFA requires a user to present a physical or virtual device token *plus* their password. **Root users must have MFA. Admins must have MFA. All users must have MFA.**

**Supported Device Types:**

1. **FIDO2 Security Keys (Hardware):** The gold standard. YubiKey, Feitian. USB or NFC. Phishing-resistant because the key verifies the website's URL.
    - *Built-in authenticators:* TouchID (Mac), Windows Hello (fingerprint/camera).
2. **Virtual Authenticator Apps (TOTP):** Google Authenticator, Authy, Microsoft Authenticator. Generates a 6-digit code that expires every 30 seconds (RFC 6238).
3. **SMS Text Message:** **Deprecated for new accounts.** Least secure (SIM swapping).

**Best Practice:**

- **Root User:** Enable MFA immediately. Store the physical key or backup codes in a safe.
- **IAM Users:** Force them to enroll via policy.
    *Policy Check:* If `aws:MultiFactorAuthPresent` is "false," deny the `Allow` action. This forces the user to log into the "MFA prompt" screen before running CLI commands.

---

## Part 2: IAM Roles for Services (The "Doers")

While Users are people, **Roles** are identities for **AWS services** (EC2, Lambda, etc.) or **temporary access**. Roles provide *temporary* credentials. You never embed a password or key in code.

### How a Role Works (The "AssumeRole" Flow)

1. You create a Role and attach a Policy (e.g., "Read S3").
2. You tell AWS who is *trusted* to *assume* this role (The Trust Policy).
3. The AWS service (e.g., EC2) calls `sts:AssumeRole`.
4. AWS returns temporary Access Keys (valid for 1 hour max).
5. The service uses those keys to act.

### Common Roles & Use Cases

| Role / Service | Use Case | Trust Policy Principal |
| :--- | :--- | :--- |
| **EC2 Instance Role** | A web server on EC2 needs to read/write files to S3. You assign an **Instance Profile** (container for a role) to the EC2 instance. | `ec2.amazonaws.com` |
| **Lambda Execution Role** | Your Python Lambda function needs to write logs to CloudWatch and query DynamoDB. | `lambda.amazonaws.com` |
| **Cross-Account Role** | You have an account `Prod` and `Dev`. A user in `Dev` needs to check a log in `Prod`. You create a role in `Prod` trusting the `Dev` account. | `AWS: arn:aws:iam::DEV-ACCOUNT-ID:root` |
| **IAM Roles Anywhere** | An on-premises server (outside AWS) needs to access an AWS S3 bucket. It gets a certificate, calls IAM Roles Anywhere, and gets temporary AWS keys. | `Service: rolesanywhere.amazonaws.com` |
| **Federated User Access** | Your employee logs into Okta/Google. Okta assumes an IAM Role mapped to their group. No IAM user created. | `Federated: saml-provider` |

### The Trust Policy (The "Secret Sauce")

A Role is useless without a Trust Policy. It defines *who* can take this role.

```json
{
  "Effect": "Allow",
  "Principal": { "Service": "ec2.amazonaws.com" },  // ONLY EC2 can take this
  "Action": "sts:AssumeRole"
}
```

- **Principal:** The entity (User, Account, or Service) allowed to assume the role.
- **Action:** Almost always `sts:AssumeRole`.

**Best Practice:** Never hardcode keys in an app. If your app runs on EC2, **use an Instance Role**. AWS automatically rotates the credentials for you.

---

## Part 3: The Developer's Toolbox (CLI, SDK, CloudShell)

Now we need tools to actually *use* these permissions.

### 🖥️ AWS Command Line Interface (CLI)

The CLI allows you to type commands (`aws s3 ls`, `ec2 describe-instances`) to control AWS.

**Credentials Priority (Highest to Lowest):**

1. **Command line options** (`--profile` flag).
2. **Environment variables** (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`).
3. **CLI Named Profiles** (`~/.aws/credentials`).
4. **IAM Roles** (if on EC2).
5. **ECS container credentials**.

**Managing Access Keys (The Danger Zone):**

- **The Problem:** Long-term Access Keys (created via `CreateAccessKey` in Python or Console) are static secrets. If leaked, an attacker has access until you delete the key.
- **The CLI Command:** `aws configure --profile dev-user` (This saves keys to your hard drive).
- **The Risk:** Developers accidentally committing keys to GitHub.

**Best Practices for CLI:**

1. **Do not use Root Access Keys.** Delete them if they exist.
2. **Use Named Profiles:** `--profile prod` vs `--profile dev`. Prevents you from running `aws s3 rm --recursive s3://production-bucket` by accident.
3. **Use `aws sts get-session-token` (with MFA):** Instead of using long-term keys, request a short-term token.
4. **Rotate keys:** Delete unused keys. Rotate used keys every 90 days (`aws iam update-access-key`).
5. **Audit:** `aws iam list-access-keys --user-name Bob` to see who has keys.

### 🐍 AWS SDK for Python (Boto3)

Boto3 is the AWS SDK for Python. You import it to interact with AWS services from code.

**Basic Pattern:**

```python
import boto3

# 1. Create a client (usually uses the same priority chain as CLI)
ec2 = boto3.client('ec2', region_name='us-east-1')

# 2. Call an API
response = ec2.describe_instances()

# 3. Process response
for reservation in response['Reservations']:
    for instance in reservation['Instances']:
        print(instance['InstanceId'])
```

**Common IAM Actions in Boto3:**

- **Create User/Key:** `iam.create_user(UserName='...')`
- **Attach Policy:** `iam.attach_user_policy(UserName='...', PolicyArn='...')`
- **Create Role:** `iam.create_role(RoleName='...', AssumeRolePolicyDocument='...')`
- **Instance Profile:** You must create a role, then create an instance profile, then add the role to the profile to attach to EC2.

**Best Practice for SDK:**

- **Never commit keys to code.** Use IAM Roles (if on AWS) or IAM Roles Anywhere (if on-prem).
- **Use Paginators:** If you request 1000 items, Boto3 only returns 100 by default (if not using paginator). Use `get_paginator()` to loop through all results.

### ☁️ AWS CloudShell

CloudShell is a **browser-based, pre-authenticated terminal** available directly in the AWS Console.

**Why use it?**

- **Zero Config:** You don't install the CLI or configure access keys. It automatically inherits the permissions of the IAM user logged into the Console.
- **Pre-installed Tools:** Comes with AWS CLI, Python (Boto3 ready), Git, Node.js, and common utilities.
- **Persistence:** You get **1 GB of persistent storage** per region (files saved in `~/` stay there). The compute (1 vCPU + 2 GiB RAM) is ephemeral.
- **File Transfer:** You can upload/download files directly from the UI.

**Limitations:**

- **Not everywhere:** Only available in specific regions (e.g., `us-east-1`, `eu-west-1`, `ap-southeast-1`). Check the Region Table.
- **Not for heavy compute:** Don't try to compile a kernel or run a ML model. It's for DevOps tasks.
- **Timeout:** Idle sessions eventually close (though `tmux` attempts to restore them).

**Use Cases:**

- **Quick CLI tests:** "Does this policy work?" `aws s3 ls`.
- **Python prototyping:** Write a quick `boto3` script to check if a bucket is public.
- **Incident Response:** Need to run a CLI command but your local machine is blocked by corporate VPN? Use CloudShell.
- **Learning:** Great for following along with AWS tutorials without installing anything.

---

## Summary: The "Golden Path" of AWS Access

1. **If you are a Human (Admin/Dev):**
    - **Console:** Use IAM Identity Center (SSO) + MFA. Avoid IAM users if possible.
    - **CLI:** Use `aws sso login` (short-term tokens) OR `aws sts get-session-token`. Avoid long-term Access Keys.
    - **Quick Tasks:** Use **CloudShell** in the browser.

2. **If you are a Workload (EC2/Lambda):**
    - **NEVER** use Access Keys.
    - **ALWAYS** use **IAM Roles** attached to the service.

3. **If you are a 3rd Party / On-Prem Server:**
    - **NEVER** use Access Keys.
    - Use **IAM Roles Anywhere** or **STS** to get temporary tokens.
