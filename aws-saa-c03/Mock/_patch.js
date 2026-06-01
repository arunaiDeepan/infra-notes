const fs = require('fs');
const path = 'Set - 2.md';
let s = fs.readFileSync(path, 'utf8');

// Each entry: qHeader (start search), explMarker (the literal Overall Explanation line as it appears),
// and the replacement text that runs FROM explMarker THROUGH the **Domain:** line (inclusive),
// i.e. everything between explMarker and the trailing separator is replaced.
// We locate explMarker index after qHeader, then find the next separator line (\n---\n or \n----\n)
// after it, and replace [explStart, sepStart).

function replaceBlock(qHeader, explMarker, newBlock) {
  const qIdx = s.indexOf(qHeader);
  if (qIdx < 0) throw new Error('header not found: ' + qHeader);
  const explIdx = s.indexOf(explMarker, qIdx);
  if (explIdx < 0) throw new Error('expl not found in ' + qHeader);
  // find separator after explIdx: a line that is exactly --- or ---- (with surrounding newlines)
  const re = /\n(-{3,})\n/g;
  re.lastIndex = explIdx;
  const m = re.exec(s);
  if (!m) throw new Error('separator not found after ' + qHeader);
  const sepStart = m.index; // position of the \n before dashes
  s = s.slice(0, explIdx) + newBlock + s.slice(sepStart);
}

// ---------------- Q1 ----------------
replaceBlock('### Question 1', '**Overall Explanation:**',
`**Overall Explanation:**

SQL injection and cross-site scripting (XSS) are application-layer (OSI Layer 7) attacks: the malicious payload is hidden inside the body, headers, query string, or cookies of an otherwise normal HTTP/HTTPS request. To block them you need a control that can actually parse the request and match its contents against attack signatures, which is precisely what **AWS WAF (Web Application Firewall)** does. WAF attaches a Web ACL to a CloudFront distribution, API Gateway, AppSync API, or an Application Load Balancer and inspects every request before it reaches the backend. AWS even ships managed rule groups (such as the SQL database and Known Bad Inputs sets) that recognize these exact patterns, so any request that matches a block rule is answered with an HTTP 403 (Forbidden) and never touches the EC2 fleet. Since the application here already sits behind an ALB, attaching a WAF Web ACL to that ALB is the direct fix.

A WAF rule can run in one of three modes: allow everything except what you specify, block everything except what you specify, or simply count matches (a safe way to validate a rule in production before enforcing it). For this scenario you create block rules for SQLi and XSS and associate them with the ALB.

\`\`\`mermaid
flowchart LR
    C["Clients & attackers"] --> W["AWS WAF Web ACL<br/>SQLi + XSS managed rules"]
    W -->|Matches block rule| B["HTTP 403 Forbidden"]
    W -->|Clean request| ALB["Application Load Balancer"]
    ALB --> ASG["Auto Scaling group<br/>EC2 instances"]
\`\`\`

Hence, the correct answer is: **Set up security rules that block SQL injection and cross-site scripting attacks in AWS Web Application Firewall (AWS WAF). Associate the rules to the Application Load Balancer.**

**Why the other options are wrong:**

- **Using AWS X-Ray to detect and block SQL injection and cross-site scripting attacks** is incorrect. X-Ray is a distributed tracing and observability tool used to profile latency and debug request paths across microservices. It is read-only telemetry; it cannot inspect request payloads for attack signatures, and it has no enforcement (block) capability whatsoever.
- **Using AWS Firewall Manager to set up security rules ... then associating the rules to the Application Load Balancer** is incorrect. Firewall Manager is a central management layer for applying WAF, Shield Advanced, and security-group policies across many accounts in an AWS Organization. It does not inspect traffic itself; the actual SQLi/XSS filtering is still performed by AWS WAF. For a single ALB it adds needless overhead, and the wording implies Firewall Manager does the blocking, which it does not.
- **Blocking all the IP addresses where the attacks originated using the Network Access Control List** is incorrect. A NACL is a stateless, subnet-level filter operating at Layers 3/4 (IP, port, protocol). It cannot read HTTP payloads, so it cannot tell a malicious SQLi request from a legitimate one arriving on the same port (443). Attackers also rotate source IPs, making IP blocklists ineffective.

**References:**

[https://aws.amazon.com/waf/](https://aws.amazon.com/waf/)

[https://docs.aws.amazon.com/waf/latest/developerguide/what-is-aws-waf.html](https://docs.aws.amazon.com/waf/latest/developerguide/what-is-aws-waf.html)

**Domain:** Design Secure Architectures
`);

console.log('Q1 done');
fs.writeFileSync(path, s);
