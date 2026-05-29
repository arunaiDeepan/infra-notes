# IAM Policy Structure - The JSON Grammar

> The full anatomy of an IAM policy document: required elements, optional elements, ARN format, condition keys, and how policies attach to identities. Reference companion to [05 - IAM Scenarios](05%20-%20IAM%20Scenarios.md).

See also: [01 - IAM Intro bits & bytes](01%20-%20IAM%20Intro%20bits%20%26%20bytes.md) · [02 - IAM Components](02%20-%20IAM%20Components.md) · [05 - IAM Scenarios](05%20-%20IAM%20Scenarios.md) · [19 - IAM Cross Account Access](19%20-%20IAM%20Cross%20Account%20Access.md)

---

## Table of Contents

- [Part 1: The Complete IAM Policy Structure](#part-1-the-complete-iam-policy-structure)
- [Part 2: The Must-Have Elements (Explained with Examples)](#part-2-the-must-have-elements-explained-with-examples)
- [Part 3: Optional But Powerful Elements](#part-3-optional-but-powerful-elements)
- [Part 4: How Policies Attach to Identities](#part-4-how-policies-attach-to-identities)
- [Part 5: Real-World Complete Examples](#part-5-real-world-complete-examples)
- [Summary: Quick Reference Card](#summary-quick-reference-card)

---

## Part 1: The Complete IAM Policy Structure

### The Skeleton (Minimum Valid Policy)

Every IAM policy must have at least these three elements:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::example-bucket"
    }
  ]
}
```

### The Full Anatomy (All Possible Elements)

```json
{
  "Version": "2012-10-17",           // REQUIRED: Policy language version
  "Id": "CorporateS3PolicyV2",       // OPTIONAL: Your identifier for the policy
  "Statement": [                      // REQUIRED: Array of one or more statements
    {
      "Sid": "AllowReadOnlySpecificBuckets",  // OPTIONAL: Statement ID (for debugging)
      "Effect": "Allow",                      // REQUIRED: "Allow" or "Deny"
      "Principal": {                          // ONLY for Resource-Based Policies (S3, SQS)
        "AWS": "arn:aws:iam::123456789012:root"
      },
      "Action": [                      // REQUIRED: API actions allowed/denied
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "NotAction": [                   // ALTERNATIVE to "Action": Everything EXCEPT these
        "s3:DeleteObject"
      ],
      "Resource": [                    // REQUIRED (for most policies): Which resources
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ],
      "NotResource": [                 // ALTERNATIVE to "Resource": Everything EXCEPT these
        "arn:aws:s3:::secret-bucket/*"
      ],
      "Condition": {                   // OPTIONAL: When does this policy apply?
        "IpAddress": {
          "aws:SourceIp": "203.0.113.0/24"
        },
        "Bool": {
          "aws:MultiFactorAuthPresent": "true"
        }
      }
    }
  ]
}
```

---

## Part 2: The Must-Have Elements (Explained with Examples)

### 1. `Version` (Required)

**What it is:** The policy language version. Always use `"2012-10-17"`. The older `2008-10-17` is deprecated.

**Example:**

```json
"Version": "2012-10-17"
```

### 2. `Statement` (Required)

**What it is:** An array containing at least one permission statement. Most policies have 1-10 statements.

**Example (Single Statement):**

```json
"Statement": [
  {
    "Effect": "Allow",
    "Action": "ec2:DescribeInstances",
    "Resource": "*"
  }
]
```

**Example (Multiple Statements - Allow + Explicit Deny):**

```json
"Statement": [
  {
    "Sid": "AllowS3Read",
    "Effect": "Allow",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::public-bucket/*"
  },
  {
    "Sid": "DenyDeleteImportantData",
    "Effect": "Deny",
    "Action": "s3:DeleteObject",
    "Resource": "arn:aws:s3:::important-bucket/*"
  }
]
```

### 3. `Effect` (Required per Statement)

**What it is:** Either `"Allow"` or `"Deny"`.

**Critical Rule:** An explicit `"Deny"` overrides any `"Allow"` from any other policy. This is your "emergency brake."

### 4. `Action` (Required per Statement, unless using `NotAction`)

**What it is:** The specific AWS API operation(s) being allowed or denied.

**Patterns:**

| Pattern | Meaning | Example |
| :--- | :--- | :--- |
| `service:action` | Single action | `"s3:GetObject"` |
| `service:*` | All actions for a service | `"ec2:*"` |
| `*` | All actions across all services | `"*"` (AdministratorAccess) |
| `service:action*` | Wildcard prefix match | `"s3:Get*"` (GetObject, GetBucketLocation, etc.) |
| `[action1, action2]` | Array of specific actions | `["s3:GetObject", "s3:PutObject"]` |

**Real-World Example: EC2 Read-Only Access**

```json
"Action": [
  "ec2:DescribeInstances",
  "ec2:DescribeImages",
  "ec2:DescribeSecurityGroups",
  "ec2:DescribeSubnets",
  "ec2:DescribeVpcs"
]
```

### 5. `Resource` (Required, unless using `NotResource`)

**What it is:** The AWS resource(s) that the action applies to, identified by an ARN (Amazon Resource Name).

**ARN Format:**

```
arn:aws:service:region:account-id:resource-type/resource-path
```

**Examples of ARNs:**

| Service | Resource | ARN |
| :--- | :--- | :--- |
| S3 Bucket | `my-bucket` | `arn:aws:s3:::my-bucket` |
| S3 Object | `cat.jpg` in `my-bucket` | `arn:aws:s3:::my-bucket/cat.jpg` |
| EC2 Instance | `i-1234567890abcdef0` | `arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0` |
| IAM User | `john` | `arn:aws:iam::123456789012:user/john` |
| Lambda Function | `my-function` | `arn:aws:lambda:us-east-1:123456789012:function:my-function` |

**Wildcards in Resources:**

| Pattern | Meaning | Example |
| :--- | :--- | :--- |
| `*` | All resources | `"Resource": "*"` |
| `/*` | All child resources | `arn:aws:s3:::my-bucket/*` (all objects in bucket) |
| `prefix*` | Resources starting with prefix | `arn:aws:ec2:us-east-1::image/ami-*` (all AMIs) |

**Real-World Example: S3 Bucket with Specific Folder Access**

```json
"Resource": [
  "arn:aws:s3:::company-bucket",           // The bucket itself (for ListBucket)
  "arn:aws:s3:::company-bucket/home/john/*" // Only John's home folder
]
```

---

## Part 3: Optional But Powerful Elements

### `Condition` (The "If" Clause)

**What it does:** Restricts *when* a policy applies based on request context.

**Common Condition Keys:**

| Condition Key | Use Case | Example Value |
| :--- | :--- | :--- |
| `aws:SourceIp` | Restrict to office IP range | `"203.0.113.0/24"` |
| `aws:MultiFactorAuthPresent` | Require MFA | `"true"` |
| `aws:CurrentTime` | Time-based access | `"2025-01-01T00:00:00Z"` |
| `s3:prefix` | S3 folder-level access | `"home/john/"` |
| `ec2:InstanceType` | Restrict EC2 instance types | `"t2.micro"` |

**Example 1: MFA Required for Sensitive Actions**

```json
"Condition": {
  "BoolIfExists": {
    "aws:MultiFactorAuthPresent": "true"
  }
}
```

**Example 2: Only Allow Access from Corporate Office**

```json
"Condition": {
  "IpAddress": {
    "aws:SourceIp": "203.0.113.0/24"
  },
  "NotIpAddress": {
    "aws:SourceIp": "203.0.113.5/32"  // Blacklist a specific IP
  }
}
```

**Example 3: Time-Bound Access (9 AM to 5 PM)**

```json
"Condition": {
  "DateGreaterThan": {
    "aws:CurrentTime": "2025-01-01T09:00:00Z"
  },
  "DateLessThan": {
    "aws:CurrentTime": "2025-01-01T17:00:00Z"
  }
}
```

**Example 4: S3 Folder-Level Access (User can only see their own folder)**

```json
"Condition": {
  "StringLike": {
    "s3:prefix": "${aws:username}/*"
  }
}
```

*This uses a variable `{aws:username}` that AWS replaces with the actual IAM username.*

---

## Part 4: How Policies Attach to Identities

AWS has **three ways** to attach policies to identities. The attachment method determines who/what the policy applies to.

### Method 1: Attach to IAM User (Least Recommended)

**When to use:** Individual service accounts or break-glass emergency users. Avoid for humans.

**How to attach:**

```bash
# AWS CLI
aws iam attach-user-policy \
  --user-name john \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Or inline policy
aws iam put-user-policy \
  --user-name john \
  --policy-name CustomS3Policy \
  --policy-document file://policy.json
```

**Console:** IAM > Users > Select user > Add permissions > Attach existing policies directly

**Effect:** Only `john` gets the permissions.

### Method 2: Attach to IAM Group (Recommended for Humans)

**When to use:** All human users. Add users to groups, attach policies to groups.

**How to attach:**

```bash
# Attach policy to group
aws iam attach-group-policy \
  --group-name Developers \
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

# Add user to group
aws iam add-user-to-group \
  --user-name alice \
  --group-name Developers
```

**Console:** IAM > Groups > Create group > Attach policies > Add users

**Effect:** Every member of the `Developers` group inherits the policy. Add/remove users from group to grant/revoke access.

### Method 3: Attach to IAM Role (For AWS Services or Temporary Access)

**When to use:** EC2 instances, Lambda functions, cross-account access, federated users.

**Step 1: Create Role with Trust Policy**

```json
// trust-policy.json (Who can assume this role)
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"  // Only EC2 can assume this
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

**Step 2: Attach Permissions Policy to Role**

```bash
# Create role with trust policy
aws iam create-role \
  --role-name EC2S3AccessRole \
  --assume-role-policy-document file://trust-policy.json

# Attach permissions policy
aws iam attach-role-policy \
  --role-name EC2S3AccessRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

**Step 3: Use the Role**

- **For EC2:** Create Instance Profile → Launch EC2 with that profile
- **For Lambda:** Select role in Lambda configuration
- **For CLI:** `aws sts assume-role --role-arn arn:aws:iam::123456789012:role/EC2S3AccessRole --role-session-name test`

---

## Part 5: Real-World Complete Examples

### Example 1: Developer Policy (Can manage their own S3 folder and read EC2)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowManageOwnS3Folder",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::company-dev-bucket",
        "arn:aws:s3:::company-dev-bucket/${aws:username}/*"
      ],
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": "203.0.113.0/24"
        }
      }
    },
    {
      "Sid": "AllowReadOnlyEC2",
      "Effect": "Allow",
      "Action": "ec2:Describe*",
      "Resource": "*"
    }
  ]
}
```

**Attachment:** Attach to `Developers` group. Every developer can only write to their own folder (named after their username) in the S3 bucket.

### Example 2: Database Backup Role (For EC2 to run backups)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "rds:CreateDBSnapshot",
        "rds:DeleteDBSnapshot",
        "rds:DescribeDBSnapshots"
      ],
      "Resource": "arn:aws:rds:us-east-1:123456789012:db:production-database"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::db-backup-bucket/production/*"
    },
    {
      "Effect": "Deny",
      "Action": "rds:DeleteDBInstance",
      "Resource": "*"
    }
  ]
}
```

**Attachment:** Create role `DBBackupRole` with trust policy for `ec2.amazonaws.com`. Attach this policy. Launch EC2 with this role.

### Example 3: Cross-Account Read-Only Access

```json
// In Account A (Production, ID: 111111111111)
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::222222222222:root"  // Account B can assume this
      },
      "Action": "sts:AssumeRole"
    }
  ]
}

// Permissions policy attached to same role
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::prod-billing-bucket",
        "arn:aws:s3:::prod-billing-bucket/*"
      ]
    }
  ]
}
```

**Usage from Account B:**

```bash
aws sts assume-role \
  --role-arn arn:aws:iam::111111111111:role/ProdReadOnlyRole \
  --role-session-name AuditSession
```

---

## Summary: Quick Reference Card

| Element | Required? | Purpose |
| :--- | :--- | :--- |
| `Version` | ✅ Yes | Always `"2012-10-17"` |
| `Statement` | ✅ Yes | Container for permissions |
| `Effect` | ✅ Yes | `"Allow"` or `"Deny"` |
| `Action` | ✅ Yes (or `NotAction`) | Which API calls |
| `Resource` | ✅ Yes (or `NotResource`) | Which ARNs |
| `Principal` | ❌ No | Only for resource-based policies (S3, SQS) |
| `Condition` | ❌ No | Restrict by IP, MFA, time, etc. |
| `Sid` | ❌ No | Optional identifier for debugging |
| `Id` | ❌ No | Optional policy-level identifier |

**Attachment Methods:**

- **Group:** Best for humans (manage via group membership)
- **User:** Avoid unless service account
- **Role:** For AWS services, cross-account, temporary access

---
