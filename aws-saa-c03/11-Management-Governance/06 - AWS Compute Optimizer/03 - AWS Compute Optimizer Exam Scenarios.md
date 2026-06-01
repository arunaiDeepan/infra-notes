# AWS Compute Optimizer - Exam Scenarios

> Exam focus: when it's the answer vs Cost Explorer / Trusted Advisor / Auto Scaling, the memory-agent gotcha, and recommend-vs-act. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - AWS Compute Optimizer Intro bits & bytes](01%20-%20AWS%20Compute%20Optimizer%20Intro%20bits%20%26%20bytes.md) · [02 - AWS Compute Optimizer Deep Dive](02%20-%20AWS%20Compute%20Optimizer%20Deep%20Dive.md) · [04 - AWS Compute Optimizer SRE Operations](04%20-%20AWS%20Compute%20Optimizer%20SRE%20Operations.md) · [01 - Cost Explorer Fundamentals & Architecture](01%20-%20Cost%20Explorer%20Fundamentals%20%26%20Architecture.md)

---

## Table of Contents

- [1. Frequently Tested Concepts](#1-frequently-tested-concepts)
- [2. Keywords AWS Uses](#2-keywords-aws-uses)
- [3. Common Distractors](#3-common-distractors)
- [4. Elimination Technique](#4-elimination-technique)
- [5. Medium Scenario Questions (1-20)](#5-medium-scenario-questions-1-20)
- [6. Hard Scenario Questions (1-10)](#6-hard-scenario-questions-1-10)
- [7. One-Line Recap](#7-one-line-recap)

---

## 1. Frequently Tested Concepts

- ML right-sizing for EC2/ASG/EBS/Lambda/Fargate/RDS.
- **Recommend only** — does not apply changes or scale.
- **Memory needs the CloudWatch Agent**.
- Compute Optimizer vs Cost Explorer (RI/SP, forecast) vs Trusted Advisor (broad checks) vs Auto Scaling (count).
- Enhanced metrics = longer lookback (paid).
- Org-wide via management/delegated admin.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                                          | Points to                                |
| :-------------------------------------------------------------- | :--------------------------------------- |
| "right-size", "over/under-provisioned", "optimal instance type" | **Compute Optimizer**                    |
| "ML-based recommendation across EC2/Lambda/EBS"                 | **Compute Optimizer**                    |
| "memory-based recommendation not showing"                       | **Install CloudWatch Agent**             |
| "RI / Savings Plans recommendation", "forecast cost"            | **Cost Explorer**                        |
| "broad best-practice checklist across the account"              | **Trusted Advisor**                      |
| "automatically add/remove capacity"                             | **Auto Scaling** (not Compute Optimizer) |
| "longer 3-month analysis"                                       | **Enhanced infrastructure metrics**      |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Expecting it to **auto-apply** or **scale** (it only recommends).
- Choosing it for **RI/SP/forecast** (that's Cost Explorer).
- Forgetting **memory needs the agent** (CPU-only sizing).
- Using it on brand-new resources (insufficient data → None).
- Confusing it with Trusted Advisor's broader checks.

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **"Right-size / optimal type / over-provisioned"** → Compute Optimizer.
2. **"Automatically scale"** → Auto Scaling (eliminate Compute Optimizer).
3. **"RI/SP/forecast"** → Cost Explorer.
4. **"Memory not factored"** → agent.
5. **"Apply the change"** → you/automation (instance refresh, Lambda config) — the service won't.

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** Reduce EC2 cost by identifying over-provisioned instances with ML.
**Options:** A) Trusted Advisor only B) Compute Optimizer C) Auto Scaling D) Budgets
**Correct:** B
**Explanation:** ML right-sizing of EC2 is Compute Optimizer.

### Q2

**Scenario:** EC2 recommendations ignore memory; workloads are memory-bound.
**Options:** A) Detailed monitoring B) Install CloudWatch Agent for memory metrics C) Enhanced metrics only D) Nothing
**Correct:** B
**Explanation:** Memory must be published via the agent.

### Q3

**Scenario:** Need Savings Plans purchase recommendations and 12-month forecast.
**Options:** A) Compute Optimizer B) Cost Explorer C) Trusted Advisor D) Config
**Correct:** B
**Explanation:** RI/SP recs and forecasting are Cost Explorer.

### Q4

**Scenario:** Automatically add instances under load.
**Options:** A) Compute Optimizer B) Auto Scaling C) Budgets D) Config
**Correct:** B
**Explanation:** Compute Optimizer recommends size, doesn't change count.

### Q5

**Scenario:** Tune Lambda memory for best price/performance.
**Options:** A) Auto Scaling B) Compute Optimizer Lambda recommendations C) Config D) Trusted Advisor
**Correct:** B
**Explanation:** Compute Optimizer recommends Lambda memory.

### Q6

**Scenario:** Modernize gp2 volumes to a cheaper type.
**Options:** A) Trusted Advisor B) Compute Optimizer EBS recommendation (gp2→gp3) C) Auto Scaling D) Budgets
**Correct:** B
**Explanation:** EBS volume recommendations cover type/size/IOPS.

### Q7

**Scenario:** Org-wide right-sizing across 30 accounts in one place.
**Options:** A) Per-account only B) Enable at management/delegated-admin account C) Cost Explorer D) Config
**Correct:** B
**Explanation:** Org-level enablement aggregates recommendations.

### Q8

**Scenario:** A new instance shows finding "None."
**Options:** A) Bug B) Insufficient utilization history yet C) Wrong region D) Need RI
**Correct:** B
**Explanation:** Needs minimum history before recommending.

### Q9

**Scenario:** Improve accuracy for monthly seasonal load.
**Options:** A) Default 14-day B) Enable enhanced infrastructure metrics (up to 3 months) C) Detailed monitoring D) Trusted Advisor
**Correct:** B
**Explanation:** Enhanced metrics extend the lookback.

### Q10

**Scenario:** Apply an ASG instance-type recommendation safely.
**Options:** A) Recreate ASG B) New Launch Template version + instance refresh C) Manual terminate D) Stop/start
**Correct:** B
**Explanation:** Instance refresh rolls the new type in.

### Q11

**Scenario:** Broad account checklist incl. idle load balancers and security.
**Options:** A) Compute Optimizer B) Trusted Advisor C) Cost Explorer D) Config
**Correct:** B
**Explanation:** Trusted Advisor gives broad multi-pillar checks.

### Q12

**Scenario:** Export recommendations for FinOps dashboards.
**Options:** A) Screenshot B) Scheduled S3 export → Athena/QuickSight C) CloudTrail D) Config
**Correct:** B
**Explanation:** S3 export feeds analytics.

### Q13

**Scenario:** Identify Graviton migration candidates for price/performance.
**Options:** A) Cost Explorer B) Compute Optimizer (surfaces ARM options) C) Budgets D) Config
**Correct:** B
**Explanation:** It can recommend Graviton options.

### Q14

**Scenario:** Right-size Fargate task CPU/memory.
**Options:** A) Auto Scaling B) Compute Optimizer ECS-on-Fargate recs C) Config D) Budgets
**Correct:** B
**Explanation:** Fargate service sizing is supported.

### Q15

**Scenario:** Decide between several alternative instance types with risk awareness.
**Options:** A) Single guess B) Compute Optimizer options with performance risk C) Trusted Advisor D) Budgets
**Correct:** B
**Explanation:** It provides multiple options + risk.

### Q16

**Scenario:** Validate a downsize won't hurt peak performance.
**Options:** A) Apply blindly B) Check performance risk + test against peak before prod C) Ignore D) Use Budgets
**Correct:** B
**Explanation:** Honor risk and validate.

### Q17

**Scenario:** Who/what applies the recommended change?
**Options:** A) Compute Optimizer automatically B) You or automation (instance refresh/Lambda config/EBS modify) C) Trusted Advisor D) Config
**Correct:** B
**Explanation:** The service recommends; action is yours.

### Q18

**Scenario:** Cost of base recommendations?
**Options:** A) Per resource B) Free (enhanced metrics are paid) C) Per API D) Per account
**Correct:** B
**Explanation:** Base is free; enhanced metrics cost.

### Q19

**Scenario:** RDS instance right-sizing.
**Options:** A) Not supported B) Supported by Compute Optimizer (newer) C) Cost Explorer only D) Trusted Advisor
**Correct:** B
**Explanation:** RDS recommendations are supported.

### Q20

**Scenario:** Combine right-sizing with commitment discounts for max savings.
**Options:** A) Either alone B) Compute Optimizer (right-size) + Cost Explorer/Savings Plans (commit on the right baseline) C) Auto Scaling D) Budgets
**Correct:** B
**Explanation:** Right-size first, then commit on the corrected baseline.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** A FinOps team wants automated, org-wide right-sizing insight feeding monthly savings reports, without granting prod change rights to the analysts.
**Options:** A) Manual per account B) Org-level Compute Optimizer + delegated admin + scheduled **S3 export** → Athena/QuickSight; analysts read-only, changes go through the platform team C) Trusted Advisor only D) Cost Explorer only
**Correct:** B
**Explanation:** Org enablement + export feeds reporting; separation of duties keeps analysts read-only.

### H2

**Scenario:** Memory-bound app instances are flagged "over-provisioned" and a downsize caused OOM crashes in test.
**Options:** A) Ignore Compute Optimizer B) Install the **CloudWatch Agent** so memory is factored, then re-evaluate; the CPU-only view was misleading C) Disable the service D) Use Trusted Advisor
**Correct:** B
**Explanation:** Without memory metrics, CPU-only analysis over-recommends downsizing for memory-bound workloads.

### H3

**Scenario:** Combine right-sizing with Savings Plans purchase in the correct order to avoid over-committing.
**Options:** A) Buy SP first, then right-size B) **Right-size first** (Compute Optimizer), stabilize the baseline, then purchase Savings Plans on the lower steady-state (Cost Explorer recs) C) Both at once D) Neither
**Correct:** B
**Explanation:** Committing before right-sizing locks in waste; correct order saves more.

### H4

**Scenario:** An ASG recommendation suggests a Graviton type; the app is x86-only with native dependencies.
**Options:** A) Adopt immediately B) Validate ARM compatibility / rebuild artifacts first; only adopt Graviton after testing — or pick the best x86 option C) Ignore all recs D) Disable ASG
**Correct:** B
**Explanation:** Graviton needs ARM-compatible builds; validate before adopting, or choose the recommended x86 alternative.

### H5

**Scenario:** Seasonal e-commerce load means 14-day analysis under-sizes for peak season.
**Options:** A) Trust the 14-day rec B) Enable **enhanced infrastructure metrics** (3-month lookback) and consider peak windows; or schedule capacity for known peaks C) Downsize anyway D) Ignore
**Correct:** B
**Explanation:** Longer lookback captures seasonality; pair with scheduled scaling for known peaks.

### H6

**Scenario:** Platform team wants to auto-apply only **Very Low risk, over-provisioned** EC2 recommendations in non-prod, with humans approving prod.
**Options:** A) Auto-apply everything B) Pull recommendations via API, filter by finding+risk, auto-apply in non-prod via pipeline, route prod to manual approval C) Manual only D) Disable
**Correct:** B
**Explanation:** API-driven filtering by finding/risk enables safe automation with a prod approval gate.

### H7

**Scenario:** Recommendations show huge EBS savings (gp2→gp3) across thousands of volumes; how to roll out safely at scale?
**Options:** A) Modify all at once B) Batch via automation (EBS volume modification is online/no-downtime for gp2→gp3), validate IOPS/throughput targets, monitor C) Recreate volumes D) Ignore
**Correct:** B
**Explanation:** gp2→gp3 can be modified live; batch with validation and monitoring.

### H8

**Scenario:** Some accounts show no recommendations at all after org enablement.
**Options:** A) Service broken B) Those accounts lack opt-in/permission or sufficient data; verify enablement, the service-linked role, and resource history C) Wrong region only D) Need Trusted Advisor
**Correct:** B
**Explanation:** Check per-account opt-in, the service-linked role, and whether resources have enough history.

### H9

**Scenario:** Leadership wants a single number: realized vs recommended savings over time.
**Options:** A) Console screenshots B) Scheduled S3 exports over time → Athena/QuickSight trend of recommended vs applied vs realized (cross-reference Cost Explorer actuals) C) Trusted Advisor D) Budgets only
**Correct:** B
**Explanation:** Time-series exports + Cost Explorer actuals quantify realized savings.

### H10

**Scenario:** A regulated workload can't tolerate any performance regression; how to use Compute Optimizer responsibly?
**Options:** A) Apply all over-provisioned recs B) Only act on **Very Low risk** recs, with memory metrics enabled, staged in non-prod, load-tested at peak, with rollback (keep prior Launch Template version) C) Never use it D) Auto-apply in prod
**Correct:** B
**Explanation:** Conservative risk threshold + full metrics + staged, tested rollout + rollback path fits a no-regression mandate.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Right-size compute with ML → Compute Optimizer (recommends only). Memory → needs the agent. Scale automatically → Auto Scaling. RI/SP/forecast → Cost Explorer. Broad checklist → Trusted Advisor. Right-size before you commit.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - AWS Compute Optimizer SRE Operations](04%20-%20AWS%20Compute%20Optimizer%20SRE%20Operations.md).
