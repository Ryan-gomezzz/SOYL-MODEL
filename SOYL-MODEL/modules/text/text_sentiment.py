"""
Text Sentiment Module (starter)

Uses a simple rule-based sentiment for the stub.

Replace with DistilBERT / fine-tuned transformer for production.
"""
from typing import Dict

def infer_from_text(text: str) -> Dict:
    """
    Infer emotion from text input.
    
    Args:
        text: Input text string
    
    Returns:
        Dict with valence, arousal, confidence, source
    """
    text_lower = text.lower()
    
    # Positive keywords
    if any(w in text_lower for w in ["love", "great", "like", "awesome", "perfect", "nice"]):
        return {"valence": 0.9, "arousal": 0.6, "confidence": 0.8, "source": "text"}
    
    # Negative keywords
    if any(w in text_lower for w in ["hate", "bad", "worst", "terrible", "nope"]):
        return {"valence": 0.1, "arousal": 0.6, "confidence": 0.8, "source": "text"}
    
    # Uncertain keywords
    if any(w in text_lower for w in ["maybe", "not sure", "unsure", "could be"]):
        return {"valence": 0.5, "arousal": 0.3, "confidence": 0.6, "source": "text"}
    
    # Default neutral
    return {"valence": 0.5, "arousal": 0.35, "confidence": 0.5, "source": "text"}

if __name__ == "__main__":
    print(infer_from_text("I like this product a lot!"))
    print(infer_from_text("Not sure about the size, maybe not."))

