"""
EmpowerShield API - Main Application Entry Point
==================================================
Run locally:
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000

Docs available at: http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routes import sos, risk, detection, evidence
from services import firebase_service

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=(
        "Women Safety and Emergency Response System — AI-powered SOS, "
        "voice/scream distress detection, fall detection, risk-hotspot "
        "prediction, safe-route recommendation, and secure evidence capture."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Restrict to Guardian Dashboard origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sos.router)
app.include_router(risk.router)
app.include_router(detection.router)
app.include_router(evidence.router)


@app.get("/")
def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "firebase_live": firebase_service.is_live(),
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
