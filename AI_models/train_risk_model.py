"""
Train Risk Prediction Model
=============================
Trains a simple, explainable classifier that predicts whether a
(latitude, longitude, hour_of_day) combination is a "high risk" instance,
using historical incident-report data as positive samples and randomly
sampled safe locations/times as negative samples.

Usage:
    python train_risk_model.py --data historical_incidents.csv

Expected CSV columns: latitude, longitude, hour, label (1 = incident, 0 = safe)

Replace the synthetic data generator below with your real crime/incident
dataset (e.g. state police open-data portals, NCRB data) before deployment.
"""
import argparse
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os


def generate_synthetic_dataset(n=4000, seed=42) -> pd.DataFrame:
    """Placeholder dataset generator — swap for real historical incident data."""
    rng = np.random.default_rng(seed)

    hotspots = [(28.6139, 77.2090), (19.0760, 72.8777), (23.2599, 77.4126)]

    rows = []
    # Positive samples: near hotspots, late-night hours
    for _ in range(n // 2):
        base_lat, base_lng = hotspots[rng.integers(0, len(hotspots))]
        lat = base_lat + rng.normal(0, 0.02)
        lng = base_lng + rng.normal(0, 0.02)
        hour = int(rng.choice([22, 23, 0, 1, 2, 3, 4], p=[0.2, 0.2, 0.2, 0.15, 0.1, 0.1, 0.05]))
        rows.append([lat, lng, hour, 1])

    # Negative samples: random locations, daytime-biased hours
    for _ in range(n // 2):
        lat = rng.uniform(8.0, 35.0)
        lng = rng.uniform(68.0, 90.0)
        hour = int(rng.choice(range(24)))
        rows.append([lat, lng, hour, 0])

    return pd.DataFrame(rows, columns=["latitude", "longitude", "hour", "label"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, default=None, help="Path to CSV of historical incidents")
    parser.add_argument("--out", type=str, default="risk_model.joblib")
    args = parser.parse_args()

    if args.data and os.path.exists(args.data):
        df = pd.read_csv(args.data)
    else:
        print("No dataset provided — using synthetic demo data. "
              "Replace with real incident-report data for production accuracy.")
        df = generate_synthetic_dataset()

    X = df[["latitude", "longitude", "hour"]]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print(classification_report(y_test, preds))

    joblib.dump(model, args.out)
    print(f"Model saved to {args.out}")


if __name__ == "__main__":
    main()
