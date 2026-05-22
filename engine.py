from datetime import datetime
from config import AIRPORT_COORDS

# ✈ ROUTE DURATIONS (seconds)
ROUTE_DURATION = {
    ("DEL", "BOM"): 2 * 60 * 60,
    ("DEL", "BLR"): int(2.5 * 60 * 60),
    ("DEL", "MAA"): int(2.5 * 60 * 60),
    ("DEL", "HYD"): 2 * 60 * 60,
    ("DEL", "CCU"): 2 * 60 * 60,
    ("DEL", "AMD"): int(1.5 * 60 * 60),
    ("DEL", "PNQ"): int(2 * 60 * 60),
    ("DEL", "COK"): int(3 * 60 * 60),
    ("DEL", "LKO"): int(1 * 60 * 60),
}


def parse_time(dep_time_str):
    try:
        clean = dep_time_str.replace("Z", "").split("+")[0]
        return datetime.strptime(clean, "%Y-%m-%d %H:%M")
    except:
        return None


def get_position(flight, origin_code):
    try:
        # ✅ ONLY SHOW DEPARTED FLIGHTS
        if flight.get("status") != "Departed":
            return None

        dest_code = flight["movement"]["airport"]["iata"]

        # ❌ skip if airport not found
        if origin_code not in AIRPORT_COORDS or dest_code not in AIRPORT_COORDS:
            print("❌ AIRPORT NOT FOUND:", origin_code, dest_code)
            return None

        lat1, lon1 = AIRPORT_COORDS[origin_code]
        lat2, lon2 = AIRPORT_COORDS[dest_code]

        # 🕒 get time
        scheduled = flight["movement"].get("scheduledTime", {})
        dep_time_str = scheduled.get("local") or scheduled.get("utc")

        dep_time = parse_time(dep_time_str)
        if not dep_time:
            print("❌ TIME ERROR:", flight.get("number"))
            return None

        now = datetime.now()
        elapsed = (now - dep_time).total_seconds()

        duration = ROUTE_DURATION.get((origin_code, dest_code), 2 * 60 * 60)

        # 🚫 NOT DEPARTED YET
        if elapsed < 0:
            return None

        # 🚫 LANDED (STRICT FIX 🔥)
        if elapsed >= duration:
            print(f"🛬 {flight.get('number')} LANDED")
            return None

        # ✅ ACTIVE FLIGHT
        progress = elapsed / duration

        # 📍 INTERPOLATION
        lat = lat1 + (lat2 - lat1) * progress
        lon = lon1 + (lon2 - lon1) * progress

        print(f"✈ {flight.get('number')} → {round(progress * 100, 1)}%")

        return {
            "lat": lat,
            "lon": lon
        }

    except Exception as e:
        print("❌ Engine Error:", e)
        return None