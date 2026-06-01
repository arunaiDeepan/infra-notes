# AWS Cost Explorer - Cross-Reference

> Cost Explorer is documented in depth in the **Cost Optimization** domain. This stub keeps the Management & Governance index complete; follow the link for the full note.

See also: [01 - Cost Explorer Fundamentals & Architecture](01%20-%20Cost%20Explorer%20Fundamentals%20%26%20Architecture.md) · [01 - AWS Budgets Fundamentals & Architecture](01%20-%20AWS%20Budgets%20Fundamentals%20%26%20Architecture.md) · [00 - Management and Governance Overview](00%20-%20Management%20and%20Governance%20Overview.md)

---

## Canonical Note

➡️ **[01 - Cost Explorer Fundamentals & Architecture](01%20-%20Cost%20Explorer%20Fundamentals%20%26%20Architecture.md)** (in `09-Cost-Optimization/03 - AWS Cost Explorer/`)

Full coverage there: cost & usage visualisation, filtering/grouping by tag/service/account, **forecasting**, **rightsizing recommendations**, and Reserved Instance / Savings Plans recommendations.

Related: [02 - Cost Explorer Features, Forecasting & Rightsizing](02%20-%20Cost%20Explorer%20Features%2C%20Forecasting%20%26%20Rightsizing.md) · [03 - Cost Explorer Exam Scenarios & Cheat Sheet](03%20-%20Cost%20Explorer%20Exam%20Scenarios%20%26%20Cheat%20Sheet.md)

---

## Governance Angle

Cost Explorer is the **analysis & recommendation** surface for cost governance. It is _reactive/analytical_ (look back, forecast forward, recommend), whereas [Budgets](01%20-%20AWS%20Budgets%20Fundamentals%20%26%20Architecture.md) is _proactive_ (alert/act on thresholds). For right-sizing **compute specifically**, pair it with [Compute Optimizer](01%20-%20AWS%20Compute%20Optimizer%20Intro%20bits%20%26%20bytes.md).

| Tool   | Cost Explorer                 | Compute Optimizer               |
| :----- | :---------------------------- | :------------------------------ |
| Scope  | All services' cost & usage    | EC2/ASG/Lambda/EBS right-sizing |
| Output | Trends, forecasts, RI/SP recs | Instance-type recommendations   |

[⬆ Back to top](#canonical-note)
