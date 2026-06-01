# DR & HA Scenario Questions - SAA-C03 Deep Dive

> Realistic SAA-C03 scenario Q&A across the whole domain: AZ failure, choosing a DR strategy by RTO/RPO, cross-Region relational and NoSQL DR, NAT/SPOF analysis, stateless tiers, Route 53 failover, S3 resilience, and cost-optimised DR. Each item gives options, reasoning, and the correct answer.

See also: [00 - DR & HA Overview & Exam Guide](00%20-%20DR%20%26%20HA%20Overview%20%26%20Exam%20Guide.md) · [01 - HA, Fault Tolerance & Core Concepts](01%20-%20HA%2C%20Fault%20Tolerance%20%26%20Core%20Concepts.md) · [02 - High Availability Building Blocks](02%20-%20High%20Availability%20Building%20Blocks.md) · [03 - The Four DR Strategies](03%20-%20The%20Four%20DR%20Strategies.md) · [04 - Cross-Region, Backup & Data Replication](04%20-%20Cross-Region%2C%20Backup%20%26%20Data%20Replication.md) · [06 - DR & HA Troubleshooting (SRE)](06%20-%20DR%20%26%20HA%20Troubleshooting%20%28SRE%29.md) · [07 - DR & HA Important Facts & Cheat Sheet](07%20-%20DR%20%26%20HA%20Important%20Facts%20%26%20Cheat%20Sheet.md)

---

## Table of Contents

- [Q1 Survive an AZ Failure](#q1-survive-an-az-failure)
- [Q2 Cheapest DR for Hours of Tolerance](#q2-cheapest-dr-for-hours-of-tolerance)
- [Q3 Near-Zero RTO Relational DR](#q3-near-zero-rto-relational-dr)
- [Q4 Multi-Region Active-Active NoSQL](#q4-multi-region-active-active-nosql)
- [Q5 The Hidden NAT Gateway SPOF](#q5-the-hidden-nat-gateway-spof)
- [Q6 Users Logged Out on Scale-In](#q6-users-logged-out-on-scale-in)
- [Q7 Route 53 Region Failover](#q7-route-53-region-failover)
- [Q8 Protect S3 Objects From Region Loss](#q8-protect-s3-objects-from-region-loss)
- [Q9 Pilot Light vs Warm Standby](#q9-pilot-light-vs-warm-standby)
- [Q10 Centralised Compliance Backups](#q10-centralised-compliance-backups)
- [Q11 Replace Unhealthy Instances Automatically](#q11-replace-unhealthy-instances-automatically)
- [Q12 RPO of Five Minutes Cost-Optimised](#q12-rpo-of-five-minutes-cost-optimised)

---

## Q1 Survive an AZ Failure

**Scenario:** A production web app runs on EC2 with an RDS MySQL database, all in a single AZ. The business needs the app to **survive the loss of one Availability Zone** with automatic recovery. What should you do?

- A. Take hourly RDS snapshots to S3
- B. Deploy EC2 in an **ASG across ≥2 AZs behind an ALB**, and enable **RDS Multi-AZ**
- C. Move everything to a larger instance type
- D. Enable S3 Cross-Region Replication

**Reasoning:** Snapshots are recovery, not HA (A). A bigger instance is still one AZ (C). CRR addresses Region loss for S3, not this app (D). HA against AZ loss = redundancy across AZs at every tier.

**Correct: B.** ASG across AZs + ALB + RDS Multi-AZ is the canonical multi-AZ HA design.

[⬆ Back to top](#table-of-contents)

---

## Q2 Cheapest DR for Hours of Tolerance

**Scenario:** A company needs a DR plan in a second Region. The business can tolerate **several hours of downtime and data loss** and wants the **lowest possible running cost**. Which strategy?

- A. Multi-Site Active/Active
- B. Warm Standby
- C. Pilot Light
- D. **Backup & Restore**

**Reasoning:** Hours of RTO/RPO + lowest cost is the textbook **Backup & Restore** profile — store backups/AMIs in the DR Region and rebuild on disaster. The others all cost more by running infrastructure continuously.

**Correct: D.** Backup & Restore — cheapest, with hours-scale RTO/RPO.

[⬆ Back to top](#table-of-contents)

---

## Q3 Near-Zero RTO Relational DR

**Scenario:** A global SaaS uses a relational database and needs **cross-Region DR with RPO around 1 second**, **failover under a minute**, and **low-latency reads** for users in other Regions. What's best?

- A. RDS Multi-AZ
- B. **Aurora Global Database**
- C. RDS cross-Region read replica
- D. Restore from cross-Region snapshots

**Reasoning:** Multi-AZ is in-Region HA only (A). A standard cross-Region read replica has higher lag and slower promotion (C). Snapshots are hours-scale (D). Aurora Global DB gives ~1s replication, sub-minute managed failover, and local reads.

**Correct: B.** Aurora Global Database.

[⬆ Back to top](#table-of-contents)

---

## Q4 Multi-Region Active-Active NoSQL

**Scenario:** A mobile backend must let users **read and write in whichever Region is closest**, with **near-zero RTO/RPO** if a Region fails. The data is key-value. Which service/feature?

- A. DynamoDB **Global Tables**
- B. Aurora Global Database
- C. RDS Multi-AZ
- D. ElastiCache Global Datastore

**Reasoning:** Aurora Global DB is single-writer (one primary Region), so it can't accept writes everywhere (B). Multi-AZ is in-Region (C). Global Datastore is a cache, not the system of record (D). DynamoDB Global Tables is multi-active: every Region is read/write.

**Correct: A.** DynamoDB Global Tables.

[⬆ Back to top](#table-of-contents)

---

## Q5 The Hidden NAT Gateway SPOF

**Scenario:** Private-subnet instances run across AZ-a and AZ-b. All of them route outbound traffic through a **single NAT Gateway in AZ-a**. AZ-a fails and instances in AZ-b lose internet access too. How do you prevent this?

- A. Use a larger NAT Gateway
- B. **Deploy one NAT Gateway per AZ and route each private subnet to its local NAT GW**
- C. Replace NAT GW with an Internet Gateway
- D. Add a second NAT GW in AZ-a

**Reasoning:** Size doesn't address the AZ SPOF (A). An IGW would make private subnets public (C). Two NAT GWs in the same AZ still die together (D). HA requires a NAT GW in **each** AZ with per-AZ route tables.

**Correct: B.** One NAT GW per AZ.

[⬆ Back to top](#table-of-contents)

---

## Q6 Users Logged Out on Scale-In

**Scenario:** A web tier in an ASG behind an ALB stores **session state in instance memory**. When the ASG scales in or replaces an instance, affected users are logged out. What's the best fix?

- A. Enable ALB sticky sessions only
- B. **Externalise sessions to ElastiCache (or DynamoDB) so the tier is stateless**
- C. Disable scale-in
- D. Increase instance size

**Reasoning:** Stickiness re-pins users to one instance, so losing that instance still drops them (A). Disabling scale-in defeats elasticity (C). Size is irrelevant (D). A stateless tier with shared session store survives instance churn.

**Correct: B.** Externalise session state (ElastiCache/DynamoDB).

[⬆ Back to top](#table-of-contents)

---

## Q7 Route 53 Region Failover

**Scenario:** An application runs active in `us-east-1` with a standby stack in `eu-west-1`. The company wants DNS to **automatically send users to the standby Region only if the primary is down**. What configuration?

- A. Weighted routing 50/50
- B. **Failover routing with health checks (primary/secondary)**
- C. Simple routing to the primary
- D. Geolocation routing

**Reasoning:** Weighted always sends some traffic to standby (A). Simple has no health awareness (C). Geolocation routes by user location, not health (D). Failover routing with health checks is exactly active-passive Region cutover.

**Correct: B.** Route 53 Failover routing + health checks.

[⬆ Back to top](#table-of-contents)

---

## Q8 Protect S3 Objects From Region Loss

**Scenario:** Critical objects in an S3 bucket in `ap-south-1` must remain available even if the **entire Region** is impaired, and must meet a data-residency copy in `ap-southeast-1`. What do you configure?

- A. Move objects to S3 One Zone-IA
- B. Enable versioning and **S3 Cross-Region Replication to ap-southeast-1**
- C. Rely on S3's 11-nines durability
- D. Take manual copies with the CLI weekly

**Reasoning:** One Zone-IA reduces resilience (single AZ) (A). 11-nines durability protects against object loss within a Region, not a Region outage (C). Manual weekly copies = poor RPO and ops overhead (D). CRR (with versioning) continuously replicates to the second Region.

**Correct: B.** Versioning + Cross-Region Replication. (Use **Batch Replication** for pre-existing objects.)

[⬆ Back to top](#table-of-contents)

---

## Q9 Pilot Light vs Warm Standby

**Scenario:** A company wants DR in a second Region. They want to **keep running costs low** but recover **faster than a full rebuild**. They're fine starting and scaling the application servers during failover, as long as the **database is always current** in the DR Region. Which strategy?

- A. Backup & Restore
- B. **Pilot Light**
- C. Warm Standby
- D. Multi-Site Active/Active

**Reasoning:** Backup & Restore wouldn't keep the DB current/replicated (A). Warm Standby keeps app servers running (more cost) (C). Active-Active is full cost (D). Pilot Light keeps the **data layer always replicated** while compute stays off until needed — low cost, faster than rebuild.

**Correct: B.** Pilot Light. (If they wanted app servers already running and just scaled up → Warm Standby.)

[⬆ Back to top](#table-of-contents)

---

## Q10 Centralised Compliance Backups

**Scenario:** An enterprise must enforce **automated backups with retention policies across EBS, RDS, DynamoDB, and EFS in many accounts**, prove compliance, and make backups **immutable**. What's the best approach?

- A. Custom Lambda + cron snapshots per service
- B. **AWS Backup with backup plans, cross-account policies via Organizations, and Vault Lock (WORM)**
- C. Manual snapshots
- D. Storage Gateway

**Reasoning:** DIY Lambda is high overhead and hard to prove compliance (A). Manual doesn't scale or audit (C). Storage Gateway is hybrid storage, not backup orchestration (D). AWS Backup centralises plans, multi-account coverage, and immutable Vault Lock.

**Correct: B.** AWS Backup (+ Vault Lock for immutability).

[⬆ Back to top](#table-of-contents)

---

## Q11 Replace Unhealthy Instances Automatically

**Scenario:** Instances sometimes keep running while the application process has crashed, so they pass EC2 status checks but serve errors. The team wants unhealthy instances **detected and replaced automatically**. What do you configure?

- A. Rely on EC2 system status checks only
- B. **Set the ASG to use ELB health checks (application-level), so failing targets are replaced**
- C. A CloudWatch alarm that emails the team
- D. Schedule daily instance restarts

**Reasoning:** EC2 status checks miss app-level failures (A). An email isn't automatic remediation (C). Daily restarts are crude and slow (D). ELB health checks probe the app; the ASG terminates and replaces instances that fail them.

**Correct: B.** ASG health-check type = **ELB**.

[⬆ Back to top](#table-of-contents)

---

## Q12 RPO of Five Minutes Cost-Optimised

**Scenario:** A relational workload needs **RPO ≤ 5 minutes** and **RTO ≤ 30 minutes** for cross-Region DR, at the **lowest cost** that meets those numbers. Which is the best fit?

- A. Multi-Site Active/Active
- B. Warm Standby with a small always-on stack
- C. **Pilot Light: cross-Region read replica (data current) + AMIs ready, scale compute on failover**
- D. Backup & Restore from 6-hourly snapshots

**Reasoning:** Active-Active and Warm Standby meet the numbers but cost more than required (A, B). Backup & Restore from 6-hourly snapshots violates the 5-minute RPO and likely the 30-minute RTO (D). Pilot Light keeps data continuously replicated (RPO minutes) and launches compute within the RTO — cheapest option that still satisfies both numbers.

**Correct: C.** Pilot Light. Always choose the **cheapest strategy that meets the stated RTO/RPO**.

[⬆ Back to top](#table-of-contents)
