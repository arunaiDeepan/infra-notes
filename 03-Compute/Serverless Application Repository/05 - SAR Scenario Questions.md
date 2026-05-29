# AWS SAR - Scenario Questions

> Exam-style scenario questions with full reasoning and "why the distractors are wrong." Covers when to pick SAR vs Service Catalog / Marketplace / ECR / CodeArtifact, sharing models, nested apps, immutability, capabilities, and pricing. Cover the answer first and reason it out before expanding.

See also: [01 - SAR Intro](01%20-%20SAR%20Intro.md) · [02 - SAR Architecture & Publishing Deep Dive](02%20-%20SAR%20Architecture%20%26%20Publishing%20Deep%20Dive.md) · [03 - SAR Sharing, Nested Apps & Governance Deep Dive](03%20-%20SAR%20Sharing%2C%20Nested%20Apps%20%26%20Governance%20Deep%20Dive.md) · [04 - SAR Examples & Patterns](04%20-%20SAR%20Examples%20%26%20Patterns.md) · [06 - SAR Important Facts & Cheat Sheet](06%20-%20SAR%20Important%20Facts%20%26%20Cheat%20Sheet.md)

---

## How to use this file

Each question lists the scenario, the options, then a collapsed answer. Try to answer before expanding. Difficulty: 🟢 recall · 🟡 application · 🔴 trap/nuance.

---

### Q1 🟢 — Core identification

A platform team wants to **share a reusable, Lambda-based serverless application** that other teams can deploy with minimal effort. Which AWS service is purpose-built for this?

A) Amazon ECR
B) AWS Serverless Application Repository
C) AWS CodeArtifact
D) AWS Service Catalog

> [!success]- Answer: B — Serverless Application Repository
> SAR is the managed catalog for **reusable serverless apps** (SAM templates). 
> - **A ECR** stores container images.
> - **C CodeArtifact** stores package dependencies (npm/pip/Maven).
> - **D Service Catalog** governs general approved products org-wide — possible but heavier; SAR is the serverless-specific, purpose-built answer.

---

### Q2 🔴 — SAR vs Service Catalog

An enterprise wants a **curated, governed catalog of approved infrastructure products of all types** (not just serverless) that business units self-serve, with **launch constraints and portfolios**. Which service?

A) Serverless Application Repository
B) AWS Service Catalog
C) AWS Marketplace
D) AWS Config

> [!success]- Answer: B — AWS Service Catalog
> "Governed catalog of **all kinds of approved products**, **portfolios**, **launch constraints**" is Service Catalog. SAR (A) is specifically for **serverless apps**. Marketplace (C) is third-party software. Config (D) is compliance assessment.

---

### Q3 🟡 — Share internally, not publicly

A company has a vetted serverless component and wants **every account in its AWS Organization** to be able to deploy it, but it must **not be exposed to the public**. What should they do?

A) Publish the app publicly with a verified author badge
B) Share the app with the AWS Organization via the application policy
C) Email the SAM template to each team
D) Copy the app into each account's SAR

> [!success]- Answer: B — Share with the Organization
> SAR integrates with AWS Organizations: grant `Deploy` to the org in the **application policy**, keeping the app private to the org while every member (including future accounts) can deploy.
> - **A** would expose it to all AWS customers.
> - **C/D** lose versioning, governance, and central control.

---

### Q4 🟢 — Cost of SAR

How much does AWS charge for **using the Serverless Application Repository** to publish and deploy applications?

A) A flat monthly fee per published app
B) Nothing for SAR itself — you pay only for the deployed resources
C) Per-deployment fee
D) Per-GB storage of the application code

> [!success]- Answer: B
> SAR is **free**; you pay only for the AWS resources the deployed app provisions/runs (Lambda, API Gateway, DynamoDB, etc.).

---

### Q5 🔴 — Updating a published version

A developer needs to fix a bug in version `1.2.0` of a published SAR app. What's the correct action?

A) Overwrite the artifacts behind version 1.2.0
B) Edit the template of 1.2.0 in the console
C) Publish a new semantic version (e.g., 1.2.1); consumers choose to upgrade
D) Delete 1.2.0 and re-publish it with the same number

> [!success]- Answer: C — Publish a new version
> Published versions are **immutable**. You cannot edit or overwrite them (A, B). The correct flow is to publish a **new semantic version**; existing deployments stay pinned until they choose to update.

---

### Q6 🟡 — Nested applications capability

A SAM template references two other SAR apps as **nested applications**. The deployment fails until a capability is acknowledged. Which one?

A) `CAPABILITY_IAM`
B) `CAPABILITY_NAMED_IAM`
C) `CAPABILITY_AUTO_EXPAND`
D) `CAPABILITY_RESOURCE_POLICY`

> [!success]- Answer: C — `CAPABILITY_AUTO_EXPAND`
> Nested applications/macros that expand at deploy time require **`CAPABILITY_AUTO_EXPAND`**. (`CAPABILITY_IAM`/`NAMED_IAM` are for creating IAM resources; `RESOURCE_POLICY` is for resource-based policies.)

---

### Q7 🟡 — How a SAR app is deployed

When a consumer deploys a SAR application into their account, what is actually created?

A) An AMI launched as an EC2 instance
B) A CloudFormation stack (via a change set) provisioning the app's resources
C) A container task in ECS
D) A CodeArtifact package

> [!success]- Answer: B — A CloudFormation stack
> SAR hands the SAM template to **CloudFormation**: deploy creates a change set, then a managed stack of resources. This is why SAR deployments are repeatable and easy to manage/delete.

---

### Q8 🔴 — SAR vs Marketplace for distribution

An ISV wants to **sell** a serverless integration to customers with **AWS-integrated billing/metering**. Best fit?

A) Publish a public SAR app
B) AWS Marketplace
C) Share via SAR organization policy
D) CodeArtifact

> [!success]- Answer: B — AWS Marketplace
> For **commercial software with integrated billing/subscriptions**, Marketplace is built for it. SAR public listing (A) lets customers deploy for free into their own accounts but is **not** a billing/commerce platform. Org sharing (C) is internal only.

---

### Q9 🟡 — Built on what?

The Serverless Application Repository is built on top of which framework, and uses which engine to provision deployed apps?

A) Built on Terraform; provisions via CDK
B) Built on AWS SAM; provisions via CloudFormation
C) Built on Elastic Beanstalk; provisions via OpsWorks
D) Built on Helm; provisions via EKS

> [!success]- Answer: B — SAM + CloudFormation
> SAR apps are **SAM templates**; deployment is a **CloudFormation** stack. This pairing is core to how SAR works.

---

### Q10 🔴 — Publishing a public app

A team is publishing an app to the **public** catalog but the submission is rejected. Which requirement is most likely missing?

A) A multi-AZ configuration
B) A publicly readable `SourceCodeUrl` and a license (e.g., SPDX)
C) A reserved concurrency setting on the Lambda
D) An attached AWS WAF web ACL

> [!success]- Answer: B
> Public apps must include a **publicly accessible `SourceCodeUrl`** and **license**, and pass **AWS review**. The other items are unrelated to SAR publishing requirements.

---

### Q11 🟡 — Catalog confusion

Match the artifact to the right repository service: a team needs to store **Docker images**, **npm/Maven packages**, and **reusable serverless apps**, respectively.

A) ECR, CodeArtifact, SAR
B) SAR, ECR, CodeArtifact
C) CodeArtifact, SAR, ECR
D) ECR, SAR, CodeArtifact

> [!success]- Answer: A — ECR, CodeArtifact, SAR
> **Container images → ECR**, **package dependencies → CodeArtifact**, **serverless apps → SAR**. Keep these three straight; they're frequent distractors.

---

### Q12 🟡 — Permission to deploy

Account B can **see** a shared SAR app but cannot deploy it. What's most likely missing in the application policy?

A) The `Deploy` action for Account B's principal
B) A NAT gateway in Account B
C) `CAPABILITY_IAM` on the publisher side
D) A VPC peering connection

> [!success]- Answer: A — the `Deploy` action
> Sharing must grant the **`Deploy`** action (CreateCloudFormationChangeSet + GetApplication) to the consumer principal. Viewing without `Deploy` means they can find but not launch it.

---

### Q13 🔴 — Reproducible nested builds

A team wants nested-app references in their template to produce **identical, reproducible** deployments over time. What should they do?

A) Always reference the "latest" version
B) Pin each nested app's `SemanticVersion` to a specific immutable version
C) Copy the nested app's resources inline
D) Disable `CAPABILITY_AUTO_EXPAND`

> [!success]- Answer: B — Pin `SemanticVersion`
> Because versions are immutable, **pinning `SemanticVersion`** in each `AWS::Serverless::Application` `Location` guarantees reproducible builds. "Latest" (A) could change underneath you; inlining (C) loses the reuse/versioning benefit.

---

### Q14 🟡 — Where does the code go?

During `sam package`, where are the Lambda code artifacts uploaded before publishing to SAR?

A) Directly into the SAR application object
B) Amazon S3, with the template rewritten to reference the S3 location
C) Amazon ECR
D) AWS CodeArtifact

> [!success]- Answer: B — Amazon S3
> `sam package` uploads artifacts to **S3** and rewrites `CodeUri`/`ContentUri` to S3 URIs; the packaged template is then published. SAR is also **regional**, so artifacts must exist in the target Region.

---

### Q15 🔴 — Best fit, multi-account guardrails

A security team publishes a standard "logging + alerting" serverless app and wants (1) all org accounts to deploy it and (2) member accounts blocked from disabling CloudTrail. What combination is best?

A) Public SAR app + IAM users
B) SAR shared with the Organization + an SCP denying CloudTrail disable actions
C) Service Catalog product + NACLs
D) Marketplace subscription + security groups

> [!success]- Answer: B — SAR org-share + SCP
> **SAR shared with the Organization** distributes the app internally; an **SCP** ([08 - SCP](08%20-%20SCP.md)) provides the hard org-wide guardrail (deny disabling CloudTrail). These two layers solve the two distinct needs cleanly.

---

## Rapid-fire trigger drills

| Stimulus in the question | Answer |
| :--- | :--- |
| "Reusable/shareable **serverless app**" | SAR |
| "Share serverless app **org-wide, not public**" | SAR shared with the **Organization** |
| "Distribute serverless app to **external** customers (free)" | **Public** SAR app + verified author |
| "**Sell** software with AWS billing" | AWS **Marketplace** |
| "Governed catalog of **all** product types, portfolios/constraints" | **Service Catalog** |
| "Store **container images**" | **ECR** |
| "Store **package dependencies**" | **CodeArtifact** |
| "**Update** a published SAR version" | Publish a **new semantic version** (immutable) |
| "Deploy a SAR app creates a..." | **CloudFormation stack** |
| "Template has **nested apps**" | Acknowledge **`CAPABILITY_AUTO_EXPAND`** |
| "Cost of SAR" | **Free** (pay only for deployed resources) |
| "Consumer can see but not deploy" | Grant **`Deploy`** in application policy |

> Next: [06 - SAR Important Facts & Cheat Sheet](06%20-%20SAR%20Important%20Facts%20%26%20Cheat%20Sheet.md) — the one-page exam cram.
