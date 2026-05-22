from flask import Flask, render_template, request
import json
import os
from datetime import datetime
from weather import get_weather_for_hour
import joblib
import pandas as pd
import numpy as np
from map import map_bp

app = Flask(__name__)

DATA_FILE = os.path.join("data", "flights.json")
TRAIN_FILE = os.path.join("data", "trains.json")
HOTEL_FILE = os.path.join("data", "hotels.json")

# ================= LOAD MODEL =================
try:
    model = joblib.load("models/xgb_delay_model.pkl")
    encoders = joblib.load("models/label_encoders.pkl")
    features = joblib.load("models/features.pkl")
    print("✅ Model Loaded")
except:
    model = None
    encoders = {}
    features = []
    print("⚠️ Model Not Loaded")

# ================= HELPERS =================
def safe_encode(encoder, value):
    try:
        if encoder is None:
            return 0
        if value not in encoder.classes_:
            encoder.classes_ = np.append(encoder.classes_, value)
        return encoder.transform([value])[0]
    except:
        return 0

def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def load_flights():
    return load_json(DATA_FILE, {})

def load_trains():
    return load_json(TRAIN_FILE, [])

def load_hotels():
    return load_json(HOTEL_FILE, {})

def get_hourly_traffic(flights):
    hourly = {}

    for flight in flights:
        try:
            sched = flight.get("movement", {}).get("scheduledTime", {}).get("local")
            if not sched:
                continue
            hh = sched.split(" ")[1][:2]
            hourly[hh] = hourly.get(hh, 0) + 1
        except:
            pass

    return hourly

# ================= ROUTES =================
@app.route("/")
def home():
    with open("data/weather.json", "r", encoding="utf-8") as f:
        weather = json.load(f)

    flights_data = load_flights()

    flight_count = 0
    for airport, flights in flights_data.items():
        flight_count += len(flights)

    airport_count = len(flights_data)

    return render_template(
        "index.html",
        weather=weather,
        flight_count=flight_count,
        airport_count=airport_count
    )

@app.route("/airports")
def airports():
    data = load_flights()
    return render_template("airports.html", airports=list(data.keys()))

@app.route("/search")
def search_page():
    return render_template("search.html")

@app.route("/search_flights", methods=["GET"])
def search_flights():
    origin = request.args.get("origin", "").upper().strip()
    destination = request.args.get("destination", "").upper().strip()
    selected_date = request.args.get("date", "")

    flights = load_flights().get(origin, [])
    matched = []
    now = datetime.now()

    for flight in flights:
        try:
            movement = flight.get("movement", {})
            airport = movement.get("airport", {})
            dest_code = airport.get("iata", "").upper()

            sched_local = movement.get("scheduledTime", {}).get("local")
            if not sched_local:
                continue

            parsed_time = datetime.strptime(
                sched_local.split("+")[0],
                "%Y-%m-%d %H:%M"
            )

            if (
                dest_code == destination and
                parsed_time.strftime("%Y-%m-%d") == selected_date
            ):
                flight["formatted_time"] = parsed_time.strftime("%H:%M")
                flight["destination"] = f"{airport.get('name')} ({dest_code})"
                flight["is_future"] = parsed_time > now
                matched.append(flight)

        except:
            continue

    return render_template(
        "search_results.html",
        flights=matched,
        origin=origin,
        destination=destination,
        date=selected_date
    )

@app.route("/departures/<airport_code>")
def departures(airport_code):
    flights = load_flights().get(airport_code, [])
    selected_date = request.args.get("date")
    now = datetime.now()

    filtered_flights = []

    for flight in flights:
        try:
            movement = flight.get("movement", {})
            sched_local = movement.get("scheduledTime", {}).get("local")

            if not sched_local:
                continue

            parsed_time = datetime.strptime(
                sched_local.split("+")[0],
                "%Y-%m-%d %H:%M"
            )

            if selected_date:
                if parsed_time.strftime("%Y-%m-%d") != selected_date:
                    continue

            airport = movement.get("airport", {})

            flight["formatted_time"] = parsed_time.strftime("%H:%M")
            flight["date"] = parsed_time.strftime("%Y-%m-%d")
            flight["is_future"] = parsed_time > now
            flight["destination"] = f"{airport.get('name')} ({airport.get('iata')})"

            filtered_flights.append(flight)

        except:
            continue

    return render_template(
        "departures.html",
        airport=airport_code,
        flights=filtered_flights
    )

# ================= PREDICT =================
@app.route("/predict", methods=["POST"])
def predict():
    airline = request.form.get("airline")
    origin = request.form.get("origin")
    destination = request.form.get("destination")
    time_str = request.form.get("time")
    selected_date = request.form.get("date")

    hour = int(time_str.split(":")[0])
    dep_hour = hour
    time_key = f"{hour:02d}:00"
           

    try:
        source_weather = get_weather_for_hour(origin, selected_date, time_key)
    except:
        source_weather = {}

    try:
        dest_weather = get_weather_for_hour(destination, selected_date, time_key)
    except:
        dest_weather = {}

    weather_rows = [w for w in [source_weather, dest_weather] if w]

    visibility_values = [w.get("visibility", 0) for w in weather_rows]
    pressure_values = [w.get("pressure", 0) for w in weather_rows]

    visibility = min(visibility_values) if visibility_values else 0
    pressure = sum(pressure_values) / len(pressure_values) if pressure_values else 0

    all_flights = load_flights().get(origin, [])
    route_flights = []

    for f in all_flights:
        try:
            dest_code = f.get("movement", {}).get("airport", {}).get("iata")
            if dest_code == destination:
                route_flights.append(f)
        except:
            pass

    route_freq = len(route_flights)
    total_departures = len(all_flights)

    hourly_traffic = get_hourly_traffic(all_flights)
    current_hour_count = hourly_traffic.get(f"{hour:02d}", 0)

    avg_traffic = (
        sum(hourly_traffic.values()) / len(hourly_traffic)
        if hourly_traffic else 0
    )

    is_peak = int(current_hour_count > avg_traffic)

    distance = route_freq if route_freq else total_departures
    plf = route_freq / total_departures if total_departures else 0
    distance_load = distance * plf
    market_share = plf
    otp = total_departures if total_departures else 0
    airline_rating = route_freq
    airport_rating = total_departures
    route = f"{origin}_{destination}"

    airline_enc = safe_encode(encoders.get("Airline"), airline)
    origin_enc = safe_encode(encoders.get("From"), origin)
    dest_enc = safe_encode(encoders.get("To"), destination)
    route_enc = safe_encode(encoders.get("route"), route)

    input_dict = {
    "Airline": airline_enc,
    "From": origin_enc,
    "To": dest_enc,
    "route": route_enc,

    "Distance": distance,

    "Passenger Load Factor": plf,

    "distance_load": distance_load,

    "Airline Rating": airline_rating,

    "Airport Rating": airport_rating,

    "Market Share": market_share,

    "OTP Index": otp,

    "dep_hour": dep_hour,

    "is_peak": is_peak,

    "route_freq": route_freq,

    "weather_severity": (
        source_weather.get("humidity", 0)
        + source_weather.get("cloud", 0)
        + source_weather.get("precip", 0)
    ),

    "weather__hourly__visibility": visibility,

    "weather__hourly__pressure": pressure,
}

    for col in features:
        if col not in input_dict:
            input_dict[col] = 0

    input_data = pd.DataFrame(
        [[input_dict[col] for col in features]],
        columns=features
    )
    try:
        probs = model.predict_proba(input_data)[0]

        on_time_prob = round(probs[0] * 100, 2)
        delay_prob = round(probs[1] * 100, 2)

        

        result = "Delayed" if delay_prob >= 60 else "On Time"
    except Exception as e:
        print("Prediction Error:", e)
        result = "Model Error"
        on_time_prob = 0
        delay_prob = 0

    # ================= REASONS =================
    reasons = []

    if result == "Delayed":

        if source_weather:
            if source_weather.get("precip", 0) > 0:
                reasons.append(
                     f"Moderate rainfall near {origin} affecting departures"
                )

            if source_weather.get("visibility", 10) < 10:
                reasons.append(
                    f"Poor visibility conditions at {origin}"
                )

            if source_weather.get("windspeed", 0) > 10:
                reasons.append(
                    f"Strong wind activity reported at {origin}"
                )

            if source_weather.get("humidity", 0) > 60:
                reasons.append(
                    f"High atmospheric humidity around {origin}"
                )

        if dest_weather:
            if dest_weather.get("precip", 0) > 0:
                reasons.append(
                      f"Rainfall near destination airport {destination}"
                )

            if dest_weather.get("visibility", 10) < 8:
                reasons.append(
                      f"Low visibility at destination airport {destination}"
                )

            if dest_weather.get("windspeed", 0) > 20:
                reasons.append(
                     f"Strong winds near destination airport {destination}"
                )

            if dest_weather.get("humidity", 0) > 75:
                reasons.append(
                    f"High humidity levels near {destination}"
                )

        if current_hour_count >= (avg_traffic * 1.5) and delay_prob >= 60:
            reasons.append(f"Peak hour congestion around {time_str}")

        if not reasons:
            reasons.append("Operational delay risk detected by model")

    trains = load_trains()
    hotels = load_hotels().get(destination, [])

    return render_template(
        "prediction_result.html",
        result=result,
        on_time_prob=on_time_prob,
        delay_prob=delay_prob,
        origin=origin,
        destination=destination,
        time=time_str,
        date=selected_date,
        trains=trains,
        hotels=hotels,
        reasons=reasons
    )

@app.route("/alternatives")
def alternatives_page_query():
    origin = request.args.get("origin")
    destination = request.args.get("destination")
    time_str = request.args.get("time")

    flights = load_flights().get(origin, [])
    selected_time = datetime.strptime(time_str, "%H:%M")

    filtered = []

    for f in flights:
        try:
            dest_code = f.get("movement", {}).get("airport", {}).get("iata")
            sched = f.get("movement", {}).get("scheduledTime", {}).get("local")

            if dest_code != destination or not sched:
                continue

            flight_time = datetime.strptime(
                sched.split("+")[0],
                "%Y-%m-%d %H:%M"
            )

            if flight_time.time() > selected_time.time():
                filtered.append(f)

        except:
            continue

    filtered = sorted(
        filtered,
        key=lambda x: x["movement"]["scheduledTime"]["local"]
    )[:10]

    return render_template(
        "alternatives.html",
        flights=filtered,
        origin=origin,
        destination=destination
    )
@app.route("/trains_smart")
def smart_trains():
    origin = request.args.get("origin")
    destination = request.args.get("destination")
    time_str = request.args.get("time")

    trains = load_trains()
    selected_time = datetime.strptime(time_str, "%H:%M")

    filtered = []

    for t in trains:
        try:
            if t["from"] == origin and t["to"] == destination:
                train_time = datetime.strptime(t["departure"], "%H:%M")
                if train_time.time() > selected_time.time():
                    filtered.append(t)
        except:
            continue

    filtered = sorted(filtered, key=lambda x: x["departure"])[:5]

    if not filtered:
        filtered = trains[:3]

    return render_template("trains.html", trains=filtered)

@app.route("/hotels_smart")
def smart_hotels():
    origin = request.args.get("origin")
    hotel_data = load_hotels()

    hotels = hotel_data.get(origin, [])

    if not hotels and hotel_data:
        hotels = list(hotel_data.values())[0]

    hotels = hotels[:5]

    return render_template(
        "hotels.html",
        hotels=hotels,
        city=origin
    )
app.register_blueprint(map_bp)

@app.route("/test")
def test():
    return "APP WORKING"

if __name__ == "__main__":
    app.run(debug=True)