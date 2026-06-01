# Aurora Important Facts & Cheat Sheet - SAA-C03 Deep Dive

> Dense, exam-ready reference: durability/quorum numbers, replica and storage limits, Global Database limits, endpoints, Backtrack vs PITR, Aurora vs RDS, key metrics, and 20+ rapid-fire facts.

See also: [01 - Aurora Intro & Core Concepts](01%20-%20Aurora%20Intro%20%26%20Core%20Concepts.md) · [02 - Aurora Architecture Deep Dive](02%20-%20Aurora%20Architecture%20Deep%20Dive.md) · [03 - Aurora Best Practices & Examples](03%20-%20Aurora%20Best%20Practices%20%26%20Examples.md) · [04 - Aurora Scenario Questions](04%20-%20Aurora%20Scenario%20Questions.md) · [05 - Aurora Troubleshooting (SRE)](05%20-%20Aurora%20Troubleshooting%20%28SRE%29.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md) · [01 - RDS Intro & Core Concepts](01%20-%20RDS%20Intro%20%26%20Core%20Concepts.md)

---

## Table of Contents

- [Durability & Quorum](#durability--quorum)
- [Cluster Limits](#cluster-limits)
- [Global Database Limits](#global-database-limits)
- [Failover Priority](#failover-priority)
- [Endpoints Table](#endpoints-table)
- [Backtrack vs PITR](#backtrack-vs-pitr)
- [Aurora vs RDS Comparison](#aurora-vs-rds-comparison)
- [Key Metrics](#key-metrics)
- [Rapid-Fire Facts](#rapid-fire-facts)

---

## Durability & Quorum

| Item               | Value                                                                             |
| :----------------- | :-------------------------------------------------------------------------------- |
| Copies of data     | **6**                                                                             |
| Availability Zones | **3** (2 copies each)                                                             |
| Write quorum (Vw)  | **4 of 6**                                                                        |
| Read quorum (Vr)   | **3 of 6**                                                                        |
| Survives           | Loss of a full **AZ** (writes continue); loss of **AZ + 1 copy** (reads continue) |
| Storage segment    | **10 GB** protection groups, each 6-way replicated                                |
| Self-healing       | Automatic, continuous                                                             |

[⬆ Back to top](#table-of-contents)

---

## Cluster Limits

| Item                    | Value                                       |
| :---------------------- | :------------------------------------------ |
| Writer instances        | **1** (single-master, common mode)          |
| Aurora Replicas         | **Up to 15**                                |
| Replica lag             | Typically **milliseconds** (shared storage) |
| Failover time           | Typically **< 30s**                         |
| Storage max             | **128 TiB**                                 |
| Storage growth          | **10 GB** increments, automatic             |
| Backup retention (PITR) | **1–35 days**                               |
| Backtrack window        | Up to **72 hours** (Aurora MySQL only)      |

[⬆ Back to top](#table-of-contents)

---

## Global Database Limits

| Item                   | Value                                    |
| :--------------------- | :--------------------------------------- |
| Primary Regions        | **1**                                    |
| Secondary Regions      | **Up to 5**                              |
| Replicas per secondary | Up to **16** (read-only)                 |
| Replication latency    | Typically **< 1 second**                 |
| RPO                    | **~1 second**                            |
| RTO                    | **< 1 minute**                           |
| Write forwarding       | Supported (MySQL & PostgreSQL)           |
| Replication type       | **Storage-layer** (no instance CPU cost) |

[⬆ Back to top](#table-of-contents)

---

## Failover Priority

| Item            | Value                                          |
| :-------------- | :--------------------------------------------- |
| Promotion tiers | **0–15**                                       |
| Promoted first  | **Lowest tier number** (0 = highest priority)  |
| Tie-breaker     | **Largest instance size** within the same tier |
| No replicas     | Aurora creates a new instance (slower)         |

[⬆ Back to top](#table-of-contents)

---

## Endpoints Table

| Endpoint             | Targets                | Use                                |
| :------------------- | :--------------------- | :--------------------------------- |
| **Cluster (writer)** | Current writer         | Writes; follows failover           |
| **Reader**           | Load-balanced replicas | Scale-out reads                    |
| **Custom**           | User-defined subset    | Targeted routing (e.g., analytics) |
| **Instance**         | One instance           | Diagnostics only — avoid in apps   |

[⬆ Back to top](#table-of-contents)

---

## Backtrack vs PITR

| Aspect          | Backtrack                               | PITR / Snapshot Restore       |
| :-------------- | :-------------------------------------- | :---------------------------- |
| Engine          | **Aurora MySQL only**                   | MySQL & PostgreSQL            |
| Mechanism       | **In-place rewind** of existing cluster | Restore to a **new** cluster  |
| Speed           | Seconds–minutes                         | Slower (new cluster)          |
| Window          | Up to **72h** (change records)          | Retention **1–35 days**       |
| Is it a backup? | **No**                                  | Yes (continuous to S3)        |
| Best for        | Quick undo of a bad write               | Durable recovery / compliance |

[⬆ Back to top](#table-of-contents)

---

## Aurora vs RDS Comparison

| Dimension       | RDS (MySQL/PostgreSQL)                         | Aurora                       |
| :-------------- | :--------------------------------------------- | :--------------------------- |
| Storage         | EBS per instance                               | Shared 6-copy / 3-AZ volume  |
| Read replicas   | Up to 5, async                                 | **Up to 15**, low lag        |
| Failover        | ~60–120s                                       | **< 30s**                    |
| Storage scaling | Manual/autoscaling                             | Auto, 10 GB → **128 TiB**    |
| Throughput      | Baseline                                       | **5x MySQL / 3x PostgreSQL** |
| Backtrack       | No                                             | **Yes (MySQL)**              |
| Global Database | No                                             | **Yes**                      |
| Cloning         | No (snapshot copy)                             | **Fast copy-on-write**       |
| Engines         | MySQL, PostgreSQL, MariaDB, Oracle, SQL Server | **MySQL & PostgreSQL only**  |

[⬆ Back to top](#table-of-contents)

---

## Key Metrics

| Metric                               | Watch for                    |
| :----------------------------------- | :--------------------------- |
| `AuroraReplicaLag`                   | Stale reads / replica health |
| `AuroraGlobalDBReplicationLag`       | DR readiness                 |
| `DatabaseConnections`                | Connection pile-ups          |
| `CPUUtilization`                     | Right-sizing / auto scaling  |
| `FreeableMemory`                     | Memory pressure              |
| `VolumeBytesUsed`                    | Storage growth to 128 TiB    |
| `VolumeReadIOPS` / `VolumeWriteIOPS` | I/O cost (Standard)          |
| `BacktrackChangeRecordsStored`       | Backtrack window health      |

[⬆ Back to top](#table-of-contents)

---

## Rapid-Fire Facts

1. Aurora is **MySQL- and PostgreSQL-compatible**, cloud-native.
2. **5x** MySQL / **3x** PostgreSQL throughput (AWS claim).
3. Compute and storage are **decoupled**.
4. **6 copies** of data across **3 AZs**.
5. Write quorum **4/6**, read quorum **3/6**.
6. Storage auto-grows **10 GB** increments to **128 TiB**.
7. Storage segments are **10 GB** protection groups.
8. **1 writer** + **up to 15 Aurora Replicas**.
9. Replicas share storage → **millisecond** lag.
10. Failover typically **< 30s**.
11. Promotion **tiers 0–15**; lowest wins; ties by **size**.
12. Endpoints: **cluster, reader, custom, instance**.
13. Use **cluster/reader endpoints** in apps, never instance.
14. **Global Database**: 1 primary + **up to 5** secondary Regions.
15. Global DB replication **< 1s**, **RPO ~1s**, **RTO < 1 min**.
16. **Write forwarding** lets secondaries write to primary.
17. **Backtrack = Aurora MySQL only**, in-place, up to **72h**, not a backup.
18. **Fast cloning** is **copy-on-write** — minutes regardless of size.
19. **Continuous backup** to **S3**, no perf impact; PITR **1–35 days**.
20. **Encryption** (KMS) must be enabled **at creation**; add later via snapshot-copy.
21. **I/O-Optimized** removes per-I/O charges — pick when I/O **> ~25%** of bill.
22. **Aurora Serverless v2** auto-scales compute in **ACUs**.
23. **RDS Proxy** pools connections, smooths failover (great for Lambda).
24. Aurora supports **only MySQL & PostgreSQL** (no Oracle/SQL Server/MariaDB).
25. Static parameter changes need a **reboot**; mind **cluster vs instance** parameter groups.

[⬆ Back to top](#table-of-contents)
