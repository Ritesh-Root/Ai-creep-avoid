# SmartShield AI – A Digital Boundary Enforcement System

> **Hackathon-Ready | Privacy-First | Explainable AI | Real-Time Protection**

> **Note**: This repository contains two frontend implementations merged from separate branches:
> - **HTML/JS frontend** (`frontend/index.html`, `frontend/app.js`) – lightweight demo UI
> - **React frontend** (`frontend/src/`) – full React + TailwindCSS SPA
>
> It also contains two backend implementations:
> - **Structured backend** (`backend/app/`) – modular FastAPI app with full test suite
> - **Flat backend** (`backend/main.py`, `backend/scoring.py`) – simpler single-file approach

> **Hackathon-Ready | Privacy-First | Explainable AI | Real-Time Protection**

---

## 1. Problem Statement

Digital harassment has become a pervasive threat in online spaces. Women, minorities, and vulnerable users face relentless toxic messages, unsolicited explicit images (cyber-flashing), and stalking-like behavioral patterns across social platforms, dating apps, and messaging services. Existing moderation systems are reactive, rely on user reports, and fail to protect in real-time.

**SmartShield AI** addresses this by providing:
- Proactive, real-time detection of toxic text, NSFW images, and aggressive behavioral patterns
- A unified **Creep Score (0–1)** that quantifies threat level
- Automatic content blurring/blocking before a user is harmed
- Full **Explainable AI (XAI)** reasoning so users understand *why* content was flagged
- A **privacy-first** architecture with no permanent data storage and optional on-device processing

---

## 2. Hackathon MVP Scope (24–36 Hour Build)

| Feature | In Scope | Out of Scope |
|---|---|---|
| Text toxicity detection | ✅ | Full NLP pipeline training |
| NSFW image classification | ✅ | Video frame analysis |
| Behavioral pattern tracking (per session) | ✅ | Cross-platform user graph |
| Creep Score (0–1) with threshold enforcement | ✅ | Adaptive threshold ML |
| Content blur/block API response | ✅ | Browser extension integration |
| XAI reasoning string per flag | ✅ | SHAP/LIME visualizations |
| REST API (FastAPI) | ✅ | WebSocket real-time push |
| Interactive web demo (HTML/JS) | ✅ | Full React SPA |
| Privacy: ephemeral session memory only | ✅ | Federated learning |

**MVP Deliverable**: A single API endpoint (`/api/v1/analyze`) that accepts a text message or image, optional sender metadata, and returns a Creep Score with actionable reasoning and a content-disposition directive (`ALLOW` / `BLUR` / `BLOCK`).

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                         │
│   Web App (HTML/JS)  ◄──────────────► Mobile (future)      │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS REST
┌───────────────────────────▼─────────────────────────────────┐
│                      API GATEWAY (FastAPI)                   │
│   /api/v1/analyze   /api/v1/session   /api/v1/health        │
└───────────┬───────────────┬───────────────┬─────────────────┘
            │               │               │
┌───────────▼───┐  ┌────────▼──────┐  ┌────▼──────────────────┐
│  TEXT PIPELINE│  │ IMAGE PIPELINE│  │  BEHAVIORAL PIPELINE  │
│               │  │               │  │                       │
│ Toxic-BERT    │  │ NudeNet /     │  │  Pattern Tracker      │
│ (HuggingFace) │  │ CLIP NSFW     │  │  (In-Memory per       │
│               │  │               │  │   session)            │
│ Outputs:      │  │ Outputs:      │  │                       │
│ - toxicity    │  │ - nsfw_score  │  │ Signals:              │
│ - categories  │  │ - categories  │  │ - msg_flood_rate      │
│ - confidence  │  │ - confidence  │  │ - unanswered_streak   │
│               │  │               │  │ - time_pattern        │
└───────┬───────┘  └────────┬──────┘  └────────┬──────────────┘
        │                   │                   │
┌───────▼───────────────────▼───────────────────▼─────────────┐
│                    CREEP SCORE ENGINE                        │
│                                                             │
│   score = w1*text_score + w2*image_score + w3*behavior_score│
│                                                             │
│   Thresholds: WARN(0.4) | BLUR(0.6) | BLOCK(0.8)          │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                   XAI REASONING MODULE                       │
│   Generates human-readable explanations for each flag       │
│   e.g. "Message contains sexual language (87% confidence)   │
│         Sender sent 12 unanswered messages in 10 minutes"   │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                   RESPONSE PIPELINE                          │
│   { creep_score, disposition, reasons[], categories[] }     │
│   ALLOW → pass content through                              │
│   BLUR  → return blurred image / hide text preview          │
│   BLOCK → content removed, user notified                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Recommended Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| **API Framework** | Python 3.11 + FastAPI | Async, auto OpenAPI docs, fast iteration |
| **Text AI** | HuggingFace Transformers | Access to pre-trained toxic classifiers |
| **Image AI** | NudeNet + Pillow | Lightweight NSFW detector, no GPU needed for MVP |
| **Behavioral Logic** | Pure Python (in-memory dict) | No DB dependency for hackathon |
| **Frontend** | HTML5 + Vanilla JS | Fast to demo, no build step |
| **Serving** | Uvicorn | ASGI, production-ready |
| **Model Cache** | HuggingFace Hub cache | Avoid re-downloading models |
| **Testing** | Pytest + HTTPX | Async-friendly API tests |

---

## 5. Pre-Trained Models

### Text Analysis
| Model | HuggingFace ID | Use Case |
|---|---|---|
| **Toxic-BERT** | `unitary/toxic-bert` | Multi-label toxicity (toxic, severe_toxic, obscene, threat, insult, identity_hate) |
| **HateSpeech Detector** | `Hate-speech-CNERG/dehatebert-mono-english` | Hate speech classification |
| **Sexual Content** | `michellejieli/NSFW_text_classifier` | Sexually explicit text |

### Image Analysis
| Model | Source | Use Case |
|---|---|---|
| **NudeNet** | `notAI-tech/NudeNet` | NSFW body part detection, cyber-flashing |
| **CLIP + NSFW adapter** | `openai/clip-vit-base-patch32` | Zero-shot NSFW classification |
| **Google ViT NSFW** | `Falconsai/nsfw_image_detection` | Fast binary NSFW/SFW |

**Hackathon Primary Choices**: `unitary/toxic-bert` for text, `Falconsai/nsfw_image_detection` for images (both small, CPU-runnable).

---

## 6. Behavioral Scoring Logic & Creep Score Formula

### Behavioral Signals

| Signal | Description | Score Contribution |
|---|---|---|
| `message_flood_rate` | Messages sent per minute | `min(rate / 10, 1.0)` |
| `unanswered_streak` | Consecutive messages without reply | `min(streak / 15, 1.0)` |
| `odd_hour_penalty` | Messages between 00:00–05:00 | `+0.15` flat bonus |
| `escalation_rate` | Rising toxicity across message window | `delta_toxicity * 2` |
| `keyword_alarm` | Presence of tracked threatening keywords | `+0.30` flat bonus |

### Creep Score Formula

```
text_score    = toxicity_confidence  (from Toxic-BERT, 0–1)
image_score   = nsfw_confidence      (from NSFW classifier, 0–1)
behavior_score = clamp(
    message_flood_rate * 0.25
  + unanswered_streak_score * 0.35
  + odd_hour_penalty
  + escalation_rate * 0.20
  + keyword_alarm,
  0.0, 1.0
)

raw_score = (
    0.40 * text_score
  + 0.35 * image_score
  + 0.25 * behavior_score
)

creep_score = clamp(raw_score, 0.0, 1.0)
```

### Disposition Thresholds

| Score Range | Disposition | Action |
|---|---|---|
| 0.00 – 0.39 | `ALLOW` | Content passes through |
| 0.40 – 0.59 | `WARN` | Flag shown to recipient, content visible |
| 0.60 – 0.79 | `BLUR` | Image blurred, text preview hidden |
| 0.80 – 1.00 | `BLOCK` | Content removed, sender notified |

---

## 7. Privacy & Ethical Considerations

| Concern | Mitigation |
|---|---|
| **No permanent storage** | All behavioral data is session-scoped (TTL: 30 min), stored only in RAM |
| **No PII retention** | Sender IDs are hashed (SHA-256) before storage; originals never stored |
| **On-device option** | Text models can run via ONNX Runtime locally in browser (future) |
| **Bias in AI models** | Use ensemble of models; allow user to dispute flags; log false-positive rate |
| **False positives** | Disposition `WARN` inserted before `BLUR`/`BLOCK`; user can override |
| **Transparency** | Every decision includes `reasons[]` array explaining contributing factors |
| **Consent** | Users explicitly opt-in to AI analysis; analysis consent is revocable |
| **GDPR alignment** | No user profiling persisted; right to erasure = session expiry |

---

## 8. Demo Presentation Strategy

### Setup (Pre-demo)
1. Start the FastAPI server: `cd backend && uvicorn app.main:app --reload`
2. Open `frontend/index.html` in browser
3. Have 3 demo scenarios pre-loaded

### Demo Flow (5 minutes)
1. **Normal message** ("Hey, how are you?") → Score: 0.05 → ALLOW ✅
2. **Toxic text** ("I know where you live, you'll regret this") → Score: 0.82 → BLOCK 🚫 + reasoning
3. **NSFW image upload** → Score: 0.91 → BLUR + BLOCK 🔞
4. **Behavioral flooding demo** → Send 10 rapid messages → Score escalates live from 0.2 → 0.75

### Key Talking Points
- Show the `reasons[]` array in the response (XAI)
- Demonstrate no data persisted after session (show empty DB state)
- Toggle the threshold slider to show real-time re-classification

---

## 9. 2-Minute Pitch Structure

| Time | Section | Content |
|---|---|---|
| **0:00–0:15** | **Hook** | "Every 2 minutes, someone receives an unsolicited explicit image online. Current systems do nothing until the victim reports it. We built SmartShield AI to stop it *before* it's seen." |
| **0:15–0:40** | **Problem** | Toxic texts, cyber-flashing, stalking patterns cause real psychological harm. Platforms are reactive, not proactive. |
| **0:40–1:05** | **Solution** | SmartShield AI scores every message and image in real-time with a Creep Score (0–1). Above threshold = blur/block. Explainable AI tells you *why*. |
| **1:05–1:35** | **Live Demo** | Show toxic text → BLOCK. Show NSFW image → BLUR. Show behavioral flood → escalating score. |
| **1:35–1:50** | **Privacy Edge** | "Zero permanent storage. Sender IDs are hashed. Users opt-in. We protect victims without creating surveillance." |
| **1:50–2:00** | **Ask / Close** | "We need compute resources and API partnerships. With SmartShield AI, we can make digital spaces safe by default." |

---

## 10. Future Scalability & Innovation Factor

### Scalability Roadmap

| Phase | Feature | Technology |
|---|---|---|
| **Phase 2** | WebSocket real-time stream analysis | FastAPI WebSockets + Redis pub/sub |
| **Phase 2** | Multi-language toxic text support | `xlm-roberta-base` multilingual |
| **Phase 3** | Video/GIF NSFW frame detection | FFmpeg + image pipeline per frame |
| **Phase 3** | Cross-platform behavior graph | Neo4j graph DB (anonymized) |
| **Phase 4** | On-device inference (browser) | ONNX.js / TensorFlow.js |
| **Phase 4** | Federated learning | Flower framework |
| **Phase 5** | Platform SDK / Browser extension | Chrome Extension API |
| **Phase 5** | Legal escalation pathway | Auto-generate evidence package for law enforcement |

### Innovation Factor

- **Unified Creep Score**: No prior art combines text toxicity + image NSFW + behavioral patterns into a single, explainable threat score
- **Privacy-by-Design**: Ephemeral analysis without building persistent user profiles
- **XAI for Safety**: Explainable AI in content moderation is rare; most systems are black boxes
- **Hackathon Differentiator**: Running end-to-end (detect → score → blur → explain) in a 24-hour build demonstrates technical depth and real-world impact

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/Ritesh-Root/Ai-creep-avoid.git
cd Ai-creep-avoid

# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (in another terminal)
cd frontend
# Open index.html in browser or:
python -m http.server 3000
# Visit http://localhost:3000
```

### API Example

```bash
# Analyze a text message
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "type": "text",
    "content": "I know where you live",
    "sender_id": "user_abc",
    "session_id": "sess_123"
  }'

# Response:
{
  "creep_score": 0.84,
  "disposition": "BLOCK",
  "text_score": 0.91,
  "image_score": 0.0,
  "behavior_score": 0.43,
  "reasons": [
    "Message contains threatening language (confidence: 91%)",
    "Sender has sent 8 unanswered messages in this session",
    "Keyword alarm: threatening phrase detected"
  ],
  "categories": ["threat", "harassment"],
  "processing_time_ms": 142,
  "session_id": "sess_123"
}
```

---

## Project Structure

```
SmartShield-AI/
├── README.md                    # This file – full project plan
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI application entry point
│   │   ├── api/
│   │   │   └── routes.py       # All API route handlers
│   │   ├── models/
│   │   │   ├── text_analyzer.py      # HuggingFace toxic-bert wrapper
│   │   │   ├── image_analyzer.py     # NSFW image classifier
│   │   │   ├── behavioral_tracker.py # In-memory session behavior tracker
│   │   │   └── creep_score.py        # Score aggregation & disposition
│   │   └── utils/
│   │       ├── privacy.py      # Hashing, TTL session management
│   │       └── explainer.py    # XAI reason generation
│   ├── tests/
│   │   ├── test_text_analyzer.py
│   │   ├── test_image_analyzer.py
│   │   ├── test_behavioral_tracker.py
│   │   ├── test_creep_score.py
│   │   └── test_api.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html              # Demo UI
│   ├── app.js                  # Frontend logic
│   └── styles.css              # Styles
└── docs/
    ├── ARCHITECTURE.md         # Detailed architecture diagrams
    ├── API.md                  # API reference
    └── PITCH.md                # Pitch deck content
```

---

*Built for hackathons. Designed for the real world. SmartShield AI – because digital boundaries matter.*
