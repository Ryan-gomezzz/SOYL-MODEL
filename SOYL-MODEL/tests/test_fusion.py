"""
Unit tests for fusion module.
"""
from modules.fusion.fusion import compute_emotion_state

def test_fusion_basic():
    """Test basic fusion functionality."""
    sample = [
        {"valence": 0.8, "arousal": 0.6, "confidence": 0.9, "source": "face"},
        {"valence": 0.6, "arousal": 0.4, "confidence": 0.7, "source": "voice"}
    ]
    out = compute_emotion_state(sample)
    assert "valence" in out and "arousal" in out
    assert out["dominant_signal"] in ("face", "voice")
    assert 0.0 <= out["valence"] <= 1.0
    assert 0.0 <= out["arousal"] <= 1.0
    assert 0.0 <= out["confidence"] <= 1.0

def test_fusion_single_module():
    """Test fusion with single module."""
    sample = [
        {"valence": 0.5, "arousal": 0.5, "confidence": 0.8, "source": "text"}
    ]
    out = compute_emotion_state(sample)
    assert out["valence"] == 0.5
    assert out["arousal"] == 0.5
    assert out["dominant_signal"] == "text"

if __name__ == "__main__":
    test_fusion_basic()
    test_fusion_single_module()
    print("All tests passed!")

