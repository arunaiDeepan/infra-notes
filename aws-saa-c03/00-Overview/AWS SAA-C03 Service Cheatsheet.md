# AWS SAA-C03 Service Cheatsheet - All Services

> A one-stop exam cheatsheet for every service likely on the SAA-C03: **what it is**, **when to use it**, and **what it's used for**. Organised by domain. Use the per-row "exam trigger" hints to map question keywords → the right service.

See also: [AWS Glossary](AWS%20Glossary.md) · [01 - RDS Intro & Core Concepts](01%20-%20RDS%20Intro%20%26%20Core%20Concepts.md) · [04 - Amazon DynamoDB](04%20-%20Amazon%20DynamoDB.md)

---

## Table of Contents

- [How to Use This Sheet](#how-to-use-this-sheet)
- [Compute](#compute)
- [Storage](#storage)
- [Databases](#databases)
- [Networking & Content Delivery](#networking--content-delivery)
- [Security, Identity & Compliance](#security-identity--compliance)
- [Application Integration](#application-integration)
- [Management & Governance](#management--governance)
- [Monitoring & Observability](#monitoring--observability)
- [Migration & Transfer](#migration--transfer)
- [Analytics](#analytics)
- [Cost Management](#cost-management)
- [High-Level Decision Triggers](#high-level-decision-triggers)
- [Exam Keyword → Service Map](#exam-keyword--service-map)

---

## How to Use This Sheet

The SAA-C03 is **scenario-based**, not trivia. Almost every question is "given this situation, which service/config is **best** (cheapest / most available / most secure / least operational overhead)?" So for each service, lock in three things:

- **What it is** — the one-line definition.
- **When to use** — the scenario keywords that point to it.
- **Watch-outs** — the trap that makes a _similar_ service wrong.

> [!tip] The four lenses
> Most "best answer" questions are decided by one of: **Cost**, **High Availability / Durability**, **Security / least privilege**, or **Operational overhead (managed > self-managed)**. Read the last sentence of the question first — it tells you which lens to apply.

[⬆ Back to top](#table-of-contents)

---

## Compute

| Service                      | What it is                                              | When to use                                                    | Used for / Watch-outs                                                                                                                                                                 |
| ---------------------------- | ------------------------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **EC2**                      | Resizable virtual servers (IaaS).                       | Full OS control, legacy/long-running apps, custom software.    | Pick instance family by workload: **T** (burstable), **M** (general), **C** (compute), **R/X** (memory), **P/G** (GPU), **I/D** (storage).                                            |
| **EC2 Purchasing**           | Pricing models.                                         | Match commitment to predictability.                            | **On-Demand** (spiky), **Reserved/Savings Plans** (steady 1–3 yr), **Spot** (fault-tolerant batch, up to 90% off, can be reclaimed), **Dedicated Host** (licensing/compliance, BYOL). |
| **Auto Scaling Group (ASG)** | Maintains/scaling a fleet of EC2 across AZs.            | Elasticity + self-healing for EC2.                             | Target tracking / step / scheduled / predictive scaling. Spans **multiple AZs** for HA. Not for sub-second scaling.                                                                   |
| **Elastic Beanstalk**        | PaaS that deploys your code onto managed EC2/ASG/ELB.   | Devs want to deploy without managing infra, but keep access.   | You still own the resources; good for classic web apps. Less control than raw EC2, more than Lambda.                                                                                  |
| **Lambda**                   | Serverless functions, event-driven, pay-per-invocation. | Short tasks (≤15 min), glue code, event processing, APIs.      | No server mgmt; scales automatically. Watch **cold starts**, **15-min max**, **/tmp & memory limits**. Pair with API Gateway / EventBridge / S3 events.                               |
| **ECS**                      | AWS-native container orchestration.                     | Run Docker containers without Kubernetes.                      | **EC2 launch type** (you manage nodes) vs **Fargate** (serverless).                                                                                                                   |
| **EKS**                      | Managed Kubernetes.                                     | You need Kubernetes / portability / existing k8s tooling.      | More overhead than ECS; choose when k8s is a requirement.                                                                                                                             |
| **Fargate**                  | Serverless compute for ECS/EKS.                         | Containers with no node management.                            | Pay per task vCPU/memory; best for variable container workloads.                                                                                                                      |
| **AWS Batch**                | Managed batch computing.                                | Large-scale batch/HPC jobs queued and run on EC2/Fargate/Spot. | Great with **Spot** for cost. Not for real-time.                                                                                                                                      |
| **Lightsail**                | Simplified VPS with flat pricing.                       | Simple websites/blogs, dev/test, predictable cost, beginners.  | Limited integration; "easy/simple/predictable price" = exam trigger.                                                                                                                  |
| **Outposts**                 | AWS hardware in your data center.                       | Low-latency / data-residency needs on-prem with AWS APIs.      | Hybrid; truly local compute/storage.                                                                                                                                                  |
| **Wavelength**               | AWS compute at 5G telecom edge.                         | Ultra-low-latency mobile/5G apps.                              | Edge of carrier network.                                                                                                                                                              |

> [!tip] Compute decision
> "Least operational overhead" + event-driven → **Lambda**. Containers, no k8s → **ECS/Fargate**. Need full OS / licensing → **EC2**. Fault-tolerant + cheapest → **Spot**.

[⬆ Back to top](#table-of-contents)

---

## Storage

| Service                        | What it is                                                | When to use                                                | Used for / Watch-outs                                                                                                                                                                   |
| ------------------------------ | --------------------------------------------------------- | ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **S3**                         | Object storage, 11-nines durability, virtually unlimited. | Static assets, backups, data lakes, logs, static websites. | Object (not block/file). Flat namespace. Integrates with everything.                                                                                                                    |
| **S3 Storage Classes**         | Tiers by access frequency.                                | Cost-optimise by access pattern.                           | **Standard** (hot), **Intelligent-Tiering** (unknown pattern), **Standard-IA / One Zone-IA** (infrequent), **Glacier Instant / Flexible / Deep Archive** (archive, retrieval mins→hrs). |
| **S3 Lifecycle / Replication** | Auto-transition/expire objects; CRR/SRR.                  | Aging data to cheaper tiers; DR/compliance copies.         | **CRR** = cross-region (DR, latency); **SRR** = same-region (log aggregation, compliance).                                                                                              |
| **EBS**                        | Block storage for a single EC2 (network-attached).        | Boot volumes, databases on EC2.                            | **Single AZ** (snapshot to S3 for durability). **gp3** (general), **io1/io2** (high IOPS), **st1** (throughput HDD), **sc1** (cold HDD). Multi-Attach only io1/io2 + cluster-aware app. |
| **Instance Store**             | Physical disk attached to host.                           | Temp/scratch, caches, high IOPS.                           | **Ephemeral** — data lost on stop/terminate.                                                                                                                                            |
| **EFS**                        | Managed NFS shared file system (Linux).                   | Shared POSIX file access across many EC2/AZs.              | Multi-AZ, scales automatically. Linux only. More expensive than EBS/S3.                                                                                                                 |
| **FSx for Windows**            | Managed Windows SMB file shares.                          | Windows apps, Active Directory integration.                | SMB protocol.                                                                                                                                                                           |
| **FSx for Lustre**             | High-performance file system.                             | HPC, ML, media processing; links to S3.                    | Massive throughput.                                                                                                                                                                     |
| **Storage Gateway**            | Hybrid on-prem ↔ AWS storage bridge.                      | Extend on-prem to cloud; backups; tiering.                 | **File GW** (NFS/SMB→S3), **Volume GW** (iSCSI block), **Tape GW** (VTL→Glacier).                                                                                                       |
| **AWS Backup**                 | Centralised backup across services.                       | Policy-based backups (EBS, RDS, DynamoDB, EFS, etc.).      | Compliance, cross-region/cross-account backup.                                                                                                                                          |

> [!tip] Storage decision
> One EC2, block → **EBS**. Shared Linux files → **EFS**. Windows files → **FSx Windows**. Objects/backups/cheap → **S3** (+ lifecycle to Glacier). Hybrid on-prem → **Storage Gateway**.

[⬆ Back to top](#table-of-contents)

---

## Databases

| Service               | What it is                                                              | When to use                                                              | Used for / Watch-outs                                                                                                                                  |
| --------------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **RDS**               | Managed relational DB (MySQL, PostgreSQL, MariaDB, Oracle, SQL Server). | OLTP, structured data, minimal DB admin.                                 | **Multi-AZ** = HA/failover (synchronous standby, _not_ for reads). **Read Replicas** = scale reads (async, up to 15, cross-region).                    |
| **Aurora**            | AWS cloud-native MySQL/PostgreSQL-compatible DB.                        | Need RDS but higher performance/availability.                            | 6 copies across 3 AZs, up to 15 read replicas, auto-storage scaling, **Global Database** (cross-region DR <1s).                                        |
| **Aurora Serverless** | Auto-scaling Aurora capacity.                                           | Intermittent/unpredictable workloads, dev/test.                          | Pay per ACU; scales to demand.                                                                                                                         |
| **DynamoDB**          | Managed serverless NoSQL key-value/document.                            | Single-digit-ms at any scale, serverless apps, session/cart.             | **On-demand vs provisioned** capacity. **DAX** = microsecond cache. **Streams** = CDC. **Global Tables** = multi-region active-active. TTL for expiry. |
| **ElastiCache**       | Managed in-memory cache (Redis / Memcached).                            | Reduce DB load, sub-ms reads, session store, leaderboards.               | **Redis** (persistence, replication, HA, pub/sub) vs **Memcached** (simple, multi-threaded, no persistence).                                           |
| **Redshift**          | Petabyte-scale columnar data warehouse (OLAP).                          | Analytics/BI on structured data, complex aggregations.                   | Not for OLTP. **Spectrum** queries S3 directly.                                                                                                        |
| **DocumentDB**        | Managed MongoDB-compatible document DB.                                 | MongoDB workloads, JSON documents.                                       | —                                                                                                                                                      |
| **Neptune**           | Managed graph database.                                                 | Highly connected data: social, fraud, recommendations, knowledge graphs. | Gremlin / SPARQL.                                                                                                                                      |
| **Keyspaces**         | Managed Apache Cassandra.                                               | Cassandra workloads, wide-column.                                        | Serverless CQL.                                                                                                                                        |
| **OpenSearch**        | Managed search & log analytics (ELK).                                   | Full-text search, log analytics, observability dashboards.               | —                                                                                                                                                      |
| **Timestream**        | Managed time-series DB.                                                 | IoT/metrics/sensor time-series data.                                     | —                                                                                                                                                      |
| **QLDB**              | Immutable ledger DB.                                                    | Cryptographically verifiable, immutable transaction log.                 | Single trusted owner (vs blockchain).                                                                                                                  |

> [!tip] DB decision
> Relational + managed → **RDS/Aurora**. NoSQL serverless ms scale → **DynamoDB**. Analytics/warehouse → **Redshift**. Cache → **ElastiCache**. Graph → **Neptune**. Search/logs → **OpenSearch**. **Multi-AZ = HA, Read Replica = read scaling** (common trap).

[⬆ Back to top](#table-of-contents)

---

## Networking & Content Delivery

| Service                | What it is                                      | When to use                                               | Used for / Watch-outs                                                                                                               |
| ---------------------- | ----------------------------------------------- | --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| **VPC**                | Your isolated virtual network.                  | Foundation for almost everything.                         | Subnets (public/private), route tables, IGW, NAT, NACLs, SGs.                                                                       |
| **Subnets**            | IP range within an AZ.                          | Segment public vs private resources.                      | **Public** = route to IGW. **Private** = no direct internet. One subnet = one AZ.                                                   |
| **Security Groups**    | Stateful instance-level firewall.               | Control traffic to ENIs/instances.                        | **Stateful** (return traffic auto-allowed), allow rules only.                                                                       |
| **NACLs**              | Stateless subnet-level firewall.                | Subnet-wide allow/deny, block specific IPs.               | **Stateless** (must allow both directions), supports **deny**, ordered rules.                                                       |
| **Internet Gateway**   | VPC ↔ internet.                                 | Give public subnets internet access.                      | Horizontally scaled, HA.                                                                                                            |
| **NAT Gateway**        | Outbound internet for private subnets.          | Private instances reach internet, no inbound.             | Managed, AZ-resilient (deploy per AZ for HA). NAT Instance = legacy/cheaper but self-managed.                                       |
| **VPC Endpoints**      | Private access to AWS services (no internet).   | Keep traffic on AWS backbone, no IGW/NAT.                 | **Gateway Endpoint** (S3 & DynamoDB only, free) vs **Interface Endpoint** (PrivateLink, ENI, most services).                        |
| **PrivateLink**        | Private connectivity to a service across VPCs.  | Expose/consume a service privately without VPC peering.   | Interface endpoints + NLB.                                                                                                          |
| **VPC Peering**        | Connect two VPCs privately.                     | Few VPCs, 1:1.                                            | **Not transitive**; no overlapping CIDRs.                                                                                           |
| **Transit Gateway**    | Hub-and-spoke network hub.                      | Connect many VPCs + on-prem at scale.                     | Transitive routing; replaces mesh of peerings.                                                                                      |
| **ELB**                | Distributes traffic across targets.             | HA + scaling for apps.                                    | **ALB** (L7 HTTP/host/path), **NLB** (L4 TCP/UDP, ultra-low latency, static IP), **GWLB** (firewalls/appliances), **CLB** (legacy). |
| **Route 53**           | Managed DNS + health checks + routing policies. | DNS, domain registration, failover, geo routing.          | Policies: **Simple, Weighted, Latency, Failover, Geolocation, Geoproximity, Multi-value**. Alias records (free, to AWS resources).  |
| **CloudFront**         | Global CDN (edge caching).                      | Cache static/dynamic content near users, lower latency.   | Integrates S3/ALB/EC2; **OAC** to lock S3; supports WAF, signed URLs/cookies.                                                       |
| **Global Accelerator** | Anycast static IPs over AWS backbone.           | Global low-latency to apps (non-HTTP too); fast failover. | Not caching (vs CloudFront); good for TCP/UDP, gaming, APIs.                                                                        |
| **Direct Connect**     | Dedicated private line to AWS.                  | Consistent low latency, high bandwidth, hybrid.           | Weeks to provision; pair with VPN for encryption/backup.                                                                            |
| **Site-to-Site VPN**   | Encrypted tunnel over internet to VPC.          | Quick hybrid connectivity, DX backup.                     | Over public internet (variable latency).                                                                                            |
| **Client VPN**         | Managed remote-access VPN for users.            | Remote workforce into VPC.                                | —                                                                                                                                   |

> [!tip] Networking traps
> **SG = stateful/allow-only; NACL = stateless/deny-capable.** S3/DynamoDB private access = **Gateway Endpoint (free)**. Many VPCs → **Transit Gateway**. Global latency for HTTP → **CloudFront**; for any protocol + static IP + failover → **Global Accelerator**.

[⬆ Back to top](#table-of-contents)

---

## Security, Identity & Compliance

| Service                           | What it is                                 | When to use                                                                  | Used for / Watch-outs                                                                                                        |
| --------------------------------- | ------------------------------------------ | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **IAM**                           | Identity & access management.              | Control who can do what.                                                     | **Users, Groups, Roles, Policies**. Least privilege. **Roles** for AWS services/cross-account/federation (never embed keys). |
| **IAM Roles**                     | Temporary credentials assumed by entities. | EC2/Lambda → AWS APIs, cross-account access.                                 | Prefer over access keys. STS issues temp creds.                                                                              |
| **IAM Identity Center (SSO)**     | Centralised workforce SSO.                 | One login across accounts/apps, Organizations.                               | Successor to AWS SSO.                                                                                                        |
| **Organizations**                 | Multi-account management.                  | Consolidated billing, **SCPs**, central governance.                          | **SCPs** = guardrails (max permissions, don't grant). OUs group accounts.                                                    |
| **Cognito**                       | App user identity (sign-up/sign-in).       | Auth for web/mobile apps; federation.                                        | **User Pools** (auth) vs **Identity Pools** (AWS creds for app users).                                                       |
| **KMS**                           | Managed encryption keys.                   | Encrypt data at rest, manage keys.                                           | **AWS-managed vs customer-managed (CMK)** keys; integrates with S3/EBS/RDS, etc.                                             |
| **CloudHSM**                      | Dedicated hardware security module.        | FIPS 140-2 L3, full key control, regulatory.                                 | You manage; more control than KMS.                                                                                           |
| **Secrets Manager**               | Store & **auto-rotate** secrets.           | DB credentials, API keys with rotation.                                      | Rotation built-in (vs SSM Parameter Store = cheaper, no native rotation).                                                    |
| **WAF**                           | Web app firewall (L7).                     | Block SQLi/XSS, rate-limit, geo-block.                                       | Attaches to CloudFront/ALB/API GW.                                                                                           |
| **Shield**                        | DDoS protection.                           | **Standard** (free, always on) / **Advanced** (paid, 24/7, cost protection). | Network/transport + app-layer (with WAF).                                                                                    |
| **GuardDuty**                     | Intelligent threat detection.              | Detect malicious/anomalous activity from logs.                               | Analyses CloudTrail/VPC Flow/DNS logs; no agents.                                                                            |
| **Inspector**                     | Automated vulnerability scanning.          | Scan EC2/ECR/Lambda for CVEs & exposure.                                     | —                                                                                                                            |
| **Macie**                         | Data security via ML.                      | Discover & protect **PII/sensitive data in S3**.                             | —                                                                                                                            |
| **Security Hub**                  | Central security posture dashboard.        | Aggregate findings, compliance checks.                                       | Aggregates GuardDuty/Inspector/Macie.                                                                                        |
| **AWS Certificate Manager (ACM)** | Free public/private TLS certs.             | HTTPS on ALB/CloudFront/API GW.                                              | Auto-renewal; region-bound (CloudFront needs us-east-1).                                                                     |

> [!tip] Security traps
> **SCP limits, never grants.** Auto-rotating secrets → **Secrets Manager**; plain config/cheap → **Parameter Store**. PII discovery in S3 → **Macie**. Threat detection from logs → **GuardDuty**. DDoS → **Shield (+WAF for L7)**.

[⬆ Back to top](#table-of-contents)

---

## Application Integration

| Service            | What it is                                    | When to use                                                         | Used for / Watch-outs                                                                                                                  |
| ------------------ | --------------------------------------------- | ------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **SQS**            | Managed message queue (pull).                 | **Decouple** producers/consumers, buffer load, async work.          | **Standard** (at-least-once, best-effort order) vs **FIFO** (exactly-once, ordered, lower TPS). Visibility timeout, DLQ, long polling. |
| **SNS**            | Pub/sub notifications (push).                 | Fan-out one message to many subscribers.                            | Topics → SQS/Lambda/HTTP/email/SMS. **SNS + SQS fan-out** is a classic pattern.                                                        |
| **EventBridge**    | Serverless event bus.                         | Route events by rules; SaaS & AWS service events; scheduling.       | Schema registry, content filtering; **cron/scheduled tasks** (replaces CloudWatch Events).                                             |
| **Step Functions** | Serverless workflow orchestration.            | Coordinate multi-step Lambda/services, retries, branching.          | **Standard** (long, durable) vs **Express** (high-volume, short). Visual state machine.                                                |
| **Amazon MQ**      | Managed ActiveMQ/RabbitMQ.                    | Migrate existing apps using **standard protocols** (AMQP/MQTT/JMS). | Choose over SQS/SNS only when protocol compatibility required.                                                                         |
| **AppFlow**        | Managed SaaS data integration.                | Move data between SaaS (Salesforce, etc.) and AWS.                  | No-code data flows.                                                                                                                    |
| **AppSync**        | Managed GraphQL API.                          | Real-time/offline mobile & web data; GraphQL.                       | Backed by DynamoDB/Lambda/RDS.                                                                                                         |
| **API Gateway**    | Managed API front door (REST/HTTP/WebSocket). | Expose Lambda/backends as APIs; throttle, authz, cache.             | Auth via IAM/Cognito/Lambda authorizers; usage plans + API keys.                                                                       |

> [!tip] Integration traps
> **Decouple + buffer = SQS** (pull). **Fan-out / push = SNS**. **Route/filter events = EventBridge**. **Orchestrate steps = Step Functions**. Existing AMQP/MQTT/JMS app → **Amazon MQ**.

[⬆ Back to top](#table-of-contents)

---

## Management & Governance

| Service                   | What it is                                    | When to use                                                             | Used for / Watch-outs                                                                     |
| ------------------------- | --------------------------------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| **CloudFormation**        | Infrastructure as Code (templates).           | Repeatable, version-controlled provisioning.                            | Declarative; stacks, change sets, drift detection. Region/account portable.               |
| **Systems Manager (SSM)** | Operational management of fleets.             | Patch, run commands, **Session Manager** (no SSH), **Parameter Store**. | Session Manager = keyless shell access (exam favorite for "no bastion/no SSH keys").      |
| **CloudTrail**            | Records API calls / account activity.         | **Auditing, governance, who-did-what**.                                 | Management + data events; deliver to S3, multi-region trail.                              |
| **Config**                | Resource configuration tracking & compliance. | Track config changes, evaluate against rules.                           | "Is my resource compliant / how did config change?" → Config (vs CloudTrail = API calls). |
| **Control Tower**         | Automated multi-account landing zone.         | Set up secure, governed multi-account environment fast.                 | Built on Organizations + guardrails.                                                      |
| **Trusted Advisor**       | Best-practice recommendations.                | Cost, performance, security, fault tolerance, limits checks.            | Full checks need Business/Enterprise support.                                             |
| **Service Catalog**       | Curated approved products.                    | Let teams self-serve approved IaC products.                             | Governance + standardization.                                                             |
| **License Manager**       | Track software licenses.                      | BYOL compliance.                                                        | —                                                                                         |
| **Health Dashboard**      | Service & account health events.              | AWS outages + events affecting your resources.                          | —                                                                                         |
| **Compute Optimizer**     | Right-sizing recommendations (ML).            | Optimise EC2/EBS/Lambda/ASG cost & performance.                         | —                                                                                         |

> [!tip] Audit vs Config trap
> **CloudTrail = "who made the API call"** (audit). **Config = "what is the configuration / is it compliant / what changed"** (state). Keyless EC2 access → **SSM Session Manager**.

[⬆ Back to top](#table-of-contents)

---

## Monitoring & Observability

| Service                          | What it is                              | When to use                                                | Used for / Watch-outs                                                                     |
| -------------------------------- | --------------------------------------- | ---------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| **CloudWatch Metrics**           | Metrics & dashboards.                   | Monitor performance, set baselines.                        | Standard (5-min) vs **detailed (1-min)** vs **custom metrics** (e.g. memory needs agent). |
| **CloudWatch Alarms**            | Threshold-based alarms.                 | Trigger scaling/SNS/actions on metrics.                    | Composite alarms; ties to ASG & SNS.                                                      |
| **CloudWatch Logs**              | Centralised log collection.             | App/system logs, metric filters, retention.                | Needs **CloudWatch Agent** for on-instance logs/memory.                                   |
| **EventBridge (scheduling)**     | Cron/scheduled & event-driven triggers. | Scheduled Lambda, react to AWS events.                     | See [Application Integration](#application-integration).                                                         |
| **X-Ray**                        | Distributed tracing.                    | Debug latency/bottlenecks in microservices.                | Traces requests across Lambda/ECS/API GW.                                                 |
| **Managed Grafana / Prometheus** | Managed observability stack.            | Container/metrics dashboards at scale, open-source compat. | —                                                                                         |

> [!tip] Monitoring traps
> **Memory/disk usage are NOT default metrics** — need the **CloudWatch Agent** (custom metrics). Latency across microservices → **X-Ray**.

[⬆ Back to top](#table-of-contents)

---

## Migration & Transfer

| Service                                 | What it is                        | When to use                                                      | Used for / Watch-outs                                                                |
| --------------------------------------- | --------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| **DMS**                                 | Database Migration Service.       | Migrate DBs with minimal downtime; homogeneous or heterogeneous. | Source keeps running. Pair with **SCT** (Schema Conversion Tool) for engine changes. |
| **Snowball / Snowball Edge**            | Physical data transfer appliance. | TBs–PBs offline transfer; poor bandwidth sites.                  | Edge has compute too.                                                                |
| **Snowmobile**                          | Exabyte-scale truck.              | 100 PB+ data center evacuation.                                  | Rare, extreme scale.                                                                 |
| **DataSync**                            | Online data transfer/sync.        | On-prem ↔ AWS file/object transfer over network.                 | NFS/SMB → S3/EFS/FSx; scheduled, incremental.                                        |
| **Transfer Family**                     | Managed SFTP/FTPS/FTP.            | Replace existing SFTP servers landing into S3/EFS.               | —                                                                                    |
| **Migration Hub**                       | Track migrations centrally.       | Visibility across migration tools.                               | —                                                                                    |
| **Application Migration Service (MGN)** | Lift-and-shift servers to EC2.    | Rehost on-prem/VM workloads.                                     | Block-level replication.                                                             |

> [!tip] Transfer decision
> Bandwidth-limited / huge offline → **Snowball**. Ongoing online sync → **DataSync**. DB migration (live) → **DMS** (+SCT if changing engine). Managed SFTP → **Transfer Family**.

[⬆ Back to top](#table-of-contents)

---

## Analytics

| Service                   | What it is                     | When to use                                                                               | Used for / Watch-outs                                                     |
| ------------------------- | ------------------------------ | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| **Athena**                | Serverless SQL on S3.          | Ad-hoc queries on S3 data, pay-per-scan.                                                  | No infra; cheaper with Parquet/partitioning. Pairs with **Glue Catalog**. |
| **Glue**                  | Serverless ETL + Data Catalog. | Prepare/transform data, schema discovery (crawlers).                                      | Catalog feeds Athena/Redshift Spectrum.                                   |
| **Kinesis Data Streams**  | Real-time streaming ingestion. | Low-latency custom stream processing, ordered shards.                                     | You manage consumers; retention; **real-time**.                           |
| **Kinesis Data Firehose** | Managed delivery stream.       | Load streaming data into S3/Redshift/OpenSearch.                                          | **Near-real-time**, auto-scaling, no code; buffering + transform.         |
| **Kinesis vs SQS**        | —                              | Streaming/ordered/multi-consumer replay → **Kinesis**; simple decoupling queue → **SQS**. | Common trap.                                                              |
| **EMR**                   | Managed Hadoop/Spark.          | Big-data processing frameworks at scale.                                                  | Use Spot for cost.                                                        |
| **QuickSight**            | Serverless BI dashboards.      | Visualisation/BI for business users.                                                      | SPICE in-memory engine.                                                   |
| **Lake Formation**        | Build/secure data lakes.       | Centralised data-lake permissions on S3.                                                  | Sits over Glue/S3.                                                        |
| **MSK**                   | Managed Apache Kafka.          | Existing Kafka workloads.                                                                 | Choose over Kinesis for Kafka compatibility.                              |

> [!tip] Streaming traps
> **Firehose = near-real-time, zero-admin load to S3/Redshift.** **Data Streams = real-time, custom consumers, replay.** Query S3 with SQL, no servers → **Athena**.

[⬆ Back to top](#table-of-contents)

---

## Cost Management

| Service                            | What it is                    | When to use                                                    | Used for / Watch-outs                                     |
| ---------------------------------- | ----------------------------- | -------------------------------------------------------------- | --------------------------------------------------------- |
| **Cost Explorer**                  | Visualise & forecast spend.   | Analyse cost trends, RI/SP recommendations.                    | Historical + forecast.                                    |
| **AWS Budgets**                    | Custom budgets + alerts.      | Alert/act when cost or usage crosses threshold.                | Cost, usage, RI/SP coverage budgets; can trigger actions. |
| **Cost & Usage Report (CUR)**      | Most granular billing data.   | Detailed line-item analysis (to S3 / Athena / QuickSight).     | Deepest detail.                                           |
| **Savings Plans**                  | Flexible commitment discount. | Steady compute usage, 1–3 yr, flexible across instance/region. | Simpler than RIs; **Compute SP** = most flexible.         |
| **Reserved Instances**             | Capacity/discount commitment. | Steady, predictable instance usage.                            | Standard (cheapest, less flexible) vs Convertible.        |
| **Billing / Consolidated Billing** | Org-level billing.            | One bill, volume discounts across accounts.                    | Via Organizations.                                        |

> [!tip] Cost traps
> **Alert on spend → Budgets.** **Analyse/forecast → Cost Explorer.** **Line-item deep dive → CUR.** Steady compute, want flexibility → **Savings Plans**; fault-tolerant → **Spot**.

[⬆ Back to top](#table-of-contents)

---

## High-Level Decision Triggers

| If the question stresses…                                   | Lean toward…                                                                        |
| ----------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| **Least operational overhead / fully managed / serverless** | Lambda, Fargate, DynamoDB, Aurora Serverless, S3, SQS/SNS, EventBridge              |
| **Lowest cost / fault-tolerant**                            | Spot, S3 Glacier, Reserved/Savings Plans, Intelligent-Tiering                       |
| **High availability**                                       | Multi-AZ, ASG across AZs, ELB, Route 53 failover, multi-AZ NAT                      |
| **Disaster recovery / cross-region**                        | Aurora Global DB, DynamoDB Global Tables, S3 CRR, AWS Backup cross-region, Route 53 |
| **Decouple components**                                     | SQS (queue), SNS (fan-out), EventBridge (routing)                                   |
| **Private connectivity (no internet)**                      | VPC Endpoints (Gateway free for S3/DDB), PrivateLink, Direct Connect                |
| **Secure secrets / encryption**                             | KMS, Secrets Manager (rotation), Parameter Store (cheap), CloudHSM (FIPS L3)        |
| **Audit / compliance**                                      | CloudTrail (API calls), Config (resource state), Security Hub, GuardDuty            |
| **Scale reads on a relational DB**                          | Read Replicas (RDS/Aurora), ElastiCache, DAX (DynamoDB)                             |
| **Global low latency**                                      | CloudFront (HTTP/cache), Global Accelerator (any protocol + static IP)              |

[⬆ Back to top](#table-of-contents)

---

## Exam Keyword → Service Map

| Keyword in question                                               | Likely answer                           |
| ----------------------------------------------------------------- | --------------------------------------- |
| "decouple", "buffer", "asynchronous", "queue"                     | **SQS**                                 |
| "fan-out", "notify multiple", "publish/subscribe"                 | **SNS**                                 |
| "route events", "schedule", "cron", "SaaS events"                 | **EventBridge**                         |
| "orchestrate", "workflow", "multiple steps", "retries"            | **Step Functions**                      |
| "single-digit millisecond", "key-value at scale", "serverless DB" | **DynamoDB**                            |
| "in-memory cache", "reduce DB load", "sub-millisecond"            | **ElastiCache**                         |
| "data warehouse", "OLAP", "complex analytics queries"             | **Redshift**                            |
| "query S3 with SQL", "ad-hoc", "pay per query"                    | **Athena**                              |
| "near-real-time load into S3/Redshift", "no code"                 | **Kinesis Firehose**                    |
| "real-time streaming", "custom consumers", "replay/shards"        | **Kinesis Data Streams**                |
| "shared file system", "POSIX", "many Linux instances"             | **EFS**                                 |
| "Windows file share", "SMB", "Active Directory"                   | **FSx for Windows**                     |
| "object storage", "static website", "backups", "data lake"        | **S3**                                  |
| "archive", "rarely accessed", "lowest storage cost"               | **S3 Glacier / Deep Archive**           |
| "no SSH keys", "no bastion", "shell into instance"                | **SSM Session Manager**                 |
| "who made the API call", "audit account activity"                 | **CloudTrail**                          |
| "is the resource compliant", "config changed"                     | **AWS Config**                          |
| "auto-rotate database credentials"                                | **Secrets Manager**                     |
| "detect threats from logs", "malicious activity"                  | **GuardDuty**                           |
| "find PII / sensitive data in S3"                                 | **Macie**                               |
| "DDoS protection"                                                 | **Shield (+ WAF for layer 7)**          |
| "max permissions guardrail across accounts"                       | **SCP (Organizations)**                 |
| "private access to S3 without internet"                           | **Gateway VPC Endpoint**                |
| "connect many VPCs + on-prem at scale"                            | **Transit Gateway**                     |
| "global static IP + fast failover, any protocol"                  | **Global Accelerator**                  |
| "cache content near users, lower latency (HTTP)"                  | **CloudFront**                          |
| "huge offline data transfer, limited bandwidth"                   | **Snowball**                            |
| "ongoing online file transfer/sync to AWS"                        | **DataSync**                            |
| "migrate database with minimal downtime"                          | **DMS (+ SCT)**                         |
| "lift-and-shift servers to EC2"                                   | **Application Migration Service (MGN)** |
| "alert when spend exceeds budget"                                 | **AWS Budgets**                         |
| "right-size instances", "cost/perf recommendations"               | **Compute Optimizer / Trusted Advisor** |

[⬆ Back to top](#table-of-contents)
