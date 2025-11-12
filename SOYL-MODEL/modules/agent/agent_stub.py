"""
Agent stub - receives emotion state and returns a simple template response.
Replace with LLM integration or more advanced policy later.
"""
from typing import Dict

def respond(emotion_state: Dict) -> Dict:
    """
    Generate response based on emotion state.
    
    Args:
        emotion_state: Dict with valence, arousal, confidence, dominant_signal
    
    Returns:
        Dict with tone and message
    """
    val = emotion_state.get("valence", 0.5)
    
    if val > 0.7:
        return {
            "tone": "enthusiastic",
            "message": "Great! You seem to like this — want to see similar premium options?"
        }
    
    if val < 0.4:
        return {
            "tone": "empathetic",
            "message": "I understand — would you like recommendations for simpler styles or help on sizing?"
        }
    
    return {
        "tone": "neutral",
        "message": "Here are a few options you might like based on what you tried."
    }

