"""
Voice distress and fall/motion detection routes.
These act as a server-side second opinion on top of the on-device
TFLite models, primarily to reduce false-positive SOS alerts.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

from models import voice_distress, fall_detection

router = APIRouter(prefix="/detect", tags=["Distress & Fall Detection"])


class VoiceDistressRequest(BaseModel):
    scream_confidence: float
    transcribed_text: Optional[str] = ""


class Vector3(BaseModel):
    x: float
    y: float
    z: float


class MotionRequest(BaseModel):
    accel_window: List[Vector3]
    gyro_window: List[Vector3]


@router.post("/voice")
def detect_voice_distress(payload: VoiceDistressRequest):
    return voice_distress.classify_distress(payload.scream_confidence, payload.transcribed_text)


@router.post("/motion")
def detect_fall(payload: MotionRequest):
    accel = [v.model_dump() for v in payload.accel_window]
    gyro = [v.model_dump() for v in payload.gyro_window]
    return fall_detection.analyze_motion(accel, gyro)
