# Emotion Sales MVP

**Goal:** Phase-1 MVP for Emotion-Adaptive AI Salesperson.
This repo contains starter modules for:
- Face emotion detection (vision)
- Voice emotion detection (audio)
- Text sentiment & intent
- Fusion FastAPI that exposes `/getEmotionState`

## Structure
```
app/ # FastAPI app and entrypoint
modules/
  vision/ # face_emotion.py
  voice/ # voice_emotion.py
  text/ # text_sentiment.py
  fusion/ # fusion logic
  agent/ # placeholder for future agent
tests/ # unit tests
docs/ # design docs
```

## Quickstart (local)
1. Create and activate a virtualenv:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   # On Windows:
   # .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Run the FastAPI app:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   Visit docs at: http://localhost:8000/docs

## API contract
POST `/getEmotionState` — accepts JSON array of module outputs, returns weighted emotion state:
```json
{
  "valence": 0.7,
  "arousal": 0.5,
  "confidence": 0.82,
  "dominant_signal": "voice"
}
```

## Development
Each module should expose a function returning:
```json
{
  "valence": float,
  "arousal": float,
  "confidence": float,
  "source": "face|voice|text"
}
```

## Privacy note
This is a prototype. Do not store raw images/audio without consent. Store only anonymized embeddings and outputs.

