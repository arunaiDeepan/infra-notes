# AWS DataSync - Exam Scenarios

> Exam focus: recognise _online, validated, high-speed file/object transfer & sync to S3/EFS/FSx_, agent/locations/tasks, and DataSync vs Snow vs Storage Gateway vs Transfer Family vs DMS/MGN. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - AWS DataSync Intro bits & bytes](01%20-%20AWS%20DataSync%20Intro%20bits%20%26%20bytes.md) · [02 - AWS DataSync Deep Dive](02%20-%20AWS%20DataSync%20Deep%20Dive.md) · [04 - AWS DataSync SRE Operations](04%20-%20AWS%20DataSync%20SRE%20Operations.md) · [00 - Migration & Transfer Overview](00%20-%20Migration%20%26%20Transfer%20Overview.md)

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

- **Online file/object transfer & sync** to S3/EFS/FSx → DataSync.
- **Built-in integrity validation** and **metadata preservation**.
- **Incremental, scheduled** syncs (hybrid steady-state).
- **AWS-to-AWS** transfers are **agentless**.
- DataSync (online) vs **Snow** (offline) vs **Storage Gateway** (ongoing access) vs **Transfer Family** (SFTP).
- Use **filters** and **bandwidth throttle**; **task reports** for audit.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                                | Points to                          |
| :---------------------------------------------------- | :--------------------------------- |
| "copy/sync NFS/SMB/file shares to AWS"                | **DataSync**                       |
| "fast, validated, scheduled, incremental transfer"    | **DataSync**                       |
| "transfer to S3 / EFS / FSx"                          | **DataSync**                       |
| "S3 cross-region / EFS↔FSx (AWS to AWS)"              | **DataSync (agentless)**           |
| "network too slow / petabytes / offline"              | **Snow Family**                    |
| "ongoing low-latency local file access, cloud-backed" | **Storage Gateway (File Gateway)** |
| "partners upload via SFTP/FTPS"                       | **Transfer Family**                |
| "migrate the database" / "migrate whole servers"      | **DMS** / **MGN**                  |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- **Storage Gateway** offered for a **one-time bulk migration** (it's for ongoing hybrid access; DataSync moves bulk).
- **Snow** offered when the network is perfectly fine for online transfer.
- **S3 CLI/rsync** offered when validated, scheduled, metadata-preserving transfer is needed.
- **Transfer Family** offered for internal NAS sync (that's DataSync).
- **DMS/MGN** offered for plain file copy (those are DB/server).
- Forgetting AWS-to-AWS transfers don't need an agent.

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **Files/objects, online, validated/scheduled?** → DataSync.
2. **Too big for the link / offline?** → Snow.
3. **Ongoing mounted local access?** → Storage Gateway.
4. **Partner SFTP/FTPS ingestion?** → Transfer Family.
5. **Database?** → DMS. **Whole servers?** → MGN.
6. **AWS-to-AWS?** → DataSync without an agent.

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** Migrate 80 TB of on-prem NFS to S3 over the network with integrity checks and metadata preserved.
**Options:** A) rsync B) DataSync C) Snowball D) Transfer Family
**Correct:** B
**Explanation:** Online validated file transfer → DataSync.

### Q2

**Scenario:** Nightly sync of a NAS to S3, only changed files.
**Options:** A) Full copy each night B) DataSync scheduled incremental task C) Manual D) Snowball weekly
**Correct:** B
**Explanation:** Scheduled, incremental DataSync task.

### Q3

**Scenario:** Copy S3 data from us-east-1 to eu-west-1 with validation, no agent.
**Options:** A) Snowball B) DataSync (AWS-to-AWS, agentless) C) Storage Gateway D) Transfer Family
**Correct:** B
**Explanation:** AWS-to-AWS DataSync needs no agent.

### Q4

**Scenario:** 4 PB to move; the link would take 5 months.
**Options:** A) DataSync B) Snow Family (offline) C) rsync D) Transfer Family
**Correct:** B
**Explanation:** Offline ship when online is too slow.

### Q5

**Scenario:** Where is the DataSync agent deployed for an on-prem source?
**Options:** A) In AWS only B) As a VM/EC2 near the source C) On every file D) Not needed ever
**Correct:** B
**Explanation:** Agent runs near the source; AWS-to-AWS is agentless.

### Q6

**Scenario:** Protect the production link during a daytime transfer.
**Options:** A) No control B) Set a bandwidth throttle on the task C) Run more agents D) Disable verification
**Correct:** B
**Explanation:** Per-task bandwidth limit.

### Q7

**Scenario:** Land transferred data directly in S3 Standard-IA.
**Options:** A) Not possible B) Choose the target S3 storage class in the task C) Lifecycle only D) Manual move
**Correct:** B
**Explanation:** DataSync can write to specific storage classes.

### Q8

**Scenario:** Provide auditors a per-file manifest of a transfer.
**Options:** A) Guess B) DataSync task report to S3 C) CloudTrail only D) None
**Correct:** B
**Explanation:** Task reports list transferred/skipped/verified/errors.

### Q9

**Scenario:** Move data to FSx for Windows preserving SMB ACLs.
**Options:** A) S3 CLI B) DataSync (preserves SMB metadata) C) Snowball D) Transfer Family
**Correct:** B
**Explanation:** DataSync preserves NFS/SMB metadata to FSx/EFS.

### Q10

**Scenario:** Only `.parquet` files under `/data` should move.
**Options:** A) Move everything B) Include/exclude filters C) Separate buckets D) Manual
**Correct:** B
**Explanation:** Filters select what transfers.

### Q11

**Scenario:** Ensure transferred data wasn't corrupted.
**Options:** A) Hope B) DataSync verification (checksums) C) Re-download D) None
**Correct:** B
**Explanation:** Built-in end-to-end verification.

### Q12

**Scenario:** Keep all traffic off the public internet.
**Options:** A) Internet only B) VPC endpoints (PrivateLink) + DX/VPN C) Email D) Not possible
**Correct:** B
**Explanation:** Private connectivity via endpoints + DX/VPN.

### Q13

**Scenario:** Trigger a Lambda when a transfer task finishes.
**Options:** A) Poll B) EventBridge on task state C) Cron D) SNS only via manual
**Correct:** B
**Explanation:** EventBridge events on task execution state.

### Q14

**Scenario:** Ongoing local file access with cloud backing and caching (not a one-time move).
**Options:** A) DataSync B) Storage Gateway (File Gateway) C) Snowball D) Transfer Family
**Correct:** B
**Explanation:** Continuous hybrid access → File Gateway.

### Q15

**Scenario:** Partners must drop files via SFTP into S3.
**Options:** A) DataSync B) Transfer Family C) Snowball D) Storage Gateway
**Correct:** B
**Explanation:** Managed SFTP → Transfer Family.

### Q16

**Scenario:** Speed up a huge transfer.
**Options:** A) One small agent B) Direct Connect + multiple agents/tasks in parallel C) Disable TLS D) Smaller bucket
**Correct:** B
**Explanation:** Scale bandwidth and parallelism.

### Q17

**Scenario:** Encrypt destination data with a customer-managed key.
**Options:** A) No encryption B) SSE-KMS on the S3 destination C) Only TLS D) Client app
**Correct:** B
**Explanation:** KMS on destination handles at-rest encryption.

### Q18

**Scenario:** Mirror deletions from source to destination.
**Options:** A) Not possible B) Configure overwrite/preserve options to remove deleted files C) Manual delete D) New bucket
**Correct:** B
**Explanation:** Task options control deletion behaviour.

### Q19

**Scenario:** Migrate from another cloud's object store to S3.
**Options:** A) Only AWS sources B) DataSync supports other-cloud object sources C) Snowball only D) Impossible
**Correct:** B
**Explanation:** DataSync can move from other-cloud object stores.

### Q20

**Scenario:** A few small ad-hoc files need copying once.
**Options:** A) Build DataSync B) Simple S3 CLI is fine (DataSync shines at scale/repeatable validated sync) C) Snowball D) Transfer Family
**Correct:** B
**Explanation:** DataSync's value is at scale/repeatability; tiny one-offs don't need it.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** A media company must move 500 TB of footage to S3, keep an on-prem NAS in sync nightly during a 3-month transition, validate integrity, and protect the WAN during business hours.
**Options:** A) rsync cron B) **DataSync** scheduled incremental tasks with **verification**, **bandwidth throttle** (business hours) and **DX** for capacity C) Snowball weekly D) Storage Gateway
**Correct:** B
**Explanation:** DataSync handles bulk + ongoing incremental sync with validation and throttling; DX adds capacity.

### H2

**Scenario:** 6 PB must reach AWS within 3 weeks; the site has a 200 Mbps link.
**Options:** A) DataSync online B) **Snow Family** (offline) - the link can't move 6 PB in time C) Transfer Family D) rsync
**Correct:** B
**Explanation:** Do the math - the link is far too slow; ship offline.

### H3

**Scenario:** After bulk migration, the team still needs on-prem apps to read/write the data with low latency while it lives in S3.
**Options:** A) DataSync forever B) **Storage Gateway (File Gateway)** for ongoing cached access; DataSync did the bulk move C) Snowball D) Transfer Family
**Correct:** B
**Explanation:** DataSync = move; File Gateway = ongoing hybrid access. Use both for their roles.

### H4

**Scenario:** Compliance: transfers must never traverse the public internet, data encrypted with the security team's KMS key, and a per-file audit trail retained.
**Options:** A) Internet + SSE-S3 B) **VPC endpoints + DX/VPN**, **SSE-KMS (CMK)** on destination, **task reports** to a locked S3 bucket C) Public + no report D) Email logs
**Correct:** B
**Explanation:** Private transport + CMK + task reports satisfy all three requirements.

### H5

**Scenario:** Millions of tiny files are transferring far slower than expected.
**Options:** A) Disable verification permanently B) Split into multiple parallel tasks/agents; expect small-file overhead; consider aggregating files where possible C) Use Snowball for a network problem D) Bigger bucket
**Correct:** B
**Explanation:** Small-file overhead is inherent; parallelism and aggregation help.

### H6

**Scenario:** A periodic S3→S3 cross-account, cross-region replica is needed with validation and reporting, no on-prem involved.
**Options:** A) Snowball B) **DataSync AWS-to-AWS (agentless)** task with cross-account IAM, scheduled, verified, task report C) rsync D) Transfer Family
**Correct:** B
**Explanation:** Agentless DataSync handles AWS-to-AWS with validation/reporting.

### H7

**Scenario:** Only a subset of a huge dataset (specific prefixes/extensions, changed in the last run) should move each night to control cost.
**Options:** A) Full transfer nightly B) Include/exclude **filters** + **incremental** transfer mode C) Manual selection D) Move all to IA
**Correct:** B
**Explanation:** Filters + incremental mode minimise moved bytes and cost.

### H8

**Scenario:** A transfer must land in the cheapest immediately-retrievable tier and then age to Glacier.
**Options:** A) Standard forever B) DataSync write to **S3 Standard-IA / Glacier Instant Retrieval**, then **S3 lifecycle** to Glacier/Deep Archive C) Manual D) Snowball
**Correct:** B
**Explanation:** Target storage class + lifecycle optimises ongoing storage cost.

### H9

**Scenario:** Post-transfer, a downstream pipeline must start only when the task completes successfully, and page on failure.
**Options:** A) Fixed timer B) **EventBridge** rule on task success → start pipeline; on error → SNS page C) Poll S3 D) Manual
**Correct:** B
**Explanation:** Event-driven orchestration on task-state events.

### H10

**Scenario:** A hybrid org wants DataSync but worries the agent VM is a security/availability risk.
**Options:** A) No mitigation B) Run the agent on hardened, patched infra (or EC2), restrict its network, monitor it, and deploy multiple agents for resilience/throughput C) Skip DataSync D) Public agent
**Correct:** B
**Explanation:** Harden, restrict, monitor, and scale agents for security and availability.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Online, validated, scheduled file/object transfer & sync to S3/EFS/FSx → DataSync (Agent + Locations + Task; AWS-to-AWS is agentless). Offline/too-big → Snow. Ongoing local access → Storage Gateway. Partner SFTP → Transfer Family. DB → DMS, servers → MGN.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - AWS DataSync SRE Operations](04%20-%20AWS%20DataSync%20SRE%20Operations.md).
