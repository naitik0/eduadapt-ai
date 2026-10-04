"""Load the trained classifier and predict learner level / pace / support.

Usage (CLI):  python ml/predict.py '{"previous_score": 55, "recent_score": 70, ...}'
"""
import json
import sys
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from features import FEATURES  # noqa: E402

DEFAULT_MODEL = HERE / "models" / "classifier.joblib"


@lru_cache(maxsize=4)
def _load(path: str):
    return joblib.load(path)


def reload(path: Path = DEFAULT_MODEL):
    _load.cache_clear()
    return _load(str(path))


def model_info(path: Path = DEFAULT_MODEL) -> dict:
    if not Path(path).exists():
        return {"trained": False}
    b = _load(str(path))
    return {"trained": True, "trained_at": b["trained_at"], "n_samples": b["n_samples"],
            "data": b["data"], "metrics": b["metrics"]}


def predict(features: dict, path: Path = DEFAULT_MODEL) -> dict:
    """Return {'learning_level','learning_pace','support_level','confidence','probabilities'}."""
    bundle = _load(str(path))
    x = np.array([[float(features.get(f, 0)) for f in FEATURES]])
    out, confs, probs = {}, [], {}
    for target, clf in bundle["models"].items():
        p = clf.predict_proba(x)[0]
        i = int(np.argmax(p))
        out[target] = str(clf.classes_[i])
        confs.append(float(p[i]))
        probs[target] = {str(c): round(float(v), 3) for c, v in zip(clf.classes_, p)}
    out["confidence"] = round(float(np.mean(confs)), 3)
    out["probabilities"] = probs
    return out


if __name__ == "__main__":
    feats = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {
        "previous_score": 45, "recent_score": 60, "attempts": 6, "study_hours": 6, "completion_rate": 0.6,
        "time_per_question": 45, "topic_mastery": 40, "goal": 0, "interest": 0, "difficulty": 1.8}
    print(json.dumps(predict(feats), indent=2))
