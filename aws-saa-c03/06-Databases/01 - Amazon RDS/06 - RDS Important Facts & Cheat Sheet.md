# RDS Important Facts & Cheat Sheet - SAA-C03 Deep Dive

> Dense quick-reference: limits, ports, storage maxes, Multi-AZ vs read replica comparison, encryption facts, key CloudWatch metrics, and 20+ rapid-fire exam facts.

See also: [01 - RDS Intro & Core Concepts](01%20-%20RDS%20Intro%20%26%20Core%20Concepts.md) · [02 - RDS Architecture Deep Dive](02%20-%20RDS%20Architecture%20Deep%20Dive.md) · [03 - RDS Best Practices & Examples](03%20-%20RDS%20Best%20Practices%20%26%20Examples.md) · [04 - RDS Scenario Questions](04%20-%20RDS%20Scenario%20Questions.md) · [05 - RDS Troubleshooting (SRE)](05%20-%20RDS%20Troubleshooting%20%28SRE%29.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md)

---

## Table of Contents

- [Limits and Quotas](#limits-and-quotas)
- [Default Ports](#default-ports)
- [Storage Maximums](#storage-maximums)
- [Multi-AZ vs Read Replica](#multi-az-vs-read-replica)
- [Encryption Facts](#encryption-facts)
- [Key CloudWatch Metrics](#key-cloudwatch-metrics)
- [Rapid-Fire Exam Facts](#rapid-fire-exam-facts)

---

## Limits and Quotas

| Item                                         | Value                                                  |
| :------------------------------------------- | :----------------------------------------------------- |
| Automated backup retention                   | **0–35 days** (0 disables)                             |
| PITR granularity                             | ~**5 minutes** (within retention)                      |
| Read replicas (MySQL / MariaDB / PostgreSQL) | **15**                                                 |
| Read replicas (Oracle / SQL Server)          | **5**                                                  |
| Maintenance window                           | **30 min/week**                                        |
| IAM auth token lifetime                      | **15 minutes**                                         |
| Stopped instance auto-restart                | after **7 days**                                       |
| Storage autoscaling trigger                  | free < **10%** for **5 min**, **6h** since last change |

> [!tip] Exam Tip
> Memorize **35-day** max retention and **15** read replicas (open-source engines) / **5** (Oracle, SQL Server).

[⬆ Back to top](#table-of-contents)

---

## Default Ports

| Engine                         | Port     |
| :----------------------------- | :------- |
| MySQL / MariaDB / Aurora MySQL | **3306** |
| PostgreSQL / Aurora PostgreSQL | **5432** |
| Oracle                         | **1521** |
| SQL Server                     | **1433** |

> [!tip] Exam Tip
> Security group questions hinge on the right port: MySQL **3306**, PostgreSQL **5432**, Oracle **1521**, SQL Server **1433**.

[⬆ Back to top](#table-of-contents)

---

## Storage Maximums

| Engine                                   | Max storage                                                    |
| :--------------------------------------- | :------------------------------------------------------------- |
| MySQL, MariaDB, PostgreSQL, Oracle       | **64 TiB**                                                     |
| SQL Server                               | **16 TiB**                                                     |
| Storage types                            | gp3, gp2 (legacy), io1, io2 (Block Express), magnetic (legacy) |
| gp3 baseline                             | 3,000 IOPS / 125 MB/s, independently scalable                  |
| Provisioned IOPS max (io2 Block Express) | up to **256,000 IOPS**                                         |

> [!tip] Exam Tip
> Most engines top out at **64 TiB**; **SQL Server is the outlier at 16 TiB**.

[⬆ Back to top](#table-of-contents)

---

## Multi-AZ vs Read Replica

| Feature               | Multi-AZ (instance) | Read Replica               | Multi-AZ DB Cluster    |
| :-------------------- | :------------------ | :------------------------- | :--------------------- |
| Replication           | Synchronous         | Asynchronous               | Semi-synchronous       |
| Primary purpose       | HA / failover       | Read scaling               | HA + readable standbys |
| Standby readable?     | **No**              | Yes (it's a replica)       | **Yes** (2 readers)    |
| Automatic failover?   | Yes (~60–120s)      | No (manual promote)        | Yes (~under 35s)       |
| Cross-Region?         | No                  | **Yes**                    | No                     |
| Count                 | 1 standby           | up to 15 / 5               | 2 standbys             |
| Data loss on failover | ~0 (RPO~0)          | possible lag               | minimal                |
| Use for               | Survive AZ failure  | Offload reads / DR promote | HA + read capacity     |

> [!tip] Exam Tip
> Multi-AZ = **availability**, read replica = **scalability**. Standby in classic Multi-AZ is **not readable**. Cross-Region DR for RDS = **cross-Region read replica**.

[⬆ Back to top](#table-of-contents)

---

## Encryption Facts

| Fact                    | Detail                                                                                     |
| :---------------------- | :----------------------------------------------------------------------------------------- |
| At-rest engine          | **AWS KMS**                                                                                |
| When to enable          | **At creation only**                                                                       |
| Encrypt existing DB     | Snapshot → **copy with encryption** → restore                                              |
| What's covered          | Storage, automated backups, snapshots, read replicas                                       |
| Replica of encrypted DB | Also encrypted                                                                             |
| TDE (column/tablespace) | **Oracle & SQL Server** via **Option Group**                                               |
| In transit              | **TLS/SSL** via `rds-ca` bundle; enforce with `rds.force_ssl` / `require_secure_transport` |
| Can't encrypt           | An encrypted DB cannot be made unencrypted                                                 |

> [!tip] Exam Tip
> Two encryption traps: (1) **must enable at create**; (2) to encrypt an existing DB use **snapshot → copy-with-KMS → restore**.

[⬆ Back to top](#table-of-contents)

---

## Key CloudWatch Metrics

| Metric                         | Watch for                   |
| :----------------------------- | :-------------------------- |
| **CPUUtilization**             | Sustained high CPU          |
| **FreeStorageSpace**           | DiskFull prevention         |
| **FreeableMemory**             | Memory pressure             |
| **DatabaseConnections**        | Connection exhaustion       |
| **ReadLatency / WriteLatency** | I/O bottleneck              |
| **ReadIOPS / WriteIOPS**       | Throughput                  |
| **DiskQueueDepth**             | I/O saturation              |
| **ReplicaLag**                 | Stale replica reads         |
| **BurstBalance**               | gp2 burst credit exhaustion |
| **SwapUsage**                  | Memory thrashing            |

For deeper analysis: **Performance Insights** (wait events / top SQL) and **Enhanced Monitoring** (per-process OS, 1s granularity).

> [!tip] Exam Tip
> Core alarms: **CPUUtilization, FreeStorageSpace, ReadLatency, DatabaseConnections**. Add **ReplicaLag** and **BurstBalance** when relevant.

[⬆ Back to top](#table-of-contents)

---

## Rapid-Fire Exam Facts

1. RDS = managed relational DB on **EC2 + EBS**; no OS access (except **RDS Custom**).
2. Six engines: **MySQL, MariaDB, PostgreSQL, Oracle, SQL Server, Aurora**.
3. **Aurora can't run Oracle/SQL Server** — those need RDS (or EC2).
4. **Multi-AZ** = synchronous standby, automatic failover, **not readable**, single-Region.
5. **Read replicas** = asynchronous, readable, up to **15** (open-source) / **5** (commercial), can be **cross-Region**.
6. **Cross-Region read replica** = the RDS DR pattern; promote to writer.
7. **Multi-AZ DB cluster** = 1 writer + **2 readable standbys**, failover under ~35s.
8. Connect via **DNS endpoint**, never IP; failover swaps DNS.
9. Backups: automated **0–35 days**, **PITR ~5 min**; restore = **new instance**.
10. **Automated backups deleted with the instance**; **manual snapshots persist**.
11. Encryption (**KMS**) must be enabled **at create**; existing DB → snapshot/copy-encrypted/restore.
12. **TDE** = Oracle/SQL Server via **Option Group**; TLS in transit via `rds-ca`.
13. **RDS Proxy** = connection pooling for **Lambda**; cuts failover time; supports IAM auth + Secrets Manager.
14. **IAM DB auth** (MySQL/PostgreSQL) = **15-min** token, no stored password.
15. **Secrets Manager** = automatic credential **rotation**.
16. **Blue/Green Deployments** = safe engine/schema upgrades, switchover <1 min.
17. **gp3** is the modern default (independent IOPS); **io1/io2** for guaranteed high IOPS; **gp2** bursts then throttles.
18. **Storage Autoscaling** prevents DiskFull (free <10% for 5 min, 6h since last change).
19. Storage max **64 TiB** (most), **16 TiB** SQL Server.
20. **Static parameters** require a **reboot**; dynamic apply immediately.
21. **Reserved Instances** for steady prod; **stop/start** for idle dev (auto-restart after 7 days).
22. Oracle/SQL Server licensing: **License Included** vs **BYOL**.
23. **Performance Insights** = wait events/top SQL; **Enhanced Monitoring** = per-process OS at 1s.
24. Maintenance: **30-min weekly window**; minor versions can auto-apply, **major never auto**.
25. **Burstable (db.t)** uses CPU credits — not for sustained production load.

> [!tip] Exam Tip
> If you remember only one line: **Multi-AZ = availability (sync, not readable), Read Replica = scalability (async, readable, cross-Region for DR).**

[⬆ Back to top](#table-of-contents)
