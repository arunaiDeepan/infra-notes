# AWS Step Functions - Scenarios, Best Practices & SRE Troubleshooting (SAA-C03)

> Scenario drills + production troubleshooting for orchestration. Key exam discriminators: Standard vs Express, when to orchestrate vs choreograph, and the callback pattern.

See also: [01 - Step Functions Fundamentals & Deep Dive](01%20-%20Step%20Functions%20Fundamentals%20%26%20Deep%20Dive.md) · [02 - Step Functions Architecture & Examples](02%20-%20Step%20Functions%20Architecture%20%26%20Examples.md) · [03 - EventBridge Scenarios, Best Practices & Troubleshooting](03%20-%20EventBridge%20Scenarios%2C%20Best%20Practices%20%26%20Troubleshooting.md)

---

## Table of Contents

- [1. Scenario-Based Questions](#1-scenario-based-questions)
- [2. Best Practices](#2-best-practices)
- [3. Common Errors & Troubleshooting (SRE View)](#3-common-errors--troubleshooting-sre-view)
- [4. Key CloudWatch Metrics](#4-key-cloudwatch-metrics)
- [5. Orchestration vs Choreography](#5-orchestration-vs-choreography)
- [6. Rapid-Fire Facts](#6-rapid-fire-facts)

---

## 1. Scenario-Based Questions

**Q1.** An order process has 8 steps with conditional branches, retries, and a refund on failure - currently a tangle of Lambdas calling Lambdas.
**A.** **Step Functions Standard** state machine with Choice/Retry/Catch; removes orchestration code from Lambdas and adds visual debugging.

---

**Q2.** A workflow must pause until a manager clicks "approve" in an email, possibly days later.
**A.** **Standard** workflow + **`.waitForTaskToken`** callback; resumes on `SendTaskSuccess`.

---

**Q3.** Process 10 million S3 objects in parallel, serverless, with concurrency control.
**A.** **Distributed Map** state.

---

**Q4.** A high-volume API backend needs to orchestrate 3 quick steps per request at 50,000 req/s, cheaply.
**A.** **Express** workflow (synchronous), priced by duration.

---

**Q5.** Coordinate a nightly ETL across Glue, EMR, and Redshift, waiting for each job and retrying transient failures.
**A.** **Standard** workflow using **`.sync`** service integrations + Retry; triggered by **EventBridge Scheduler**.

---

**Q6.** Maintain consistency across payment, inventory, and shipping microservices without a distributed transaction.
**A.** **Saga pattern** in Step Functions with **Catch → compensation** steps.

---

**Q7.** You need exactly-once execution and a full audit trail of each run for compliance.
**A.** **Standard** workflows (exactly-once + execution history).

---

**Q8.** Replace legacy Amazon SWF orchestration with a managed, visual service.
**A.** **Step Functions** (SWF is legacy).

---

**Q9.** Trigger a workflow whenever an object lands in S3.
**A.** **EventBridge rule** (S3 ObjectCreated) → **StartExecution**.

[⬆ Back to top](#table-of-contents)

---

## 2. Best Practices

| Area                          | Best Practice                                                             |
| :---------------------------- | :------------------------------------------------------------------------ |
| **Pick the right type**       | Standard for long/auditable; Express for short/high-volume.               |
| **Use Retry/Catch**           | Push resilience into the state machine, not Lambda code.                  |
| **Idempotent tasks**          | Retries and at-least-once (Express) can re-run a step.                    |
| **Least-privilege role**      | Scope the execution role to exact task resources.                         |
| **Keep state small**          | Payload limit is 256 KB between states - pass S3 references for big data. |
| **Use `.sync` for jobs**      | Let the workflow wait for ECS/Glue/EMR completion natively.               |
| **Distributed Map for scale** | Don't loop millions of items in a single Lambda.                          |
| **Observability**             | Enable X-Ray + CloudWatch Logs; alarm on `ExecutionsFailed`.              |
| **Timeouts**                  | Set `TimeoutSeconds` on Task states to avoid stuck executions.            |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Errors & Troubleshooting (SRE View)

| Symptom                         | Likely Cause                                               | Resolution                                                                    |
| :------------------------------ | :--------------------------------------------------------- | :---------------------------------------------------------------------------- |
| **`States.Timeout`**            | Task ran longer than `TimeoutSeconds` or default           | Increase timeout; add heartbeats for long tasks                               |
| **`States.DataLimitExceeded`**  | State payload > **256 KB**                                 | Pass **S3 references** instead of inline data                                 |
| **Task `AccessDenied`**         | Execution role lacks permission to invoke target           | Grant least-privilege to the exact resource ARN                               |
| **Workflow stuck (callback)**   | `SendTaskSuccess`/`Failure` never called; heartbeat missed | Ensure the external system returns the **task token**; set `HeartbeatSeconds` |
| **Express execution lost**      | At-least-once / at-most-once semantics                     | Use Standard for exactly-once; make steps idempotent                          |
| **Lambda `TooManyRequests`**    | Downstream Lambda throttled                                | Add Retry on `Lambda.TooManyRequestsException`; raise concurrency             |
| **Execution history truncated** | Express logs to CloudWatch, not visual history             | Use Standard for full visual history, or read CW Logs                         |
| **High cost (Standard)**        | Many state transitions in a hot path                       | Switch hot, short workflows to **Express**                                    |
| **`States.Runtime` error**      | Bad input/output path / JSON reference                     | Fix `ResultPath`/`Parameters` JSONPath                                        |
| **Map running too hot**         | Unbounded concurrency overloads downstream                 | Set `MaxConcurrency` on Map/Distributed Map                                   |

**SRE note:** The single most common production issue is **payload bloat** (256 KB limit) - always pass pointers to S3 for large data between states. The second is **stuck callbacks** - always pair `.waitForTaskToken` with heartbeats and timeouts so a missing callback fails fast instead of hanging for a year.

[⬆ Back to top](#table-of-contents)

---

## 4. Key CloudWatch Metrics

| Metric                | Tells You                                      |
| :-------------------- | :--------------------------------------------- |
| `ExecutionsStarted`   | Throughput of new workflows                    |
| `ExecutionsSucceeded` | Successful completions                         |
| `ExecutionsFailed`    | Failed workflows (alarm)                       |
| `ExecutionsTimedOut`  | Workflows hitting timeouts                     |
| `ExecutionThrottled`  | Start rate exceeding limits                    |
| `ExecutionTime`       | Duration distribution (cost & SLA for Express) |

[⬆ Back to top](#table-of-contents)

---

## 5. Orchestration vs Choreography

|                | **Orchestration (Step Functions)**                        | **Choreography (EventBridge/SNS/SQS)**       |
| :------------- | :-------------------------------------------------------- | :------------------------------------------- |
| **Control**    | Central state machine drives the flow                     | Services react to events independently       |
| **Visibility** | Full visual history of each run                           | Distributed; harder to trace end-to-end      |
| **Best when**  | Multi-step, branching, retries, compensation, human steps | Loose coupling, fan-out, independent scaling |
| **Coupling**   | Coordinator knows the steps                               | Producers don't know consumers               |

> **Exam:** "Need centralized control, visibility, and error handling across steps" → **Step Functions (orchestration)**. "Need loose coupling and independent reactions" → **EventBridge/SNS/SQS (choreography)**.

[⬆ Back to top](#table-of-contents)

---

## 6. Rapid-Fire Facts

- State machine in **ASL (JSON)**; states: Task, Choice, Parallel, Map, Wait, Pass, Succeed, Fail.
- **Standard:** ≤ 1 year, exactly-once, per-transition, visual history.
- **Express:** ≤ 5 min, 100k+/s, per-duration, CloudWatch Logs.
- Built-in **Retry** (backoff) + **Catch** (fallback/compensation).
- Integration patterns: **Request/Response**, **`.sync`**, **`.waitForTaskToken`**.
- **Distributed Map** = millions of S3 items in parallel.
- State payload limit **256 KB** → pass S3 references.
- **SWF is legacy** → use Step Functions.
- EventBridge **triggers**; Step Functions **orchestrates**.

[⬆ Back to top](#table-of-contents)
