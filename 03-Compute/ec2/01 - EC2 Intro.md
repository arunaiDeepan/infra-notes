# 📘 Amazon EC2 - SAA-C03 Complete Study Guide

Amazon EC2 (Elastic Compute Cloud) is the **fundamental compute service** in AWS. It provides secure, resizable compute capacity in the cloud.

> **EC2 + ASG series:** [01 - EC2 Intro](01%20-%20EC2%20Intro.md) · [02 - EC2 Instance Types Deep Dive](02%20-%20EC2%20Instance%20Types%20Deep%20Dive.md) · [03 - EC2 Storage Deep Dive](03%20-%20EC2%20Storage%20Deep%20Dive.md) · [04 - EC2 Networking, Placement & Metadata Deep Dive](04%20-%20EC2%20Networking%2C%20Placement%20%26%20Metadata%20Deep%20Dive.md) · [05 - EC2 Pricing & Purchasing Options Deep Dive](05%20-%20EC2%20Pricing%20%26%20Purchasing%20Options%20Deep%20Dive.md) · [06 - EC2 Auto Scaling (ASG)](06%20-%20EC2%20Auto%20Scaling%20%28ASG%29.md) · [07 - ASG Architecture & Advanced Deep Dive](07%20-%20ASG%20Architecture%20%26%20Advanced%20Deep%20Dive.md) · [08 - EC2 & ASG Architecture Patterns & Examples](08%20-%20EC2%20%26%20ASG%20Architecture%20Patterns%20%26%20Examples.md) · [09 - EC2 & ASG Scenario Questions](09%20-%20EC2%20%26%20ASG%20Scenario%20Questions.md) · [10 - EC2 & ASG Important Facts & Cheat Sheet](10%20-%20EC2%20%26%20ASG%20Important%20Facts%20%26%20Cheat%20Sheet.md)

---

## Table of Contents

- [🎯 EC2 Core Concepts - The Foundation](#-ec2-core-concepts---the-foundation)
- [🏗️ EC2 Instance Types - The Complete Breakdown](#-ec2-instance-types---the-complete-breakdown)
- [📀 Storage Options - EBS vs Instance Store vs EFS](#-storage-options---ebs-vs-instance-store-vs-efs)
- [🔐 Security Groups & Network ACLs - The Firewall Layer](#-security-groups--network-acls---the-firewall-layer)
- [💰 EC2 Pricing Models - Exam Critical](#-ec2-pricing-models---exam-critical)
- [🔄 User Data & Metadata - Bootstrapping EC2](#-user-data--metadata---bootstrapping-ec2)
- [📈 EC2 Auto Scaling - The Complete Picture](#-ec2-auto-scaling---the-complete-picture)
- [🔗 EC2 with Other Services - Integration Architecture](#-ec2-with-other-services---integration-architecture)
- [💡 Cost Optimization with EC2](#-cost-optimization-with-ec2)
- [🔥 High Performance Configurations](#-high-performance-configurations)
- [🛡️ Resilience Best Practices](#-resilience-best-practices)
- [📝 EC2 Exam Question Bank](#-ec2-exam-question-bank)
- [📊 EC2 Quick Reference for Exam Day](#-ec2-quick-reference-for-exam-day)

> Deeper dives live in the companion files above — this intro is the map; [instance types](02%20-%20EC2%20Instance%20Types%20Deep%20Dive.md), [storage](03%20-%20EC2%20Storage%20Deep%20Dive.md), [pricing](05%20-%20EC2%20Pricing%20%26%20Purchasing%20Options%20Deep%20Dive.md), and [Auto Scaling](06%20-%20EC2%20Auto%20Scaling%20%28ASG%29.md) each get their own deep-dive.

---

## 🎯 EC2 Core Concepts - The Foundation

### What is EC2?

EC2 allows you to rent virtual servers (called "instances") in AWS's data centers. You have full control over the operating system, software, and configuration.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EC2 MENTAL MODEL                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   EC2 Instance = A virtual server in the cloud                             │
│                                                                             │
│   You configure:                                                            │
│   ├── AMI (Amazon Machine Image) = Operating System + pre-installed apps   │
│   ├── Instance Type = CPU, Memory, Network (t3.micro, m5.large, etc.)      │
│   ├── Storage = EBS volumes (persistent) or Instance Store (ephemeral)     │
│   ├── Security Group = Virtual firewall (allow/deny traffic)               │
│   └── Key Pair = SSH access (Linux) or RDP admin password (Windows)        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

[⬆ Back to top](#table-of-contents)

## 🏗️ EC2 Instance Types - The Complete Breakdown

AWS has **hundreds** of instance types organized into families. For the exam, you need to know WHICH FAMILY to choose for WHICH WORKLOAD.

### Instance Family Naming Convention

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EC2 INSTANCE NAMING CONVENTION                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Example: m5.2xlarge                                                      │
│            │ │  │                                                           │
│            │ │  └─── Size (2xlarge = 8 vCPUs, 32 GB RAM)                  │
│            │ └────── Generation (5th generation of this family)            │
│            └──────── Family (m = General Purpose)                          │
│                                                                             │
│   Common Families:                                                          │
│   ├── t - Burstable (T2, T3, T4g)                                         │
│   ├── m - General Purpose (M5, M6g, M7g)                                   │
│   ├── c - Compute Optimized (C5, C6g, C7g)                                 │
│   ├── r - Memory Optimized (R5, R6g, R7g)                                  │
│   ├── i - High I/O (I3, I4i) - Local NVMe SSD                              │
│   ├── d - Dense Storage (D3, D3en) - HDD storage                           │
│   ├── g - GPU (G4dn, G5) - Graphics/ML                                     │
│   ├── p - GPU (P3, P4d) - ML/Training                                      │
│   ├── x - Large Memory (X1, X2idn) - SAP HANA                              │
│   └── z - High Frequency (Z1d) - Fast CPU                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Detailed Family Reference

| Family | Sub-Family | Use Case | Example Instance | Exam Trick |
|--------|------------|----------|------------------|------------|
| **General Purpose (t, m)** | **T (Burstable)** | Dev/test, small DBs, web servers with variable load | `t3.micro` (free tier) | CPU credits! T2/T3 unlimited mode |
| | **M** | Production web apps, app servers, small DBs | `m5.large` | Most common production choice |
| **Compute Optimized (c)** | **C5/C7g** | Batch processing, ad serving, gaming servers | `c5.4xlarge` | High vCPU-to-memory ratio |
| **Memory Optimized (r, x, z)** | **R** | Production DBs (PostgreSQL, MySQL), caching | `r5.large` | High memory-to-vCPU ratio |
| | **X** | SAP HANA, large in-memory DBs | `x1e.32xlarge` | Up to 4 TB RAM |
| | **Z** | High-frequency trading, EDA tools | `z1d.6xlarge` | 4.0 GHz sustained |
| **Storage Optimized (i, d, im)** | **I** | NoSQL DBs (Cassandra, MongoDB), data warehousing | `i3.8xlarge` | Local NVMe SSD (high IOPS) |
| | **D** | HDFS, MapReduce, distributed file systems | `d3.8xlarge` | Local HDD (high density) |
| **Accelerated Computing (g, p)** | **G** | Graphics rendering, ML inference | `g4dn.xlarge` | NVIDIA T4 GPU |
| | **P** | ML training, HPC | `p4d.24xlarge` | NVIDIA A100 GPU |

### Burstable Instances (T Family) - Critical for Exam

T instances are **the most cost-effective** for workloads that don't run at 100% CPU constantly.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BURSTABLE INSTANCES (T2, T3, T4g)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   HOW IT WORKS:                                                             │
│                                                                             │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                │
│   │  IDLE (10%)  │───►│  CREDITS     │───►│ BURST (100%) │                │
│   │  CPU usage   │    │  ACCUMULATE  │    │  CPU usage   │                │
│   └──────────────┘    └──────────────┘    └──────────────┘                │
│                                                                             │
│   Base Performance = 10-20% (varies by size)                               │
│                                                                             │
│   Each vCPU earns credits:                                                  │
│   ├── T3 - 24 credits per hour (unused capacity becomes credits)          │
│   ├── T2 - 6 credits per hour (T2 is older, less efficient)               │
│   └── Each credit = 1 vCPU running at 100% for 1 minute                   │
│                                                                             │
│   TWO MODES:                                                                │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ STANDARD MODE                                                        │  │
│   │ ├── Burst only when credits available                               │  │
│   │ ├── Performance limited by credit balance                           │  │
│   │ └── Best for: Dev/test, unpredictable workloads                     │  │
│   ├─────────────────────────────────────────────────────────────────────┤  │
│   │ UNLIMITED MODE                                                       │  │
│   │ ├── Can burst beyond credits (pay surcharge)                        │  │
│   │ ├── CPU credits spent first, then pays $0.05 per vCPU-hour          │  │
│   │ ├── Can't surge for more than 24 hours                              │  │
│   │ └── Best for: Production where occasional bursts needed             │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   T3 vs T2 Differences:                                                     │
│   ├── T3 has higher base performance per vCPU                             │
│   ├── T3 earns credits FASTER (24/hr vs 6/hr)                             │
│   ├── T3 supports Unlimited mode (T2 does not)                            │
│   └── T3 uses newer hardware (faster)                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Exam Question Pattern**:
> "A web server uses 10% CPU most of the day but spikes to 80% for 15 minutes every hour. Which instance type and configuration is most cost-effective?"
> **Answer**: T3 instance with Unlimited mode enabled.

### Graviton Processors (AWS ARM-based)

AWS builds its own ARM-based processors called **Graviton**.

| Generation | Instance Families | Performance vs x86 | Savings |
|------------|-------------------|-------------------|---------|
| Graviton2 (G) | M6g, C6g, R6g, T4g | 40% better price/performance | ~20% cheaper |
| Graviton3 (G) | M7g, C7g, R7g | 25% better performance | Same savings |

**When to use Graviton**:

- Applications recompiled for ARM (Go, Rust, Java, Python, Node.js work)
- Containerized workloads
- Web servers, microservices

**When NOT to use Graviton**:

- Windows workloads (Windows doesn't support ARM)
- Proprietary x86 binaries
- Legacy applications that can't be recompiled

---

[⬆ Back to top](#table-of-contents)

## 📀 Storage Options - EBS vs Instance Store vs EFS

### Comparison Matrix

| Aspect | EBS (Elastic Block Store) | Instance Store | EFS (Elastic File System) |
|--------|--------------------------|----------------|---------------------------|
| **Persistence** | ✅ Survives instance termination | ❌ Lost on stop/termination | ✅ Survives instance termination |
| **Attachment** | Single instance (multi-attach for some) | Single instance | Many instances (NFS v4.1) |
| **Use Case** | OS drives, persistent DB storage | Cache, temp data, scratch space | Shared storage, content management |
| **Max Size** | 64 TiB per volume | Varies (up to 30 TB) | Unlimited (PB scale) |
| **Performance** | Up to 256,000 IOPS (io2) | Millions of IOPS | Bursting to 10+ GB/s |
| **Replication** | Within AZ (automatic) | Single physical disk | Across AZs (regional) |
| **Cost Model** | GB-month + IOPS | Included in instance price | GB-month (more expensive) |

### EBS Volume Types - Exam Critical

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EBS VOLUME TYPES                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SSD-BASED (Transaction-intensive workloads)                                │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ io2 Block Express (NEW - CRITICAL FOR EXAM)                           │ │
│  │ ├── Max IOPS: 256,000                                                │ │
│  │ ├── Max Throughput: 4,000 MB/s                                       │ │
│  │ ├── Max Size: 64 TiB                                                 │ │
│  │ ├── 99.999% durability (not 99.99% like others)                     │ │
│  │ └── Use: Largest, most demanding DBs (SAP HANA, Oracle)             │ │
│  ├───────────────────────────────────────────────────────────────────────┤ │
│  │ io2                                                                   │ │
│  │ ├── Max IOPS: 64,000                                                 │ │
│  │ ├── Max Size: 16 TiB                                                 │ │
│  │ ├── 99.999% durability (higher than io1)                             │ │
│  │ └── Use: Production DBs (MySQL, PostgreSQL, SQL Server)              │ │
│  ├───────────────────────────────────────────────────────────────────────┤ │
│  │ io1 (Older)                                                           │ │
│  │ ├── Max IOPS: 64,000                                                 │ │
│  │ ├── Max Size: 16 TiB                                                 │ │
│  │ ├── 99.99% durability                                                │ │
│  │ └── Use: Legacy; io2 is same/better price                            │ │
│  ├───────────────────────────────────────────────────────────────────────┤ │
│  │ gp3 (NEW - HIGH PERFORMANCE AT LOWER COST)                           │ │
│  │ ├── Baseline: 3,000 IOPS (regardless of size)                       │ │
│  │ ├── Baseline throughput: 125 MB/s                                   │ │
│  │ ├── Provision up to: 16,000 IOPS, 1,000 MB/s                        │ │
│  │ ├── 20-40% cheaper than gp2                                         │ │
│  │ └── Use: Virtual desktops, boot volumes, dev/test, general use      │ │
│  ├───────────────────────────────────────────────────────────────────────┤ │
│  │ gp2                                                                   │ │
│  │ ├── IOPS tied to size: 3 IOPS per GB (min 100, max 16,000)          │ │
│  │ ├── Burst credits (accumulates when idle)                           │ │
│  │ └── Use: Legacy; gp3 is cheaper and better                          │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  HDD-BASED (Throughput-intensive workloads)                                 │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ st1 (Throughput Optimized HDD)                                        │ │
│  │ ├── Max Throughput: 500 MB/s                                         │ │
│  │ ├── Use: Big data, data warehouses, log processing                   │ │
│  │ └── Cost: LOWEST $/GB for large data                                 │ │
│  ├───────────────────────────────────────────────────────────────────────┤ │
│  │ sc1 (Cold HDD)                                                        │ │
│  │ ├── Max Throughput: 250 MB/s                                         │ │
│  │ ├── Use: Infrequently accessed data                                  │ │
│  │ └── Cost: Even cheaper than st1                                      │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### EBS Multi-Attach - Exam Concept

**What it is**: Attach the SAME EBS volume to up to 16 Nitro-based EC2 instances in the SAME Availability Zone.

| Capability | Details |
|------------|---------|
| **Supported volume types** | io1, io2 (NOT gp2, gp3, st1, sc1) |
| **Max attachments** | 16 instances |
| **Instance requirements** | Nitro-based (C5, M5, R5, etc.) |
| **File system required** | Cluster-aware (AWS Cluster FS, Oracle ASM, etc.) |
| **NOT supported** | Windows instances |

**Exam scenario**: "You need 5 EC2 instances to read/write to the same storage with low latency. Storage must persist beyond instance termination. What do you use?" → **EBS with Multi-Attach (io2 volume)**

### EBS Snapshot - Backup & Disaster Recovery

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EBS SNAPSHOTS                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Key Features:                                                             │
│   ├── Incremental backups (only changed blocks)                            │
│   ├── Stored in S3 (but NOT directly accessible)                           │
│   ├── Can copy across regions                                              │
│   ├── Can share with other AWS accounts                                    │
│   └── Can create volumes from snapshots (different size/type)              │
│                                                                             │
│   FAST SNAPSHOT RESTORE (NEW):                                              │
│   ├── Eliminates pre-warming for snapshots                                 │
│   ├── Creates volumes with full performance IMMEDIATELY                    │
│   ├── Use for: Large DBs (>1 TB)                                          │
│   └── Cost: Additional hourly fee per snapshot                             │
│                                                                             │
│   SNAPSHOT RECYCLE BIN:                                                     │
│   ├── Prevent accidental deletion of snapshots                            │
│   ├── Retention rules (1 day to 1 year)                                    │
│   └── Automatic or manual recovery                                         │
│                                                                             │
│   EXAM TRICK: To create a backup before instance termination:              │
│   ├── Stop the instance (optional but recommended for consistency)        │
│   ├── Create snapshot of attached EBS volumes                              │
│   └── Terminate instance                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

[⬆ Back to top](#table-of-contents)

## 🔐 Security Groups & Network ACLs - The Firewall Layer

### Deep Comparison

| Aspect | Security Group | Network ACL |
|--------|---------------|-------------|
| **Scope** | Instance level (ENI) | Subnet level |
| **Rules** | ALLOW only (no DENY) | ALLOW and DENY |
| **State** | Stateful (return traffic auto-allowed) | Stateless (must specify both directions) |
| **Rule Order** | All rules evaluated | Processed in order (lowest number first) |
| **Default** | Deny all inbound, Allow all outbound | Allow all inbound/outbound (custom VPC) |
| **Association** | Can attach to multiple instances | Associated with subnet (all instances in subnet) |

### Security Group Best Practices

```yaml
# Web Server Security Group
WebSecurityGroup:
  Inbound:
    - Protocol: TCP, Port: 443, Source: 0.0.0.0/0  # HTTPS from anywhere
    - Protocol: TCP, Port: 80, Source: 0.0.0.0/0   # HTTP from anywhere
    - Protocol: TCP, Port: 22, Source: 10.0.0.0/8  # SSH from corporate VPN
    - Protocol: TCP, Port: 8080, Source: sg-app-sg  # App tier communication
  Outbound:
    - Protocol: ALL, Destination: 0.0.0.0/0  # Allow all outbound

# Database Security Group
DBSecurityGroup:
  Inbound:
    - Protocol: TCP, Port: 5432, Source: sg-web-sg  # PostgreSQL from web tier
    - Protocol: TCP, Port: 3306, Source: sg-app-sg  # MySQL from app tier
  Outbound:
    - Protocol: ALL, Destination: 0.0.0.0/0
```

---

[⬆ Back to top](#table-of-contents)

## 💰 EC2 Pricing Models - Exam Critical

### The Four Pricing Models

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EC2 PRICING MODELS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. ON-DEMAND - Pay by the second (min 60 seconds)                         │
│     ├── Use: Short-term, unpredictable workloads                           │
│     ├── No upfront payment                                                 │
│     ├── Highest flexibility, highest price                                 │
│     └── No commitment                                                      │
│                                                                             │
│  2. RESERVED INSTANCES (RI) - 1 or 3 year commitment                       │
│     ├── Up to 72% discount vs On-Demand                                    │
│     ├── Three payment options:                                            │
│     │   ├── All Upfront (AURI) - Best discount                            │
│     │   ├── Partial Upfront (PURI) - Balance monthly                      │
│     │   └── No Upfront (NURI) - Monthly only                              │
│     ├── Three offerings:                                                  │
│     │   ├── Standard RI - Best discount, less flexibility                 │
│     │   ├── Convertible RI - Can change instance family (less discount)   │
│     │   └── Scheduled RI - Specific time windows (legacy)                 │
│     └── Can sell in Reserved Instance Marketplace                         │
│                                                                             │
│  3. SPOT INSTANCES - Bid for unused capacity                               │
│     ├── Up to 90% discount                                                 │
│     ├── Can be interrupted with 2-minute notice                           │
│     ├── Use: Batch processing, CI/CD, dev/test                            │
│     ├── DO NOT use: Production DBs, real-time apps                        │
│     └── Spot Fleet can mix On-Demand + Spot                               │
│                                                                             │
│  4. SAVINGS PLANS (NEWER than RIs)                                         │
│     ├── Compute Savings Plan: ANY instance, ANY region, ANY family        │
│     │   └── Up to 66% discount                                            │
│     ├── EC2 Instance Savings Plan: Specific family in specific region     │
│     │   └── Up to 72% discount                                            │
│     └── Better flexibility than RIs (but similar savings)                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### When to Use Which Model (Decision Tree)

```
START: Is workload continuous 24/7?
        │
        ├── NO ──► Use On-Demand or Spot
        │          │
        │          └── Can it be interrupted?
        │               ├── YES ──► Spot
        │               └── NO ───► On-Demand
        │
        └── YES ──► Will it run for 1+ years?
                    │
                    ├── YES ──► Reserved Instance or Savings Plan
                    │
                    └── NO ───► On-Demand with Auto Scaling
```

### Spot Instance Strategies for Batch Workloads

```json
{
  "SpotFleetRequestConfigData": {
    "AllocationStrategy": "lowestPrice",
    "InstanceInterruptionBehavior": "terminate",
    "SpotMaintenanceStrategies": {
      "CapacityRebalance": {
        "TerminationDelay": 120  // 2 minute notice
      }
    }
  }
}
```

**Exam Trick**: Spot instances can be STOPPED (if instance type supports hibernation) or TERMINATED. For Batch jobs, termination is preferred.

---

[⬆ Back to top](#table-of-contents)

## 🔄 User Data & Metadata - Bootstrapping EC2

### User Data

**What it is**: Script that runs when EC2 instance FIRST launches (as root).

```bash
#!/bin/bash
# User Data script for web server
yum update -y
yum install -y httpd
systemctl enable httpd
systemctl start httpd

# Download application code from S3
aws s3 cp s3://my-app-bucket/webapp/ /var/www/html/ --recursive

# Get instance metadata and write to webpage
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
INSTANCE_ID=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id)
echo "Instance ID: $INSTANCE_ID" > /var/www/html/index.html
```

**Key Points**:

- Maximum size: 16 KB (base64 encoded)
- Runs ONCE at first boot (not on subsequent starts)
- Use for: Installing software, downloading configs, joining clusters
- Can be modified after stop/start (if instance uses C5/M5/R5 or newer)

### Instance Metadata Service v2 (IMDSv2) - SECURITY CRITICAL

```bash
# IMDSv2 requires session token (prevents SSRF attacks)
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

# Then use token for all metadata requests
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/

# IMDSv1 (deprecated for security) - NO TOKEN
curl http://169.254.169.254/latest/meta-data/
```

**Why IMDSv2 Matters**:

- Prevents open firewalls from exposing metadata
- Protects against SSRF attacks (common in misconfigured proxies)
- **Exam loves this**: "How to secure EC2 instance metadata?" → Enable IMDSv2

**How to enforce IMDSv2**:

```bash
aws ec2 modify-instance-metadata-options \
  --instance-id i-1234567890abcdef0 \
  --http-tokens required \
  --http-endpoint enabled
```

---

[⬆ Back to top](#table-of-contents)

## 📈 EC2 Auto Scaling - The Complete Picture

### What Auto Scaling Does

Auto Scaling Group (ASG) ensures you have the RIGHT number of EC2 instances:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AUTO SCALING GROUP                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  LAUNCH TEMPLATE (or Configuration)                                 │  │
│   │  ├── AMI ID                                                         │  │
│   │  ├── Instance type (or multiple types for mixed)                    │  │
│   │  ├── Security Groups                                                │  │
│   │  ├── Key Pair                                                       │  │
│   │  ├── User Data                                                      │  │
│   │  └── IAM Role                                                       │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  AUTO SCALING GROUP                                                 │  │
│   │  ├── Min: 2 (always have at least 2)                               │  │
│   │  ├── Max: 10 (never exceed 10)                                     │  │
│   │  ├── Desired: 2 (start with 2)                                     │  │
│   │  └── Subnets: us-east-1a, us-east-1b, us-east-1c (multi-AZ)        │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  SCALING POLICIES                                                   │  │
│   │  ├── Target Tracking: CPU = 50%                                    │  │
│   │  ├── Simple: +2 instances when CPU > 70%                           │  │
│   │  ├── Scheduled: Increase to 5 at 9 AM                              │  │
│   │  └── Predictive: ML-based forecasting                              │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Scaling Policy Types - Exam Deep Dive

| Policy Type | How It Works | Use Case | Exam Trick |
|-------------|--------------|----------|------------|
| **Target Tracking** | Maintains metric at target value (e.g., CPU=50%) | Most common production | Simplest to configure |
| **Simple Scaling** | Execute one action when threshold crossed | Legacy; avoid | Has cooldown period (300 sec default) |
| **Step Scaling** | Multiple thresholds with different actions | Granular control | Use instead of simple scaling |
| **Scheduled Scaling** | Time-based (e.g., 9 AM scale up) | Predictable patterns | Can combine with dynamic scaling |
| **Predictive Scaling** | Uses ML to forecast demand | Daily/weekly patterns | Requires 14 days of history |

### Health Checks - Three Types

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EC2 HEALTH CHECK TYPES                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. EC2 STATUS CHECKS (free, default)                                      │
│     ├── System reachability                                                │
│     ├── Instance reachability                                              │
│     └── Replaces instances that fail                                       │
│                                                                             │
│  2. ELB HEALTH CHECKS (requires Load Balancer)                             │
│     ├── HTTP/HTTPS endpoint (e.g., /health)                               │
│     ├── Configurable (interval, timeout, threshold)                        │
│     └── More accurate (checks application health)                          │
│                                                                             │
│  3. CUSTOM HEALTH CHECKS                                                   │
│     ├── EC2 sends heartbeat to SQS/CloudWatch                             │
│     ├── ASG uses SQS to determine health                                  │
│     └── For complex health validation                                     │
│                                                                             │
│  IMPORTANT: ASG will mark instance as UNHEALTHY after:                     │
│  - 2 consecutive EC2 status check failures OR                             │
│  - 2 consecutive ELB health check failures                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Lifecycle Hooks - Graceful Draining

**Purpose**: Allow instances to complete work before termination.

```python
# Lambda function triggered by lifecycle hook
def lambda_handler(event, context):
    # Get instance info
    instance_id = event['detail']['EC2InstanceId']
    lifecyle_hook = event['detail']['LifecycleHookName']
    
    # Your cleanup logic
    deregister_from_load_balancer(instance_id)
    drain_connections(instance_id)
    upload_logs_to_s3(instance_id)
    
    # Complete the lifecycle hook
    autoscaling = boto3.client('autoscaling')
    autoscaling.complete_lifecycle_action(
        LifecycleHookName=lifecyle_hook,
        AutoScalingGroupName=event['detail']['AutoScalingGroupName'],
        LifecycleActionResult='CONTINUE'
    )
```

### Warm Pools - Reduce Latency for Scaling

**What it is**: Pre-initialized instances that are stopped (not running) but ready to start quickly.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WARM POOLS                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Without Warm Pool:                                                        │
│   Scale event → Launch EC2 (2 min) → Boot OS (30 sec) → App start → Ready  │
│   Total: ~3-5 minutes                                                       │
│                                                                             │
│   With Warm Pool:                                                           │
│   Scale event → Start stopped instance (30 sec) → App ready                │
│   Total: ~30-60 seconds                                                     │
│                                                                             │
│   Configuration:                                                            │
│   ├── Min warm pool size: 2                                                │
│   ├── Max warm pool size: 5                                                │
│   ├── Pool state: Stopped (costs less than Running)                        │
│   └── Instance reuse policy: Reuse or replace                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

[⬆ Back to top](#table-of-contents)

## 🔗 EC2 with Other Services - Integration Architecture

### Complete Three-Tier Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THREE-TIER WEB APPLICATION                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   USER ──► CloudFront ──► ALB (Internet-facing)                           │
│                                │                                            │
│                                ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  TIER 1: WEB (Public Subnets)                                       │  │
│   │  ├── ASG: Web Servers                                               │  │
│   │  ├── Instance Type: t3.medium                                       │  │
│   │  ├── Security Group: Allow 80/443 from ALB                         │  │
│   │  └── User Data: Install nginx, download from S3                    │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  TIER 2: APPLICATION (Private Subnets)                              │  │
│   │  ├── ASG: App Servers (Internal ALB)                               │  │
│   │  ├── Instance Type: c5.large (compute optimized)                   │  │
│   │  ├── Security Group: Allow 8080 from Web SG                         │  │
│   │  └── User Data: Install Java/Node.js app                            │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  TIER 3: DATABASE (Private Subnets)                                 │  │
│   │  ├── RDS Multi-AZ (PostgreSQL)                                      │  │
│   │  ├── Security Group: Allow 5432 from App SG                         │  │
│   │  └── Read Replicas for reporting                                    │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   Supporting Services:                                                      │
│   ├── Secrets Manager: DB credentials                                      │
│   ├── S3: Static assets                                                   │
│   ├── CloudWatch: Logs and metrics                                        │
│   └── VPC Endpoints: Private access to S3                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### IAM Roles for EC2 - Best Practices

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-app-config/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "ssm:GetParameter",
      "Resource": "arn:aws:ssm:us-east-1:123456789012:parameter/app/*"
    }
  ]
}
```

**NEVER put AWS credentials in EC2 User Data or AMI! Always use IAM Roles!**

---

[⬆ Back to top](#table-of-contents)

## 💡 Cost Optimization with EC2

### Top 5 Cost-Saving Strategies

| Strategy | Savings | Implementation |
|----------|---------|----------------|
| **Right-sizing** | 20-50% | Use Compute Optimizer or Trusted Advisor |
| **Savings Plans** | 40-66% | Purchase 1-3 year commitment |
| **Spot instances** | 60-90% | Batch, dev/test, fault-tolerant workloads |
| **Auto Scaling** | Variable | Scale down to min capacity overnight |
| **EBS gp3** | 20-40% | Replace gp2 with gp3 (same performance, lower cost) |

### Cost Comparison Example

```
Workload: 10 instances, 24/7/365, m5.large (On-Demand ~$0.096/hour)

On-Demand: 10 × 0.096 × 8760 = $8,409.60/year

1-year Standard RI (All Upfront): $4,740.00/year → SAVE $3,669.60

3-year Standard RI (All Upfront): $2,688.00/year → SAVE $5,721.60

Spot (if applicable, 70% discount): $2,522.88/year → SAVE $5,886.72

Compute Savings Plan (1-year): $5,049.60/year → SAVE $3,360.00
```

---

[⬆ Back to top](#table-of-contents)

## 🔥 High Performance Configurations

### EBS-Optimized Instances

| Instance Family | EBS-Optimized by Default | Max Bandwidth |
|----------------|-------------------------|---------------|
| T3 | Yes | 5 Gbps |
| M5 | Yes | 10 Gbps |
| C5 | Yes | 10 Gbps |
| R5 | Yes | 10 Gbps |
| X2idn | Yes | 25 Gbps |

**Without EBS optimization**: EBS traffic shares network bandwidth with data traffic → poor performance.

### Placement Groups - Exam Critical

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PLACEMENT GROUPS                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CLUSTER - Low latency, high throughput                                    │
│  ├── Single AZ, Rack-level proximity                                       │
│  ├── 10 Gbps (single flow) - 25 Gbps (multi-flow)                          │
│  ├── Use: HPC, tightly-coupled apps (SAP, Oracle RAC)                     │
│  └── Risk: Single point of failure (same rack)                             │
│                                                                             │
│  SPREAD - High availability                                                │
│  ├── Across distinct hardware (max 7 instances per AZ)                     │
│  ├── Use: Critical small cluster (ZooKeeper, Consul)                       │
│  └── Note: Limited to 7 instances per AZ                                   │
│                                                                             │
│  PARTITION - Large scale distributed                                       │
│  ├── Across partitions (max 7 per AZ)                                      │
│  ├── Each partition has its own rack                                       │
│  ├── Use: Large distributed systems (Hadoop, Kafka)                        │
│  └── Partition aware applications                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

[⬆ Back to top](#table-of-contents)

## 🛡️ Resilience Best Practices

| Practice | Implementation | Protects Against |
|----------|----------------|-------------------|
| **Multi-AZ** | Spread ASG across ≥2 AZs | AZ failure |
| **Multi-region** | Route53 failover to secondary region | Regional outage |
| **EBS Snapshots** | Daily automated snapshots | Data loss |
| **AMI backups** | Create AMI after patching | Corrupt boot volume |
| **Termination Protection** | Enable on critical instances | Accidental termination |
| **Recovery CloudWatch** | Recover instance if status check fails | Instance failure |

---

[⬆ Back to top](#table-of-contents)

## 📝 EC2 Exam Question Bank

### Question 1: Instance Selection

**Scenario**: A company runs a web application that has consistent traffic patterns. CPU usage is stable at 40% during business hours and drops to 5% overnight. The application needs to respond within 200ms at all times.

**Question**: Which instance family and configuration is MOST cost-effective?

A. c5.large On-Demand with Auto Scaling  
B. t3.large with Unlimited mode enabled  
C. m5.large Reserved Instance  
D. r5.large Spot Instance

**Answer**: B

**Explanation**: T3 instances with Unlimited mode allow bursting above baseline while being cheaper for variable workloads. Since traffic is consistent during business hours (not spiking), T3 provides sufficient performance. Unlimited mode prevents throttling.

---

### Question 2: EBS Performance

**Scenario**: A PostgreSQL database requires 50,000 IOPS for a critical production workload. The database runs on a single EC2 instance and cannot be re-architected.

**Question**: Which EBS volume type and configuration should be used?

A. gp3 with 50,000 provisioned IOPS  
B. io2 Block Express with 50,000 provisioned IOPS  
C. st1 with 50,000 provisioned IOPS  
D. Two gp2 volumes in RAID 0

**Answer**: B

**Explanation**: io2 Block Express supports up to 256,000 IOPS and provides 99.999% durability. gp3 maxes at 16,000 IOPS. st1 is HDD (not for DB workloads). RAID 0 would work but adds complexity and risk.

---

### Question 3: Auto Scaling

**Scenario**: An e-commerce application experiences unpredictable traffic spikes during flash sales. The Auto Scaling group currently uses simple scaling policies.

**Question**: What improvement would BEST handle these unpredictable spikes?

A. Increase the cooldown period to 600 seconds  
B. Switch to target tracking scaling policy based on CPU  
C. Switch to scheduled scaling for flash sale times  
D. Use lifecycle hooks to pre-warm instances

**Answer**: B

**Explanation**: Target tracking dynamically maintains CPU at target value, automatically scaling to meet demand. Simple scaling has cooldown periods that can't keep up with rapid spikes.

---

### Question 4: Security Groups

**Scenario**: A three-tier application has web, app, and database layers. The web tier must only accept HTTPS traffic from the internet. The app tier must only accept traffic from the web tier. The database tier must only accept traffic from the app tier.

**Question**: Which security group configuration meets these requirements?

A. Web SG: Allow 443 from 0.0.0.0/0; App SG: Allow 8080 from Web SG; DB SG: Allow 3306 from App SG  
B. Web NACL: Allow 443 from 0.0.0.0/0; App NACL: Allow 8080 from Web; DB NACL: Allow 3306 from App  
C. Web SG: Allow 443 from 0.0.0.0/0; App SG: Allow 0.0.0.0/0; DB SG: Allow 0.0.0.0/0  
D. Web SG: Allow 443 from ALB; App SG: Allow 8080 from ALB; DB SG: Allow 3306 from ALB

**Answer**: A

**Explanation**: Security Groups (not NACLs) are used at instance level. Referencing another security group (App SG from Web SG) is the correct pattern. Allow 0.0.0.0/0 would bypass all security.

---

### Question 5: Spot Instances

**Scenario**: A data processing job runs for 2 hours every night. The job is fault-tolerant and can be interrupted. The job must complete within an 8-hour window.

**Question**: Which configuration is MOST cost-effective?

A. On-Demand instances in a compute-optimized family  
B. Reserved Instances in a general purpose family  
C. Spot Instances in a compute-optimized family  
D. Dedicated Hosts in a memory-optimized family

**Answer**: C

**Explanation**: The workload is fault-tolerant, time-flexible (8-hour window), and night-only. Spot instances provide 60-90% savings. Compute-optimized family (C5) matches the batch processing workload.

---

### Question 6: IMDSv2

**Scenario**: A security audit reveals that EC2 instances are vulnerable to SSRF attacks that could expose instance metadata.

**Question**: What should be done to remediate this vulnerability?

A. Move instances to private subnets  
B. Enable IMDSv2 and require tokens on all instances  
C. Disable the metadata service entirely  
D. Add a NACL rule to block 169.254.169.254

**Answer**: B

**Explanation**: IMDSv2 requires a session token to access metadata, preventing SSRF attacks. Disabling metadata breaks functionality. NACL blocking would break legitimate metadata access.

---

[⬆ Back to top](#table-of-contents)

## 📊 EC2 Quick Reference for Exam Day

| If the question asks about... | Think... |
|-------------------------------|----------|
| Variable CPU usage, cost optimization | T3 Unlimited |
| Consistent high CPU | C5 or M5 |
| Large in-memory database | R5 or X2idn |
| Batch processing, cost-sensitive | Spot with C5 |
| High IOPS for DB | io2 Block Express |
| Shared storage across instances | EFS (not EBS) |
| Fast scaling from stopped state | Warm pools |
| Automatic metric-based scaling | Target tracking |
| Graceful shutdown on scale-in | Lifecycle hooks |
| Low-latency within instances | Placement group (Cluster) |
| High availability across racks | Placement group (Spread) |
| Protecting from SSRF | IMDSv2 |
| Instance access to AWS services | IAM Role (never keys) |
| Bootstrapping at launch | User Data |
| Backup before termination | EBS snapshot |
| Cross-region disaster recovery | AMI copy |

---
