# SmartShield AI – Pitch Deck Content

## Slide 1: Title
**SmartShield AI**
*A Digital Boundary Enforcement System*

"Real-time. Explainable. Privacy-first."

---

## Slide 2: The Problem

- 1 in 3 women receive unsolicited explicit images online (cyber-flashing)
- 41% of Americans have experienced online harassment (Pew Research)
- Current moderation is **reactive** – users report, platforms review, damage is already done
- Toxic text, NSFW images, and stalking patterns are handled by **separate, siloed tools**

---

## Slide 3: The Gap

> "Existing systems wait for the victim to report the crime. We stop it before it's seen."

- No unified threat score
- No behavioral pattern analysis
- No explainability – users don't know *why* content was flagged
- No privacy-first approach – user data is stored and profiled

---

## Slide 4: Our Solution

**SmartShield AI** is a real-time, multi-modal content safety API.

✅ Detects toxic text (HuggingFace toxic-bert)
✅ Detects NSFW images (NSFW image classifier)
✅ Tracks behavioral patterns (message flooding, unanswered streaks, escalation)
✅ Generates a **Creep Score (0–1)** unifying all signals
✅ Returns **XAI reasoning** – every flag explained in plain English
✅ **Privacy-first** – SHA-256 hashed IDs, RAM-only session storage, auto-expiry

---

## Slide 5: The Creep Score

```
score = 0.40 × text_toxicity
      + 0.35 × image_nsfw
      + 0.25 × behavior_score

ALLOW (0.00–0.39) → content passes through
WARN  (0.40–0.59) → warning shown to recipient
BLUR  (0.60–0.79) → content hidden/blurred
BLOCK (0.80–1.00) → content removed
```

---

## Slide 6: Live Demo

**Scenario 1**: "Hey! How are you?" → Score: 0.02 → ✅ ALLOW

**Scenario 2**: "I know where you live" → Score: 0.84 → 🚫 BLOCK

**Scenario 3**: NSFW image upload → Score: 0.91 → 🔞 BLUR + BLOCK

**Scenario 4**: 10 rapid unanswered messages → Score escalates 0.2 → 0.75 → ⚠️ BLUR

---

## Slide 7: Tech Stack

| Layer | Tech |
|---|---|
| API | Python + FastAPI |
| Text AI | HuggingFace `unitary/toxic-bert` |
| Image AI | `Falconsai/nsfw_image_detection` |
| Behavior | In-memory session tracking |
| Privacy | SHA-256 hashing, TTL sessions |
| Demo UI | HTML5 + Vanilla JS |

**Cold start**: < 3 seconds (mock mode), < 30 seconds (full models)
**Inference**: < 200ms per request (CPU)

---

## Slide 8: Privacy Commitment

- ❌ No database writes
- ❌ No PII storage (IDs are hashed)
- ❌ No cross-session profiling
- ✅ Session data auto-expires (30 min TTL)
- ✅ Explicit session delete endpoint
- ✅ Users can opt out at any time
- ✅ GDPR-aligned by design

---

## Slide 9: Market Opportunity

- **Dating apps**: Bumble, Tinder, Hinge – 300M+ users
- **Social platforms**: Instagram, Twitter/X, Discord – 1B+ users
- **Enterprise**: Workplace harassment monitoring
- **Gaming**: Anti-toxicity in multiplayer chat

API licensing model: $0.001 per analysis request
At 10M requests/day → $3.65M ARR from a single platform

---

## Slide 10: What We're Asking For

- 🖥️ **GPU compute** (A100/V100) for production model serving
- 🤝 **Platform API partnerships** (dating apps, social platforms)
- 👩‍⚖️ **Legal/ethics advisors** for responsible deployment
- 🌱 **Seed funding** to build on-device ONNX inference module

---

## 2-Minute Pitch Script

**[0:00–0:15] Hook**
"Every 2 minutes, someone receives an unsolicited explicit image online. Current platforms do nothing until the victim reports it. By then, the damage is done. We built SmartShield AI to stop it *before* it's seen."

**[0:15–0:40] Problem**
"Toxic texts, cyber-flashing, and message flooding cause real psychological harm. Existing moderation systems are reactive, siloed, and opaque. Victims have no protection – only a report button."

**[0:40–1:05] Solution**
"SmartShield AI scores every message and image in real-time with a unified Creep Score from 0 to 1. Above the threshold, content is blurred or blocked before the victim sees it. And crucially – we explain every decision in plain English, so users trust the system."

**[1:05–1:35] Live Demo**
[Demo: safe message → ALLOW, threat → BLOCK, flood → escalating score]

**[1:35–1:50] Privacy Edge**
"Zero permanent storage. Sender IDs are hashed. Users opt in. We protect victims without creating surveillance infrastructure."

**[1:50–2:00] Close**
"With SmartShield AI, digital spaces can be safe by default. We need compute and platform partnerships to scale this. Who's in?"
