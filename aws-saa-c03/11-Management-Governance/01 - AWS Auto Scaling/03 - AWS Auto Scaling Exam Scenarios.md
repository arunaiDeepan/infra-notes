# AWS Auto Scaling - Exam Scenarios

> SAA-C03 exam focus for Auto Scaling: the keywords AWS uses, the distractors it plants, an elimination technique, and **20 medium + 10 hard** scenario questions with full reasoning.

See also: [01 - AWS Auto Scaling Intro bits & bytes](01%20-%20AWS%20Auto%20Scaling%20Intro%20bits%20%26%20bytes.md) · [02 - AWS Auto Scaling Deep Dive](02%20-%20AWS%20Auto%20Scaling%20Deep%20Dive.md) · [04 - AWS Auto Scaling SRE Operations](04%20-%20AWS%20Auto%20Scaling%20SRE%20Operations.md) · [29 - Ex Qns](29%20-%20Ex%20Qns.md)

---

## Table of Contents

- [1. Frequently Tested Concepts](#1-frequently-tested-concepts)
- [2. Keywords AWS Uses (Trigger Words)](#2-keywords-aws-uses-trigger-words)
- [3. Common Distractors](#3-common-distractors)
- [4. Elimination Technique](#4-elimination-technique)
- [5. Medium Scenario Questions (1-20)](#5-medium-scenario-questions-1-20)
- [6. Hard Scenario Questions (1-10)](#6-hard-scenario-questions-1-10)
- [7. One-Line Recap](#7-one-line-recap)

---

## 1. Frequently Tested Concepts

- **ELB vs EC2 health checks** — replacing hung-but-running instances.
- **Choosing the policy type** — target tracking vs scheduled vs predictive vs step.
- **Multi-AZ resilience** — `min` capacity surviving an AZ failure.
- **Spot + On-Demand mixed instances** for cost on fault-tolerant tiers.
- **Lifecycle hooks** for graceful bootstrap/drain.
- **Why an ASG won't scale** (vCPU quota, subnet IP exhaustion, grace period).
- **SQS-driven scaling** using a backlog-per-instance custom metric.
- **Auto Scaling vs Compute Optimizer** (count vs size).

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses (Trigger Words)

| Phrase in the question                                           | Points to                                           |
| :--------------------------------------------------------------- | :-------------------------------------------------- |
| "automatically replace unhealthy / failed instances"             | ASG + **ELB health checks**                         |
| "maintain average CPU at…"                                       | **Target tracking**                                 |
| "every weekday at 8 AM" / "known schedule"                       | **Scheduled scaling**                               |
| "scale **before** the spike", "recurring daily pattern"          | **Predictive scaling**                              |
| "most cost-effective", "fault-tolerant", "interruption-tolerant" | **Spot** in a mixed-instances ASG                   |
| "run a script before termination", "drain connections"           | **Lifecycle hook** (Terminating:Wait)               |
| "process a queue", "messages backlog"                            | Scale on **SQS backlog per instance** custom metric |
| "highly available", "survive AZ failure"                         | **Multi-AZ**, raise `min`                           |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- **Launch Configuration** offered alongside Launch Template — choose **Launch Template** (LCs are legacy, no Spot mix, no versioning).
- **CloudWatch alarm without a scaling policy** — an alarm alone doesn't scale anything; it must invoke a policy.
- **Simple scaling** vs step/target — simple is legacy; prefer target tracking.
- **Scaling the database with EC2 Auto Scaling** — RDS/DynamoDB use their own scaling; an ASG can't scale them.
- **Vertical scaling (bigger instance)** offered when the correct answer is horizontal scaling for HA.
- **Increasing `desired` manually** when the scenario asks for _automatic_ adjustment.

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **Is the trigger a clock or a metric?** Clock → scheduled. Metric → target tracking/step. Learned pattern, must pre-scale → predictive.
2. **Is the requirement HA or cost?** HA → multi-AZ + higher `min`. Cost → Spot mixed instances + aggressive scale-in.
3. **Is it "replace failed instances"?** → ASG with **ELB health checks** (not EC2).
4. **Is the resource EC2?** If it's DynamoDB/ECS/Aurora, the answer is _Application_ Auto Scaling, not an EC2 ASG.
5. **Reject legacy options** (Launch Configuration, simple scaling) unless explicitly required.

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** A web tier behind an ALB occasionally has instances that are "running" but return HTTP 500s. The ASG never replaces them.
**Options:** A) Switch to larger instances B) Enable ELB health checks on the ASG C) Add a second ALB D) Increase desired capacity
**Correct:** B
**Explanation:** Default `EC2` health checks only see instance state, not app health. **ELB health checks** let the target group's view of health drive replacement.
**Why others are wrong:** A/C/D don't address detection of app-level failure.

### Q2

**Scenario:** Traffic is heavy 9 AM–6 PM weekdays and near-zero otherwise. Minimise cost while meeting demand.
**Options:** A) Target tracking only B) Scheduled scaling C) Predictive only D) Manual changes
**Correct:** B
**Explanation:** The trigger is a **known clock**; scheduled scaling pre-sets capacity. Often paired with target tracking as a safety net.
**Why others are wrong:** Target tracking reacts late each morning; manual is not automatic; predictive is overkill for a fixed schedule.

### Q3

**Scenario:** Keep average CPU utilisation near 50% across a fleet with minimal configuration.
**Options:** A) Step scaling B) Simple scaling C) Target tracking D) Scheduled
**Correct:** C
**Explanation:** Target tracking maintains a metric at a setpoint with the least tuning.

### Q4

**Scenario:** A fault-tolerant batch tier must be as cheap as possible and can tolerate interruptions.
**Options:** A) All On-Demand B) Reserved Instances C) Mixed instances with Spot D) Dedicated Hosts
**Correct:** C
**Explanation:** Spot in a mixed-instances ASG cuts cost dramatically for interruption-tolerant work; keep a small On-Demand base.

### Q5

**Scenario:** Before an instance is terminated on scale-in, you must upload its logs and deregister it from an external system.
**Options:** A) User data B) Lifecycle hook (Terminating:Wait) C) Termination policy D) Cooldown
**Correct:** B
**Explanation:** A terminate lifecycle hook pauses termination so you can drain/clean up, then call `CompleteLifecycleAction`.

### Q6

**Scenario:** Worker fleet processes an SQS queue. Scale workers with the backlog.
**Options:** A) Scale on CPU B) Scale on a custom "backlog per instance" metric C) Scheduled scaling D) Scale on network in
**Correct:** B
**Explanation:** The right signal is `ApproximateNumberOfMessages` / number of instances → backlog per instance, used in target tracking.

### Q7

**Scenario:** An application must survive the loss of one Availability Zone with no capacity shortfall.
**Options:** A) ASG in 1 AZ, min 4 B) ASG across 2 AZs, min sized for full load in one AZ C) Two ASGs in one AZ D) Vertical scaling
**Correct:** B
**Explanation:** Span ≥2 AZs and set `min` so a surviving AZ can carry the load.

### Q8

**Scenario:** You must roll out a new AMI to all ASG instances with minimal downtime, no external tooling.
**Options:** A) Terminate all instances B) Instance refresh with MinHealthyPercentage C) Change desired to 0 then up D) New ASG manually
**Correct:** B
**Explanation:** **Instance refresh** does a controlled rolling replacement to a new Launch Template/AMI version.

### Q9

**Scenario:** New instances are killed seconds after launch before the app finishes booting.
**Options:** A) Increase max B) Increase health check grace period C) Lower desired D) Use NLB
**Correct:** B
**Explanation:** The **health check grace period** is shorter than boot time; raise it.

### Q10

**Scenario:** Choose the recipe object for a new ASG that needs Spot+On-Demand mix and versioning.
**Options:** A) Launch Configuration B) Launch Template C) AMI only D) User data script
**Correct:** B
**Explanation:** Only **Launch Templates** support mixed instances and versioning.

### Q11

**Scenario:** DynamoDB throttling under variable load; you want capacity to adjust automatically.
**Options:** A) EC2 Auto Scaling B) DynamoDB auto scaling (Application Auto Scaling) C) Larger instances D) Step scaling on EC2
**Correct:** B
**Explanation:** DynamoDB scales via Application Auto Scaling, not an EC2 ASG.

### Q12

**Scenario:** Instances are added then removed repeatedly (flapping) within minutes.
**Options:** A) Lower the target value B) Add instance warm-up / cooldown C) Use smaller instances D) Disable health checks
**Correct:** B
**Explanation:** Lack of warm-up/cooldown lets metrics from booting instances trigger premature opposite actions.

### Q13

**Scenario:** Audit requirement: know who changed an ASG's desired capacity and when.
**Options:** A) CloudWatch Logs B) CloudTrail C) Config D) VPC Flow Logs
**Correct:** B
**Explanation:** API calls like `SetDesiredCapacity` are recorded in **CloudTrail**.

### Q14

**Scenario:** A cyclical daily traffic wave; reactive scaling always lags and users see slowness at the ramp.
**Options:** A) Step scaling B) Predictive scaling C) Simple scaling D) Bigger instances
**Correct:** B
**Explanation:** Predictive scaling forecasts and pre-scales ahead of the recurring wave.

### Q15

**Scenario:** You want notifications whenever the ASG launches or terminates instances.
**Options:** A) SNS notifications / EventBridge rule on ASG events B) CloudTrail email C) Config rule D) Flow logs
**Correct:** A
**Explanation:** ASG integrates with **SNS** and **EventBridge** for lifecycle event notifications.

### Q16

**Scenario:** During scale-in you want the oldest AMI versions removed first during a migration.
**Options:** A) NewestInstance B) OldestLaunchTemplate termination policy C) ClosestToNextInstanceHour D) Default only
**Correct:** B
**Explanation:** `OldestLaunchTemplate` retires stale-recipe instances first.

### Q17

**Scenario:** A slow-booting app (5 min) needs near-instant scale-out for sudden spikes.
**Options:** A) Predictive only B) Warm pool C) Larger max D) NLB
**Correct:** B
**Explanation:** **Warm pools** keep pre-initialised stopped instances ready to enter service quickly.

### Q18

**Scenario:** Cost report shows the fleet rarely scales in even at night.
**Options:** A) Raise min B) Make scale-in policy less conservative / add scheduled scale-in C) Use bigger instances D) Disable scaling
**Correct:** B
**Explanation:** Overly timid scale-in (or no scheduled scale-in) wastes money off-peak.

### Q19

**Scenario:** One instance runs a long job and must not be terminated on scale-in.
**Options:** A) Standby B) Instance scale-in protection C) Lifecycle hook D) Cooldown
**Correct:** B
**Explanation:** **Scale-in protection** exempts a specific instance from scale-in termination.

### Q20

**Scenario:** A team wants right-sizing recommendations for the ASG's instance type, not more instances.
**Options:** A) Predictive scaling B) Compute Optimizer C) Step scaling D) Warm pool
**Correct:** B
**Explanation:** Compute Optimizer recommends a better **type/size**; Auto Scaling changes **count**.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** A stateful app keeps a per-instance cache. Under target tracking it scales correctly, but every scale-in drops a node mid-request and users hit errors. Requirements: keep elasticity, eliminate user-facing errors on scale-in.
**Options:** A) Disable scale-in B) Add a Terminating lifecycle hook that drains connections + enable connection draining (deregistration delay) on the target group C) Switch to scheduled scaling D) Use bigger instances
**Correct:** B
**Explanation:** Graceful scale-in needs **target-group deregistration delay (connection draining)** plus a **lifecycle hook** to finish in-flight work before termination. Elasticity is preserved.
**Why others are wrong:** A kills cost savings; C doesn't fix mid-request termination; D doesn't address draining.

### H2

**Scenario:** An ASG behind an ALB serves a global audience. During a regional AZ impairment, capacity dropped and latency spiked even though `min` was met across 3 AZs. Investigation shows all instances were the same instance type, which had a capacity shortage in the healthy AZs.
**Options:** A) Increase max only B) Use a mixed-instances policy with multiple instance types and `price-capacity-optimized` C) Move to a single larger type D) Add a second ALB
**Correct:** B
**Explanation:** Diversifying instance types via a **mixed-instances policy** avoids being blocked by a single type's capacity shortage during an AZ event.

### H3

**Scenario:** A queue-driven worker fleet must scale to zero when idle to save cost but resume within seconds when work arrives. CPU-based scaling keeps a minimum of 2 running.
**Options:** A) Target tracking on CPU, min 2 B) Target tracking on SQS backlog-per-instance with min 0 + warm pool C) Scheduled scaling D) Predictive scaling
**Correct:** B
**Explanation:** Scaling on **backlog per instance** with `min=0` allows scale-to-zero; a **warm pool** gives fast resume. CPU is the wrong signal for a queue worker.

### H4

**Scenario:** After enabling predictive scaling, capacity sometimes overshoots on atypical days (holidays). The business wants predictive benefit on normal days but a hard cost ceiling.
**Options:** A) Disable predictive B) Set predictive to **Forecast only** then validate, and cap with `max` + a target-tracking policy for reactive correction C) Use scheduled only D) Lower min
**Correct:** B
**Explanation:** Run predictive in **forecast-only** mode first to validate, keep `max` as a hard ceiling, and let target tracking correct reactively. This balances anticipation with a cost cap.

### H5

**Scenario:** An ASG won't grow beyond 20 instances despite `max=50` and demand. No errors in the ASG console; activity history shows "launch failed."
**Options:** A) Raise max B) Check EC2 On-Demand vCPU quota and subnet free IP addresses C) Change termination policy D) Add an AZ blindly
**Correct:** B
**Explanation:** Launch failures at a ceiling below `max` almost always mean an **account vCPU quota** or **subnet IP exhaustion**, not the ASG config. See [01 - AWS Service Quotas Intro bits & bytes](01%20-%20AWS%20Service%20Quotas%20Intro%20bits%20%26%20bytes.md).

### H6

**Scenario:** A blue/green-style AMI rollout via instance refresh stalled at 60% with several instances stuck `Pending:Wait`.
**Options:** A) Cancel and terminate all B) A launch lifecycle hook isn't calling CompleteLifecycleAction — fix the bootstrap signal or it times out C) Raise max D) Disable health checks
**Correct:** B
**Explanation:** Instances in `Pending:Wait` are blocked on a **launch lifecycle hook** awaiting `CompleteLifecycleAction`; the refresh pauses until they proceed or time out.

### H7

**Scenario:** A regulated workload requires that scaling activity and capacity configuration changes are both immutably auditable and that drift from an approved configuration is detected.
**Options:** A) CloudTrail only B) CloudTrail (who/what) + AWS Config (configuration history & drift) C) CloudWatch only D) SNS only
**Correct:** B
**Explanation:** **CloudTrail** answers "who changed it"; **AWS Config** records configuration state over time and detects **drift** from the desired config. See [24 - AWS Config & Audit Manager](24%20-%20AWS%20Config%20%26%20Audit%20Manager.md).

### H8

**Scenario:** Target tracking on `RequestCountPerTarget` causes wild oscillation: it scales out hard, then the per-target metric collapses and it scales in hard, repeating.
**Options:** A) Lower max B) Set an appropriate **instance warm-up** so warming instances are excluded from the metric, and pick a stable target C) Switch to simple scaling D) Disable the ALB
**Correct:** B
**Explanation:** Without warm-up, newly added instances dilute the per-target metric immediately, triggering opposite actions. Proper **warm-up** + a realistic target damps oscillation.

### H9

**Scenario:** A cost-sensitive Spot-heavy fleet suffers correlated interruptions that briefly drop below safe capacity.
**Options:** A) All Spot, more types B) Mixed instances: On-Demand base capacity + Spot for the rest, multiple types/AZs, capacity rebalancing C) All On-Demand D) Single Spot type
**Correct:** B
**Explanation:** Define an **On-Demand base** for guaranteed floor, diversify Spot across many types/AZs, and enable **capacity rebalancing** to replace before interruption.

### H10

**Scenario:** A multi-account org wants every team's ASGs to enforce IMDSv2, span ≥2 AZs, and use ELB health checks — without relying on teams remembering.
**Options:** A) Email guidelines B) Enforce via Launch Template baked in a Service Catalog product + Config rules + SCP/guardrails, deployed org-wide C) Manual review D) CloudWatch alarm
**Correct:** B
**Explanation:** Standardise via a **Service Catalog** product (golden Launch Template), detect violations with **Config rules**, and constrain with **SCPs/Control Tower guardrails** — governance, not goodwill. See [01 - AWS Service Catalog Intro bits & bytes](01%20-%20AWS%20Service%20Catalog%20Intro%20bits%20%26%20bytes.md) and [07 - AWS Control Tower](07%20-%20AWS%20Control%20Tower.md).

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Clock → scheduled. Metric → target tracking. Learned cycle → predictive. Replace failures → ELB health checks. Cheap + fault-tolerant → Spot mixed instances. Won't scale → check vCPU quota & subnet IPs.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - AWS Auto Scaling SRE Operations](04%20-%20AWS%20Auto%20Scaling%20SRE%20Operations.md) for troubleshooting, runbooks, and real examples.
