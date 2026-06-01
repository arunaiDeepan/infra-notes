# Neptune Scenario Questions - SAA-C03 Deep Dive

> Exam-style scenarios that map relationship-heavy, graph, RDF, fraud, recommendation, and "joins too slow" requirements to Amazon Neptune — and contrast it with relational and DynamoDB choices.

See also: [01 - Neptune Intro & Core Concepts](01%20-%20Neptune%20Intro%20%26%20Core%20Concepts.md) · [02 - Neptune Architecture Deep Dive](02%20-%20Neptune%20Architecture%20Deep%20Dive.md) · [03 - Neptune Best Practices & Examples](03%20-%20Neptune%20Best%20Practices%20%26%20Examples.md) · [05 - Neptune Troubleshooting (SRE)](05%20-%20Neptune%20Troubleshooting%20%28SRE%29.md) · [06 - Neptune Important Facts & Cheat Sheet](06%20-%20Neptune%20Important%20Facts%20%26%20Cheat%20Sheet.md) · [00 - Databases Overview & Exam Guide](00%20-%20Databases%20Overview%20%26%20Exam%20Guide.md) · [01 - Aurora Intro & Core Concepts](01%20-%20Aurora%20Intro%20%26%20Core%20Concepts.md)

---

## Table of Contents

- [Q1 Social Network Friends-of-Friends](#q1-social-network-friends-of-friends)
- [Q2 Fraud Detection Ring](#q2-fraud-detection-ring)
- [Q3 Knowledge Graph](#q3-knowledge-graph)
- [Q4 RDF / SPARQL Data](#q4-rdf--sparql-data)
- [Q5 Joins Too Slow](#q5-joins-too-slow)
- [Q6 Neptune vs DynamoDB](#q6-neptune-vs-dynamodb)
- [Q7 Recommendation Engine](#q7-recommendation-engine)
- [Q8 Predict Missing Connections](#q8-predict-missing-connections)
- [Exam Tips & Traps](#exam-tips--traps)

---

## Q1 Social Network Friends-of-Friends

**Scenario:** A social app must show "people you may know" by finding friends-of-friends and mutual connections in real time across millions of users. Relational JOINs are getting slow.

**Answer:** **Amazon Neptune** (property graph). Multi-hop traversals (`out('knows').out('knows')`) are exactly what a graph database is built for.

**Why not others:** RDS/Aurora would need recursive self-joins that degrade with depth and data size; DynamoDB has no efficient multi-hop traversal.

[⬆ Back to top](#table-of-contents)

---

## Q2 Fraud Detection Ring

**Scenario:** A payments company wants to detect fraud rings — accounts that share devices, addresses, or cards within a few hops of a flagged account — and surface these patterns quickly.

**Answer:** **Amazon Neptune**. Model accounts, devices, cards, addresses as nodes and shared usage as edges; detect rings via relationship-pattern traversals.

**Why:** Fraud detection over **connected entities** is a canonical graph use case; SQL pattern matching across many shared attributes is slow and complex.

[⬆ Back to top](#table-of-contents)

---

## Q3 Knowledge Graph

**Scenario:** An enterprise is building a knowledge graph linking entities (people, projects, documents, topics) for semantic search and discovery of related items.

**Answer:** **Amazon Neptune**. Use a property graph (Gremlin/openCypher) or RDF (SPARQL) depending on whether you need W3C-standard, interoperable semantics.

**Why:** Knowledge graphs are inherently relationship-centric; Neptune is purpose-built for them.

[⬆ Back to top](#table-of-contents)

---

## Q4 RDF / SPARQL Data

**Scenario:** A research team has existing **RDF triples** and queries them with **SPARQL**, integrating multiple public linked-data vocabularies. They want a managed service.

**Answer:** **Amazon Neptune** with the **RDF model and SPARQL**. Neptune natively supports W3C RDF/SPARQL.

**Why not others:** No relational or NoSQL AWS DB natively runs SPARQL over RDF triples. The keyword **SPARQL/RDF/W3C → Neptune**.

[⬆ Back to top](#table-of-contents)

---

## Q5 Joins Too Slow

**Scenario:** An app stores deeply connected data in PostgreSQL. Key queries traverse 5–6 levels of relationships and now require huge recursive CTEs that time out as data grows.

**Answer:** Migrate the relationship-heavy workload to **Amazon Neptune**. Traversal cost scales with relationships touched, not table size.

**Why:** "Many JOINs / recursive queries too slow for deep relationships" is the textbook signal to move from relational to **graph**.

[⬆ Back to top](#table-of-contents)

---

## Q6 Neptune vs DynamoDB

**Scenario:** A team debates DynamoDB vs Neptune for a feature that finds the shortest connection path between any two users across a large network.

**Answer:** **Amazon Neptune**. Shortest-path / connectivity / multi-hop traversal needs a graph engine.

**Why not DynamoDB:** DynamoDB is a **key-value/document** store optimized for fast single-item/partition access at scale — it cannot efficiently do arbitrary-depth relationship traversals or pathfinding.

| Need                                               | Best fit         |
| :------------------------------------------------- | :--------------- |
| Multi-hop relationships, paths, rings              | **Neptune**      |
| Single-digit-ms key-value lookups at massive scale | **DynamoDB**     |
| General relational/tabular + SQL                   | **RDS / Aurora** |

[⬆ Back to top](#table-of-contents)

---

## Q7 Recommendation Engine

**Scenario:** An e-commerce site wants "customers who bought this also bought" plus recommendations based on what a user's connections purchased, updated as the graph grows.

**Answer:** **Amazon Neptune** (property graph traversals for collaborative-filtering-style recommendations).

**Why:** Recommendations are computed by traversing purchase/relationship edges — a graph-native pattern. For predictive recommendations, add **Neptune ML**.

[⬆ Back to top](#table-of-contents)

---

## Q8 Predict Missing Connections

**Scenario:** A platform wants to predict likely-but-not-yet-existing relationships (e.g., suggest connections or likely fraudulent links) using machine learning on its graph.

**Answer:** **Neptune ML** — uses **Graph Neural Networks via SageMaker** for **link prediction** and **node classification**.

**Why:** This is ML-driven inference over graph structure, which is exactly Neptune ML's purpose (see [02 - Neptune Architecture Deep Dive](02%20-%20Neptune%20Architecture%20Deep%20Dive.md)).

[⬆ Back to top](#table-of-contents)

---

## Exam Tips & Traps

- Relationship/connection/graph/path keywords → **Neptune**, not DynamoDB or RDS.
- **SPARQL/RDF/W3C** → Neptune RDF model; **Gremlin/openCypher** → Neptune property graph.
- "JOINs/recursive queries too slow for deep relationships" → migrate to **Neptune**.
- **Fraud rings, friends-of-friends, recommendations, knowledge/identity graphs** → Neptune.
- ML predictions on a graph (link prediction, node classification) → **Neptune ML (GNN + SageMaker)**.
- DynamoDB = key-value scale, **not** multi-hop traversal.

[⬆ Back to top](#table-of-contents)
