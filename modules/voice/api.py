from fastapi import FastAPI
import base64
import numpy as np
from .voice_emotion import analyze_voice

app = FastAPI(title="SOYL Voice API")

@app.get("/health")
def health_check():
    return {"status": "voice api running"}

@app.post("/voice")
def analyze_voice_api(payload: dict):
    wav_b64 = payload.get("wav_b64")
    sr = payload.get("sr", 16000)

    if not wav_b64:
        return {"error": "missing wav_b64"}

    audio_bytes = base64.b64decode(wav_b64)
    y = np.frombuffer(audio_bytes, dtype=np.int16).astype("float32") / 32768.0

    return analyze_voice(y, sr)
