# DocumentDB Scenario Questions - SAA-C03 Deep Dive

> Exam-style scenarios covering MongoDB migration, document store vs DynamoDB, read scaling, multi-AZ HA, massive sharded scale with Elastic Clusters, and the DocumentDB-vs-DynamoDB decision — each with the answer and the reasoning.

See also: [01 - DocumentDB Intro & Core Concepts](01%20-%20DocumentDB%20Intro%20%26%20Core%20Concepts.md) · [02 - DocumentDB Architecture Deep Dive](02%20-%20DocumentDB%20Architecture%20Deep%20Dive.md) · [03 - DocumentDB Best Practices & Examples](03%20-%20DocumentDB%20Best%20Practices%20%26%20Examples.md) · [05 - DocumentDB Troubleshooting (SRE)](05%20-%20DocumentDB%20Troubleshooting%20%28SRE%29.md) · [06 - DocumentDB Important Facts & Cheat Sheet](06%20-%20DocumentDB%20Important%20Facts%20%26%20Cheat%20Sheet.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md) · [01 - Aurora Intro & Core Concepts](01%20-%20Aurora%20Intro%20%26%20Core%20Concepts.md) · [01 - DynamoDB Intro & Core Concepts](01%20-%20DynamoDB%20Intro%20%26%20Core%20Concepts.md)

---

## Table of Contents

- [Q1 - Migrate Self-Managed MongoDB](#q1---migrate-self-managed-mongodb)
- [Q2 - JSON Document Store With MongoDB API](#q2---json-document-store-with-mongodb-api)
- [Q3 - Read Scaling for a Document Workload](#q3---read-scaling-for-a-document-workload)
- [Q4 - High Availability Across AZs](#q4---high-availability-across-azs)
- [Q5 - Massive Sharded Scale](#q5---massive-sharded-scale)
- [Q6 - DocumentDB vs DynamoDB Decision](#q6---documentdb-vs-dynamodb-decision)
- [Q7 - Minimal-Downtime Migration](#q7---minimal-downtime-migration)
- [Q8 - Encrypt an Existing Cluster](#q8---encrypt-an-existing-cluster)
- [Exam Tips & Traps](#exam-tips--traps)

---

## Q1 - Migrate Self-Managed MongoDB

**Scenario:** A team runs MongoDB on EC2 instances and spends significant effort on patching, backups, and replica-set failover. They want a **fully managed** service but must **keep their existing MongoDB drivers and queries** unchanged.

**Answer:** **Amazon DocumentDB (with MongoDB compatibility).**

**Why:** DocumentDB is MongoDB API/wire-compatible, so the same drivers/queries work after changing the connection string, while AWS manages provisioning, patching, backups, replication, and failover.

**Distractors:** DynamoDB (different API, would require rewriting the app); RDS/Aurora (relational, not document); self-hosting on bigger EC2 (still self-managed).

[⬆ Back to top](#table-of-contents)

---

## Q2 - JSON Document Store With MongoDB API

**Scenario:** A new content-management app stores articles as **flexible JSON documents** and the developers want to use the **MongoDB query language and aggregation pipeline**.

**Answer:** **Amazon DocumentDB.**

**Why:** It is purpose-built for JSON-like documents and supports the MongoDB query/aggregation API. DynamoDB stores items but uses its **own** API, not MongoDB's query language.

**Distractors:** DynamoDB (no MongoDB query language/aggregation pipeline); Aurora (relational); S3 (object store, not a queryable document DB).

[⬆ Back to top](#table-of-contents)

---

## Q3 - Read Scaling for a Document Workload

**Scenario:** A DocumentDB-backed product catalog is **read-heavy**; the single primary is CPU-bound on reads. The team wants to scale reads **without changing the data model** and balance read traffic automatically.

**Answer:** **Add replica instances (up to 15) and point read traffic at the reader endpoint.**

**Why:** Replicas share the same storage volume (no data copy), serve reads, and the reader endpoint load-balances across them. Use a `secondaryPreferred` read preference in the driver.

**Trap:** Reads from replicas are **eventually consistent**; if read-after-write consistency is required, read from the **primary**.

[⬆ Back to top](#table-of-contents)

---

## Q4 - High Availability Across AZs

**Scenario:** A production DocumentDB cluster currently has only a **single instance**. The team needs to survive an **Availability Zone failure** with automatic recovery in seconds.

**Answer:** **Add one or more replica instances in different AZs.**

**Why:** With a replica in another AZ, DocumentDB automatically **promotes the replica to primary** on failure (typically ~30s), and the **cluster endpoint** repoints automatically. The underlying storage is already 6-copy/3-AZ, but you still need a replica instance for fast compute failover.

**Trap:** Storage durability alone (6 copies/3 AZs) does not give fast failover — a single-instance cluster must rebuild a new primary, which is slower.

[⬆ Back to top](#table-of-contents)

---

## Q5 - Massive Sharded Scale

**Scenario:** A workload must support **millions of reads/writes per second** and grow to **petabytes** of document data — beyond what a single primary and 64 TiB volume can handle.

**Answer:** **Amazon DocumentDB Elastic Clusters.**

**Why:** Elastic Clusters shard data across multiple shards using a shard key, scaling horizontally to millions of ops/sec and petabyte storage, with managed sharding and elastic scale-out/in.

**Distractors:** Adding more replicas (scales reads only, not writes/storage); a bigger instance (vertical limit); standard cluster (capped at 64 TiB / single writer).

[⬆ Back to top](#table-of-contents)

---

## Q6 - DocumentDB vs DynamoDB Decision

**Scenario:** A greenfield team wants a **serverless** datastore with **single-digit-millisecond** latency at virtually unlimited scale, **no instance management**, and they have **no MongoDB requirement**.

**Answer:** **Amazon DynamoDB.**

**Why:** DynamoDB is serverless (no instances), auto-scales, and delivers low-latency key-value/document access. DocumentDB is instance-based and only preferred when **MongoDB compatibility** is required.

**Rule:** "Keep MongoDB / migrate MongoDB" → **DocumentDB**; "serverless, no MongoDB need, key-value at scale" → **DynamoDB** ([01 - DynamoDB Intro & Core Concepts](01%20-%20DynamoDB%20Intro%20%26%20Core%20Concepts.md)).

[⬆ Back to top](#table-of-contents)

---

## Q7 - Minimal-Downtime Migration

**Scenario:** A business must migrate a large, **always-on** MongoDB database to DocumentDB with **minimal downtime** and continuous replication during cutover.

**Answer:** **AWS Database Migration Service (DMS)** with MongoDB as source and DocumentDB as target, using change data capture (CDC).

**Why:** DMS performs an initial full load plus ongoing CDC, keeping source and target in sync until a brief cutover. `mongodump`/`mongorestore` is offline/bulk and better for one-time, downtime-tolerant migrations.

[⬆ Back to top](#table-of-contents)

---

## Q8 - Encrypt an Existing Cluster

**Scenario:** A compliance audit requires **encryption at rest** on a DocumentDB cluster that was created **without** encryption.

**Answer:** **Take a snapshot, copy the snapshot with encryption enabled (KMS key), and restore it to a new encrypted cluster;** then cut over.

**Why:** Encryption at rest can only be enabled **at creation**; it cannot be toggled on an existing cluster in place. The snapshot-copy-restore flow is the supported path.

**Trap:** "Just enable encryption on the running cluster" is not possible.

[⬆ Back to top](#table-of-contents)

---

## Exam Tips & Traps

- Keywords **"MongoDB-compatible / keep MongoDB drivers / migrate MongoDB"** → **DocumentDB**.
- **MongoDB query language / aggregation on JSON** → DocumentDB, **not** DynamoDB.
- Scale **reads** → replicas + reader endpoint; scale **writes/petabytes** → **Elastic Clusters**.
- **HA across AZs** → add replicas in other AZs (storage durability alone is not fast failover).
- **Minimal-downtime migration** → **AWS DMS**; offline bulk → mongodump/mongorestore.
- **Encrypt existing cluster** → snapshot → copy encrypted → restore.

[⬆ Back to top](#table-of-contents)
