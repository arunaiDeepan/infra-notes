# AWS Backup - Exam Scenarios

> Exam focus: centralized/tag-based backups, Vault Lock immutability, cross-account/Region copy for DR & ransomware defense, and backup vs replication. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - AWS Backup Intro bits & bytes](01%20-%20AWS%20Backup%20Intro%20bits%20%26%20bytes.md) · [02 - AWS Backup Deep Dive](02%20-%20AWS%20Backup%20Deep%20Dive.md) · [04 - AWS Backup SRE Operations](04%20-%20AWS%20Backup%20SRE%20Operations.md) · [24 - AWS Config & Audit Manager](24%20-%20AWS%20Config%20%26%20Audit%20Manager.md)

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

- **Centralized, policy-driven** backups across services/accounts.
- **Tag-based** dynamic selection.
- **Vault Lock (Compliance)** = immutability/WORM.
- **Cross-Region** (DR) and **cross-account** (isolation/ransomware) copy.
- **Organizations backup policies** for org-wide enforcement.
- Backup (recovery points) ≠ **replication** (HA/low-RPO).

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                                    | Points to                                         |
| :-------------------------------------------------------- | :------------------------------------------------ |
| "centralized backup across services/accounts"             | **AWS Backup**                                    |
| "back up everything with a tag automatically"             | **Tag-based selection**                           |
| "immutable / WORM / cannot be deleted before retention"   | **Vault Lock (Compliance)**                       |
| "protect backups from a compromised account / ransomware" | **Cross-account copy to isolated backup account** |
| "DR copy in another Region"                               | **Cross-Region copy**                             |
| "enforce backup policy across all accounts"               | **Organizations backup policies**                 |
| "prove resources are backed up per policy"                | **Backup Audit Manager**                          |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Using **replication** (Multi-AZ/global tables/S3 CRR) when a **point-in-time recovery/backup** is required (and vice versa).
- Expecting Vault Lock **Governance** to stop admins (only **Compliance** is truly immutable).
- Forgetting **cross-account** copy for ransomware defense.
- Manual per-service snapshots when **centralized** AWS Backup is the intended answer.
- Thinking backups in the same account/Region survive account compromise or Region loss.

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **"Centralized/consistent backups"** → AWS Backup.
2. **"Immutable/WORM"** → Vault Lock Compliance.
3. **"Ransomware/compromised account"** → cross-account copy to isolated account.
4. **"Region DR"** → cross-Region copy.
5. **"Real-time/low-RPO/HA"** → replication, NOT backup.

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** Centrally back up EBS, RDS, DynamoDB, and EFS with one consistent policy.
**Options:** A) Per-service scripts B) AWS Backup plan C) S3 only D) Snapshots manually
**Correct:** B
**Explanation:** AWS Backup centralizes multi-service backup.

### Q2

**Scenario:** Automatically back up any resource tagged `Backup=daily`, including new ones.
**Options:** A) ARN list B) Tag-based resource selection C) Manual D) Config
**Correct:** B
**Explanation:** Tag selection is dynamic.

### Q3

**Scenario:** Backups must be immutable for 7 years — not even root can delete.
**Options:** A) Governance lock B) Vault Lock Compliance mode C) KMS only D) Versioning
**Correct:** B
**Explanation:** Compliance mode is truly immutable.

### Q4

**Scenario:** Protect backups if the production account is compromised.
**Options:** A) Same-account vault B) Cross-account copy to isolated backup account C) More retention D) Governance lock
**Correct:** B
**Explanation:** Isolation in a separate account.

### Q5

**Scenario:** DR requirement: recover in another Region after a Region outage.
**Options:** A) Same-Region only B) Cross-Region copy C) Multi-AZ only D) Versioning
**Correct:** B
**Explanation:** Cross-Region copy enables Region DR.

### Q6

**Scenario:** Enforce backup policy across all org accounts.
**Options:** A) Per account B) Organizations backup policies C) SCP only D) Config only
**Correct:** B
**Explanation:** Org backup policies centralize enforcement.

### Q7

**Scenario:** Prove resources are backed up per policy for an audit.
**Options:** A) Screenshots B) Backup Audit Manager C) CloudTrail only D) Budgets
**Correct:** B
**Explanation:** Audit Manager reports compliance.

### Q8

**Scenario:** Validate backups are actually restorable.
**Options:** A) Assume B) Restore testing C) Vault Lock D) KMS
**Correct:** B
**Explanation:** Automated restore testing.

### Q9

**Scenario:** Reduce backup storage cost for old recovery points.
**Options:** A) Delete plan B) Lifecycle to cold storage + retention C) More copies D) Governance lock
**Correct:** B
**Explanation:** Lifecycle/retention manage cost.

### Q10

**Scenario:** Real-time HA for a database (near-zero RPO).
**Options:** A) AWS Backup B) RDS Multi-AZ / read replicas (replication) C) Vault Lock D) Cross-Region copy
**Correct:** B
**Explanation:** HA/low-RPO is replication, not backup.

### Q11

**Scenario:** Encrypt recovery points.
**Options:** A) Not possible B) KMS-encrypted vault C) Plaintext D) S3 only
**Correct:** B
**Explanation:** Vaults are KMS-encrypted.

### Q12

**Scenario:** Detect resources that have NO backup configured.
**Options:** A) Manual B) Config rule / Backup Audit Manager C) Budgets D) CloudTrail
**Correct:** B
**Explanation:** Config/Audit Manager find unprotected resources.

### Q13

**Scenario:** Prevent accidental (but reversible) backup deletion.
**Options:** A) Compliance lock B) Vault Lock Governance mode C) No lock D) KMS
**Correct:** B
**Explanation:** Governance mode guards against accidents (reversible by privileged users).

### Q14

**Scenario:** Notify on a failed backup job.
**Options:** A) Manual B) EventBridge/SNS on job state C) Config D) Budgets
**Correct:** B
**Explanation:** Job events to SNS/EventBridge.

### Q15

**Scenario:** Point-in-time restore for RDS via AWS Backup.
**Options:** A) Not supported B) Continuous backup / PITR for supported services C) Only daily D) S3 only
**Correct:** B
**Explanation:** PITR supported for some services.

### Q16

**Scenario:** Standardize the backup tag across the org.
**Options:** A) Manual B) Tag policies (+ enforcement) C) SCP only D) Budgets
**Correct:** B
**Explanation:** Tag policies standardize selection tags.

### Q17

**Scenario:** Prevent disabling/deleting backups org-wide.
**Options:** A) Trust B) SCP denying backup deletion + Vault Lock C) IAM only D) Budgets
**Correct:** B
**Explanation:** SCP + Vault Lock harden against deletion.

### Q18

**Scenario:** Audit who restored a backup.
**Options:** A) Config B) CloudTrail C) Budgets D) Backup only
**Correct:** B
**Explanation:** CloudTrail logs restore API calls.

### Q19

**Scenario:** Cost driver to watch with cross-Region copies.
**Options:** A) None B) Storage + cross-Region data transfer C) IAM D) CloudWatch
**Correct:** B
**Explanation:** Copies cost storage + transfer.

### Q20

**Scenario:** Single pane for backup status across accounts.
**Options:** A) Per-account consoles B) Delegated admin + cross-account monitoring C) CUR D) Budgets
**Correct:** B
**Explanation:** Delegated administration centralizes visibility.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** A bank must ensure backups are immutable for 7 years, recoverable in a second Region, and safe even if an admin or attacker tries to delete them.
**Options:** A) Same-account snapshots B) AWS Backup with **Vault Lock (Compliance)** + **cross-Region** copy + **cross-account** copy to an isolated, locked backup-account vault C) S3 versioning D) RDS Multi-AZ
**Correct:** B
**Explanation:** Compliance Vault Lock = immutability; cross-Region = DR; cross-account isolation defends against admin/attacker deletion.

### H2

**Scenario:** Ransomware encrypts production and the attacker has admin in the prod account; the company must still recover.
**Options:** A) Same-account backups B) Backups **copied to an isolated backup account** with **Compliance Vault Lock** — attacker can't delete/alter them C) More retention D) Governance lock only
**Correct:** B
**Explanation:** Cross-account isolation + immutability survive a compromised prod account.

### H3

**Scenario:** An auditor asks for proof that every production database is backed up daily with 35-day retention and encryption.
**Options:** A) Screenshots B) **Backup Audit Manager** controls/report verifying frequency/retention/encryption; Config for unprotected resources C) Manual list D) Budgets
**Correct:** B
**Explanation:** Audit Manager produces the compliance evidence; Config catches gaps.

### H4

**Scenario:** A team "has backups" but a real incident revealed they were never restorable.
**Options:** A) Hope B) Enable **restore testing** (scheduled automated restores) to validate recoverability and measure restore time C) More copies D) Vault Lock
**Correct:** B
**Explanation:** Restore testing closes the untested-backup gap.

### H5

**Scenario:** A 50-account org needs guaranteed, consistent backup coverage including for accounts created next quarter.
**Options:** A) Per-account setup B) **Organizations backup policies** (inherited by new accounts) + tag policies + SCP preventing deletion C) Email policy D) Manual
**Correct:** B
**Explanation:** Org backup policies enforce coverage org-wide and for future accounts.

### H6

**Scenario:** Leadership confuses AWS Backup with HA and expects zero data loss on instance failure.
**Options:** A) Rely on backups B) Clarify: **backups = recovery points (RPO≠0)**; for HA/low-RPO use **replication** (Multi-AZ, read replicas, global tables, S3 CRR) alongside backups C) More frequent backups only D) Vault Lock
**Correct:** B
**Explanation:** Backup and replication solve different problems; use both per RPO/RTO.

### H7

**Scenario:** Backup storage costs are ballooning from long warm retention and many cross-Region copies.
**Options:** A) Stop backups B) **Lifecycle to cold storage**, right-size retention, copy cross-Region only what DR requires C) Delete all old D) Governance lock
**Correct:** B
**Explanation:** Cold-tier lifecycle + retention tuning + selective copies control cost (mind Vault Lock minimums).

### H8

**Scenario:** A regulated workload requires that retention can never be shortened, even by mistake or insider.
**Options:** A) Governance lock B) **Vault Lock Compliance mode** (irreversible min retention) C) IAM deny D) KMS
**Correct:** B
**Explanation:** Only Compliance mode makes retention truly unalterable.

### H9

**Scenario:** Security wants automatic remediation when a production resource lacks a backup plan.
**Options:** A) Manual sweeps B) **Config** rule detects unprotected resources → notify/remediate (assign backup tag / plan); Audit Manager reports C) Budgets D) CloudTrail
**Correct:** B
**Explanation:** Config detection + remediation enforces backup coverage continuously.

### H10

**Scenario:** A cross-account copy fails with access errors.
**Options:** A) AWS bug B) The **destination vault's access policy** must allow the source account/role; fix the vault policy + KMS key grants C) Add retention D) New Region
**Correct:** B
**Explanation:** Cross-account copy requires destination vault policy + KMS permissions for the source.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Centralized, tag-driven, multi-service/account backups → AWS Backup. Immutable/WORM → Vault Lock Compliance. Ransomware/compromise defense → cross-account copy to isolated account. Region DR → cross-Region copy. Org-wide → Organizations backup policies. Backups ≠ replication (RPO≠0).**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - AWS Backup SRE Operations](04%20-%20AWS%20Backup%20SRE%20Operations.md).
