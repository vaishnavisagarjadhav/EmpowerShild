"""
AI Risk Prediction & Safe Route routes.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from datetime import datetime

from models import risk_prediction

router = APIRouter(prefix="/ai", tags=["AI Risk & Routes"])


class RiskQuery(BaseModel):
    latitude: float
    longitude: float


class Waypoint(BaseModel):
    lat: float
    lng: float
    label: str = ""


class RouteQuery(BaseModel):
    waypoints: List[Waypoint]


@router.post("/risk-score")
def get_risk_score(payload: RiskQuery):
    return risk_prediction.predict_risk(payload.latitude, payload.longitude, datetime.utcnow())


@router.post("/safe-route")
def get_safe_route(payload: RouteQuery):
    waypoints = [w.model_dump() for w in payload.waypoints]
    return risk_prediction.suggest_safe_route(waypoints)
