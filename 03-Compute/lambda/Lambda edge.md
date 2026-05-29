# 📘 Lambda@Edge - Complete Deep Dive for SAA-C03

> Lambda@Edge is one of the **most misunderstood** services on the SAA-C03 exam. It's essentially AWS Lambda **extended to run at CloudFront edge locations** across the globe. Understanding where it fits (and where it DOESN'T fit) is critical for exam success.

See also: [Lambda intro](Lambda%20intro.md) · [Lambda Core Concepts & Architecture](Lambda%20Core%20Concepts%20%26%20Architecture.md) · [Lambda Invocation Modes](Lambda%20Invocation%20Modes.md) · [Lambda Cold Starts & Performance](Lambda%20Cold%20Starts%20%26%20Performance.md) · [Lambda Concurrency & Scaling](Lambda%20Concurrency%20%26%20Scaling.md) · [Lambda Scenario Questions](Lambda%20Scenario%20Questions.md)

---

## Table of Contents

- [🎯 Core Concept: What is Lambda@Edge?](#-core-concept-what-is-lambdaedge)
- [⚡ Lambda@Edge vs CloudFront Functions - CRITICAL for Exam](#-lambdaedge-vs-cloudfront-functions---critical-for-exam)
- [🚫 Lambda@Edge Limitations (CONSTANT Exam Trap)](#-lambdaedge-limitations-constant-exam-trap)
- [🎯 Real-World Use Cases for Lambda@Edge](#-real-world-use-cases-for-lambdaedge)
- [📊 Lambda@Edge Use Cases Summary](#-lambdaedge-use-cases-summary)
- [📝 SAA-C03 Exam Question Bank](#-saa-c03-exam-question-bank)
- [📊 Quick Reference for Exam Day](#-quick-reference-for-exam-day)
- [🏗️ Architecture Patterns Summary](#-architecture-patterns-summary)

---

## 🎯 Core Concept: What is Lambda@Edge?

**Lambda@Edge is a Lambda function that runs at CloudFront edge locations** instead of in your primary AWS region.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HOW LAMBDA@EDGE WORKS                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   You write Lambda function in us-east-1                                    │
│                    │                                                        │
│                    ▼                                                        │
│   Lambda@Edge automatically REPLICATES to all edge locations                │
│                    │                                                        │
│                    ▼                                                        │
│   Edge locations (New York, London, Tokyo, Sydney, Sao Paulo, etc.)         │
│                    │                                                        │
│                    ▼                                                        │
│   Function runs CLOSE to your users (minimizes latency)                     │
│                                                                             │
│   Key Insight: The function travels WITH CloudFront to wherever users are   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Source**: AWS official documentation states "Lambda@Edge is an extension of Lambda that provides powerful and flexible computation for complex functions, bringing complete application logic closer to your viewers".

---

[⬆ Back to top](#table-of-contents)

## ⚡ Lambda@Edge vs CloudFront Functions - CRITICAL for Exam

This comparison appears on the exam **frequently**. You MUST know when to use which.

| Aspect | CloudFront Functions | Lambda@Edge |
|--------|---------------------|-------------|
| **Programming languages** | JavaScript (ECMAScript 5.1) | Node.js **and** Python |
| **Event triggers** | Viewer Request, Viewer Response | Viewer Request, Viewer Response, **Origin Request, Origin Response** |
| **Scale** | 10,000,000+ requests/second | Up to 10,000 requests/second per region |
| **Function duration** | Sub-millisecond | 5 seconds (viewer events) or 30 seconds (origin events) |
| **Max memory** | 2 MB | 128 MB - 3,008 MB |
| **Code + libs max size** | 10 KB | 1 MB (viewer) or 50 MB (origin) |
| **Network access** | ❌ No | ✅ Yes |
| **File system access** | ❌ No | ✅ Yes |
| **Access request body** | ❌ No | ✅ Yes |
| **Can test in CloudFront console** | ✅ Yes | ❌ No |
| **Pricing** | Free tier + per request | No free tier; per request + duration |

### The 4 Lambda@Edge Event Triggers

Based on AWS CDK documentation, Lambda@Edge can be triggered at four points in the request/response lifecycle:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LAMBDA@EDGE EVENT TRIGGERS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│Viewer ──► [VIEWER REQUEST] ──►CloudFront Cache──► [ORIGIN REQUEST] ──► Origin
│                     │                              │
│                     ▼                              ▼
│   Viewer ◄── [VIEWER RESPONSE] ◄─────────────────── [ORIGIN RESPONSE] ◄─────┘
│
│
│   VIEWER REQUEST (runs before CloudFront cache check)
│   └── Use: URL rewrites, redirects, auth checks, add/remove headers
│
│   ORIGIN REQUEST (runs when request MISSES cache, before hitting origin)
│   └── Use: Modify origin request, change origin based on logic
│
│   ORIGIN RESPONSE (runs after origin responds, before caching)
│   └── Use: Modify response from origin, add headers, transform content
│
│   VIEWER RESPONSE (runs before returning to viewer)
│   └── Use: Modify final response, add security headers
│
└─────────────────────────────────────────────────────────────────────────────┘
```

**Source**: AWS CDK API documentation lists these four event types as `VIEWER_REQUEST`, `VIEWER_RESPONSE`, `ORIGIN_REQUEST`, and `ORIGIN_RESPONSE`.

---

[⬆ Back to top](#table-of-contents)

## 🚫 Lambda@Edge Limitations (CONSTANT Exam Trap)

Many of these limitations are **exam favorites** because they're counterintuitive. Official AWS documentation lists them explicitly.

### 1. Function Must Be in us-east-1

**The Lambda function MUST be created in `us-east-1` (N. Virginia)**. Lambda@Edge automatically replicates it to edge locations, but the source function lives in us-east-1.

**Exam Trap**: "A developer creates a Lambda@Edge function in eu-west-1 and can't attach it to CloudFront distribution." → WRONG REGION.

### 2. Must Use Numbered Versions, NOT $LATEST

You cannot associate `$LATEST` or an alias with CloudFront. You must use a **published version number** (e.g., `function:42`).

**Exam Trap**: "Why can't I attach my Lambda function to CloudFront?" → You're using `$LATEST` instead of a numbered version.

### 3. IAM Role Must Trust TWO Principals

The execution role must be assumable by BOTH:

- `lambda.amazonaws.com`
- `edgelambda.amazonaws.com`

### 4. What Lambda@Edge Does NOT Support

According to AWS documentation:

| Feature | Support |
|---------|---------|
| Lambda environment variables | ❌ No (except reserved variables) |
| VPC access | ❌ No |
| Provisioned Concurrency | ❌ No |
| Auto (default) runtime config only | ✅ Only default |
| Ephemeral storage >512 MB | ❌ No |

**Source**: AWS Lambda@Edge restrictions page explicitly states "Lambda@Edge does not support Lambda functions configured to access resources in your VPC".

### 5. Request Body Size Limits

When accessing or modifying request bodies:

| Event Type | Max Body Size |
|------------|---------------|
| **Viewer Request** (read access) | 40 KB |
| **Origin Request** (read access) | 1 MB |
| **Viewer Request** (replace body) | 40 KB (plain) / 53.2 KB (base64) |
| **Origin Request** (replace body) | 1 MB (plain) / 1.33 MB (base64) |

**Exam Trap**: "Lambda@Edge function processes 2 MB request body" → Exceeds limit, will fail with HTTP 502.

---

[⬆ Back to top](#table-of-contents)

## 🎯 Real-World Use Cases for Lambda@Edge

### Use Case 1: Dynamic Image Resizing (HIGH PROBABILITY)

This is the **most common Lambda@Edge exam scenario**.

**Scenario**: "A social media company has over a billion images in S3 and processes thousands each second. They need to resize images dynamically and serve appropriate formats to clients."

**Solution**: Lambda@Edge function with image processing library associated with CloudFront behaviors.

**Why This Works**:

- Processing happens at edge (close to users) → lower latency
- No need to maintain EC2 instances for image processing
- Scales automatically with CloudFront

**Exam Discussion Validation**: "The moment there is a need to implement some logic at the CDN think Lambda@Edge".

**Correct Answer Pattern** (from exam discussion):
> "Using a Lambda@Edge function with an external image management library is the best solution to resize the images dynamically and serve appropriate formats to clients. Lambda@Edge allows running custom code in response to CloudFront events, such as viewer requests and origin requests. It has built-in support for external libraries that can be used to process images. This approach reduces operational overhead and scales automatically with traffic."

---

### Use Case 2: A/B Testing (Origin Request Pattern)

This scenario appears in AWS re:Post discussions.

**Concept**: Route a percentage of traffic to a different origin (e.g., beta S3 bucket) while preserving user experience with cookies.

**Viewer Request Function** (assigns user to experiment):

```javascript
// Viewer Request: Assign user to A or B group
const sourceCoookie = 'X-Source';
const sourceMain = 'main-bucket.s3-website-us-east-1.amazonaws.com';
const sourceExperiment = 'beta-bucket.s3-website-us-east-1.amazonaws.com';
const experimentTraffic = 0.5;  // 50% of users see beta

exports.handler = (event, context, callback) => {
    const request = event.Records[0].cf.request;
    const headers = request.headers;

    // If user already has a source cookie, use that
    if (headers.cookie) {
        for (let i = 0; i < headers.cookie.length; i++) {        
            if (headers.cookie[i].value.indexOf(sourceCoookie) >= 0) {
                callback(null, request);  // Forward unchanged
                return;
            }         
        }       
    }

    // Otherwise, randomly assign to Main or Experiment
    const source = (Math.random() < experimentTraffic) ? sourceExperiment : sourceMain;
    
    // Add cookie so user stays in same group for future requests
    const cookie = `${sourceCoookie}=${source}`;
    headers.cookie = headers.cookie || [];
    headers.cookie.push({ key:'Cookie', value: cookie });

    callback(null, request);
};
```

**Origin Request Function** (routes to correct origin):

```javascript
// Origin Request: Change origin based on cookie
exports.handler = (event, context, callback) => {
    const request = event.Records[0].cf.request;
    
    // Check if user should go to experiment bucket
    if (request.headers.cookie?.some(c => 
        c.value.includes('X-Source=beta-bucket.s3-website-us-east-1.amazonaws.com'))) {
        
        // Change origin to experiment bucket
        request.origin = {
            s3: {
                domainName: 'beta-bucket.s3-website-us-east-1.amazonaws.com',
                region: 'us-east-1'
            }
        };
        headers['host'] = [{key: 'host', value: 'beta-bucket.s3-website-us-east-1.amazonaws.com'}];
    }
    // Otherwise, request goes to main origin by default

    callback(null, request);
};
```

**Source**: AWS re:Post contains this exact A/B testing pattern using Viewer Request and Origin Request triggers.

---

### Use Case 3: Request Authorization (JWT Validation)

CloudFront Functions can also handle this for simple cases, but Lambda@Edge is needed for complex token validation.

**Use case**: Validate JSON Web Tokens (JWTs) at the edge before requests reach your origin.

**Why Lambda@Edge**:

- Can make network calls to validate tokens
- Can access external libraries for JWT parsing
- Can handle complex validation logic

**Source**: AWS documentation explicitly lists "request authorization" as a CloudFront Functions use case for simple JWTs, but Lambda@Edge for more complex scenarios.

---

### Use Case 4: Origin Failover with Lambda@Edge (What NOT to do)

**Common Exam Trap**: Some might think Lambda@Edge can handle origin failover. It CANNOT be configured as an origin.

**Correct Approach for HA**: Use CloudFront **Origin Groups** with multiple EC2 instances across Availability Zones, NOT Lambda@Edge.

**Exam Discussion Clarification**:
> "Lambda@Edge is not an origin. Lambda@Edge runs at CloudFront edge locations to customize requests and responses, enforce security, or add business logic closer to users, but it cannot host or serve your application's dynamic content. It cannot be configured as a member of an origin group, since origin groups are strictly for actual origins like EC2, ALB, or S3."

---

[⬆ Back to top](#table-of-contents)

## 📊 Lambda@Edge Use Cases Summary

| Use Case | Event Trigger | Why Lambda@Edge |
|----------|---------------|-----------------|
| Image optimization (resize, format conversion) | Origin Request | Needs external libraries, can access request body |
| A/B testing with different origins | Viewer Request + Origin Request | Needs to modify origin based on cookie |
| Authentication/authorization (complex) | Viewer Request | Can make network calls to validate tokens |
| Response header modification (CORS, security) | Origin Response / Viewer Response | Simple use case; CloudFront Functions may suffice for some |
| URL rewrite/redirect | Viewer Request | For complex pattern matching; CloudFront Functions for simple |
| Content transformation (e.g., HTML injection) | Origin Response | Can modify response body |
| Geo-targeting (serve different content by country) | Viewer Request | Can access viewer location |

---

[⬆ Back to top](#table-of-contents)

## 📝 SAA-C03 Exam Question Bank

### Question 1: Dynamic Image Resizing (HIGH PROBABILITY)

**Scenario**: A social media company runs its application on EC2 instances behind an ALB. The ALB is the origin for a CloudFront distribution. The application has over a billion images stored in S3 and processes thousands of images each second. The company needs to resize images dynamically and serve appropriate formats to clients.

**Question**: Which solution meets these requirements with the LEAST operational overhead?

**Options**:
A. Install an external image management library on an EC2 instance. Use the library to process images.

B. Create a CloudFront origin request policy. Use the policy to automatically resize images based on User-Agent headers.

C. Use a Lambda@Edge function with an external image management library. Associate it with CloudFront behaviors serving the images.

D. Create a CloudFront response headers policy. Use it to automatically resize images based on User-Agent headers.

**Answer**: C

**Explanation**:

- Lambda@Edge runs at edge locations (close to users), reducing latency
- External libraries can be included for image processing
- No servers to manage → least operational overhead
- CloudFront policies cannot process images (Options B and D are impossible)
- EC2 approach adds management overhead (Option A)

**Exam Discussion**: "Using a Lambda@Edge function with an external image management library is the best solution to resize the images dynamically... This approach will reduce operational overhead and scale automatically with traffic."

---

### Question 2: What Lambda@Edge Cannot Do (Origin HA)

**Scenario**: A company wants to launch a web application globally through CloudFront. The application has dynamic content served from EC2 instances. The company needs high availability for the origin infrastructure.

**Question**: What should the solutions architect do to ensure high origin availability?

**Options**:
A. Use a single EC2 instance as the origin. Configure Lambda@Edge to fail over to a backup instance.

B. Use Lambda@Edge functions as the origin for all dynamic requests.

C. Provision two EC2 instances in different Availability Zones. Configure them as part of a CloudFront origin group.

D. Configure Lambda@Edge to cache all dynamic content at edge locations.

**Answer**: C

**Explanation**:

- Lambda@Edge is NOT an origin and cannot be configured in an origin group
- Origin groups with multiple EC2 instances across AZs provide HA
- Option A is incorrect because Lambda@Edge doesn't handle origin failover this way
- Option D is impossible; dynamic content still needs an origin

**Exam Discussion Confirmation**: "Lambda@Edge is not an origin. It cannot be configured as a member of an origin group, since origin groups are strictly for actual origins like EC2, ALB, or S3."

---

### Question 3: CloudFront Functions vs Lambda@Edge (Exam Favorite)

**Scenario**: A company serves a static website from S3 through CloudFront. They need to add security headers (like `X-Frame-Options`) to all responses before they reach viewers. The function should have minimal latency impact.

**Question**: Which solution is MOST cost-effective and has the lowest latency?

**Options**:
A. Create a Lambda@Edge function triggered by origin response to add headers.

B. Create a CloudFront function triggered by viewer response to add headers.

C. Modify the S3 objects to include headers as metadata.

D. Use an Application Load Balancer in front of S3 to add headers.

**Answer**: B

**Explanation**:

- CloudFront Functions have sub-millisecond latency
- CloudFront Functions are cheaper (have free tier)
- Header manipulation is a SIMPLE use case that doesn't need Lambda@Edge complexity
- Option C: S3 object metadata doesn't become HTTP response headers
- Option D adds unnecessary complexity and cost

**Exam Discussion Connection**: The official documentation explicitly lists "header manipulation" as a CloudFront Functions use case.

---

### Question 4: Request Body Size Limits (Technical Trap)

**Scenario**: A company uses Lambda@Edge to modify request bodies before they reach an S3 origin. The average request body size is 50 KB, and the peak is 200 KB. Some requests require up to 1.2 MB of data.

**Question**: What is the limitation the architect must consider?

**Options**:
A. Lambda@Edge viewer request events can only access up to 40 KB of request body.

B. Lambda@Edge functions cannot access request bodies at all.

C. Lambda@Edge only works with request bodies under 10 KB.

D. There are no limits on request body size for Lambda@Edge.

**Answer**: A

**Explanation**:

- Viewer request events truncate request bodies at 40 KB
- Origin request events can access up to 1 MB
- 1.2 MB exceeds the origin request limit as well

**Technical Detail from AWS**: "For viewer request events, the body is truncated at 40 KB. For origin request events, the body is truncated at 1 MB."

---

### Question 5: A/B Testing with Lambda@Edge

**Scenario**: A company wants to test a new website design. 10% of users should see the new design, while 90% see the current design. Users should consistently see the same design across sessions. The website is served from two different S3 buckets behind CloudFront.

**Question**: Which combination of Lambda@Edge triggers should be used?

**Options**:
A. Viewer request only, to randomly assign users each time

B. Origin request only, to change the origin bucket

C. Viewer request to assign a cookie, AND origin request to read the cookie and change origin

D. Viewer response only, to modify the HTML after origin response

**Answer**: C

**Explanation**:

- Viewer request assigns user to A/B group and sets a cookie
- Origin request reads the cookie and routes to correct S3 bucket
- Two functions are needed: one for assignment, one for routing
- Option A would assign users randomly each request (inconsistent experience)

**AWS re:Post Pattern**: "You create two Lambda@Edge functions: one associated with viewer request event to assign users, and one associated with origin request event to route based on the cookie."

---

### Question 6: IAM Role Requirements (Configuration Trap)

**Scenario**: A solutions architect is creating a Lambda@Edge function. After creating the function, it cannot be associated with CloudFront.

**Question**: What is the MOST likely cause?

**Options**:
A. The function is in `us-west-2` region.

B. The IAM execution role does not allow `edgelambda.amazonaws.com` as a trusted entity.

C. The function uses Python 3.12 runtime.

D. The function has 256 MB of memory configured.

**Answer**: B

**Explanation**:

- The IAM role must allow BOTH `lambda.amazonaws.com` AND `edgelambda.amazonaws.com`
- Lambda@Edge functions MUST be in `us-east-1` (Option A would be correct if function was in `us-west-2`, but it's asking for MOST likely; both could be issues, but B is often overlooked)
- Python is supported
- 256 MB is allowed (128 MB - 3008 MB)

---

[⬆ Back to top](#table-of-contents)

## 📊 Quick Reference for Exam Day

| If the exam question mentions... | Think... |
|--------------------------------|----------|
| "Dynamic image resizing at CDN" | Lambda@Edge with external library |
| "Header modification only" | CloudFront Functions (cheaper, faster) |
| "URL redirect/rewrite" | CloudFront Functions for simple; Lambda@Edge for complex |
| "JWT validation at edge" | CloudFront Functions for simple; Lambda@Edge for complex |
| "Can't attach function to CloudFront" | Check region (`us-east-1`) OR using `$LATEST` instead of numbered version |
| "Modify request body before origin" | Lambda@Edge (Origin Request) |
| "Function accessing network/file system" | Lambda@Edge (CloudFront Functions cannot) |
| "High origin availability" | Origin group with multiple origins (NOT Lambda@Edge) |
| "A/B testing with different origins" | Viewer Request + Origin Request Lambda@Edge functions |
| "50 KB request body" | Use Origin Request (1 MB limit), NOT Viewer Request (40 KB limit) |
| "Sub-millisecond latency required" | CloudFront Functions |

---

[⬆ Back to top](#table-of-contents)

## 🏗️ Architecture Patterns Summary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMPLETE LAMBDA@EDGE ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   USER ──► CloudFront Distribution                                          │
│                 │                                                           │
│                 ├── [VIEWER REQUEST] Lambda@Edge: Auth check, A/B assign    │
│                 │                                                           │
│                 ├── [CloudFront Cache]                                      │
│                 │                                                           │
│                 ├── [ORIGIN REQUEST] Lambda@Edge: Modify origin, transform  │
│                 │                                                           │
│                 ▼                                                           │
│            Origin (S3/ALB/EC2)                                              │
│                 │                                                           │
│                 ├── [ORIGIN RESPONSE] Lambda@Edge: Add headers, transform   │
│                 │                                                           │
│                 ├── [Cache Storage]                                         │
│                 │                                                           │
│                 └── [VIEWER RESPONSE] Lambda@Edge: Final modifications      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Exam Patterns**:

1. **Image processing** → `ORIGIN_REQUEST` or `ORIGIN_RESPONSE`
2. **A/B testing** → `VIEWER_REQUEST` (assign) + `ORIGIN_REQUEST` (route)
3. **Auth/headers** → `VIEWER_REQUEST` (check) + `VIEWER_RESPONSE` (add)
4. **Content transformation** → `ORIGIN_RESPONSE`

---

[⬆ Back to top](#table-of-contents)
