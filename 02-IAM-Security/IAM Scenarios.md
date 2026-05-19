# IAM Scenarios — Real-World Practice for AWS SAA-C03

> Practical IAM policy scenarios with JSON examples, line-by-line explanations, CLI testing steps, and common mistakes. See also: [IAM Intro bits & bytes](IAM%20Intro%20bits%20%26%20bytes.md) for the fundamentals.

---

## Table of Contents

### Scenario-Based Policies

- [Scenario 1 — Users Can Only Access Their Own S3 Folder](#scenario-1--users-can-only-access-their-own-s3-folder)
- [Scenario 2 — Developers Can Stop/Start EC2 But Not Delete](#scenario-2--developers-can-stopstart-ec2-but-not-delete)
- [Scenario 3 — MFA Conditions — "No MFA, No Sensitive Actions"](#scenario-3--mfa-conditions--no-mfa-no-sensitive-actions)
- [Scenario 4 — Resource-Based Policies (S3 Bucket Policies vs IAM Policies)](#scenario-4--resource-based-policies-s3-bucket-policies-vs-iam-policies)

### Reference & Cheat Sheets

- [Combining Multiple Policies](#combining-multiple-policies)
- [Testing Checklist](#testing-checklist)
- [IAM Policy Evaluation Logic](#iam-policy-evaluation-logic)
- [Condition Keys Quick Reference](#condition-keys-quick-reference)
- [Hands-On Exercise](#hands-on-exercise)
- [Exam Tips (SAA-C03)](#exam-tips-saa-c03)

---

## Scenario 1 — Users Can Only Access Their Own S3 Folder

### Requirement

You have an S3 bucket named `company-files`. Each developer (IAM user: `alice`, `bob`, `carol`) should only be able to:

- List the contents of their own folder (e.g., `company-files/alice/`)
- Upload, download, and delete files in their own folder

**They must NOT be able to:**

- See other users' folders
- Delete the entire bucket
- Access anything outside their folder

### The Challenge

S3 has two separate permission categories that work differently:

- `s3:ListBucket` — operates at the **bucket level** (resource = bucket ARN)
- `s3:GetObject` / `PutObject` / `DeleteObject` — operate at the **object level** (resource = object ARN)

You need both, but you must restrict `ListBucket` to only show the user's own prefix.

### Solution

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowListingOfOwnFolder",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::company-files",
      "Condition": {
        "StringLike": {
          "s3:prefix": "${aws:username}/*"
        }
      }
    },
    {
      "Sid": "AllowReadWriteDeleteOwnObjects",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::company-files/${aws:username}/*"
    }
  ]
}
```

### Line-by-Line Explanation

**Statement 1 (`s3:ListBucket`):**

- `Action: s3:ListBucket` — API call to list objects in a bucket
- `Resource: arn:aws:s3:::company-files` — the bucket itself (not the objects inside)
- `Condition: StringLike { "s3:prefix": "${aws:username}/*" }` — only list objects whose path starts with the user's username (e.g., `alice/`)

**Statement 2 (Object permissions):**

- `Action: ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]` — read, write, delete
- `Resource: arn:aws:s3:::company-files/${aws:username}/*` — only objects inside their personal folder (`*` matches any file inside)
- `${aws:username}` — a policy variable AWS replaces with the authenticated IAM username

### Result Matrix

| User | Access `company-files/alice/report.pdf`? | Access `company-files/bob/secret.txt`? |
| :--- | :--- | :--- |
| `alice` | ✅ Yes (username matches) | ❌ No (`${aws:username}` resolves to `alice`, path mismatch) |
| `bob`   | ❌ No | ✅ Yes |
| `carol` | ❌ No | ❌ No |

### Testing With AWS CLI

**Test as user `alice`:**

```bash
# Configure CLI as alice
aws configure set profile.alice.aws_access_key_id AKIA...
aws configure set profile.alice.aws_secret_access_key ...

# List own folder — works
aws s3 ls s3://company-files/alice/ --profile alice

# Upload to own folder — works
echo "Hello" > test.txt
aws s3 cp test.txt s3://company-files/alice/test.txt --profile alice

# List bob's folder — fails (Access Denied)
aws s3 ls s3://company-files/bob/ --profile alice

# Upload to bob's folder — fails (Access Denied)
aws s3 cp test.txt s3://company-files/bob/test.txt --profile alice
```

### Common Mistakes & Fixes

| Mistake | Why It's Wrong | Fix |
| :--- | :--- | :--- |
| Using `Resource: arn:aws:s3:::company-files/*` for `ListBucket` | `ListBucket` requires the bucket ARN, not object ARNs | Use bucket ARN + condition on `s3:prefix` |
| Forgetting the trailing `/*` in object ARN | Without `/*` you only target the *folder marker* (which doesn't exist), not files inside | Use `${aws:username}/*` |
| Using `${aws:username}` in a role | Roles have no username — variable resolves to empty string | Use `${aws:userid}` or pass via `sts:RoleSessionName` |

[⬆ Back to top](#table-of-contents)

---

## Scenario 2 — Developers Can Stop/Start EC2 But Not Delete

### Requirement

Developers in the `DevTeam` group need to manage EC2 instances in the `dev` environment, but with safety limits:

- ✅ Start, stop, reboot, describe instances
- ❌ Terminate (delete) instances
- ❌ Create new instances
- ❌ Modify security groups or VPC settings

### Solution

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowDescribeInstances",
      "Effect": "Allow",
      "Action": "ec2:DescribeInstances",
      "Resource": "*"
    },
    {
      "Sid": "AllowStartStopReboot",
      "Effect": "Allow",
      "Action": [
        "ec2:StartInstances",
        "ec2:StopInstances",
        "ec2:RebootInstances"
      ],
      "Resource": "arn:aws:ec2:us-east-1:123456789012:instance/*",
      "Condition": {
        "StringEquals": {
          "ec2:ResourceTag/Environment": "dev"
        }
      }
    },
    {
      "Sid": "ExplicitDenyTerminate",
      "Effect": "Deny",
      "Action": "ec2:TerminateInstances",
      "Resource": "*"
    }
  ]
}
```

### Line-by-Line Explanation

**Statement 1 — Describe:**

- `ec2:DescribeInstances` is a read-only API call. It returns metadata, not a specific resource, so it requires `Resource: "*"`.

**Statement 2 — Start/Stop/Reboot with tag check:**

- `Resource: arn:aws:ec2:us-east-1:123456789012:instance/*` — all EC2 instances in this account/region
- `Condition: StringEquals { "ec2:ResourceTag/Environment": "dev" }` — only allow the action if the instance is tagged `Environment=dev`

**Statement 3 — Explicit Deny on Terminate:**

- Overrides any Allow from other policies. This is your safety net even if someone attaches `EC2FullAccess` later.

### Tag-Based Restriction Behavior

| Instance Tag | Can user stop it? |
| :--- | :--- |
| `Environment=dev` | ✅ Yes |
| `Environment=prod` | ❌ No |
| No `Environment` tag | ❌ No |
| `Environment=staging` | ❌ No |

### Testing With AWS CLI

```bash
# Describe instances — works (shows all)
aws ec2 describe-instances --profile alice

# Stop dev instance — works
aws ec2 stop-instances --instance-ids i-11111 --profile alice

# Stop prod instance — fails (condition mismatch)
aws ec2 stop-instances --instance-ids i-22222 --profile alice

# Terminate any instance — fails (explicit Deny wins)
aws ec2 terminate-instances --instance-ids i-11111 --profile alice
```

### Common Mistakes & Fixes

| Mistake | Why It's Wrong | Fix |
| :--- | :--- | :--- |
| Forgetting `ec2:DescribeInstances` | Users can't see instances in console/CLI, so they can't pick one to stop | Always include describe permissions |
| Using `arn:aws:ec2:*:*:instance/*` | Too broad — applies across all regions | Restrict to specific region |
| Relying only on tags without explicit Deny | Another attached policy with admin rights could bypass tag checks | Add explicit Deny on dangerous actions |
| Allowing `StopInstances` without `StartInstances` | User can stop but never restart (stranded instance) | Pair stop with start |

[⬆ Back to top](#table-of-contents)

---

## Scenario 3 — MFA Conditions — "No MFA, No Sensitive Actions"

### The Problem

A developer's password gets phished. Without MFA enforcement, the attacker has full CLI access. MFA conditions solve this by requiring `aws:MultiFactorAuthPresent` to be `true` for sensitive actions.

### Solution: Tiered Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowReadOnlyWithoutMFA",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "ec2:DescribeInstances",
        "cloudwatch:GetMetricData"
      ],
      "Resource": "*"
    },
    {
      "Sid": "AllowWriteActionsOnlyWithMFA",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:DeleteObject",
        "ec2:StartInstances",
        "ec2:StopInstances",
        "ec2:TerminateInstances",
        "iam:CreateAccessKey"
      ],
      "Resource": "*",
      "Condition": {
        "Bool": {
          "aws:MultiFactorAuthPresent": "true"
        }
      }
    },
    {
      "Sid": "ExplicitDenySensitiveWithoutMFA",
      "Effect": "Deny",
      "Action": [
        "s3:PutObject",
        "ec2:StartInstances",
        "iam:CreateAccessKey"
      ],
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

### The `BoolIfExists` Trap

| Condition | Behavior |
| :--- | :--- |
| `"Bool": { "aws:MultiFactorAuthPresent": "true" }` | ✅ Works only when MFA is present |
| `"Bool": { "aws:MultiFactorAuthPresent": "false" }` | ⚠️ Fails when the key doesn't exist (some API calls don't include it) |
| `"BoolIfExists": { "aws:MultiFactorAuthPresent": "false" }` | ✅ Handles both "missing" and "false" — use this for Deny statements |

> **Critical:** When AWS evaluates an API call made via an IAM Role, `aws:MultiFactorAuthPresent` may not exist at all. `BoolIfExists` gracefully treats missing keys as a match.

### Real-World MFA Policy for Developers

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadOnlyAlways",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket",
        "ec2:Describe*",
        "rds:Describe*",
        "cloudwatch:Get*",
        "logs:Describe*",
        "logs:Get*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "WriteActionsRequireMFA",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:DeleteObject",
        "ec2:StartInstances",
        "ec2:StopInstances",
        "ec2:RebootInstances",
        "lambda:UpdateFunctionCode",
        "lambda:PublishVersion"
      ],
      "Resource": "*",
      "Condition": {
        "Bool": {
          "aws:MultiFactorAuthPresent": "true"
        }
      }
    },
    {
      "Sid": "BlockDangerousActionsWithoutMFA",
      "Effect": "Deny",
      "Action": [
        "iam:CreateAccessKey",
        "iam:DeleteAccessKey",
        "iam:CreateLoginProfile",
        "iam:UpdateLoginProfile",
        "ec2:TerminateInstances"
      ],
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

### Using MFA From the CLI

**Step 1 — Long-term keys give read-only access:**

```bash
aws s3 ls s3://company-bucket/ --profile dev          # works (read)
aws s3 cp file.txt s3://company-bucket/ --profile dev # fails (write requires MFA)
```

**Step 2 — Request an MFA session token:**

```bash
aws sts get-session-token \
  --serial-number arn:aws:iam::123456789012:mfa/alice \
  --token-code 123456 \
  --profile dev
# Returns AccessKeyId / SecretAccessKey / SessionToken (valid up to 36h)
```

**Step 3 — Configure a new profile using the temporary credentials:**

```bash
aws configure set profile.dev-mfa.aws_access_key_id ASIA...
aws configure set profile.dev-mfa.aws_secret_access_key ...
aws configure set profile.dev-mfa.aws_session_token ...

aws s3 cp file.txt s3://company-bucket/ --profile dev-mfa  # works now
```

### Helper Script: `aws-mfa`

```bash
#!/bin/bash
# ~/bin/aws-mfa <token-code>
MFA_DEVICE_ARN="arn:aws:iam::123456789012:mfa/$USER"
TOKEN_CODE=$1
[ -z "$TOKEN_CODE" ] && { echo "Usage: aws-mfa <token-code>"; exit 1; }

STS=$(aws sts get-session-token \
  --serial-number "$MFA_DEVICE_ARN" \
  --token-code "$TOKEN_CODE" \
  --duration-seconds 43200)

export AWS_ACCESS_KEY_ID=$(echo "$STS" | jq -r .Credentials.AccessKeyId)
export AWS_SECRET_ACCESS_KEY=$(echo "$STS" | jq -r .Credentials.SecretAccessKey)
export AWS_SESSION_TOKEN=$(echo "$STS" | jq -r .Credentials.SessionToken)
echo "MFA session active for 12 hours"
```

[⬆ Back to top](#table-of-contents)

---

## Scenario 4 — Resource-Based Policies (S3 Bucket Policies vs IAM Policies)

### The Fundamental Difference

| Aspect | Identity-Based Policy (IAM) | Resource-Based Policy (S3, SQS, SNS, KMS, Lambda) |
| :--- | :--- | :--- |
| **Attached to** | IAM User, Group, Role | AWS resource (S3 bucket, SQS queue, etc.) |
| **Who it grants access to** | The specific identity it's attached to | Any principal — including cross-account |
| **Requires `Principal`** | No (implied from identity) | Yes (explicit) |
| **Cross-account access** | Needs role + trust policy | Direct (no role needed) |
| **Size limit** | 6,144 chars (managed) / 2,048 (inline) | 20 KB for S3 bucket policy |

### Example: S3 Bucket Policy (Cross-Account Read)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCrossAccountRead",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::222222222222:root"
      },
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::shared-bucket",
        "arn:aws:s3:::shared-bucket/*"
      ]
    },
    {
      "Sid": "DenyDeleteFromEveryone",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:DeleteObject",
      "Resource": "arn:aws:s3:::shared-bucket/*"
    }
  ]
}
```

### How IAM + Resource Policies Combine

When a request hits S3, AWS evaluates **both** the IAM policy on the caller's identity and the bucket policy:

```
User has IAM Policy: Allow s3:GetObject on shared-bucket/*
Bucket Policy:      Allow s3:GetObject from Principal = Account B
RESULT: ✅ Access granted (both Allow)

User has IAM Policy: DENY s3:GetObject
Bucket Policy:      Allow
RESULT: ❌ Denied (any Deny wins)

User has IAM Policy: Allow
Bucket Policy:      Deny
RESULT: ❌ Denied (Deny wins)
```

> Same-account access requires **either** an Allow in IAM **or** in the resource policy. Cross-account access requires **both** — the trusting account grants via resource policy, and the trusted account's IAM admin grants the user IAM permission.

### Public Read-Only Bucket (Static Website)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-static-website/*"
    },
    {
      "Sid": "DenyWriteFromAnonymous",
      "Effect": "Deny",
      "Principal": "*",
      "Action": [
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::my-static-website/*"
    }
  ]
}
```

> 💡 **S3 Block Public Access** settings can still override this. If public access is intentional, disable BPA for the bucket.

### When to Use Which?

| Use Case | Best Approach |
| :--- | :--- |
| Internal corporate app (users in your AWS account) | IAM policies attached to user groups |
| Public website assets (CSS, JS, images) | S3 bucket policy with `Principal: "*"` |
| Cross-account access (Account A reads Account B's S3) | S3 bucket policy (no role needed) |
| Cross-account access to EC2 | IAM role with trust policy (EC2 has no resource policy) |
| Complex conditions (IP, MFA, time) | IAM policy (supports more condition keys) |
| Restrict access to a specific VPC endpoint | S3 bucket policy with `aws:SourceVpce` |

### Defense in Depth — VPC + MFA Required

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "RequireVPCAndMFA",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::sensitive-bucket",
        "arn:aws:s3:::sensitive-bucket/*"
      ],
      "Condition": {
        "StringNotEquals": {
          "aws:SourceVpc": "vpc-12345678"
        },
        "BoolIfExists": {
          "aws:MultiFactorAuthPresent": "false"
        }
      }
    }
  ]
}
```

Even an `AdministratorAccess` IAM policy can't bypass this bucket-level Deny.

[⬆ Back to top](#table-of-contents)

---

## Combining Multiple Policies

You can attach multiple policies to a user/group. AWS merges them when evaluating each request.

```bash
# Create both policies
aws iam create-policy \
  --policy-name S3UserFolderAccess \
  --policy-document file://s3-folder-policy.json

aws iam create-policy \
  --policy-name EC2DevStopStart \
  --policy-document file://ec2-stop-start-policy.json

# Attach both to the Developers group
aws iam attach-group-policy \
  --group-name Developers \
  --policy-arn arn:aws:iam::123456789012:policy/S3UserFolderAccess

aws iam attach-group-policy \
  --group-name Developers \
  --policy-arn arn:aws:iam::123456789012:policy/EC2DevStopStart
```

Effective permissions for a user in `Developers`:

- S3: own-folder access (restricted by `${aws:username}`)
- EC2: start/stop on instances tagged `Environment=dev`
- Independent — they govern different services, so no conflicts

[⬆ Back to top](#table-of-contents)

---

## Testing Checklist

Before deploying any policy to production:

1. **Dry-run (EC2):**

   ```bash
   aws ec2 stop-instances --instance-ids i-11111 --dry-run --profile test-user
   # "Request would have succeeded" or permission error
   ```

2. **Force unbuffered errors:**

   ```bash
   aws s3 ls s3://company-files/bob/ --no-cli-pager --profile alice
   ```

3. **IAM Policy Simulator** (Console → IAM → Policy Simulator):
   - Select the user/group/role
   - Choose the action (e.g., `s3:PutObject`)
   - Enter the resource ARN and any condition context (MFA, source IP)
   - Reads "allowed" or "implicit/explicit deny"

4. **CloudTrail for failed attempts:**

   ```bash
   aws cloudtrail lookup-events \
     --lookup-attributes AttributeKey=Username,AttributeValue=alice \
     --output table
   ```

5. **IAM Access Analyzer** — surfaces resources that grant access to external principals (public/anonymous, cross-account).

[⬆ Back to top](#table-of-contents)

---

## IAM Policy Evaluation Logic

The official AWS evaluation order for a single account (simplified):

```
1.  Default: implicit DENY
2.  Apply Service Control Policies (SCPs) at the Org level  ──► any Deny ends here
3.  Apply Resource-based policies                            ──► Allow can grant cross-account
4.  Apply Identity-based policies (IAM user/group/role)
5.  Apply Permissions Boundaries (max permissions ceiling)
6.  Apply Session policies (if AssumeRole with --policy)
7.  Apply explicit Deny from any of the above                ──► always wins
8.  If no explicit Deny and at least one Allow ──► ALLOW
    Otherwise ──► DENY
```

### Mental Model

```
        ┌────────────────────────┐
        │ Explicit Deny anywhere │ ──► DENY (final)
        └────────────────────────┘
                  │ none
                  ▼
        ┌────────────────────────┐
        │  Any Allow that also   │
        │  fits Boundaries/SCPs  │ ──► ALLOW
        └────────────────────────┘
                  │ none
                  ▼
              implicit DENY
```

### Permissions Boundary vs SCP vs IAM Policy

| Layer | Scope | Grants permissions? | Caps permissions? |
| :--- | :--- | :--- | :--- |
| **SCP** (AWS Organizations) | Whole account / OU | ❌ No | ✅ Yes — max for everyone in account, including root |
| **Permissions Boundary** | A single IAM user/role | ❌ No | ✅ Yes — max for that identity |
| **Identity policy** | User / group / role | ✅ Yes | ❌ No |
| **Resource policy** | The resource | ✅ Yes (to anyone, incl. cross-account) | ❌ No |
| **Session policy** | One STS session | ✅ Filters inherited permissions | ✅ Yes |

> **Exam pattern:** "Even though the IAM user has `AdministratorAccess`, they can't perform action X. Why?" — usually an SCP, a permissions boundary, an explicit Deny, or a resource-policy Deny.

[⬆ Back to top](#table-of-contents)

---

## Condition Keys Quick Reference

### Global Condition Keys (work for every service)

| Key | Type | Example Use |
| :--- | :--- | :--- |
| `aws:MultiFactorAuthPresent` | Bool | Require MFA for write/delete actions |
| `aws:MultiFactorAuthAge` | Numeric | Allow only if MFA was used in last N seconds |
| `aws:SourceIp` | IP | Restrict to a corporate CIDR (`203.0.113.0/24`) |
| `aws:SourceVpc` / `aws:SourceVpce` | String | Force traffic via a VPC endpoint |
| `aws:CurrentTime` | Date | Limit access to office hours / a date range |
| `aws:RequestedRegion` | String | Lock policy to specific regions |
| `aws:PrincipalOrgID` | String | Allow only principals in your Organization |
| `aws:SecureTransport` | Bool | Force HTTPS (deny plain HTTP) |
| `aws:username` / `aws:userid` | Variable | Substitute in `Resource` or `Condition` |

### Service-Specific Keys (high-yield ones)

| Service | Key | Example |
| :--- | :--- | :--- |
| S3 | `s3:prefix` | Limit `ListBucket` to a folder |
| S3 | `s3:x-amz-server-side-encryption` | Force SSE on uploads |
| S3 | `s3:x-amz-acl` | Block public ACLs |
| EC2 | `ec2:ResourceTag/<key>` | Restrict to tagged resources |
| EC2 | `ec2:InstanceType` | Restrict allowed instance sizes |
| IAM | `iam:PassedToService` | Limit which services a role can be passed to |
| KMS | `kms:ViaService` | Allow KMS use only through specific services |

### Condition Operators Cheat-Sheet

| Operator family | Use for | Examples |
| :--- | :--- | :--- |
| `String*` | Most string comparisons | `StringEquals`, `StringLike`, `StringNotEquals` |
| `Numeric*` | Numbers | `NumericLessThan`, `NumericGreaterThanEquals` |
| `Date*` | Times | `DateGreaterThan`, `DateLessThan` |
| `Bool` | True/false | MFA present |
| `IpAddress` / `NotIpAddress` | CIDR matching | `aws:SourceIp` |
| `ArnEquals` / `ArnLike` | Compare ARNs | Cross-account principal matching |
| `Null` | Key present or not | Detect missing keys |
| Suffix `IfExists` | Treat missing key as match | `BoolIfExists`, `StringEqualsIfExists` |
| Suffix `ForAllValues` / `ForAnyValue` | Multi-value sets (e.g., tag sets) | Tag-based access control |

[⬆ Back to top](#table-of-contents)

---

## Hands-On Exercise

**Task:** Write a policy that allows `s3:PutObject` only when:

1. The user has authenticated with MFA, AND
2. The request comes during an explicit time window

**Hint:** Use `aws:MultiFactorAuthPresent`, `aws:CurrentTime`, `DateGreaterThan`, `DateLessThan`.

**Reference solution:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::your-bucket/*",
      "Condition": {
        "Bool": {
          "aws:MultiFactorAuthPresent": "true"
        },
        "DateGreaterThan": {
          "aws:CurrentTime": "2026-01-01T09:00:00Z"
        },
        "DateLessThan": {
          "aws:CurrentTime": "2026-12-31T17:00:00Z"
        }
      }
    }
  ]
}
```

> A recurring office-hours window (e.g. "9–5 every weekday") can't be expressed cleanly in a single IAM policy — production setups usually use IAM Identity Center permission sets with time-bound sessions, or a Lambda+EventBridge job that toggles policy attachment.

[⬆ Back to top](#table-of-contents)

---

## Exam Tips (SAA-C03)

High-yield IAM patterns the exam loves to test:

1. **EC2 should access S3 → use an IAM Role on the instance.** Never hardcode access keys.
2. **Cross-account: which side does what?**
   - Trusting account (the one with the resource): publishes a trust/resource policy naming the other account.
   - Trusted account (the caller): grants the user/role IAM permission to `sts:AssumeRole`.
3. **Federation patterns:**
   - External corporate users → **IAM Identity Center** (formerly SSO) or **SAML 2.0 federation**.
   - Mobile/web app users → **Amazon Cognito** (user pools + identity pools).
   - Existing on-prem AD → **AWS Directory Service / AD Connector** or SAML.
4. **Permissions Boundary vs SCP:**
   - Boundary = caps a single user/role.
   - SCP = caps an entire account/OU (and even root in that account).
5. **Explicit Deny always wins.** Period. Used as the safety mechanism in every well-designed policy.
6. **Resource policies grant cross-account access without a role** — for services that support them: S3, SQS, SNS, Lambda, KMS, ECR, Secrets Manager. EC2, RDS, DynamoDB do **not** have resource-based policies — you must use roles for them.
7. **`iam:PassRole`** is required to attach a role to a service (e.g., launch EC2 with a role). Common gotcha — users can launch EC2 but can't attach the role.
8. **`MFAAge` vs `MFAPresent`:** if the question says "MFA in last 30 minutes," it's `aws:MultiFactorAuthAge`.
9. **STS session length:** `GetSessionToken` ≤ 36h for IAM users; `AssumeRole` ≤ 12h (and ≤ role's `MaxSessionDuration`).
10. **`aws:SourceIp` does NOT match traffic from VPC endpoints** — use `aws:SourceVpc` / `aws:SourceVpce` instead.
11. **S3 Block Public Access overrides bucket policies.** If a "public" bucket policy isn't working in a question, suspect BPA.
12. **IAM is global, not regional.** Users, groups, roles, policies have no region. (The resources you control with them may be regional.)

[⬆ Back to top](#table-of-contents)
