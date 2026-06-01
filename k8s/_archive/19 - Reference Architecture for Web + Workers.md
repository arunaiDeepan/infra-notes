## Reference Architecture: Reliable Kubernetes for Web + Workers

### Components

- **Ingress/Gateway** → routes external HTTP(S)
- **Web API Deployment** → stateless, horizontally scalable
- **Worker Deployment** → queue consumers (scale on queue depth)
- **Redis** (cache) → ideally managed, or StatefulSet if you must
- **Database** → strongly recommended managed (RDS/Cloud SQL/etc). If self-hosted, StatefulSet + proper backup/replication.
- **Observability stack** → metrics/logs/traces/events
- **Policies** → PSA + admission rules + NetworkPolicy
- **Autoscaling** → HPA + Cluster Autoscaler + KEDA (for queues)

### Node pools (recommended)

- **system pool**: CoreDNS, ingress controller, observability agents, CSI, policy controllers
- **apps pool**: web + worker pods
- **stateful pool** (optional): if you insist on running DB/Redis in-cluster and want predictable IO

---

## 1) Web API: Deployment + Service + Probes + PDB + HPA

### Deployment (key reliability bits)

- readinessProbe gates traffic
- startupProbe prevents premature probe failure
- livenessProbe only if you can detect “wedged”
- graceful shutdown
- resource requests/limits (mandatory in production)
- topology spread or anti-affinity

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-api
  namespace: team-a-prod
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: web-api
  template:
    metadata:
      labels:
        app: web-api
    spec:
      terminationGracePeriodSeconds: 30
      containers:
        - name: web
          image: registry.example.com/web-api@sha256:REPLACE_WITH_DIGEST
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: "200m"
              memory: "512Mi"
            limits:
              cpu: "1000m"
              memory: "1024Mi"
          startupProbe:
            httpGet:
              path: /startup
              port: 8080
            failureThreshold: 30
            periodSeconds: 2
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            periodSeconds: 5
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: /live
              port: 8080
            periodSeconds: 10
            failureThreshold: 3
          lifecycle:
            preStop:
              exec:
                command: ["sh", "-c", "sleep 10"]
```

Why these choices matter:

- `maxUnavailable: 0` ensures you don’t drop serving capacity during rollout (works only if you have enough cluster capacity to surge).
- preStop “sleep 10” gives load balancers and clients time to drain connections (not always necessary but very common).
- digest pinning prevents “tag drift” surprises.

### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-api
  namespace: team-a-prod
spec:
  selector:
    app: web-api
  ports:
    - port: 80
      targetPort: 8080
```

### PodDisruptionBudget

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-api-pdb
  namespace: team-a-prod
spec:
  maxUnavailable: 1
  selector:
    matchLabels:
      app: web-api
```

Why PDB is set like this:

- It allows node drains and autoscaler scale-down without killing too many replicas at once.
- Don’t set `minAvailable: 3` unless you always _have_ >3 and enough capacity to move them.

### HPA (CPU-based baseline)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-api-hpa
  namespace: team-a-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-api
  minReplicas: 3
  maxReplicas: 30
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
```

Upgrade path:

- Replace/augment CPU metrics with RPS or latency if you have custom metrics (more reliable for IO-bound services).

---

## 2) Workers: KEDA (queue depth) + PDB + resources

Workers usually should scale on **queue depth**, not CPU.

### Worker Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: worker
  namespace: team-a-prod
spec:
  replicas: 2
  selector:
    matchLabels:
      app: worker
  template:
    metadata:
      labels:
        app: worker
    spec:
      containers:
        - name: worker
          image: registry.example.com/worker@sha256:REPLACE_WITH_DIGEST
          resources:
            requests:
              cpu: "200m"
              memory: "512Mi"
            limits:
              cpu: "2000m"
              memory: "1024Mi"
```

### KEDA ScaledObject (example concept)

Exact fields depend on your queue system (Kafka/SQS/RabbitMQ/etc), but the idea is the same: scale based on backlog.

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: worker-scaledobject
  namespace: team-a-prod
spec:
  scaleTargetRef:
    name: worker
  minReplicaCount: 0
  maxReplicaCount: 50
  pollingInterval: 30
  cooldownPeriod: 300
  triggers:
    - type: prometheus
      metadata:
        serverAddress: http://prometheus.observability.svc.cluster.local:9090
        metricName: queue_depth
        query: sum(queue_depth{queue="jobs"})
        threshold: "100"
```

Why this is good:

- Workers can scale to zero when idle (if your system tolerates cold starts).

- You scale on the real bottleneck: backlog.

### Worker PDB (careful!)

Workers often can tolerate more disruption than web, but you still want safety:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: worker-pdb
  namespace: team-a-prod
spec:
  maxUnavailable: 50%
  selector:
    matchLabels:
      app: worker
```

---

## 3) Resource governance: Quota + LimitRange (per namespace)

This prevents runaway teams and forces sane defaults.

### LimitRange (defaults if teams forget)

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: defaults
  namespace: team-a-prod
spec:
  limits:
    - type: Container
      defaultRequest:
        cpu: "100m"
        memory: "256Mi"
      default:
        cpu: "1000m"
        memory: "512Mi"
```

### ResourceQuota (cap the namespace)

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-a-prod-quota
  namespace: team-a-prod
spec:
  hard:
    requests.cpu: "20"
    requests.memory: "40Gi"
    limits.cpu: "40"
    limits.memory: "80Gi"
    pods: "200"
    persistentvolumeclaims: "50"
```

---

## 4) NetworkPolicy: default deny + explicit allows

This is the “no surprises” networking model.

### Default deny (ingress + egress)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: team-a-prod
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

### Allow DNS egress (CoreDNS)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: team-a-prod
spec:
  podSelector: {}
  policyTypes: ["Egress"]
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
          podSelector:
            matchLabels:
              k8s-app: kube-dns
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
```

### Allow ingress from ingress controller to web-api

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-ingress-to-web
  namespace: team-a-prod
spec:
  podSelector:
    matchLabels:
      app: web-api
  policyTypes: ["Ingress"]
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: ingress
```

You’d also add explicit allows from web → db, worker → queue, etc., ideally by namespace + labels.

---

## 5) Secrets: external store + workload identity (recommended)

Best practice in production:

- don’t store long-lived cloud keys in Kubernetes Secrets
- use workload identity + external secrets store

Pattern:

- web/worker SA maps to cloud IAM role
- fetch secrets from Secrets Manager/Vault via CSI driver or operator
- rotate secrets regularly

---

## 6) Reliability “interaction warnings” (the deadlock list)

These are the traps that make “everything is configured” but nothing moves:

- `maxUnavailable: 0` + no spare capacity → rollout stuck Pending.
- PDB too strict + node drain → upgrades and autoscaler scale-down stuck.
- readiness depends on DB being perfect → a DB hiccup removes all endpoints and causes total outage.
- default deny NetworkPolicy + forgot DNS allow → everything fails in weird ways.
- CPU limits too tight → throttling → readiness fails → cascading failure.
- HPA CPU scaling + wrong CPU requests → scaling becomes nonsense.
- worker scale-to-zero + slow cold start + queue spike → backlog delays (tune minReplicas or warmers).

---

## 7) The “operations contract” for this architecture

If you run this setup, you should also have:

- dashboards for golden signals
- alerting on burn rate + saturation
- runbooks for: bad rollout, DNS issues, CNI issues, OOM storms, volume attach issues
- game days (kill nodes, break DNS in staging, practice rollback)

---
