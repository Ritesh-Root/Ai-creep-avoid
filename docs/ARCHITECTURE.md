# SmartShield AI – System Architecture

## Overview

SmartShield AI uses a three-pipeline architecture that runs in parallel for each incoming request:

1. **Text Pipeline** – HuggingFace toxic-bert classifier
2. **Image Pipeline** – NSFW image classifier
3. **Behavioral Pipeline** – In-memory session-scoped pattern tracker

All three sub-scores are aggregated by the **Creep Score Engine** into a unified 0–1 score, then passed to the **XAI Reasoning Module** which generates human-readable explanations.

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  FastAPI Application (app/main.py)                              │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Router (app/api/routes.py)                               │  │
│  │  POST /analyze/text   POST /analyze/image                 │  │
│  │  POST /reply          DELETE /session/{id}                │  │
│  │  GET  /health                                             │  │
│  └────────────┬──────────────────────┬────────────────────── ┘  │
│               │                      │                          │
│  ┌────────────▼──────┐  ┌────────────▼──────┐                  │
│  │  TextAnalyzer     │  │  ImageAnalyzer    │                  │
│  │  (models/         │  │  (models/         │                  │
│  │   text_analyzer)  │  │   image_analyzer) │                  │
│  │                   │  │                   │                  │
│  │ toxic-bert        │  │ Falconsai NSFW    │                  │
│  │ keyword heuristic │  │ skin-ratio mock   │                  │
│  └────────────┬──────┘  └────────────┬──────┘                  │
│               │                      │                          │
│  ┌────────────▼──────────────────────▼──────────────────────┐  │
│  │  BehavioralTracker (models/behavioral_tracker.py)        │  │
│  │  SessionStore (utils/privacy.py)                         │  │
│  │                                                          │  │
│  │  Signals: flood_rate, unanswered_streak, odd_hour,       │  │
│  │           escalation_rate, keyword_alarm                 │  │
│  └────────────────────────────┬─────────────────────────────┘  │
│                               │                                 │
│  ┌────────────────────────────▼─────────────────────────────┐  │
│  │  CreepScore Engine (models/creep_score.py)               │  │
│  │                                                          │  │
│  │  score = 0.40*text + 0.35*image + 0.25*behavior          │  │
│  │  → ALLOW | WARN | BLUR | BLOCK                           │  │
│  └────────────────────────────┬─────────────────────────────┘  │
│                               │                                 │
│  ┌────────────────────────────▼─────────────────────────────┐  │
│  │  XAI Explainer (utils/explainer.py)                      │  │
│  │  → reasons[] array                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
Client Request
    │
    ▼
Input Validation (Pydantic)
    │
    ├──► TextAnalyzer.analyze(text)
    │       └─► returns TextAnalysisResult { score, categories, keyword_alarm }
    │
    ├──► ImageAnalyzer.analyze_bytes(image)
    │       └─► returns ImageAnalysisResult { score, categories }
    │
    ├──► BehavioralTracker.record_message(session_id, sender_hash, ...)
    │       └─► returns BehaviorSignals { flood_rate, unanswered_streak, ... }
    │
    ├──► compute_behavior_score(signals) → float
    ├──► compute_creep_score(text, image, behavior) → CreepScoreResult
    │
    └──► build_reasons(...) → list[str]
            │
            ▼
        AnalyzeResponse (JSON)
```

## Privacy Architecture

```
Client Request: { content, sender_id, session_id }
                                │
              ┌─────────────────▼──────────────────┐
              │  hash_sender_id(sender_id)          │
              │  SHA-256 digest – original NEVER    │
              │  stored or logged                   │
              └─────────────────┬──────────────────┘
                                │
              ┌─────────────────▼──────────────────┐
              │  SessionStore (RAM only)            │
              │  TTL: 30 minutes from last access   │
              │  Auto-evict on expiry               │
              │  clear_all() on app shutdown        │
              └─────────────────────────────────────┘
```

## File Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI app, lifespan manager
│   ├── api/
│   │   └── routes.py            # All HTTP endpoints
│   ├── models/
│   │   ├── text_analyzer.py     # HuggingFace toxic-bert wrapper
│   │   ├── image_analyzer.py    # NSFW image classifier
│   │   ├── behavioral_tracker.py# Session-scoped pattern tracker
│   │   └── creep_score.py       # Score aggregation + disposition
│   └── utils/
│       ├── privacy.py           # SessionStore + hashing
│       └── explainer.py         # XAI reason generation
└── tests/
    ├── test_api.py
    ├── test_text_analyzer.py
    ├── test_image_analyzer.py
    ├── test_behavioral_tracker.py
    ├── test_creep_score.py
    └── test_privacy.py
```
