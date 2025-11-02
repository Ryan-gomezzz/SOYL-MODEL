from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI(title="SOYL-MODEL Fusion API")


class ModuleItem(BaseModel):
    valence: float
    arousal: float
    confidence: float
    source: str


class GetEmotionRequest(BaseModel):
    modules: List[ModuleItem]


class EmotionState(BaseModel):
    valence: float
    arousal: float
    confidence: float
    dominant_signal: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/getEmotionState", response_model=EmotionState)
def get_emotion_state(req: GetEmotionRequest):
    if not req.modules:
        return {
            "valence": 0.5,
            "arousal": 0.2,
            "confidence": 0.0,
            "dominant_signal": "none",
        }
    # Simple placeholder fusion: confidence-weighted average
    total_w = sum(m.confidence for m in req.modules) or 1.0
    val = sum(m.valence * m.confidence for m in req.modules) / total_w
    ar = sum(m.arousal * m.confidence for m in req.modules) / total_w
    best = max(req.modules, key=lambda x: x.confidence)
    return {
        "valence": round(val, 3),
        "arousal": round(ar, 3),
        "confidence": round(max(m.confidence for m in req.modules), 3),
        "dominant_signal": best.source,
    }
