# Amazon Kinesis Video Streams - Exam Scenarios

> Exam focus: recognise _streaming media ingestion from devices for storage/playback/ML_, the durable-streaming vs **WebRTC** distinction, the Rekognition Video pipeline, and not confusing KVS with Kinesis **Data** Streams or with file transcoders. Keywords, distractors, elimination, and **20 medium + 10 hard** scenarios.

See also: [01 - Amazon Kinesis Video Streams Intro bits & bytes](01%20-%20Amazon%20Kinesis%20Video%20Streams%20Intro%20bits%20%26%20bytes.md) · [02 - Amazon Kinesis Video Streams Deep Dive](02%20-%20Amazon%20Kinesis%20Video%20Streams%20Deep%20Dive.md) · [04 - Amazon Kinesis Video Streams SRE Operations](04%20-%20Amazon%20Kinesis%20Video%20Streams%20SRE%20Operations.md) · [00 - Media Services Overview](00%20-%20Media%20Services%20Overview.md)

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

- **Ingest live media from many devices** → KVS (durable streaming).
- **Sub-second, two-way live** → **KVS WebRTC** (no storage, peer-to-peer).
- **Time-indexed replay** by timestamp (fragments).
- **Real-time video analytics** → KVS → **Rekognition Video** → Kinesis Data Streams → Lambda.
- KVS ≠ **Kinesis Data Streams** (generic records) and ≠ **Elastic Transcoder/MediaConvert** (file transcode).
- **KMS encryption** of streams by default.

[⬆ Back to top](#table-of-contents)

---

## 2. Keywords AWS Uses

| Phrase                                                  | Points to                             |
| :------------------------------------------------------ | :------------------------------------ |
| "ingest video from millions of cameras/devices"         | **Kinesis Video Streams**             |
| "store and replay video by time / time-indexed"         | **KVS durable streaming** (retention) |
| "sub-second / two-way / live talk-back / peer-to-peer"  | **KVS WebRTC**                        |
| "detect faces/objects in the video stream in real time" | **KVS + Rekognition Video**           |
| "stream JSON/clickstream/log records"                   | **Kinesis Data Streams** (not Video)  |
| "transcode uploaded video files to HLS"                 | **Elastic Transcoder / MediaConvert** |
| "broadcast-grade live channel for distribution"         | **MediaLive + MediaPackage**          |
| "encrypt the stored video stream"                       | **KMS** (default on KVS)              |

[⬆ Back to top](#table-of-contents)

---

## 3. Common Distractors

- Choosing **Kinesis Data Streams** when the payload is **media** (use Video Streams).
- Choosing **KVS** when the payload is **non-media records** (use Data Streams/Firehose).
- Choosing **Elastic Transcoder/MediaConvert** for _live device ingestion_ (those are file/VOD).
- Choosing durable KVS when the requirement is **sub-second two-way** (use WebRTC).
- Expecting **WebRTC to store** video (it doesn't - run a durable stream too).
- Forgetting Rekognition Video publishes detections to a **Kinesis Data Stream**.

[⬆ Back to top](#table-of-contents)

---

## 4. Elimination Technique

1. **Is the payload media (video/audio)?** Yes → KVS family. No → Kinesis **Data** Streams/Firehose.
2. **Sub-second + two-way?** → KVS **WebRTC**. Otherwise → KVS durable streaming.
3. **Need storage/replay/ML?** → durable streaming (set retention).
4. **Real-time detection?** → Rekognition Video → KDS → Lambda.
5. **Files, not streams?** → Elastic Transcoder/MediaConvert.
6. **Broadcast channel?** → MediaLive/MediaPackage.

[⬆ Back to top](#table-of-contents)

---

## 5. Medium Scenario Questions (1-20)

### Q1

**Scenario:** A company has 50,000 IP cameras and wants to ingest, store, and replay footage by time, plus run ML.
**Options:** A) Kinesis Data Streams B) Kinesis Video Streams C) Elastic Transcoder D) S3 upload
**Correct:** B
**Explanation:** Media ingestion + time-indexed storage + ML → KVS.

### Q2

**Scenario:** A smart doorbell needs two-way audio/video with sub-second latency.
**Options:** A) KVS durable streaming B) KVS WebRTC C) MediaLive D) HLS playback
**Correct:** B
**Explanation:** Sub-second, two-way, peer-to-peer → WebRTC.

### Q3

**Scenario:** Detect faces in a live camera stream and trigger an alert.
**Options:** A) Rekognition Video on KVS → KDS → Lambda → SNS B) Athena C) MediaConvert D) Glue
**Correct:** A
**Explanation:** Standard real-time video analytics pipeline.

### Q4

**Scenario:** App streams clickstream JSON events for real-time processing.
**Options:** A) Kinesis Video Streams B) Kinesis Data Streams C) KVS WebRTC D) MediaLive
**Correct:** B
**Explanation:** Non-media records → Data Streams.

### Q5

**Scenario:** What unit does KVS use to time-index stored media?
**Options:** A) Shards B) Fragments C) Objects D) Partitions
**Correct:** B
**Explanation:** Fragments carry timestamps/fragment numbers.

### Q6

**Scenario:** Play KVS video in a browser without writing a custom decoder.
**Options:** A) GetMedia raw B) HLS/DASH streaming session URL C) PutMedia D) GetClip only
**Correct:** B
**Explanation:** `GetHLSStreamingSessionURL` gives a player-ready URL.

### Q7

**Scenario:** Reduce KVS storage cost.
**Options:** A) Increase retention to max B) Set retention to the period actually needed C) Add more streams D) Disable KMS
**Correct:** B
**Explanation:** Retention drives storage cost.

### Q8

**Scenario:** Encrypt stored streams with a key you control.
**Options:** A) No encryption B) Customer-managed KMS CMK on the stream C) Only TLS D) Client app
**Correct:** B
**Explanation:** KVS encrypts at rest with KMS; use a CMK for control.

### Q9

**Scenario:** Export a 30-second clip of an incident to S3.
**Options:** A) GetClip (MP4) → S3 B) PutMedia C) HLS only D) Not possible
**Correct:** A
**Explanation:** `GetClip` produces an MP4 you can store.

### Q10

**Scenario:** Transcode uploaded MP4 marketing videos to multiple resolutions.
**Options:** A) KVS B) Elastic Transcoder/MediaConvert C) KVS WebRTC D) KDS
**Correct:** B
**Explanation:** Files → transcoder, not KVS.

### Q11

**Scenario:** Many viewers must watch one camera live.
**Options:** A) Many GetMedia consumers B) HLS/DASH playback (fan-out) C) WebRTC to each (storage) D) Email frames
**Correct:** B
**Explanation:** HLS/DASH scales playback fan-out better than raw GetMedia.

### Q12

**Scenario:** Producer device pushes media to KVS using what?
**Options:** A) S3 PUT B) Producer SDK / GStreamer (PutMedia) C) Kinesis Agent D) Firehose
**Correct:** B
**Explanation:** KVS Producer SDK / GStreamer plugin.

### Q13

**Scenario:** Need both live two-way view AND a recording of the same camera.
**Options:** A) WebRTC only B) WebRTC for live + a durable KVS stream for recording C) Durable only D) MediaLive
**Correct:** B
**Explanation:** WebRTC has no storage; pair it with a durable stream.

### Q14

**Scenario:** Where do Rekognition Video detections land?
**Options:** A) S3 only B) A Kinesis Data Stream C) SQS only D) DynamoDB directly
**Correct:** B
**Explanation:** Rekognition Video stream processor outputs to a KDS.

### Q15

**Scenario:** Seek to footage between 14:00 and 14:05 yesterday.
**Options:** A) LIVE selector B) ON_DEMAND/LIVE_REPLAY fragment selector by timestamp C) WebRTC D) Not supported
**Correct:** B
**Explanation:** Fragment selectors allow time-range replay.

### Q16

**Scenario:** Run a custom ML model on frames.
**Options:** A) Impossible B) Consumer (ECS/EC2) GetMedia → decode → SageMaker C) Athena D) Glue
**Correct:** B
**Explanation:** Custom consumers feed frames to SageMaker.

### Q17

**Scenario:** Alarm when a camera stops sending video.
**Options:** A) CloudTrail B) CloudWatch alarm on IncomingBytes = 0 C) S3 events D) Config
**Correct:** B
**Explanation:** Incoming bytes dropping to zero signals producer disconnect.

### Q18

**Scenario:** WebRTC peers can't connect directly due to strict NAT.
**Options:** A) Fail B) TURN relays the media C) Increase retention D) Use HLS
**Correct:** B
**Explanation:** TURN relays when direct P2P is blocked.

### Q19

**Scenario:** Audit who deleted a video stream.
**Options:** A) SNS B) CloudTrail C) CloudWatch D) HLS logs
**Correct:** B
**Explanation:** CloudTrail records `DeleteStream`.

### Q20

**Scenario:** A finished, correctly-formatted video just needs global on-demand delivery.
**Options:** A) KVS B) S3 + CloudFront C) WebRTC D) MediaLive
**Correct:** B
**Explanation:** No live ingest/ML - just store and deliver.

[⬆ Back to top](#table-of-contents)

---

## 6. Hard Scenario Questions (1-10)

### H1

**Scenario:** A home-security company needs (a) live two-way talk with sub-second latency, (b) 30-day recorded playback, and (c) real-time person detection, across millions of devices.
**Options:** A) One durable stream only B) **WebRTC** for live talk + a **durable KVS stream** (30-day retention) for recording + **Rekognition Video → KDS → Lambda** for detection C) MediaLive D) KDS only
**Correct:** B
**Explanation:** Each requirement maps to a distinct KVS capability; WebRTC has no storage so a durable stream runs alongside.

### H2

**Scenario:** A team uses Kinesis Data Streams to "stream camera video" and hits payload/throughput problems.
**Options:** A) Add shards forever B) Use **Kinesis Video Streams** - the purpose-built media service - instead of Data Streams C) Firehose D) SQS
**Correct:** B
**Explanation:** Media belongs in Video Streams; Data Streams is for generic records.

### H3

**Scenario:** Storage costs are exploding; they keep all footage 1 year but only review the last 7 days and incidents.
**Options:** A) Keep 1-year retention B) Lower stream **retention** (e.g., 7 days) and **GetClip incidents to S3 + Glacier lifecycle** for long-term C) Delete streams D) Disable KMS
**Correct:** B
**Explanation:** Tune retention; archive only needed clips to cheaper S3 tiers.

### H4

**Scenario:** Each device must only be able to write its own stream and nothing else; millions of devices.
**Options:** A) Shared IAM user B) Per-device identity via **IoT/Cognito** with scoped IAM granting `PutMedia` to that device's stream only C) Public stream D) Root keys
**Correct:** B
**Explanation:** Per-device scoped identities enforce least privilege at fleet scale.

### H5

**Scenario:** Viewers report ~10s delay watching a live feed via HLS; they need near-instant.
**Options:** A) Increase fragment size B) Switch the live view to **WebRTC** (sub-second) while keeping HLS/durable for replay C) More retention D) MediaConvert
**Correct:** B
**Explanation:** HLS has inherent multi-second latency; WebRTC delivers sub-second.

### H6

**Scenario:** A custom detector (not Rekognition) must process frames and the results must trigger workflows reliably.
**Options:** A) Rekognition only B) Consumer on ECS using **GetMedia** → decode → **SageMaker**, publish results to **KDS → Lambda → Step Functions** C) Athena D) Glue
**Correct:** B
**Explanation:** Custom ML path: GetMedia → SageMaker → KDS → orchestration.

### H7

**Scenario:** Compliance requires that stored video be encrypted with a key the security team manages and that all stream deletions are audited.
**Options:** A) SSE default + no audit B) Customer-managed **KMS CMK** on streams + **CloudTrail** for `DeleteStream`/`UpdateDataRetention` C) No encryption D) Client-side only
**Correct:** B
**Explanation:** CMK gives key control; CloudTrail provides the audit trail.

### H8

**Scenario:** A factory wants RADAR/LIDAR time-series plus video correlated for safety analytics.
**Options:** A) Only video B) KVS can carry **time-encoded data** (not just video); ingest both as time-indexed streams and correlate by timestamp C) S3 only D) DynamoDB
**Correct:** B
**Explanation:** KVS supports arbitrary time-encoded media/data, enabling timestamp correlation.

### H9

**Scenario:** During an incident, investigators must pull the exact 2-minute window across 12 cameras quickly.
**Options:** A) Download everything B) Use **fragment selectors (ON_DEMAND by timestamp)** / **GetClip** per stream for the precise window C) WebRTC D) Re-stream
**Correct:** B
**Explanation:** Time-range fragment selection / GetClip gives precise, fast retrieval.

### H10

**Scenario:** A broadcaster needs a 24x7 channel with ABR distribution to a CDN - someone proposes KVS.
**Options:** A) KVS B) **MediaLive** (live encode) + **MediaPackage** (packaging/DRM) → CloudFront; KVS is for device ingestion/analytics, not broadcast distribution C) Elastic Transcoder D) KDS
**Correct:** B
**Explanation:** Broadcast-grade live distribution is MediaLive/MediaPackage; KVS is ingestion/analytics.

[⬆ Back to top](#table-of-contents)

---

## 7. One-Line Recap

> **Ingest live media from many devices, store/replay time-indexed, run ML → Kinesis Video Streams (durable). Sub-second two-way live → KVS WebRTC (no storage). Real-time detection → KVS + Rekognition Video → KDS → Lambda. Don't confuse with Kinesis Data Streams (records) or Elastic Transcoder/MediaConvert (files) or MediaLive (broadcast).**

[⬆ Back to top](#table-of-contents)

---

> Continue to [04 - Amazon Kinesis Video Streams SRE Operations](04%20-%20Amazon%20Kinesis%20Video%20Streams%20SRE%20Operations.md).
