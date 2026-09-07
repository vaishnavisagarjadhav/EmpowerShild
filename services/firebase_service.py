"""
Firebase service layer.
Handles Firestore reads/writes for users, incidents, and guardian data.
Falls back to an in-memory store if Firebase credentials are not configured,
so the API is fully runnable/demoable without a live Firebase project.
"""
from datetime import datetime
from typing import Optional
import os

from config import settings

_firebase_ready = False
db = None

try:
    import firebase_admin
    from firebase_admin import credentials, firestore

    if os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        _firebase_ready = True
except Exception:
    # No credentials found / firebase_admin not configured -> use mock store
    _firebase_ready = False


class _MockCollection:
    """In-memory fallback so the demo runs without real Firebase creds."""
    def __init__(self):
        self._store = {}
        self._counter = 0

    def add(self, data: dict):
        self._counter += 1
        doc_id = f"mock_{self._counter}"
        self._store[doc_id] = data
        return doc_id, data

    def get_all(self):
        return [{"id": k, **v} for k, v in self._store.items()]

    def get(self, doc_id: str):
        return self._store.get(doc_id)

    def update(self, doc_id: str, data: dict):
        if doc_id in self._store:
            self._store[doc_id].update(data)
        return self._store.get(doc_id)


_mock_incidents = _MockCollection()
_mock_users = _MockCollection()


def is_live() -> bool:
    return _firebase_ready


def create_incident(payload: dict) -> dict:
    payload["created_at"] = datetime.utcnow().isoformat()
    payload["status"] = "ACTIVE"
    if _firebase_ready:
        doc_ref = db.collection("incidents").document()
        doc_ref.set(payload)
        return {"id": doc_ref.id, **payload}
    doc_id, data = _mock_incidents.add(payload)
    return {"id": doc_id, **data}


def get_incident(incident_id: str) -> Optional[dict]:
    if _firebase_ready:
        doc = db.collection("incidents").document(incident_id).get()
        return doc.to_dict() if doc.exists else None
    return _mock_incidents.get(incident_id)


def update_incident(incident_id: str, updates: dict) -> Optional[dict]:
    if _firebase_ready:
        db.collection("incidents").document(incident_id).update(updates)
        return get_incident(incident_id)
    return _mock_incidents.update(incident_id, updates)


def list_active_incidents() -> list:
    if _firebase_ready:
        docs = db.collection("incidents").where("status", "==", "ACTIVE").stream()
        return [{"id": d.id, **d.to_dict()} for d in docs]
    return [i for i in _mock_incidents.get_all() if i.get("status") == "ACTIVE"]


def register_user(payload: dict) -> dict:
    if _firebase_ready:
        doc_ref = db.collection("users").document()
        doc_ref.set(payload)
        return {"id": doc_ref.id, **payload}
    doc_id, data = _mock_users.add(payload)
    return {"id": doc_id, **data}
