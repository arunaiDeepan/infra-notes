# AWS Snow Family - Exam Scenarios

> Exam focus: pick _offline transfer_ when the network is too slow / connectivity is poor, choose the right device (Snowcone / Snowball Edge Storage vs Compute), edge compute, security (KMS/NIST), and Snow vs DataSync vs Direct Connect. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - AWS Snow Family Intro bits & bytes](01%20-%20AWS%20Snow%20Family%20Intro%20bits%20%26%20bytes.md) · [02 - AWS Snow Family Deep Dive](02%20-%20AWS%20Snow%20Family%20Deep%20Dive.md) · [04 - AWS Snow Family SRE Operations](04%20-%20AWS%20Snow%20Family%20SRE%20Operations.md) · [00 - Migration & Transfer Overview](00%20-%20Migration%20%26%20Transfer%20Overview.md)

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

- **Offline bulk transfer** when online would take **weeks/months**.
- **Device selection**: Snowcone (small/portable/edge), Snowball Edge **Storage** (bulk), Snowball Edge **Compute** (edge EC2/Lambda/GPU).
- **Edge compute** in disconnected/harsh environments.
- **Security**: KMS encryption, keys not on device, tamper-evident, **NIST erase**.
- **Snow vs DataSync vs Direct Connect** (the bandwidth-vs-time decision).
- Snow can **seed** a DMS load; Snowcone can run a **DataSync agent**.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                             | Points to                           |
| :------------------------------------------------- | :---------------------------------- |
| "petabytes / would take months over the network"   | **Snow Family (offline)**           |
| "limited/no/intermittent connectivity at the site" | **Snow Family**                     |
| "process data locally at the edge / on-site ML"    | **Snowball Edge Compute Optimized** |
| "small, portable, rugged device"                   | **Snowcone**                        |
| "tens of TB bulk to S3, one-time"                  | **Snowball Edge Storage Optimized** |
| "exabytes" (older questions)                       | **Snowmobile** (legacy)             |
| "fast dedicated link, sustained transfer"          | **Direct Connect** (not Snow)       |
| "online scheduled sync, adequate bandwidth"        | **DataSync** (not Snow)             |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Choosing **Snow** when the network is **adequate** (use DataSync/DX).
- Choosing **DataSync/DX** when the volume is **too large for the time window** (use Snow).
- Picking **Storage Optimized** when **edge compute/GPU** is required (use Compute Optimized).
- Picking a big Snowball when a **portable Snowcone** fits the constraints.
- Forgetting Snow's **encryption/NIST erase** when security is questioned.
- Using Snow for **ongoing continuous** sync (it's one-time-ish).

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **Compute time = data ÷ bandwidth.** Weeks/months online? → **Snow**.
2. **Poor/no connectivity?** → **Snow** (and maybe edge compute).
3. **Need local processing/ML?** → **Snowball Edge Compute** (GPU if ML).
4. **Small/portable?** → **Snowcone**.
5. **Bulk one-time to S3, decent size?** → **Snowball Edge Storage**.
6. **Adequate link / ongoing?** → **DataSync** / **Direct Connect** (not Snow).

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** 500 TB to S3; 100 Mbps link; needed within a month.
**Options:** A) DataSync online B) Snowball Edge Storage Optimized C) Direct Connect D) S3 CLI
**Correct:** B
**Explanation:** Online would take far longer than a month; ship offline.

### Q2

**Scenario:** Remote mining site, no reliable internet, needs on-site data filtering with compute.
**Options:** A) Snowball Edge Compute Optimized B) DataSync C) DMS D) Snowcone storage only
**Correct:** A
**Explanation:** Edge compute in a disconnected environment.

### Q3

**Scenario:** Small, rugged, portable device for a field team to collect a few TB.
**Options:** A) Snowmobile B) Snowcone C) Snowball Edge Storage D) Direct Connect
**Correct:** B
**Explanation:** Snowcone is the small/portable option.

### Q4

**Scenario:** How is Snow data protected at rest?
**Options:** A) No encryption B) KMS 256-bit, keys not on device, NIST erase C) Only a password D) Client zip
**Correct:** B
**Explanation:** KMS encryption + tamper-evidence + NIST sanitisation.

### Q5

**Scenario:** 40 TB and a 10 Gbps Direct Connect already in place.
**Options:** A) Snowball B) Online via DataSync/DX (faster than shipping) C) Snowcone D) Snowmobile
**Correct:** B
**Explanation:** With fast DX, online beats shipping for 40 TB.

### Q6

**Scenario:** On-site ML inference needing a GPU at a disconnected location.
**Options:** A) Snowcone B) Snowball Edge Compute Optimized (GPU) C) Storage Optimized D) DataSync
**Correct:** B
**Explanation:** GPU edge compute → Compute Optimized.

### Q7

**Scenario:** Manage and monitor a Snow device with a GUI, no scripting.
**Options:** A) Snowball Client only B) AWS OpsHub C) CloudTrail D) Console only
**Correct:** B
**Explanation:** OpsHub is the GUI management app.

### Q8

**Scenario:** Distribute a large dataset from S3 to a disconnected branch.
**Options:** A) Import job B) Export-from-S3 job on a Snow device C) DataSync D) Transfer Family
**Correct:** B
**Explanation:** Export jobs move S3 data out to the device.

### Q9

**Scenario:** Avoid large internet egress charges moving petabytes.
**Options:** A) Online transfer B) Snow (offline, no internet egress for the data) C) Transfer Family D) rsync
**Correct:** B
**Explanation:** Offline shipping avoids egress at scale.

### Q10

**Scenario:** Copy data to the device as if it were S3.
**Options:** A) Only NFS B) Local S3-compatible endpoint (or NFS) C) FTP D) SMB only
**Correct:** B
**Explanation:** Devices expose an S3 API (and NFS on supported models).

### Q11

**Scenario:** Ensure imported data wasn't corrupted.
**Options:** A) Hope B) Checksums validated by client + AWS on import C) None D) Manual
**Correct:** B
**Explanation:** End-to-end checksum validation.

### Q12

**Scenario:** Need more edge capacity and local durability than one device.
**Options:** A) One bigger device only B) A Snowball Edge cluster C) Snowcone D) Snowmobile
**Correct:** B
**Explanation:** Clusters add capacity + durability.

### Q13

**Scenario:** Snowcone with intermittent connectivity wants to send data online when possible.
**Options:** A) Impossible B) Run a DataSync agent on Snowcone C) FTP D) Email
**Correct:** B
**Explanation:** Snowcone supports a DataSync agent for online transfer.

### Q14

**Scenario:** Reduce Snow cost.
**Options:** A) Keep device for months B) Return promptly to avoid per-day fees; right-size device C) Order extra always D) Bigger bucket
**Correct:** B
**Explanation:** On-site days beyond included incur fees.

### Q15

**Scenario:** Exabyte-scale migration referenced in an older exam item.
**Options:** A) Snowcone B) Snowmobile (legacy) C) Snowball D) DataSync
**Correct:** B
**Explanation:** Snowmobile was the exabyte/truck option (now discontinued).

### Q16

**Scenario:** Seed a huge initial DB load offline, then keep syncing changes online.
**Options:** A) DMS only B) Snow to seed initial data + DMS CDC for ongoing changes C) DataSync only D) MGN
**Correct:** B
**Explanation:** Offline-seed + CDC hybrid.

### Q17

**Scenario:** Track when the device ships, arrives, and finishes importing.
**Options:** A) Guess B) SNS notifications + console job tracking C) CloudFront logs D) Config
**Correct:** B
**Explanation:** SNS + console track job lifecycle.

### Q18

**Scenario:** A ship at sea collects sensor data for weeks with no connectivity.
**Options:** A) DataSync B) Snowball Edge (collect + optional edge compute), import on return C) Direct Connect D) Transfer Family
**Correct:** B
**Explanation:** Disconnected collection + later import.

### Q19

**Scenario:** Physical chain-of-custody and data residency must be provable.
**Options:** A) Online only B) Snow's tamper-evident hardware + KMS + controlled physical handling C) Public bucket D) None
**Correct:** B
**Explanation:** Physical control + tamper-evidence supports residency/custody.

### Q20

**Scenario:** Ongoing nightly sync of a NAS with a good link.
**Options:** A) Snowball nightly B) DataSync scheduled (Snow is not for continuous sync) C) Snowcone D) Snowmobile
**Correct:** B
**Explanation:** Continuous online sync → DataSync, not Snow.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** A genomics lab must move 2 PB to S3 within 6 weeks; their best link is 1 Gbps shared with research.
**Options:** A) DataSync online B) **Multiple Snowball Edge Storage Optimized** devices (or a cluster) in parallel, offline C) Direct Connect upgrade only D) rsync
**Correct:** B
**Explanation:** 2 PB over a shared 1 Gbps is months; parallel Snow devices meet the window.

### H2

**Scenario:** A defense customer needs to process classified sensor data **on-site** (no cloud connectivity), run ML inference, and only later import results.
**Options:** A) Cloud EC2 B) **Snowball Edge Compute Optimized (GPU)** for edge ML + import results when back C) DataSync D) DMS
**Correct:** B
**Explanation:** Disconnected edge ML → Compute Optimized; import later.

### H3

**Scenario:** Cost review: a 300 TB online migration over months would incur heavy egress and saturate the WAN.
**Options:** A) Push online anyway B) **Snow** offline - no internet egress for the data, no WAN contention, faster end-to-end C) Transfer Family D) Storage Gateway
**Correct:** B
**Explanation:** At this scale Snow is cheaper (egress) and faster than the constrained link.

### H4

**Scenario:** A retailer has 1,200 stores, each with ~5 TB and poor links, to consolidate to S3.
**Options:** A) One big device B) **Snowcone/Snowball per region/store wave**, possibly with on-device **DataSync** when links allow; consolidate to S3 C) DataSync only D) Snowmobile
**Correct:** B
**Explanation:** Many small sites → portable devices in waves; DataSync where connectivity permits.

### H5

**Scenario:** Security demands the unlock secret never travel with the device and provable sanitisation.
**Options:** A) Tape the code to the box B) Keep **manifest and unlock code separate**, rely on **KMS** + **NIST 800-88 erase** after import C) No encryption D) Public download
**Correct:** B
**Explanation:** Separation of unlock material + KMS + NIST erase meet the controls.

### H6

**Scenario:** A factory needs continuous edge processing for years, not a one-time transfer.
**Options:** A) Repeated Snow orders forever B) Reconsider architecture - Snow is for offline transfer/edge bursts; for permanent edge use **Outposts/Local Zones** or owned edge hardware; Snow Edge fits temporary/disconnected, DataSync/DX for ongoing online C) Snowmobile D) Transfer Family
**Correct:** B
**Explanation:** Permanent edge is an Outposts/Local Zones question; Snow suits temporary/disconnected workloads.

### H7

**Scenario:** A DB migration of a 50 TB warehouse over a thin link must minimise downtime.
**Options:** A) Online full load B) **Snow to seed** the initial 50 TB into the target, then **DMS CDC** to apply ongoing changes online; cut over at CDC≈0 C) Snowmobile D) DataSync only
**Correct:** B
**Explanation:** Offline-seed + CDC catch-up minimises both transfer time and downtime.

### H8

**Scenario:** Many tiny files make device loading slow.
**Options:** A) Accept it B) **Aggregate (tar)** small files and parallelise copies to saturate the NIC C) Smaller device D) Online instead
**Correct:** B
**Explanation:** Small-file overhead - aggregate and parallelise.

### H9

**Scenario:** A 100 TB migration where the customer also wants to verify every object landed correctly in S3.
**Options:** A) Trust the import B) Use Snow's **checksum validation** + reconcile S3 inventory/object counts against the source manifest C) No verification D) Re-ship
**Correct:** B
**Explanation:** Validate via checksums and reconcile against an inventory/manifest.

### H10

**Scenario:** Choosing between Snowball Edge Storage vs Compute for a 60 TB move that also needs light on-device transformation.
**Options:** A) Storage only B) If transformation needs meaningful compute → **Compute Optimized**; if it's mostly bulk transfer with minimal processing → **Storage Optimized** C) Snowcone D) Snowmobile
**Correct:** B
**Explanation:** Match the device to the compute requirement, not just capacity.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Network too slow / petabytes / poor connectivity → Snow Family (offline). Portable/small → Snowcone; bulk → Snowball Edge Storage; edge compute/ML/GPU → Snowball Edge Compute. KMS-encrypted, tamper-evident, NIST-erased. Adequate link/ongoing → DataSync or Direct Connect, not Snow. Snow can seed a DMS load.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - AWS Snow Family SRE Operations](04%20-%20AWS%20Snow%20Family%20SRE%20Operations.md).
