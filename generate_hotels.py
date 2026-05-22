import json
import random
import os

cities = {
    "DEL": "Delhi",
    "BOM": "Mumbai",
    "BLR": "Bangalore",
    "HYD": "Hyderabad",
    "MAA": "Chennai",
    "CCU": "Kolkata",
    "COK": "Kochi",
    "AMD": "Ahmedabad",
    "PNQ": "Pune",
    "LKO": "Lucknow"
}

# realistic hotel names
hotel_names = [
    "Taj Hotel",
    "Radisson Blu",
    "ITC Grand",
    "Marriott",
    "Hyatt Regency",
    "The Leela Palace",
    "Holiday Inn",
    "Novotel",
    "Lemon Tree Hotel",
    "FabHotel",
    "Treebo Trend",
    "OYO Premium"
]

# realistic locations
locations = [
    "Airport Road",
    "City Center",
    "MG Road",
    "Near Railway Station",
    "Business District",
    "IT Park Area",
    "Main Market",
    "Ring Road",
    "Metro Station Area"
]

hotel_data = {}

for code, city in cities.items():

    hotel_data[code] = []

    for i in range(10):  # 🔥 10 hotels per city

        name = random.choice(hotel_names)

        location = random.choice(locations)

        hotel = {
            "name": f"{name} {city}",
            "rating": round(random.uniform(3.5, 5.0), 1),
            "price": random.randint(1500, 7000),

            # 🔥 FULL ADDRESS
            "address": f"{location}, {city}, India",

            # 🔥 DISTANCE FROM AIRPORT
            "distance": f"{random.randint(1,15)} km from Airport"
        }

        hotel_data[code].append(hotel)

# SAVE
os.makedirs("data", exist_ok=True)

with open("data/hotels.json", "w") as f:
    json.dump(hotel_data, f, indent=4)

print("✅ 10 realistic hotels per city generated")import json
import random
import os

cities = {
    "DEL": "Delhi",
    "BOM": "Mumbai",
    "BLR": "Bangalore",
    "HYD": "Hyderabad",
    "MAA": "Chennai",
    "CCU": "Kolkata",
    "COK": "Kochi",
    "AMD": "Ahmedabad",
    "PNQ": "Pune",
    "LKO": "Lucknow"
}

# realistic hotel names
hotel_names = [
    "Taj Hotel",
    "Radisson Blu",
    "ITC Grand",
    "Marriott",
    "Hyatt Regency",
    "The Leela Palace",
    "Holiday Inn",
    "Novotel",
    "Lemon Tree Hotel",
    "FabHotel",
    "Treebo Trend",
    "OYO Premium"
]

# realistic locations
locations = [
    "Airport Road",
    "City Center",
    "MG Road",
    "Near Railway Station",
    "Business District",
    "IT Park Area",
    "Main Market",
    "Ring Road",
    "Metro Station Area"
]

hotel_data = {}

for code, city in cities.items():

    hotel_data[code] = []

    for i in range(10):  # 🔥 10 hotels per city

        name = random.choice(hotel_names)

        location = random.choice(locations)

        hotel = {
            "name": f"{name} {city}",
            "rating": round(random.uniform(3.5, 5.0), 1),
            "price": random.randint(1500, 7000),

            # 🔥 FULL ADDRESS
            "address": f"{location}, {city}, India",

            # 🔥 DISTANCE FROM AIRPORT
            "distance": f"{random.randint(1,15)} km from Airport"
        }

        hotel_data[code].append(hotel)

# SAVE
os.makedirs("data", exist_ok=True)

with open("data/hotels.json", "w") as f:
    json.dump(hotel_data, f, indent=4)

print("✅ 10 realistic hotels per city generated")