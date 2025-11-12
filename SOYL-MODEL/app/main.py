from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import modules.fusion.fusion as fusion

app = FastAPI(title="Emotion Sales MVP - Fusion API")

class ModuleOutput(BaseModel):
    valence: float
    arousal: float
    confidence: float
    source: str

class FusionRequest(BaseModel):
    modules: List[ModuleOutput]

@app.post("/getEmotionState")
async def get_emotion_state(req: FusionRequest):
    try:
        fused = fusion.compute_emotion_state([m.dict() for m in req.modules])
        return fused
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"status": "ok", "message": "Emotion Sales MVP Fusion API"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

