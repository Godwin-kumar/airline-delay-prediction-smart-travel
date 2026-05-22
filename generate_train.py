import json
from datetime import datetime, timedelta

print("🚆 Generating CLEAN train data (today)...")

# ✅ 10 airports
airports = ["DEL", "BOM", "BLR", "HYD", "MAA", "CCU", "COK", "AMD", "PNQ", "LKO"]

trains = []

# ✅ TODAY DATE (FIXED)
date_str = datetime.now().strftime("%Y-%m-%d")

# ✅ time range
start_time = datetime.strptime("05:00", "%H:%M")
end_time = datetime.strptime("23:45", "%H:%M")

current_time = start_time

while current_time <= end_time:

    dep_time = current_time.strftime("%H:%M")

    for origin in airports:
        for destination in airports:

            if origin == destination:
                continue

            # ✅ safe duration (no randomness)
            duration = 5 + ((len(origin) + len(destination)) % 5)  # 5–9 hrs

            # ✅ arrival calculation
            dep_hour, dep_min = map(int, dep_time.split(":"))
            total_minutes = dep_hour * 60 + dep_min + duration * 60

            arr_hour = (total_minutes // 60) % 24
            arr_min = total_minutes % 60

            arrival_time = f"{arr_hour:02d}:{arr_min:02d}"

            trains.append({
                "train_no": f"{origin}{destination}{dep_time.replace(':','')}",
                "train_name": f"Express ({origin}-{destination})",
                "from": origin,
                "to": destination,
                "departure": dep_time,
                "arrival": arrival_time,
                "duration": duration,
                "price": 300 + (duration * 120),
                "date": date_str   # 🔥 FIXED HERE
            })

    # ✅ every 45 mins
    current_time += timedelta(minutes=45)

print("TOTAL TRAINS:", len(trains))

with open("data/trains.json", "w", encoding="utf-8") as f:
    json.dump(trains, f, indent=4)

print("✅ Clean train data created successfully")