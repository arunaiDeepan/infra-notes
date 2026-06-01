# Incident Response - Scenarios & SRE Ops

> Rehearsing the moves so you're calm when it's on fire. Symptom→cause→mitigation tables, CKA/CKAD-style triage tasks, interview questions, EKS production incidents, and runbooks. Pair with [01 - Incident Response Guide](01%20-%20Incident%20Response%20Guide.md).

See also: [01 - Incident Response Guide](01%20-%20Incident%20Response%20Guide.md) · [02 - Observability Scenarios & SRE Ops](02%20-%20Observability%20Scenarios%20%26%20SRE%20Ops.md) · [02 - Control Plane Reliability Scenarios & SRE Ops](02%20-%20Control%20Plane%20Reliability%20Scenarios%20%26%20SRE%20Ops.md)

---

## Table of Contents

- [1. Frequently Tested Concepts](#1-frequently-tested-concepts)
- [2. Symptom → Layer → First Move](#2-symptom--layer--first-move)
- [3. Triage Tasks (rehearsed moves)](#3-triage-tasks-rehearsed-moves)
- [4. Interview Questions](#4-interview-questions)
- [5. EKS Production Incidents](#5-eks-production-incidents)
- [6. Runbooks](#6-runbooks)
- [7. One-Line Recap](#7-one-line-recap)

---

## 1. Frequently Tested Concepts

- **Algorithm:** confirm → freeze → isolate layer → mitigate → preserve → root-cause.
- **Most outages are change-related** (bad rollout = #1).
- **Mitigate before diagnosing** (rollback/scale/failover).
- **Zero endpoints** = readiness/labels; **`--previous` logs** for crashes.
- **Default-deny without DNS allow** = self-inflicted outage.
- **Blameless post-mortem** → new dashboard/alert/runbook.

[⬆ Back to top](#table-of-contents)

---

## 2. Symptom → Layer → First Move

| Symptom                               | Layer         | First move                            |
| :------------------------------------ | :------------ | :------------------------------------ |
| Errors right after deploy             | App/rollout   | `kubectl rollout undo`                |
| Restarts climbing, exit 137           | Resources     | `--previous` logs; raise mem / scale  |
| Services can't resolve names          | DNS           | Check CoreDNS + NetworkPolicy 53      |
| New pods `ContainerCreating`, "no IP" | CNI           | VPC IP exhaustion → prefix delegation |
| `kubectl` hangs, nodes NotReady       | Control plane | Reduce load; check 429s/AWS Health    |
| `ImagePullBackOff`                    | Registry      | Fix creds/digest; rollback            |
| `Multi-Attach`/`FailedMount`          | Storage       | Detach stuck EBS; check CSI           |
| Time out but pods Ready               | NetworkPolicy | Add allow for critical paths          |
| 404/502/503 at edge                   | Ingress       | Check rules + ALB target health       |
| TLS fails at a set time               | Certs         | Renew; add expiry alerts              |
| Pod/ns stuck Terminating              | Finalizers    | Fix owning controller                 |
| "Everything slow"                     | Many          | `top`, traces, freeze changes         |

[⬆ Back to top](#table-of-contents)

---

## 3. Triage Tasks (rehearsed moves)

**T1 - Stop a bad rollout fast:**

```bash
kubectl rollout undo deploy/<name>
kubectl get endpointslices -l kubernetes.io/service-name=<svc> -o wide
```

**T2 - Crash root cause:**

```bash
kubectl describe pod <pod> | sed -n '/Events/,$p'
kubectl logs <pod> --previous --tail=200
```

**T3 - Prove DNS in/out:**

```bash
kubectl run tmp --rm -it --image=busybox -- nslookup kubernetes.default
```

**T4 - Isolate a bad node:**

```bash
kubectl cordon <node>
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data
```

**T5 - Force traffic off unready pods (confirm readiness gating):**

```bash
kubectl get pods -l app=<app> -o wide   # READY column; endpoints follow readiness
```

[⬆ Back to top](#table-of-contents)

---

## 4. Interview Questions

**Q1: Walk me through your first 5 minutes of a major incident.**

> Confirm impact + scope; declare incident/roles; freeze risky changes (pause rollouts/autoscale); correlate with the latest change; mitigate (rollback/scale/failover) to stop the bleeding; _then_ diagnose.

**Q2: Errors started right after a deploy. What do you do?**

> Assume the deploy until proven otherwise. `rollout undo`, verify endpoints recover, then capture `--previous` logs + config/image diff to find the real cause.

**Q3: Services time out but every pod is Ready. Hypotheses?**

> NetworkPolicy drop (esp. DNS egress), CoreDNS issue, or a dependency. Test from a debug pod, check recent policy changes, verify endpoints + DNS.

**Q4: How do you avoid making an incident worse?**

> Freeze changes, don't run expensive cluster-wide LISTs during control-plane stress, mitigate reversibly (rollback over hand-editing), and preserve evidence before deleting resources.

**Q5: What makes a good post-mortem?**

> Blameless, timeline of trigger + earliest signals, what mitigated fastest, and a concrete shipped guardrail (alert/runbook/policy) so it can't recur silently.

[⬆ Back to top](#table-of-contents)

---

## 5. EKS Production Incidents

### Medium

**M1 - Deploy bricked the service; need fastest recovery.**

> `kubectl rollout undo`; confirm endpoints repopulate; ALB targets healthy. Capture evidence. Add a canary + readiness fix to prevent recurrence.

**M2 - CoreDNS overwhelmed during a traffic spike.**

> Scale CoreDNS, deploy NodeLocal DNSCache, reduce `ndots` amplification. Alert on CoreDNS latency.

**M3 - Cert expired on the ALB at midnight.**

> Reissue via ACM/cert-manager; add expiry alerts 30/14/7 days out; automate renewal.

**M4 - Namespace stuck Terminating, blocking cleanup.**

> A finalizer's controller is down. Restore the controller; remove finalizer only as a documented last resort.

### Hard

**H1 - Cascading outage: tight CPU limits throttled pods → readiness failed → traffic concentrated → more failures.**

> Break the loop: raise CPU limits / scale out now; long-term move HPA to RPS and loosen latency-path limits. Classic throttling cascade. See [01 - Scheduling & Resources Guide](01%20-%20Scheduling%20%26%20Resources%20Guide.md).

**H2 - A default-deny NetworkPolicy rollout took the whole namespace down.**

> Missing DNS + ingress allows. Apply emergency allow rules (DNS, ingress→app, app→db); roll back the policy; re-stage with allows first in a canary namespace.

**H3 - apiserver 429s during a mass job; nodes flapping NotReady.**

> A controller/job is hammering the API → heartbeat cascade. Throttle/stop the offender, rely on APF, avoid bulk LISTs, check EKS control-plane metrics. See [01 - Control Plane Reliability Guide](01%20-%20Control%20Plane%20Reliability%20Guide.md).

**H4 - Stateful pod down: `Multi-Attach error` after an ungraceful node loss.**

> EBS RWO volume still attached to the dead node. Wait for / force detach, confirm single-mount, let the pod reschedule in the volume's AZ. See [01 - StatefulSets & Storage Guide](01%20-%20StatefulSets%20%26%20Storage%20Guide.md).

**H5 - "Everything is slow" with no deploy and no obvious cause.**

> Systematically isolate: one service vs many → traces for slow span; DNS latency; node pressure; control-plane latency; dependency saturation. Mitigate by scaling/shedding while you localize; freeze changes meanwhile.

[⬆ Back to top](#table-of-contents)

---

## 6. Runbooks

### Runbook: incident commander checklist

1. Declare incident; assign IC + comms + ops roles.
2. Confirm impact + scope; set a status channel.
3. Freeze changes (rollouts, autoscaling if amplifying).
4. Isolate layer (use the symptom table); mitigate reversibly.
5. Preserve evidence (`--previous` logs, events, metric snapshots).
6. Stabilize → comms update → schedule blameless post-mortem.

### Runbook: post-incident

1. Build the timeline (trigger, earliest signals, actions, recovery).
2. Identify the fastest effective mitigation and codify it.
3. Ship one concrete guardrail (alert/runbook/policy/limit).
4. File action items with owners + dates; verify they land.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Confirm → freeze → isolate layer → mitigate → preserve → root-cause. Most outages are change-related; rollback first, diagnose second. Use the symptom→layer table to jump to the right playbook (rollout, OOM, DNS, CNI, control plane, image/volume, NetworkPolicy/ingress/certs, finalizers, mystery latency). Every incident ships a guardrail.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [01 - Reliability Architectures Guide](01%20-%20Reliability%20Architectures%20Guide.md).
