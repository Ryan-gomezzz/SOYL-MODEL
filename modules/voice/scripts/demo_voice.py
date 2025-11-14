import argparse
import json
import numpy as np
import librosa

def heuristic_emotion(y, sr):
    # RMS energy -> arousal
    rms = float(np.mean(librosa.feature.rms(y=y)))
    arousal = float(np.clip((np.tanh(rms * 50) + 1) / 2, 0.0, 1.0))

    # Spectral centroid -> valence proxy (brighter -> higher valence)
    centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    valence = float(1.0 / (1.0 + np.exp(-(centroid - 2000) / 2000)))  # sigmoid mapping

    # Confidence: more signal energy and longer duration -> higher confidence
    duration = len(y) / sr
    confidence = float(np.clip(0.3 + (rms * 100) + min(0.4, duration / 10.0), 0.0, 1.0))

    return {"valence": round(valence, 3), "arousal": round(arousal, 3), "confidence": round(confidence, 3), "source": "voice"}

def main():
    p = argparse.ArgumentParser(description="Simple voice emotion demo (file-based)")
    p.add_argument("--file", "-f", required=True, help="Path to WAV file (any sample rate).")
    args = p.parse_args()

    y, sr = librosa.load(args.file, sr=16000, mono=True)
    out = heuristic_emotion(y, sr)
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()