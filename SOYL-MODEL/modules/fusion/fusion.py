"""
Simple fusion logic: confidence-weighted average of valence & arousal
"""
from typing import List, Dict

def compute_emotion_state(module_outputs: List[Dict]) -> Dict:
    """
    Compute fused emotion state from multiple module outputs.
    
    Args:
        module_outputs: List of dicts with keys: valence, arousal, confidence, source
    
    Returns:
        Dict with fused valence, arousal, confidence, and dominant_signal
    """
    # Validate inputs
    if not module_outputs:
        raise ValueError("No module outputs provided.")
    
    total_weight = 0.0
    valence_sum = 0.0
    arousal_sum = 0.0
    dominant = None
    best_conf = -1.0
    
    for m in module_outputs:
        c = float(m.get("confidence", 0.5))
        v = float(m.get("valence", 0.5))
        a = float(m.get("arousal", 0.5))
        
        valence_sum += v * c
        arousal_sum += a * c
        total_weight += c
        
        if c > best_conf:
            best_conf = c
            dominant = m.get("source", "unknown")
    
    if total_weight == 0:
        total_weight = 1.0
    
    fused_valence = round(valence_sum / total_weight, 4)
    fused_arousal = round(arousal_sum / total_weight, 4)
    overall_confidence = round(min(1.0, max(0.0, total_weight / len(module_outputs))), 4)
    
    return {
        "valence": fused_valence,
        "arousal": fused_arousal,
        "confidence": overall_confidence,
        "dominant_signal": dominant
    }


# Quick local test helper
if __name__ == "__main__":
    sample = [
        {"valence": 0.8, "arousal": 0.6, "confidence": 0.9, "source": "face"},
        {"valence": 0.6, "arousal": 0.4, "confidence": 0.7, "source": "voice"}
    ]
    print(compute_emotion_state(sample))

