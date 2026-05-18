## Real world scenario based qns

- [Users can only access their own folder in S3](#policy-1-users-can-only-access-their-own-folder-in-s3)
- Developers can stop/start EC2 but not delete it?
- Allow EC2 start/stop only if user authenticated with MFA
- [Resource-based policies](#resource-based-policies-s3-bucket-policy-vs-iam-policy-how-it-works)

---

## 1: Users Can Only Access Their Own Folder in S3

### The Requirement

You have an S3 bucket named `company-files`. Each developer (IAM user: `alice`, `bob`, `carol`) should only be able to:
- List the contents of their own folder (e.g., `company-files/alice/`)
- Upload files to their own folder
- Download files from their own folder
- Delete files in their own folder

**They must NOT be able to:**
- See other users' folders
- Delete the entire bucket
- Access anything outside their folder

### The Challenge

S3 has two separate permissions that work differently:
- `s3:ListBucket` = List objects in a bucket (works at the **bucket level**)
- `s3:GetObject` / `PutObject` / `DeleteObject` = Act on objects (work at the **object level**)

The tricky part: `s3:ListBucket` applies to the bucket ARN, while object permissions apply to object ARNs. You need both, but you must restrict `ListBucket` to only show the user's own prefix.

### The Solution (Two Statements)

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
- `Action: s3:ListBucket` – The API call that lists objects in a bucket
- `Resource: arn:aws:s3:::company-files` – The bucket itself (not the objects inside)
- `Condition: StringLike { "s3:prefix": "${aws:username}/*" }` – Only list objects where the path starts with the user's username (e.g., `alice/`)

**Statement 2 (Object permissions):**
- `Action: ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]` – Read, write, delete
- `Resource: arn:aws:s3:::company-files/${aws:username}/*` – Only objects inside their personal folder (the `*` means any file inside)
- `{aws:username}` – A special variable that AWS automatically replaces with the IAM username of the authenticated user

### What Happens When Each User Tries to Access

| User | Can access `company-files/alice/report.pdf`? | Can access `company-files/bob/secret.txt`? |
| :--- | :--- | :--- |
| `alice` | ✅ Yes (username matches) | ❌ No (resource path uses `bob/*`, but `{aws:username}` = `alice`) |
| `bob` | ❌ No | ✅ Yes |
| `carol` | ❌ No | ❌ No |

### Testing This Policy (Using AWS CLI)

**Prerequisites:** Create IAM users `alice`, `bob`, and attach this policy to them (or to a group they're in).

**Test as user `alice`:**
```bash
# Configure CLI as alice (or use --profile alice)
aws configure set profile.alice.aws_access_key_id AKIA...
aws configure set profile.alice.aws_secret_access_key ...

# Try to list her own folder (works)
aws s3 ls s3://company-files/alice/ --profile alice

# Try to upload a file to her folder (works)
echo "Hello" > test.txt
aws s3 cp test.txt s3://company-files/alice/test.txt --profile alice

# Try to list bob's folder (fails - permission denied)
aws s3 ls s3://company-files/bob/ --profile alice
# ERROR: Access Denied

# Try to upload to bob's folder (fails)
aws s3 cp test.txt s3://company-files/bob/test.txt --profile alice
# ERROR: Access Denied
```

### Common Mistakes & Fixes

| Mistake | Why It's Wrong | Fix |
| :--- | :--- | :--- |
| Using `Resource: arn:aws:s3:::company-files/*` for `ListBucket` | `ListBucket` doesn't work with object-level ARNs. It needs the bucket ARN only. | Use bucket ARN + condition on `s3:prefix` |
| Forgetting the trailing `/*` in object ARN | Without `/*`, you can only act on the *folder itself* (which doesn't exist as an object), not files inside. | Use `${aws:username}/*` |
| Using `{aws:username}` in a role (not a user) | Roles don't have a username variable. It becomes empty string. | Use a different variable like `{aws:userid}` or pass via `sts:RoleSessionName` |

---

## 2: Developers Can Stop/Start EC2 But Not Delete

### The Requirement

Developers in the `DevTeam` group need to manage EC2 instances in the `dev` environment, but with safety limits:
- ✅ Can start instances
- ✅ Can stop instances
- ✅ Can reboot instances
- ✅ Can describe instances (list them)
- ❌ Cannot terminate (delete) instances
- ❌ Cannot create new instances
- ❌ Cannot modify security groups or VPC settings

### The Solution

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

**Statement 1 (Describe):**
- `Action: ec2:DescribeInstances` – The read-only API call to list instances
- `Resource: "*"` – Describe actions usually require wildcard because they don't act on a specific resource

**Statement 2 (Start/Stop/Reboot with tag check):**
- `Action: ["ec2:StartInstances", "ec2:StopInstances", "ec2:RebootInstances"]` – The management actions
- `Resource: arn:aws:ec2:us-east-1:123456789012:instance/*` – Applies to all EC2 instances in this account/region
- `Condition: StringEquals { "ec2:ResourceTag/Environment": "dev" }` – **Critical safety check:** Only allow these actions if the instance has a tag `Environment=dev`

**Statement 3 (Explicit Deny on Terminate):**
- `Action: ec2:TerminateInstances` – The dangerous action
- `Effect: "Deny"` – Explicit deny (overrides any Allow elsewhere)
- `Resource: "*"` – All instances, regardless of tags

### Why the Explicit Deny on Terminate?

Even if a developer somehow gets `TerminateInstances` permission from another policy (e.g., someone accidentally attaches `EC2FullAccess`), this explicit deny will **block it**. This is your safety net.

### The Tag-Based Restriction Explained

In Statement 2, the condition `ec2:ResourceTag/Environment = "dev"` means:

| Instance Tag | Can user stop it? |
| :--- | :--- |
| `Environment=dev` | ✅ Yes |
| `Environment=prod` | ❌ No |
| No Environment tag | ❌ No |
| `Environment=staging` | ❌ No |

This protects your production instances from accidental stops by developers.

### Testing This Policy

**Prerequisites:**
- Create two EC2 instances:
  - `i-11111` with tag `Environment=dev`
  - `i-22222` with tag `Environment=prod`
- Attach the policy to the `DevTeam` group
- Add user `alice` to `DevTeam`

**Test as `alice`:**
```bash
# Describe instances (works - shows all)
aws ec2 describe-instances --profile alice

# Try to stop the dev instance (works)
aws ec2 stop-instances --instance-ids i-11111 --profile alice

# Try to stop the prod instance (fails - permission denied by condition)
aws ec2 stop-instances --instance-ids i-22222 --profile alice
# ERROR: Not authorized to perform ec2:StopInstances on resource i-22222

# Try to terminate any instance (fails - explicit deny)
aws ec2 terminate-instances --instance-ids i-11111 --profile alice
# ERROR: Not authorized (Deny overrides any Allow)
```

### Common Mistakes & Fixes

| Mistake                                                   | Why It's Wrong                                                                | Fix                                      |
| :-------------------------------------------------------- | :---------------------------------------------------------------------------- | :--------------------------------------- |
| Forgetting `ec2:DescribeInstances`                        | Users can't see instances in console/CLI, so they can't select which to stop. | Always include describe permissions.     |
| Using `Resource: "arn:aws:ec2:*:*:instance/*"`            | Too broad across regions.                                                     | Restrict to specific region if possible. |
| Relying only on tags without explicit deny                | A user with Admin-like permissions could bypass tag checks.                   | Add explicit deny on dangerous actions.  |
| Allowing `ec2:StopInstances` without `ec2:StartInstances` | User can stop an instance but never restart it (stranded).                    | Pair stop with start permissions.        |

---

## Combining(1 & 2) Both Policies (Advanced)

You can attach **multiple policies** to a user/group. For example, a developer might need both S3 folder access AND EC2 management. AWS merges all attached policies.

**Attach both policies:**
```bash
# Create policy documents (save as s3-folder-policy.json and ec2-stop-start-policy.json)

# Create policies
aws iam create-policy \
  --policy-name S3UserFolderAccess \
  --policy-document file://s3-folder-policy.json

aws iam create-policy \
  --policy-name EC2DevStopStart \
  --policy-document file://ec2-stop-start-policy.json

# Attach both to a group
aws iam attach-group-policy \
  --group-name Developers \
  --policy-arn arn:aws:iam::123456789012:policy/S3UserFolderAccess

aws iam attach-group-policy \
  --group-name Developers \
  --policy-arn arn:aws:iam::123456789012:policy/EC2DevStopStart
```

**Effective permissions for a user in `Developers` group:**
- From S3 policy: Own folder access (restricted by username)
- From EC2 policy: Can stop/start dev-tagged instances
- No conflict between them (they control different services)

---

## Quick Reference(1 & 2): Testing Checklist

Before deploying a policy to production:

1. **Test with `--dry-run` (EC2 only):**
   ```bash
   aws ec2 stop-instances --instance-ids i-11111 --dry-run --profile test-user
   # Returns "Request would have succeeded" or permission error
   ```

2. **Use `--no-cli-pager` to see raw errors:**
   ```bash
   aws s3 ls s3://company-files/bob/ --no-cli-pager --profile alice
   ```

3. **Simulate policy with IAM Policy Simulator** (AWS Console > IAM > Policy Simulator):
   - Select user/group
   - Choose action (e.g., `s3:PutObject`)
   - Enter resource ARN
   - See if policy allows or denies

4. **Check CloudTrail for failed attempts:**
   ```bash
   aws cloudtrail lookup-events \
     --lookup-attributes AttributeKey=Username,AttributeValue=alice \
     --output table
   ```

---

Excellent. Let's tackle two advanced topics that separate beginner IAM knowledge from **real-world security expertise**:

1. **MFA Conditions** (forcing users to use MFA for sensitive actions)
2. **Resource-Based Policies** (S3 bucket policies vs IAM policies, and why the distinction matters)

---

## 3: MFA Conditions - "No MFA, No Sensitive Actions"

### The Problem

A developer's password gets phished. The attacker now has full CLI access with the developer's permissions. **Without MFA enforcement, the attacker wins.**

MFA conditions solve this by requiring the `aws:MultiFactorAuthPresent` condition key to be `true` for sensitive actions.

### The Solution: Break Actions into Two Tiers

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

### Why Three Statements? The "BoolIfExists" Trap

| Condition | What it means | Problem |
| :--- | :--- | :--- |
| `"Bool": { "aws:MultiFactorAuthPresent": "true" }` | Only allow if MFA is present | ✅ Works for MFA users |
| `"Bool": { "aws:MultiFactorAuthPresent": "false" }` | Only allow if MFA is NOT present | ⚠️ Fails for API calls where the key doesn't exist |
| `"BoolIfExists": { "aws:MultiFactorAuthPresent": "false" }` | Allow if key is missing OR set to false | ✅ Handles both cases |

**The Critical Insight:** When you call AWS via an IAM Role (not a user with MFA), the `aws:MultiFactorAuthPresent` key **doesn't exist at all**, not even as `false`. Using `Bool` without `IfExists` will cause the condition to fail (treat missing as false, but strict evaluation can break). `BoolIfExists` handles missing keys gracefully.

### Real-World MFA Policy for Developers

Here's a policy you can actually deploy to a `Developers` group:

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

### How Developers Use This (The MFA Login Flow for CLI)

**Step 1: Regular login without MFA (read-only only)**
```bash
aws configure set profile.dev.aws_access_key_id AKIA...
aws configure set profile.dev.aws_secret_access_key ...

# Read operations work
aws s3 ls s3://company-bucket/ --profile dev

# Write operations fail
aws s3 cp file.txt s3://company-bucket/ --profile dev
# ERROR: Access Denied (MFA required)
```

**Step 2: Request MFA session token**
```bash
# Get MFA token from your authenticator app (e.g., 123456)
aws sts get-session-token \
  --serial-number arn:aws:iam::123456789012:mfa/alice \
  --token-code 123456 \
  --profile dev

# Returns temporary credentials:
# {
#   "Credentials": {
#     "AccessKeyId": "ASIA...",
#     "SecretAccessKey": "...",
#     "SessionToken": "...",
#     "Expiration": "2025-01-15T18:00:00Z"
#   }
# }
```

**Step 3: Use MFA credentials**
```bash
# Configure a new profile with session token
aws configure set profile.dev-mfa.aws_access_key_id ASIA...
aws configure set profile.dev-mfa.aws_secret_access_key ...
aws configure set profile.dev-mfa.aws_session_token ...

# Now write operations work
aws s3 cp file.txt s3://company-bucket/ --profile dev-mfa  # Success!
```

### Best Practice: Automate MFA with `aws-mfa` Script

Instead of manual STS calls, use a helper script:

```bash
#!/bin/bash
# save as ~/bin/aws-mfa

MFA_DEVICE_ARN="arn:aws:iam::123456789012:mfa/$USER"
TOKEN_CODE=$1

if [ -z "$TOKEN_CODE" ]; then
  echo "Usage: aws-mfa <token-code>"
  exit 1
fi

# Get session token
STS_OUTPUT=$(aws sts get-session-token \
  --serial-number $MFA_DEVICE_ARN \
  --token-code $TOKEN_CODE \
  --duration-seconds 43200)

# Parse and set environment variables
export AWS_ACCESS_KEY_ID=$(echo $STS_OUTPUT | jq -r .Credentials.AccessKeyId)
export AWS_SECRET_ACCESS_KEY=$(echo $STS_OUTPUT | jq -r .Credentials.SecretAccessKey)
export AWS_SESSION_TOKEN=$(echo $STS_OUTPUT | jq -r .Credentials.SessionToken)

echo "MFA session active for 12 hours"
```

---

## 4: Resource-Based Policies (S3 Bucket Policies vs IAM Policies)

### The Fundamental Difference

| Aspect | Identity-Based Policy (IAM) | Resource-Based Policy (S3, SQS, SNS, KMS) |
| :--- | :--- | :--- |
| **Attached to** | IAM User, Group, Role | AWS Resource (S3 bucket, SQS queue, etc.) |
| **Who it grants access to** | The specific identity | Anyone (including cross-account) |
| **Requires Principal** | No (implied from identity) | Yes (explicitly states who) |
| **Cross-account access** | Requires trust policy + role | Direct (no role needed) |
| **Size limit** | 6,144 characters (managed) / 2,048 (inline) | 20 KB for S3 bucket policy |

### Example: S3 Bucket Policy (Resource-Based)

This policy allows any IAM user from Account B to read objects, **without** Account B creating a role.

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

### The Logic: How IAM + Resource Policies Combine

When a user requests access to an S3 bucket, AWS evaluates:
1. **IAM Policy** (attached to the user) – must Allow the action
2. **S3 Bucket Policy** (attached to the bucket) – must Allow the action
3. **Result:** Both must Allow (intersection). If either denies, access is denied.

**Visual:**
```
User has IAM Policy: Allow s3:GetObject on shared-bucket/*
Bucket Policy: Allow s3:GetObject from Principal = Account B
RESULT: ✅ Access granted

User has IAM Policy: DENY s3:GetObject
Bucket Policy: Allow
RESULT: ❌ Access denied (IAM Deny wins)

User has IAM Policy: Allow
Bucket Policy: Deny (for any reason)
RESULT: ❌ Access denied (Explicit Deny wins)
```

### Real-World Scenario: Public Read-Only Bucket for Static Website

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

**Effect:**
- Anyone on the internet can download `https://my-static-website.s3.amazonaws.com/index.html`
- No one (including anonymous) can upload or delete

### When to Use Which?

| Use Case | Best Approach |
| :--- | :--- |
| **Internal corporate app** (users in your AWS account) | IAM policies attached to user groups |
| **Public website assets** (CSS, JS, images) | S3 bucket policy with `Principal: "*"` |
| **Cross-account access** (Account A needs to read Account B's S3) | S3 bucket policy (no role needed) |
| **Cross-account access to EC2** (can't use resource policy) | IAM role with trust policy (EC2 doesn't support resource policies) |
| **Complex conditions** (IP, MFA, time) | IAM policy (supports more condition keys) |
| **Restricting access to specific VPC endpoints** | S3 bucket policy (supports `aws:SourceVpce`) |

### Advanced: Combining IAM + Resource Policies for Defense in Depth

```json
// S3 Bucket Policy (defense layer 1)
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "RequireVPCAndMFA",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": "arn:aws:s3:::sensitive-bucket/*",
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

This bucket policy says: **Deny ALL access unless**:
- The request comes from VPC `vpc-12345678` (corporate network)
- AND the user authenticated with MFA

Even if a user has `AdministratorAccess` IAM policy, this bucket policy blocks them if they're not in the correct network with MFA.

---

## Summary(3 & 4): Which One Should You Use?

| Scenario | Recommended Approach |
| :--- | :--- |
| "Developers can start/stop EC2 with MFA" | **IAM Policy** with MFA condition |
| "Anyone on internet can download my logo.png" | **S3 Bucket Policy** with `Principal: "*"` |
| "Partner company can write to my S3 bucket" | **S3 Bucket Policy** with cross-account Principal |
| "Lambda function needs to read from DynamoDB" | **IAM Role** attached to Lambda (resource policies not supported) |
| "Only allow access from my corporate VPN" | **IAM Policy** with `aws:SourceIp` OR **S3 Bucket Policy** with same condition |

---

## Hands-On Exercise for You

Try this in your own AWS account (or use AWS CloudShell):

**Task:** Create a policy that allows `s3:PutObject` but ONLY when:
1. User has authenticated with MFA
2. AND the request comes between 9 AM and 5 PM (office hours)

**Hint:** You'll need `aws:MultiFactorAuthPresent`, `aws:CurrentTime`, `DateGreaterThan`, and `DateLessThan`.

**Solution structure:**
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
          "aws:CurrentTime": "2025-01-15T09:00:00Z"
        },
        "DateLessThan": {
          "aws:CurrentTime": "2025-01-15T17:00:00Z"
        }
      }
    }
  ]
}
```

---
