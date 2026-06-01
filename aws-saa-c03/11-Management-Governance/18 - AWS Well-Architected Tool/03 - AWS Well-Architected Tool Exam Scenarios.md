# AWS Well-Architected Tool - Exam Scenarios

> Exam focus: the six pillars, HRIs/milestones, lenses, and WA Tool vs Trusted Advisor vs Config. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - AWS Well-Architected Tool Intro bits & bytes](01%20-%20AWS%20Well-Architected%20Tool%20Intro%20bits%20%26%20bytes.md) · [02 - AWS Well-Architected Tool Deep Dive](02%20-%20AWS%20Well-Architected%20Tool%20Deep%20Dive.md) · [04 - AWS Well-Architected Tool SRE Operations](04%20-%20AWS%20Well-Architected%20Tool%20SRE%20Operations.md) · [01 - AWS Trusted Advisor Intro bits & bytes](01%20-%20AWS%20Trusted%20Advisor%20Intro%20bits%20%26%20bytes.md)

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

- **Six pillars** (Sustainability is the sixth).
- Guided **review** producing **HRIs/MRIs** + improvement plan.
- **Milestones** to track progress.
- **Lenses** (default, specialized catalog, custom).
- WA Tool (review) vs Trusted Advisor (automated checks) vs Config (compliance).
- It's **advisory** — doesn't enforce or auto-detect.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                           | Points to                         |
| :----------------------------------------------- | :-------------------------------- |
| "structured/guided architecture review"          | **WA Tool**                       |
| "identify high-risk issues", "improvement plan"  | **WA Tool (HRIs)**                |
| "track improvement over time"                    | **Milestones**                    |
| "serverless/SaaS/ML specific best practices"     | **Specialized lens**              |
| "encode our own internal standards into reviews" | **Custom lens**                   |
| "automated account checks"                       | **Trusted Advisor** (not WA Tool) |
| "the six pillars / sustainability"               | **Well-Architected Framework**    |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Expecting the WA Tool to **auto-detect** issues (it relies on answers).
- Confusing it with **Trusted Advisor** (automated) or **Config** (compliance/enforcement).
- Forgetting **Sustainability** as the sixth pillar.
- Thinking it **enforces** best practices (it's advisory).
- Using it to **right-size** (Compute Optimizer).

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **"Review / questionnaire / HRIs / improvement plan / milestones"** → WA Tool.
2. **"Automated checks"** → Trusted Advisor.
3. **"Continuous custom compliance / remediation"** → Config.
4. **"Domain-specific best practices"** → specialized lens; **"our standards"** → custom lens.
5. **"Right-size / forecast cost"** → Compute Optimizer / Cost Explorer.

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** Run a structured review of a workload against AWS best practices and get an improvement plan.
**Options:** A) Trusted Advisor B) Well-Architected Tool C) Config D) Compute Optimizer
**Correct:** B
**Explanation:** Guided reviews + improvement plans are the WA Tool.

### Q2

**Scenario:** How many WA pillars and which is newest?
**Options:** A) Five B) Six; Sustainability C) Four D) Seven
**Correct:** B
**Explanation:** Six pillars; Sustainability is newest.

### Q3

**Scenario:** Track whether HRIs decrease across quarterly reviews.
**Options:** A) Trusted Advisor B) WA Tool milestones C) Config D) Budgets
**Correct:** B
**Explanation:** Milestones snapshot progress.

### Q4

**Scenario:** Apply serverless-specific best practices to a Lambda app review.
**Options:** A) Default lens only B) Serverless lens from the Lens Catalog C) Custom rule D) Trusted Advisor
**Correct:** B
**Explanation:** Specialized lenses tailor the review.

### Q5

**Scenario:** Encode the company's internal standards into reviews.
**Options:** A) Config B) Custom lens C) SCP D) Budget
**Correct:** B
**Explanation:** Custom lenses capture internal best practices.

### Q6

**Scenario:** Need automated, continuous account checks instead of a review.
**Options:** A) WA Tool B) Trusted Advisor C) Milestones D) Profile
**Correct:** B
**Explanation:** Automated checks → Trusted Advisor.

### Q7

**Scenario:** Pre-launch readiness assessment for a new workload.
**Options:** A) Compute Optimizer B) WA Tool review (e.g. FTR lens) C) Budgets D) CloudTrail
**Correct:** B
**Explanation:** WA Tool reviews assess readiness.

### Q8

**Scenario:** Prioritize the most relevant questions for a regulated, cost-sensitive context.
**Options:** A) Answer all equally B) Use a Profile C) Trusted Advisor D) Config
**Correct:** B
**Explanation:** Profiles tailor prioritization to context.

### Q9

**Scenario:** Share a workload review with a central architecture team in another account.
**Options:** A) Email screenshots B) Share the workload (IAM/account/org) C) Export only D) Not possible
**Correct:** B
**Explanation:** Workloads/lenses can be shared.

### Q10

**Scenario:** Does the WA Tool enforce best practices automatically?
**Options:** A) Yes B) No — it's advisory; enforce via SCP/Config/Service Catalog C) Only security D) Only cost
**Correct:** B
**Explanation:** It records/guides; enforcement is elsewhere.

### Q11

**Scenario:** Bring live account findings into the review.
**Options:** A) Manual B) Surfaced Trusted Advisor checks within the review C) Config only D) Not possible
**Correct:** B
**Explanation:** WA Tool surfaces relevant TA checks.

### Q12

**Scenario:** Which pillar covers DR and recovering from failure?
**Options:** A) Security B) Reliability C) Performance D) Cost
**Correct:** B
**Explanation:** Reliability covers HA/DR/recovery.

### Q13

**Scenario:** Which pillar covers minimizing environmental impact?
**Options:** A) Cost B) Sustainability C) Performance D) Ops
**Correct:** B
**Explanation:** Sustainability pillar.

### Q14

**Scenario:** Which pillar covers IaC, observability, and runbooks?
**Options:** A) Operational Excellence B) Reliability C) Security D) Cost
**Correct:** A
**Explanation:** Operational Excellence.

### Q15

**Scenario:** Document accepted risks formally for audit.
**Options:** A) Wiki B) WA Tool review + milestone with noted risk acceptance C) Budget D) CloudTrail
**Correct:** B
**Explanation:** Reviews + milestones document risk posture.

### Q16

**Scenario:** Standardize how dozens of teams start reviews.
**Options:** A) Ad hoc B) Review templates C) Custom rule D) Budget
**Correct:** B
**Explanation:** Review templates ensure consistency.

### Q17

**Scenario:** Cost of using the WA Tool?
**Options:** A) Per review B) Free C) Per workload D) Support-gated
**Correct:** B
**Explanation:** The tool is free.

### Q18

**Scenario:** Convert HRIs into tracked, owned work.
**Options:** A) Ignore B) Export/integrate improvement items into ticketing (Jira) with owners C) Just note them D) Delete
**Correct:** B
**Explanation:** Turn HRIs into tracked remediation.

### Q19

**Scenario:** Apply both general and domain best practices to one workload.
**Options:** A) One lens only B) Multiple lenses (default + specialized) C) Custom rule D) Two workloads
**Correct:** B
**Explanation:** Multiple lenses can apply to a workload.

### Q20

**Scenario:** Which tool gives the _book_ of best practices vs the _review workbook_?
**Options:** A) Both same B) Framework = guidance; WA Tool = the review C) Trusted Advisor D) Config
**Correct:** B
**Explanation:** Framework is content; WA Tool operationalizes it.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** An enterprise wants every workload reviewed consistently, with internal compliance questions included, results visible to a central team, and progress tracked.
**Options:** A) Spreadsheets B) WA Tool with a **custom lens** (internal standards) + **review templates** + **shared workloads** org-wide + **milestones** C) Trusted Advisor only D) Config only
**Correct:** B
**Explanation:** Custom lens encodes standards; templates standardize; sharing centralizes; milestones track — the full WA Tool governance pattern.

### H2

**Scenario:** A serverless team's review using the default lens misses serverless-specific risks (cold starts, idempotency, fan-out).
**Options:** A) Default lens is enough B) Apply the **Serverless lens** (and relevant catalog lenses) in addition to the default C) Use Trusted Advisor D) Use Config
**Correct:** B
**Explanation:** Specialized lenses cover domain risks the general lens doesn't.

### H3

**Scenario:** Leadership wants evidence that identified High Risk Issues were remediated between two reviews for an audit.
**Options:** A) Verbal B) Compare **milestones** (before/after) showing HRIs resolved; attach to audit C) Trusted Advisor history D) CloudTrail
**Correct:** B
**Explanation:** Milestones are immutable snapshots proving progress over time.

### H4

**Scenario:** A team treats the WA Tool as the enforcement mechanism and is surprised non-compliant resources still deploy.
**Options:** A) File a bug B) Understand it's **advisory**; enforce via **SCPs/Config/Service Catalog**; use WA Tool to _review_, not block C) Disable it D) Manual gate
**Correct:** B
**Explanation:** WA Tool doesn't enforce; pair it with actual guardrails.

### H5

**Scenario:** Answers are guesses, so the review's risk picture is unreliable.
**Options:** A) Accept it B) Ground answers in **evidence** — Trusted Advisor checks (surfaced inline), Config compliance, Compute Optimizer/Cost Explorer data C) Skip questions D) Use defaults
**Correct:** B
**Explanation:** Evidence-based answers make the HRI/MRI output trustworthy.

### H6

**Scenario:** A regulated org needs context-aware reviews: pre-launch vs production, regulated vs internal, prioritizing the most relevant risks.
**Options:** A) Same questionnaire for all B) Use **Profiles** to capture business context so the tool prioritizes relevant questions/risks C) Trusted Advisor D) Custom rule
**Correct:** B
**Explanation:** Profiles tailor prioritization to the workload's context.

### H7

**Scenario:** HRIs are identified but nothing improves because no one owns them.
**Options:** A) Re-review more often B) Export improvement items into **ticketing** with owners/due dates; re-review and compare milestones C) Add lenses D) Ignore
**Correct:** B
**Explanation:** Operationalize HRIs as owned, tracked work, then verify via milestones.

### H8

**Scenario:** A central platform team must review 200 workloads across many accounts efficiently.
**Options:** A) One account B) **Share** workloads org-wide + standardized **review templates** + **custom lens**; aggregate results centrally C) Manual per account D) Trusted Advisor org view only
**Correct:** B
**Explanation:** Sharing + templates + custom lens scale consistent reviews across the org.

### H9

**Scenario:** Reliability pillar review reveals single-AZ and no DR; the team wants both the finding documented and the fix tracked to closure.
**Options:** A) WA Tool fixes it B) Document HRI in WA Tool → implement Multi-AZ/DR (Reliability best practices) → re-review → milestone shows HRI closed C) Trusted Advisor remediates D) Config
**Correct:** B
**Explanation:** WA Tool documents and tracks; the actual fix is architectural; milestones evidence closure.

### H10

**Scenario:** An org wants a combined practice: automated daily checks AND periodic deep reviews AND continuous compliance enforcement.
**Options:** A) One tool B) **Trusted Advisor** (automated checks) + **WA Tool** (periodic reviews) + **Config** (continuous compliance/remediation), each for its strength C) WA Tool only D) Config only
**Correct:** B
**Explanation:** The three are complementary: checks, reviews, and enforcement together form mature governance.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Structured review against the six pillars → Well-Architected Tool (HRIs/MRIs + improvement plan + milestones). Domain best practices → specialized lens; internal standards → custom lens. It's advisory — enforce with SCP/Config/Service Catalog. Automated checks → Trusted Advisor.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - AWS Well-Architected Tool SRE Operations](04%20-%20AWS%20Well-Architected%20Tool%20SRE%20Operations.md).
