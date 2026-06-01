# Policy Type Comparison & Practice Questions

> Side-by-side comparison of all four AWS policy types (SCP, RCP, Declarative Policy, Permissions Boundary) plus exam-style practice questions with explanations. Use as the final review pass before sitting the SAA-C03.

See also: [08 - SCP](08%20-%20SCP.md) · [09 - RCP](09%20-%20RCP.md) · [10 - Declarative Policies](10%20-%20Declarative%20Policies.md) · [11 - Permissions Boundaries](11%20-%20Permissions%20Boundaries.md) · [23 - IAM Security Tools](23%20-%20IAM%20Security%20Tools.md) · [19 - IAM Cross Account Access](19%20-%20IAM%20Cross%20Account%20Access.md) · [05 - IAM Scenarios](05%20-%20IAM%20Scenarios.md)

---

## Table of Contents

- [Part 1: Master Comparison Table](#part-1-master-comparison-table)
- [Part 2: SCP Exam Questions](#part-2-scp-exam-questions)
- [Part 3: RCP Exam Questions](#part-3-rcp-exam-questions)
- [Part 4: Declarative Policy Exam Questions](#part-4-declarative-policy-exam-questions)
- [Part 5: Permissions Boundary Exam Questions](#part-5-permissions-boundary-exam-questions)
- [Part 6: Mixed Scenario Questions (Most Challenging)](#part-6-mixed-scenario-questions-most-challenging)
- [Part 7: Quick Decision Tree for Exam Questions](#part-7-quick-decision-tree-for-exam-questions)
- [Part 8: Exam-Day Cheat Sheet](#part-8-exam-day-cheat-sheet)

---

**Comprehensive reference guide** for all four AWS policy types, designed specifically for SAA-C03 exam preparation.

---

## Part 1: Master Comparison Table

| Feature                           | **SCP**                      | **RCP**                                                                                                                                                                           | **Declarative Policy**                                             | **Permissions Boundary**                |
| :-------------------------------- | :--------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------- | :-------------------------------------- |
| **Primary purpose**               | Limit what principals can do | Limit who can access resources                                                                                                                                                    | Enforce service configurations                                     | Set max permissions for specific entity |
| **What it governs**               | IAM principals (users/roles) | AWS resources                                                                                                                                                                     | Service configuration                                              | IAM user or role                        |
| **Attached to**                   | Organization, OU, account    | Organization, OU, account                                                                                                                                                         | Organization, OU, account                                          | Specific IAM user or role               |
| **Can grant permissions?**        | ❌ No (only limits)          | ❌ No (only limits)                                                                                                                                                               | ❌ N/A (configures)                                                | ❌ No (only limits)                     |
| **Evaluation layer**              | Layer 1 (first evaluated)    | Layer 1 (first evaluated)                                                                                                                                                         | Service control plane (parallel to IAM)                            | Layer 2 (after SCP, before IAM)         |
| **Management account exempt?**    | ✅ Yes (principals)          | ✅ Yes (resources? Actually resources in management account? Need to check. RCPs apply to resources in member accounts. Management account resources may have different behavior) | ❌ No (full organization)                                          | ❌ No (applies if attached)             |
| **Custom error messages**         | ❌ No                        | ❌ No                                                                                                                                                                             | ✅ Yes                                                             | ❌ No                                   |
| **Service-linked roles required** | ❌ No                        | ❌ No                                                                                                                                                                             | ✅ Yes                                                             | ❌ No                                   |
| **Future API coverage**           | ❌ Must update               | ❌ Must update                                                                                                                                                                    | ✅ Automatic                                                       | ❌ Must update                          |
| **Blocks existing violations**    | ✅ Yes (immediately)         | ✅ Yes (immediately)                                                                                                                                                              | ⚠️ Depends on setting (`block_all_sharing` vs `block_new_sharing`) | ✅ Yes (immediately)                    |
| **Typical use case**              | Compliance, banned services  | Data perimeter, external access                                                                                                                                                   | Configuration enforcement, security baselines                      | Delegated IAM admin                     |
| **Key condition/attribute**       | `aws:PrincipalAccount`       | `aws:PrincipalOrgID`                                                                                                                                                              | `snapshot_block_public_access`                                     | `iam:PermissionsBoundary`               |

---

## Part 2: SCP Exam Questions

### Question 1 (Easy)

**Question:** A company has an AWS Organization with 20 member accounts. The security team wants to prevent any IAM principal from launching EC2 instances in the `us-west-2` region across all accounts. Which policy should they use?

A) Resource Control Policy (RCP) with a Deny effect on `ec2:RunInstances` in us-west-2  
B) Service Control Policy (SCP) with a Deny effect on `ec2:RunInstances` and a condition on `aws:RequestedRegion`  
C) Declarative Policy on EC2 attributes  
D) Permissions Boundary attached to the root user of each account

**Answer:** B

**Explanation:** SCPs are the correct tool for organization-wide principal restrictions. The condition `aws:RequestedRegion` allows targeting specific regions. RCPs control resource access, not principal actions. Declarative policies control configuration, not API actions. Permissions boundaries apply to specific entities, not all principals.

**Exam Tip:** The presence of "any IAM principal across all accounts" immediately signals SCP.

---

### Question 2 (Medium)

**Question:** An organization has an SCP attached at the root level that denies `s3:DeleteBucket`. A user in a member account has an IAM policy attached directly to their user that allows `s3:*` on all resources. Can this user delete an S3 bucket?

A) Yes, because the IAM policy grants explicit Allow  
B) No, because the SCP Deny overrides the IAM Allow  
C) Yes, because the user is in a member account, not the management account  
D) No, because SCPs apply only to IAM roles, not users

**Answer:** B

**Explanation:** Explicit Deny at any layer (SCP, RCP, Permissions Boundary, IAM) overrides any Allow from other layers. The SCP's Deny makes the user's IAM policy irrelevant for `s3:DeleteBucket`.

**Exam Trap:** Answer C is a common distractor. Being in a member account doesn't exempt you from SCPs - being in the _management account_ does.

---

### Question 3 (Hard)

**Question:** A company uses an allow-list SCP strategy. The SCP attached to the `Production` OU allows only `ec2:*`, `s3:*`, and `cloudwatch:*`. A developer in the `Production` OU has an IAM role with `AdministratorAccess` attached. Which services can the developer access?

A) All AWS services (AdministratorAccess overrides the SCP)  
B) Only EC2, S3, and CloudWatch (intersection of SCP and IAM)  
C) No services (allow-list SCPs block everything without explicit allow)  
D) Only IAM services (for managing permissions)

**Answer:** B

**Explanation:** In an allow-list strategy, the SCP explicitly allows only certain services. Even with `AdministratorAccess`, the effective permissions are the **intersection** of what SCP allows and what IAM allows. Since SCP doesn't allow other services (RDS, Lambda, etc.), those actions are implicitly denied.

**Exam Tip:** Remember the formula: `Effective = (SCP Allow) ∩ (IAM Policy Allow)`. Neither alone determines the outcome.

---

## Part 3: RCP Exam Questions

### Question 4 (Easy)

**Question:** An organization wants to ensure that no principal outside their AWS Organization can access any S3 bucket in their member accounts. What is the MOST efficient way to achieve this?

A) Attach a bucket policy to every S3 bucket denying external access  
B) Attach an RCP to the organization root that denies access when `aws:PrincipalOrgID` doesn't match  
C) Attach an SCP to the organization root that denies access to external principals  
D) Use AWS WAF to block external IP addresses

**Answer:** B

**Explanation:** RCPs are designed exactly for this - controlling _who_ can access resources. A single RCP at the root applies to **all resources** in all member accounts, eliminating the need for individual bucket policies. SCPs control what principals can do, not who can access resources.

**Exam Tip:** "External principals accessing our resources" → RCP. "Our principals accessing external resources" → SCP with `aws:ResourceAccount` condition.

---

### Question 5 (Medium)

**Question:** An RCP attached to the `Development` OU denies access from any principal not in the organization. A developer in the management account tries to access an S3 bucket in a member account within the `Development` OU. What happens?

A) Access is allowed because management account principals are exempt from RCPs  
B) Access is denied because the principal is not in the organization (management account is separate)  
C) Access is allowed because RCPs don't apply to S3  
D) Access is denied because RCPs apply to all principals accessing resources in the OU, regardless of account type

**Answer:** D

**Explanation:** Unlike SCPs (which exempt management account principals), RCPs apply to **any principal** accessing resources in affected accounts. The developer is from the management account but is still an external principal relative to the member account's resources.

**Exam Trap:** Many candidates incorrectly assume RCPs have the same management account exemption as SCPs. They don't.

---

### Question 6 (Hard)

**Question:** A company has an RCP denying access from external principals. They also have an S3 bucket with a bucket policy that explicitly allows `"Principal": "*"` for `s3:GetObject`. A user from outside the organization attempts to download an object from this bucket. What happens?

A) Access allowed - bucket policy Allow overrides RCP  
B) Access denied - RCP Deny overrides bucket policy Allow  
C) Access allowed - S3 bucket policies are evaluated before RCPs  
D) Access denied - external users cannot use S3 at all

**Answer:** B

**Explanation:** Explicit Deny at any layer = final Deny. The RCP's Deny on external principals makes the bucket policy's Allow irrelevant. AWS evaluates all layers, and a single Deny fails the request.

**Exam Tip:** This tests the fundamental principle that **Deny always wins**, regardless of policy type.

---

## Part 4: Declarative Policy Exam Questions

### Question 7 (Easy)

**Question:** AWS releases a new API that allows sharing AMIs through a new mechanism. A company has an SCP that denies `ec2:ModifyImageAttribute` (the old API for sharing). Users begin using the new API to share AMIs publicly. Why isn't the SCP blocking this?

A) SCPs don't apply to AMI sharing  
B) The new API is not in the SCP's deny list, so it's allowed  
C) AMIs are not supported by SCPs  
D) The users are in the management account

**Answer:** B

**Explanation:** SCPs operate at the API level and must explicitly list each action. New APIs are not automatically blocked. This is the **key advantage** of declarative policies - they operate at the service control plane and cover future APIs automatically.

---

### Question 8 (Medium)

**Question:** A security team wants to prevent users from creating public EBS snapshots. When a user attempts to share a snapshot publicly, they want the user to see a message directing them to an internal approval process. Which policy type supports this requirement?

A) SCP with a custom error message condition  
B) RCP with a custom error message condition  
C) Declarative Policy with an `exception_message` attribute  
D) Permissions Boundary with a custom error message

**Answer:** C

**Explanation:** Only declarative policies support custom error messages (via the `exception_message` attribute). This is a unique differentiator for the exam.

**Exam Tip:** If you see "custom error message" in a question, the answer is almost always Declarative Policy.

---

### Question 9 (Hard)

**Question:** An organization attaches a declarative policy at the root level that sets `snapshot_block_public_access` to `block_all_sharing`. A security engineer in the management account needs to share a forensic EBS snapshot publicly for an external audit. What should they do?

A) Remove the declarative policy from the root level temporarily  
B) Attach an overriding declarative policy directly to the management account with `state: unblocked`  
C) Use an SCP to override the declarative policy  
D) This is impossible - declarative policies cannot be overridden

**Answer:** B

**Explanation:** Declarative policies support **overrides at lower levels**. Attaching a different declarative policy directly to the management account (or a specific OU containing it) overrides the root-level policy for that account only. The `unblocked` state allows public sharing for that specific account.

**Exam Tip:** Override hierarchy: Account-level policy > OU-level policy > Root-level policy.

---

## Part 5: Permissions Boundary Exam Questions

### Question 10 (Easy)

**Question:** A company wants to allow a junior administrator to create IAM roles for developers. These roles should be limited to only S3 read access. What should the company use?

A) SCP attached to the junior admin's account  
B) RCP attached to the S3 bucket  
C) Permissions Boundary attached to every role the junior admin creates  
D) Declarative policy on IAM

**Answer:** C

**Explanation:** Permissions boundaries are designed for delegating IAM administration safely. The junior admin can create roles, but the boundary ensures those roles cannot exceed S3 read access regardless of what policies the junior admin attaches.

**Exam Tip:** "Delegating IAM administration" + "limiting created roles" = Permissions Boundary.

---

### Question 11 (Medium)

**Question:** A user has a permissions boundary that allows only `s3:GetObject`. The user has an IAM policy attached to their user that allows `s3:*` and `ec2:*`. Can this user launch an EC2 instance?

A) Yes, because the IAM policy allows `ec2:*`  
B) No, because the permissions boundary doesn't allow EC2 actions  
C) Yes, because permissions boundaries only restrict S3 actions  
D) No, because EC2 actions require a service-linked role

**Answer:** B

**Explanation:** Permissions boundaries set the **maximum** permissions. The effective permission is the intersection of the boundary and the IAM policy. Since the boundary doesn't allow EC2 actions, the user cannot launch EC2 instances regardless of their IAM policy.

**Exam Tip:** Remember: `Effective = (Boundary Allow) ∩ (IAM Policy Allow)`. The boundary is a **ceiling**, not a floor.

---

### Question 12 (Hard)

**Question:** An organization has an SCP that denies all DynamoDB actions. A delegated admin creates an IAM role with a permissions boundary that allows DynamoDB actions and attaches an IAM policy that allows DynamoDB actions. Can a user assuming this role access DynamoDB?

A) Yes - the boundary and IAM policy both allow it  
B) No - the SCP Deny overrides both the boundary and the IAM policy  
C) Yes - permissions boundaries override SCPs  
D) No - DynamoDB doesn't support cross-account access

**Answer:** B

**Explanation:** Evaluation order is **SCP → Boundary → IAM Policy**. An SCP Deny at the first layer makes the boundary and IAM policy irrelevant. This tests understanding of the complete evaluation hierarchy.

**Exam Tip:** When multiple policy types are involved, remember the order: **SCP first, then Boundary, then IAM**. Deny at any level = final Deny.

---

## Part 6: Mixed Scenario Questions (Most Challenging)

### Question 13 (Hard)

**Question:** A company has the following policies in place:

- **SCP** (Organization root): Denies `s3:DeleteBucket`
- **RCP** (Production OU): Denies access from external principals
- **Permissions Boundary** (User `deploy`): Allows `s3:*` only
- **IAM Policy** (User `deploy`): Allows `s3:*` and `iam:*`

User `deploy` is in the Production OU. The company's management account user tries to access an S3 bucket in the Production OU from outside the organization's network. Which statement is correct?

A) The management account user can delete S3 buckets because management account is exempt from SCPs  
B) User `deploy` can delete S3 buckets because their IAM policy allows it  
C) The external management account user cannot access the bucket because RCP blocks external access  
D) User `deploy` can create IAM users because their IAM policy allows `iam:*`

**Answer:** C

**Explanation:**

- The RCP blocks **any** external principal (including management account) from accessing resources in the Production OU.
- For user `deploy`: SCP blocks `s3:DeleteBucket` regardless of boundary/IAM.
- For user `deploy`: Permissions boundary only allows `s3:*`, so `iam:*` from IAM policy is irrelevant (blocked by boundary).

**Exam Tip:** This question tests your ability to evaluate **multiple policy types simultaneously** and remember that **Deny wins** at every level.

---

### Question 14 (Very Hard - SAA-C03 Level)

**Question:** A security engineer needs to design a governance strategy with these requirements:

1. Prevent any IAM principal from launching EC2 instances with public IP addresses
2. Ensure no S3 bucket can be shared publicly, even if a bucket policy allows it
3. Allow a delegated admin to create S3-only roles for contractors
4. Display a custom error message when someone attempts to create a public EBS snapshot

Which policy types should be used for each requirement? (Match each requirement to the correct policy type)

| Requirement                         | Policy Type |
| :---------------------------------- | :---------- |
| #1 (EC2 public IPs)                 | ?           |
| #2 (S3 public sharing)              | ?           |
| #3 (Delegated admin for S3 roles)   | ?           |
| #4 (Custom error for EBS snapshots) | ?           |

**Answers:**

| Requirement | Policy Type              | Why                                                                             |
| :---------- | :----------------------- | :------------------------------------------------------------------------------ |
| #1          | **SCP**                  | Restricting what principals can do (launch EC2) is SCP's domain                 |
| #2          | **RCP**                  | Controlling who can access resources (preventing public access) is RCP's domain |
| #3          | **Permissions Boundary** | Delegating IAM role creation with restrictions                                  |
| #4          | **Declarative Policy**   | Custom error messages are unique to declarative policies                        |

**Explanation of #2:** While SCPs could also block `s3:PutBucketPolicy`, RCPs are the **newer, recommended approach** for data perimeter controls. RCPs apply directly to resources and are more comprehensive.

---

## Part 7: Quick Decision Tree for Exam Questions

```
START: What needs to be controlled?
    │
    ├─→ PRINCIPAL actions (what can users/roles do?)
    │       │
    │       ├─→ Across entire organization? → SCP
    │       │
    │       └─→ For specific delegated admin? → Permissions Boundary
    │
    ├─→ RESOURCE access (who can access resources?)
    │       │
    │       └─→ Across entire organization? → RCP
    │
    └─→ SERVICE CONFIGURATION (how are services set up?)
            │
            ├─→ Need custom error messages? → Declarative Policy
            │
            └─→ Future API coverage important? → Declarative Policy
```

---

## Part 8: Exam-Day Cheat Sheet

| If you see...                        | Think...                     |
| :----------------------------------- | :--------------------------- |
| "Prevent any principal from doing X" | SCP                          |
| "Block external access to resources" | RCP                          |
| "Delegate IAM administration"        | Permissions Boundary         |
| "Custom error message"               | Declarative Policy           |
| "Future APIs automatically covered"  | Declarative Policy           |
| "Management account exemption"       | SCP (not RCP or Declarative) |
| "Intersection of permissions"        | Permissions Boundary + IAM   |
| "Explicit Deny overrides"            | All policy types             |

---
