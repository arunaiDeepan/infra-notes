# 📘 AWS Batch - SAA-C03 Study Guide

AWS Batch is a fully managed service that enables developers, scientists, and engineers to run hundreds of thousands of batch computing jobs efficiently on AWS. It dynamically provisions the optimal quantity and type of compute resources (e.g., CPU or memory optimized instances) based on the volume and resource requirements of the batch jobs submitted.

Think of it as a "managed queue" for computing. You submit a job, and Batch handles the rest: pulling the job from a queue, spinning up EC2 instances or using AWS Fargate, running the job in a container, and then terminating the resources when the job is complete.

### 🎯 The Core Use Case

The single most important concept for the exam is differentiating **AWS Batch** from a generic EC2 Auto Scaling group.

- **AWS Batch:** Best for **jobs that have a defined start and end**. Examples: payroll processing, financial risk modeling, video transcoding, genomic sequencing, or running a large-scale data conversion. You don't care about the underlying servers, you just need the computation to happen.
- **EC2 Auto Scaling:** Best for **long-running, continuous processes**. Examples: hosting a web application, a microservice, or a corporate website that must stay "always on" to serve traffic.

---

## 1. Design Secure Architectures (30%)

_Protecting data and access at every step._

**How it works:** Batch jobs often process sensitive data (e.g., customer PII, financial records). Security must be configured for the code, the data, and the compute environment.

**Key Services & Configurations:**

- **Instance Metadata Service Version 2 (IMDSv2):** Configure your Batch compute environments to require IMDSv2 to protect against open firewalls and misconfigured services.
- **AWS Identity and Access Management (IAM):**
  - **`Batch Service Role`:** An IAM role that allows the AWS Batch service to call other AWS services (like EC2, ECS) on your behalf to create the compute environment.
  - **`ECS Task Role`:** This is **critical**. It's the role attached to the container running your actual job. It should follow the **least privilege principle**, granting only permissions needed for _that specific job_ (e.g., `s3:GetObject` for input, `s3:PutObject` for output).
- **Amazon ECR Private Repositories:** Store your batch job container images in ECR. Use IAM policies to control who can pull (read) and push (write) images.

**Real-World Example:**
A financial company runs a daily fraud detection batch job.

- **Secure Configuration:** They create two IAM roles. The `BatchServiceRole` has permission to launch EC2 instances. The `FraudJobTaskRole` has only one permission: `s3:GetObject` on the `fraud-input-data` bucket and `s3:PutObject` on the `fraud-output-results` bucket. Even if the job is compromised, it cannot access S3 buckets for payroll or HR.

---

## 2. Design Resilient Architectures (26%)

_Ensuring jobs complete even if there are failures._

**How it works:** Resiliency for batch processing isn't about low latency; it's about **job completion** and **retry logic**. A job that fails halfway must be retried or re-queued.

**Best Practices:**

- **Compute Environment Types:**
  - **Managed:** AWS Batch manages the EC2 instance scaling and environment. This is the default and most resilient as Batch will automatically replace failed instances.
  - **Unmanaged:** You manage the environment. Less resilient unless you have a very specific need.
- **Job Retry Policies:** Define a retry strategy per job definition. If a job fails (e.g., due to a transient S3 error), Batch will automatically re-run it.
  - `attempts`: The number of times to retry (e.g., 3).
  - `evaluateOnExit`: Conditions to retry on (e.g., `onExitCode = 1`).
- **Job Timeouts:** Always set a `timeout` value. If a job hangs due to a bug, the timeout will fail the job and stop you from incurring unnecessary costs on a stuck process.
- **Avoid Single Point of Failure:** Design your jobs to be **idempotent**. If a job is retried, it should produce the same result without causing errors (e.g., "skip if output file already exists").

**Exam Scenario:**

- **Question:** Your video transcoding job keeps failing when EC2 Spot Instances are reclaimed. How do you fix this?
- **Answer:** Configure the job definition's retry strategy. When a Spot Instance is reclaimed, the job fails, Batch re-queues it, and it will run on a new On-Demand or different Spot Instance.

---

## 3. Design High-Performing Architectures (24%)

_Selecting the right resources for the right job._

**How it works:** Performance for Batch means **throughput** (how many jobs finish per hour). The fastest way to run 1,000 jobs is to run them in parallel on 1,000 CPUs.

**Key Strategies:**

- **Job Queues:** You can create multiple queues (e.g., `critical-queue`, `normal-queue`). Prioritize jobs by submitting them to higher-priority queues.
- **Compute Environment Allocation Strategies:**
  - `BEST_FIT` (default for On-Demand): Batch picks the best instance family for the job.
  - `BEST_FIT_PROGRESSIVE`: Batch picks instances that fit, but reuses existing instances for subsequent jobs.
- **Leveraging Spot Instances:** For non-critical, interruptible batch jobs (like data backtesting), use **Spot Instances**. You can get up to 90% cost savings, dramatically increasing performance-per-dollar. Configure your environment to use a mix of On-Demand and Spot.
- **Array Jobs:** This is a high-performance feature. You submit one `Array Job` that launches thousands of child jobs, each processing a different index (e.g., `array-size: 10000`). This is highly efficient for "embarrassingly parallel" problems.

**Best Practice:**

- Use **AWS Fargate** as your compute environment for Batch. Fargate is serverless, meaning you don't manage EC2 clusters. Batch will simply launch a new container for each job, eliminating the need for instance selection and scaling management.

---

## 4. Design Cost-Optimized Architectures (20%)

_Don't pay for idle servers._

**How it works:** The #1 rule of batch processing is **don't keep the servers running when there are no jobs**. AWS Batch excels at this by automatically scaling down to zero instances.

**Cost Optimization Tactics:**

- **Provisioning Models:**
  - **Spot Instances:** Use a **low-priority queue** configured to use 100% Spot Instances. This is perfect for jobs that can be interrupted.
  - **On-Demand:** Use for high-priority, time-sensitive jobs.
  - **Savings Plans:** If you have a constant baseline of Batch jobs running 24/7, purchase Compute Savings Plans to cover the On-Demand portion.
- **Instance Selection:** Match the instance type to the job's memory and CPU needs. Don't run a small, memory-light job on a `r5.4xlarge` (memory-optimized). Use the `BEST_FIT` allocation strategy.
- **Lifecycle:** Set your compute environment's `minimum vCPUs` to **0**. This ensures that when the queue is empty, Batch terminates _all_ EC2 instances, saving 100% of the idle cost.

**Real World Scenario:**
A research lab runs genome sequencing. They submit 10,000 jobs once per week.

- **Cost-Optimized Architecture:**
  1. A `SpotQueue` with a `min_vcpus=0`.
  2. When 10,000 jobs are submitted, Batch scales up to 100 `c5.large` Spot Instances.
  3. The jobs run in 2 hours.
  4. Batch terminates all 100 instances.
  5. **Cost:** For 51 weeks out of the year, the cost is $0. For the one week of processing, cost is 90% cheaper than On-Demand.

---

## 5. AWS Batch Job Lifecycle & States (Critical Exam Focus)

AWS Batch jobs go through a series of states. Knowing the states and how to troubleshoot transitions is a common source of exam questions.

### 🔄 Job States Sequence

1. **`SUBMITTED`**: The job has been defined and sent to the job queue, but it has not been processed or scheduled yet.
2. **`PENDING`**: The job is in the queue, and Batch is verifying dependencies (e.g., waiting on upstream jobs).
3. **`RUNNABLE`**: The job is ready to run and is waiting for compute resources to be available in the compute environment. **(Major Exam Target)**
4. **`STARTING`**: Compute resources are being provisioned, and the container is being scheduled/started.
5. **`RUNNING`**: The container is executing the job command.
6. **`SUCCEEDED`**: The job finished with an exit code of `0`.
7. **`FAILED`**: The job failed with a non-zero exit code or was cancelled/terminated.

### ⚠️ Exam Alert: Jobs Stuck in `RUNNABLE` State

If a scenario describes jobs sitting in the `RUNNABLE` state indefinitely, it means **AWS Batch is unable to allocate the required compute resources**. The most common root causes tested on the exam are:

- **VPC / Networking Issues (EC2 cannot communicate):**
  - The compute environment instances are launched in a **private subnet** with **no route to the internet (missing NAT Gateway)** or **no VPC Endpoints** for ECS, ECR, and CloudWatch.
  - As a result, the ECS agent running on the instances cannot pull the container image from ECR or register with the ECS cluster, preventing the job from leaving `RUNNABLE`.
- **Resource Request Mismatch:**
  - The Job Definition requests more vCPUs or memory than what is supported by the instance types allowed in the Compute Environment (e.g., requesting 16 vCPUs in a compute environment limited to `t3.micro` instances).
- **Compute Environment Limits (`Max vCPUs` = 0):**
  - The compute environment's `maximum vCPUs` parameter is set to `0` or is capped too low, preventing Batch from scaling up instances to run the job.
- **IAM Role/Permissions Issues:**
  - The ECS instance profile role or the Batch service role lacks permissions to provision resources or pull images.

---

### 📝 Exam Question: Scenario-Based

**Question:**
A genomics company uses AWS Batch to run DNA sequence alignment jobs. The workload is fault-tolerant and can be interrupted. The jobs are submitted in large batches (5,000-10,000 jobs) every night and must complete by 8:00 AM the next morning. A Solutions Architect needs to design a solution that minimizes cost while ensuring all jobs finish by the deadline.

**Which combination of steps should the Architect take?** (Select TWO)

A. Set the compute environment’s `minimum vCPUs` to 100 to ensure capacity is always available.
B. Use a Low-Priority Job Queue and configure the compute environment to use only **Spot Instances**.
C. Provision a massive EC2 **On-Demand** Fleet using a Launch Template to guarantee speed.
D. Set the `maximum vCPUs` high enough to handle the peak load and set the `minimum vCPUs` to 0.
E. Store the input data in **Amazon EFS** so all instances can access the files simultaneously.

**Answer & Explanation:**

- **Correct Answers: B & D**
  - **B (Spot Instances):** Since the workload is "fault-tolerant," Spot Instances are the best choice for cost optimization.
  - **D (Min vCPUs = 0):** This ensures the cluster scales down to ZERO instances when no jobs are running, saving money during the day. Setting a high `max vCPUs` allows it to scale up to meet the 8:00 AM deadline.
- **Why the others are wrong:**
  - **A (Min vCPUs = 100):** This would keep 100 instances running 24/7, which is extremely expensive and unnecessary.
  - **C (On-Demand only):** This guarantees completion but costs significantly more than Spot for a fault-tolerant workload.
  - **E (Amazon EFS):** EFS is a file system. While it could work, S3 is the standard, lower-cost, and higher-throughput storage service for Batch input/output. This doesn't solve the cost or speed requirement.

---

### 🏗️ How to Architect AWS Batch with Other Services

A robust AWS Batch architecture rarely stands alone. Here is how it integrates with the ecosystem:

1. **Source:** User uploads a video to **Amazon S3**.
2. **Trigger:** An S3 event notification invokes a **AWS Lambda** function.
3. **Job Submission:** The Lambda function submits a `SubmitJob` request to **AWS Batch** (specifying the Job Definition, Queue, and input file path in S3).
4. **Compute:** Batch pulls the container image from **Amazon ECR**, spins up resources in the customer's **VPC** (or uses Fargate), and runs the trans-coding software.
5. **Output:** The trans-coded video is written back to a different S3 bucket.
6. **Monitoring:** **Amazon CloudWatch** tracks the job status (`RUNNING`, `SUCCEEDED`, `FAILED`).
7. **Notification:** On job completion, Batch can send a notification to **Amazon SNS**, alerting the user that their video is ready.

---
