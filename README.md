# 🧠 SOYL-MODEL  
**Cognitive Signal Processing for Agentic AI**  
*Phase 1 — Core Emotion Modules (MVP Build)*  

---

## 📘 Overview
**SOYL-MODEL** is an R&D project that aims to create an **Emotion-Adaptive AI Salesperson** — an intelligent agent that understands human emotions through **facial expressions, voice tone, and text sentiment**, and adapts its dialogue and recommendations in real time.

This first phase (MVP) focuses on building the **core emotion perception layer** — a multimodal system that detects, fuses, and serves emotional states through a unified API.

In simpler terms:
> We're teaching AI to *feel* how the customer feels.

---

## 🧩 Phase 1 Objective
To build and integrate three emotion-detection modules — **Face**, **Voice**, and **Text** — and expose a REST API (`/getEmotionState`) that returns a unified emotion vector:
```json
{
  "valence": 0.72,
  "arousal": 0.51,
  "confidence": 0.83,
  "dominant_signal": "voice"
}
```

This will serve as:
- The emotional intelligence backbone for future agentic behavior
- The data pipeline for training the SOYL Foundation Model later

## 🏗️ Architecture Overview
```
[ Camera ] ───▶ FaceEmotionModule ───┐
[ Microphone ] ─▶ VoiceEmotionModule ─┤──▶ Fusion API ─▶ Emotion State JSON
[ Text Input ] ─▶ TextSentimentModule ─┘
```

Each module returns its emotion estimation (valence, arousal, confidence), and the Fusion Layer combines them into one coherent emotional state.

## ⚙️ Tech Stack
| Component | Technology |
|-----------|-----------|
| Backend API | FastAPI (Python) |
| Vision Module | OpenCV, MediaPipe, PyTorch |
| Voice Module | Librosa, TorchAudio, Wav2Vec2 (later) |
| Text Module | Hugging Face Transformers (DistilBERT) |
| Integration | JSON-based schema + Fusion weighting logic |
| Testing | Pytest |
| Future expansion | AR front-end, LLM dialogue layer, foundation model pretraining |

## 📂 Directory Structure
```bash
SOYL-MODEL/
│
├── app/                  # FastAPI app (main API)
│   └── main.py
│
├── modules/
│   ├── vision/            # Face Emotion Detection
│   │   └── face_emotion.py
│   ├── voice/             # Voice Emotion Detection
│   │   └── voice_emotion.py
│   ├── text/              # Text Sentiment Analysis
│   │   └── text_sentiment.py
│   ├── fusion/            # Fusion logic
│   │   └── fusion.py
│   └── agent/             # Placeholder for adaptive AI agent
│
├── scripts/               # Testing and demo scripts
│   └── test_api.py
│
├── tests/                 # Unit tests
│   └── test_fusion.py
│
├── requirements.txt
├── README.md
├── .gitignore
└── pyproject.toml
```

## 🚀 Quick Start

### 1️⃣ Setup Environment
```bash
git clone <your_repo_url>
cd SOYL-MODEL
python3 -m venv .venv
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate
pip install -r requirements.txt
```

### 2️⃣ Run API
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3️⃣ Test Endpoint
```bash
python scripts/test_api.py
```

Visit http://localhost:8000/docs for interactive Swagger documentation.

## 🧪 Example API Request
```json
POST /getEmotionState
{
  "modules": [
    {"valence": 0.8, "arousal": 0.6, "confidence": 0.9, "source": "face"},
    {"valence": 0.6, "arousal": 0.4, "confidence": 0.7, "source": "voice"},
    {"valence": 0.7, "arousal": 0.5, "confidence": 0.6, "source": "text"}
  ]
}
```

**Example Response:**
```json
{
  "valence": 0.7,
  "arousal": 0.5,
  "confidence": 0.79,
  "dominant_signal": "face"
}
```

## 👥 Team Roles (Phase 1)
| Member | Role | Key Deliverables |
|--------|------|-----------------|
| Ryan (Lead / Integration) | Build FastAPI /getEmotionState, handle integration & fusion logic | Unified API + demo |
| Member 2 (Vision Engineer) | Build real-time face emotion detection (MediaPipe/OpenCV) | face_emotion.py + demo |
| Member 3 (Audio & NLP Engineer) | Build voice emotion & text sentiment modules | voice_emotion.py, text_sentiment.py |

## 🎯 Milestone Goals
| Week | Focus | Output |
|------|-------|--------|
| 1–2 | Set up data & model baselines | Face + Voice prototypes |
| 3–4 | Integration & testing | Fusion API live |
| 5 | Optimization & documentation | Stable outputs |
| 6 | Demo + dataset logging | MVP proof & data collection |

## 🧠 Phase 1 Outcome
At the end of this phase, we will have:

✅ Functional multimodal emotion detection

✅ Unified API serving real-time emotional state

✅ 50+ user sessions for dataset creation

✅ Foundation for AR & adaptive agent in next phase

## 🧾 Notes on Privacy & Ethics
SOYL-MODEL follows privacy-first design principles:

- All emotion inference runs locally when possible
- No raw images or voice data stored
- Only anonymized emotion embeddings logged with consent
- Transparent user consent screen to be implemented in Phase 2

## 🌍 Roadmap Snapshot
- **Phase 1:** Core Emotion Modules (MVP)
- **Phase 2:** Cognitive Signal Processor (Fusion Transformer)
- **Phase 3:** Adaptive AI Sales Agent (Emotion → Action)
- **Phase 4:** SOYL Foundation Model (Multimodal Affect Pretraining)
- **Phase 5:** Productization (B2B API + SDK)

## 💡 Inspiration
> "Cognitive Signal Processing meets Emotional Intelligence."  
> The future of AI is not just to think, but also to feel and adapt.

---

**Developed by Ryan, Renya and Nysa**
