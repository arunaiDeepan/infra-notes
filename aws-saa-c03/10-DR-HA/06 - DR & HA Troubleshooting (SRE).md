# DR & HA Troubleshooting (SRE) - SAA-C03 Deep Dive

> On-call playbooks for the failures that break availability and DR: failover that didn't trigger, replica lag blowing the RPO, AZ capacity imbalance, NAT/SPOF outages, ELB health-check flapping, DNS failover not happening (TTL), restore failures, and untested DR runbooks. Each follows symptom → metric/signal → root cause → remediation → prevention.

See also: [00 - DR & HA Overview & Exam Guide](00%20-%20DR%20%26%20HA%20Overview%20%26%20Exam%20Guide.md) · [02 - High Availability Building Blocks](02%20-%20High%20Availability%20Building%20Blocks.md) · [03 - The Four DR Strategies](03%20-%20The%20Four%20DR%20Strategies.md) · [04 - Cross-Region, Backup & Data Replication](04%20-%20Cross-Region%2C%20Backup%20%26%20Data%20Replication.md) · [05 - DR & HA Scenario Questions](05%20-%20DR%20%26%20HA%20Scenario%20Questions.md) · [07 - DR & HA Important Facts & Cheat Sheet](07%20-%20DR%20%26%20HA%20Important%20Facts%20%26%20Cheat%20Sheet.md)

---

## Table of Contents

- [RDS Multi-AZ Failover Did Not Trigger](#rds-multi-az-failover-did-not-trigger)
- [Cross-Region Replica Lag Breaks RPO](#cross-region-replica-lag-breaks-rpo)
- [AZ Capacity Imbalance After Failure](#az-capacity-imbalance-after-failure)
- [NAT Gateway AZ Outage](#nat-gateway-az-outage)
- [ELB Health Check Flapping](#elb-health-check-flapping)
- [Route 53 Failover Not Happening DNS TTL](#route-53-failover-not-happening-dns-ttl)
- [Sessions Lost on Instance Replacement](#sessions-lost-on-instance-replacement)
- [Backup Restore Fails or Is Too Slow](#backup-restore-fails-or-is-too-slow)
- [S3 Replication Not Copying Objects](#s3-replication-not-copying-objects)
- [DR Failover Untested Runbook Drift](#dr-failover-untested-runbook-drift)

---

## RDS Multi-AZ Failover Did Not Trigger

- **Symptom:** Primary AZ degraded but the application kept hitting the dead primary; long outage.
- **Signal:** No `RDS-EVENT` failover event; app using a **cached IP** or a stale connection pool.
- **Root cause:** App resolved and **pinned the IP** of the old primary instead of re-resolving the **RDS endpoint DNS**; or very long client-side DNS caching; or single-AZ instance (Multi-AZ never enabled).
- **Remediation:** Confirm **Multi-AZ is enabled**; make the app connect to the **endpoint name** and **re-resolve DNS on reconnect**; lower JVM/driver DNS TTL; use **RDS Proxy** for faster, transparent failover.
- **Prevention:** Use RDS Proxy or short DNS TTL; never cache the resolved IP; test failover with **reboot-with-failover**.

> [!tip] Exam Tip
> Failover works by **swapping the DNS record** to the standby. Apps that cache the IP miss it → connect via the **endpoint** and honour DNS TTL, or use **RDS Proxy**.

[⬆ Back to top](#table-of-contents)

---

## Cross-Region Replica Lag Breaks RPO

- **Symptom:** After a Region failover, more data was lost than the SLA allows.
- **Signal:** High **ReplicaLag** / **AuroraGlobalDBReplicationLag**; replication throttled.
- **Root cause:** Async replication couldn't keep up — write bursts, undersized replica, network constraints; RPO target was tighter than the replication mechanism can deliver.
- **Remediation:** Right-size the replica; reduce write amplification; for relational near-zero RPO move to **Aurora Global Database**; for active-active NoSQL use **DynamoDB Global Tables**.
- **Prevention:** Alarm on replication lag against the **RPO budget**; load-test replication under peak writes; pick a mechanism whose lag fits the RPO.

> [!tip] Exam Tip
> Cross-Region replication is **asynchronous** — there is always lag. If the RPO is ~seconds, choose **Aurora Global DB** (~1s) or **DynamoDB Global Tables**, not snapshot copy.

[⬆ Back to top](#table-of-contents)

---

## AZ Capacity Imbalance After Failure

- **Symptom:** When one AZ failed, the surviving AZ couldn't handle the full load → throttling/timeouts.
- **Signal:** Healthy-host count halved; CPU/latency spike on remaining instances.
- **Root cause:** ASG capacity sized only for the **sum across AZs at normal load**, so losing an AZ left too few instances; or instances spread across too few AZs.
- **Remediation:** Increase ASG `min`/desired so the **remaining AZs** can absorb a full AZ loss (the "N+1 / lose-one-AZ" rule); spread across **3 AZs** so losing one drops only ~⅓ of capacity.
- **Prevention:** Capacity-plan for **AZ-1 survivability**; enable predictive/target scaling with headroom; use ≥3 AZs.

> [!tip] Exam Tip
> HA isn't just "multiple AZs" — you must have **enough spare capacity** that the survivors carry the load when one AZ is gone. Three AZs reduce the per-AZ blast radius vs two.

[⬆ Back to top](#table-of-contents)

---

## NAT Gateway AZ Outage

- **Symptom:** An AZ failed and **all** private instances (including healthy AZs) lost outbound internet.
- **Signal:** Outbound calls time out fleet-wide; only one NAT GW exists.
- **Root cause:** Single NAT Gateway in the failed AZ; all private route tables pointed at it.
- **Remediation:** Create a NAT GW **in each AZ**; point each AZ's private route table at its **local** NAT GW.
- **Prevention:** Standardise **one NAT GW per AZ** in IaC; alarm on NAT GW `ErrorPortAllocation`/packet drops.

> [!tip] Exam Tip
> Single NAT GW = AZ-bound **SPOF** and inter-AZ data cost. Per-AZ NAT GW + per-AZ routes is the only HA-correct pattern.

[⬆ Back to top](#table-of-contents)

---

## ELB Health Check Flapping

- **Symptom:** Targets cycle healthy/unhealthy; intermittent 5xx; ASG churns instances.
- **Signal:** `UnHealthyHostCount` oscillating; target group health flapping.
- **Root cause:** Health-check **path** too heavy or hits a dependency (DB); thresholds/timeout too aggressive; interval shorter than app warm-up; deregistration delay too short.
- **Remediation:** Point health checks at a **lightweight, dependency-free** path (e.g. `/health`); tune **healthy/unhealthy thresholds, interval, timeout**; set sensible **deregistration delay (connection draining)**; align ASG **health-check grace period** with boot time.
- **Prevention:** Shallow vs deep health-check design; load-test under churn; grace period ≥ app startup.

> [!tip] Exam Tip
> A health check that calls the **database** turns a DB blip into a full fleet outage. Keep liveness checks **shallow**; reserve deep checks for separate monitoring.

[⬆ Back to top](#table-of-contents)

---

## Route 53 Failover Not Happening DNS TTL

- **Symptom:** Primary Region down, but clients kept resolving to it for minutes.
- **Signal:** Health check is unhealthy, yet old IP still served to clients.
- **Root cause:** **High record TTL** → resolvers/clients cache the old answer; or health check misconfigured (wrong port/path) so it never marked unhealthy.
- **Remediation:** Lower the record **TTL** (e.g. 60s) on failover-critical records; verify the **health check** target/threshold; use **Alias** to AWS resources where possible.
- **Prevention:** Pre-set low TTLs on DR records; test failover end-to-end; monitor health-check status.

> [!tip] Exam Tip
> DNS failover is only as fast as the **TTL** clients cache. Keep TTL low (e.g. 60s) on records you intend to fail over.

[⬆ Back to top](#table-of-contents)

---

## Sessions Lost on Instance Replacement

- **Symptom:** Users logged out / cart lost whenever the ASG replaces or scales in an instance.
- **Signal:** Complaints correlate with scaling/termination events.
- **Root cause:** **Stateful** web tier — session in instance memory or local disk.
- **Remediation:** Externalise session state to **ElastiCache (Redis)** or **DynamoDB**; store uploads in **S3/EFS**, not local EBS.
- **Prevention:** Design the tier **stateless** from the start; treat instances as cattle, not pets.

> [!tip] Exam Tip
> "Logged out on scale-in" = **stateful tier**. Fix by externalising state, not by sticky sessions (which just re-create the SPOF).

[⬆ Back to top](#table-of-contents)

---

## Backup Restore Fails or Is Too Slow

- **Symptom:** DR test restore fails, or takes far longer than the RTO.
- **Signal:** Restore job errors (KMS access, missing snapshot in DR Region); restore time > RTO.
- **Root cause:** Snapshot/AMI **not copied to the DR Region**; **KMS key** not available/shared cross-Region or cross-account; cold/archive storage retrieval time; restore process never timed.
- **Remediation:** Copy snapshots/AMIs (and **re-encrypt with a DR-Region KMS key**) cross-Region; ensure cross-account KMS grants; account for Glacier retrieval times; pre-stage what you can (Pilot Light).
- **Prevention:** Automate cross-Region copy via **AWS Backup**; **regularly test restores** and measure against RTO; document the runbook.

> [!tip] Exam Tip
> A backup you've never **restored** is not a backup. Cross-Region restores commonly fail on **KMS key availability** — the DR Region needs an accessible key.

[⬆ Back to top](#table-of-contents)

---

## S3 Replication Not Copying Objects

- **Symptom:** Objects exist in the source bucket but never appear in the destination.
- **Signal:** Replication metrics show no/failed replication.
- **Root cause:** **Versioning not enabled** on both buckets; replication rule added **after** objects existed (only new objects replicate); missing IAM role permissions; KMS-encrypted objects without replication config; replication rule scoped by prefix/tag that excludes them.
- **Remediation:** Enable **versioning** on both; run **S3 Batch Replication** for existing objects; fix the replication **IAM role** and **KMS** permissions; verify rule scope.
- **Prevention:** Enable versioning + replication **before** loading data; monitor replication metrics; use Batch Replication for backfills.

> [!tip] Exam Tip
> S3 replication needs **versioning** and only copies objects created **after** it's enabled. Backfill existing objects with **S3 Batch Replication**.

[⬆ Back to top](#table-of-contents)

---

## DR Failover Untested Runbook Drift

- **Symptom:** A real disaster exposes broken DR — wrong AMI, missing IAM, drifted config, undocumented steps.
- **Signal:** Failover takes far longer than planned; manual scramble; secondary can't be promoted.
- **Root cause:** DR never exercised; infrastructure drift between primary and DR; tribal-knowledge runbooks.
- **Remediation:** Run **regular game-day DR drills**; codify both Regions with the **same IaC** (CloudFormation/Terraform); automate promotion/DNS steps.
- **Prevention:** Scheduled DR tests, drift detection, version-controlled runbooks; measure actual RTO/RPO against targets.

> [!tip] Exam Tip
> The Well-Architected reliability pillar stresses **testing recovery procedures**. "We have a DR plan but never tested it" is itself the risk — drills convert a plan into a capability.

[⬆ Back to top](#table-of-contents)
