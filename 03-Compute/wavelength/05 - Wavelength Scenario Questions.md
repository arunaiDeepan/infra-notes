# AWS Wavelength - Scenario Questions

> Exam-style scenario questions with full reasoning and "why the distractors are wrong." Covers use-case identification, Wavelength vs Local Zones vs Outposts vs CloudFront, Carrier Gateway / Carrier IP networking, resilience traps, and edge-vs-Region placement. Cover the answer and reason first.

See also: [01 - Wavelength Intro](01%20-%20Wavelength%20Intro.md) · [02 - Wavelength Architecture Deep Dive](02%20-%20Wavelength%20Architecture%20Deep%20Dive.md) · [03 - Wavelength Services & Networking Deep Dive](03%20-%20Wavelength%20Services%20%26%20Networking%20Deep%20Dive.md) · [04 - Wavelength Examples & Patterns](04%20-%20Wavelength%20Examples%20%26%20Patterns.md) · [06 - Wavelength Important Facts & Cheat Sheet](06%20-%20Wavelength%20Important%20Facts%20%26%20Cheat%20Sheet.md)

---

## How to use this file

Each question lists the scenario, the options, then a collapsed answer. Try to answer before expanding. Difficulty is tagged: 🟢 recall · 🟡 application · 🔴 trap/nuance.

---

### Q1 🟢 — Core use-case identification

A company builds a **mobile AR game** delivered over **5G** and needs **ultra-low latency** between the player's device and the rendering compute. Which AWS offering fits best?

A) AWS Outposts
B) AWS Wavelength
C) AWS Local Zones
D) Amazon CloudFront

> [!success]- Answer: B — AWS Wavelength
> Mobile + 5G + ultra-low latency to devices is the textbook Wavelength case — compute sits inside the carrier network so traffic never leaves it.
> - **A Outposts** is for on-prem workloads in *your* facility.
> - **C Local Zones** target metro end users generally, not specifically 5G/mobile.
> - **D CloudFront** caches static/dynamic content at edge locations but does not run your **interactive game compute**.

---

### Q2 🔴 — Wavelength vs Local Zones vs Outposts

A telecom-partnered firm has three needs: (1) ultra-low latency for **5G mobile** users; (2) single-digit-ms latency for users in a **metro that has no AWS Region**; (3) a database that must stay in **its own on-prem data center** for compliance.

A) Wavelength for all three
B) Wavelength for 5G, Local Zones for the metro, Outposts for on-prem
C) Local Zones for all three
D) Outposts for 5G, Wavelength for metro, Local Zones for on-prem

> [!success]- Answer: B
> **Wavelength** = inside 5G carrier networks; **Local Zones** = AWS-owned metro sites near users; **Outposts** = the customer's own facility. Map each requirement to the service that owns that location.

---

### Q3 🟡 — Which gateway for mobile reachability

You launch EC2 in a Wavelength subnet and need **5G mobile devices** to reach it. What must you configure?

A) Attach an Internet Gateway and assign an Elastic IP
B) Attach a **Carrier Gateway** and assign a **Carrier IP**
C) Attach a NAT Gateway in the Wavelength subnet
D) Peer the Wavelength subnet with the carrier VPC

> [!success]- Answer: B — Carrier Gateway + Carrier IP
> Wavelength subnets face the carrier network through a **Carrier Gateway**, which NATs to a **Carrier IP** reachable by mobile devices.
> - **A** uses Region constructs (IGW + Elastic IP) that don't serve the carrier network.
> - **C** NAT Gateway is a Region egress construct, not the carrier front door.
> - **D** there is no "carrier VPC peering" model here.

---

### Q4 🔴 — Carrier IP vs Elastic IP

An architect assigns a standard **Elastic IP** to a Wavelength instance and is surprised 5G devices can't reach it. Why?

A) Elastic IPs work fine; the issue is the security group
B) Mobile reachability requires a **Carrier IP** (carrier-network address) via the Carrier Gateway, not a Region Elastic IP
C) Wavelength instances can't have any public address
D) The instance needs a second ENI in the Region

> [!success]- Answer: B
> A **Carrier IP** is an address from the **carrier network** that the Carrier Gateway NATs to; a Region Elastic IP is not reachable from the carrier side. Allocate the address in the zone's network-border-group so it becomes a Carrier IP.

---

### Q5 🟡 — Where does the database go?

A latency-sensitive 5G app runs on EC2 in a Wavelength Zone and needs a durable relational database. Best practice?

A) Run the database in the Wavelength Zone for lowest latency
B) Keep the app tier in the Wavelength Zone and run the database (e.g., RDS Multi-AZ) in the **parent Region**, reached over the AWS backbone
C) Run the database on Outposts
D) Use DynamoDB inside the Wavelength Zone

> [!success]- Answer: B
> Wavelength is a **compute edge**, not a mini-Region — managed databases like RDS run in the **Region**. Put the latency-critical tier at the edge and keep durable state in the Region (RDS isn't a Wavelength-zone service; neither is DynamoDB).

---

### Q6 🔴 — The HA trap

A team asks how to make their single-Wavelength-Zone app **highly available**. Best guidance?

A) Deploy one larger Wavelength Zone
B) Use **multiple Wavelength Zones** with Route 53 routing/health checks, anchor durable state in the Region, and fall back to the Region if a zone fails
C) Enable Multi-AZ within the Wavelength Zone
D) Wavelength is inherently HA; nothing needed

> [!success]- Answer: B
> A single Wavelength Zone is a **single failure domain**. HA comes from **multiple zones + Region fallback**, with state in the Region. There's no "Multi-AZ within a zone" (C), and a bigger single zone (A) doesn't remove the single-site risk.

---

### Q7 🟡 — Edge ML inference

A connected-vehicle platform needs **real-time object detection** on video streamed over 5G, too time-critical to send to a Region. What's the right edge compute?

A) t3 instances in a Local Zone
B) **G4dn GPU instances in a Wavelength Zone**
C) Lambda in the parent Region
D) Outposts servers at a roadside cabinet

> [!success]- Answer: B — G4dn in a Wavelength Zone
> Real-time inference for **5G** devices → **GPU (G4dn) at the carrier edge** for millisecond responses. Local Zones (A) aren't the 5G-specific edge; Region Lambda (C) adds backhaul latency; Outposts (D) is for *your* facility, not the carrier network.

---

### Q8 🔴 — Wavelength vs CloudFront

A media company wants to reduce latency delivering **cacheable video segments** to mobile viewers worldwide. Wavelength or CloudFront?

A) Wavelength — it's the mobile edge
B) **CloudFront** — for caching/delivering content at edge locations globally; Wavelength is for **running latency-critical application compute** at the 5G edge, not a CDN
C) Both are interchangeable CDNs
D) Neither; use S3 Transfer Acceleration

> [!success]- Answer: B
> **CloudFront** is the CDN for content delivery/caching. **Wavelength** runs *compute* (game servers, inference, AR rendering) at the 5G edge. Static cacheable content → CloudFront; interactive real-time compute over 5G → Wavelength.

---

### Q9 🟡 — Opt-in behavior

A team can't launch instances into a Wavelength Zone and sees it isn't listed by default. Why?

A) Wavelength requires an Outpost first
B) Wavelength Zones are **opt-in** — you must enable the zone group in the account before using it (like Local Zones)
C) Wavelength is only available to telecom companies
D) You must open a support ticket for every launch

> [!success]- Answer: B
> Wavelength Zones (like Local Zones) are **opt-in**; enable the zone group, then create a subnet and launch. No Outpost or special account type is required.

---

### Q10 🔴 — Minimizing Region round-trips

A Wavelength app shows good device latency but feels slow because every request calls back to the Region database. Best fix?

A) Move the whole database into the Wavelength Zone
B) Cache hot/read-mostly data at the edge so most requests are served within the zone, and write-through to the Region for durability
C) Add a second Carrier Gateway
D) Switch to Outposts

> [!success]- Answer: B
> Wavelength accelerates the **device↔app** hop, not **app↔Region**. Cache/process at the edge so the per-request hot path stays in the carrier network; only misses/writes traverse the backbone. You can't run managed RDS in the zone (A).

---

### Q11 🟡 — Physical security responsibility

For a Wavelength deployment, who is responsible for **physical security** of the hardware?

A) The customer, as with Outposts
B) AWS and the **carrier** — the hardware is in the carrier's facility, so the customer has **no physical custody** burden (unlike Outposts)
C) The customer must staff the carrier site
D) No one; it's serverless

> [!success]- Answer: B
> Unlike Outposts (customer owns physical custody), Wavelength hardware sits in the **carrier's** data center. Physical security is AWS/carrier; the customer still owns **service-level** security (IAM, SGs, encryption).

---

### Q12 🔴 — Instance family limits

A team wants to run a specialized HPC instance family in a Wavelength Zone and finds it unavailable. What's the reality?

A) All Region instance families are available in every Wavelength Zone
B) Wavelength offers a **limited subset** of families (commonly t3, r5, G4dn); plan around that or run the workload in the Region
C) You must request a quota increase to unlock all families
D) Only Graviton instances run in Wavelength

> [!success]- Answer: B
> Wavelength edge sites are smaller and offer a **curated subset** of instance types (t3 / r5 / G4dn typical). Workloads needing other families run in the **Region**.

---

### Q13 🟡 — Route 53 to reach the nearest zone

An app spans Wavelength Zones in several metros. How do you send each user to the closest healthy zone?

A) A single ALB in one Wavelength Zone
B) **Route 53 latency/geolocation routing with health checks** across the zones, with the Region as fallback
C) Carrier Gateway routing decides automatically
D) CloudFront origin failover

> [!success]- Answer: B
> **Route 53** latency/geo routing + health checks directs users to the nearest healthy Wavelength Zone and fails over (to another zone or the Region). A single zonal ALB (A) doesn't span zones.

---

### Q14 🔴 — Outposts vs Wavelength wording trap

A factory wants **single-digit-ms latency to its on-prem PLCs/machines** and to keep data in its own building. Wavelength?

A) Yes — Wavelength gives the lowest latency
B) No — that's **Outposts** (on-prem, your facility, data residency); Wavelength is for **5G/mobile** users via a carrier network
C) Yes, if the factory has 5G
D) Use Local Zones

> [!success]- Answer: B
> "On-prem systems / your own building / data residency" → **Outposts**. The Wavelength discriminator is **5G/mobile end users on a carrier network**, which this scenario isn't about.

---

### Q15 🟡 — What flows over the backbone

In a Wavelength architecture, which traffic uses the **AWS network backbone** rather than the carrier network?

A) Device-to-app traffic
B) App-to-Region traffic (e.g., the edge instance reading from RDS/S3 in the parent Region)
C) Carrier IP NAT
D) Security group evaluation

> [!success]- Answer: B
> The **device↔app** hop stays in the carrier network (low latency). The **app↔Region** hop (databases, object storage, control plane) travels over the **AWS backbone** to the parent Region.

---

## Rapid-fire trigger drills

| Stimulus in the question | Answer |
| :--- | :--- |
| "5G / mobile, ultra-low latency to devices" | Wavelength |
| "AR/VR, real-time mobile gaming" | Wavelength (often **G4dn**) |
| "edge ML inference for connected vehicles" | Wavelength + G4dn |
| "traffic must not leave the carrier network" | Wavelength |
| "embedded in a telecom/CSP data center" | Wavelength |
| "make mobile devices reach the instance" | **Carrier Gateway + Carrier IP** |
| "metro end users, no Region nearby" | Local Zones |
| "low latency to on-prem systems / data residency" | Outposts |
| "cache/deliver content globally at the edge" | CloudFront (not Wavelength) |
| "make the single Wavelength Zone HA" | Multiple zones + Region fallback |
| "where does the durable database live" | Parent Region (not the zone) |
| "which instances at the edge" | t3 / r5 / **G4dn** subset |

> Next: [06 - Wavelength Important Facts & Cheat Sheet](06%20-%20Wavelength%20Important%20Facts%20%26%20Cheat%20Sheet.md) — the one-page exam cram.
