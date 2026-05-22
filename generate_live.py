import json
from datetime import datetime
from config import AIRPORT_COORDS

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


def parse_time(t):
    clean = t.replace("Z", "").split("+")[0]
    return datetime.strptime(clean, "%Y-%m-%d %H:%M")


# 📂 LOAD MAIN DATA
with open("data/flights.json") as f:
    data = json.load(f)

now = datetime.now()

live_data = {}

for origin, flights in data.items():

    for f in flights:

        dest = f["movement"]["airport"]["iata"]
        dep_str = f["movement"]["scheduledTime"].get("local") or f["movement"]["scheduledTime"].get("utc")

        try:
            dep_time = parse_time(dep_str)
        except:
            continue

        duration = ROUTE_DURATION.get((origin, dest), 2 * 60 * 60)

        elapsed = (now - dep_time).total_seconds()

        # ✅ ONLY ACTIVE FLIGHTS
        if 0 < elapsed < duration:

            if origin not in live_data:
                live_data[origin] = []

            live_data[origin].append(f)


# 💾 SAVE LIVE FILE
with open("data/live_flight.json", "w") as f:
    json.dump(live_data, f, indent=2)

print("✈️ Active flights:", sum(len(v) for v in live_data.values()))