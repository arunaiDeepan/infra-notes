# VMware Cloud on AWS - Scenario Questions

> Exam-style scenario questions with full reasoning and "why the distractors are wrong." Covers VMC vs Outposts vs native-EC2 migration, HCX, stretched clusters, the native-AWS ENI, DR, Hybrid Linked Mode, and shared responsibility. Cover the answer first and reason it out before expanding.

See also: [01 - VMware Cloud on AWS Intro](01%20-%20VMware%20Cloud%20on%20AWS%20Intro.md) · [02 - VMware Cloud Architecture Deep Dive](02%20-%20VMware%20Cloud%20Architecture%20Deep%20Dive.md) · [03 - VMware Cloud Networking, Migration & Integration Deep Dive](03%20-%20VMware%20Cloud%20Networking%2C%20Migration%20%26%20Integration%20Deep%20Dive.md) · [04 - VMware Cloud Examples & Patterns](04%20-%20VMware%20Cloud%20Examples%20%26%20Patterns.md) · [06 - VMware Cloud Important Facts & Cheat Sheet](06%20-%20VMware%20Cloud%20Important%20Facts%20%26%20Cheat%20Sheet.md)

---

## How to use this file

Each question lists the scenario, the options, then a collapsed answer. Try to answer before expanding. Difficulty: 🟢 recall · 🟡 application · 🔴 trap/nuance.

---

### Q1 🟢 — Core identification

A company runs **hundreds of VMware vSphere VMs** on-prem and wants to migrate to AWS **with minimal changes**, keeping its **existing VMware tools and skills**. Which service fits best?

A) Rehost everything to native EC2 with AWS MGN
B) VMware Cloud on AWS
C) AWS Outposts
D) Amazon EKS

> [!success]- Answer: B — VMware Cloud on AWS
> Keep the **VMware operating model** and **lift-and-shift VMs as-is** → VMware Cloud on AWS.
> - **A** converts VMs to native EC2 — more change, drops the VMware tooling.
> - **C Outposts** puts AWS hardware in *your* data center; it doesn't migrate you *to* AWS.
> - **D EKS** is Kubernetes, unrelated to lifting vSphere VMs.

---

### Q2 🔴 — VMC vs Outposts

A manufacturer must run AWS-managed services **inside its own factory** for **data residency and low latency to on-prem machines**. Which service?

A) VMware Cloud on AWS
B) AWS Outposts
C) AWS Local Zones
D) AWS Wavelength

> [!success]- Answer: B — AWS Outposts
> "AWS services **in your own facility**, data residency, low latency to **on-prem** systems" → **Outposts**. VMware Cloud on AWS (A) runs in **AWS** data centers, so it can't satisfy on-prem residency. (See [01 - Outposts Intro](01%20-%20Outposts%20Intro.md).)

---

### Q3 🟡 — Migrating with minimal downtime

A team needs to migrate **many VMs to VMware Cloud on AWS** with **near-zero downtime** and **without changing their IP addresses**. Which tool/feature?

A) AWS DataSync
B) VMware HCX with bulk/vMotion migration and L2 Network Extension
C) AWS Snowball
D) Database Migration Service (DMS)

> [!success]- Answer: B — VMware HCX (+ L2 Network Extension)
> **HCX** performs live vMotion / bulk migration with **minimal downtime**, and **L2 Network Extension** stretches on-prem networks so VMs **keep their IPs**.
> - DataSync (A) moves file/object data, not live VMs.
> - Snowball (C) is offline bulk transfer.
> - DMS (D) migrates databases, not VMs.

---

### Q4 🔴 — Surviving an AZ failure

A production VMware workload on VMC must keep running through a **full Availability Zone outage**. What should you configure?

A) Rely on vSphere HA within the cluster
B) Deploy a stretched cluster across two AZs (synchronous vSAN)
C) Take nightly snapshots to S3
D) Enable Elastic DRS

> [!success]- Answer: B — Stretched cluster across two AZs
> vSphere HA (A) only restarts VMs after a **host** failure within one AZ. To survive a **whole AZ**, use a **stretched cluster** spanning two AZs with synchronous vSAN. Snapshots (C) are backup, not HA. Elastic DRS (D) scales host count, not AZ resilience.

---

### Q5 🟡 — Accessing native AWS services

VMs in a VMC SDDC need **fast, private, low-cost** access to **Amazon S3 and RDS**. What provides this, and how do you avoid egress charges?

A) Public internet gateway; charges are unavoidable
B) The high-bandwidth ENI to the connected VPC; place the SDDC in the same AZ as the services to avoid egress charges
C) A NAT gateway in the SDDC
D) VMware HCX

> [!success]- Answer: B — ENI + same-AZ placement
> The SDDC's **ENI** to the **connected VPC** gives private, high-bandwidth access; keeping the SDDC in the **same AZ** as S3/RDS avoids cross-AZ **egress charges**. HCX (D) is for migration, not runtime service access.

---

### Q6 🔴 — When NOT to use VMC

A startup will **refactor its few VMs into native EC2 and containers** as part of the move and doesn't care about keeping VMware tooling. Best approach?

A) VMware Cloud on AWS
B) Rehost/refactor to native AWS using AWS Application Migration Service (MGN)
C) AWS Outposts
D) Stretched cluster on VMC

> [!success]- Answer: B — Native AWS via MGN
> If you're **dropping the VMware operating model** and converting to native EC2/containers, VMC's value (keep VMware as-is) doesn't apply. Use **AWS MGN** to rehost, then refactor. VMC (A, D) is for keeping the VMware stack.

---

### Q7 🟡 — Single-pane management

During a phased migration, admins want to manage **on-prem vCenter and the cloud SDDC vCenter together** from one console. What enables this?

A) AWS Systems Manager
B) Hybrid Linked Mode
C) VMware HCX
D) AWS Organizations

> [!success]- Answer: B — Hybrid Linked Mode
> **Hybrid Linked Mode** links on-prem and SDDC vCenters into a **single inventory/console**. HCX (C) moves VMs; it isn't the management-console linkage. Systems Manager/Organizations are AWS-native and not vCenter linkage.

---

### Q8 🔴 — Shared responsibility

On VMware Cloud on AWS, who is responsible for **patching the ESXi hypervisor and vCenter**, and who patches the **guest OS**?

A) Customer patches everything
B) VMware/AWS patch the SDDC software (ESXi/vCenter/vSAN/NSX); the customer patches the guest OS and apps
C) AWS patches everything including guest OS
D) VMware patches the guest OS; customer patches ESXi

> [!success]- Answer: B
> It's a **managed service**: VMware/AWS handle the **SDDC software and hardware** lifecycle; the **customer** still owns **guest OS, applications, and data** (and backups). This differs from self-managed EC2 where you'd patch more.

---

### Q9 🟡 — Disaster recovery target

A company wants AWS to be a **DR site for its on-prem VMware workloads** with **pilot-light economics** (avoid paying for a full standby site 24/7). Best fit?

A) VMware Cloud Disaster Recovery (on-demand)
B) A second on-prem data center
C) Replicate VMs to S3 only
D) AWS Backup for EC2

> [!success]- Answer: A — VMware Cloud DR
> **VMware Cloud DR** provides an efficient cloud recovery store and **on-demand** SDDC capacity (pilot-light), so you avoid funding a full standby environment continuously. (VMware Site Recovery/SRM is the orchestrated-failover alternative.)

---

### Q10 🔴 — Scaling connectivity

An enterprise has **multiple SDDCs and many VPCs** that all need to interconnect at high bandwidth, plus on-prem reachability. What should they use?

A) One connected-VPC ENI per SDDC and nothing else
B) VMware Transit Connect (a VMware-managed Transit Gateway)
C) VPC peering mesh between every pair
D) Public internet routing

> [!success]- Answer: B — VMware Transit Connect (VTGW)
> **Transit Connect** is the Transit-Gateway-style hub for **SDDC-to-SDDC, SDDC-to-VPC, and SDDC-to-on-prem** at scale. A single connected-VPC ENI (A) is fine for simple cases; a peering mesh (C) doesn't scale.

---

### Q11 🟡 — What hardware does it run on?

VMware Cloud on AWS runs the VMware SDDC on what kind of AWS infrastructure?

A) Shared multi-tenant EC2 instances
B) Dedicated, single-tenant AWS bare-metal hosts
C) AWS Lambda functions
D) Fargate containers

> [!success]- Answer: B — Dedicated bare-metal hosts
> The ESXi hypervisor runs directly on **dedicated, single-tenant AWS bare-metal EC2 hosts** (e.g., i3.metal-class). It is not multi-tenant, serverless, or containerized.

---

### Q12 🔴 — Cost optimization

A steady, predictable VMware workload runs 24/7 on VMC. Which combination best optimizes cost?

A) On-demand hosts only
B) 1- or 3-year host subscriptions + Elastic DRS right-sizing + same-AZ ENI to AWS services
C) Move it to Outposts
D) Run it on the public internet to cut ENI costs

> [!success]- Answer: B
> For steady workloads, **1/3-year commitments** cut host cost; **Elastic DRS** right-sizes host count; **same-AZ ENI** avoids egress charges to native AWS. On-demand only (A) is pricier for steady load.

---

### Q13 🟡 — Modernization path

After migrating VMs to VMC, a team wants to **offload its database to a managed service** with minimal disruption. What's the typical approach?

A) Keep the DB on a VM forever; managed DBs aren't reachable
B) Move the database to Amazon RDS/Aurora and reach it over the same-AZ ENI
C) Re-migrate the whole SDDC to Outposts
D) Use HCX to convert the DB to DynamoDB

> [!success]- Answer: B — RDS/Aurora over the ENI
> The "migrate first, modernize later" pattern: VMs in VMC reach **RDS/Aurora** privately over the **same-AZ ENI**, so you offload the DB to a managed service incrementally. HCX (D) migrates VMs, not DB engine conversions.

---

### Q14 🔴 — Outposts wording trap

A scenario says: "We want a **cloud** environment that uses our **existing VMware vSphere skills**, but the hardware must be in an **AWS Region**, not our building." VMC or Outposts?

A) Outposts — it's hybrid
B) VMware Cloud on AWS — VMware stack on AWS hardware **in an AWS Region**
C) Either works identically
D) Local Zones

> [!success]- Answer: B — VMware Cloud on AWS
> "VMware skills + hardware **in an AWS Region** (not our building)" → **VMC**. Outposts would put the hardware **in your building**, which the scenario explicitly rules out.

---

### Q15 🟡 — Migration link choice

For a **large VMware migration** requiring **consistent high bandwidth and low latency**, which on-prem-to-SDDC connection is preferred?

A) IPsec VPN over the internet
B) AWS Direct Connect
C) Public S3 endpoints
D) CloudFront

> [!success]- Answer: B — AWS Direct Connect
> **Direct Connect** gives private, consistent, high-bandwidth/low-latency connectivity — preferred for large migrations and steady hybrid traffic. VPN (A) is the quicker/cheaper or backup path; HCX rides over either.

---

## Rapid-fire trigger drills

| Stimulus in the question | Answer |
| :--- | :--- |
| "Migrate **VMware vSphere** VMs to AWS, **minimal change**, keep tools" | **VMware Cloud on AWS** |
| "AWS services **in our own data center** / on-prem data residency" | **Outposts** |
| "**Convert** VMs to native EC2/containers" | **Rehost via AWS MGN** (not VMC) |
| "Migrate **many VMs, near-zero downtime, keep IPs**" | **HCX** (bulk/vMotion + **L2 extension**) |
| "Survive a **full AZ** outage" | **Stretched cluster across 2 AZs** |
| "Only **host** failure tolerance needed" | **vSphere HA** |
| "VMs reach **S3/RDS** privately & cheaply" | **ENI to connected VPC, same AZ** |
| "**Single pane** for on-prem + cloud vCenter" | **Hybrid Linked Mode** |
| "AWS as **DR site** for VMware, pilot-light" | **VMware Cloud DR** (or **Site Recovery/SRM**) |
| "Connect **many SDDCs/VPCs** at scale" | **VMware Transit Connect (VTGW)** |
| "What hardware?" | **Dedicated bare-metal hosts** |
| "Who patches ESXi/vCenter vs guest OS" | **VMware/AWS** vs **customer** |

> Next: [06 - VMware Cloud Important Facts & Cheat Sheet](06%20-%20VMware%20Cloud%20Important%20Facts%20%26%20Cheat%20Sheet.md) — the one-page exam cram.
