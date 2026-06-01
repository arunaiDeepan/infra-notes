# 📘 AWS Lambda - Complete SAA-C03 Study Guide

> AWS Lambda is the **heart of serverless** on AWS. It lets you run code without provisioning or managing servers—you pay only for the compute time you consume. For the SAA-C03 exam, Lambda appears in **nearly every scenario** involving event-driven architectures, real-time processing, and cost optimization. This file is the broad overview; use the linked deep-dive files for each subtopic.

See also: [Lambda Core Concepts & Architecture](Lambda%20Core%20Concepts%20%26%20Architecture.md) · [Lambda Invocation Modes](Lambda%20Invocation%20Modes.md) · [Lambda Cold Starts & Performance](Lambda%20Cold%20Starts%20%26%20Performance.md) · [Lambda Concurrency & Scaling](Lambda%20Concurrency%20%26%20Scaling.md) · [Lambda Scenario Questions](Lambda%20Scenario%20Questions.md) · [Lambda edge](Lambda%20edge.md)

---

## Table of Contents

- [🎯 Core Concept: What is AWS Lambda?](#-core-concept-what-is-aws-lambda)
- [🆚 Lambda vs EC2: The Exam's Favorite Comparison](#-lambda-vs-ec2-the-exams-favorite-comparison)
- [📊 Lambda Limitations (Critical for Exam)](#-lambda-limitations-critical-for-exam)
- [🔥 Cold Starts - Deep Dive](#-cold-starts---deep-dive)
- [💰 Memory & Performance Tuning (Critical for Cost)](#-memory--performance-tuning-critical-for-cost)
- [🔌 Event Sources - How Lambda Gets Triggered](#-event-sources---how-lambda-gets-triggered)
- [🔐 Security Best Practices](#-security-best-practices)
- [📈 Monitoring Lambda - What You Must Know](#-monitoring-lambda---what-you-must-know)
- [📦 Lambda Layers - Code Reuse](#-lambda-layers---code-reuse)
- [🔁 Versions vs Aliases - Deployment Management](#-versions-vs-aliases---deployment-management)
- [🔄 Destinations for Asynchronous Invocations](#-destinations-for-asynchronous-invocations)
- [🏗️ Real-World Architecture Patterns](#-real-world-architecture-patterns)
- [💡 Cost Optimization for Lambda](#-cost-optimization-for-lambda)
- [📝 Exam Question Bank](#-exam-question-bank)
- [📊 Quick Reference for Exam Day](#-quick-reference-for-exam-day)
- [🔗 Summary: Lambda's Role in the Four Exam Domains](#-summary-lambdas-role-in-the-four-exam-domains)

---

## 🎯 Core Concept: What is AWS Lambda?

**AWS Lambda is a Function-as-a-Service (FaaS)** platform that runs your code in response to events and automatically manages the underlying compute resources .

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HOW LAMBDA WORKS (Mental Model)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   1. UPLOAD CODE ──► 2. EVENT OCCURS ──► 3. LAMBDA RUNS ──► 4. SCALES      │
│                                                                             │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌──────────┐ │
│   │ Your Code   │────►│ S3 upload   │────►│ Execute    │────►│ Auto     │ │
│   │ (Python,    │     │ API call    │     │ handler()  │     │ scales   │ │
│   │ Node.js,    │     │ SQS message │     │            │     │ to zero  │ │
│   │ Go, Java)   │     │ Schedule    │     │            │     │ when idle│ │
│   └─────────────┘     └─────────────┘     └─────────────┘     └──────────┘ │
│                                                                             │
│   KEY INSIGHT: You don't see, manage, or log into servers.                 │
│                Lambda handles everything.                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

[⬆ Back to top](#table-of-contents)

## 🆚 Lambda vs EC2: The Exam's Favorite Comparison

This is **guaranteed** to appear on your exam in some form .

| Aspect                | AWS Lambda                        | Amazon EC2                             |
| --------------------- | --------------------------------- | -------------------------------------- |
| **Server management** | AWS manages everything            | You manage (patching, scaling)         |
| **Scaling**           | Automatic, from 0 to thousands    | Manual or Auto Scaling groups          |
| **Pricing**           | Per invocation + compute duration | Per second (or hour) regardless of use |
| **Execution time**    | **Max 15 minutes**                | Unlimited                              |
| **State**             | Stateless by default              | Can be stateful                        |
| **Storage**           | Ephemeral (512 MB - 10 GB tmp)    | Persistent EBS volumes                 |
| **Cold starts**       | Yes (initialization delay)        | No                                     |
| **Use cases**         | Event-driven, short-running tasks | Long-running, stateful applications    |

### Decision Framework for the Exam

```
Question: "Should I use Lambda or EC2?"

LAMBDA if:
├── Execution time < 15 minutes
├── Workload is sporadic (not always running)
├── Event-driven (S3, API Gateway, SQS, DynamoDB Streams)
├── You want to minimize operational overhead
└── Cost optimization for variable traffic

EC2 if:
├── Execution time > 15 minutes
├── Need persistent state on local disk
├── Requires specific OS customization
├── Long-running, steady-state workloads
└── Need GPU (Lambda doesn't support GPUs)
```

---

[⬆ Back to top](#table-of-contents)

## 📊 Lambda Limitations (Critical for Exam)

Knowing Lambda's **constraints** helps you identify when another service is more appropriate .

| Limitation                | Value                             | Implication                               |
| ------------------------- | --------------------------------- | ----------------------------------------- |
| **Timeout**               | 15 minutes (900 seconds) MAX      | Long-running batch jobs need EC2 or Batch |
| **Memory**                | 128 MB - 10,240 MB (10 GB)        | Memory = proportional CPU allocation      |
| **Ephemeral storage**     | 512 MB - 10,240 MB (/tmp)         | For temporary files only                  |
| **Deployment package**    | 50 MB (zipped), 250 MB (unzipped) | Large dependencies go in Layers           |
| **Concurrent executions** | 1,000 (default soft limit)        | Can request increase                      |
| **Request payload**       | 6 MB (sync), 256 KB (async)       | Large payloads need S3                    |
| **Environment variables** | 4 KB total                        | For configuration only (not secrets!)     |

**Exam Trick**: If a scenario requires processing that exceeds these limits, Lambda is NOT the right choice. Look for answers using Batch, Fargate, or EC2 instead .

---

[⬆ Back to top](#table-of-contents)

## 🔥 Cold Starts - Deep Dive

A **cold start** happens when Lambda creates a new execution environment for a function that hasn't been used recently. The runtime initializes your code before executing the handler .

### Cold Start Times by Runtime (2026 Benchmarks)

| Runtime                    | Cold Start (p50) | Cold Start (p99) | Best For                      |
| -------------------------- | ---------------- | ---------------- | ----------------------------- |
| **Rust**                   | 50-80ms          | 100-200ms        | Fastest, low-level control    |
| **Go**                     | 50-100ms         | 150-250ms        | High-performance APIs         |
| **Node.js 22**             | 200-350ms        | 600ms-1s         | Web APIs, JSON processing     |
| **Python 3.13**            | 200-400ms        | 800ms-1.2s       | Data processing, ML inference |
| **Java 21** (no SnapStart) | 2-5s             | 6-10s            | Enterprise workloads          |
| **Java 21** (+SnapStart)   | 90-140ms         | 200-400ms        | Dramatic improvement          |

Source:

### Strategies to Reduce Cold Starts

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COLD START MITIGATION STRATEGIES                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. USE ARM64 (Graviton2/3)                                                │
│     └── 20% cheaper AND 15-40% faster cold starts              │
│                                                                             │
│  2. MINIMIZE PACKAGE SIZE                                                   │
│     ├── Use Lambda Layers for large dependencies                            │
│     ├── Tree-shake/bundle JavaScript (esbuild)                             │
│     └── Remove unused imports                                              │
│                                                                             │
│  3. PROVISIONED CONCURRENCY (PAID FEATURE)                                  │
│     ├── Keeps execution environments "warm"                                 │
│     ├── Cost: ~$80-120/month for 10 concurrent instances       │
│     └── Only for latency-critical, high-traffic endpoints                   │
│                                                                             │
│  4. LAMBDA SNAPSTART (JAVA ONLY)                                            │
│     ├── Takes a snapshot of initialized Java function                      │
│     ├── Restores from snapshot on cold start (not full init)               │
│     └── Reduces Java cold starts from 6s to ~200ms             │
│                                                                             │
│  5. KEEP FUNCTIONS WARM (WORKAROUND)                                        │
│     └── CloudWatch Event every 5 minutes to invoke function                │
│         (Not recommended - costs money, better to accept cold starts)      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Exam Keyword Recognition**: If the question mentions "users experience latency on first request" or "function hasn't been invoked recently" → **Cold start** problem. Solution depends on runtime:

- Java → **Lambda SnapStart**
- High-traffic critical path → **Provisioned Concurrency**
- General optimization → **ARM64 + smaller deployment package**

---

[⬆ Back to top](#table-of-contents)

## 💰 Memory & Performance Tuning (Critical for Cost)

Lambda allocates **CPU proportionally to memory**. More memory = more CPU = faster execution. Sometimes increasing memory reduces BOTH execution time AND cost .

### The Counterintuitive Truth

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MEMORY vs COST RELATIONSHIP                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Real example (data processing function):                                  │
│                                                                             │
│   128MB: 3000ms execution, $0.0000625 per invocation                        │
│   512MB: 800ms execution,  $0.0000667 per invocation  (7% more expensive)   │
│   1024MB: 400ms execution, $0.0000667 per invocation  (same cost!)          │
│                                                                             │
│   THE SWEET SPOT: 512MB - 1024MB provides best cost-performance │
│                                                                             │
│   Going below 256MB rarely saves money because execution time increases     │
│   proportionally.                                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### AWS Lambda Power Tuning

This open-source tool helps you find the optimal memory setting:

- Deploys a Step Function that runs your function at different memory settings
- Charts execution time vs cost
- Free and highly recommended for production functions

---

[⬆ Back to top](#table-of-contents)

## 🔌 Event Sources - How Lambda Gets Triggered

Lambda can be triggered by **over 200 AWS services**. For the exam, focus on these :

### Synchronous Invocations (Client waits for response)

| Event Source                 | Use Case                  |
| ---------------------------- | ------------------------- |
| **API Gateway**              | REST APIs, HTTP endpoints |
| **ELB (ALB)**                | Web applications          |
| **CloudFront (Lambda@Edge)** | CDN edge processing       |

### Asynchronous Invocations (Lambda queues, client doesn't wait)

| Event Source        | Use Case                                            |
| ------------------- | --------------------------------------------------- |
| **S3**              | Object creation (image resizing, video transcoding) |
| **SNS**             | Pub/sub notifications                               |
| **EventBridge**     | Scheduled cron jobs, event routing                  |
| **CloudWatch Logs** | Log processing                                      |

### Stream/Poll-based Invocations

| Event Source             | Use Case                             |
| ------------------------ | ------------------------------------ |
| **DynamoDB Streams**     | Real-time changes to DynamoDB tables |
| **Kinesis Data Streams** | Real-time data processing            |
| **SQS**                  | Decoupled application components     |

**Exam Trick**: SQS with Lambda is a **common pattern** for decoupling. Lambda polls the SQS queue and processes messages. If the Lambda function fails, the message remains in the queue (depending on redrive policy) .

### Real-World Example: Financial Transaction Processing

This exact scenario appeared in SAA-C03 practice exams :

> **Requirement**: Stream millions of financial transactions in near-real-time, remove sensitive data, store in DynamoDB for low-latency retrieval, and share with multiple internal apps.

**Correct Architecture**:

```
Kinesis Data Streams ──► Lambda (remove PII) ──► DynamoDB
                              │
                              └──► Other apps consume from Kinesis stream
```

**Why this works**:

- Kinesis Data Streams handles high-volume, near-real-time data
- Lambda processes each transaction to remove sensitive data
- DynamoDB provides low-latency retrieval
- Multiple applications can consume from the same Kinesis stream

**Why NOT other options**:

- DynamoDB doesn't have built-in data redaction
- S3 doesn't provide low-latency retrieval
- S3 batch processing isn't near-real-time

---

[⬆ Back to top](#table-of-contents)

## 🔐 Security Best Practices

### IAM Roles (Critical!)

Every Lambda function has **two** IAM roles, just like AWS Batch :

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TWO IAM ROLES FOR LAMBDA                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EXECUTION ROLE (lambda.amazonaws.com)                                      │
│  ├── What: Allows Lambda service to operate                                 │
│  ├── Permissions needed:                                                   │
│  │   ├── logs:CreateLogGroup, logs:PutLogEvents (CloudWatch)              │
│  │   ├── ec2:... (if VPC-attached)                                        │
│  │   └── xray:PutTraceSegments (if using X-Ray)                           │
│  └── NEVER give this role unnecessary permissions                          │
│                                                                             │
│  FUNCTION ROLE (Your code's identity)                                       │
│  ├── What: Permissions for YOUR code to call AWS services                  │
│  ├── Example: s3:GetObject, dynamodb:PutItem, sns:Publish                  │
│  └── Follow LEAST PRIVILEGE: only what your function needs     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Secrets Management

**NEVER put secrets in environment variables** (plaintext) .

**Correct approach**:

```python
import json
import boto3
from functools import lru_cache

@lru_cache(maxsize=1)
def get_db_credentials():
    """Cache secrets in memory across invocations"""
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='prod/db-credentials')
    return json.loads(response['SecretString'])

# Called once, cached for execution environment lifetime
credentials = get_db_credentials()
```

**Options for secrets**:

1. **AWS Secrets Manager** - Best for rotating secrets, cross-account access
2. **Parameter Store (SecureString)** - Good for configuration, lower cost
3. **Lambda Extensions** - Cache secrets for better performance

### VPC Considerations

Only put Lambda in a VPC if it needs to access **private resources** (RDS, ElastiCache, internal services) .

**Key points for exam**:

- VPC-attached Lambdas need an **execution role** with `ec2:CreateNetworkInterface`
- Hyperplane ENI resolved most cold start issues (but still slightly slower)
- Use private subnets (not public) for VPC-attached functions

---

[⬆ Back to top](#table-of-contents)

## 📈 Monitoring Lambda - What You Must Know

### CloudWatch Metrics (Automatic)

| Metric               | What It Measures                | Alarm When                 |
| -------------------- | ------------------------------- | -------------------------- |
| `Invocations`        | Number of times function called | -                          |
| `Duration`           | Execution time (milliseconds)   | > threshold (e.g., 1000ms) |
| `Errors`             | Failed invocations (4xx/5xx)    | > 0                        |
| `Throttles`          | Concurrency limit exceeded      | > 0                        |
| `IteratorAge`        | Stream processing lag           | > threshold                |
| `InitDuration` (NEW) | Cold start initialization time  | > threshold                |

### New Billing Change (August 1, 2025)

**Important for exam**: Starting August 1, 2025, AWS bills for the **INIT phase** (cold starts) for managed runtimes. Previously, only the INVOKE phase was billed .

**Impact**: Most users see minimal impact (cold starts <1% of invocations). Monitor `InitDuration` CloudWatch metric to optimize cold start costs .

### CloudWatch Logs

Lambda automatically sends logs to CloudWatch Logs:

- Log group: `/aws/lambda/{function-name}`
- Include `START`, `END`, `REPORT` lines
- REPORT lines include billing duration, memory used, and init duration

### AWS X-Ray for Tracing

Enable X-Ray to trace requests across distributed services:

- See end-to-end request path
- Identify bottlenecks
- Debug performance issues

---

[⬆ Back to top](#table-of-contents)

## 📦 Lambda Layers - Code Reuse

**What they are**: Distribution mechanism for libraries, custom runtimes, and other dependencies.

**Benefits**:

- Share code across multiple functions
- Keep deployment packages small (<50MB)
- Version layers independently

**Layer size limits**: Unzipped layers count toward function's 250MB limit.

**Example layer structure**:

```
layer.zip
└── python/
    ├── pandas/
    ├── numpy/
    └── requests/
```

---

[⬆ Back to top](#table-of-contents)

## 🔁 Versions vs Aliases - Deployment Management

| Concept     | Description                                | Use Case                                       |
| ----------- | ------------------------------------------ | ---------------------------------------------- |
| **Version** | Immutable snapshot of function code/config | Production deployment, rollback point          |
| **Alias**   | Pointer to a specific version (can change) | Blue/green deployments, environment separation |

**Example**:

- `$LATEST` - Always the latest (development)
- Version `42` - Production-proven code
- Alias `PROD` → Version `42`
- Update alias to version `43` for deployment

**Exam Trick**: Weighted aliases can route percentage of traffic (e.g., 95% to version 42, 5% to version 43) for canary deployments.

---

[⬆ Back to top](#table-of-contents)

## 🔄 Destinations for Asynchronous Invocations

When a function is invoked **asynchronously**, you can configure destinations for success/failure records:

| Destination Type | Use Case                             |
| ---------------- | ------------------------------------ |
| **SQS**          | Queue failed events for reprocessing |
| **SNS**          | Send notifications on failure        |
| **Lambda**       | Chain functions                      |
| **EventBridge**  | Route events to multiple targets     |

**Exam Scenario**: "Failed Lambda invocations need to be stored for later analysis" → Configure `OnFailure` destination to **SQS** or **SNS**.

---

[⬆ Back to top](#table-of-contents)

## 🏗️ Real-World Architecture Patterns

### Pattern 1: Serverless REST API

```
API Gateway (REST/HTTP) ──► Lambda (business logic) ──► DynamoDB
                              │
                              └──► Secrets Manager (credentials)

Authorization: IAM, Cognito, or Lambda Authorizer
```

### Pattern 2: Event-Driven Data Processing

```
S3 upload ──► Lambda (trigger) ──► SQS queue ──► Lambda (processor) ──► DynamoDB
                                    (buffer for variable rate)
```

**Why SQS in the middle**: If the uploads happen faster than the processor can handle, SQS acts as a buffer .

### Pattern 3: Scheduled Jobs (Cron)

```
EventBridge (cron schedule) ──► Lambda ──► API / Database
```

**Example**: Run daily report generation at 1 AM.

### Pattern 4: Stream Processing (Real-time)

```
Kinesis Data Stream ──► Lambda (per-record processing) ──► S3 / DynamoDB
                              │
                              └──► Use batch window (up to 300s) for batching
```

---

[⬆ Back to top](#table-of-contents)

## 💡 Cost Optimization for Lambda

| Strategy                          | Savings Potential        | Implementation                               |
| --------------------------------- | ------------------------ | -------------------------------------------- |
| **Use ARM64 (Graviton)**          | 20%                      | One-line config change                       |
| **Right-size memory**             | 10-50%                   | Lambda Power Tuning tool                     |
| **Batch SQS messages**            | Reduces invocation count | `BatchSize=10`, `MaximumBatchingWindow=30s`  |
| **Minimize duration**             | Proportional             | Optimize code, use faster runtime            |
| **Avoid Lambda for steady-state** | Significant              | Use Fargate/EC2 if invoked every second 24/7 |

### Batching SQS Example (CloudFormation/SAM)

```yaml
Events:
  SQSTrigger:
    Type: SQS
    Properties:
      Queue: !GetAtt MyQueue.Arn
      BatchSize: 10 # 10 messages per invocation
      MaximumBatchingWindowInSeconds: 30 # Wait up to 30s to fill batch
```

**Result**: 10x reduction in invocation count .

---

[⬆ Back to top](#table-of-contents)

## 📝 Exam Question Bank

### Question 1: Lambda vs EC2 Selection

**Scenario**: A company needs to run a process that pulls data from an API every 5 minutes, transforms it, and stores it in DynamoDB. The process takes about 30 seconds to complete.

**Question**: Which compute service is MOST cost-effective?

A. EC2 t4g.nano running 24/7  
B. Lambda with 30-second timeout  
C. Fargate spot task  
D. Batch with Spot Instances

**Answer**: B

**Explanation**: The workload is infrequent (every 5 minutes) and short-running (30 seconds). Lambda's per-invocation pricing makes it significantly cheaper than keeping an EC2 instance running 24/7 .

---

### Question 2: Cold Start Problem

**Scenario**: A Java-based Lambda function is part of a customer-facing API. The first request of the hour takes 6 seconds to respond, but subsequent requests take 200ms. Customers are complaining about the delay.

**Question**: What is the MOST cost-effective solution?

A. Migrate to EC2 instances with Auto Scaling  
B. Enable Provisioned Concurrency with 10 concurrent instances  
C. Enable Lambda SnapStart  
D. Keep the function warm with a CloudWatch event every minute

**Answer**: C

**Explanation**: Lambda SnapStart is designed specifically for Java cold starts. It reduces cold start time from 6 seconds to ~200ms at no additional cost (unlike Provisioned Concurrency, which would cost ~$80-120/month) .

---

### Question 3: SQS Integration

**Scenario**: An e-commerce application uses Lambda to process orders. During flash sales, orders are being throttled because Lambda concurrency limits are exceeded. Orders cannot be lost.

**Question**: What should be added to the architecture?

A. Increase Lambda concurrency limit  
B. Add an SQS queue between the event source and Lambda  
C. Use Provisioned Concurrency  
D. Switch to EC2 instances for order processing

**Answer**: B

**Explanation**: SQS acts as a buffer during traffic spikes. Lambda will poll the queue at its concurrency limit, and messages remain in the queue until processed. No messages are lost. Option A just shifts the problem (service quota). Option C is expensive. Option D adds management overhead .

---

### Question 4: VPC Considerations

**Scenario**: A Lambda function needs to read from an RDS database in a private subnet. The function currently times out when trying to connect.

**Question**: What is the FIRST thing to check?

A. RDS security group inbound rules  
B. Lambda execution role permissions  
C. Lambda memory configuration  
D. Lambda timeout setting

**Answer**: A

**Explanation**: When Lambda is VPC-attached, it gets an ENI in the subnet. The most common issue is the RDS security group not allowing inbound traffic from the Lambda function's security group or CIDR range.

---

### Question 5: Asynchronous vs Synchronous

**Scenario**: A user uploads a profile picture to S3. The system needs to resize the image and update the user's profile in DynamoDB. The user doesn't need to wait for this to complete.

**Question**: Which invocation type should be used?

A. Synchronous (RequestResponse)  
B. Asynchronous (Event)  
C. DryRun  
D. Stream-based

**Answer**: B

**Explanation**: Asynchronous invocation (Event) is appropriate when the caller doesn't need to wait for the result. S3 events naturally invoke Lambda asynchronously, which is perfect for this use case.

---

[⬆ Back to top](#table-of-contents)

## 📊 Quick Reference for Exam Day

| If the question mentions...             | Think...                                                 |
| --------------------------------------- | -------------------------------------------------------- |
| "First request is slow"                 | Cold start → SnapStart (Java) or Provisioned Concurrency |
| "Function runs every 5 minutes"         | Lambda (cost-effective for infrequent workloads)         |
| "Process takes 20 minutes"              | NOT Lambda (15 min max) → Batch or Fargate               |
| "SQS messages piling up"                | Increase concurrency OR batch size                       |
| "Order processing cannot lose messages" | Dead Letter Queue (DLQ) or SQS with Lambda               |
| "Memory-intensive but time is short"    | Increase memory (512-1024MB sweet spot)                  |
| "Deployment package >50MB"              | Lambda Layers for dependencies                           |
| "Share code across functions"           | Lambda Layers                                            |
| "Canary deployment"                     | Weighted aliases                                         |
| "High-volume steady-state"              | NOT Lambda → Fargate or EC2                              |
| "Real-time stream processing"           | Kinesis → Lambda                                         |
| "Schedule a job"                        | EventBridge → Lambda                                     |
| "Secrets rotation"                      | Secrets Manager (not environment variables)              |
| "Java cold start"                       | Lambda SnapStart                                         |
| "20% cheaper, faster cold starts"       | ARM64 (Graviton) architecture                            |

---

[⬆ Back to top](#table-of-contents)

## 🔗 Summary: Lambda's Role in the Four Exam Domains

| Domain          | Lambda Application                                                                                           |
| --------------- | ------------------------------------------------------------------------------------------------------------ |
| **Security**    | IAM roles (separate execution vs function roles), Secrets Manager for credentials, VPC for private resources |
| **Resilience**  | Asynchronous invocations with DLQ, SQS buffering, retry policies (2 attempts default)                        |
| **Performance** | Right-size memory (512-1024MB sweet spot), ARM64 architecture, SnapStart for Java                            |
| **Cost**        | Pay-per-invocation + duration, ARM64 (20% cheaper), batching SQS messages, scale to zero                     |

---

[⬆ Back to top](#table-of-contents)
