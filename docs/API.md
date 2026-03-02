# SmartShield AI – API Reference

Base URL: `http://localhost:8000/api/v1`

Interactive docs: `http://localhost:8000/docs` (Swagger UI)

---

## POST `/analyze/text`

Analyze a text message for toxicity, threats, and sexual content.

**Request Body (JSON)**

| Field | Type | Required | Description |
|---|---|---|---|
| `content` | string | ✅ | Text message (1–4096 chars) |
| `sender_id` | string | ✅ | Sender identifier (hashed before storage) |
| `session_id` | string | ❌ | Session ID; auto-generated if omitted |
| `has_reply` | boolean | ❌ | True if this is a reply (resets unanswered streak) |

**Response (JSON)**

```json
{
  "session_id": "sess_abc123",
  "creep_score": 0.84,
  "disposition": "BLOCK",
  "text_score": 0.91,
  "image_score": 0.0,
  "behavior_score": 0.43,
  "reasons": [
    "Message contains high-confidence harmful language (91% confidence) – categories: threat, insult.",
    "Sender sent 8 consecutive unanswered messages – possible stalking or pressure pattern."
  ],
  "categories": ["threat", "insult"],
  "processing_time_ms": 142.5
}
```

**Dispositions**

| Value | Score Range | Meaning |
|---|---|---|
| `ALLOW` | 0.00–0.39 | Content is safe |
| `WARN` | 0.40–0.59 | Marginal; flag shown |
| `BLUR` | 0.60–0.79 | Hide/blur content |
| `BLOCK` | 0.80–1.00 | Remove content |

---

## POST `/analyze/image`

Analyze an uploaded image for NSFW content.

**Request (multipart/form-data)**

| Field | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | ✅ | Session ID |
| `sender_id` | string | ✅ | Sender identifier |
| `file` | file | ✅ | Image file (JPEG, PNG, WebP, etc.) |

**Response**: Same schema as `/analyze/text`.

---

## POST `/reply`

Record that the recipient replied to a sender. Resets the sender's unanswered message streak.

**Request Body (JSON)**

```json
{ "session_id": "sess_abc123", "sender_id": "user_xyz" }
```

**Response**

```json
{ "status": "ok", "message": "Reply recorded; unanswered streak reset." }
```

---

## DELETE `/session/{session_id}`

Immediately delete all session data (privacy control).

**Response**

```json
{ "status": "ok", "message": "Session 'sess_abc123' data deleted." }
```

---

## GET `/health`

Liveness check.

**Response**

```json
{ "status": "ok", "service": "SmartShield AI" }
```

---

## Error Responses

| Status | Description |
|---|---|
| `400` | Invalid input (e.g., non-image file uploaded) |
| `422` | Validation error (missing required field) |
| `500` | Internal server error |
