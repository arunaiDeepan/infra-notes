# AWS Application Migration Service (MGN) - Exam Scenarios

> Exam focus: recognise _rehost / lift-and-shift of servers to EC2 with minimal downtime_, the block-level CDC + test + cutover model, MGN vs DMS/DataSync/Snow, and MGN vs DRS. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - AWS Application Migration Service Intro bits & bytes](01%20-%20AWS%20Application%20Migration%20Service%20Intro%20bits%20%26%20bytes.md) · [02 - AWS Application Migration Service Deep Dive](02%20-%20AWS%20Application%20Migration%20Service%20Deep%20Dive.md) · [04 - AWS Application Migration Service SRE Operations](04%20-%20AWS%20Application%20Migration%20Service%20SRE%20Operations.md) · [00 - Migration & Transfer Overview](00%20-%20Migration%20%26%20Transfer%20Overview.md)

---

## Table of Contents

- [1. Frequently Tested Concepts](#1-frequently-tested-concepts)
- [2. Keywords AWS Uses](#2-keywords-aws-uses)
- [3. Common Distractors](#3-common-distractors)
- [4. Elimination Technique](#4-elimination-technique)
- [5. Medium Scenario Questions (1-20)](#5-medium-scenario-questions-1-20)
- [6. Hard Scenario Questions (1-10)](#6-hard-scenario-questions-1-10)
- [7. One-Line Recap](#7-one-line-recap)

---

## 1. Frequently Tested Concepts

- **Rehost / lift-and-shift** many servers to EC2 → MGN.
- **Minimal cutover downtime** via continuous **block-level replication (CDC)**.
- **Non-disruptive test** before cutover; **post-launch SSM actions**.
- MGN = **machines**; **DMS** = databases; **DataSync** = files; **Snow** = offline bulk.
- **MGN vs DRS**: migration (one-time cutover) vs disaster recovery (ongoing failover).
- MGN is the **successor to CloudEndure/SMS**.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                                    | Points to                           |
| :-------------------------------------------------------- | :---------------------------------- |
| "lift and shift / rehost / migrate as-is, no code change" | **MGN**                             |
| "minimal downtime cutover for many servers"               | **MGN** (continuous replication)    |
| "test the migrated server before going live"              | **MGN test instances**              |
| "migrate the database / change DB engine"                 | **DMS** (not MGN)                   |
| "copy file shares / NAS to AWS"                           | **DataSync** (not MGN)              |
| "network too slow / petabytes / disconnected site"        | **Snow Family**                     |
| "ongoing replication for failover/DR"                     | **Elastic Disaster Recovery (DRS)** |
| "track migration progress across the portfolio"           | **Migration Hub**                   |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Picking **MGN** when the workload is specifically a **database migration** → **DMS**.
- Picking **MGN** to move just **files** → **DataSync**.
- Confusing **MGN (migrate)** with **DRS (disaster recovery)**.
- Re-architecting to containers/serverless offered as "rehost" (that's refactor).
- Forgetting **test instances** don't disrupt the source or replication.
- Choosing **Snow** when the network is perfectly adequate for online replication.

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **Whole servers/VMs to EC2, minimal change?** → MGN.
2. **It's a database?** → DMS (+SCT if engine change).
3. **It's files/objects?** → DataSync.
4. **Network too slow / petabytes?** → Snow.
5. **Ongoing failover (not migration)?** → DRS.
6. **Minimal downtime?** → continuous replication (MGN/DMS), not a one-shot copy.

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** Migrate 150 on-prem VMs to EC2 with minimal downtime and no application changes.
**Options:** A) DataSync B) MGN C) DMS D) Snowball
**Correct:** B
**Explanation:** Rehost many servers → MGN.

### Q2

**Scenario:** What keeps MGN cutover downtime low?
**Options:** A) Nightly full copies B) Continuous block-level CDC keeps staging in sync C) Manual disk copy D) DNS only
**Correct:** B
**Explanation:** Pre-synced replica → fast cutover.

### Q3

**Scenario:** Validate a migrated app before go-live without affecting source.
**Options:** A) Cutover directly B) Launch MGN test instances C) Stop replication D) Snapshot only
**Correct:** B
**Explanation:** Test instances are non-disruptive.

### Q4

**Scenario:** Migrate an Oracle DB to Aurora PostgreSQL.
**Options:** A) MGN B) DMS + SCT C) DataSync D) Snowball
**Correct:** B
**Explanation:** Heterogeneous DB migration → DMS + SCT.

### Q5

**Scenario:** Copy 40 TB of file-server data online to S3 and keep it synced.
**Options:** A) MGN B) DataSync C) DMS D) Transfer Family
**Correct:** B
**Explanation:** File/object online sync → DataSync.

### Q6

**Scenario:** Standardise landed EC2 instances (install agents, run scripts) automatically after launch.
**Options:** A) Manual SSH B) MGN post-launch actions via SSM C) Lambda only D) Not possible
**Correct:** B
**Explanation:** Post-launch actions run via Systems Manager.

### Q7

**Scenario:** Which AWS service does MGN replace?
**Options:** A) DMS B) CloudEndure Migration / SMS C) DataSync D) Snow
**Correct:** B
**Explanation:** MGN is the successor to CloudEndure Migration and SMS.

### Q8

**Scenario:** Track progress of a 500-server migration across teams.
**Options:** A) Spreadsheet B) AWS Migration Hub C) CloudTrail D) Config
**Correct:** B
**Explanation:** Migration Hub aggregates portfolio status.

### Q9

**Scenario:** Encrypt the replicated data at rest in staging with a controlled key.
**Options:** A) No encryption B) EBS encryption with a customer-managed KMS key C) Only TLS D) Client-side
**Correct:** B
**Explanation:** Staging EBS encrypted with KMS CMK.

### Q10

**Scenario:** High-volume secure replication for a large fleet over a private link.
**Options:** A) Public internet only B) Direct Connect (or VPN) C) Email D) Snowball
**Correct:** B
**Explanation:** DX/VPN for private, high-throughput replication.

### Q11

**Scenario:** After cutover, reduce ongoing cost from migration.
**Options:** A) Keep staging forever B) Finalize and decommission staging resources C) Keep source running D) Oversize EC2
**Correct:** B
**Explanation:** Finalize to stop staging EBS/EC2 charges.

### Q12

**Scenario:** On-prem servers run VMware vSphere and you prefer not to install agents.
**Options:** A) Impossible B) MGN agentless replication for vSphere C) DataSync D) Snow
**Correct:** B
**Explanation:** Agentless option exists for supported vSphere.

### Q13

**Scenario:** Need ongoing replication to AWS for failover, not a one-time migration.
**Options:** A) MGN B) Elastic Disaster Recovery (DRS) C) DataSync D) Backup
**Correct:** B
**Explanation:** Continuous DR/failover → DRS.

### Q14

**Scenario:** Right-size the target so you don't copy oversized on-prem specs.
**Options:** A) 1:1 copy specs B) Tune the launch template instance type C) Always largest D) Not configurable
**Correct:** B
**Explanation:** Launch settings control instance sizing.

### Q15

**Scenario:** What ports do agents use to replicate?
**Options:** A) 22 only B) TCP 1500 to replication servers, 443 to AWS endpoints C) 3389 D) 80
**Correct:** B
**Explanation:** 1500 for block data, 443 for control/S3.

### Q16

**Scenario:** Is MGN charged during the migration window?
**Options:** A) Always charged B) Free for the standard window; pay for EBS/EC2/transfer C) Per server license D) Per GB only
**Correct:** B
**Explanation:** Service free for ~90 days; you pay for resources used.

### Q17

**Scenario:** Migrate workloads from another cloud provider to EC2.
**Options:** A) Only on-prem supported B) MGN supports other-cloud sources C) Snow only D) Not possible
**Correct:** B
**Explanation:** MGN can rehost from other clouds.

### Q18

**Scenario:** A wave-based migration of many applications with dependencies.
**Options:** A) All at once B) Migrate in waves, test each, cut over per app C) Random order D) Never test
**Correct:** B
**Explanation:** Wave planning with per-app test/cutover.

### Q19

**Scenario:** Audit who initiated a cutover.
**Options:** A) SNS B) CloudTrail C) CloudWatch D) Migration Hub only
**Correct:** B
**Explanation:** CloudTrail records MGN API actions.

### Q20

**Scenario:** Source must keep running during migration.
**Options:** A) Source must be offline B) Continuous replication lets source stay live until cutover C) Stop the app first D) Snapshot then shut down
**Correct:** B
**Explanation:** CDC replicates a live source until the brief cutover.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** An enterprise must move 800 mixed Windows/Linux servers to AWS in 6 months with minimal downtime per app, central tracking, and standardised landed instances.
**Options:** A) Manual AMIs B) **MGN** for block-level replication + **Migration Hub** tracking + **post-launch SSM actions**, migrated in **waves** with per-app test/cutover C) Snowball for all D) DMS
**Correct:** B
**Explanation:** MGN rehosts at scale; Migration Hub tracks; SSM standardises; waves manage risk.

### H2

**Scenario:** The same replication technology is wanted for ongoing DR after migration completes, with low RPO/RTO failover.
**Options:** A) Keep MGN running forever B) Use **Elastic Disaster Recovery (DRS)** for ongoing replication/failover (MGN is for one-time migration) C) Backups only D) Multi-AZ only
**Correct:** B
**Explanation:** MGN ends at cutover; DRS provides continuous DR with the same lineage.

### H3

**Scenario:** A three-tier app: web/app servers plus an Oracle DB. Minimal downtime; the DB should become Aurora PostgreSQL.
**Options:** A) MGN for everything B) **MGN** for web/app servers + **DMS + SCT** for the Oracle→Aurora PostgreSQL conversion C) Snow D) DataSync
**Correct:** B
**Explanation:** Rehost servers with MGN; convert/migrate the heterogeneous DB with DMS+SCT.

### H4

**Scenario:** Replication is saturating the office internet link and impacting users.
**Options:** A) Ignore B) Throttle replication / schedule waves and/or use **Direct Connect** for dedicated bandwidth C) Stop migrating D) Snowball only
**Correct:** B
**Explanation:** Manage bandwidth via throttling/waves or private DX capacity.

### H5

**Scenario:** Security requires no migration traffic over the public internet and customer-managed encryption.
**Options:** A) Public + SSE-S3 B) **VPN/Direct Connect + VPC endpoints** for private transport + **EBS encryption with CMK** C) Internet + no encryption D) Disable encryption
**Correct:** B
**Explanation:** Private connectivity plus CMK-encrypted staging meets the requirement.

### H6

**Scenario:** After cutover, costs didn't drop as expected.
**Options:** A) Larger EC2 B) **Finalize** migrations to remove staging EBS/replication servers; right-size production EC2; apply Savings Plans/RIs C) Keep staging D) Re-migrate
**Correct:** B
**Explanation:** Unfinalized staging keeps billing; finalize + right-size + commit pricing.

### H7

**Scenario:** A handful of legacy servers run an OS MGN doesn't support.
**Options:** A) Force MGN B) Re-platform/rebuild those manually or via supported tooling; use MGN for the supported majority C) Snowball D) Abandon
**Correct:** B
**Explanation:** Check the supported-OS matrix; handle unsupported ones separately.

### H8

**Scenario:** Multi-account landing zone - migrated workloads must land in specific target accounts with guardrails.
**Options:** A) One shared account B) Integrate MGN with **Organizations/Control Tower**; target the correct account/region per workload C) Root account D) Manual only
**Correct:** B
**Explanation:** Align MGN targets with the multi-account landing zone.

### H9

**Scenario:** Cutover failed validation; you must roll back quickly.
**Options:** A) No rollback possible B) Keep the **source live until validated**; if cutover fails, revert traffic to source and re-test (replication continued) C) Delete source first D) Restore from tape
**Correct:** B
**Explanation:** Because the source stays live until you finalize, rollback is routing traffic back and re-testing.

### H10

**Scenario:** A migration program needs repeatable, automated post-migration hardening (CIS, agents, tagging) on every instance.
**Options:** A) Manual per server B) **Post-launch actions (SSM)** running standardised automation documents on each launched instance C) One-off scripts D) None
**Correct:** B
**Explanation:** Post-launch SSM actions enforce consistent hardening/config at scale.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Rehost/lift-and-shift many servers to EC2 with minimal downtime → MGN (block-level CDC, test, cutover, post-launch SSM, tracked in Migration Hub). Databases → DMS (+SCT). Files → DataSync. Offline bulk → Snow. Ongoing failover/DR → DRS, not MGN.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - AWS Application Migration Service SRE Operations](04%20-%20AWS%20Application%20Migration%20Service%20SRE%20Operations.md).
