import json
import random
from datetime import datetime, timedelta
import os

# ================= CONFIG =================
airports = [
    {"iata": "DEL", "icao": "VIDP", "name": "Delhi"},
    {"iata": "BOM", "icao": "VABB", "name": "Mumbai"},
    {"iata": "BLR", "icao": "VOBL", "name": "Bangalore"},
    {"iata": "HYD", "icao": "VOHS", "name": "Hyderabad"},
    {"iata": "MAA", "icao": "VOMM", "name": "Chennai"},
    {"iata": "CCU", "icao": "VECC", "name": "Kolkata"},
    {"iata": "COK", "icao": "VOCI", "name": "Kochi"},
    {"iata": "AMD", "icao": "VAAH", "name": "Ahmedabad"},
    {"iata": "PNQ", "icao": "VAPO", "name": "Pune"},
    {"iata": "LKO", "icao": "VILK", "name": "Lucknow"}
]

airlines = [
    {"name": "IndiGo", "iata": "6E", "icao": "IGO"},
    {"name": "Air India", "iata": "AI", "icao": "AIC"},
    {"name": "Vistara", "iata": "UK", "icao": "VTI"}
]

# 🔥 FIX: 3 MONTH RANGE
start_date = datetime(2026, 3, 1)
end_date = datetime(2026, 5, 31)

FLIGHTS_PER_DAY = 15
TIME_SLOTS = list(range(5, 23))

# ================= DATA STRUCTURE =================
flights_data = {}

for airport in airports:
    flights_data[airport["iata"]] = []

# ================= GENERATE =================
current_date = start_date

while current_date <= end_date:

    for origin in airports:

        origin_code = origin["iata"]

        possible_destinations = [
            a for a in airports if a["iata"] != origin_code
        ]

        for _ in range(FLIGHTS_PER_DAY):

            dest = random.choice(possible_destinations)
            airline = random.choice(airlines)

            hour = random.choice(TIME_SLOTS)
            minute = random.choice([0, 15, 30, 45])

            # 🔥 IMPORTANT: USE CURRENT DATE
            local_time = current_date.replace(hour=hour, minute=minute)
            utc_time = local_time - timedelta(hours=5, minutes=30)

            flight_number = f"{airline['iata']} {random.randint(1000,9999)}"

            flight = {
                "movement": {
                    "airport": {
                        "icao": dest["icao"],
                        "iata": dest["iata"],
                        "name": dest["name"],
                        "countryCode": "in",
                        "timeZone": "Asia/Kolkata"
                    },
                    "scheduledTime": {
                        "utc": utc_time.strftime("%Y-%m-%d %H:%MZ"),
                        "local": local_time.strftime("%Y-%m-%d %H:%M+05:30")
                    },
                    "revisedTime": {
                        "utc": utc_time.strftime("%Y-%m-%d %H:%MZ"),
                        "local": local_time.strftime("%Y-%m-%d %H:%M+05:30")
                    },
                    "terminal": str(random.randint(1, 3)),
                    "gate": f"{random.randint(1,50)}{random.choice(['A','B','C'])}",
                    "quality": ["Basic", "Live"]
                },
                "number": flight_number,
                "callSign": airline["icao"] + str(random.randint(1000,9999)),
                "status": random.choice(["Scheduled", "Departed", "Delayed"]),
                "codeshareStatus": "IsOperator",
                "isCargo": False,
                "aircraft": {
                    "reg": "VT-" + random.choice(["IPR","ABC","XYZ"]),
                    "modeS": "80159A",
                    "model": "Airbus A320 NEO"
                },
                "airline": airline
            }

            flights_data[origin_code].append(flight)

    current_date += timedelta(days=1)

# ================= SORT =================
for origin in flights_data:
    flights_data[origin].sort(
        key=lambda x: x["movement"]["scheduledTime"]["local"]
    )

# ================= SAVE =================
os.makedirs("data", exist_ok=True)

with open("data/flights.json", "w") as f:
    json.dump(flights_data, f, indent=4)

print("✅ 90 DAYS flights.json created successfully")