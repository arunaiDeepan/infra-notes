# RDS Scenario Questions - SAA-C03 Deep Dive

> Realistic SAA-C03 scenario Q&A covering Multi-AZ vs read replica, encrypting existing DBs, RDS Proxy, reporting offload, cross-Region DR, failover behavior, storage full, and licensing.

See also: [01 - RDS Intro & Core Concepts](01%20-%20RDS%20Intro%20%26%20Core%20Concepts.md) · [02 - RDS Architecture Deep Dive](02%20-%20RDS%20Architecture%20Deep%20Dive.md) · [03 - RDS Best Practices & Examples](03%20-%20RDS%20Best%20Practices%20%26%20Examples.md) · [05 - RDS Troubleshooting (SRE)](05%20-%20RDS%20Troubleshooting%20%28SRE%29.md) · [06 - RDS Important Facts & Cheat Sheet](06%20-%20RDS%20Important%20Facts%20%26%20Cheat%20Sheet.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md)

---

## Table of Contents

- [Q1 Multi-AZ vs Read Replica](#q1-multi-az-vs-read-replica)
- [Q2 Encrypt an Existing Database](#q2-encrypt-an-existing-database)
- [Q3 Lambda Connection Exhaustion](#q3-lambda-connection-exhaustion)
- [Q4 Offloading Reporting Load](#q4-offloading-reporting-load)
- [Q5 Cross-Region Disaster Recovery](#q5-cross-region-disaster-recovery)
- [Q6 Failover Behavior and Endpoints](#q6-failover-behavior-and-endpoints)
- [Q7 Storage Filling Up](#q7-storage-filling-up)
- [Q8 Licensing Oracle and SQL Server](#q8-licensing-oracle-and-sql-server)
- [Q9 No Hardcoded Database Passwords](#q9-no-hardcoded-database-passwords)
- [Q10 Minimize Downtime During Engine Upgrade](#q10-minimize-downtime-during-engine-upgrade)

---

## Q1 Multi-AZ vs Read Replica

**Scenario:** A production MySQL RDS database must survive an Availability Zone failure with **automatic failover** and **no data loss**. Which option meets this?

- A. Add five read replicas in different AZs
- B. Enable Multi-AZ deployment
- C. Increase the instance size
- D. Schedule hourly snapshots to another AZ

**Reasoning:** Read replicas are **asynchronous** and for read scaling, not automatic failover. Snapshots are recovery, not HA. Only Multi-AZ provides a **synchronous** standby with **automatic failover**.

**Correct: B.** Multi-AZ gives synchronous replication (RPO ~0) and automatic DNS-based failover.

[⬆ Back to top](#table-of-contents)

---

## Q2 Encrypt an Existing Database

**Scenario:** An unencrypted RDS PostgreSQL instance is in production. Compliance now requires encryption at rest. What is the correct approach?

- A. Modify the instance and toggle "encryption enabled"
- B. Attach a KMS key to the running instance
- C. Take a snapshot, copy it with encryption enabled using a KMS key, then restore from the encrypted snapshot
- D. Enable Multi-AZ, which encrypts the standby

**Reasoning:** Encryption **must be enabled at creation**; you cannot toggle it on a live instance (A, B invalid). Multi-AZ has nothing to do with encryption (D). The supported path is snapshot → encrypted copy → restore.

**Correct: C.** This is the canonical "encrypt an existing DB" answer. The restored instance has a new endpoint to repoint to.

[⬆ Back to top](#table-of-contents)

---

## Q3 Lambda Connection Exhaustion

**Scenario:** A Lambda function scales to thousands of concurrent executions and overwhelms an RDS MySQL database with `Too many connections` errors. What fixes this with least effort?

- A. Increase `max_connections` indefinitely
- B. Put RDS Proxy between Lambda and RDS to pool connections
- C. Migrate to DynamoDB
- D. Add read replicas

**Reasoning:** Raising `max_connections` is bounded by instance memory and just delays the problem. DynamoDB is a re-architecture. Replicas don't help write-side connection storms. **RDS Proxy** pools and reuses connections — designed exactly for serverless.

**Correct: B.** RDS Proxy. It also improves failover and supports IAM auth.

[⬆ Back to top](#table-of-contents)

---

## Q4 Offloading Reporting Load

**Scenario:** Nightly analytical/reporting queries on the primary RDS instance slow down customer-facing transactions. How do you isolate reporting without hurting OLTP?

- A. Enable Multi-AZ and run reports on the standby
- B. Create a read replica and direct reporting queries to it
- C. Increase backup retention
- D. Move reporting to the maintenance window

**Reasoning:** The Multi-AZ standby is **not readable** (classic mode), so A is wrong. Backups/maintenance windows are irrelevant. A **read replica** absorbs read-heavy reporting traffic, protecting the primary.

**Correct: B.** Read replica with reporting pointed at its endpoint.

[⬆ Back to top](#table-of-contents)

---

## Q5 Cross-Region Disaster Recovery

**Scenario:** A company needs DR for an RDS MySQL database so it can recover in a **second Region** with low RPO. Which is the best fit?

- A. Multi-AZ deployment
- B. Cross-Region read replica that can be promoted during a disaster
- C. Daily local snapshots only
- D. EBS snapshots of the DB volume

**Reasoning:** Multi-AZ is single-Region (A). Local snapshots don't survive a Region outage (C). You can't directly snapshot RDS EBS volumes (D). A **cross-Region read replica** continuously replicates and can be **promoted** to a standalone writer.

**Correct: B.** Cross-Region read replica (also copy snapshots cross-Region for backup DR).

[⬆ Back to top](#table-of-contents)

---

## Q6 Failover Behavior and Endpoints

**Scenario:** During a Multi-AZ failover, the application briefly errors then recovers without any config change. Why?

- A. The application's hardcoded IP was updated
- B. RDS updates the DNS endpoint to point to the promoted standby; clients reconnect to the same endpoint
- C. The read replica was promoted
- D. The security group was rewritten

**Reasoning:** Clients connect to a **DNS endpoint**, not an IP. On failover, RDS promotes the standby and **updates DNS** to it; reconnecting clients hit the same name. Low DNS TTL speeds recovery.

**Correct: B.** DNS endpoint swap. Keep client DNS caching short for fast reconnection.

[⬆ Back to top](#table-of-contents)

---

## Q7 Storage Filling Up

**Scenario:** An RDS instance ran out of storage last month, causing an outage. The team wants to prevent recurrence automatically. What should they enable?

- A. A read replica
- B. RDS Storage Autoscaling with a maximum storage threshold, plus a FreeStorageSpace alarm
- C. Multi-AZ
- D. Larger backup retention

**Reasoning:** Replicas, Multi-AZ, and retention don't address capacity. **Storage Autoscaling** grows storage when free space stays under ~10% for 5+ minutes (and 6h since last change), up to a defined ceiling. Pair with a CloudWatch alarm.

**Correct: B.** Storage Autoscaling + FreeStorageSpace alarm.

[⬆ Back to top](#table-of-contents)

---

## Q8 Licensing Oracle and SQL Server

**Scenario:** A team wants to run **Oracle** on RDS but does not own Oracle licenses and wants AWS to handle licensing on a pay-as-you-go basis. Which option?

- A. BYOL (Bring Your Own License)
- B. License Included
- C. Run Oracle on Aurora
- D. Run Oracle on EC2 with a free license

**Reasoning:** Aurora cannot run Oracle (C). BYOL requires owning licenses (A). There is no free Oracle license (D). **License Included** bundles the license into the hourly/second price.

**Correct: B.** License Included. (Use BYOL only when you already own licenses.)

[⬆ Back to top](#table-of-contents)

---

## Q9 No Hardcoded Database Passwords

**Scenario:** Security requires that application code contain **no database passwords**, and access be governed by IAM. The DB is RDS PostgreSQL. What do you implement?

- A. Store the password in an environment variable
- B. Enable IAM database authentication and have the app request a short-lived auth token
- C. Disable the master password
- D. Use a public endpoint with TLS

**Reasoning:** Env vars still hold a secret (A). You can't simply disable the master account (C). Public endpoints are unrelated and risky (D). **IAM database authentication** issues a 15-minute token via the AWS API — no stored password.

**Correct: B.** IAM DB authentication (pair with TLS; consider RDS Proxy). For rotating static creds use Secrets Manager.

[⬆ Back to top](#table-of-contents)

---

## Q10 Minimize Downtime During Engine Upgrade

**Scenario:** A team must upgrade the MySQL major version and test schema changes with the ability to roll back instantly and minimal production downtime. Best approach?

- A. Modify the instance in place and hope for the best
- B. Use an RDS Blue/Green Deployment, validate on green, then switch over
- C. Restore a snapshot to a new instance and migrate manually
- D. Promote a read replica

**Reasoning:** In-place upgrades risk extended downtime and hard rollback (A). Manual snapshot migration is slow and risky (C). Promoting a replica doesn't test the upgrade safely (D). **Blue/Green Deployments** keep a synced green copy and switch over in under a minute with safety checks and easy rollback.

**Correct: B.** RDS Blue/Green Deployment.

[⬆ Back to top](#table-of-contents)
