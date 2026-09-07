"""
Voice / Scream Distress Detection Module
-----------------------------------------
On-device, this runs as a TFLite audio-classification model (YAMNet-style,
fine-tuned on scream/distress-keyword datasets) inside the Flutter app itself
for offline operation. This backend endpoint exists for:
  1. Server-side re-verification (reduce false SOS alerts)
  2. Analytics / model retraining pipeline

Expects pre-extracted audio features (e.g. MFCCs or the on-device model's
confidence score) rather than raw audio, to keep bandwidth low.
"""
from config import settings

DISTRESS_KEYWORDS = ["help", "bachao", "save me", "call police", "leave me"]


def classify_distress(scream_confidence: float, transcribed_text: str = "") -> dict:
    """
    scream_confidence: float 0-1 from the on-device acoustic classifier
    transcribed_text: optional speech-to-text output for keyword matching
    """
    keyword_hit = any(k in transcribed_text.lower() for k in DISTRESS_KEYWORDS)

    # Combine acoustic + linguistic signals
    combined_score = scream_confidence
    if keyword_hit:
        combined_score = min(1.0, combined_score + 0.25)

    is_distress = combined_score >= settings.SCREAM_CONFIDENCE_THRESHOLD

    return {
        "scream_confidence": scream_confidence,
        "keyword_detected": keyword_hit,
        "combined_score": round(combined_score, 3),
        "is_distress": is_distress,
        "action": "TRIGGER_SOS" if is_distress else "MONITOR",
    }
