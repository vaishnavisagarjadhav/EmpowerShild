"""
EmpowerShield - Global configuration
Loads environment variables and holds app-wide constants.
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME: str = "EmpowerShield API"
    VERSION: str = "1.0.0"

    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = os.getenv(
        "FIREBASE_CREDENTIALS_PATH", "firebase_credentials.json"
    )
    FIREBASE_DB_URL: str = os.getenv("FIREBASE_DB_URL", "")

    # Risk model thresholds
    HIGH_RISK_THRESHOLD: float = 0.7
    MEDIUM_RISK_THRESHOLD: float = 0.4

    # Fall detection thresholds (accelerometer magnitude in g)
    FALL_ACCEL_THRESHOLD: float = 2.5
    FALL_GYRO_THRESHOLD: float = 200.0  # deg/s spike

    # Voice distress detection
    SCREAM_CONFIDENCE_THRESHOLD: float = 0.75

    # Twilio / SMS fallback (offline / no-internet emergency path)
    SMS_GATEWAY_NUMBER: str = os.getenv("SMS_GATEWAY_NUMBER", "")


settings = Settings()
