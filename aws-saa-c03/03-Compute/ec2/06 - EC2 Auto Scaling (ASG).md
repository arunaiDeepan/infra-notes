# 📘 Amazon EC2 Auto Scaling - Deep Dive for SAA-C03

Auto Scaling is one of the **most heavily tested** topics on the SAA-C03 exam. Understanding it deeply will directly impact your score.

> **EC2 + ASG series:** [01 - EC2 Intro](01%20-%20EC2%20Intro.md) · [02 - EC2 Instance Types Deep Dive](02%20-%20EC2%20Instance%20Types%20Deep%20Dive.md) · [03 - EC2 Storage Deep Dive](03%20-%20EC2%20Storage%20Deep%20Dive.md) · [04 - EC2 Networking, Placement & Metadata Deep Dive](04%20-%20EC2%20Networking%2C%20Placement%20%26%20Metadata%20Deep%20Dive.md) · [05 - EC2 Pricing & Purchasing Options Deep Dive](05%20-%20EC2%20Pricing%20%26%20Purchasing%20Options%20Deep%20Dive.md) · [06 - EC2 Auto Scaling (ASG)](06%20-%20EC2%20Auto%20Scaling%20%28ASG%29.md) · [07 - ASG Architecture & Advanced Deep Dive](07%20-%20ASG%20Architecture%20%26%20Advanced%20Deep%20Dive.md) · [08 - EC2 & ASG Architecture Patterns & Examples](08%20-%20EC2%20%26%20ASG%20Architecture%20Patterns%20%26%20Examples.md) · [09 - EC2 & ASG Scenario Questions](09%20-%20EC2%20%26%20ASG%20Scenario%20Questions.md) · [10 - EC2 & ASG Important Facts & Cheat Sheet](10%20-%20EC2%20%26%20ASG%20Important%20Facts%20%26%20Cheat%20Sheet.md)

---

## Table of Contents

- [🎯 Core Concept: What is Auto Scaling?](#-core-concept-what-is-auto-scaling)
- [🔧 Launch Templates vs Launch Configurations (Critical for Exam)](#-launch-templates-vs-launch-configurations-critical-for-exam)
- [📊 Scaling Policies - Complete Breakdown](#-scaling-policies---complete-breakdown)
- [🔄 Lifecycle Hooks - The Complete Guide](#-lifecycle-hooks---the-complete-guide)
- [🔥 Warm Pools - Reduce Scaling Latency](#-warm-pools---reduce-scaling-latency)
- [🩺 Health Checks - EC2 vs ELB](#-health-checks---ec2-vs-elb)
- [💰 Cost-Optimized Strategies: Mixed Instances & Spot](#-cost-optimized-strategies-mixed-instances--spot)
- [📝 Real Exam Questions - Deep Analysis](#-real-exam-questions---deep-analysis)
- [📊 Quick Reference Table - Exam Day](#-quick-reference-table---exam-day)
- [📌 Summary: Key Points for SAA-C03](#-summary-key-points-for-saa-c03)
- [🔗 Integration with Other Services](#-integration-with-other-services)

> Companion deep-dives: [07 - ASG Architecture & Advanced Deep Dive](07%20-%20ASG%20Architecture%20%26%20Advanced%20Deep%20Dive.md) (instance refresh, termination policies, cooldown internals, scaling-flow mermaid), [08 - EC2 & ASG Architecture Patterns & Examples](08%20-%20EC2%20%26%20ASG%20Architecture%20Patterns%20%26%20Examples.md), [09 - EC2 & ASG Scenario Questions](09%20-%20EC2%20%26%20ASG%20Scenario%20Questions.md), and [10 - EC2 & ASG Important Facts & Cheat Sheet](10%20-%20EC2%20%26%20ASG%20Important%20Facts%20%26%20Cheat%20Sheet.md).

---

## 🎯 Core Concept: What is Auto Scaling?

Auto Scaling is NOT just about "scaling out" (adding instances). It's a **complete lifecycle management system** for EC2 instances that does four things:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WHAT AUTO SCALING ACTUALLY DOES                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. MAINTAIN CAPACITY - Keeps desired number of instances running           │
│     └── If an instance dies, ASG launches a new one automatically           │
│                                                                             │
│  2. SCALE OUT - Adds instances when demand increases                        │
│     └── Triggered by CloudWatch alarms or schedules                         │
│                                                                             │
│  3. SCALE IN - Removes instances when demand decreases                      │
│     └── Terminates instances (oldest, newest, or closest to next hour)      │
│                                                                             │
│  4. REPLACE UNHEALTHY - Automatically replaces failed instances             │
│     └── Based on EC2 status checks OR ELB health checks                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Insight for Exam**: An Auto Scaling group provides **resilience** even without any scaling policies. Just setting `Min=2, Max=5, Desired=2` means the ASG will always keep 2 instances running, replacing any that fail .

---

[⬆ Back to top](#table-of-contents)

## 🔧 Launch Templates vs Launch Configurations (Critical for Exam)

This is a **high-yield exam topic**. AWS is **phasing out launch configurations** entirely.

| Feature                     | Launch Template            | Launch Configuration         |
| --------------------------- | -------------------------- | ---------------------------- |
| **Status**                  | ✅ Current/recommended     | ❌ Legacy (being deprecated) |
| **Versioning**              | ✅ Yes (multiple versions) | ❌ No                        |
| **Multiple instance types** | ✅ Yes                     | ❌ No                        |
| **Spot + On-Demand mix**    | ✅ Yes                     | ❌ No                        |
| **T2/T3 Unlimited**         | ✅ Yes                     | ❌ No                        |
| **io2 EBS volumes**         | ✅ Yes                     | ❌ No                        |
| **EBS volume tagging**      | ✅ Yes                     | ❌ No                        |
| **Capacity Reservations**   | ✅ Yes                     | ❌ No                        |

**Source**: AWS Documentation and exam study guides

### Why This Matters for the Exam

**Exam Trick**: If you see an answer suggesting a "launch configuration" for a new implementation, it's probably wrong. Launch templates are the modern, recommended approach.

### Real Exam Scenario

```
Question: A company needs to create an Auto Scaling group that launches both
Spot and On-Demand instances across multiple instance types. What is REQUIRED?

A. A launch configuration with mixed instances policy
B. A launch template with mixed instances policy
C. Two separate Auto Scaling groups (one for Spot, one for On-Demand)
D. A launch configuration with multiple instance types

Answer: B

Explanation: Launch configurations do NOT support multiple instance types or
mixed purchase options. This requires a launch template .
```

### Migration Note

Starting **October 1, 2024**, new AWS accounts cannot create launch configurations at all . This makes launch templates the **only** option going forward.

---

[⬆ Back to top](#table-of-contents)

## 📊 Scaling Policies - Complete Breakdown

AWS Auto Scaling offers **five distinct policy types**. Understanding WHEN to use each is exam-critical.

### Policy Type Comparison

| Policy Type            | How It Works                                           | Best For                               | Exam Keyword                                      |
| ---------------------- | ------------------------------------------------------ | -------------------------------------- | ------------------------------------------------- |
| **Target Tracking**    | Maintains metric at target value (e.g., CPU=50%)       | Most production workloads              | "Maintain", "Keep at", "Simple to configure"      |
| **Step Scaling**       | Add/remove instances in steps based on alarm magnitude | Workloads needing fine-grained control | "Multiple thresholds", "Different adjustments"    |
| **Simple Scaling**     | One action per alarm; cooldown period                  | Legacy; avoid                          | "Cooldown period", "Wait 300 seconds"             |
| **Scheduled Scaling**  | Time-based scaling (e.g., 9 AM scale up)               | Predictable patterns                   | "Predictable", "Known schedule", "Business hours" |
| **Predictive Scaling** | ML forecasts demand; launches ahead of load            | Daily/weekly recurring patterns        | "ML", "Forecast", "Proactive", "Pattern"          |

Source:

### Deep Dive: Target Tracking (Most Common)

Target tracking is the **recommended default** for most workloads .

```json
{
  "AutoScalingGroupName": "my-asg",
  "PolicyName": "cpu-target-tracking",
  "PolicyType": "TargetTrackingScaling",
  "TargetTrackingConfiguration": {
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ASGAverageCPUUtilization"
    },
    "TargetValue": 50.0,
    "DisableScaleIn": false
  }
}
```

**How it works**:

1. You set a target (e.g., "keep average CPU at 50%")
2. Auto Scaling continuously adjusts capacity to maintain that target
3. Handles both scale-out AND scale-in automatically
4. No cooldown periods - uses **warm-up times** instead

**Exam Trick**: Target tracking is the answer when the question asks for "simplest" or "most automated" scaling solution.

### Deep Dive: Scheduled Scaling

**Use when traffic patterns are predictable** (e.g., business hours, flash sales, end of month) .

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SCHEDULED SCALING EXAMPLE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Schedule: Every weekday at 8:00 AM                                        │
│   Action: Set Min=10, Desired=10, Max=20                                    │
│                                                                             │
│   Schedule: Every weekday at 8:00 PM                                        │
│   Action: Set Min=2, Desired=2, Max=10                                      │
│                                                                             │
│   Result: System is already scaled BEFORE traffic arrives                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Why this matters**: Scheduled scaling solves the "cold start" problem. Without it, your system only scales AFTER traffic increases, causing user-facing latency during the scale-out period.

### Deep Dive: Predictive Scaling

**What it is**: Uses machine learning to forecast future traffic based on historical patterns. Launches capacity **before** the predicted load arrives .

| Aspect           | Detail                                              |
| ---------------- | --------------------------------------------------- |
| **Requirement**  | 14 days of historical CloudWatch metrics            |
| **Best for**     | Daily/weekly patterns (e.g., retail, banking, SaaS) |
| **How it works** | ML analyzes patterns, predicts load, pre-scales     |
| **Combine with** | Target tracking for fine-grained adjustment         |

**Exam Trick**: If you see "forecast," "machine learning," "historical patterns," or "predictable daily peaks" → think Predictive Scaling.

### Cooldown Periods vs Warm-up Times

This is a subtle but important distinction for the exam.

| Concept             | Applies To                    | Behavior                                                             |
| ------------------- | ----------------------------- | -------------------------------------------------------------------- |
| **Cooldown Period** | Simple Scaling (legacy)       | After scaling, wait 300 seconds before evaluating again              |
| **Warm-up Time**    | Target tracking, Step scaling | New instances are given time to "warm up" before their metrics count |

**Why it matters**: Warm-up times prevent premature scale-in. If a new instance's CPU is low during initialization, you don't want the ASG to terminate it.

---

[⬆ Back to top](#table-of-contents)

## 🔄 Lifecycle Hooks - The Complete Guide

Lifecycle hooks allow you to run **custom code** when instances are launching OR terminating. This is a **high-exam-weight topic** .

### What Lifecycle Hooks Enable

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LIFECYCLE HOOKS IN ACTION                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LAUNCHING (PENDING state):                                                 │
│  ├── Install software / run configuration management                        │
│  ├── Pull secrets from Parameter Store / Secrets Manager                    │
│  ├── Download application code from S3                                      │
│  ├── Register with service discovery (Consul, ECS)                          │
│  └── Warm up caches / pre-load data                                         │
│                                                                             │
│  TERMINATING (TERMINATING state):                                           │
│  ├── Drain connections / finish processing                                  │
│  ├── Upload logs to S3 / CloudWatch                                         │
│  ├── Deregister from load balancer                                          │
│  ├── Send final metrics                                                     │
│  └── Notify other systems of shutdown                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Real Exam Question

**The exact scenario appears on ExamTopics** :

> "A company recently deployed a new auditing system to centralize information about operating system versions, patching, and installed software for Amazon EC2 instances. A solutions architect must ensure all instances provisioned through EC2 Auto Scaling groups successfully send reports to the auditing system as soon as they are launched and terminated. Which solution achieves these goals MOST efficiently?"

**Correct Answer**: Use EC2 Auto Scaling lifecycle hooks to run a custom script to send data to the audit system when instances are launched and terminated.

**Why**:

- Lifecycle hooks can handle BOTH launch AND termination
- Launch configurations cannot handle termination events
- Scheduled Lambda would miss instances launched between runs
- User data only runs at launch, not termination

### Technical Details

| Parameter                     | Value                               |
| ----------------------------- | ----------------------------------- |
| **Default heartbeat timeout** | 3600 seconds (1 hour)               |
| **Maximum heartbeat timeout** | 172800 seconds (48 hours)           |
| **Default result on timeout** | CONTINUE (or ABANDON if configured) |

### Implementing a Lifecycle Hook

```python
# Lambda function triggered by lifecycle hook
def lambda_handler(event, context):
    # Extract hook details
    hook_name = event['detail']['LifecycleHookName']
    asg_name = event['detail']['AutoScalingGroupName']
    instance_id = event['detail']['EC2InstanceId']
    lifecycle_action = event['detail']['LifecycleActionToken']

    # Your custom logic here
    if lifecycle_action == 'launch':
        configure_instance(instance_id)
        register_with_service_discovery(instance_id)
    elif lifecycle_action == 'terminate':
        upload_logs_to_s3(instance_id)
        drain_connections(instance_id)
        deregister_from_load_balancer(instance_id)

    # Complete the hook
    client.complete_lifecycle_action(
        LifecycleHookName=hook_name,
        AutoScalingGroupName=asg_name,
        LifecycleActionResult='CONTINUE'
    )
```

**Exam Trick**: Lifecycle hooks are the answer when the question mentions needing to perform actions **both at launch AND at termination**, or when data must not be lost during scale-in.

---

[⬆ Back to top](#table-of-contents)

## 🔥 Warm Pools - Reduce Scaling Latency

**Problem**: New EC2 instances take 3-10 minutes to boot, install software, and warm up. During a traffic spike, users experience latency during this time.

**Solution**: Warm pools keep pre-initialized instances in a `Stopped` state, ready to start in seconds .

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WARM POOL ARCHITECTURE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Without Warm Pool:                                                         │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐                   │
│  │ Scale   │───►│ Launch  │───►│ Boot    │───►│ Ready   │                   │
│  │ Event   │    │ (2 min) │    │ (2 min) │    │         │                   │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘                   │
│  Total: 5-10 minutes                                                        │
│                                                                             │
│  With Warm Pool:                                                            │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                                  │
│  │ Scale   │───►│ Start   │───►│ Ready   │                                  │
│  │ Event   │    │ (30 sec)│    │         │                                  │
│  └─────────┘    └─────────┘    └─────────┘                                  │
│  Total: 30-60 seconds                                                       │
│                                                                             │
│  Cost: Stopped instances cost less than running instances                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### When to Use Warm Pools

| Use Case                              | Why                                                     |
| ------------------------------------- | ------------------------------------------------------- |
| Applications with long initialization | Java apps (JVM warm-up), large cache pre-loading        |
| Traffic spikes that happen suddenly   | Flash sales, breaking news, viral content               |
| Predictable but rapid scaling         | Morning business hours (combine with scheduled scaling) |

**Exam Keyword**: "Slow scaling response," "initialization takes several minutes," "users experience latency during scale-out" → **Warm Pool** .

---

[⬆ Back to top](#table-of-contents)

## 🩺 Health Checks - EC2 vs ELB

This is a **common exam trap**. Auto Scaling groups have two health check sources.

| Health Check Type     | What It Checks                                     | Failure Detection               | Default?          |
| --------------------- | -------------------------------------------------- | ------------------------------- | ----------------- |
| **EC2 status checks** | Instance reachability, system power                | Instance is running or not      | ✅ Yes            |
| **ELB health checks** | Application endpoint (e.g., `/health` returns 200) | Application is actually working | ❌ Must configure |

**THE EXAM TRAP**: If your application crashes (web server dies, app throws errors) but the EC2 instance is still running, **EC2 status checks will PASS**. The instance stays in the ASG, but your application is DOWN .

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HEALTH CHECK COMPARISON                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Scenario: Web server process crashes, but EC2 instance is running          │
│                                                                             │
│  EC2 Status Check:                                                          │
│  ├── "Instance is running" → PASS                                           │
│  └── Result: ASG keeps instance, but website is DOWN                        │
│                                                                             │
│  ELB Health Check:                                                          │
│  ├── GET /health → Connection refused → FAIL                                │
│  ├── ELB marks instance unhealthy                                           │
│  └── Result: ASG replaces instance, website recovers                        │
│                                                                             │
│  CORRECT CONFIGURATION: Use ELB health checks for production apps           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Configuration for ELB Health Checks

```bash
aws autoscaling attach-load-balancer-target-groups \
    --auto-scaling-group-name my-asg \
    --target-group-arns arn:aws:elasticloadbalancing:us-east-1:123:targetgroup/my-targets

# Then set health check type
aws autoscaling update-auto-scaling-group \
    --auto-scaling-group-name my-asg \
    --health-check-type ELB \
    --health-check-grace-period 300
```

**Health Check Grace Period**: How long to wait after an instance launches before checking its health. Set this longer than your application's startup time to avoid killing instances that are still initializing.

---

[⬆ Back to top](#table-of-contents)

## 💰 Cost-Optimized Strategies: Mixed Instances & Spot

For cost-sensitive, fault-tolerant workloads, Auto Scaling can mix **On-Demand and Spot instances** across **multiple instance types** .

### Mixed Instances Policy Example

```json
{
  "AutoScalingGroupName": "cost-optimized-asg",
  "MixedInstancesPolicy": {
    "LaunchTemplate": {
      "LaunchTemplateSpecification": {
        "LaunchTemplateName": "my-template",
        "Version": "$Latest"
      }
    },
    "InstancesDistribution": {
      "OnDemandPercentageAboveBaseCapacity": 20,
      "SpotAllocationStrategy": "capacity-optimized",
      "SpotInstancePools": 4
    }
  }
}
```

### Allocation Strategies Explained

| Strategy                           | Behavior                                      | Best For                                     |
| ---------------------------------- | --------------------------------------------- | -------------------------------------------- |
| **lowest-price**                   | Selects the cheapest Spot pools               | Cost minimization (higher interruption risk) |
| **capacity-optimized**             | Selects pools with most available capacity    | Workloads that can't be interrupted          |
| **capacity-optimized-prioritized** | Combines instance type priority with capacity | Complex workloads                            |

**Exam Trick**: For production Spot workloads, `capacity-optimized` is preferred because it reduces the chance of Spot interruption .

---

[⬆ Back to top](#table-of-contents)

## 📝 Real Exam Questions - Deep Analysis

### Question 1: Lifecycle Hooks (High Probability)

**Scenario**: A company's order processing system runs on EC2 instances in an Auto Scaling group. When instances are terminated during scale-in events, in-progress orders are being lost. The company needs to ensure no orders are lost during scaling.

**Question**: What should a solutions architect do to prevent data loss during scale-in?

**Options**:
A. Increase the cooldown period to 600 seconds  
B. Use lifecycle hooks to drain connections before termination  
C. Switch from step scaling to target tracking  
D. Enable termination protection on all instances

**Answer**: B

**Explanation**: Lifecycle hooks intercept the termination process, allowing custom code to finish processing orders before the instance is terminated .

---

### Question 2: Warm Pools (High Probability)

**Scenario**: An e-commerce application runs on EC2 instances in an Auto Scaling group. During flash sales, traffic spikes cause new instances to launch, but users experience 5-10 minutes of latency while instances initialize. The application takes 8 minutes to fully warm up.

**Question**: Which solution minimizes latency during scale-out events?

**Options**:
A. Increase the maximum capacity of the Auto Scaling group  
B. Use scheduled scaling to pre-launch instances before flash sales  
C. Configure a warm pool with pre-initialized instances  
D. Switch to a larger instance type

**Answer**: C

**Explanation**: Warm pools keep instances in a stopped state after initialization. When scaling out, these instances start in seconds instead of minutes . Scheduled scaling (B) helps with predictable events but flash sales are unpredictable by nature.

---

### Question 3: Health Checks (Medium Probability)

**Scenario**: A web application runs behind an Application Load Balancer with an Auto Scaling group. Users report intermittent errors, but the Auto Scaling group is not replacing any instances. CloudWatch shows the instances are running and passing EC2 status checks.

**Question**: What is the MOST likely cause?

**Options**:
A. The Auto Scaling group is using EC2 status checks instead of ELB health checks  
B. The cooldown period is too long  
C. The launch template has an invalid AMI  
D. The Auto Scaling group has termination protection enabled

**Answer**: A

**Explanation**: EC2 status checks only verify the instance is running, not that the application is healthy. Switching to ELB health checks would detect application failures .

---

### Question 4: Launch Templates (High Probability)

**Scenario**: A solutions architect is creating an Auto Scaling group that must launch both Spot and On-Demand instances across three different instance types (c5.large, c5.xlarge, c5.2xlarge).

**Question**: Which configuration is REQUIRED to meet this requirement?

**Options**:
A. A launch configuration with multiple instance types  
B. A launch template with a mixed instances policy  
C. Three separate Auto Scaling groups (one per instance type)  
D. A launch configuration with a Spot allocation strategy

**Answer**: B

**Explanation**: Launch configurations do NOT support multiple instance types or mixed purchase options. This feature requires a launch template with a mixed instances policy .

---

### Question 5: Scaling Policy Selection (Medium Probability)

**Scenario**: A company runs a daily batch processing job that runs from 10 PM to 6 AM. The workload is consistent each night. During the day, the system is idle and should scale to zero.

**Question**: Which scaling configuration is MOST cost-effective?

**Options**:
A. Target tracking scaling based on CPU utilization  
B. Step scaling with multiple CloudWatch alarms  
C. Scheduled scaling to increase capacity at 9:45 PM and decrease at 6:15 AM  
D. Predictive scaling with 14 days of history

**Answer**: C

**Explanation**: Since the workload follows a predictable daily schedule, scheduled scaling is most efficient. It ensures capacity is ready when needed and scales to zero when idle, minimizing costs .

---

[⬆ Back to top](#table-of-contents)

## 📊 Quick Reference Table - Exam Day

| If the question mentions...                  | Think...                                         |
| -------------------------------------------- | ------------------------------------------------ |
| "Instance fails but ASG doesn't replace it"  | Use ELB health checks (not EC2 status checks)    |
| "Prevent data loss during scale-in"          | Lifecycle hooks on termination                   |
| "Run script when instance launches"          | User data OR lifecycle hooks (launch)            |
| "Run script when instance terminates"        | Lifecycle hooks (only option)                    |
| "Application takes 5+ minutes to start"      | Warm pool                                        |
| "Predictable daily traffic pattern"          | Scheduled scaling                                |
| "ML forecast of traffic"                     | Predictive scaling                               |
| "Maintain CPU at 50% automatically"          | Target tracking                                  |
| "Multiple instance types + Spot + On-Demand" | Launch template with mixed instances policy      |
| "Launch configuration vs launch template"    | Launch template (always for new implementations) |
| "EC2 vs ELB health check grace period"       | Set grace period > application startup time      |

---

[⬆ Back to top](#table-of-contents)

## 📌 Summary: Key Points for SAA-C03

1. **Launch templates are MANDATORY** for modern features (multi-instance-type, mixed purchase options, versioning)

2. **Lifecycle hooks are the ONLY way** to run code at BOTH launch AND termination

3. **ELB health checks detect application failures** that EC2 status checks miss

4. **Warm pools solve slow scaling** for applications with long initialization times

5. **Target tracking is the recommended default** for most production workloads

6. **Scheduled scaling is for predictable patterns** (business hours, end-of-month batch)

7. **Predictive scaling uses ML** and requires 14 days of history

---

[⬆ Back to top](#table-of-contents)

## 🔗 Integration with Other Services

A complete Auto Scaling architecture often includes:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMPLETE ASG ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CloudWatch ──────► Alarms ──────► Auto Scaling Policies                    │
│       │                   │              │                                  │
│       │                   │              ▼                                  │
│       │                   │      Auto Scaling Group                         │
│       │                   │              │                                  │
│       │                   │              ├── Launch Template                │
│       │                   │              ├── Lifecycle Hooks ──► Lambda     │
│       │                   │              └── Warm Pool                      │
│       │                   │                                                 │
│       │                   ▼                                                 │
│       │              SNS (notifications)                                    │
│       │                                                                     │
│       ▼                                                                     │
│  ELB (health checks, traffic distribution)                                  │
│                                                                             │
│  Other integrations:                                                        │
│  ├── Systems Manager (parameter store for config)                           │
│  ├── Secrets Manager (database credentials)                                 │
│  ├── S3 (bootstrapping scripts, application code)                           │
│  └── CloudFormation (infrastructure as code)                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---
