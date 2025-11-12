import argparse
import json
import sys
import numpy as np

try:
    import sounddevice as sd
except Exception as e:
    print("ERROR: sounddevice is required to record from microphone. Install it in your venv.", file=sys.stderr)
    raise

try:
    import speech_recognition as sr
except Exception:
    sr = None  # transcription will be skipped if speech_recognition is not installed

def heuristic_emotion(y: np.ndarray, sr_rate: int):
    y = np.asarray(y, dtype="float32").flatten()
    rms = float(np.sqrt(np.mean(np.square(y)) + 1e-12))
    arousal = float(np.clip((np.tanh(rms * 50) + 1) / 2, 0.0, 1.0))

    try:
        S = np.abs(np.fft.rfft(y))
        freqs = np.fft.rfftfreq(len(y), 1.0 / sr_rate)
        centroid = float((S * freqs).sum() / (S.sum() + 1e-9))
    except Exception:
        centroid = 2000.0
    valence = float(1.0 / (1.0 + np.exp(-(centroid - 2000) / 2000)))

    duration = len(y) / sr_rate
    confidence = float(np.clip(0.3 + (rms * 100) + min(0.4, duration / 10.0), 0.0, 1.0))

    return {
        "valence": round(valence, 3),
        "arousal": round(arousal, 3),
        "confidence": round(confidence, 3),
        "source": "voice",
        "duration": round(duration, 3),
    }

def record(duration: float = 4.0, sr_rate: int = 16000):
    print(f"🎙️  Listening... recording {duration:.1f}s @ {sr_rate}Hz", flush=True)
    try:
        audio = sd.rec(int(duration * sr_rate), samplerate=sr_rate, channels=1, dtype="float32")
        sd.wait()
    except Exception as e:
        print("ERROR: failed to record from microphone:", e, file=sys.stderr)
        raise
    return audio.flatten(), sr_rate

def transcribe_with_speech_recognition(y: np.ndarray, sr_rate: int):
    if sr is None:
        return None, "speech_recognition not installed"
    recognizer = sr.Recognizer()
    # Convert float32 [-1,1] to int16 bytes expected by AudioData
    int16 = (np.clip(y, -1.0, 1.0) * 32767).astype(np.int16)
    audio_bytes = int16.tobytes()
    audio_data = sr.AudioData(audio_bytes, sr_rate, 2)  # sample_width=2 bytes
    try:
        text = recognizer.recognize_google(audio_data)
        return text, None
    except sr.UnknownValueError:
        return None, "could not understand audio"
    except sr.RequestError as e:
        return None, f"request error: {e}"
    except Exception as e:
        return None, str(e)

def main():
    p = argparse.ArgumentParser(description="Record short audio from mic, transcribe and output heuristic emotion JSON")
    p.add_argument("--duration", "-d", type=float, default=4.0, help="Recording duration in seconds (default 4.0)")
    p.add_argument("--sr", type=int, default=16000, help="Sample rate (default 16000)")
    args = p.parse_args()

    y, sr_rate = record(duration=args.duration, sr_rate=args.sr)
    # Transcription (may require internet for recognize_google)
    transcription, trans_err = transcribe_with_speech_recognition(y, sr_rate)
    if transcription:
        print("\nTranscription:\n", transcription, flush=True)
    else:
        print("\nTranscription: (none)", file=sys.stdout, flush=True)
        if trans_err:
            print(f"Note: {trans_err}", file=sys.stdout, flush=True)

    out = heuristic_emotion(y, sr_rate)
    print("\nEmotion analysis:\n", json.dumps(out, indent=2), flush=True)

if __name__ == "__main__":
    main()