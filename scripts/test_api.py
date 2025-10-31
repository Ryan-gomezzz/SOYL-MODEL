"""
Simple test script to call the Fusion API.
Run this after starting the FastAPI server.
"""
import requests

url = "http://localhost:8000/getEmotionState"
payload = {
    "modules": [
        {"valence": 0.8, "arousal": 0.6, "confidence": 0.9, "source": "face"},
        {"valence": 0.6, "arousal": 0.4, "confidence": 0.7, "source": "voice"},
        {"valence": 0.7, "arousal": 0.5, "confidence": 0.6, "source": "text"}
    ]
}

try:
    r = requests.post(url, json=payload)
    print("Status:", r.status_code)
    print("Response:", r.json())
except requests.exceptions.ConnectionError:
    print("Error: Could not connect to API. Make sure the server is running on http://localhost:8000")
except Exception as e:
    print(f"Error: {e}")

