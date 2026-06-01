# AWS Transfer Family - Exam Scenarios

> Exam focus: recognise _managed SFTP/FTPS/FTP/AS2 into S3/EFS_, identity provider choices, endpoint types (public vs VPC/EIP allow-listing), logical directories, managed workflows, AS2/EDI, and Transfer Family vs DataSync/Snow/Storage Gateway. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - AWS Transfer Family Intro bits & bytes](01%20-%20AWS%20Transfer%20Family%20Intro%20bits%20%26%20bytes.md) · [02 - AWS Transfer Family Deep Dive](02%20-%20AWS%20Transfer%20Family%20Deep%20Dive.md) · [04 - AWS Transfer Family SRE Operations](04%20-%20AWS%20Transfer%20Family%20SRE%20Operations.md) · [00 - Migration & Transfer Overview](00%20-%20Migration%20%26%20Transfer%20Overview.md)

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

- **Managed SFTP/FTPS/FTP/AS2** landing files in **S3/EFS**, no servers to run.
- **Identity providers**: service-managed, **AD/Directory Service**, **custom Lambda IdP** (Cognito/Secrets/LDAP).
- **Endpoint types**: public vs **VPC** (security groups + **Elastic IPs** for partner allow-listing); **FTP = VPC-internal only**.
- **Logical directories** to isolate/mask partner paths.
- **Managed Workflows** for post-upload automation (scan/decrypt/route).
- **AS2** for B2B/EDI; **per-user IAM** least privilege.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                                | Points to                                 |
| :---------------------------------------------------- | :---------------------------------------- |
| "partners/customers upload via SFTP/FTPS"             | **Transfer Family**                       |
| "retire/replace self-managed FTP servers"             | **Transfer Family**                       |
| "files must land in S3/EFS"                           | **Transfer Family** backends              |
| "authenticate against Active Directory / custom auth" | **Directory Service / custom Lambda IdP** |
| "partners must allow-list our static IPs"             | **VPC endpoint with Elastic IPs**         |
| "B2B / EDI / trading partners / MDN receipts"         | **AS2**                                   |
| "scan/transform files automatically after upload"     | **Managed Workflows**                     |
| "internal bulk file migration/sync"                   | **DataSync** (not Transfer Family)        |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- **DataSync** offered for **partner SFTP exchange** (that's Transfer Family).
- **Transfer Family** offered for **internal bulk migration** (that's DataSync/Snow).
- Using **public FTP** (unencrypted, not allowed publicly) instead of SFTP/FTPS.
- Forgetting **VPC endpoint + EIP** when partners need **static IPs to allow-list**.
- Over-broad IAM instead of **per-user least-privilege + logical directories**.
- Building custom FTP on EC2 when a **managed** service is wanted.

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **External partners using SFTP/FTPS/FTP/AS2?** → Transfer Family.
2. **Internal bulk move/sync?** → DataSync. **Offline/PB?** → Snow.
3. **Need static IPs to allow-list?** → VPC endpoint + **Elastic IPs**.
4. **AD/custom auth?** → Directory Service / custom Lambda IdP.
5. **B2B/EDI?** → AS2.
6. **Post-upload processing?** → Managed Workflows.

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** Vendors must upload nightly files via SFTP, landing in S3, with no FTP servers to manage.
**Options:** A) EC2 SFTP B) Transfer Family (SFTP → S3) C) DataSync D) Snowball
**Correct:** B
**Explanation:** Managed SFTP into S3.

### Q2

**Scenario:** Which protocol can't be used on a public internet endpoint?
**Options:** A) SFTP B) Plain FTP (unencrypted) C) FTPS D) AS2
**Correct:** B
**Explanation:** FTP is VPC-internal only.

### Q3

**Scenario:** Partners require you to give them static IPs to allow-list.
**Options:** A) Public endpoint B) VPC (internet-facing) endpoint with Elastic IPs C) Random IPs D) Not possible
**Correct:** B
**Explanation:** VPC endpoints provide fixed EIPs + security groups.

### Q4

**Scenario:** Authenticate SFTP users against corporate Microsoft AD.
**Options:** A) Service-managed only B) AWS Directory Service / AD as IdP C) Hardcode D) Public access
**Correct:** B
**Explanation:** Directory Service integration for AD auth.

### Q5

**Scenario:** Automatically PGP-decrypt and route files after upload.
**Options:** A) Cron B) Managed Workflows (decrypt + custom Lambda) C) Manual D) DataSync
**Correct:** B
**Explanation:** Workflows automate post-upload steps.

### Q6

**Scenario:** B2B EDI exchange with signing and MDN receipts.
**Options:** A) SFTP B) AS2 C) FTP D) HTTP
**Correct:** B
**Explanation:** AS2 is the B2B/EDI protocol.

### Q7

**Scenario:** Each partner must only see their own folder, not bucket structure.
**Options:** A) One shared dir B) Logical directories + per-user IAM C) Public bucket D) No isolation
**Correct:** B
**Explanation:** Logical directories mask/isolate paths.

### Q8

**Scenario:** Store files in a POSIX file system instead of object storage.
**Options:** A) S3 only B) EFS backend C) DynamoDB D) EBS
**Correct:** B
**Explanation:** Transfer Family supports EFS as a backend.

### Q9

**Scenario:** Custom auth integrating Cognito + Secrets Manager + IP checks.
**Options:** A) Service-managed B) Custom Lambda identity provider C) AD only D) None
**Correct:** B
**Explanation:** Custom IdP via Lambda enables flexible auth/logic.

### Q10

**Scenario:** Give partners a friendly hostname like sftp.company.com.
**Options:** A) Use the raw endpoint B) Map a Route 53 custom hostname C) IP only D) Not possible
**Correct:** B
**Explanation:** Route 53 custom hostname to the endpoint.

### Q11

**Scenario:** Internal team needs to bulk-migrate 50 TB of NAS to S3.
**Options:** A) Transfer Family B) DataSync C) AS2 D) FTP
**Correct:** B
**Explanation:** Bulk internal migration → DataSync.

### Q12

**Scenario:** Encrypt files at rest with a customer-managed key.
**Options:** A) None B) SSE-KMS on the S3 backend C) Only TLS D) Client app
**Correct:** B
**Explanation:** KMS for at-rest on the backend.

### Q13

**Scenario:** Audit user file operations and auth.
**Options:** A) Nothing B) CloudWatch Logs (logging role) + CloudTrail C) S3 only D) Guess
**Correct:** B
**Explanation:** CloudWatch session logs + CloudTrail control-plane audit.

### Q14

**Scenario:** Scope each user to only their S3 prefix.
**Options:** A) Admin to all B) Per-user IAM role + session policy C) Public D) Root
**Correct:** B
**Explanation:** Least-privilege per-user role/policy.

### Q15

**Scenario:** Reduce Transfer Family cost from idle servers.
**Options:** A) Keep all running B) Consolidate users/protocols; delete unused servers (hourly billing) C) Bigger bucket D) More protocols
**Correct:** B
**Explanation:** Endpoints bill hourly while they exist.

### Q16

**Scenario:** Trigger downstream processing when a file arrives.
**Options:** A) Poll B) Managed Workflow / EventBridge on upload C) Cron D) Manual
**Correct:** B
**Explanation:** Workflows/EventBridge react to uploads.

### Q17

**Scenario:** A scenario needs encrypted FTP (certificate-based).
**Options:** A) FTP B) FTPS C) HTTP D) SMB
**Correct:** B
**Explanation:** FTPS = FTP over TLS.

### Q18

**Scenario:** Replace an aging on-prem SFTP server farm.
**Options:** A) Rebuild on EC2 B) Migrate to managed Transfer Family C) DataSync D) Snowball
**Correct:** B
**Explanation:** Managed SFTP replaces self-managed servers.

### Q19

**Scenario:** Provide both upload (/inbound) and download (/outbound) virtual folders per partner.
**Options:** A) Real prefixes only B) Logical directory mappings C) Separate buckets only D) Not possible
**Correct:** B
**Explanation:** Logical directories compose a clean per-partner view.

### Q20

**Scenario:** Your own application can use the AWS SDK to write to S3 directly.
**Options:** A) Force Transfer Family B) Use S3 API directly (Transfer Family is for FTP-protocol clients) C) AS2 D) FTP
**Correct:** B
**Explanation:** No FTP client requirement → use S3 SDK; Transfer Family is for protocol-bound partners.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** A bank must let 300 external partners upload via SFTP, each isolated to their own folder, authenticated against corporate AD, with partners allow-listing fixed IPs and all files encrypted and scanned on arrival.
**Options:** A) EC2 SFTP farm B) **Transfer Family**: **VPC endpoint + Elastic IPs** (allow-list), **AD identity provider**, **per-user IAM + logical directories** (isolation), **SSE-KMS**, **Managed Workflow** AV scan C) DataSync D) Public FTP
**Correct:** B
**Explanation:** Every requirement maps to a Transfer Family feature - the canonical enterprise SFTP design.

### H2

**Scenario:** A retailer exchanges EDI documents with trading partners requiring signed, encrypted messages and delivery receipts.
**Options:** A) SFTP B) **AS2** on Transfer Family (signing, encryption, **MDN** receipts, partner profiles/agreements) C) FTP D) HTTP POST
**Correct:** B
**Explanation:** AS2 is purpose-built for B2B/EDI with MDNs.

### H3

**Scenario:** Auth must be fully custom: validate against an external API, return per-user role/home dir, and reject logins from unknown source IPs.
**Options:** A) Service-managed B) **Custom Lambda identity provider** returning role/home/policy and enforcing source-IP checks C) AD only D) Hardcoded users
**Correct:** B
**Explanation:** Custom IdP Lambda enables arbitrary auth logic and dynamic per-user config.

### H4

**Scenario:** Files dropped via SFTP must be virus-scanned, PGP-decrypted, tagged, and moved to a processing bucket - automatically, with error handling.
**Options:** A) Nightly batch B) **Managed Workflow**: custom (scan) + decrypt + tag + copy steps, with on-error path C) Manual D) DataSync
**Correct:** B
**Explanation:** Managed Workflows chain built-in + custom steps with error handling.

### H5

**Scenario:** Partners complain the endpoint IPs keep changing, breaking their firewall rules.
**Options:** A) Public endpoint (AWS-managed IPs) B) Switch to a **VPC endpoint with Elastic IPs** so the IPs are stable and allow-listable C) Rotate IPs D) Disable firewall
**Correct:** B
**Explanation:** Public endpoints use AWS-managed IPs; VPC + EIP gives stable IPs.

### H6

**Scenario:** Cost spiked: several servers run 24x7 but only one partner integration is active.
**Options:** A) Add servers B) **Consolidate** users/protocols onto fewer servers and **delete unused** ones (endpoints bill hourly) C) Bigger instances D) More EIPs
**Correct:** B
**Explanation:** Idle endpoints bill continuously; consolidate/delete.

### H7

**Scenario:** Compliance requires every file operation logged immutably and access scoped so no partner can read another's data.
**Options:** A) One shared role B) **Per-user IAM + logical directories** for isolation, **CloudWatch Logs** + **CloudTrail** (to an immutable S3/Object Lock bucket) C) Public bucket D) Admin for all
**Correct:** B
**Explanation:** Least-privilege isolation + comprehensive, immutable logging.

### H8

**Scenario:** A workload needs both managed SFTP for partners AND a one-time 80 TB bulk import of historical files.
**Options:** A) Transfer Family for both B) **Transfer Family** for ongoing partner SFTP + **DataSync/Snowball** for the one-time 80 TB bulk import C) AS2 D) FTP
**Correct:** B
**Explanation:** Right tool per job: Transfer Family = exchange; DataSync/Snow = bulk migration.

### H9

**Scenario:** Internal apps in a private VPC need plain FTP to a managed endpoint (legacy client, no TLS), never exposed publicly.
**Options:** A) Public FTP B) **VPC (internal) endpoint** with **FTP** allowed, reachable only inside the VPC/on-prem via DX/VPN C) FTPS public D) Not possible
**Correct:** B
**Explanation:** Plain FTP is permitted only on VPC-internal endpoints.

### H10

**Scenario:** A partner integration must present `/incoming` and `/reports` that actually map to two different buckets/prefixes, hiding real names.
**Options:** A) One bucket only B) **Logical directories** mapping virtual paths to multiple S3 locations C) Separate servers D) Public listing
**Correct:** B
**Explanation:** Logical directories compose multiple backends into a clean, masked view.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Partners exchange files over SFTP/FTPS/FTP/AS2 into S3/EFS, fully managed → Transfer Family. Static IPs to allow-list → VPC endpoint + Elastic IPs. AD/custom auth → Directory Service / custom Lambda IdP. Isolate partners → per-user IAM + logical directories. Post-upload automation → Managed Workflows. B2B/EDI → AS2. Bulk internal move → DataSync, not Transfer Family.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - AWS Transfer Family SRE Operations](04%20-%20AWS%20Transfer%20Family%20SRE%20Operations.md).
