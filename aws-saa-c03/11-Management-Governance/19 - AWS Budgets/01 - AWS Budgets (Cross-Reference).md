# AWS Budgets - Cross-Reference

> AWS Budgets is documented in depth in the **Cost Optimization** domain. This stub keeps the Management & Governance index complete; follow the link for the full note.

See also: [01 - AWS Budgets Fundamentals & Architecture](01%20-%20AWS%20Budgets%20Fundamentals%20%26%20Architecture.md) · [01 - Cost Explorer Fundamentals & Architecture](01%20-%20Cost%20Explorer%20Fundamentals%20%26%20Architecture.md) · [00 - Management and Governance Overview](00%20-%20Management%20and%20Governance%20Overview.md)

---

## Canonical Note

➡️ **[01 - AWS Budgets Fundamentals & Architecture](01%20-%20AWS%20Budgets%20Fundamentals%20%26%20Architecture.md)** (in `09-Cost-Optimization/01 - AWS Budgets/`)

Full coverage there: budget types (cost, usage, RI/SP utilisation & coverage), alert thresholds (actual vs forecasted), **budget actions** (apply an SCP/IAM policy or stop EC2/RDS when a threshold is hit), and exam scenarios.

Related: [02 - Budget Types, Actions & Alerts](02%20-%20Budget%20Types%2C%20Actions%20%26%20Alerts.md) · [03 - AWS Budgets Exam Scenarios & Cheat Sheet](03%20-%20AWS%20Budgets%20Exam%20Scenarios%20%26%20Cheat%20Sheet.md)

---

## Governance Angle

Budgets is the **proactive cost-control guardrail**: it can take an _action_ (attach a restrictive SCP/IAM policy) when spend crosses a threshold — turning a passive alert into enforcement.

| Need                                     | Service                                                            |
| :--------------------------------------- | :----------------------------------------------------------------- |
| Alert/act when spend crosses a threshold | **AWS Budgets** → [01 - AWS Budgets Fundamentals & Architecture](01%20-%20AWS%20Budgets%20Fundamentals%20%26%20Architecture.md) |
| Analyse & forecast historical cost       | [Cost Explorer](01%20-%20Cost%20Explorer%20Fundamentals%20%26%20Architecture.md)  |
| Raw billing line items for BI            | [Cost & Usage Report](01%20-%20CUR%20Fundamentals%20%26%20Architecture.md)      |

[⬆ Back to top](#canonical-note)
