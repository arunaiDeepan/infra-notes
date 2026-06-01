# Amazon OpenSearch Scenario Questions - SAA-C03 Deep Dive

> Eight exam-style scenarios with reasoning: centralized log analytics, full-text product search, cost-tiering old logs, secure dashboard access, VPC isolation, OpenSearch vs Redshift vs Athena, and managed vs self-managed Elasticsearch.

See also: [01 - OpenSearch Intro & Core Concepts](01%20-%20OpenSearch%20Intro%20%26%20Core%20Concepts.md) · [02 - OpenSearch Architecture Deep Dive](02%20-%20OpenSearch%20Architecture%20Deep%20Dive.md) · [03 - OpenSearch Best Practices & Examples](03%20-%20OpenSearch%20Best%20Practices%20%26%20Examples.md) · [05 - OpenSearch Troubleshooting (SRE)](05%20-%20OpenSearch%20Troubleshooting%20%28SRE%29.md) · [06 - OpenSearch Important Facts & Cheat Sheet](06%20-%20OpenSearch%20Important%20Facts%20%26%20Cheat%20Sheet.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md)

---

## Table of Contents

- [Scenario 1: Centralized Log Analytics and Observability](#scenario-1-centralized-log-analytics-and-observability)
- [Scenario 2: Full-Text Product Search](#scenario-2-full-text-product-search)
- [Scenario 3: Cost-Tier Old Logs](#scenario-3-cost-tier-old-logs)
- [Scenario 4: Secure Dashboard Access](#scenario-4-secure-dashboard-access)
- [Scenario 5: VPC Isolation](#scenario-5-vpc-isolation)
- [Scenario 6: OpenSearch vs Redshift](#scenario-6-opensearch-vs-redshift)
- [Scenario 7: OpenSearch vs Athena](#scenario-7-opensearch-vs-athena)
- [Scenario 8: Managed vs Self-Managed Elasticsearch](#scenario-8-managed-vs-self-managed-elasticsearch)
- [Summary: Key Takeaways](#summary-key-takeaways)

---

## Scenario 1: Centralized Log Analytics and Observability

**Scenario:** A company runs dozens of microservices on EC2/Lambda and wants a single place to **search, visualize, and alert** on application logs in near real time.

**Answer:** Stream logs via **Kinesis Data Firehose** (or CloudWatch Logs subscription) into an **Amazon OpenSearch** domain and visualize/alert with **OpenSearch Dashboards**.

**Why:** OpenSearch is purpose-built for **log analytics + observability** with fast aggregations and dashboards. Firehose is serverless ingestion with S3 backup.

> **Trap:** CloudWatch Logs Insights can query CW logs but lacks the rich dashboards, full-text relevance, and cross-source analytics of OpenSearch at scale.

[⬆ Back to top](#table-of-contents)

---

## Scenario 2: Full-Text Product Search

**Scenario:** An e-commerce site needs **typo-tolerant, relevance-ranked** product search with facets/filters returning in milliseconds.

**Answer:** **Amazon OpenSearch Service** with an index per catalog, replicas for read throughput, and FGAC for app access.

**Why:** Full-text search with **relevance scoring, fuzzy matching, and aggregations (facets)** is OpenSearch's core strength. DynamoDB/RDS cannot do relevance-ranked full-text search well.

> **Exam Tip:** **"Full-text / relevance / fuzzy / faceted search"** is the strongest OpenSearch signal on the exam.

[⬆ Back to top](#table-of-contents)

---

## Scenario 3: Cost-Tier Old Logs

**Scenario:** A team must retain **18 months of logs** but only the last 7 days are queried often; older data is queried rarely. They want to minimize cost while keeping data searchable.

**Answer:** Keep recent indices in **hot**, automatically migrate older indices to **UltraWarm**, then to **cold storage**, and delete past 18 months — driven by an **Index State Management (ISM)** policy.

**Why:** **UltraWarm** and **cold** are **S3-backed** tiers far cheaper than hot data-node storage; UltraWarm stays searchable, cold is archival (reattach to query).

> **Exam Tip:** "Cheaply retain searchable old logs" → **UltraWarm**; "rarely accessed archive, lowest cost" → **cold**.

[⬆ Back to top](#table-of-contents)

---

## Scenario 4: Secure Dashboard Access

**Scenario:** Analysts must log into **OpenSearch Dashboards** using the company's existing **corporate identity provider** with SSO.

**Answer:** Configure **SAML** authentication for OpenSearch Dashboards (federate with the enterprise IdP). For AWS-native user pools instead, use **Amazon Cognito**.

**Why:** Dashboard sign-in supports exactly two managed options: **SAML** (enterprise SSO/IdP) and **Amazon Cognito** (user pools + identity pools).

> **Trap:** Plain IAM SigV4 secures the _API_, but the question about _dashboard login_ points to **SAML or Cognito**.

[⬆ Back to top](#table-of-contents)

---

## Scenario 5: VPC Isolation

**Scenario:** Compliance requires the OpenSearch endpoint to be **unreachable from the internet** and accessible only from private application subnets.

**Answer:** Create the domain with **VPC access**, place ENIs in private subnets (one per AZ), and restrict access with **security groups** + IAM/FGAC.

**Why:** **VPC access** gives a private endpoint controlled by security groups; **public access** is internet-reachable. Access mode is set at creation and **cannot be switched** later.

> **Trap:** If the domain was created with public access, you must **recreate it** (or restore a snapshot into a new VPC domain) — you can't flip the switch.

[⬆ Back to top](#table-of-contents)

---

## Scenario 6: OpenSearch vs Redshift

**Scenario:** A BI team needs to run **complex SQL joins and aggregations over petabytes of structured sales data** for scheduled reports.

**Answer:** **Amazon Redshift** (columnar MPP data warehouse), not OpenSearch.

**Why:** Redshift is built for **structured OLAP / SQL analytics at petabyte scale**. OpenSearch excels at **full-text search and log analytics**, not heavy relational SQL joins.

> **Exam Tip:** "SQL joins + data warehouse + BI reporting" → **Redshift**. "Search + logs + dashboards on semi-structured data" → **OpenSearch**.

[⬆ Back to top](#table-of-contents)

---

## Scenario 7: OpenSearch vs Athena

**Scenario:** A team occasionally runs **ad-hoc SQL queries directly over log files in S3** and wants **no infrastructure to manage and to pay only per query**.

**Answer:** **Amazon Athena** (serverless SQL over S3), not OpenSearch.

**Why:** Athena is **serverless, pay-per-query** over S3 — ideal for **infrequent, ad-hoc** analysis with no cluster. OpenSearch is better when you need **interactive dashboards, low-latency search, and near-real-time** analytics on continuously ingested data.

> **Exam Tip:** **Infrequent ad-hoc S3 queries, no infra** → **Athena**. **Continuous ingestion + live dashboards + search** → **OpenSearch**.

[⬆ Back to top](#table-of-contents)

---

## Scenario 8: Managed vs Self-Managed Elasticsearch

**Scenario:** A company self-manages an Elasticsearch cluster on EC2 and is overwhelmed by patching, scaling, snapshots, and node failures. They want the same capabilities with far less operational overhead.

**Answer:** Migrate to **Amazon OpenSearch Service** (managed). For zero capacity planning on spiky workloads, consider **OpenSearch Serverless**.

**Why:** The managed service handles patching, node recovery, snapshots, scaling, and Multi-AZ — eliminating the undifferentiated heavy lifting of self-managed Elasticsearch on EC2.

> **Exam Tip:** "Reduce operational overhead of self-managed Elasticsearch on EC2" → **Amazon OpenSearch Service** (managed); spiky/unpredictable → **Serverless**.

[⬆ Back to top](#table-of-contents)

---

## Summary: Key Takeaways

- **Logs/observability** with live dashboards → **OpenSearch + Firehose**.
- **Full-text / relevance / faceted search** → **OpenSearch** (its sweet spot).
- **Cheap searchable old logs** → **UltraWarm**; archive → **cold**; automate with **ISM**.
- **Dashboard login** → **SAML or Cognito**; private endpoint → **VPC access** (set at creation).
- **SQL OLAP at PB scale** → **Redshift**; **ad-hoc serverless S3 SQL** → **Athena**.
- **Drop self-managed Elasticsearch on EC2** → **Amazon OpenSearch Service** (or Serverless).

[⬆ Back to top](#table-of-contents)
