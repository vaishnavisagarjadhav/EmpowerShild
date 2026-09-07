"""
Train Fall Detection Model (1D-CNN on accelerometer + gyroscope windows)
==========================================================================
Trains a lightweight 1D-CNN on labeled motion windows (fall vs. ADL —
activities of daily living), then exports it to TFLite for fully offline,
on-device inference inside the Flutter app.

Recommended public datasets: SisFall, MobiFall, UMAFall.

Usage:
    python train_fall_detection.py --data sisfall_processed.npz

Expected .npz contents:
    X: shape (num_samples, window_len, 6)   # ax, ay, az, gx, gy, gz
    y: shape (num_samples,)                  # 1 = fall, 0 = normal activity
"""
import argparse
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models


WINDOW_LEN = 100   # ~2 seconds at 50Hz sampling rate
NUM_CHANNELS = 6   # ax, ay, az, gx, gy, gz


def generate_synthetic_dataset(n=2000, seed=1):
    """Placeholder — replace with real SisFall/MobiFall preprocessed windows."""
    rng = np.random.default_rng(seed)
    X, y = [], []
    for _ in range(n):
        is_fall = rng.integers(0, 2)
        if is_fall:
            window = rng.normal(0, 0.3, (WINDOW_LEN, NUM_CHANNELS))
            spike_idx = rng.integers(20, 80)
            window[spike_idx:spike_idx + 5, :3] += rng.uniform(2.0, 4.0)   # accel spike
            window[spike_idx:spike_idx + 5, 3:] += rng.uniform(150, 300)  # gyro spike
        else:
            window = rng.normal(0, 0.15, (WINDOW_LEN, NUM_CHANNELS))
        X.append(window)
        y.append(is_fall)
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)


def build_model():
    model = models.Sequential([
        layers.Input(shape=(WINDOW_LEN, NUM_CHANNELS)),
        layers.Conv1D(32, kernel_size=5, activation="relu"),
        layers.MaxPooling1D(2),
        layers.Conv1D(64, kernel_size=5, activation="relu"),
        layers.GlobalAveragePooling1D(),
        layers.Dense(32, activation="relu"),
        layers.Dropout(0.3),
        layers.Dense(1, activation="sigmoid"),
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, default=None)
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--out", type=str, default="fall_detection_model.h5")
    args = parser.parse_args()

    if args.data:
        data = np.load(args.data)
        X, y = data["X"], data["y"]
    else:
        print("No dataset provided — using synthetic demo data. "
              "Replace with real SisFall/MobiFall data for production accuracy.")
        X, y = generate_synthetic_dataset()

    split = int(0.8 * len(X))
    X_train, X_val = X[:split], X[split:]
    y_train, y_val = y[:split], y[split:]

    model = build_model()
    model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=args.epochs, batch_size=32)

    model.save(args.out)
    print(f"Model saved to {args.out}. Run convert_to_tflite.py next for on-device deployment.")


if __name__ == "__main__":
    main()
