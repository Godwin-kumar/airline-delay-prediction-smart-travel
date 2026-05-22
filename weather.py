import requests
import json
import os
from config import airport_data
from datetime import datetime

API_KEY = "8874614a8e944a0a942202601262203"

DATA_DIR = "data"
WEATHER_FILE = os.path.join(DATA_DIR, "weather.json")


# ✅ Create storage
def init_storage():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if not os.path.exists(WEATHER_FILE):
        with open(WEATHER_FILE, "w") as f:
            json.dump({}, f)


# ✅ Load JSON
def load_weather():
    init_storage()
    try:
        with open(WEATHER_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


# ✅ Save JSON
def save_weather(data):
    with open(WEATHER_FILE, "w") as f:
        json.dump(data, f, indent=4)


# 🌦 Fetch one full day weather (24 hours)
def fetch_day_weather(city):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days=1&aqi=no&alerts=no"
    res = requests.get(url).json()

    if "forecast" not in res:
        raise Exception(f"Weather API failed: {res}")

    forecast_day = res["forecast"]["forecastday"][0]
    date_key = forecast_day["date"]          # e.g. 2026-04-22
    hours = forecast_day["hour"]

    hourly_data = {}

    for h in hours:
        time_key = h["time"].split(" ")[1]   # e.g. 01:00

        hourly_data[time_key] = {
            "temp_c": h["temp_c"],
            "condition": h["condition"]["text"],
            "windspeed": h["wind_kph"],
            "humidity": h["humidity"],
            "visibility": h["vis_km"],
            "pressure": h["pressure_mb"],
            "cloud": h["cloud"],
            "precip": h["precip_mm"]
        }

    return date_key, hourly_data


# 🚀 Fetch and store all airports
def preload_all_weather():
    data = {}

    for code, info in airport_data.items():
        city = info["city"]

        try:
            print(f"🌦 Fetching {city}...")

            date_key, hourly_data = fetch_day_weather(city)

            data[code] = {
                date_key: hourly_data
            }

        except Exception as e:
            print(f"❌ Error for {city}: {e}")

    data["_last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_weather(data)

    print("✅ Clean day-wise weather stored successfully")


# 🌦 Get weather by airport + date + time
def get_weather_for_hour(airport_code, date_key, time_key):
    data = load_weather()

    if airport_code not in data:
        raise Exception("Airport not found")

    if date_key not in data[airport_code]:
        raise Exception("Date not found")

    day_data = data[airport_code][date_key]

    if time_key not in day_data:
        time_key = list(day_data.keys())[0]

    return day_data[time_key]


# 🔥 Run directly
if __name__ == "__main__":
    try:
        preload_all_weather()
    except Exception as e:
        print("🚨 ERROR:", e)