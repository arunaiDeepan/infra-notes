# Keyspaces Scenario Questions - SAA-C03 Deep Dive

> Exam-style scenario questions for Amazon Keyspaces — migrating self-managed Cassandra to a serverless managed service while keeping CQL/drivers, eliminating Cassandra cluster ops, high-throughput IoT/time-series, multi-Region active-active wide-column, and Keyspaces vs DynamoDB decisions. Each item gives the scenario, the answer, and why the distractors fail.

See also: [01 - Keyspaces Intro & Core Concepts](01%20-%20Keyspaces%20Intro%20%26%20Core%20Concepts.md) · [02 - Keyspaces Architecture Deep Dive](02%20-%20Keyspaces%20Architecture%20Deep%20Dive.md) · [03 - Keyspaces Best Practices & Examples](03%20-%20Keyspaces%20Best%20Practices%20%26%20Examples.md) · [05 - Keyspaces Troubleshooting (SRE)](05%20-%20Keyspaces%20Troubleshooting%20%28SRE%29.md) · [06 - Keyspaces Important Facts & Cheat Sheet](06%20-%20Keyspaces%20Important%20Facts%20%26%20Cheat%20Sheet.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md) · [01 - DynamoDB Intro & Core Concepts](01%20-%20DynamoDB%20Intro%20%26%20Core%20Concepts.md)

---

## Table of Contents

- [Q1 - Migrate Self-Managed Cassandra](#q1---migrate-self-managed-cassandra)
- [Q2 - Eliminate Cluster Ops and Scaling](#q2---eliminate-cluster-ops-and-scaling)
- [Q3 - High-Throughput IoT Time-Series](#q3---high-throughput-iot-time-series)
- [Q4 - Multi-Region Active-Active](#q4---multi-region-active-active)
- [Q5 - Keyspaces vs DynamoDB Decision](#q5---keyspaces-vs-dynamodb-decision)
- [Q6 - Spiky Unpredictable Traffic](#q6---spiky-unpredictable-traffic)
- [Q7 - Private Connectivity and Encryption](#q7---private-connectivity-and-encryption)
- [Q8 - Recover from Accidental Deletes](#q8---recover-from-accidental-deletes)

---

## Q1 - Migrate Self-Managed Cassandra

**Scenario:** A company runs Apache Cassandra on EC2. They want a fully managed service that keeps their **existing CQL queries and Cassandra drivers** with minimal application changes.

**Answer:** Migrate to **Amazon Keyspaces (for Apache Cassandra)**. Repoint the existing Cassandra drivers to the Keyspaces endpoint (TLS:9142 + SigV4); use **DSBulk/cqlsh** to move the data.

**Why not the others:**

- **DynamoDB** — a different API; would require rewriting the data-access layer (no CQL).
- **RDS/Aurora** — relational, not a wide-column CQL store.
- **MemoryDB / ElastiCache** — in-memory, not a Cassandra replacement.

> [!tip] Exam Tip
> "Keep CQL / existing Cassandra drivers, minimal rewrite" is the unambiguous Keyspaces signal.

[⬆ Back to top](#table-of-contents)

---

## Q2 - Eliminate Cluster Ops and Scaling

**Scenario:** The Cassandra team spends time on node replacement, ring rebalancing, repairs, patching, and capacity planning. Leadership wants to **eliminate this operational burden** while staying Cassandra-compatible.

**Answer:** Move to **Amazon Keyspaces** — serverless, so there are no nodes/clusters to manage; it scales automatically and AWS handles patching/repairs/replication.

**Why not the others:**

- **Cassandra on a bigger EC2 fleet / EMR** — still self-managed ops (the trap).
- **Self-managed Cassandra with Auto Scaling groups** — ASG does not manage Cassandra ring operations, repairs, or schema.

> [!tip] Exam Tip
> Any answer that still leaves you running Cassandra on EC2 fails an "eliminate operational overhead" requirement.

[⬆ Back to top](#table-of-contents)

---

## Q3 - High-Throughput IoT Time-Series

**Scenario:** Millions of IoT devices stream sensor readings that must be stored at very high write volume and queried by device and time, using a wide-column model.

**Answer:** **Amazon Keyspaces** with a **bounded composite partition key** (e.g., `(device_id, day_bucket)`) and a **time clustering column** (`event_ts DESC`). Use **on-demand** capacity for unpredictable ingestion.

**Why not the others:**

- **RDS/Aurora** — relational scaling and write throughput are a poor fit for this volume/model.
- **Timestream** is valid for pure time-series, but the question's **wide-column + CQL/Cassandra** framing points to Keyspaces.

> [!tip] Exam Tip
> High-volume IoT/time-series **with a Cassandra/wide-column requirement** → Keyspaces; design to avoid hot partitions.

[⬆ Back to top](#table-of-contents)

---

## Q4 - Multi-Region Active-Active

**Scenario:** A global application needs **low-latency reads and writes in multiple Regions** for its Cassandra workload, and must survive a full Region outage.

**Answer:** Enable **Amazon Keyspaces Multi-Region replication** (multi-active). Each Region serves local reads/writes; data replicates asynchronously with last-writer-wins.

**Why not the others:**

- **Single-Region Keyspaces + read replicas** — Keyspaces has no cross-Region read-replica concept; you use Multi-Region replication.
- **DynamoDB global tables** — correct _pattern_, but wrong service for a Cassandra/CQL workload.

> [!tip] Exam Tip
> Keyspaces Multi-Region = active-active global writes; the Cassandra analog of DynamoDB global tables.

[⬆ Back to top](#table-of-contents)

---

## Q5 - Keyspaces vs DynamoDB Decision

**Scenario:** A greenfield NoSQL project must choose between Amazon Keyspaces and DynamoDB.

**Answer:**

- Choose **Keyspaces** if there is an **existing Cassandra/CQL** investment (skills, drivers, queries) or a strict Cassandra-compatibility requirement.
- Choose **DynamoDB** for a **greenfield AWS-native** NoSQL app with no Cassandra dependency (richer ecosystem: DAX, Streams, global tables, TTL, broad integrations).

**Why this matters:** Both are serverless, 3-AZ-durable, use RRU/WRU-style billing, and offer PITR and multi-Region — the deciding factor is the **Cassandra/CQL requirement**.

> [!tip] Exam Tip
> No Cassandra requirement on a new AWS NoSQL app → **DynamoDB**. Explicit Cassandra/CQL → **Keyspaces**.

[⬆ Back to top](#table-of-contents)

---

## Q6 - Spiky Unpredictable Traffic

**Scenario:** A Cassandra-compatible workload has **highly variable, unpredictable** traffic and the team does not want to manage capacity or risk throttling.

**Answer:** Use **Amazon Keyspaces in on-demand capacity mode** — it scales instantly with traffic and you pay per request (RRU/WRU).

**Why not the others:**

- **Provisioned without auto scaling** — risks throttling on spikes and wastes capacity at troughs.

> [!tip] Exam Tip
> Spiky/unpredictable + "no capacity management" → **on-demand**. Steady/predictable + cost focus → **provisioned + auto scaling**.

[⬆ Back to top](#table-of-contents)

---

## Q7 - Private Connectivity and Encryption

**Scenario:** Compliance requires that traffic to the Cassandra-compatible database **never traverse the public internet** and that data is **encrypted at rest with auditable keys**.

**Answer:** Connect via an **interface VPC endpoint (PrivateLink)** and use a **customer-managed KMS key** (encryption at rest is always on; in transit is TLS). Audit with **CloudTrail**.

**Why not the others:**

- "Encrypt the application data manually" — unnecessary; at-rest encryption is automatic.
- Public endpoint with security groups alone — does not meet the "never traverse public internet" requirement.

> [!tip] Exam Tip
> Private path → **VPC interface endpoint**. Key control/audit → **customer-managed KMS key**.

[⬆ Back to top](#table-of-contents)

---

## Q8 - Recover from Accidental Deletes

**Scenario:** A bad deployment deletes rows from a production Keyspaces table. The team needs to restore data to just before the incident.

**Answer:** Restore the table using **point-in-time recovery (PITR)** to a timestamp before the bad deploy (within the **35-day** window). The restore creates a **new table** for cutover.

**Why not the others:**

- 3-AZ replication does not help — it faithfully replicated the deletes.
- Multi-Region replication also propagates the deletes, so it is not a logical-recovery tool.

> [!tip] Exam Tip
> Logical/accidental data loss → **PITR**. Match the failure type to the protection: AZ failure → multi-AZ; Region failure → Multi-Region; bad data → PITR.

[⬆ Back to top](#table-of-contents)
