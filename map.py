from flask import Blueprint, render_template, jsonify
import json
import os
import time
from engine import get_position

map_bp = Blueprint("map", __name__)

# 🔥 Track last refresh
last_update = 0


@map_bp.route("/map")
def map_page():
    return render_template("map.html")


@map_bp.route("/api/flights")
def get_flights():

    global last_update

    # 🔥 AUTO REFRESH every 5 minutes (300 sec)
    if time.time() - last_update > 300:
        print("🔄 Updating live flights...")
        os.system("python generate_live.py")
        last_update = time.time()

    BASE = os.path.dirname(__file__)
    input_path = os.path.join(BASE, "data", "live_flight.json")

    with open(input_path) as f:
        data = json.load(f)

    live_flights = []

    for origin, flights in data.items():

        for f in flights:

            pos = get_position(f, origin)

            if not pos:
                continue   # skip invalid / inactive flights

            live_flights.append({
                "number": f.get("number", "UNKNOWN"),
                "lat": pos["lat"],
                "lon": pos["lon"],
                "to": f["movement"]["airport"]["iata"],
                "origin": origin,
                "airline": f.get("airline", {}).get("name", "Unknown"),
                "aircraft": f.get("aircraft", {}).get("model", "Unknown"),
                "status": f.get("status", "Unknown")
            })

    print("✈️ Flights:", len(live_flights))

    return jsonify(live_flights)