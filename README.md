# SmartShield AI – A Digital Boundary Enforcement System

An AI-based creep filtration system that proactively detects and neutralizes online harassment before it reaches the user.

## What It Does

SmartShield AI acts as a **proactive, user-side digital boundary**, catching and neutralizing harassment in real time:

- **Text Toxicity Detection** – Analyzes messages using a fine-tuned BERT model (`unitary/toxic-bert`)
- **NSFW Image Detection** – Classifies images using `Falconsai/nsfw_image_detection`
- **Behavioral Tracking** – Detects stalking-like patterns (message flooding, repeated unanswered messages)
- **Dynamic Creep Score** – Combines all signals into a score from 0 to 1
- **Content Filtering** – Blurs or blocks content when the score exceeds a threshold
- **Explainable AI** – Tells users *why* content was flagged

## Creep Score Formula

```
C_score = 0.35 × T + 0.45 × I + 0.20 × B
```

| Variable | Description | Weight |
|----------|-------------|--------|
| T | Text toxicity probability [0, 1] | 0.35 |
| I | Image NSFW probability [0, 1] | 0.45 |
| B | Behavioral penalty [0, 1] | 0.20 |

**Behavioral Penalty**: `B = min(unanswered_messages / 10, 1.0)`

| Creep Score | Action |
|-------------|--------|
| < 0.4 | ✅ Allow |
| 0.4 – 0.7 | ⚠️ Blur (soft filter) |
| ≥ 0.7 | 🚫 Block (heavy blur + explanation) |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React.js, TailwindCSS |
| Backend | FastAPI (Python) |
| Text Model | `unitary/toxic-bert` (Hugging Face) |
| Image Model | `Falconsai/nsfw_image_detection` (Hugging Face) |
| Behavior State | In-memory (Redis-ready) |

## Project Structure

```
├── backend/
│   ├── main.py          # FastAPI app with /analyze/text, /analyze/image endpoints
│   ├── scoring.py        # Creep Score calculation engine
│   ├── behavior.py       # Behavioral tracking (message flooding detection)
│   ├── models.py         # Pydantic request/response models
│   ├── requirements.txt  # Python dependencies
│   └── tests/            # pytest test suite
├── frontend/
│   ├── src/
│   │   ├── App.js              # Split-screen chat interface
│   │   ├── api.js              # Backend API service
│   │   └── components/
│   │       ├── ChatPanel.js    # Chat panel (sender/receiver)
│   │       └── MessageBubble.js # Message with blur/block states
│   └── package.json
└── README.md
```

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

The API runs at `http://localhost:8000`. Models are loaded on startup (optional – the system gracefully degrades without them).

### Frontend

```bash
cd frontend
npm install
npm start
```

The UI opens at `http://localhost:3000` with a split-screen demo.

### Run Tests

```bash
# Backend tests
python -m pytest backend/tests/ -v

# Frontend tests
cd frontend && npm test
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check & model status |
| POST | `/analyze/text` | Analyze text message for toxicity |
| POST | `/analyze/image` | Analyze uploaded image for NSFW content |
| POST | `/reply` | Record a reply (resets behavioral counter) |
| POST | `/reset` | Reset tracking between two users |

### Example Response

```json
{
  "creep_score": 0.85,
  "action": "block",
  "reason": "Blocked: 92% probability of toxic text; Message flooding detected (8 unanswered messages).",
  "text_toxicity": 0.92,
  "image_nsfw": null,
  "behavioral_penalty": 0.8
}
```

## Privacy & Ethics

- **Ephemeral Processing** – Payloads are evaluated in memory and immediately dropped
- **No Content Storage** – Only anonymized counters are stored (`user1→user2: 4`), never message content
- **Explainability** – Users see clear reasons for filtering decisions
- **User Control** – Recipients can reply to reset behavioral tracking

## Demo Strategy

Split-screen showing Sender (left) vs Receiver (right):
1. Send a normal message → passes instantly
2. Send a toxic message → blurs instantly on receiver side
3. Spam "hello" 10 times → watch the behavioral score climb from allow → blur → block

## Future Scalability

- **On-device processing** via TensorFlow.js or WebAssembly for 100% local inference
- **Multi-language support** for global deployment
- **Browser extension** for platform-agnostic protection
- **Redis clustering** for production-scale behavioral tracking