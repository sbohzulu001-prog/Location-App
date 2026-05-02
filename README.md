# 🚨 Emergency Response — Location Module
**Group 23 & 41 | Flask + Python**

## Setup & Run
```bash
pip install -r requirements.txt
python app.py
```
Then open → http://localhost:5000

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/` | Location Command Dashboard |
| POST | `/api/report_incident` | Report a new incident |
| GET  | `/api/incidents` | List all active incidents |
| GET  | `/api/responders` | List all responders |
| POST | `/api/ai_predict` | AI risk prediction |
| POST | `/api/update_location` | Update user location |

## POST /api/report_incident
```json
{ "lat": -29.8587, "lng": 31.0218, "type": "fire", "description": "...", "density": "high" }
```

## Features
- 📍 Real-time GPS location capture
- 🤖 AI Risk Scoring (CRITICAL / HIGH / MODERATE / LOW)
- 🗺️ Live map with incident & responder markers
- 🚑 Nearest responder dispatch (Haversine distance)
- 🔴 Live incident feed with auto-refresh
- 🎯 Click-to-set location on map
