"""Generate a realistic SYNTHETIC learner dataset for demonstrating the classifier.

The labels come from transparent pedagogical rules plus label noise, so the Random
Forest has to learn a noisy, non-linear boundary. Replace with real learner logs
when available; the feature schema in features.py stays the same.
"""
import argparse
import csv
from pathlib import Path

import numpy as np

from features import FEATURES, GOALS, INTERESTS

HERE = Path(__file__).resolve().parent


def label_row(r, rng):
    level_score = 0.40 * r["topic_mastery"] + 0.25 * r["recent_score"] + 0.15 * r["previous_score"] \
        + 6.0 * (r["difficulty"] - 1) + min(r["attempts"], 40) * 0.25
    level = "Beginner" if level_score < 38 else "Intermediate" if level_score < 66 else "Advanced"

    speed = 45 * r["completion_rate"] + 1.2 * r["study_hours"] - 0.35 * r["time_per_question"] \
        + 0.3 * (r["recent_score"] - r["previous_score"]) + 10
    pace = "Slow" if speed < 22 else "Moderate" if speed < 42 else "Fast"

    need = 100 - 0.6 * r["recent_score"] - 25 * r["completion_rate"] + 0.2 * r["time_per_question"] \
        - 0.2 * (r["recent_score"] - r["previous_score"])
    support = "High" if need > 62 else "Medium" if need > 38 else "Low"

    # 7% label noise per target, like inconsistent human annotation
    def noisy(value, choices):
        return rng.choice(choices) if rng.random() < 0.07 else value
    return (noisy(level, ["Beginner", "Intermediate", "Advanced"]),
            noisy(pace, ["Slow", "Moderate", "Fast"]),
            noisy(support, ["Low", "Medium", "High"]))


def generate(n: int, seed: int = 7):
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n):
        ability = rng.beta(2, 2)                       # latent skill 0..1
        diligence = rng.beta(2, 2)                     # latent effort 0..1
        prev = np.clip(rng.normal(30 + 60 * ability, 10), 0, 100)
        recent = np.clip(prev + rng.normal(8 * diligence - 2, 9), 0, 100)
        r = {
            "previous_score": round(float(prev), 1),
            "recent_score": round(float(recent), 1),
            "attempts": int(rng.poisson(3 + 25 * ability * diligence)),
            "study_hours": round(float(np.clip(rng.normal(3 + 12 * diligence, 2.5), 0.5, 30)), 1),
            "completion_rate": round(float(np.clip(rng.normal(0.25 + 0.65 * diligence, 0.12), 0, 1)), 2),
            "time_per_question": round(float(np.clip(rng.normal(70 - 40 * ability, 12), 8, 150)), 1),
            "topic_mastery": round(float(np.clip(rng.normal(10 + 80 * ability, 9), 0, 100)), 1),
            "goal": int(rng.integers(len(GOALS))),
            "interest": int(rng.integers(len(INTERESTS))),
            "difficulty": round(float(np.clip(1 + 3 * ability + rng.normal(0, 0.35), 1, 4)), 2),
        }
        r["learning_level"], r["learning_pace"], r["support_level"] = label_row(r, rng)
        rows.append(r)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5000)
    ap.add_argument("--out", default=str(HERE.parent / "data" / "synthetic_learners.csv"))
    args = ap.parse_args()
    rows = generate(args.n)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FEATURES + ["learning_level", "learning_pace", "support_level"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} synthetic rows -> {args.out}")


if __name__ == "__main__":
    main()
