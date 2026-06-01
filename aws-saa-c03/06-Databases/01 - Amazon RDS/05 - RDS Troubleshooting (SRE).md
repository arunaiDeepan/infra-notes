# RDS Troubleshooting (SRE) - SAA-C03 Deep Dive

> On-call playbooks for common RDS failures — storage full, connection exhaustion, replica lag, failover during maintenance, IOPS throttling, parameter reboots, certificate rotation, performance degradation, long transactions, and deadlocks. Each follows symptom → metric → root cause → remediation → prevention.

See also: [01 - RDS Intro & Core Concepts](01%20-%20RDS%20Intro%20%26%20Core%20Concepts.md) · [02 - RDS Architecture Deep Dive](02%20-%20RDS%20Architecture%20Deep%20Dive.md) · [03 - RDS Best Practices & Examples](03%20-%20RDS%20Best%20Practices%20%26%20Examples.md) · [04 - RDS Scenario Questions](04%20-%20RDS%20Scenario%20Questions.md) · [06 - RDS Important Facts & Cheat Sheet](06%20-%20RDS%20Important%20Facts%20%26%20Cheat%20Sheet.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md)

---

## Table of Contents

- [Storage Full DiskFull](#storage-full-diskfull)
- [Connection Exhaustion](#connection-exhaustion)
- [Replica Lag](#replica-lag)
- [Failover During Maintenance](#failover-during-maintenance)
- [IOPS Throttling and gp2 Burst Credits](#iops-throttling-and-gp2-burst-credits)
- [Parameter Group Reboot Required](#parameter-group-reboot-required)
- [Certificate Rotation rds-ca](#certificate-rotation-rds-ca)
- [Performance Degradation Diagnosis](#performance-degradation-diagnosis)
- [Long-Running Transactions](#long-running-transactions)
- [Deadlocks](#deadlocks)

---

## Storage Full DiskFull

- **Symptom:** Writes fail; instance status `storage-full`; application errors on INSERT/UPDATE; instance may become unavailable.
- **Metric:** **FreeStorageSpace** at or near 0; rising **WriteLatency**.
- **Root cause:** Allocated storage exhausted — often runaway logs (binlog, WAL), bloat, large temp tables, or unbounded growth.
- **Remediation:** Modify the instance to **increase allocated storage** (online for most engines); clear/rotate logs; reduce binlog/WAL retention; remove bloat.
- **Prevention:** Enable **Storage Autoscaling** with a max threshold; alarm on **FreeStorageSpace < 10%**; manage log retention parameters.

> [!tip] Exam Tip
> `storage-full` outage prevented automatically → **Storage Autoscaling** + FreeStorageSpace alarm.

[⬆ Back to top](#table-of-contents)

---

## Connection Exhaustion

- **Symptom:** `Too many connections` / `FATAL: remaining connection slots are reserved`; new clients rejected.
- **Metric:** **DatabaseConnections** at or near `max_connections`.
- **Root cause:** Connection storms from Lambda/autoscaling fleets; no pooling; leaked connections; `max_connections` too low for the instance memory.
- **Remediation:** Introduce **RDS Proxy** to pool/reuse connections; fix app-side connection leaks; right-size `max_connections` (it scales with instance memory). Restart offending clients.
- **Prevention:** **RDS Proxy** for serverless/spiky workloads; connection pooling in the app; alarm on DatabaseConnections approaching the limit.

> [!tip] Exam Tip
> Lambda + `Too many connections` → **RDS Proxy** is the SRE and exam answer.

[⬆ Back to top](#table-of-contents)

---

## Replica Lag

- **Symptom:** Reads from a replica return stale data; reporting numbers trail production.
- **Metric:** **ReplicaLag** (seconds) climbing.
- **Root cause:** Async replication can't keep up — heavy write volume on primary, single-threaded replication apply, undersized replica, or network/IO bottleneck on the replica.
- **Remediation:** Scale up the **replica instance class / IOPS**; reduce write burst on primary; for read-after-write needs, route critical reads to the primary; investigate long transactions blocking apply.
- **Prevention:** Size replicas to match write throughput; alarm on **ReplicaLag**; don't use replicas for strongly-consistent reads.

> [!tip] Exam Tip
> Stale replica reads = **async replication lag**, inherent to read replicas. Multi-AZ standby (synchronous) does not have user-visible lag but is not readable.

[⬆ Back to top](#table-of-contents)

---

## Failover During Maintenance

- **Symptom:** Brief connection errors during the weekly maintenance window or after a parameter change; app reconnects shortly after.
- **Metric:** RDS **events** show failover/patching; spike in connection errors then recovery.
- **Root cause:** Multi-AZ applies maintenance to the **standby first**, then **fails over** (DNS swap) to it, causing a short reconnect blip.
- **Remediation:** Implement **connection retry with backoff** in the app; keep client **DNS TTL low**; schedule the maintenance window for low-traffic periods.
- **Prevention:** Multi-AZ + retry logic; test reconnection handling; use **RDS Proxy** which holds connections and shortens failover impact.

> [!tip] Exam Tip
> Multi-AZ patches the standby then fails over to minimize downtime — apps still need **reconnect/retry** logic.

[⬆ Back to top](#table-of-contents)

---

## IOPS Throttling and gp2 Burst Credits

- **Symptom:** Periodic latency spikes / throughput cliffs on a gp2 volume, often after sustained I/O.
- **Metric:** **BurstBalance** dropping toward 0% (gp2); elevated **Read/WriteLatency**; **DiskQueueDepth** rising.
- **Root cause:** Small gp2 volumes have low baseline IOPS (3 IOPS/GiB) and rely on **burst credits**; sustained load exhausts them and throttles to baseline. Or provisioned IOPS (io1/io2) set too low.
- **Remediation:** Migrate to **gp3** (independent IOPS) or **io1/io2** (provisioned IOPS); or grow the gp2 volume to raise baseline IOPS.
- **Prevention:** Use **gp3** by default; alarm on **BurstBalance** (gp2) and latency; size IOPS to workload.

> [!tip] Exam Tip
> "Latency spikes after a period of heavy I/O on a small gp2 volume" → **burst credit exhaustion**; fix with gp3 or Provisioned IOPS.

[⬆ Back to top](#table-of-contents)

---

## Parameter Group Reboot Required

- **Symptom:** A changed parameter (e.g., `max_connections`, `rds.force_ssl`) has no effect; parameter group status shows `pending-reboot`.
- **Metric:** RDS console parameter status `pending-reboot`; behavior unchanged.
- **Root cause:** The parameter is **static**, which requires an instance **reboot** to apply (dynamic parameters apply immediately).
- **Remediation:** **Reboot** the instance during a controlled window (Multi-AZ reboot-with-failover minimizes downtime).
- **Prevention:** Know which parameters are static; batch static changes; schedule reboots in maintenance windows.

> [!tip] Exam Tip
> Parameter not taking effect = **static parameter needs a reboot**. Option Groups (e.g., TDE) are separate from Parameter Groups.

[⬆ Back to top](#table-of-contents)

---

## Certificate Rotation rds-ca

- **Symptom:** TLS connections suddenly fail with certificate validation errors near a CA expiry date.
- **Metric:** Connection errors referencing SSL/certificate; RDS console shows pending CA update.
- **Root cause:** The RDS server certificate (e.g., **rds-ca-2019 → rds-ca-rsa2048-g1**) rotated/expired; clients still trust only the old CA bundle.
- **Remediation:** Download the **current AWS RDS CA bundle**, update client truststores, and apply the new server certificate to the instance (can be done with a reboot/modify).
- **Prevention:** Track CA expiry dates; bundle the **multi-CA** truststore in clients ahead of time; automate cert-bundle updates.

> [!tip] Exam Tip
> Sudden TLS failures across all clients near a date → **RDS CA certificate rotation**; update the client trust bundle and the instance cert.

[⬆ Back to top](#table-of-contents)

---

## Performance Degradation Diagnosis

- **Symptom:** Queries slow despite adequate CPU/memory; intermittent latency.
- **Metric:** **Performance Insights** DB load by **wait event**; top SQL; **Enhanced Monitoring** for per-process OS detail.
- **Root cause:** Missing indexes, lock waits, I/O waits, or a few heavy queries dominating load — typically a **customer-responsibility** (schema/query) issue.
- **Remediation:** Use **Performance Insights** to find the top wait events and SQL; add/adjust indexes; rewrite hot queries; raise IOPS if I/O-bound; scale up if genuinely resource-bound.
- **Prevention:** Enable **Performance Insights** + **Enhanced Monitoring**; baseline normal load; review slow query logs.

> [!tip] Exam Tip
> "Identify the exact query/wait event causing load" → **Performance Insights**. "Per-process OS metrics at 1s" → **Enhanced Monitoring**.

[⬆ Back to top](#table-of-contents)

---

## Long-Running Transactions

- **Symptom:** Bloating undo/WAL, blocked queries, rising replica lag, storage growth.
- **Metric:** Long transaction age (engine views), growing **FreeStorageSpace** consumption, **ReplicaLag**.
- **Root cause:** An open transaction never commits/rolls back — idle-in-transaction sessions, batch jobs, or app bugs holding locks and pinning log cleanup.
- **Remediation:** Identify and terminate the offending session; commit/rollback; set **idle-in-transaction timeout**; fix the app to commit promptly.
- **Prevention:** Configure transaction/lock timeouts via parameter group; monitor for idle-in-transaction sessions; code reviews on transaction scope.

> [!tip] Exam Tip
> Long-open transactions can both **fill storage** (log/undo retention) and **increase replica lag**. Set idle-in-transaction timeouts.

[⬆ Back to top](#table-of-contents)

---

## Deadlocks

- **Symptom:** Transactions abort with deadlock errors; intermittent failures under concurrency.
- **Metric:** Engine deadlock counters / logs (e.g., `SHOW ENGINE INNODB STATUS`, PostgreSQL deadlock log entries).
- **Root cause:** Two+ transactions acquire locks in **conflicting order**, each waiting on the other; the engine kills one victim.
- **Remediation:** Retry the victim transaction with backoff (app-side); enable deadlock logging to find the pattern.
- **Prevention:** Acquire locks in a **consistent order**; keep transactions short; reduce lock scope; add appropriate indexes to shrink locked ranges.

> [!tip] Exam Tip
> Deadlocks are an **application/schema** concern (your responsibility), not an RDS platform fault — fix with consistent lock ordering and retries.

[⬆ Back to top](#table-of-contents)
