import speech_recognition as sr
import sounddevice as sd
import numpy as np

r = sr.Recognizer()
duration = 4   # seconds
samplerate = 16000

print("🎤 Say something...")
audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
sd.wait()

audio_bytes = audio_data.tobytes()
audio = sr.AudioData(audio_bytes, samplerate, 2)

print("🧠 Processing...")

try:
    text = r.recognize_google(audio)
    print("✅ You said:", text)
except Exception as e:
    print("❌ Error:", e)



