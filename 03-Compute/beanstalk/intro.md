# 📘 AWS Elastic Beanstalk - Complete SAA-C03 Study Guide

Elastic Beanstalk is AWS's **Platform-as-a-Service (PaaS)** offering that lets you deploy and scale applications without managing the underlying infrastructure. For the SAA-C03 exam, think of it as the "sweet spot" between full control (EC2) and serverless (Lambda).

---

## 🎯 Core Concept: What is Elastic Beanstalk?

**Elastic Beanstalk is a developer-centric view of deploying applications on AWS** . You upload your code, and Elastic Beanstalk automatically handles the rest: capacity provisioning, load balancing, auto-scaling, and application health monitoring.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ELASTIC BEANSTALK MENTAL MODEL                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   DEVELOPER EXPERIENCE:                                                     │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  "Just upload my code and make it work"                             │  │
│   │                                                                      │  │
│   │  $ git push                                                          │  │
│   │  or                                                                  │  │
│   │  $ zip -r app.zip . && aws elasticbeanstalk create-application-version│
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  ELASTIC BEANSTALK HANDLES:                                         │  │
│   │  ├── EC2 instances (provisioned and configured)                     │  │
│   │  ├── Auto Scaling Group (scales based on load)                      │  │
│   │  ├── Load Balancer (distributes traffic)                            │  │
│   │  ├── Security Groups (firewall rules)                               │  │
│   │  ├── RDS database (optional, provisioned)                           │  │
│   │  └── CloudWatch monitoring (logs and metrics)                       │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   KEY INSIGHT: Elastic Beanstalk is FREE! You only pay for the underlying   │
│                resources (EC2, RDS, ELB, etc.)     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Elastic Beanstalk Architecture Models

Elastic Beanstalk supports **three distinct architecture models** for different use cases :

| Architecture Model | Components | Use Case |
|-------------------|------------|----------|
| **Single Instance** | 1 EC2 instance, no ELB | Development, testing, low-traffic apps |
| **Load Balancer + Auto Scaling** | ELB + ASG with multiple EC2 instances | Production web applications |
| **Auto Scaling Only** | ASG only (no ELB) | Non-web production apps (workers, batch) |

### Decision Framework

```
START: What type of application?

├── Development/Test ──► Single Instance (cheapest, simplest)
│
├── Production Web App ──► Load Balancer + Auto Scaling
│                         ├── Multi-AZ for high availability
│                         └── ELB handles traffic distribution
│
└── Production Worker/Background ──► Auto Scaling only
                                    (no need for load balancer)
```

**Exam Trick**: Elastic Beanstalk uses **all the AWS components** you already know: EC2, ASG, ELB, RDS, S3, CloudWatch, and CloudFormation under the hood .

---

## 📦 Elastic Beanstalk Components

Elastic Beanstalk has a **hierarchical structure** that's important for the exam :

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ELASTIC BEANSTALK COMPONENT HIERARCHY                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   APPLICATION                                                               │
│   ├── The logical container for your project                               │
│   ├── Can have multiple environments (dev, staging, prod)                  │
│   └── Stores all application versions                                      │
│       │                                                                     │
│       ▼                                                                     │
│   APPLICATION VERSION                                                       │
│   ├── Specific labelled deployment of your code                            │
│   ├── Each deployment gets a unique version ID                             │
│   └── Stored in S3 (Elastic Beanstalk creates a bucket)                    │
│       │                                                                     │
│       ▼                                                                     │
│   ENVIRONMENT                                                               │
│   ├── A running instance of an application version                         │
│   ├── Has a unique CNAME (e.g., myapp.us-east-1.elasticbeanstalk.com)      │
│   ├── Can be: dev, staging, prod                                           │
│   └── Free naming (you choose)                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Exam Concept**: You can **promote application versions** between environments. Deploy to dev → test → promote the same version to prod .

---

## 🚀 Deployment Policies (CRITICAL for Exam)

This is one of the **most heavily tested** Elastic Beanstalk topics. Choosing the right deployment policy affects downtime, cost, and rollback capability .

### The Four Deployment Policies Compared

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT POLICIES COMPARISON                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. ALL AT ONCE (Deploy on the go)                                          │
│     ├── How: All instances updated simultaneously                           │
│     ├── Downtime: YES (instances unavailable during deployment)             │
│     ├── Cost: No additional cost                                            │
│     ├── Speed: Fastest                                                      │
│     └── Best for: Dev/test environments                                     │
│                                                                             │
│  2. ROLLING                                                                 │
│     ├── How: Update batches of instances (e.g., 25% at a time)              │
│     ├── Downtime: NO, but capacity reduced during deployment                │
│     ├── Cost: No additional cost                                            │
│     ├── Speed: Slower (depends on batch size)                               │
│     ├── Risk: Both old AND new versions run simultaneously                  │
│     └── Best for: Production with some capacity tolerance                   │
│                                                                             │
│  3. ROLLING WITH ADDITIONAL BATCH                                           │
│     ├── How: Launch new instances for the batch BEFORE taking old offline   │
│     ├── Downtime: NO, full capacity maintained                              │
│     ├── Cost: Small additional cost (temporary extra instances)             │
│     ├── Speed: Slower than rolling                                          │
│     ├── Benefit: Full capacity during deployment                            │
│     └── Best for: Production where capacity CANNOT drop                     │
│                                                                             │
│  4. IMMUTABLE                                                               │
│     ├── How: Create entirely NEW ASG with new instances, deploy, then swap  │
│     ├── Downtime: ZERO (blue/green deployment)                              │
│     ├── Cost: HIGH (double capacity during deployment)                      │
│     ├── Speed: Slowest (provisions new infrastructure)                      │
│     ├── Rollback: INSTANT (terminate new ASG)                               │
│     └── Best for: Mission-critical production                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Detailed Analysis of Each Policy

#### All At Once (Fastest, Most Downtime)

```yaml
# .ebextensions/deployment-policy.config
option_settings:
  aws:elasticbeanstalk:command:
    DeploymentPolicy: AllAtOnce
```

**Exam Use Case**: "Development team needs fastest deployment possible for testing" → All At Once.

**Why not production**: All instances are unavailable while updating. If you have 10 instances, ALL 10 are updating simultaneously → application downtime.

#### Rolling (Reduced Capacity)

```yaml
option_settings:
  aws:elasticbeanstalk:command:
    DeploymentPolicy: Rolling
    RollingUpdateType: Health
    RollingUpdateEnabled: true
    BatchSizeType: Percentage
    BatchSize: 25
```

**How it works**:

1. Take 25% of instances out of service
2. Deploy new version to those instances
3. Wait for health checks to pass
4. Move to next 25% batch

**Risk**: During deployment, you're running at 75% capacity (if batch size is 25%) .

#### Rolling with Additional Batch (Full Capacity)

```yaml
option_settings:
  aws:elasticbeanstalk:command:
    DeploymentPolicy: RollingWithAdditionalBatch
    RollingUpdateEnabled: true
    BatchSizeType: Percentage
    BatchSize: 25
```

**How it works**:

1. Launch NEW instances for the first batch (25% above desired capacity)
2. Deploy new version to new instances
3. Move traffic to new instances
4. Terminate old instances from that batch
5. Repeat

**Exam Keyword**: "Must maintain full capacity during deployment" → Rolling with Additional Batch.

#### Immutable (Zero Downtime, Fast Rollback)

```yaml
option_settings:
  aws:elasticbeanstalk:command:
    DeploymentPolicy: Immutable
```

**How it works**:

1. Create temporary Auto Scaling group alongside existing one
2. Launch completely NEW instances with new version
3. When all new instances pass health checks, redirect traffic
4. Terminate OLD Auto Scaling group

**Cost**: You pay for double the instances during deployment .

**Exam Trick**: "Mission-critical application that cannot tolerate any deployment issues" → Immutable.

### Decision Matrix

| Requirement | Recommended Policy |
|-------------|-------------------|
| Fastest deployment, downtime acceptable | All At Once |
| No downtime, cost sensitive | Rolling |
| No downtime, full capacity required | Rolling with Additional Batch |
| Zero downtime, fast rollback, higher cost acceptable | Immutable |

---

## 🔧 Supported Platforms

Elastic Beanstalk supports **many platforms out-of-the-box** :

| Platform | Support |
|----------|---------|
| **Go** | ✅ Full support |
| **Java** | ✅ Full support (Tomcat, Java SE) |
| **Python** | ✅ Full support |
| **Node.js** | ✅ Full support |
| **Ruby** | ✅ Full support |
| **PHP** | ✅ Full support |
| **.NET** | ✅ Full support (Windows) |
| **Docker** | ✅ Single container, multi-container, preconfigured |
| **Custom** | ✅ Write your own platform |

**Worker Environments**: For long-running background tasks, Elastic Beanstalk supports **worker environments** that process jobs from an SQS queue, preventing web tier overload .

---

## 🛡️ Security: Launch Templates vs Launch Configurations

This is a **timely exam topic** because AWS is **phasing out launch configurations**.

### The Transition

| Aspect | Launch Configuration | Launch Template |
|--------|---------------------|-----------------|
| **Status** | Legacy (being deprecated) | Current/recommended |
| **Support after Oct 2024** | ❌ New accounts cannot create | ✅ Fully supported |
| **Versioning** | ❌ No | ✅ Yes |
| **Mixed instance types** | ❌ No | ✅ Yes |
| **Spot + On-Demand mix** | ❌ No | ✅ Yes |

### How to Force Elastic Beanstalk to Use Launch Templates

According to AWS re:Post, Elastic Beanstalk will automatically use launch templates when you configure **any** of the following :

```yaml
# .ebextensions/launch-template.config
option_settings:
  aws:autoscaling:launchconfiguration:
    DisableIMDSv1: True        # Forces launch template
    RootVolumeType: gp3        # Forces launch template
```

**Why this matters for the exam**:

- Starting **October 1, 2024**, new AWS accounts cannot create launch configurations
- If you see an answer suggesting a "launch configuration" for a new implementation, it's likely wrong
- Elastic Beanstalk will continue using launch configurations for **existing** environments until you modify them

---

## 🏢 Real-World Case Studies

### Case Study 1: Bongo's Bingo - From Manual to Automated Scaling

**The Problem**: Bongo's Bingo's website experienced significant strain during high-demand ticket releases, leading to server errors, slowdowns, and failed purchases. Their existing infrastructure relied heavily on **manual scaling** and vertical scaling .

**The Solution**: Implemented Elastic Beanstalk with Auto Scaling Groups configured for dynamic scaling based on real-time CPU utilization .

**The Outcome**:

- Website uptime increased to **100%** even during peak ticket releases
- Significant reduction in AWS costs (eliminated manual over-provisioning)
- Automated scaling replaced error-prone manual processes

**Why Elastic Beanstalk?** The team containerized their Django application using Docker and deployed to Elastic Beanstalk, which automatically handled the ASG configuration and scaling policies .

### Case Study 2: SUMS - Why They LEFT Elastic Beanstalk (Important!)

**The Problem**: SUMS, a UK-based Students' Union ticketing platform, experienced sudden traffic spikes when tickets went on sale. Their Elastic Beanstalk environment wasn't responding quickly enough to surges .

**The Challenge**: Auto-scaling took ~3 minutes to respond to traffic spikes - too slow for flash sales .

**The Solution**: Migrated from Elastic Beanstalk to **ECS Fargate** with custom CloudWatch metrics (every 10 seconds instead of default 60 seconds). This reduced scaling time from 3 minutes to **under 1 minute** .

**Key Lesson for the Exam**: Elastic Beanstalk is excellent for most workloads, but **latency-sensitive applications requiring sub-minute scaling** may benefit from ECS/Fargate .

---

## 📊 Elastic Beanstalk vs Other Compute Services (Exam Favorite)

This comparison appears **frequently** on the exam .

| Aspect | Elastic Beanstalk | ECS Fargate | EC2 | Lambda |
|--------|-------------------|-------------|-----|--------|
| **Level of Control** | Low-medium | Medium | High | None |
| **Ease of Setup** | Easiest (upload and go) | Moderate | Complex | Easy |
| **Pricing Model** | Pay for underlying resources | Pay per vCPU-hour | Pay for EC2 instances | Pay per invocation |
| **Scaling** | Built-in auto scaling | Configurable auto scaling | Manual or ASG | Automatic |
| **Best For** | Dev teams wanting PaaS | Steady container workloads | Full control needs | Event-driven, spiky traffic |
| **Execution time limit** | Unlimited | Unlimited | Unlimited | 15 minutes max |
| **State management** | Can be stateful | Stateless by design | Fully stateful | Stateless |

### Decision Framework

```
Question: "Which AWS compute service should I use?"

├── Need to deploy a web app FAST with minimal ops? → Elastic Beanstalk
│
├── Running containers but don't want to manage servers? → ECS Fargate
│
├── Need full OS control or specific compliance? → EC2
│
├── Event-driven, short-running (<15 min), spiky traffic? → Lambda
│
└── Have a standard web app but need ultra-fast scaling (<1 min)? → Consider ECS Fargate
```

**Exam Trick from the Decision Tree**: "Lambda wins on spiky traffic and jobs that finish under 15 minutes. It loses on steady high-throughput services where Fargate or EC2 is materially cheaper" .

---

## 📝 Exam Question Bank

### Question 1: Deployment Policy Selection (HIGH PROBABILITY)

**Scenario**: A company has a production web application running on Elastic Beanstalk with 20 EC2 instances behind a load balancer. The application must maintain full capacity during deployments and cannot have any downtime. The team is willing to pay a small additional cost for temporary instances during deployment.

**Question**: Which deployment policy should be used?

A. All at once  
B. Rolling  
C. Rolling with additional batch  
D. Immutable

**Answer**: C

**Explanation**: Rolling with additional batch maintains full capacity by launching new instances before taking old ones offline. Immutable also works but is more expensive (double capacity vs small additional cost). The key phrase is "small additional cost," which points to rolling with additional batch .

---

### Question 2: When to Choose Beanstalk vs EC2

**Scenario**: A startup is building a Python web application. They have no dedicated DevOps team and want to focus on writing code rather than managing infrastructure. The application needs to handle variable traffic and automatically scale.

**Question**: Which AWS service is MOST appropriate?

A. Deploy directly to EC2 with a manually configured Auto Scaling group  
B. Use Elastic Beanstalk with Python platform  
C. Use Lambda with API Gateway  
D. Use ECS Fargate with containers

**Answer**: B

**Explanation**: Elastic Beanstalk is specifically designed for developers who want to focus on code, not infrastructure. It automatically handles capacity provisioning, load balancing, scaling, and monitoring. EC2 requires manual configuration. Lambda has a 15-minute timeout (not suitable for all web apps). Fargate requires containerization .

---

### Question 3: Worker Environments Use Case

**Scenario**: An e-commerce application processes orders in real-time. After an order is placed, the system needs to send a confirmation email and update inventory. These tasks take 30-60 seconds and should not block the user's checkout experience.

**Question**: How should the architect design this?

A. Process everything in the web tier synchronously  
B. Use Elastic Beanstalk worker environments to process tasks from an SQS queue  
C. Use EC2 instances with a cron job  
D. Use Lambda with a 60-second timeout

**Answer**: B

**Explanation**: Elastic Beanstalk worker environments are designed for background processing tasks. They pull messages from an SQS queue, allowing the web tier to respond quickly to users while long-running tasks are processed asynchronously in the background .

---

### Question 4: Launch Template Requirement (TIMELY TOPIC)

**Scenario**: A solutions architect is creating a new Elastic Beanstalk environment in a new AWS account. The company requires support for multiple instance types and a mix of Spot and On-Demand instances.

**Question**: What must the architect do to enable these features?

A. Use a launch configuration with mixed instances policy  
B. Ensure Elastic Beanstalk uses a launch template instead of a launch configuration  
C. Create separate environments for Spot and On-Demand  
D. Use a custom AMI

**Answer**: B

**Explanation**: Launch configurations do NOT support multiple instance types or mixed purchase options. Launch templates are required for these features. Since October 1, 2024, new AWS accounts cannot create launch configurations at all .

---

### Question 5: Blue/Green with Beanstalk

**Scenario**: A company needs to deploy a new version of their application with zero downtime and the ability to instantly roll back if issues are detected. The application must be fully tested in the production environment before receiving any user traffic.

**Question**: Which approach should be used?

A. Immutable deployment policy  
B. Rolling deployment policy  
C. Create a new Elastic Beanstalk environment with the new version and swap CNAMEs  
D. Rolling with additional batch deployment policy

**Answer**: C

**Explanation**: Creating a separate environment and performing a CNAME swap is the blue/green deployment pattern. This allows full testing in an environment identical to production before any user traffic is directed to the new version. Rollback is instant by swapping back to the original environment .

---

## 📊 Quick Reference for Exam Day

| If the exam question mentions... | Think... |
|--------------------------------|----------|
| "Developers don't want to manage servers" | Elastic Beanstalk (PaaS) |
| "Fastest deployment, downtime acceptable" | All At Once |
| "No downtime, maintains full capacity" | Rolling with Additional Batch |
| "Zero downtime, fast rollback, double capacity cost" | Immutable |
| "Both old and new versions run simultaneously" | Rolling deployment |
| "Cannot use launch configurations after Oct 2024" | Launch templates required |
| "Background processing without blocking web tier" | Worker environment |
| "Sudden unpredictable traffic spikes" | Elastic Beanstalk with ASG (or consider Fargate) |
| "Ultra-fast scaling (<1 minute required)" | Consider ECS Fargate over Beanstalk |
| "Promote application version from staging to prod" | Application version promotion |

---

## 🔗 Integration with Other Services

Elastic Beanstalk integrates seamlessly with the AWS ecosystem:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ELASTIC BEANSTALK ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Developer ──► Git Push / AWS CLI / EB CLI                                 │
│                    │                                                        │
│                    ▼                                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  ELASTIC BEANSTALK (PaaS Layer)                                     │   │
│   │  ├── Provisions EC2 instances                                       │   │
│   │  ├── Configures Auto Scaling Group                                  │   │
│   │  ├── Sets up Elastic Load Balancer                                  │   │
│   │  ├── Deploys application version from S3                            │   │
│   │  ├── Configures Security Groups                                     │   │
│   │  └── Launches RDS (if configured)                                   │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                    │                                                        │
│                    ▼                                                        │
│   ┌───────────────┬───────────────┬───────────────┬──────────────────────┐  │
│   │  CloudWatch   │  S3 (code     │  RDS (DB)     │  SNS (notifications) │  │
│   │  (monitoring) │  storage)     │               │                      │  │
│   └───────────────┴───────────────┴───────────────┴──────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Configuration via `.ebextensions`**:

```yaml
# .ebextensions/options.config
option_settings:
  aws:elasticbeanstalk:environment:
    EnvironmentType: LoadBalanced
  
  aws:autoscaling:asg:
    MinSize: 2
    MaxSize: 10
  
  aws:autoscaling:launchconfiguration:
    InstanceType: t3.medium
    EC2KeyName: my-key
    IamInstanceProfile: aws-elasticbeanstalk-ec2-role
  
  aws:elasticbeanstalk:application:
    Application Healthcheck URL: /health
  
  aws:elasticbeanstalk:cloudwatch:logs:
    StreamLogs: true
    DeleteOnTerminate: false
```

---

## 📌 Summary: Elastic Beanstalk for the Four Exam Domains

| Domain | Elastic Beanstalk Application |
|--------|------------------------------|
| **Security** | IAM roles for EC2 instances, security groups, encrypted RDS, Secrets Manager integration, IMDSv2 support |
| **Resilience** | Multi-AZ deployments, Auto Scaling, health checks, immutable deployments |
| **Performance** | Load balancer distribution, right-sized instances, worker environments for background tasks |
| **Cost** | Pay only for underlying resources, auto-scaling adjusts to demand, no additional Beanstalk charges |

---
