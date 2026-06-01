# AWS Organizations - Cross-Reference

> AWS Organizations is documented in depth in the **Security** domain alongside IAM Identity Center and SCPs. This stub keeps the Management & Governance index complete; follow the link for the full note.

See also: [06 - IAM Identity Center & Organizations](06%20-%20IAM%20Identity%20Center%20%26%20Organizations.md) · [08 - SCP](08%20-%20SCP.md) · [00 - Management and Governance Overview](00%20-%20Management%20and%20Governance%20Overview.md)

---

## Canonical Note

➡️ **[06 - IAM Identity Center & Organizations](06%20-%20IAM%20Identity%20Center%20%26%20Organizations.md)** (in `02-IAM-Security/`)

That note covers: the management account vs member accounts, organizational units (OUs), **consolidated billing**, service control policies, trusted access & delegated administration, and IAM Identity Center for workforce access.

Related policy notes: [08 - SCP](08%20-%20SCP.md) · [09 - RCP](09%20-%20RCP.md) · [10 - Declarative Policies](10%20-%20Declarative%20Policies.md)

---

## Why Organizations Is the Foundation of Governance

Almost every governance capability in this section is **multi-account-aware** and depends on AWS Organizations:

| Capability                                                       | Depends on Organizations for            |
| :--------------------------------------------------------------- | :-------------------------------------- |
| [Control Tower](07%20-%20AWS%20Control%20Tower.md)                        | Account/OU structure + SCP guardrails   |
| [CloudTrail](01%20-%20AWS%20CloudTrail%20Intro%20bits%20%26%20bytes.md) org trail | One trail logging all member accounts   |
| [Config](24%20-%20AWS%20Config%20%26%20Audit%20Manager.md) aggregator           | Multi-account compliance view           |
| [Service Catalog](01%20-%20AWS%20Service%20Catalog%20Intro%20bits%20%26%20bytes.md) | Sharing portfolios across accounts      |
| [Billing](01%20-%20AWS%20Billing%20Dashboard%20Intro%20bits%20%26%20bytes.md)       | Consolidated billing + volume discounts |
| [AWS Backup](01%20-%20AWS%20Backup%20Intro%20bits%20%26%20bytes.md)               | Org-wide backup policies                |

> Exam shortcut: anything described as "across all accounts in the organization" assumes **AWS Organizations** is enabled and usually points to an **org-level** feature (org trail, delegated admin, aggregator, StackSets with org targets).

[⬆ Back to top](#canonical-note)
