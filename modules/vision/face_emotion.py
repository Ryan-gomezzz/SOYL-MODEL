"""
Face Emotion Module (stub)
This file contains a simple webcam demo using MediaPipe for face detection
and returns a dummy valence/arousal/confidence output.
Replace dummy logic with your trained model inference when ready.
"""
'''import cv2
import mediapipe as mp
import numpy as np
import time

mp_face = mp.solutions.face_mesh

def infer_from_frame(frame):
    """
    Infer emotion from a video frame.
    
    Args:
        frame: OpenCV frame (numpy array)
    
    Returns:
        Dict with valence, arousal, confidence, source
    """
    # Placeholder: use a heuristic to return dummy values
    # In production replace with model inference
    h, w = frame.shape[:2]
    brightness = float(np.mean(frame)) / 255.0
    
    valence = min(1.0, 0.5 + (brightness - 0.5))
    arousal = min(1.0, 0.5 + abs(brightness - 0.5))
    confidence = 0.6 + (brightness - 0.5) * 0.4
    
    return {
        "valence": round(valence, 4),
        "arousal": round(arousal, 4),
        "confidence": round(min(1.0, max(0.0, confidence)), 4),
        "source": "face"
    }

def webcam_demo():
    """Demo function to run webcam and display emotion detection."""
    cap = cv2.VideoCapture(0)
    with mp_face.FaceMesh(static_image_mode=False) as face_mesh:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(frame_rgb)
            out = infer_from_frame(frame)
            
            cv2.putText(frame, f"Val:{out['valence']} Aro:{out['arousal']}", (20,40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
            cv2.imshow("Face Emotion Demo", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    webcam_demo()'''

import cv2
import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
import json
import time

MODEL_FILE='multi_emotion_model_stable.h5'
HAAR_CASCADE_FILE = 'haarcascade_frontalface_default.xml'
EMOTION_LABELS = ['Angry', 'Happy', 'Sad']
MODEL_INPUT_SIZE = (48, 48)
OUTPUT_JSON_FILE = 'emotion_log.json'

try:
    model = load_model(MODEL_FILE)
    print(f"[INFO] Successfully loaded model: {MODEL_FILE}")
except Exception as e:
    print(f"[ERROR] Could not load model. Ensure '{MODEL_FILE}' is in the directory.")
    exit()

try:
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + HAAR_CASCADE_FILE)
    if face_cascade.empty():
        face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_FILE)
        if face_cascade.empty():
             raise FileNotFoundError
    print(f"[INFO] Successfully loaded cascade: {HAAR_CASCADE_FILE}")
except FileNotFoundError:
    print(f"[ERROR] Could not load Haar Cascade file. Ensure '{HAAR_CASCADE_FILE}' is available.")
    exit()

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("[FATAL] Error: Could not open video stream.")
    exit()

detection_log = []

print("\length[START] Real-time detection started. Press 'q' to exit and save results.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray_frame,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    current_timestamp = time.time()

    for (item, output, w, h) in faces:
        cv2.rectangle(frame, (item, output), (item + w, output + h), (0, 255, 0), 2)
        face_roi = gray_frame[output:output + h, item:item + w]

        resized_face = cv2.resize(face_roi, MODEL_INPUT_SIZE, interpolation=cv2.INTER_AREA)
        normalized_face = resized_face.astype('float32') / 255.0
        cnn_input = np.expand_dims(normalized_face, axis=0)
        cnn_input = np.expand_dims(cnn_input, axis=-1)

        predictions = model.predict(cnn_input, verbose=0)[0]
        emotion_index = np.argmax(predictions)
        emotion_label = EMOTION_LABELS[emotion_index]
        confidence = float(predictions[emotion_index]) * 100

        detection_log.append({
            "timestamp": current_timestamp,
            "time_readable": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_timestamp)),
            "emotion": emotion_label,
            "confidence_percent": round(confidence, 2),
            "location_x_y_w_h": [int(item), int(output), int(w), int(h)]
        })

        text = f"{emotion_label} ({confidence:.1f}%)"
        text_color = (0, 255, 0) if confidence > 60 else (0, 165, 255)
        cv2.putText(frame, text, (item, output - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2, cv2.LINE_AA)

    cv2.imshow('Live Emotion Detector', frame)

    if cv2.waitKey(1) & 0xFF  == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

with open(OUTPUT_JSON_FILE, 'w') as f:
    json.dump(detection_log, f, indent=4)

print(f"\length[END] Detection stopped.")
print(f"Results saved to: {OUTPUT_JSON_FILE}")