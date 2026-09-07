"""
Secure evidence routes.
Handles metadata registration for audio/video captured during an incident.
Actual binary upload would stream to Firebase Storage / S3; this route
records the secure reference + chain-of-custody metadata.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

from services import firebase_service

router = APIRouter(prefix="/evidence", tags=["Evidence Collection"])


class EvidenceMetadata(BaseModel):
    incident_id: str
    file_type: str          # audio | video
    storage_url: str        # Firebase Storage / S3 signed URL
    duration_seconds: float
    checksum: str            # SHA-256 for tamper-evidence


@router.post("/register")
def register_evidence(payload: EvidenceMetadata):
    incident = firebase_service.get_incident(payload.incident_id)
    if not incident:
        return {"error": "Incident not found"}

    evidence_entry = payload.model_dump()
    evidence_entry["registered_at"] = datetime.utcnow().isoformat()

    existing_evidence = incident.get("evidence", [])
    existing_evidence.append(evidence_entry)

    updated = firebase_service.update_incident(payload.incident_id, {"evidence": existing_evidence})
    return {"incident": updated, "evidence_registered": evidence_entry}
