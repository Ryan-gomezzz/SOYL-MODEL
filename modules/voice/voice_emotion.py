"""
Voice Emotion Module (stub)

Placeholder code to demonstrate audio input and produce dummy valence/arousal/confidence.

Replace with real model (Wav2Vec2 / fine-tuned classifier).
"""
import numpy as np
try:
    import sounddevice as sd
    HAS_SOUNDDEVICE = True
except ImportError:
    HAS_SOUNDDEVICE = False
import queue
import threading
import time

q = queue.Queue()

def audio_callback(indata, frames, time_info, status):
    """Callback for audio stream."""
    q.put(indata.copy())

def infer_from_audio_chunk(chunk):
    """
    Infer emotion from audio chunk.
    
    Args:
        chunk: numpy array of audio samples
    
    Returns:
        Dict with valence, arousal, confidence, source
    """
    # Simple heuristic: energy -> arousal
    energy = float(np.mean(np.abs(chunk)))
    valence = 0.5
    arousal = min(1.0, energy * 10)
    confidence = min(1.0, 0.4 + energy * 5)
    
    return {
        "valence": round(valence, 4),
        "arousal": round(arousal, 4),
        "confidence": round(confidence, 4),
        "source": "voice"
    }

def record_and_infer(duration=3, samplerate=16000, channels=1):
    """
    Record audio and infer emotion.
    
    Args:
        duration: Recording duration in seconds
        samplerate: Audio sample rate
        channels: Number of audio channels
    
    Returns:
        Dict with valence, arousal, confidence, source
    """
    if not HAS_SOUNDDEVICE:
        return {"valence": 0.5, "arousal": 0.2, "confidence": 0.2, "source": "voice"}
    
    frames = []
    def _run():
        with sd.InputStream(samplerate=samplerate, channels=channels, callback=audio_callback):
            start = time.time()
            while time.time() - start < duration:
                try:
                    data = q.get(timeout=1)
                    frames.append(data)
                except queue.Empty:
                    pass
    
    t = threading.Thread(target=_run)
    t.start()
    t.join()
    
    if not frames:
        return {"valence": 0.5, "arousal": 0.2, "confidence": 0.2, "source": "voice"}
    
    audio = np.concatenate(frames, axis=0)
    return infer_from_audio_chunk(audio)

if __name__ == "__main__":
    print("Recording 3 seconds of audio...")
    out = record_and_infer(duration=3)
    print(out)

