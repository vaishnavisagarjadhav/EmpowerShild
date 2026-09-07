# EmpowerShield
### Women Safety and Emergency Response System — Project Exhibition

An AI-powered personal safety system: instant emergency assistance,
unsafe-situation prediction, automatic distress detection (voice + motion),
live location sharing, secure evidence collection, and safer travel routes —
designed to work fully offline where existing apps (bSafe, My Safetipin,
112 India) fall short.

## Repository structure

```
EmpowerShield/
├── backend/              FastAPI server — SOS, AI risk scoring, detection, evidence
│   ├── main.py            App entry point
│   ├── config.py           Thresholds & settings
│   ├── routes/             sos.py, risk.py, detection.py, evidence.py
│   ├── models/             risk_prediction.py, voice_distress.py, fall_detection.py
│   └── services/           firebase_service.py, notification_service.py
│
├── mobile_app/           Flutter app (Android/iOS)
│   ├── pubspec.yaml
│   └── lib/
│       ├── main.dart
│       ├── screens/        home_screen.dart, safe_route_screen.dart, guardian_dashboard.dart
│       ├── services/       api_service.dart, location_service.dart,
│       │                   sensor_service.dart, voice_detection_service.dart
│       └── widgets/        sos_button.dart
│
├── ai_models/            Model training + TFLite export scripts
│   ├── train_risk_model.py
│   ├── train_fall_detection.py
│   └── convert_to_tflite.py
│
└── dashboard/            Standalone web Guardian Console (quick-demo, no Flutter needed)
    └── index.html
```

## Quick demo (fastest way to show reviewers something running)

**1. Run the backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Open **http://127.0.0.1:8000/docs** — full interactive Swagger UI of every
endpoint (SOS trigger, risk scoring, safe route, voice/fall detection,
evidence registration). This alone is a strong live demo.

**2. Open the Guardian Console**
Just double-click `dashboard/index.html` in a browser (or serve it with
`python -m http.server` inside `dashboard/`). It polls the backend every
5 seconds and lists active SOS incidents in real time — trigger one from
the Swagger docs (`POST /sos/trigger`) and watch it appear.

**3. Run the Flutter app (optional, needs Flutter SDK installed)**
```bash
cd mobile_app
flutter pub get
flutter run
```
Update `ApiService.baseUrl` in `lib/services/api_service.dart` to point
at your backend (use `10.0.2.2:8000` for the Android emulator, or your
machine's LAN IP for a physical device).

## How this maps to the project brief

| Brief requirement                         | Where it lives |
|--------------------------------------------|----------------|
| One-Tap SOS / instant emergency assistance | `mobile_app/lib/widgets/sos_button.dart`, `backend/routes/sos.py` |
| AI-powered unsafe situation prediction     | `backend/models/risk_prediction.py`, `ai_models/train_risk_model.py` |
| Automatic distress detection (voice)       | `backend/models/voice_distress.py`, `mobile_app/lib/services/voice_detection_service.dart` |
| Automatic distress detection (motion/fall) | `backend/models/fall_detection.py`, `mobile_app/lib/services/sensor_service.dart` |
| Live location sharing with trusted contacts| `mobile_app/lib/services/location_service.dart`, `backend/services/notification_service.py` |
| Secure evidence collection                 | `backend/routes/evidence.py` |
| Safer travel route recommendations         | `backend/models/risk_prediction.py::suggest_safe_route`, `mobile_app/lib/screens/safe_route_screen.dart` |
| Guardian Dashboard / real-time monitoring  | `dashboard/index.html`, `mobile_app/lib/screens/guardian_dashboard.dart` |
| No network dependency (offline AI)         | On-device TFLite models (`ai_models/convert_to_tflite.py`) + `offline_mode` SMS fallback in `notification_service.py` |
| Reduce false SOS alerts using AI           | Server-side re-verification in `voice_distress.py` (keyword + acoustic score fusion) and `fall_detection.py` (dual accel+gyro thresholding) |

## Software stack (as presented)

| Component      | Technology              |
|----------------|--------------------------|
| Mobile App     | Flutter                  |
| Backend        | FastAPI                  |
| Database       | Firebase Firestore       |
| Authentication | Firebase Auth            |
| Maps           | Google Maps SDK          |
| Notifications  | Firebase Cloud Messaging |
| AI / ML        | TFLite, MediaPipe, scikit-learn |
| Dashboard      | Web (HTML/JS) — or Flutter Web / React |

## Connecting real Firebase

The backend runs out of the box with an **in-memory mock database** so it's
demoable with zero setup. To go live:

1. Create a Firebase project → Project Settings → Service Accounts →
   generate a private key → save as `backend/firebase_credentials.json`.
2. Set `FIREBASE_DB_URL` in a `.env` file inside `backend/`.
3. Restart the server — `firebase_live` in the root `/` response will
   flip to `true` and all incident/user data now persists to Firestore.

## Training the AI models on real data

Both `ai_models/train_risk_model.py` and `train_fall_detection.py` ship
with synthetic data generators so they run immediately for demonstration.
For a production-accurate model, swap in:
- **Risk prediction**: historical incident-report data (state police
  open-data portals, NCRB crime statistics) with `latitude, longitude, hour, label` columns.
- **Fall detection**: a labeled public dataset such as SisFall, MobiFall,
  or UMAFall.

Then run `convert_to_tflite.py` to export a quantized, on-device model for
fully offline inference in the Flutter app.

## Team

| Member | Roll No. | Contribution |
|---|---|---|
| Kashish Raj | 25BAI11409 | Data Collection & Preprocessing |
| Vaishnavi Jadhav | 25BAI11401 | Machine Learning Models (Risk Prediction, Hotspot Analysis) |
| Buddha S | 25BAI11592 | AI Modules (Voice, Fall, Computer Vision) |
| Tanishq Gupta | 25BAI11026 | Backend & Database |
| Anusha Sinha | 25BAI10793 | Mobile App & Maps |
| Sumanth B | 25BAI11402 | Dashboard, Testing & Deployment |
