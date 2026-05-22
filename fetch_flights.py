import requests
import json
from datetime import datetime
import os
import time

API_KEY = "f1d22a0927msh1a6845fa5474264p106d17jsnf9fdffef7507"
API_HOST = "aerodatabox.p.rapidapi.com"

# 🔥 10 AIRPORT NETWORK
AIRPORTS = ["DEL", "BOM", "MAA", "BLR", "HYD", "CCU", "COK", "AMD", "PNQ", "LKO"]

DATA_FILE = "data/flights.json"

os.makedirs("data", exist_ok=True)


# 🔥 TIME WINDOW LOGIC (FINAL)
def get_time_range():
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")

    # 🌞 DAY MODE (FIXED FULL BLOCK)
    if 6 <= now.hour < 18:
        return f"{today}T06:00", f"{today}T17:50"

    # 🌙 NIGHT MODE
    else:
        return f"{today}T18:00", f"{today}T23:59"


def fetch_airport(airport):
    from_time, to_time = get_time_range()

    url = f"https://{API_HOST}/flights/airports/iata/{airport}/{from_time}/{to_time}"

    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }

    params = {
        "direction": "Departure",
        "withCancelled": "false"
    }

    try:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            print(f"\n✅ {airport} fetched")

            flights = response.json().get("departures", [])

            filtered = []

            for f in flights:
                try:
                    dest = f["movement"]["airport"]["iata"]
                    country = f["movement"]["airport"].get("countryCode", "").lower()

                    # 🔥 ONLY YOUR NETWORK (NO MOSCOW)
                    if (
                        dest in AIRPORTS and
                        dest != airport and
                        country == "in"
                    ):
                        filtered.append(f)

                except:
                    continue

            # 🔥 SORT
            filtered.sort(
                key=lambda x: x.get("movement", {})
                .get("scheduledTime", {})
                .get("local", "")
            )

            print(f"➡ {airport}: {len(filtered)} flights stored")

            return filtered

        elif response.status_code == 403:
            print("❌ 403 Forbidden – Check API key")
            return []

        elif response.status_code == 429:
            print("⚠️ Rate limit hit – waiting")
            time.sleep(5)
            return []

        else:
            print(f"❌ {airport} failed:", response.status_code)
            return []

    except Exception as e:
        print("🔥 Error:", e)
        return []


# ================= RESET DATA BASED ON TIME =================
now = datetime.now()

# 🌙 NIGHT → CLEAR OLD DATA
if now.hour >= 18 or now.hour < 6:
    print("🌙 Night mode → clearing old data")
    all_data = {}

# 🌞 DAY → ALSO RESET (to avoid mixing)
else:
    print("🌞 Day mode → fresh full dataset")
    all_data = {}


# ================= FETCH ALL AIRPORTS =================
total_all = 0

for airport in AIRPORTS:

    new_flights = fetch_airport(airport)

    # 🔥 REPLACE (NOT APPEND)
    all_data[airport] = new_flights

    airport_total = len(new_flights)
    total_all += airport_total

    print(f"📊 {airport}: {airport_total} flights")

    time.sleep(1.5)


# ================= SAVE =================
with open(DATA_FILE, "w") as f:
    json.dump(all_data, f, indent=4)

print("\n🚀 Flights saved successfully.")
print(f"🔥 TOTAL FLIGHTS: {total_all}")