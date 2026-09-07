"""
AI Risk Prediction Module
--------------------------
Predicts how unsafe a given location/time is, based on:
  - time of day
  - historical crime-hotspot density near the coordinates
  - population/lighting proxy score (simulated for demo)

In production this loads a trained scikit-learn / TFLite model
(see ai_models/train_risk_model.py). For the demo it falls back
to a transparent rule-based scorer so the API always returns a result.
"""
import math
import os
from datetime import datetime

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "ai_models", "risk_model.joblib")

_model = None
try:
    import joblib
    if os.path.exists(MODEL_PATH):
        _model = joblib.load(MODEL_PATH)
except Exception:
    _model = None

# Simulated historical incident hotspots: (lat, lng, severity 0-1)
KNOWN_HOTSPOTS = [
    (28.6139, 77.2090, 0.9),   # example: New Delhi central
    (19.0760, 72.8777, 0.6),   # Mumbai
    (23.2599, 77.4126, 0.7),   # Bhopal
]


def _haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _time_risk_factor(hour: int) -> float:
    """Late night / early morning hours carry higher baseline risk."""
    if 22 <= hour or hour <= 4:
        return 0.9
    if 19 <= hour < 22 or 5 <= hour < 7:
        return 0.5
    return 0.15


def _hotspot_proximity_score(lat: float, lng: float) -> float:
    score = 0.0
    for h_lat, h_lng, severity in KNOWN_HOTSPOTS:
        dist = _haversine_km(lat, lng, h_lat, h_lng)
        if dist < 5:
            score = max(score, severity * (1 - dist / 5))
    return score


def predict_risk(lat: float, lng: float, timestamp: datetime = None) -> dict:
    timestamp = timestamp or datetime.utcnow()

    if _model is not None:
        features = [[lat, lng, timestamp.hour]]
        proba = float(_model.predict_proba(features)[0][1])
        risk_score = proba
    else:
        time_factor = _time_risk_factor(timestamp.hour)
        hotspot_factor = _hotspot_proximity_score(lat, lng)
        risk_score = round(min(1.0, 0.5 * time_factor + 0.5 * hotspot_factor), 3)

    if risk_score >= 0.7:
        level = "HIGH"
    elif risk_score >= 0.4:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "latitude": lat,
        "longitude": lng,
        "risk_score": risk_score,
        "risk_level": level,
        "evaluated_at": timestamp.isoformat(),
        "model_source": "trained_model" if _model else "rule_based_fallback",
    }


def suggest_safe_route(waypoints: list) -> dict:
    """
    Given a list of {lat, lng} waypoints, score each and flag risky segments.
    Route re-planning (actual pathfinding) would call Google Maps Directions API
    then re-score alternate routes here.
    """
    scored = []
    for point in waypoints:
        r = predict_risk(point["lat"], point["lng"])
        scored.append({**point, "risk_level": r["risk_level"], "risk_score": r["risk_score"]})

    overall_risk = max(p["risk_score"] for p in scored) if scored else 0
    flagged = [p for p in scored if p["risk_level"] == "HIGH"]

    return {
        "waypoints": scored,
        "overall_risk_score": overall_risk,
        "high_risk_segments": flagged,
        "recommendation": (
            "Consider an alternate route avoiding flagged segments."
            if flagged else "Route looks reasonably safe."
        ),
    }
