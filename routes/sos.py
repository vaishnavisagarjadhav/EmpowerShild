"""
SOS / Emergency routes
Handles: manual SOS trigger, AI-triggered SOS, incident status updates,
and Guardian Dashboard live incident feed.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from services import firebase_service, notification_service

router = APIRouter(prefix="/sos", tags=["SOS & Emergency"])


class GuardianContact(BaseModel):
    name: str
    phone: str
    fcm_token: Optional[str] = None


class SOSRequest(BaseModel):
    user_id: str
    latitude: float
    longitude: float
    trigger_type: str = "manual"          # manual | voice_ai | fall_ai | route_ai
    offline_mode: bool = False
    guardian_contacts: List[GuardianContact] = []
    notes: Optional[str] = None


class IncidentUpdate(BaseModel):
    status: str    # ACTIVE | RESOLVED | FALSE_ALARM


@router.post("/trigger")
def trigger_sos(payload: SOSRequest):
    """
    Step 1-3 of the process flow:
    SOS pressed / AI detects danger -> live location captured -> alert + calls contacts
    """
    incident = firebase_service.create_incident({
        "user_id": payload.user_id,
        "latitude": payload.latitude,
        "longitude": payload.longitude,
        "trigger_type": payload.trigger_type,
        "notes": payload.notes,
    })

    notify_result = notification_service.notify_guardians(
        [c.model_dump() for c in payload.guardian_contacts],
        incident,
        offline=payload.offline_mode,
    )

    return {
        "incident": incident,
        "notification_result": notify_result,
        "next_steps": [
            "audio_video_recording_started",
            "live_tracking_enabled",
            "guardian_dashboard_updated",
        ],
    }


@router.patch("/incident/{incident_id}")
def update_incident_status(incident_id: str, payload: IncidentUpdate):
    updated = firebase_service.update_incident(incident_id, {
        "status": payload.status,
        "resolved_at": datetime.utcnow().isoformat() if payload.status != "ACTIVE" else None,
    })
    if not updated:
        return {"error": "Incident not found"}
    return {"incident": updated}


@router.get("/incident/{incident_id}")
def get_incident(incident_id: str):
    incident = firebase_service.get_incident(incident_id)
    if not incident:
        return {"error": "Incident not found"}
    return {"incident": incident}


@router.get("/active")
def list_active_incidents():
    """Feeds the Guardian Dashboard's live incident map."""
    return {"active_incidents": firebase_service.list_active_incidents()}
