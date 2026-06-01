# Amazon Managed Grafana - Exam Scenarios

> Exam focus: multi-source dashboards, SSO/SAML auth, AMG+AMP pairing, and AMG vs CloudWatch dashboards/QuickSight. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - Amazon Managed Grafana Intro bits & bytes](01%20-%20Amazon%20Managed%20Grafana%20Intro%20bits%20%26%20bytes.md) · [02 - Amazon Managed Grafana Deep Dive](02%20-%20Amazon%20Managed%20Grafana%20Deep%20Dive.md) · [04 - Amazon Managed Grafana SRE Operations](04%20-%20Amazon%20Managed%20Grafana%20SRE%20Operations.md) · [01 - Amazon Managed Service for Prometheus Intro bits & bytes](01%20-%20Amazon%20Managed%20Service%20for%20Prometheus%20Intro%20bits%20%26%20bytes.md)

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

- **Managed Grafana = managed visualization** across many sources (doesn't store data).
- Auth via **Identity Center / SAML** (not IAM users).
- Pairs with **AMP** for Prometheus/container metrics.
- AMG vs CloudWatch dashboards vs QuickSight (BI).
- Per-active-user pricing.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                                           | Points to                  |
| :--------------------------------------------------------------- | :------------------------- |
| "managed Grafana", "Grafana dashboards without managing servers" | **Amazon Managed Grafana** |
| "dashboards across CloudWatch and Prometheus and others"         | **AMG (multi-source)**     |
| "container/Kubernetes metrics with Grafana"                      | **AMP + AMG**              |
| "users sign in with SSO/SAML"                                    | **AMG auth**               |
| "open-source compatible dashboards/alerting"                     | **AMG**                    |
| "business intelligence / analytics dashboards"                   | **QuickSight** (not AMG)   |
| "simple AWS-native dashboard"                                    | **CloudWatch dashboards**  |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Choosing AMG as a **metrics store** (it visualizes only).
- Choosing **QuickSight** for ops metrics (that's BI).
- Expecting **IAM-user** login (it's Identity Center/SAML).
- Using AMG when **CloudWatch dashboards** suffice for AWS-only.
- Forgetting **AMP** as the Prometheus backend.

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **"Grafana, managed, multi-source"** → AMG.
2. **"Prometheus/container metrics"** → AMP (store) + AMG (view).
3. **"SSO/SAML sign-in for dashboards"** → AMG.
4. **"BI/analytics"** → QuickSight.
5. **"AWS-native simple dashboard"** → CloudWatch dashboards.

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** Build Grafana dashboards combining CloudWatch and Prometheus without running Grafana servers.
**Options:** A) Self-host Grafana B) Amazon Managed Grafana C) QuickSight D) CloudWatch dashboards
**Correct:** B
**Explanation:** AMG is managed multi-source Grafana.

### Q2

**Scenario:** How do users authenticate to AMG?
**Options:** A) IAM users B) IAM Identity Center / SAML C) Root D) Access keys
**Correct:** B
**Explanation:** SSO/SAML, not IAM users.

### Q3

**Scenario:** Visualize EKS Prometheus metrics with managed Grafana.
**Options:** A) CloudWatch only B) AMP + AMG C) QuickSight D) Athena
**Correct:** B
**Explanation:** AMP stores/scrapes, AMG visualizes.

### Q4

**Scenario:** Does AMG store metrics?
**Options:** A) Yes B) No — queries data sources C) Only logs D) Only traces
**Correct:** B
**Explanation:** AMG is visualization, not storage.

### Q5

**Scenario:** BI dashboards for sales analytics.
**Options:** A) AMG B) QuickSight C) CloudWatch D) AMP
**Correct:** B
**Explanation:** BI/analytics is QuickSight.

### Q6

**Scenario:** Simple AWS-native dashboard for a few CloudWatch metrics.
**Options:** A) AMG B) CloudWatch dashboards C) QuickSight D) AMP
**Correct:** B
**Explanation:** CloudWatch dashboards suffice and are cheaper.

### Q7

**Scenario:** Alert from Grafana to PagerDuty/Slack on a PromQL condition.
**Options:** A) Not possible B) Grafana alerting → contact points C) Config D) Budgets
**Correct:** B
**Explanation:** AMG supports Grafana alerting to contact points.

### Q8

**Scenario:** Pricing model of AMG.
**Options:** A) Per dashboard B) Per active user/workspace/month C) Per query D) Per metric
**Correct:** B
**Explanation:** Per active user.

### Q9

**Scenario:** Query a private self-managed Prometheus in a VPC from AMG.
**Options:** A) Public only B) VPC connection from the workspace C) NAT only D) Not possible
**Correct:** B
**Explanation:** Workspace VPC connectivity reaches private sources.

### Q10

**Scenario:** One dashboard across multiple accounts' CloudWatch.
**Options:** A) Per-account Grafana B) AMG + CloudWatch cross-account observability C) QuickSight D) Manual
**Correct:** B
**Explanation:** Cross-account data access enables org-wide dashboards.

### Q11

**Scenario:** Map IdP groups to dashboard edit vs view rights.
**Options:** A) IAM only B) Grafana roles (Admin/Editor/Viewer) from SAML/Identity Center C) Bucket policy D) SCP
**Correct:** B
**Explanation:** Grafana roles map from the IdP.

### Q12

**Scenario:** Correlate traces and metrics in one view.
**Options:** A) Separate tools B) AMG with X-Ray + CloudWatch/AMP sources C) QuickSight D) Config
**Correct:** B
**Explanation:** AMG can combine traces and metrics sources.

### Q13

**Scenario:** Manage dashboards as code.
**Options:** A) Click only B) Grafana HTTP API C) CloudFormation only D) Not possible
**Correct:** B
**Explanation:** The Grafana API enables GitOps dashboards.

### Q14

**Scenario:** Reduce AMG cost.
**Options:** A) Fewer dashboards B) Right-size active users / consolidate workspaces C) More queries D) Bigger workspace
**Correct:** B
**Explanation:** Cost is per active user.

### Q15

**Scenario:** Need HA Grafana without ops burden.
**Options:** A) EC2 Grafana B) AMG (managed HA) C) Lambda D) ECS DIY
**Correct:** B
**Explanation:** AMG is managed and HA.

### Q16

**Scenario:** Visualize OpenSearch log analytics alongside metrics.
**Options:** A) Not possible B) Add OpenSearch as an AMG data source C) QuickSight D) Athena only
**Correct:** B
**Explanation:** OpenSearch is a supported source.

### Q17

**Scenario:** Which stores the metrics AMG charts for containers?
**Options:** A) AMG B) AMP C) QuickSight D) S3
**Correct:** B
**Explanation:** AMP is the Prometheus-compatible store.

### Q18

**Scenario:** Provide read-only dashboards to many stakeholders cheaply.
**Options:** A) Admin for all B) Viewer-tier users C) Self-host D) QuickSight
**Correct:** B
**Explanation:** Viewer tier is the lower-cost user type.

### Q19

**Scenario:** Upgrade Grafana version safely.
**Options:** A) Reinstall B) Workspace managed version upgrade C) New account D) Not possible
**Correct:** B
**Explanation:** AMG provides a managed upgrade path.

### Q20

**Scenario:** Authenticate workforce already in Identity Center.
**Options:** A) New IAM users B) Connect AMG to Identity Center C) SAML only D) Root
**Correct:** B
**Explanation:** Identity Center integrates directly.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** A platform team runs EKS across 3 accounts and wants unified Grafana dashboards (container metrics + ALB metrics + traces) with SSO and no Grafana server management.
**Options:** A) Self-host Grafana per account B) **AMP** (collect Prometheus metrics) + **AMG** (multi-source: AMP + CloudWatch + X-Ray) with **Identity Center** auth and cross-account data access C) CloudWatch dashboards only D) QuickSight
**Correct:** B
**Explanation:** AMP stores container metrics; AMG visualizes across sources/accounts with SSO — fully managed.

### H2

**Scenario:** Security requires that dashboard users authenticate via the corporate IdP and that edit rights are limited to SREs.
**Options:** A) IAM users B) **SAML/Identity Center** federation mapping the SRE group to **Editor/Admin**, everyone else **Viewer** C) Shared login D) Root
**Correct:** B
**Explanation:** Federated auth + role mapping enforces least privilege on dashboards.

### H3

**Scenario:** A workspace must read a private self-managed Prometheus and a private OpenSearch in a VPC.
**Options:** A) Make them public B) Attach a **VPC connection** to the workspace so it reaches private sources C) NAT gateway only D) Copy data to S3
**Correct:** B
**Explanation:** Workspace VPC connectivity reaches private data sources securely.

### H4

**Scenario:** Leadership wants one pane combining metrics from 30 accounts' CloudWatch without copying data.
**Options:** A) 30 workspaces B) One AMG workspace + **CloudWatch cross-account observability** + cross-account data access C) Export to one account D) QuickSight
**Correct:** B
**Explanation:** Cross-account observability + AMG queries source accounts without duplication.

### H5

**Scenario:** The team wants alerting on a multi-source condition (PromQL container metric AND a CloudWatch metric) that CloudWatch alarms can't express alone.
**Options:** A) Two separate alarms B) **Grafana alerting** in AMG combining the sources, routed to contact points C) Config D) Budgets
**Correct:** B
**Explanation:** Grafana alerting can evaluate multi-source/PromQL conditions and route notifications.

### H6

**Scenario:** Dashboards must be version-controlled and reproducible across environments.
**Options:** A) Manual export B) Provision dashboards via the **Grafana HTTP API** from git (GitOps) C) Screenshots D) Per-user copies
**Correct:** B
**Explanation:** API-driven provisioning makes dashboards code.

### H7

**Scenario:** Cost is climbing because hundreds of stakeholders have Editor access they don't need.
**Options:** A) Remove dashboards B) Downgrade most to **Viewer** tier (lower cost), keep Editors minimal C) New workspace D) Self-host
**Correct:** B
**Explanation:** Per-active-user pricing means right-tiering users (Viewer vs Editor) controls cost.

### H8

**Scenario:** A regulated org needs audit of who changed dashboards and data-source access scoped tightly.
**Options:** A) Trust users B) Federated identities (auditable), **customer-managed** data-source role with least privilege, CloudTrail for workspace API actions C) Admin for all D) Public dashboards
**Correct:** B
**Explanation:** Federation + least-privilege role + CloudTrail gives auditability and scoping.

### H9

**Scenario:** Migrating from self-hosted Grafana; they want to keep dashboards and reduce ops.
**Options:** A) Rebuild from scratch B) Import existing dashboards (JSON) into **AMG**, connect the same data sources, retire the servers C) Stay self-hosted D) Use CloudWatch dashboards
**Correct:** B
**Explanation:** AMG is Grafana-compatible; import dashboards and offload ops.

### H10

**Scenario:** A team needs both AWS-native quick dashboards for on-call and rich multi-source dashboards for deep analysis, cost-consciously.
**Options:** A) AMG for everything B) **CloudWatch dashboards** for simple on-call views + **AMG** where multi-source/Grafana features are needed C) Self-host D) QuickSight
**Correct:** B
**Explanation:** Use the cheaper CloudWatch dashboards for simple needs and AMG where its multi-source power justifies the per-user cost.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Managed, multi-source Grafana dashboards → Amazon Managed Grafana (visualizes, doesn't store). Auth = Identity Center/SAML. Container/Prometheus metrics → AMP + AMG. BI → QuickSight. Simple AWS-native → CloudWatch dashboards. Priced per active user.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - Amazon Managed Grafana SRE Operations](04%20-%20Amazon%20Managed%20Grafana%20SRE%20Operations.md).
