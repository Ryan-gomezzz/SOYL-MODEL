from modules.text import text_sentiment


def test_infer_returns_keys():
    out = text_sentiment.infer_text_emotion("I love this!")
    assert (
        "valence" in out
        and "arousal" in out
        and "confidence" in out
        and "dominant_signal" in out
    )
