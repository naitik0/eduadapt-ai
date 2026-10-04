"""Train one Random Forest per target (level, pace, support) and save them with joblib.

Usage:  python ml/train_model.py [--data data/synthetic_learners.csv]
The dataset is SYNTHETIC (see generate_dataset.py) and exists for demonstration.
"""
import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from features import FEATURES, TARGETS  # noqa: E402
import generate_dataset  # noqa: E402

DEFAULT_DATA = HERE.parent / "data" / "synthetic_learners.csv"
MODEL_PATH = HERE / "models" / "classifier.joblib"


def load(path: Path):
    if not path.exists():
        print(f"{path} missing; generating synthetic data first")
        rows = generate_dataset.generate(5000)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FEATURES + TARGETS)
            w.writeheader(); w.writerows(rows)
    with open(path) as f:
        rows = list(csv.DictReader(f))
    X = np.array([[float(r[c]) for c in FEATURES] for r in rows])
    Y = {t: np.array([r[t] for r in rows]) for t in TARGETS}
    return X, Y


def train(data_path: Path = DEFAULT_DATA, model_path: Path = MODEL_PATH) -> dict:
    X, Y = load(data_path)
    idx_train, idx_test = train_test_split(np.arange(len(X)), test_size=0.2, random_state=42,
                                           stratify=Y["learning_level"])
    models, metrics = {}, {}
    for target in TARGETS:
        clf = RandomForestClassifier(n_estimators=200, max_depth=12, min_samples_leaf=3,
                                     class_weight="balanced", random_state=42, n_jobs=-1)
        clf.fit(X[idx_train], Y[target][idx_train])
        pred = clf.predict(X[idx_test])
        metrics[target] = {
            "accuracy": round(float(accuracy_score(Y[target][idx_test], pred)), 3),
            "macro_f1": round(float(f1_score(Y[target][idx_test], pred, average="macro")), 3),
            "feature_importance": {f: round(float(v), 3) for f, v in
                                   sorted(zip(FEATURES, clf.feature_importances_), key=lambda x: -x[1])},
        }
        models[target] = clf
    bundle = {"models": models, "features": FEATURES, "metrics": metrics,
              "trained_at": datetime.now(timezone.utc).isoformat(), "n_samples": int(len(X)),
              "data": "synthetic (demonstration only)"}
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, model_path)
    return {"model_path": str(model_path), "metrics": {t: {k: v for k, v in m.items() if k != "feature_importance"}
                                                        for t, m in metrics.items()}}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(DEFAULT_DATA))
    ap.add_argument("--out", default=str(MODEL_PATH))
    a = ap.parse_args()
    print(json.dumps(train(Path(a.data), Path(a.out)), indent=2))
