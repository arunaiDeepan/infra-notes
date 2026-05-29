
# 1. The Core Components: Users, Groups, Roles, Policies

### 👤 IAM User

An **IAM User** is a *permanent identity* representing a **person** or **application** that needs long-term access to AWS.

- **Credentials:** Has long-term credentials (Username/Password for Console, or Access Keys for API/CLI).
- **Scope:** Exists only within a single AWS account.
- **Rule:** One human = One IAM User (no sharing accounts).

### 👥 IAM Group

A **Group** is simply a **container for IAM Users**. It has no identity of its own (you cannot log in as a group).

- **Purpose:** To manage permissions for multiple users at once (e.g., `Developers`, `Managers`, `Auditors`).
- **Constraint:** A Group cannot contain another Group (no nesting groups).

### 📜 IAM Policy

A **Policy** is the document that *defines permissions*. It answers: *"Who can do What on Which resource?"*

- **Types:**
  - **AWS Managed:** Created by AWS (e.g., `AdministratorAccess`, `ReadOnlyAccess`).
  - **Customer Managed:** You create and manage them.
  - **Inline:** A policy embedded directly *inside* a single User or Group (not recommended-hard to audit).

### 🎭 IAM Role

A **Role** is an identity *intended to be assumed* temporarily. It has no long-term credentials (no password, no access key).

- **Who assumes it?** Users, Applications (EC2), AWS Services (Lambda), or even Users from another AWS Account.
- **Use Case:** "Give my EC2 instance permission to write to S3" → You attach a Role to the EC2 instance.

---

## 2. IAM Policy Structure (The JSON Grammar)

Every policy is a JSON document. Here is the **anatomy**:

```json
{
  "Version": "2012-10-17",   // Policy language version (always use this date)
  "Id": "S3ReadOnlyPolicy",  // Optional (friendly name)
  "Statement": [              // Array of individual permissions (can have multiple)
    {
      "Sid": "ListAndRead",   // Optional (sub-ID for the statement)
      "Effect": "Allow",      // OR "Deny" (Deny always overrides Allow)
      "Action": [             // What API calls are allowed?
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [           // Which specific resources?
        "arn:aws:s3:::my-company-bucket/*",  // All objects in this bucket
        "arn:aws:s3:::my-company-bucket"      // The bucket itself
      ],
      "Condition": {          // Optional (when is it allowed?)
        "IpAddress": {
          "aws:SourceIp": "203.0.113.0/24"   // Only from this office IP range
        }
      }
    }
  ]
}
```

### Key Fields Explained

| Field | Meaning |
| :--- | :--- |
| **Effect** | `Allow` or `Deny`. Deny is absolute. |
| **Action** | The AWS API operation (e.g., `ec2:RunInstances`, `s3:DeleteObject`). Use `*` for all actions. |
| **Resource** | The ARN (Amazon Resource Name) of the AWS object. The most specific you can make it, the better. |
| **Condition** | The "if" clause. Examples: IP address, time of day, MFA present, etc. |

### The Override Logic (Explicit Deny)
>
> **Default = `Deny` (implicit).**  
> **If there's an `Allow` policy = `Allow`.**  
> **If there's an *Explicit* `Deny` policy = `Deny` (wins over everything).**

This is why a "Deny" is so powerful. Even if a user has `AdministratorAccess`, an explicit Deny on `s3:DeleteBucket` will stop them.

---

## 3. Inheritance & Evaluation Logic

This is the most misunderstood part. **Groups do NOT nest**. Instead, permissions are *aggregated*.

### How Permissions are Collected

When a user makes an API request, AWS:

1. Collects **all** policies attached directly to the **User**.
2. Collects **all** policies attached to **every Group** the user is a member of.
3. Collects **all** policies attached to the **Role** (if they assumed one).
4. Merges them into a single effective policy.
5. Applies the **Explicit Deny** rule.

### Example

- **User `Alice`** is in **Group `Developers`**.
- `Developers` Group has: `Allow ec2:DescribeInstances`.
- `Alice` User has a direct policy: `Allow ec2:RunInstances`.
- **Result:** Alice can `Describe` (from group) AND `Run` (from direct).

### The "No Inheritance" Trap

You **cannot** do this:

- Group A (contains) Group B (contains) User C.
- AWS does not support nested groups. If you need hierarchy, you must add User C to both Group A AND Group B manually.

---

## 4. Root User vs. IAM User (The Critical Difference)

| Feature | **Root User** | **IAM User** |
| :--- | :--- | :--- |
| **Creation** | Created when you open the AWS account. Email + password. | Created by Root or Admin IAM User. |
| **Permissions** | **Has EVERY permission.** Cannot be restricted. | Has only explicitly granted permissions. |
| **Use Case** | **NEVER use for daily work.** Only for billing, account closure, support. | **ALL daily work.** Developers, apps, admins. |
| **MFA** | Strongly recommended, but not required by default. | Required by best-practice policy. |
| **Access Keys** | Can create them (very dangerous). | Can create them (scoped to their permissions). |
| **Deletion** | Cannot be deleted. Ever. | Can be deleted. |

### What ONLY Root User Can Do

- Change the account name or close the account.
- Change your AWS Support plan.
- View the full bill (some invoice views require Root).
- Register as a seller in the Reserved Instance Marketplace.
- Restore IAM user permissions (if locked out).

> **"Golden Rule of Root":**  
>
> 1. Enable MFA on Root **immediately**.  
> 2. Generate access keys for Root **only if absolutely necessary** (almost never).  
> 3. Store Root credentials in a physical safe or password manager.  
> 4. Never, ever use Root for anything except the above tasks.

---

## 5. User with Admin Permission (The Right Way)

You will often need an IAM User who can do everything *except* the Root-only tasks. This is an **Admin IAM User**.

### The Dangerous (Legacy) Way

Attach the AWS-managed policy `AdministratorAccess` directly to the user.

```json
{
  "Effect": "Allow",
  "Action": "*",
  "Resource": "*"
}
```

✅ Works. ❌ Horrible security practice. No MFA requirement, no IP restriction.

### The Best Practice Way (Admin with Guardrails)

Create a **Customer Managed Policy** that requires MFA for all sensitive actions.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "BoolIfExists": {
          "aws:MultiFactorAuthPresent": "true"
        }
      }
    }
  ]
}
```

**Why this matters:** If an admin's password is stolen, the attacker **also needs the physical MFA device** to do anything. This stops 99% of credential theft attacks.

### Best Practice Checklist for Admin Users

1. **No inline policies** – use managed or group policies.
2. **Require MFA** for the user (enforced by policy).
3. **Require MFA for every API call** (as shown above).
4. **Use a break-glass role** – for emergency, assume a separate admin role rather than having long-term admin on a user.
5. **Rotate access keys** every 90 days if used.

---

## 6. Complete Best Practices Summary

| Practice | Why |
| :--- | :--- |
| **Enable MFA on Root and all IAM Users** | Stops credential theft. |
| **Use Groups, not individual user policies** | Manageability. Add a user to a group, permissions apply automatically. |
| **Grant least privilege** | Start with `ReadOnlyAccess`, then add specific actions. Never start with `AdministratorAccess`. |
| **Use Roles for EC2 / Lambda** | Never hardcode access keys on a server. |
| **Regularly audit with IAM Access Analyzer** | Finds unused permissions and public resources. |
| **Delete unused IAM users and keys** | Reduces attack surface. |
| **Use Conditions (IP, MFA, Time)** | Adds context-aware security. |
| **Never share IAM users** | One human = one IAM user. |

---

## 7. Quick Mini-Quiz to Test Yourself

**Q1:** User `Bob` is in Group `Dev` (allow `s3:GetObject`). A direct policy on `Bob` says `Deny s3:GetObject`. What happens?  
*A:* **Deny** wins. Explicit Deny overrides any Allow.

**Q2:** You need to give 20 developers permission to launch EC2 instances, but only from the office IP. What's the right way?  
*A:* Create one Customer Managed Policy with `ec2:RunInstances` and the `Condition` on `aws:SourceIp`. Attach that policy to a `Developers` Group. Add all 20 users to the Group.

**Q3:** Can Root User be restricted by an IAM policy?  
*A:* **No.** Root bypasses all IAM policies. That's why it's so dangerous.

**Q4:** What happens if a policy is attached to a user AND to a group the user belongs to?  
*A:* They combine (union) of all permissions. Deny still overrides.

---
