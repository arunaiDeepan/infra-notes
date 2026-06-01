# EC2 & ASG Scenario Questions (SAA-C03)

> Exam-style scenarios with full reasoning and "why the distractors are wrong," spanning instance selection, storage, networking/placement, pricing, and Auto Scaling. Answers are in collapsible blocks (`<details>`) that work in **both Obsidian and GitHub** — try before you expand. Difficulty: 🟢 recall · 🟡 application · 🔴 trap/nuance.

> **EC2 + ASG series:** [01 - EC2 Intro](01%20-%20EC2%20Intro.md) · [02 - EC2 Instance Types Deep Dive](02%20-%20EC2%20Instance%20Types%20Deep%20Dive.md) · [03 - EC2 Storage Deep Dive](03%20-%20EC2%20Storage%20Deep%20Dive.md) · [04 - EC2 Networking, Placement & Metadata Deep Dive](04%20-%20EC2%20Networking%2C%20Placement%20%26%20Metadata%20Deep%20Dive.md) · [05 - EC2 Pricing & Purchasing Options Deep Dive](05%20-%20EC2%20Pricing%20%26%20Purchasing%20Options%20Deep%20Dive.md) · [06 - EC2 Auto Scaling (ASG)](06%20-%20EC2%20Auto%20Scaling%20%28ASG%29.md) · [07 - ASG Architecture & Advanced Deep Dive](07%20-%20ASG%20Architecture%20%26%20Advanced%20Deep%20Dive.md) · [08 - EC2 & ASG Architecture Patterns & Examples](08%20-%20EC2%20%26%20ASG%20Architecture%20Patterns%20%26%20Examples.md) · [09 - EC2 & ASG Scenario Questions](09%20-%20EC2%20%26%20ASG%20Scenario%20Questions.md) · [10 - EC2 & ASG Important Facts & Cheat Sheet](10%20-%20EC2%20%26%20ASG%20Important%20Facts%20%26%20Cheat%20Sheet.md)

---

## Table of Contents

- [Instance Selection](#instance-selection)
- [Storage](#storage)
- [Networking & Placement](#networking--placement)
- [Pricing & Purchasing](#pricing--purchasing)
- [Auto Scaling](#auto-scaling)
- [Rapid-Fire Trigger Drills](#rapid-fire-trigger-drills)

---

## Instance Selection

### Q1 🟢 — Bursty web server

A small web server idles at ~10% CPU but spikes to 80% for a few minutes each hour. The team wants the lowest cost without throttling during spikes.

A) c5.large On-Demand · B) t3.large in Unlimited mode · C) m5.large Reserved · D) r5.large Spot

<details><summary>Answer</summary>

**B — t3.large (Unlimited mode).** Burstable T-family is cheapest for mostly-idle workloads; **Unlimited mode** lets it burst through spikes without throttling. C/M over-provision for a mostly-idle server; R is memory-optimized and Spot risks interruption for a user-facing server. See [02 - EC2 Instance Types Deep Dive > Burstable T-Family & CPU Credits](02%20-%20EC2%20Instance%20Types%20Deep%20Dive.md#burstable-t-family--cpu-credits).

</details>

---

### Q2 🟡 — SAP HANA

A company is migrating a large in-memory **SAP HANA** database needing several TB of RAM.

A) c7g · B) High Memory (u-\*) / X-family · C) i4i · D) t3.2xlarge

<details><summary>Answer</summary>

**B — High Memory / X-family.** SAP HANA is the canonical memory-optimized workload; **High Memory** instances reach up to 24 TB RAM. C is compute-optimized, I is storage-optimized, T is burstable. See [02 - EC2 Instance Types Deep Dive > Memory Optimized (R, X, High Memory, z)](02%20-%20EC2%20Instance%20Types%20Deep%20Dive.md#memory-optimized-r-x-high-memory-z).

</details>

---

### Q3 🔴 — Graviton eligibility

A team wants to cut compute cost ~20–40% by moving to **Graviton (ARM)**. Which workload is the **poorest** candidate?

A) Linux Node.js microservices in containers · B) Open-source PostgreSQL · C) A **Windows Server** licensed app · D) A Go batch processor

<details><summary>Answer</summary>

**C — Windows Server.** Graviton is ARM; **Windows Server workloads don't run on Graviton**, and proprietary x86 binaries can't be recompiled. A/B/D all recompile/run on ARM. See [02 - EC2 Instance Types Deep Dive > AWS Graviton (ARM)](02%20-%20EC2%20Instance%20Types%20Deep%20Dive.md#aws-graviton-arm).

</details>

---

## Storage

### Q4 🟡 — 50,000 IOPS database

A single-instance PostgreSQL DB needs a sustained **50,000 IOPS** on one volume and can't be re-architected.

A) gp3 at 50,000 IOPS · B) io2 Block Express · C) st1 · D) Two gp2 in RAID 0

<details><summary>Answer</summary>

**B — io2 Block Express.** gp3 caps at **16,000 IOPS** (A impossible); st1 is throughput HDD; RAID-0 adds risk/complexity and the question wants one volume. io2 (and Block Express) reach 64,000–256,000 IOPS. See [03 - EC2 Storage Deep Dive > EBS Volume Types (Exam Critical)](03%20-%20EC2%20Storage%20Deep%20Dive.md#ebs-volume-types-exam-critical).

</details>

---

### Q5 🔴 — Shared storage across AZs

A fleet of **Linux** instances **across three AZs** must read and write the **same files** concurrently.

A) EBS Multi-Attach io2 · B) EFS · C) Instance store · D) gp3 attached to each

<details><summary>Answer</summary>

**B — EFS.** A shared POSIX file system across **multiple AZs** = EFS (NFS). **Multi-Attach is single-AZ block** and needs a cluster-aware FS (A wrong). Instance store is ephemeral/local; a gp3 volume attaches to one instance in one AZ. See [03 - EC2 Storage Deep Dive > Shared File Storage: EFS vs FSx](03%20-%20EC2%20Storage%20Deep%20Dive.md#shared-file-storage-efs-vs-fsx).

</details>

---

### Q6 🟡 — Windows file shares with AD

A Windows app needs an **SMB** file share integrated with **Active Directory**.

A) EFS · B) FSx for Windows File Server · C) FSx for Lustre · D) S3

<details><summary>Answer</summary>

**B — FSx for Windows File Server.** SMB + AD = FSx for Windows. EFS is NFS/Linux, Lustre is HPC, S3 is object storage. See [03 - EC2 Storage Deep Dive > Shared File Storage: EFS vs FSx](03%20-%20EC2%20Storage%20Deep%20Dive.md#shared-file-storage-efs-vs-fsx).

</details>

---

### Q7 🔴 — Encrypt an existing volume

An unencrypted EBS volume must become encrypted with the least disruption.

A) Toggle "encrypt" on the volume in place · B) Snapshot → copy snapshot with encryption → create new volume → swap · C) Use a NACL · D) Move to instance store

<details><summary>Answer</summary>

**B.** You **cannot** encrypt a volume in place. Snapshot it, **copy the snapshot with encryption enabled** (a KMS key), create a new encrypted volume, and attach it. See [03 - EC2 Storage Deep Dive > EBS Encryption](03%20-%20EC2%20Storage%20Deep%20Dive.md#ebs-encryption).

</details>

---

### Q8 🟡 — Automated backup policy

A team needs **scheduled EBS snapshots with retention/deletion** and no custom scripts.

A) Cron on each instance · B) Data Lifecycle Manager (DLM) · C) Manual snapshots · D) S3 lifecycle rules

<details><summary>Answer</summary>

**B — Data Lifecycle Manager.** DLM automates snapshot/AMI creation, retention, and deletion on a schedule. See [03 - EC2 Storage Deep Dive > EBS Snapshots, DLM & Fast Snapshot Restore](03%20-%20EC2%20Storage%20Deep%20Dive.md#ebs-snapshots-dlm--fast-snapshot-restore).

</details>

---

## Networking & Placement

### Q9 🔴 — HPC node-to-node latency

A tightly-coupled **HPC/MPI** cluster needs the **lowest possible inter-node latency** and highest throughput.

A) Spread placement group · B) Cluster placement group + EFA · C) Partition placement group · D) Multi-AZ ASG

<details><summary>Answer</summary>

**B — Cluster placement group + EFA.** Cluster packs instances on the same rack for lowest latency; **EFA** adds OS-bypass for MPI. Spread maximizes availability (opposite goal); Partition is for big-data; multi-AZ adds latency. See [04 - EC2 Networking, Placement & Metadata Deep Dive > Placement Groups (Exam Critical)](04%20-%20EC2%20Networking%2C%20Placement%20%26%20Metadata%20Deep%20Dive.md#placement-groups-exam-critical).

</details>

---

### Q10 🟡 — Block a malicious IP

A specific external IP range is attacking the app and must be **explicitly blocked** at the subnet edge.

A) Security group deny rule · B) NACL deny rule · C) Remove the SG · D) IAM policy

<details><summary>Answer</summary>

**B — NACL deny rule.** **Security groups can't deny**; a NACL (subnet-level, supports Deny) is the tool to block an IP range. See [04 - EC2 Networking, Placement & Metadata Deep Dive > Security Groups vs Network ACLs](04%20-%20EC2%20Networking%2C%20Placement%20%26%20Metadata%20Deep%20Dive.md#security-groups-vs-network-acls).

</details>

---

### Q11 🔴 — SSRF on metadata

A pen-test shows an SSRF flaw lets attackers read **IAM role credentials** from the instance metadata endpoint.

A) Move to a private subnet · B) Require IMDSv2 · C) Disable the metadata service · D) Block 169.254.169.254 with a NACL

<details><summary>Answer</summary>

**B — Require IMDSv2.** Session tokens + hop-limit defeat SSRF. Disabling metadata breaks IAM roles; NACLs can't filter the link-local address; a private subnet doesn't stop an in-instance SSRF. See [04 - EC2 Networking, Placement & Metadata Deep Dive > Instance Metadata Service (IMDSv1 vs IMDSv2)](04%20-%20EC2%20Networking%2C%20Placement%20%26%20Metadata%20Deep%20Dive.md#instance-metadata-service-imdsv1-vs-imdsv2).

</details>

---

### Q12 🟡 — Max availability for 3 quorum nodes

Three critical quorum nodes must each sit on **distinct hardware** to survive a single hardware failure.

A) Cluster placement group · B) Spread placement group · C) Partition placement group · D) Single AZ, same rack

<details><summary>Answer</summary>

**B — Spread placement group** (distinct hardware, up to 7 per AZ). Cluster shares a failure domain; Partition is for large partition-aware fleets. See [04 - EC2 Networking, Placement & Metadata Deep Dive > Placement Groups (Exam Critical)](04%20-%20EC2%20Networking%2C%20Placement%20%26%20Metadata%20Deep%20Dive.md#placement-groups-exam-critical).

</details>

---

## Pricing & Purchasing

### Q13 🟡 — Steady workload, want flexibility

A predictable 24/7 workload should get RI-level savings but the team expects to **change instance families** over the next year and also runs **Fargate**.

A) Standard RI · B) Compute Savings Plan · C) Spot · D) On-Demand

<details><summary>Answer</summary>

**B — Compute Savings Plan.** Commits to $/hr spend with flexibility across families/Regions and also covers **Fargate/Lambda**. Standard RI locks the config; Spot/On-Demand don't give committed-use discounts. See [05 - EC2 Pricing & Purchasing Options Deep Dive > Savings Plans](05%20-%20EC2%20Pricing%20%26%20Purchasing%20Options%20Deep%20Dive.md#savings-plans).

</details>

---

### Q14 🔴 — BYOL bound to sockets

A company must run **Oracle/Windows licensed per physical socket** and the license requires visibility into sockets/cores on a fixed server.

A) Dedicated Instance · B) Dedicated Host · C) Reserved Instance · D) Spot

<details><summary>Answer</summary>

**B — Dedicated Host.** Only Dedicated Hosts expose socket/core layout and host affinity for **per-socket BYOL**. A Dedicated Instance gives isolation but no socket visibility. See [05 - EC2 Pricing & Purchasing Options Deep Dive > Dedicated Hosts vs Dedicated Instances](05%20-%20EC2%20Pricing%20%26%20Purchasing%20Options%20Deep%20Dive.md#dedicated-hosts-vs-dedicated-instances).

</details>

---

### Q15 🟡 — Guaranteed AZ capacity, no commitment

For a DR drill, the team must be **certain instances can launch in a specific AZ** during a window, without a 1–3 year commitment.

A) Zonal RI · B) On-Demand Capacity Reservation · C) Compute Savings Plan · D) Spot

<details><summary>Answer</summary>

**B — On-Demand Capacity Reservation.** Reserves capacity in a specific AZ with no term commitment. A Zonal RI also reserves capacity but **requires a 1–3 yr commit**; Savings Plans **don't reserve capacity**; Spot has no guarantee. See [05 - EC2 Pricing & Purchasing Options Deep Dive > Capacity Reservations](05%20-%20EC2%20Pricing%20%26%20Purchasing%20Options%20Deep%20Dive.md#capacity-reservations).

</details>

---

### Q16 🟢 — Cheapest fault-tolerant batch

A nightly batch job is fault-tolerant, can be restarted, and has an 8-hour window.

A) On-Demand · B) Reserved · C) Spot · D) Dedicated Host

<details><summary>Answer</summary>

**C — Spot Instances.** Fault-tolerant + time-flexible = up to 90% savings on Spot. See [05 - EC2 Pricing & Purchasing Options Deep Dive > Spot Instances](05%20-%20EC2%20Pricing%20%26%20Purchasing%20Options%20Deep%20Dive.md#spot-instances).

</details>

---

## Auto Scaling

### Q17 🔴 — Instance up but app down

Users get intermittent errors, yet the ASG isn't replacing instances; EC2 status checks pass.

A) ASG uses EC2 status checks instead of ELB health checks · B) Cooldown too long · C) Bad AMI · D) Termination protection on

<details><summary>Answer</summary>

**A.** EC2 status checks only confirm the instance is _running_, not that the app is healthy. Switch the ASG **health-check type to ELB** so app failures trigger replacement. See [06 - EC2 Auto Scaling (ASG) > 🩺 Health Checks - EC2 vs ELB](06%20-%20EC2%20Auto%20Scaling%20%28ASG%29.md#-health-checks---ec2-vs-elb).

</details>

---

### Q18 🟡 — No data loss on scale-in

In-progress orders are lost when instances terminate during scale-in.

A) Increase cooldown · B) Lifecycle hook on terminate to drain · C) Target tracking · D) Termination protection

<details><summary>Answer</summary>

**B — Lifecycle hook (terminate).** Hooks pause termination so the instance can finish/drain work first. The only mechanism that runs code **before** scale-in termination. See [06 - EC2 Auto Scaling (ASG) > 🔄 Lifecycle Hooks - The Complete Guide](06%20-%20EC2%20Auto%20Scaling%20%28ASG%29.md#-lifecycle-hooks---the-complete-guide).

</details>

---

### Q19 🟡 — Slow scale-out

The app takes 8 minutes to initialize; flash-sale users see latency during scale-out.

A) Bigger instances · B) Increase max capacity · C) Warm pool · D) Longer cooldown

<details><summary>Answer</summary>

**C — Warm pool.** Pre-initialized **stopped** instances start in seconds. Flash sales are unpredictable, so scheduled pre-scaling alone won't always help. See [06 - EC2 Auto Scaling (ASG) > 🔥 Warm Pools - Reduce Scaling Latency](06%20-%20EC2%20Auto%20Scaling%20%28ASG%29.md#-warm-pools---reduce-scaling-latency).

</details>

---

### Q20 🔴 — Mixed Spot + On-Demand across types

An ASG must launch **both Spot and On-Demand** across **three instance types**.

A) Launch configuration with multiple types · B) Launch template with a mixed instances policy · C) Three separate ASGs · D) Launch configuration with Spot strategy

<details><summary>Answer</summary>

**B.** **Launch configurations don't support multiple instance types or mixed purchase options** — this requires a **launch template + mixed instances policy**. See [06 - EC2 Auto Scaling (ASG) > 🔧 Launch Templates vs Launch Configurations (Critical for Exam)](06%20-%20EC2%20Auto%20Scaling%20%28ASG%29.md#-launch-templates-vs-launch-configurations-critical-for-exam).

</details>

---

### Q21 🟡 — Predictable daily batch

A batch job runs 10 PM–6 AM nightly with consistent load; the system should scale to near-zero by day.

A) Target tracking on CPU · B) Step scaling · C) Scheduled scaling · D) Predictive only

<details><summary>Answer</summary>

**C — Scheduled scaling.** A known clock-based pattern is handled most efficiently by scheduled actions (scale up ~9:45 PM, down ~6:15 AM). See [07 - ASG Architecture & Advanced Deep Dive > Dynamic Scaling Policies Compared](07%20-%20ASG%20Architecture%20%26%20Advanced%20Deep%20Dive.md#dynamic-scaling-policies-compared).

</details>

---

### Q22 🔴 — New instances killed immediately

Newly launched ASG instances are terminated before the app finishes starting.

A) Increase the health-check grace period · B) Lower min capacity · C) Disable ELB checks · D) Use Spot

<details><summary>Answer</summary>

**A.** The **health-check grace period** is shorter than app startup, so instances are marked unhealthy mid-init. Set it longer than startup time. See [07 - ASG Architecture & Advanced Deep Dive > Cooldown vs Instance Warm-up](07%20-%20ASG%20Architecture%20%26%20Advanced%20Deep%20Dive.md#cooldown-vs-instance-warm-up).

</details>

---

### Q23 🟡 — Deploy new AMI, no downtime

Roll a new AMI across an existing ASG without dropping below capacity.

A) Delete and recreate the ASG · B) Instance Refresh with min healthy % · C) Edit launch config in place · D) Stop all instances and restart

<details><summary>Answer</summary>

**B — Instance Refresh.** Replaces instances in batches honoring a minimum healthy percentage; or use a **blue/green** second ASG. See [07 - ASG Architecture & Advanced Deep Dive > Instance Refresh & Updating the Fleet](07%20-%20ASG%20Architecture%20%26%20Advanced%20Deep%20Dive.md#instance-refresh--updating-the-fleet).

</details>

---

## Rapid-Fire Trigger Drills

| Stimulus                                        | Answer                                        |
| :---------------------------------------------- | :-------------------------------------------- |
| "Bursty, mostly idle, cheap"                    | **T3/T4g** (Unlimited if no throttle allowed) |
| "Sustained high CPU batch"                      | **C family**                                  |
| "SAP HANA / huge in-memory DB"                  | **High Memory / X**                           |
| "Highest local IOPS, replicated data"           | **Instance store (I family)**                 |
| ">64,000 IOPS single volume"                    | **io2 Block Express**                         |
| "Shared FS, Linux, multi-AZ"                    | **EFS**                                       |
| "Windows SMB + AD"                              | **FSx for Windows**                           |
| "Same block volume, several instances, one AZ"  | **EBS Multi-Attach (io2)**                    |
| "Automated snapshot lifecycle"                  | **DLM**                                       |
| "Lowest node-to-node latency / HPC"             | **Cluster PG + EFA**                          |
| "Max availability, few critical nodes"          | **Spread PG (7/AZ)**                          |
| "Explicitly block an IP range"                  | **NACL deny**                                 |
| "SSRF stealing metadata creds"                  | **Require IMDSv2**                            |
| "RI savings + flexibility + Fargate"            | **Compute Savings Plan**                      |
| "BYOL per physical socket"                      | **Dedicated Host**                            |
| "Guarantee AZ capacity, no commit"              | **On-Demand Capacity Reservation**            |
| "Cheapest fault-tolerant batch"                 | **Spot**                                      |
| "Instance running but app down, no replacement" | **ELB health check**                          |
| "No data loss on scale-in"                      | **Lifecycle hook (terminate)**                |
| "App takes minutes to boot, fast scale-out"     | **Warm pool**                                 |
| "Mixed Spot + On-Demand, multiple types"        | **Launch template + mixed instances policy**  |
| "Predictable clock-based scaling"               | **Scheduled scaling**                         |
| "Recurring forecastable pattern"                | **Predictive scaling**                        |
| "New AMI to whole ASG, no downtime"             | **Instance Refresh / blue-green**             |

[⬆ Back to top](#table-of-contents)

> Next: [10 - EC2 & ASG Important Facts & Cheat Sheet](10%20-%20EC2%20%26%20ASG%20Important%20Facts%20%26%20Cheat%20Sheet.md) — the one-page cram.
