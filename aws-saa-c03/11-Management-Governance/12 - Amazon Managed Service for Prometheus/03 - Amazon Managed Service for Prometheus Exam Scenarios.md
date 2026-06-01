# Amazon Managed Service for Prometheus - Exam Scenarios

> Exam focus: AMP = managed Prometheus metrics store for containers, paired with Grafana; AMP vs CloudWatch; IAM/SigV4 ingestion. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - Amazon Managed Service for Prometheus Intro bits & bytes](01%20-%20Amazon%20Managed%20Service%20for%20Prometheus%20Intro%20bits%20%26%20bytes.md) · [02 - Amazon Managed Service for Prometheus Deep Dive](02%20-%20Amazon%20Managed%20Service%20for%20Prometheus%20Deep%20Dive.md) · [04 - Amazon Managed Service for Prometheus SRE Operations](04%20-%20Amazon%20Managed%20Service%20for%20Prometheus%20SRE%20Operations.md) · [01 - Amazon Managed Grafana Intro bits & bytes](01%20-%20Amazon%20Managed%20Grafana%20Intro%20bits%20%26%20bytes.md)

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

- AMP = **managed Prometheus** metrics store + PromQL (no servers).
- **remote_write** ingestion; **IAM/SigV4** auth; **IRSA** for EKS pods.
- Pairs with **Managed Grafana** for dashboards.
- AMP (containers/PromQL) vs CloudWatch (AWS-native).
- Cardinality/retention drive cost.
- Alert Manager → SNS.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                          | Points to                |
| :---------------------------------------------- | :----------------------- |
| "Prometheus / PromQL, managed, no servers"      | **AMP**                  |
| "Kubernetes / EKS / container metrics at scale" | **AMP** (+ Grafana)      |
| "highly available, durable Prometheus storage"  | **AMP**                  |
| "remote_write"                                  | **AMP ingestion**        |
| "dashboards for Prometheus metrics"             | **Managed Grafana**      |
| "AWS-native metrics/alarms"                     | **CloudWatch** (not AMP) |
| "scrape EKS without managing a collector"       | **AMP managed scraper**  |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Using AMP for **AWS-native** metrics (CloudWatch is simpler).
- Expecting AMP to **draw dashboards** (use Grafana).
- Self-managing Prometheus when managed is required ("no servers").
- Forgetting **IAM/SigV4** auth (open-source Prometheus is unauthenticated).
- Using AMP for **logs/traces** (metrics only).

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **"Prometheus/PromQL/containers, managed"** → AMP.
2. **"Dashboards"** → Grafana (AMG), not AMP.
3. **"AWS-native metrics"** → CloudWatch.
4. **"Logs/traces"** → CloudWatch Logs/OpenSearch/X-Ray.
5. **"Scrape EKS, least ops"** → AMP managed scraper / ADOT.

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** Store and query EKS Prometheus metrics with PromQL, fully managed.
**Options:** A) CloudWatch B) AMP C) Self-host Prometheus D) Timestream
**Correct:** B
**Explanation:** AMP is managed Prometheus storage + PromQL.

### Q2

**Scenario:** Visualize AMP metrics.
**Options:** A) AMP dashboards B) Managed Grafana C) QuickSight D) Athena
**Correct:** B
**Explanation:** AMP doesn't visualize; pair with Grafana.

### Q3

**Scenario:** How are metrics sent to AMP?
**Options:** A) PutMetricData B) remote_write (SigV4) C) S3 upload D) Kinesis
**Correct:** B
**Explanation:** Prometheus remote_write, IAM-signed.

### Q4

**Scenario:** Authenticate writes to AMP.
**Options:** A) Open HTTP B) IAM / SigV4 C) Basic auth D) None
**Correct:** B
**Explanation:** AMP uses IAM/SigV4 (unlike OSS Prometheus).

### Q5

**Scenario:** Least-effort scraping of an EKS cluster.
**Options:** A) DIY Prometheus B) AMP managed (agentless) scraper C) Lambda D) CloudWatch agent
**Correct:** B
**Explanation:** The managed scraper removes collector ops.

### Q6

**Scenario:** AWS-native metrics + alarms for RDS/EC2.
**Options:** A) AMP B) CloudWatch C) Grafana D) Timestream
**Correct:** B
**Explanation:** AWS-native is CloudWatch.

### Q7

**Scenario:** Give EKS pods least-privilege write to AMP.
**Options:** A) Node role B) IRSA with aps:RemoteWrite C) Access keys D) Root
**Correct:** B
**Explanation:** IRSA scopes pod permissions.

### Q8

**Scenario:** Route Prometheus alerts to email/Slack.
**Options:** A) Not possible B) AMP Alert Manager → SNS → targets C) Config D) Budgets
**Correct:** B
**Explanation:** Managed Alert Manager routes via SNS.

### Q9

**Scenario:** HA, durable Prometheus storage without sharding.
**Options:** A) Single Prometheus B) AMP (multi-AZ managed) C) EBS snapshots D) Thanos DIY
**Correct:** B
**Explanation:** AMP is multi-AZ/durable/managed.

### Q10

**Scenario:** Reduce AMP cost from too many series.
**Options:** A) More storage B) Drop/relabel high-cardinality series at the agent C) Longer retention D) Bigger workspace
**Correct:** B
**Explanation:** Cardinality drives cost.

### Q11

**Scenario:** Keep AMP ingest/query traffic private.
**Options:** A) Public only B) VPC interface endpoint (PrivateLink) C) NAT only D) IGW
**Correct:** B
**Explanation:** PrivateLink keeps traffic private.

### Q12

**Scenario:** OpenTelemetry-based collection to AMP.
**Options:** A) Not supported B) ADOT collector remote_write C) Kinesis D) S3
**Correct:** B
**Explanation:** ADOT scrapes and remote-writes.

### Q13

**Scenario:** Precompute an expensive PromQL query for fast dashboards.
**Options:** A) Bigger workspace B) Recording rules C) More queries D) CloudWatch
**Correct:** B
**Explanation:** Recording rules precompute series.

### Q14

**Scenario:** AMP for logs?
**Options:** A) Yes B) No — metrics only; use CloudWatch Logs/OpenSearch C) Only errors D) Only traces
**Correct:** B
**Explanation:** AMP is metrics only.

### Q15

**Scenario:** Control how long metrics are kept.
**Options:** A) Fixed forever B) Workspace retention setting C) Per metric only D) Not configurable
**Correct:** B
**Explanation:** Retention is configurable.

### Q16

**Scenario:** Encrypt AMP data at rest.
**Options:** A) Not possible B) KMS encryption C) Client only D) None
**Correct:** B
**Explanation:** KMS at rest, TLS in transit.

### Q17

**Scenario:** HA ingestion from a cluster.
**Options:** A) Single agent B) Redundant collectors writing to the workspace C) One Lambda D) Manual
**Correct:** B
**Explanation:** Redundant collectors give HA ingestion.

### Q18

**Scenario:** Migrate many self-hosted Prometheus servers to managed.
**Options:** A) Keep self-hosting B) remote_write existing Prometheus to AMP / move to managed scraper C) CloudWatch only D) Drop metrics
**Correct:** B
**Explanation:** remote_write to AMP consolidates onto managed.

### Q19

**Scenario:** Raise AMP ingestion limits.
**Options:** A) New account B) Service Quotas increase C) Not possible D) Bigger EKS
**Correct:** B
**Explanation:** Quotas are adjustable.

### Q20

**Scenario:** End-to-end managed container observability with PromQL + dashboards + alerts.
**Options:** A) CloudWatch only B) AMP + AMG + Alert Manager (ADOT/scraper) C) Self-host all D) QuickSight
**Correct:** B
**Explanation:** AMP+AMG+Alert Manager is the managed stack.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** A company runs 12 EKS clusters across accounts with self-hosted Prometheus that keeps falling over and lacks long-term storage. They want managed, HA, PromQL-compatible metrics with minimal collector ops.
**Options:** A) Bigger Prometheus nodes B) **AMP** workspace(s) with the **managed scraper** (or ADOT) remote-writing; **AMG** for dashboards; IRSA for auth C) CloudWatch only D) Thanos
**Correct:** B
**Explanation:** AMP removes HA/storage/scaling toil; managed scraper/ADOT cuts collector ops; AMG visualizes; IRSA secures.

### H2

**Scenario:** AMP costs spiked after adding a label with the request ID to every metric.
**Options:** A) Add storage B) **High cardinality** — drop/relabel the request-ID label at the agent; keep only bounded labels C) Longer retention D) New workspace
**Correct:** B
**Explanation:** Unbounded labels explode active series; relabel/drop them at collection.

### H3

**Scenario:** Security mandates that only specific pods can write metrics and only the SRE role can query, with no public network path.
**Options:** A) Open HTTP B) **IRSA** scoped to `aps:RemoteWrite` for collector pods, separate `aps:QueryMetrics` role for SRE, **PrivateLink** endpoint C) Shared keys D) Root
**Correct:** B
**Explanation:** Separate least-privilege IAM for write vs query + IRSA + PrivateLink meets the mandate.

### H4

**Scenario:** Dashboards are slow due to heavy aggregation PromQL run repeatedly.
**Options:** A) Bigger Grafana B) Define **recording rules** in AMP to precompute, then chart the precomputed series C) More queries D) CloudWatch
**Correct:** B
**Explanation:** Recording rules precompute expensive expressions for fast dashboards.

### H5

**Scenario:** A regulated workload needs Prometheus alerting routed to PagerDuty with dedup/silencing, managed.
**Options:** A) Self-host Alertmanager B) AMP **managed Alert Manager** → SNS → PagerDuty, with notification policies C) CloudWatch alarms only D) Manual
**Correct:** B
**Explanation:** AMP's managed Alert Manager provides routing/dedup/silencing to SNS→PagerDuty.

### H6

**Scenario:** They want one observability pane across AMP (containers), CloudWatch (AWS resources), and X-Ray (traces).
**Options:** A) Three tools B) **Managed Grafana** with AMP + CloudWatch + X-Ray data sources C) CloudWatch only D) QuickSight
**Correct:** B
**Explanation:** AMG correlates AMP, CloudWatch, and X-Ray in unified dashboards.

### H7

**Scenario:** HA ingestion requirement: no metric loss if one collector dies.
**Options:** A) Single collector B) Run **redundant collectors** writing to the same AMP workspace (HA pairs), AMP handles dedup C) Manual restart D) Bigger node
**Correct:** B
**Explanation:** Redundant collectors provide ingestion HA into the durable workspace.

### H8

**Scenario:** Cost governance wants AMP retention reduced for ephemeral dev metrics but kept long for prod SLOs.
**Options:** A) One retention for all B) Separate **workspaces** per environment with different **retention** settings C) Drop all dev metrics D) Infinite retention
**Correct:** B
**Explanation:** Per-workspace retention lets dev be short and prod long.

### H9

**Scenario:** Migrating gradually: existing self-hosted Prometheus must coexist while moving to AMP.
**Options:** A) Big-bang cutover B) Configure existing Prometheus **remote_write** to AMP (dual-write), validate, then retire local storage C) Stop Prometheus D) CloudWatch
**Correct:** B
**Explanation:** remote_write enables a non-disruptive, validated migration.

### H10

**Scenario:** Leadership asks whether to use AMP or CloudWatch for a new mostly-AWS-managed (Lambda/RDS/ALB) app with little Kubernetes.
**Options:** A) AMP always B) **CloudWatch** (AWS-native metrics/alarms, simpler/cheaper) for this profile; reserve AMP for Prometheus/container-heavy workloads C) Self-host D) QuickSight
**Correct:** B
**Explanation:** AMP shines for Prometheus/container ecosystems; AWS-native managed services map better to CloudWatch.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Managed Prometheus metrics store + PromQL for containers → AMP (remote_write, IAM/SigV4, multi-AZ). Dashboards → Managed Grafana. Alerts → Alert Manager → SNS. AWS-native metrics → CloudWatch. Cardinality & retention drive cost.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - Amazon Managed Service for Prometheus SRE Operations](04%20-%20Amazon%20Managed%20Service%20for%20Prometheus%20SRE%20Operations.md).
