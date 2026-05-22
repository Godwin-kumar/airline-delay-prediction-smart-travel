import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
import pickle
import joblib

# =========================
# LOAD DATA
# =========================
df = pd.read_csv("data/delay.csv")

# =========================
# TARGET (NO LEAKAGE)
# =========================
df["Delay"] = (df["Departure Delay"] > 15).astype(int)

# ❌ REMOVE LEAKAGE COLUMNS
df.drop(columns=["Departure Delay"], inplace=True, errors="ignore")

# =========================
# FEATURE ENGINEERING
# =========================
df["route"] = df["From"].astype(str) + "_" + df["To"].astype(str)

df["distance_load"] = df["Distance"] * df["Passenger Load Factor"]

df["dep_hour"] = df["SDEP"] // 100

df["is_peak"] = df["dep_hour"].between(7, 10).astype(int)

df["route_freq"] = df.groupby("route")["route"].transform("count")

# SIMPLE WEATHER FEATURE
df["weather_severity"] = (
    df["weather__hourly__precipMM"] +
    df["weather__hourly__cloudcover"] +
    df["weather__hourly__humidity"]
)

# =========================
# ENCODING
# =========================
categorical_cols = ["Airline", "From", "To", "route"]

encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    encoders[col] = le

# =========================
# FEATURES
# =========================
features = [
    "Airline", "From", "To", "route",
    "Distance", "Passenger Load Factor", "distance_load",
    "Airline Rating", "Airport Rating", "Market Share", "OTP Index",
    "dep_hour", "is_peak", "route_freq",
    "weather_severity",
    "weather__hourly__visibility",
    "weather__hourly__pressure"
]

X = df[features].fillna(0)
y = df["Delay"]

# =========================
# SPLIT
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# =========================
# BALANCE
# =========================
scale_pos_weight = len(y_train[y_train == 0]) / len(y_train[y_train == 1])

# =========================
# MODEL (OPTIMIZED)
# =========================
model = xgb.XGBClassifier(
    n_estimators=600,
    learning_rate=0.03,
    max_depth=8,
    subsample=0.8,
    colsample_bytree=0.8,
    gamma=0.2,
    min_child_weight=5,
    scale_pos_weight=scale_pos_weight,
    eval_metric="logloss",
    random_state=42
)

model.fit(X_train, y_train)

# =========================
# EVALUATION
# =========================
y_pred = model.predict(X_test)

print("\n🔥 FINAL ACCURACY:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# =========================
# SAVE
# =========================
# =========================
# SAVE
# =========================

joblib.dump(model, "models/xgb_delay_model.pkl")
joblib.dump(encoders, "models/label_encoders.pkl")
joblib.dump(features, "models/features.pkl")

print("✅ Model saved")

print("✅ Model saved")