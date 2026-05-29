## Anycast

**Anycast** is a networking technique where the **same IP address is assigned to multiple servers in different locations** around the world.

When a user sends a request to that IP:

- the internet routing system (**BGP**) automatically sends the request to the **nearest or best available server**.

Example:

- A DNS service may have servers in:
  - India
  - Singapore
  - US
  - Europe

All servers share the same IP address using anycast.

If you query that IP from Chennai, your request may go to the Singapore or India server because it is closest.

Common uses of anycast:
- DNS services
- CDNs
- DDoS protection
- Global load balancing

Benefits:
- Faster response times
- High availability
- Better fault tolerance
- Traffic distribution across regions

Real-world examples:
- Cloudflare DNS
- Google Public DNS (`8.8.8.8`)
- Amazon Route 53

Simple analogy:
- Imagine one customer care phone number connected to call centers in many cities.
- When you call, the telecom network automatically connects you to the nearest center.
- That is similar to how anycast works.

## Anycast - AWS Route 53

Amazon Web Services Amazon Route 53 uses an **anycast-based global DNS infrastructure** for its authoritative nameservers.

- When you create a hosted zone in Route 53, AWS assigns nameservers like:
  - `ns-123.awsdns-45.com`
  - `ns-678.awsdns-90.net`
- These nameservers are part of a globally distributed anycast network.
- With **anycast**, the same IP address is advertised from multiple geographic locations.
- DNS queries automatically route to the nearest or best-performing AWS edge location via BGP routing.

Benefits:

- Lower DNS lookup latency
- High availability
- DDoS resilience
- Automatic failover

AWS documentation:

- [Amazon Route 53 Developer Guide](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html?utm_source=chatgpt.com)
- [Route 53 FAQ](https://aws.amazon.com/route53/faqs)

One important clarification:

- The **hostnames** (`ns-xxxx.awsdns-xx.org`) are different per hosted zone,
- but the underlying Route 53 infrastructure uses globally distributed anycast routing.
