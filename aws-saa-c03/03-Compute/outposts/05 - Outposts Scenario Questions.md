# AWS Outposts - Scenario Questions

> Exam-style scenario questions with full reasoning and "why the distractors are wrong." Covers use-case identification, Outposts vs Local Zones vs Wavelength vs Snow, connectivity, resilience traps, and per-service nuances. Cover the answer and reason first.

See also: [01 - Outposts Intro](01%20-%20Outposts%20Intro.md) · [02 - Outposts Architecture Deep Dive](02%20-%20Outposts%20Architecture%20Deep%20Dive.md) · [03 - Outposts Services Deep Dive](03%20-%20Outposts%20Services%20Deep%20Dive.md) · [04 - Outposts Examples & Patterns](04%20-%20Outposts%20Examples%20%26%20Patterns.md) · [06 - Outposts Important Facts & Cheat Sheet](06%20-%20Outposts%20Important%20Facts%20%26%20Cheat%20Sheet.md)

---

## How to use this file

Each question lists the scenario, the options, then a collapsed answer. Try to answer before expanding. Difficulty is tagged: 🟢 recall · 🟡 application · 🔴 trap/nuance.

---

### Q1 🟢 — Core use-case identification

A municipality runs its citizen-services app on EC2 but must keep the **database on-premises** for regulatory compliance. It cannot migrate the DB to the cloud and wants a **fully managed, consistent hybrid** experience.

A) AWS Outposts
B) AWS Snowball Edge to copy data to AWS
C) AWS DataSync
D) AWS Storage Gateway

> [!success]- Answer: A — AWS Outposts
> Outposts extends AWS compute/storage into the facility, so EC2 and a managed DB run **on-prem** with the same APIs — no migration, compliance satisfied.
>
> - **B Snowball Edge** is for moving data _to_ AWS (migration not allowed here) and is temporary.
> - **C DataSync** transfers data between on-prem and cloud; it doesn't run compute locally.
> - **D Storage Gateway** gives on-prem access to _cloud_ storage; it doesn't run EC2/DB locally.

---

### Q2 🟡 — Low latency + data residency together

An architect needs a **consistent hybrid experience**, **single-digit-ms latency to on-prem systems**, and **data stored on-premises** for compliance.

A) Deploy on Outposts; use the local gateway for low-latency local access and keep data local
B) Use Outposts to store data on-prem while running all compute in the Region
C) Connect one Outpost to multiple Regions for resilience
D) Host compute on Outposts and rely solely on Direct Connect to the Region for data

> [!success]- Answer: A
> Outposts runs both compute and storage locally; the **LGW** gives low-latency local connectivity; data stays on-prem for residency.
>
> - **B** defeats the latency goal (compute round-trips to Region).
> - **C** is impossible — an Outpost attaches to **exactly one** parent Region.
> - **D** sends data to the Region, violating residency.

---

### Q3 🔴 — Outposts vs Local Zones vs Wavelength

A gaming company has three needs: (1) ultra-low latency over **5G** for mobile players; (2) single-digit-ms latency for users in a **metro with no AWS Region**; (3) on-prem hosting of an analytics DB for **data sovereignty**.

A) Outposts for all three
B) Wavelength for 5G, Local Zones for the metro, Outposts for on-prem
C) Local Zones for all three
D) Outposts for 5G, Wavelength for metro, Local Zones for on-prem

> [!success]- Answer: B
> **Wavelength** = inside 5G carrier networks; **Local Zones** = AWS-owned metro sites near users; **Outposts** = the customer's own facility.
> Mapping each requirement to the service that owns that location is the whole question.

---

### Q4 🟡 — Containers on-prem, same control plane

A company wants to run **containerized apps on-premises** managed by the **same control plane** as AWS, resilient and scalable.

A) AWS Outposts with ECS/EKS
B) Amazon ECS Anywhere
C) Amazon EKS Anywhere
D) AWS Fargate

> [!success]- Answer: A
> Outposts runs ECS/EKS on-prem with the **Region's control plane** — the "same control plane" phrase points squarely at Outposts.
>
> - **B/C Anywhere** run on **your own non-Outposts hardware** (different model, you manage more).
> - **D Fargate** is Region-only; not available on Outposts.

---

### Q5 🔴 — The HA trap

Your app runs on EC2. Which part of the AWS **global infrastructure** makes it resilient and highly available?

A) AWS Outposts
B) Availability Zones
C) Edge Locations
D) AWS data centers

> [!success]- Answer: B — Availability Zones
> Classic trap. **AZs** provide HA in the cloud. **Outposts** extends AWS **to on-prem** and is itself a **single AZ / SPOF** — it does not provide cloud HA.

---

### Q6 🔴 — Service-link outage behavior

An Outpost loses its connection (service link) to the parent Region for several hours. What happens?

A) All instances on the Outpost stop immediately
B) Running instances keep operating locally, but you can't launch new instances or make management changes until the link returns
C) The Outpost fails over to a second Region automatically
D) Workloads migrate to the parent Region automatically

> [!success]- Answer: B
> The **data plane is local** (running workloads continue); the **control plane is in the Region** (no new launches/API/management). No auto-failover to another Region (an Outpost has only one parent Region), and no automatic migration.

---

### Q7 🟡 — Snapshots that must stay on-prem

A regulated workload on Outposts requires that **EBS backups never leave the premises**. What do you use?

A) Default EBS snapshots (stored in the Region)
B) EBS **local snapshots** on S3 on Outposts
C) AWS Backup to a Region vault
D) Storage Gateway volume gateway

> [!success]- Answer: B — EBS local snapshots on S3 on Outposts
> Local snapshots stay on the Outpost (needs S3 on Outposts capacity), satisfying residency and surviving a link outage.
>
> - **A/C** store data in the Region — violates "never leave premises."
> - **D** is a different on-prem-to-cloud caching product, not Outposts snapshots.

---

### Q8 🔴 — RDS backups nuance

A hospital deploys **RDS on Outposts (PostgreSQL)** for residency. An auditor notes that **even database backups must remain on-site**. Is RDS on Outposts sufficient?

A) Yes — everything about RDS on Outposts stays local
B) No — RDS on Outposts stores automated backups/snapshots in the parent Region's S3; for fully local backups consider a self-managed DB on EC2 with EBS local snapshots
C) Yes — backups go to S3 on Outposts automatically
D) No — RDS is not supported on Outposts at all

> [!success]- Answer: B
> The live DB is local, but **RDS backups go to the Region**. If backups must also stay local, run the DB yourself on EC2 and use **EBS local snapshots**. (RDS _is_ supported on Outposts racks, so D is wrong.)

---

### Q9 🟡 — Form factor selection

A retail chain needs AWS compute in **hundreds of small stores** with limited space and power, running POS containers locally. Which Outposts option fits?

A) Outposts 42U racks in each store
B) Outposts servers (1U/2U) with a Local Network Interface
C) Local Zones
D) Wavelength

> [!success]- Answer: B — Outposts servers
> Small footprint per store → **servers**, which use an **LNI** to sit on the store LAN. Racks (A) need data-center power/space. Local Zones/Wavelength aren't in _your_ building.

---

### Q10 🔴 — LGW vs LNI trap

An architect deploying **Outposts servers** at edge sites writes a design referencing the **Local Gateway** for on-prem routing. What's the issue?

A) Nothing — servers use a Local Gateway
B) Servers don't have a Local Gateway; they use a **Local Network Interface (LNI)** — LGW is a **racks-only** feature
C) LGW is only for internet egress
D) Servers must use Direct Connect instead

> [!success]- Answer: B
> **LGW = racks. LNI = servers.** This swap is a common distractor.

---

### Q11 🟡 — Disconnection-tolerant Kubernetes

A workload on Outposts must keep its **Kubernetes scheduling and self-healing working even if the link to AWS drops**. Which EKS option?

A) EKS extended cluster (control plane in Region)
B) EKS local cluster (control plane on the Outpost)
C) EKS Anywhere on separate hardware
D) Self-managed Kubernetes only

> [!success]- Answer: B — EKS local cluster
> Local cluster runs the **control plane on the Outpost**, so it keeps scheduling during a partition. Extended clusters (A) lose the Region-hosted control plane.

---

### Q12 🟡 — Connectivity choice

For a production Outpost, which **service-link** connectivity gives the most predictable performance?

A) Public internet
B) AWS Direct Connect (recommended)
C) No connection — Outposts is fully offline
D) Inter-Region peering

> [!success]- Answer: B — Direct Connect
> DX gives predictable bandwidth/jitter for control-plane + VPC traffic. Internet works but is less predictable. Outposts always needs _some_ link (so C is wrong).

---

### Q13 🔴 — Outposts vs Snow Family

A geological survey team needs compute and storage at a **temporary remote field site for ~3 months**, with rugged portable hardware and later data transfer to AWS.

A) AWS Outposts racks
B) AWS Snowball Edge / Snow Family
C) Local Zones
D) Storage Gateway

> [!success]- Answer: B — Snow Family
> **Temporary, portable, rugged, short-term** → Snow Family. Outposts is a **permanent, 3-year, data-center-grade** install with weeks of lead time — wrong for a 3-month field deployment.

---

### Q14 🟡 — Local object storage via S3 API

An app must read/write objects via the **S3 API** but the data **must remain on-premises**. Later, aggregates should be archived to the cloud.

A) S3 on Outposts, then DataSync to Region S3 for archives
B) Regional S3 with a VPC endpoint
C) EFS on Outposts
D) FSx for Windows on Outposts

> [!success]- Answer: A
> **S3 on Outposts** keeps objects local with an S3-compatible API (via access points); **DataSync** later moves aggregates to the Region. Regional S3 (B) would store data in the cloud, violating residency.

---

### Q15 🔴 — No Spot on Outposts

A team wants to cut costs on Outposts EC2 by using **Spot Instances** for batch jobs. Advice?

A) Use Spot — it's cheapest on Outposts
B) Spot Instances are **not available on Outposts**; capacity is pre-purchased on fixed hardware, so plan via capacity tasks and burst batch to the Region for Spot
C) Spot works only for Graviton on Outposts
D) Convert the Outpost to Local Zones for Spot

> [!success]- Answer: B
> No spare-capacity marketplace exists on your fixed Outpost hardware, so **no Spot**. For Spot economics, run the batch in the **Region**.

---

### Q16 🟡 — HA across sites

A factory needs its on-prem app to survive the **loss of a single Outpost**. What's the right design?

A) One larger Outpost with more racks
B) Two Outposts at different sites with RDS on Outposts Multi-AZ / app replication, plus Region for DR
C) Outposts plus Edge Locations
D) Enable Multi-AZ within the single Outpost

> [!success]- Answer: B
> A single Outpost is one AZ/SPOF; HA requires **two Outposts**. You cannot get Multi-AZ "within" one Outpost (D) — it maps to a single AZ. More racks (A) don't remove the single-site failure domain.

---

### Q17 🟢 — Who secures what

On Outposts, who is responsible for **physical security** of the hardware and for **service-level security** (IAM, security groups, bucket policies)?

A) AWS handles both
B) Physical security = customer (it's in their facility); service-level security = customer (same as cloud); hardware maintenance/patching = AWS
C) Customer handles both physical and hardware maintenance
D) AWS secures the data, customer secures nothing

> [!success]- Answer: B
> Customer owns **physical custody** + **service-level config**; AWS owns **hardware maintenance and software/firmware updates**. Service security mirrors the cloud exactly.

---

### Q18 🔴 — Fargate distractor

A team wants **serverless containers (no EC2 to manage)** running **on their Outpost**. What should you tell them?

A) Use Fargate on the Outpost
B) Fargate isn't available on Outposts — you bring EC2 capacity for ECS/EKS on Outposts; Fargate is Region-only
C) Use Lambda on the Outpost instead
D) Use App Runner on the Outpost

> [!success]- Answer: B
> Outposts containers run on **your EC2 capacity**. Fargate, Lambda, and App Runner are **Region** services, not Outposts data-plane services.

---

## Rapid-fire trigger drills

| Stimulus in the question              | Answer                                                      |
| :------------------------------------ | :---------------------------------------------------------- |
| "Data must never leave the building"  | Outposts (+ S3/EBS local snapshots)                         |
| "Single-digit ms to on-prem machines" | Outposts                                                    |
| "Same control plane on-prem"          | Outposts (ECS/EKS), not _Anywhere_                          |
| "Metro users, no Region nearby"       | Local Zones                                                 |
| "5G mobile edge"                      | Wavelength                                                  |
| "Temporary rugged field compute"      | Snow Family                                                 |
| "Make my cloud app HA"                | Availability Zones (not Outposts)                           |
| "Survive losing the AWS link (k8s)"   | EKS local cluster                                           |
| "One Outpost, multiple Regions"       | Impossible — one parent Region                              |
| "Spot on Outposts"                    | Not available                                               |
| "Backups must stay on-prem too"       | Self-managed DB + EBS local snapshots (not RDS on Outposts) |

> Next: [06 - Outposts Important Facts & Cheat Sheet](06%20-%20Outposts%20Important%20Facts%20%26%20Cheat%20Sheet.md) — the one-page exam cram.
