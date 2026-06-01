# Aurora Troubleshooting (SRE) - SAA-C03 Deep Dive

> SRE-style runbook for Aurora: replica lag, failover and reconnection, storage scaling, Backtrack limits, Global Database lag, endpoint confusion, connection pile-ups, and parameter group changes — each as symptom → metric → root cause → fix → prevention.

See also: [01 - Aurora Intro & Core Concepts](01%20-%20Aurora%20Intro%20%26%20Core%20Concepts.md) · [02 - Aurora Architecture Deep Dive](02%20-%20Aurora%20Architecture%20Deep%20Dive.md) · [03 - Aurora Best Practices & Examples](03%20-%20Aurora%20Best%20Practices%20%26%20Examples.md) · [04 - Aurora Scenario Questions](04%20-%20Aurora%20Scenario%20Questions.md) · [06 - Aurora Important Facts & Cheat Sheet](06%20-%20Aurora%20Important%20Facts%20%26%20Cheat%20Sheet.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md) · [01 - RDS Intro & Core Concepts](01%20-%20RDS%20Intro%20%26%20Core%20Concepts.md)

---

## Table of Contents

- [Replica Lag & Stale Reads](#replica-lag--stale-reads)
- [Failover Events & Connection Handling](#failover-events--connection-handling)
- [Storage Scaling Issues](#storage-scaling-issues)
- [Backtrack Limits](#backtrack-limits)
- [Global Database Replication Lag](#global-database-replication-lag)
- [Writer-Reader Endpoint Confusion](#writer-reader-endpoint-confusion)
- [Connection Pile-Ups](#connection-pile-ups)
- [Parameter Group Changes](#parameter-group-changes)
- [Exam Tips & Traps](#exam-tips--traps)

---

## Replica Lag & Stale Reads

- **Symptom:** Reads via the reader endpoint return slightly stale data; reporting jobs see lag spikes.
- **Metric:** `AuroraReplicaLag` (ms), `AuroraReplicaLagMaximum`, `CPUUtilization` on replicas.
- **Root cause:** Heavy write volume, an under-sized replica, or a long-running read holding resources. Lag is normally milliseconds because replicas share storage.
- **Fix:** Scale up the lagging replica, move heavy analytics to a **custom endpoint** on a larger instance, or read from the **writer** for strict consistency.
- **Prevention:** Alarm on `AuroraReplicaLag`; size replicas like the writer; isolate reporting via custom endpoints.

[⬆ Back to top](#table-of-contents)

---

## Failover Events & Connection Handling

- **Symptom:** Brief application errors / dropped connections during a failover; some clients keep hitting the old writer.
- **Metric:** RDS events (`Failover` events), `DatabaseConnections`, app error rates.
- **Root cause:** App connected to an **instance endpoint** (or cached the old writer IP) instead of the **cluster endpoint**, so DNS promotion isn't followed.
- **Fix:** Connect writes to the **cluster endpoint**, reads to the **reader endpoint**; lower client DNS/TTL caching; add retry logic.
- **Prevention:** Use **RDS Proxy** to hold connections during failover; game-day with `failover-db-cluster`.

[⬆ Back to top](#table-of-contents)

---

## Storage Scaling Issues

- **Symptom:** Concern about running out of space, or unexpected storage cost growth.
- **Metric:** `VolumeBytesUsed`, `VolumeReadIOPS`/`VolumeWriteIOPS` (I/O cost on Standard).
- **Root cause:** Aurora storage auto-grows in **10 GB increments to 128 TiB**, so you won't "run out" until 128 TiB; cost growth often comes from **I/O on Standard**, not capacity.
- **Fix:** Reclaim space by deleting/archiving data (Aurora can shrink); if I/O dominates the bill, move to **I/O-Optimized**.
- **Prevention:** Alarm on `VolumeBytesUsed` approaching 128 TiB; track the I/O line item monthly.

[⬆ Back to top](#table-of-contents)

---

## Backtrack Limits

- **Symptom:** Cannot backtrack far enough, or Backtrack option is missing.
- **Metric:** `BacktrackChangeRecordsStored`, `BacktrackWindowActual` vs `BacktrackWindowAlias`.
- **Root cause:** Backtrack is **Aurora MySQL only**; window is capped (up to 72h) and bounded by change-record retention; high write churn shortens the effective window.
- **Fix:** For PostgreSQL or beyond-window recovery, use **PITR / snapshot restore**; increase the target window where possible.
- **Prevention:** Set an adequate backtrack window for the change rate; keep PITR/snapshots as the durable safety net (Backtrack is **not a backup**).

[⬆ Back to top](#table-of-contents)

---

## Global Database Replication Lag

- **Symptom:** Secondary-Region reads lag behind primary; DR readiness in question.
- **Metric:** `AuroraGlobalDBReplicationLag`, `AuroraGlobalDBReplicatedWriteIO`, `AuroraGlobalDBDataTransferBytes`.
- **Root cause:** Cross-Region network conditions or very high write throughput; normally < 1s.
- **Fix:** Ensure secondary has adequate replica capacity; investigate primary write spikes; if write forwarding is used, check forwarded-write latency.
- **Prevention:** Alarm on `AuroraGlobalDBReplicationLag`; keep a replica in each secondary Region for HA.

[⬆ Back to top](#table-of-contents)

---

## Writer-Reader Endpoint Confusion

- **Symptom:** Writes fail with read-only errors, or reads all land on the writer (no scaling).
- **Metric:** Error logs (`--read-only` / cannot execute write on read replica), `DatabaseConnections` skew toward the writer.
- **Root cause:** App sent writes to the **reader endpoint** (read-only) or all traffic to the **cluster (writer) endpoint**.
- **Fix:** Route **writes → cluster endpoint**, **reads → reader endpoint**; separate the two connection pools.
- **Prevention:** Enforce endpoint usage in config/IaC; for split logic use a driver/proxy that knows read vs write.

[⬆ Back to top](#table-of-contents)

---

## Connection Pile-Ups

- **Symptom:** "Too many connections" errors, especially from Lambda/serverless; rising latency.
- **Metric:** `DatabaseConnections` near `max_connections`, `FreeableMemory` dropping.
- **Root cause:** Many short-lived connections (Lambda) or missing pooling exhaust the connection limit (which scales with instance memory).
- **Fix:** Introduce **RDS Proxy** to pool/multiplex; add app-side pooling; right-size the instance (more memory → higher `max_connections`).
- **Prevention:** Standardize on RDS Proxy for serverless front-ends; alarm on `DatabaseConnections`.

[⬆ Back to top](#table-of-contents)

---

## Parameter Group Changes

- **Symptom:** A parameter change didn't take effect, or caused an unexpected restart.
- **Metric:** RDS events, `PendingModifiedValues`, parameter group "pending-reboot" status.
- **Root cause:** **Static** parameters require a **reboot** to apply; **dynamic** ones apply immediately. Cluster vs DB (instance) parameter groups control different scopes.
- **Fix:** Apply static-parameter changes during a maintenance window with a reboot; confirm you edited the correct **cluster** vs **instance** parameter group.
- **Prevention:** Track dynamic vs static parameters; manage parameter groups in IaC; test changes on a **clone** first.

[⬆ Back to top](#table-of-contents)

---

## Exam Tips & Traps

- Stale reads / lag → **AuroraReplicaLag**; isolate heavy reads on a **custom endpoint**.
- Failover errors → app must use **cluster/reader endpoints**, not instance endpoints; **RDS Proxy** smooths it.
- Storage never "fills" until **128 TiB**; runaway cost is usually **I/O on Standard** → consider **I/O-Optimized**.
- **Backtrack = MySQL only**, bounded window, **not a backup** — keep PITR/snapshots.
- DR readiness → watch **AuroraGlobalDBReplicationLag**.
- "Too many connections" (Lambda) → **RDS Proxy** + pooling.
- **Static** parameters need a **reboot**; mind **cluster vs instance** parameter groups.

[⬆ Back to top](#table-of-contents)
