from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import json
import math
import random

app = Flask(__name__)
app.secret_key = "emergency_response_secret_2026"

# ─── In-memory store (replace with DB in production) ───────────────────────
active_incidents = []
responders = [
    {"id": "R001", "name": "Unit Alpha",  "type": "Police",    "lat": -29.8587, "lng": 31.0218, "status": "available"},
    {"id": "R002", "name": "Unit Bravo",  "type": "Ambulance", "lat": -29.8620, "lng": 31.0150, "status": "available"},
    {"id": "R003", "name": "Unit Charlie","type": "Fire",      "lat": -29.8550, "lng": 31.0300, "status": "on_call"},
    {"id": "R004", "name": "Unit Delta",  "type": "Ambulance", "lat": -29.8700, "lng": 31.0100, "status": "available"},
]

# ─── Helpers ───────────────────────────────────────────────────────────────
def haversine(lat1, lng1, lat2, lng2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def ai_risk_score(incident_type, time_of_day, location_density):
    """Simple AI risk scoring (replace with ML model in production)."""
    base = {"fire": 85, "medical": 70, "crime": 75, "accident": 65, "flood": 80}.get(incident_type.lower(), 50)
    hour_factor = 1.2 if 22 <= time_of_day or time_of_day <= 5 else 1.0
    density_factor = 1.1 if location_density == "high" else 0.9
    score = min(100, int(base * hour_factor * density_factor))
    if score >= 80:   level = "CRITICAL"
    elif score >= 60: level = "HIGH"
    elif score >= 40: level = "MODERATE"
    else:             level = "LOW"
    return score, level

def find_nearest_responders(lat, lng, incident_type, n=3):
    type_map = {"fire": "Fire", "medical": "Ambulance", "crime": "Police", "accident": "Ambulance", "flood": "Fire"}
    preferred = type_map.get(incident_type.lower(), "Police")
    scored = []
    for r in responders:
        dist = haversine(lat, lng, r["lat"], r["lng"])
        priority = 0 if r["type"] == preferred else 1
        scored.append({**r, "distance_km": round(dist, 2), "eta_min": round(dist / 0.5), "priority": priority})
    scored.sort(key=lambda x: (x["priority"], x["distance_km"]))
    return scored[:n]

# ─── Routes ────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/report_incident", methods=["POST"])
def report_incident():
    data = request.get_json()
    required = ["lat", "lng", "type", "description"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing fields"}), 400

    hour = datetime.now().hour
    risk_score, risk_level = ai_risk_score(data["type"], hour, data.get("density", "medium"))
    nearest = find_nearest_responders(data["lat"], data["lng"], data["type"])

    incident = {
        "id": f"INC-{random.randint(1000,9999)}",
        "lat": data["lat"], "lng": data["lng"],
        "type": data["type"], "description": data["description"],
        "timestamp": datetime.now().isoformat(),
        "risk_score": risk_score, "risk_level": risk_level,
        "assigned": nearest[0]["id"] if nearest else None,
        "status": "active"
    }
    active_incidents.append(incident)

    return jsonify({
        "success": True,
        "incident_id": incident["id"],
        "risk_score": risk_score,
        "risk_level": risk_level,
        "nearest_responders": nearest,
        "message": f"Incident logged. {nearest[0]['name']} dispatched ({nearest[0]['eta_min']} min ETA)." if nearest else "Incident logged."
    })

@app.route("/api/incidents", methods=["GET"])
def get_incidents():
    return jsonify({"incidents": active_incidents})

@app.route("/api/responders", methods=["GET"])
def get_responders():
    return jsonify({"responders": responders})

@app.route("/api/ai_predict", methods=["POST"])
def ai_predict():
    data = request.get_json()
    hour = datetime.now().hour
    score, level = ai_risk_score(data.get("type","unknown"), hour, data.get("density","medium"))
    tips = {
        "CRITICAL": "Dispatch multiple units immediately. Alert hospital ER.",
        "HIGH":     "Priority response required. Notify nearest station.",
        "MODERATE": "Standard response. Monitor for escalation.",
        "LOW":      "Routine response. Single unit sufficient."
    }
    return jsonify({"risk_score": score, "risk_level": level, "recommendation": tips[level]})

@app.route("/api/update_location", methods=["POST"])
def update_location():
    data = request.get_json()
    return jsonify({"success": True, "message": "Location updated", "lat": data.get("lat"), "lng": data.get("lng")})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
