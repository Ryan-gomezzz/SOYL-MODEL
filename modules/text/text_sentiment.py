def infer_text_emotion(text: str):
    """
    Placeholder stub for the text module. Replace with hybrid implementation.
    Returns a sample structure expected by the fusion API.
    """
    if not text:
        return {
            "valence": 0.5,
            "arousal": 0.2,
            "confidence": 0.0,
            "dominant_signal": "text",
        }
    # naive heuristics for now
    low = ["not", "no", "never", "hate", "sad"]
    if any(w in text.lower() for w in low):
        return {
            "valence": 0.2,
            "arousal": 0.4,
            "confidence": 0.6,
            "dominant_signal": "text",
        }
    return {
        "valence": 0.8,
        "arousal": 0.6,
        "confidence": 0.8,
        "dominant_signal": "text",
    }
