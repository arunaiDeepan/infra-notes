# AWS Config - Cross-Reference

> AWS Config is documented in depth in the **Security** domain to keep a single source of truth. This stub exists so the Management & Governance index stays complete; follow the link below for the full note.

See also: [24 - AWS Config & Audit Manager](24%20-%20AWS%20Config%20%26%20Audit%20Manager.md) · [00 - Management and Governance Overview](00%20-%20Management%20and%20Governance%20Overview.md)

---

## Canonical Note

➡️ **[24 - AWS Config & Audit Manager](24%20-%20AWS%20Config%20%26%20Audit%20Manager.md)** (in `02-IAM-Security/`)

That note covers: configuration items & history, the configuration recorder & delivery channel, managed vs custom rules, conformance packs, remediation (with SSM Automation), aggregators for multi-account/multi-region, and Audit Manager.

---

## Why Config Lives in Governance Too

AWS Config answers the governance question **"Is this resource configured correctly, and how did its configuration change over time?"** — the complement to CloudTrail's "who made the API call" and CloudWatch's "is it healthy."

| Question                                  | Service                                                   |
| :---------------------------------------- | :-------------------------------------------------------- |
| Who did what (API audit)                  | [CloudTrail](01%20-%20AWS%20CloudTrail%20Intro%20bits%20%26%20bytes.md)    |
| Is it configured correctly / did it drift | **AWS Config** → [24 - AWS Config & Audit Manager](24%20-%20AWS%20Config%20%26%20Audit%20Manager.md)      |
| Is it healthy / performing                | [CloudWatch](01%20-%20Amazon%20CloudWatch%20Intro%20bits%20%26%20bytes.md) |

## Governance Integrations

- **Control Tower** deploys Config-based **detective guardrails** across the org → [07 - AWS Control Tower](07%20-%20AWS%20Control%20Tower.md)
- **Conformance packs** standardise compliance baselines per OU → [01 - AWS Account Factory and Landing Zone Intro bits & bytes](01%20-%20AWS%20Account%20Factory%20and%20Landing%20Zone%20Intro%20bits%20%26%20bytes.md)
- **Remediation** uses Systems Manager Automation documents → [01 - AWS Systems Manager Intro bits & bytes](01%20-%20AWS%20Systems%20Manager%20Intro%20bits%20%26%20bytes.md)

[⬆ Back to top](#canonical-note)
