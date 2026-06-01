# Amazon Elastic Transcoder - Exam Scenarios

> Exam focus: recognise _file/VOD transcoding to multiple device formats_, the Pipeline/Job/Preset model, HLS adaptive bitrate, event-driven transcoding, and when MediaConvert/MediaLive/Kinesis Video Streams is the better pick. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - Amazon Elastic Transcoder Intro bits & bytes](01%20-%20Amazon%20Elastic%20Transcoder%20Intro%20bits%20%26%20bytes.md) · [02 - Amazon Elastic Transcoder Deep Dive](02%20-%20Amazon%20Elastic%20Transcoder%20Deep%20Dive.md) · [04 - Amazon Elastic Transcoder SRE Operations](04%20-%20Amazon%20Elastic%20Transcoder%20SRE%20Operations.md) · [00 - Media Services Overview](00%20-%20Media%20Services%20Overview.md)

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

- **File/VOD transcoding** to multiple device renditions → Elastic Transcoder (or MediaConvert).
- **HLS adaptive bitrate** for web/mobile players.
- **Event-driven**: S3 upload → Lambda → CreateJob → SNS on completion.
- Inputs and outputs are always in **S3**; delivery via **CloudFront**.
- **Live ≠ Elastic Transcoder** (that's MediaLive); **device/IoT streams ≠ Elastic Transcoder** (that's Kinesis Video Streams).
- MediaConvert is the **AWS-recommended modern** file transcoder.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                                             | Points to                             |
| :----------------------------------------------------------------- | :------------------------------------ |
| "convert uploaded videos to multiple formats/resolutions"          | **Elastic Transcoder / MediaConvert** |
| "adaptive bitrate / smooth playback on any network"                | **HLS** output (ABR ladder)           |
| "transcode automatically when a file is uploaded"                  | **S3 event → Lambda → CreateJob**     |
| "notify when transcoding completes"                                | **SNS** pipeline notifications        |
| "newest codecs (HEVC), professional formats, DRM, AWS-recommended" | **MediaConvert**                      |
| "encode a live broadcast / 24x7 channel"                           | **MediaLive**                         |
| "ingest video from cameras/phones/IoT for ML or playback"          | **Kinesis Video Streams**             |
| "deliver renditions globally with low latency"                     | **CloudFront**                        |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Choosing **MediaLive** for _file_ transcoding (MediaLive is live).
- Choosing **Kinesis Video Streams** for _file_ transcoding (KVS ingests streams, doesn't transcode files to renditions).
- Suggesting **EC2 + FFmpeg** when a managed service is clearly wanted (more ops burden).
- Forgetting outputs must go to **S3** and be delivered via **CloudFront**, not served from the transcoder.
- Picking **Elastic Transcoder** when the question stresses modern codecs/DRM → **MediaConvert**.

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **"File / uploaded / VOD" transcode?** → Elastic Transcoder or MediaConvert (modern/DRM → MediaConvert).
2. **"Live / broadcast / channel"?** → MediaLive (eliminate Elastic Transcoder).
3. **"From devices/cameras/IoT, for ML/playback"?** → Kinesis Video Streams.
4. **"Adaptive / any device / any bandwidth"?** → HLS renditions (ABR).
5. **"Automatically on upload"?** → S3 event → Lambda → CreateJob.
6. **"Global delivery"?** → CloudFront in front of the S3 output bucket.

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** Users upload `.mov` files that must play on phones, tablets, and browsers with smooth quality switching.
**Options:** A) MediaLive B) Elastic Transcoder producing HLS to S3 + CloudFront C) Kinesis Video Streams D) S3 only
**Correct:** B
**Explanation:** File/VOD → transcode to HLS ABR renditions, deliver via CloudFront.

### Q2

**Scenario:** What three constructs define an Elastic Transcoder workflow?
**Options:** A) Stream/Shard/Consumer B) Pipeline/Job/Preset C) Stack/Change Set/Template D) Topic/Queue/Subscription
**Correct:** B
**Explanation:** Pipeline (queue), Job (task), Preset (recipe).

### Q3

**Scenario:** Transcoding must start automatically when a video is uploaded to S3.
**Options:** A) Cron on EC2 B) S3 Event Notification → Lambda → CreateJob C) Manual console D) Step Functions polling
**Correct:** B
**Explanation:** Event-driven, serverless trigger.

### Q4

**Scenario:** The team needs to be notified when each job finishes or errors.
**Options:** A) Poll the API B) Pipeline SNS notifications C) CloudFront logs D) S3 inventory
**Correct:** B
**Explanation:** SNS publishes job-state changes.

### Q5

**Scenario:** A new project needs HEVC output and DASH packaging with DRM.
**Options:** A) Elastic Transcoder B) MediaConvert C) MediaLive D) KVS
**Correct:** B
**Explanation:** Modern codecs/DASH/DRM → MediaConvert.

### Q6

**Scenario:** Where must input and output media live?
**Options:** A) EBS B) S3 buckets bound to the pipeline C) EFS D) DynamoDB
**Correct:** B
**Explanation:** Elastic Transcoder reads from and writes to S3.

### Q7

**Scenario:** A 24x7 live sports channel must be encoded for streaming.
**Options:** A) Elastic Transcoder B) MediaLive C) MediaConvert D) KVS
**Correct:** B
**Explanation:** Live encoding → MediaLive.

### Q8

**Scenario:** Security cameras stream to AWS for later playback and ML analysis.
**Options:** A) Elastic Transcoder B) Kinesis Video Streams C) MediaConvert D) S3 upload
**Correct:** B
**Explanation:** Device/stream ingestion → KVS.

### Q9

**Scenario:** Output renditions must reach a global audience with low latency and caching.
**Options:** A) Serve from the transcoder B) CloudFront in front of the S3 output bucket C) Public S3 website D) EC2 origin
**Correct:** B
**Explanation:** CloudFront caches and delivers globally.

### Q10

**Scenario:** Premium content must not be downloadable directly from S3.
**Options:** A) Public bucket B) Private output bucket + CloudFront OAC + signed URLs C) Bucket ACL public-read D) Pre-signed forever
**Correct:** B
**Explanation:** Keep bucket private; gate via CloudFront signed URLs.

### Q11

**Scenario:** You must reduce transcoding cost.
**Options:** A) Generate every possible rendition B) Produce only renditions your audience devices use C) Always 4K D) Disable CloudFront
**Correct:** B
**Explanation:** Billed per output minute - don't make renditions nobody plays.

### Q12

**Scenario:** Throughput is too low; jobs queue behind each other.
**Options:** A) Bigger EC2 B) Add more pipelines / increase concurrency C) Smaller bucket D) Use EFS
**Correct:** B
**Explanation:** Parallelism comes from additional pipelines/job concurrency.

### Q13

**Scenario:** A reusable output recipe (codec, resolution, bitrate) is needed across many jobs.
**Options:** A) Pipeline B) Preset C) Job D) Topic
**Correct:** B
**Explanation:** Presets are reusable output templates.

### Q14

**Scenario:** You need thumbnails for a video scrubbing UI.
**Options:** A) Separate Lambda only B) Configure thumbnail generation in the job/preset C) Rekognition D) Not possible
**Correct:** B
**Explanation:** Elastic Transcoder can emit thumbnails at intervals.

### Q15

**Scenario:** Encrypt transcoded outputs with a customer-managed key.
**Options:** A) No encryption B) SSE-KMS on the output (pipeline KMS config) C) Only HTTPS D) Client app encrypts
**Correct:** B
**Explanation:** Use KMS for at-rest encryption of outputs.

### Q16

**Scenario:** A multi-step flow: validate → transcode → publish → notify, with retries.
**Options:** A) One big Lambda B) Step Functions orchestrating the steps C) Cron D) Manual
**Correct:** B
**Explanation:** Step Functions coordinates and retries multi-step pipelines.

### Q17

**Scenario:** Large existing media library on-prem must be processed in AWS.
**Options:** A) Email files B) DataSync/Snowball to S3, then transcode C) FTP one by one D) Re-shoot
**Correct:** B
**Explanation:** Bulk-ingest to S3 first (DataSync/Snow), then transcode.

### Q18

**Scenario:** Player should switch quality based on bandwidth.
**Options:** A) Single MP4 B) HLS with a multi-rendition bitrate ladder C) WebM only D) Raw file
**Correct:** B
**Explanation:** ABR via HLS bitrate ladder.

### Q19

**Scenario:** Audit who created/deleted transcoding pipelines.
**Options:** A) SNS B) CloudTrail C) CloudFront logs D) S3 access logs
**Correct:** B
**Explanation:** CloudTrail records control-plane API calls.

### Q20

**Scenario:** A file is already in the correct format and just needs global delivery.
**Options:** A) Elastic Transcoder B) S3 + CloudFront (no transcode) C) MediaLive D) KVS
**Correct:** B
**Explanation:** No transcoding needed - just store and deliver.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** A media startup wants a fully serverless VOD pipeline that scales from 0 with no idle cost, auto-transcodes uploads to ABR, and notifies a database on completion.
**Options:** A) EC2 Auto Scaling + FFmpeg B) S3 upload → Lambda → Elastic Transcoder/MediaConvert job → SNS → Lambda updates DynamoDB; deliver via CloudFront C) ECS cluster always-on D) Batch nightly
**Correct:** B
**Explanation:** Event-driven, pay-per-use, no idle servers, completion fan-out via SNS.

### H2

**Scenario:** The platform is being modernised: they need HEVC for bandwidth savings, DASH+HLS via CMAF, and studio DRM. Which service and why?
**Options:** A) Elastic Transcoder (HLS AES-128) B) MediaConvert (HEVC, CMAF, SPEKE DRM) C) MediaLive D) KVS
**Correct:** B
**Explanation:** Elastic Transcoder lacks HEVC/CMAF/full DRM; MediaConvert is the modern VOD service.

### H3

**Scenario:** Costs are climbing because every upload generates 6 renditions but analytics show 95% of plays use 3 of them.
**Options:** A) Add more renditions B) Trim the bitrate ladder to the renditions actually played; lifecycle-expire unused outputs C) Switch to MediaLive D) Disable CloudFront
**Correct:** B
**Explanation:** Per-output-minute billing - prune the ladder and clean up unused renditions.

### H4

**Scenario:** Premium subscribers only; content must never be fetched directly from S3 and links must expire per user.
**Options:** A) Public bucket B) Private bucket + CloudFront OAC + signed URLs/cookies; optionally HLS AES-128 C) Pre-signed S3 URL valid 1 year D) IP allowlist only
**Correct:** B
**Explanation:** OAC keeps bucket private; signed URLs/cookies enforce per-user, time-bound access.

### H5

**Scenario:** Throughput must handle bursts of thousands of uploads without unbounded queue growth, and failed jobs must be retried/quarantined.
**Options:** A) One pipeline, ignore errors B) Multiple pipelines for parallelism + SNS Error → DLQ/retry workflow + backpressure via SQS C) Bigger EC2 D) Synchronous calls
**Correct:** B
**Explanation:** Scale with pipelines, decouple with SQS, handle failures via SNS error → DLQ/retry.

### H6

**Scenario:** Compliance requires all source masters and renditions encrypted with a key the security team controls, with audit of access.
**Options:** A) SSE-S3 B) SSE-KMS (CMK owned by security) on input/output + CloudTrail data events C) No encryption D) Client-side only, no audit
**Correct:** B
**Explanation:** Customer-managed KMS key + CloudTrail gives controlled, audited encryption.

### H7

**Scenario:** A regional outage concern: the team wants the VOD library and pipeline resilient across regions.
**Options:** A) Single region only B) S3 Cross-Region Replication of masters + IaC pipelines/presets re-deployable in a second region; re-transcode from masters C) EBS snapshots D) Nothing
**Correct:** B
**Explanation:** Keep masters replicated and pipelines as code so you can re-run transcoding in another region.

### H8

**Scenario:** Elastic Transcoder isn't available in the team's required region and they need broad format support.
**Options:** A) Force a non-supported region B) Use MediaConvert (broader region/format coverage) C) Run FFmpeg on Lambda only D) Give up
**Correct:** B
**Explanation:** Elastic Transcoder has limited regional availability; MediaConvert covers more regions/formats.

### H9

**Scenario:** A pipeline orchestration must validate input codec, transcode, generate thumbnails, run content moderation, then publish - with visibility into each step.
**Options:** A) One monolith Lambda B) Step Functions: validate → transcode (ET/MediaConvert) → Rekognition moderation → publish, with per-step retries C) Cron chain D) Manual review
**Correct:** B
**Explanation:** Step Functions gives orchestration, retries, and visibility across heterogeneous steps.

### H10

**Scenario:** Live event must be encoded AND a VOD archive produced for on-demand replay afterward.
**Options:** A) Elastic Transcoder for both B) MediaLive for the live encode + archive to S3, then MediaConvert/Elastic Transcoder for VOD renditions C) KVS for both D) CloudFront only
**Correct:** B
**Explanation:** Live → MediaLive; the recorded archive is then transcoded for VOD - different tools for live vs file.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **File/VOD transcode to many device formats → Elastic Transcoder (Pipeline→Job→Preset), output HLS to S3, deliver via CloudFront. Modern codecs/DRM/DASH → MediaConvert. Live → MediaLive. Device/camera ingestion → Kinesis Video Streams. Trigger on S3 upload via Lambda; notify via SNS.**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - Amazon Elastic Transcoder SRE Operations](04%20-%20Amazon%20Elastic%20Transcoder%20SRE%20Operations.md).
