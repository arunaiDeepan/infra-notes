# Amazon Managed Service for Prometheus - Deep Dive

> Architecture, ingestion (remote_write, ADOT, managed scraper), rules & Alert Manager, security (IAM/SigV4, VPC endpoints), cardinality & retention, limits, integrations, comparisons, best practices.

See also: [01 - Amazon Managed Service for Prometheus Intro bits & bytes](01%20-%20Amazon%20Managed%20Service%20for%20Prometheus%20Intro%20bits%20%26%20bytes.md) · [03 - Amazon Managed Service for Prometheus Exam Scenarios](03%20-%20Amazon%20Managed%20Service%20for%20Prometheus%20Exam%20Scenarios.md) · [04 - Amazon Managed Service for Prometheus SRE Operations](04%20-%20Amazon%20Managed%20Service%20for%20Prometheus%20SRE%20Operations.md) · [01 - Amazon Managed Grafana Intro bits & bytes](01%20-%20Amazon%20Managed%20Grafana%20Intro%20bits%20%26%20bytes.md)

---

## Table of Contents

- [1. Architecture](#1-architecture)
- [2. Ingestion Paths](#2-ingestion-paths)
- [3. Rules and Alert Manager](#3-rules-and-alert-manager)
- [4. Security: IAM, SigV4, VPC Endpoints](#4-security-iam-sigv4-vpc-endpoints)
- [5. Cardinality, Retention, and Limits](#5-cardinality-retention-and-limits)
- [6. High Availability and Durability](#6-high-availability-and-durability)
- [7. Integration Matrix](#7-integration-matrix)
- [8. Comparisons](#8-comparisons)
- [9. Best Practices by Pillar](#9-best-practices-by-pillar)

---

```mermaid
flowchart TB
    subgraph Cluster["EKS / ECS / EC2"]
        Agent["Prometheus agent / ADOT collector"]
    end
    Agent -->|remote_write (SigV4)| WS["AMP Workspace: ingest + TSDB"]
    Scraper["AMP managed scraper (agentless, EKS)"] --> WS
    WS --> Q["PromQL query API (SigV4)"]
    Q --> AMG["Managed Grafana"]
    WS --> Rules["Recording + alerting rules"]
    Rules --> AM["Alert Manager -> SNS"]
    VPCe["VPC interface endpoint (PrivateLink)"] --- WS
```

---

## 1. Architecture

An AMP **workspace** provides an ingestion endpoint (`remote_write`) and a PromQL query endpoint, backed by a managed, multi-AZ, horizontally-scaled time-series database. AWS handles sharding, replication, scaling, and durability. There are no Prometheus servers for you to size or patch; you only run the **scrape/collection** layer (or use the managed scraper).

[⬆ Back to top](#table-of-contents)

---

## 2. Ingestion Paths

| Path                                | Description                                                                                 |
| :---------------------------------- | :------------------------------------------------------------------------------------------ |
| **Prometheus agent mode**           | Run Prometheus in agent mode to scrape targets and `remote_write` to AMP                    |
| **ADOT collector**                  | AWS Distro for OpenTelemetry collector scrapes + remote-writes (recommended for OTel shops) |
| **AMP managed (agentless) scraper** | AWS fully manages discovery + scraping of your **EKS** cluster — least operational effort   |

All ingestion is **SigV4-signed** (IAM), so only authorized principals can write.

[⬆ Back to top](#table-of-contents)

---

## 3. Rules and Alert Manager

- **Recording rules**: precompute expensive PromQL into new series for fast dashboards.
- **Alerting rules**: evaluate PromQL conditions; fire alerts.
- **Managed Alert Manager**: routes/deduplicates/silences alerts and sends to **SNS** (then email/Lambda/PagerDuty, etc.).
- Rules are uploaded as Prometheus-format rule files to the workspace.

[⬆ Back to top](#table-of-contents)

---

## 4. Security: IAM, SigV4, VPC Endpoints

- **Authentication/authorization** is via **IAM** — requests are **SigV4-signed** (unlike open-source Prometheus's unauthenticated HTTP). Scope write vs query permissions per principal.
- **VPC interface endpoints (PrivateLink)** keep ingestion/query traffic private.
- **KMS** encryption at rest; encryption in transit by default.
- For EKS, use **IRSA** (IAM Roles for Service Accounts) so the collector pod gets scoped `aps:RemoteWrite` permissions.

[⬆ Back to top](#table-of-contents)

---

## 5. Cardinality, Retention, and Limits

- **Cardinality** (unique label combinations) is the dominant scaling/cost factor — high-cardinality labels (user IDs, request IDs) explode series counts. **Relabel/drop** them at the agent.
- **Retention** is configurable at the workspace (e.g. default ~150 days); longer retention = more storage cost.
- **Ingestion/query quotas** (samples/sec, active series) are soft limits adjustable via Service Quotas.

[⬆ Back to top](#table-of-contents)

---

## 6. High Availability and Durability

- The workspace is **multi-AZ** and durable by design — no single-node Prometheus risk.
- For **HA collection**, run redundant agents/collectors writing to the same workspace (AMP deduplicates with appropriate config).
- Scales automatically with ingest volume; no manual sharding/federation.

[⬆ Back to top](#table-of-contents)

---

## 7. Integration Matrix

| Service                  | Integration                                                                                                    |
| :----------------------- | :------------------------------------------------------------------------------------------------------------- |
| **Managed Grafana**      | Primary PromQL visualization → [01 - Amazon Managed Grafana Intro bits & bytes](01%20-%20Amazon%20Managed%20Grafana%20Intro%20bits%20%26%20bytes.md)                              |
| **EKS / ECS**            | Source of container metrics; managed scraper for EKS                                                           |
| **ADOT / OpenTelemetry** | Collector for scrape + remote_write                                                                            |
| **IAM**                  | SigV4 auth; IRSA for pods                                                                                      |
| **SNS**                  | Alert Manager destination                                                                                      |
| **CloudWatch**           | Complementary AWS-native metrics; can also export some metrics → [01 - Amazon CloudWatch Intro bits & bytes](01%20-%20Amazon%20CloudWatch%20Intro%20bits%20%26%20bytes.md) |
| **PrivateLink / KMS**    | Private connectivity + encryption                                                                              |
| **Organizations**        | Cross-account observability patterns                                                                           |

[⬆ Back to top](#table-of-contents)

---

## 8. Comparisons

### AMP vs CloudWatch (metrics)

|           | AMP                           | CloudWatch                      |
| :-------- | :---------------------------- | :------------------------------ |
| Query     | PromQL                        | CloudWatch metric math/Insights |
| Ecosystem | Prometheus/Grafana/K8s        | AWS-native                      |
| Ingest    | remote_write (pull-origin)    | Push/service metrics            |
| Best for  | Containers, OSS observability | AWS resources broadly           |

### AMP vs self-managed Prometheus

|                     | AMP       | Self-managed       |
| :------------------ | :-------- | :----------------- |
| HA/scale/durability | Managed   | You shard/federate |
| Auth                | IAM/SigV4 | DIY                |
| Long-term storage   | Built-in  | Thanos/Cortex DIY  |

[⬆ Back to top](#table-of-contents)

---

## 9. Best Practices by Pillar

**Operational Excellence** — use the **managed scraper** or **ADOT** to cut collection toil; manage rules as code.

**Security** — IAM/SigV4 with **IRSA** for least-privilege pod access; **PrivateLink**; KMS; separate write vs query roles.

**Reliability** — multi-AZ workspace; redundant collectors for HA ingestion; alerting via Alert Manager → SNS.

**Performance Efficiency** — recording rules for heavy queries; control cardinality.

**Cost Optimization** — drop high-cardinality/unneeded series at the agent; tune retention; consolidate workspaces.

[⬆ Back to top](#table-of-contents)

---

> Continue to [03 - Amazon Managed Service for Prometheus Exam Scenarios](03%20-%20Amazon%20Managed%20Service%20for%20Prometheus%20Exam%20Scenarios.md).
