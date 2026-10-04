"""Parse the compact roadmap DSL in roadmaps.py into structured topic dicts."""
import re

from .roadmaps import LEVEL_DIFFICULTY, LEVEL_MINUTES, ROADMAPS


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower().replace("++", "pp").replace("#", "sharp")).strip("-")


def parse_roadmap(slug: str) -> list[dict]:
    spec = ROADMAPS[slug]
    topics, order, prev_title = [], 0, None
    for level, block in spec["levels"].items():
        for line in [l.strip() for l in block.strip().splitlines() if l.strip()]:
            title, prereq_raw, concepts_raw = [p.strip() for p in line.split("|")]
            order += 1
            if prereq_raw == "^":
                prereqs = []
            elif prereq_raw == "":
                prereqs = [prev_title] if prev_title else []
            else:
                prereqs = [p.strip() for p in prereq_raw.split(",")]
            concepts = [c.strip() for c in concepts_raw.split(";") if c.strip()]
            is_project = level == "Projects"
            topics.append({
                "title": title, "slug": slugify(title), "level": level, "order": order,
                "difficulty": LEVEL_DIFFICULTY[level], "prereqs": prereqs, "concepts": concepts,
                "is_project": is_project,
                "est_minutes": LEVEL_MINUTES[level] + (10 * max(0, len(concepts) - 3) if not is_project else 60 * len(concepts)),
                "description": (f"Build a {title.lower()} in {spec['name']} that applies {', '.join(concepts)}."
                                if is_project else
                                f"{title} in {spec['name']}: {', '.join(concepts[:-1])}{' and ' if len(concepts) > 1 else ''}{concepts[-1]}."),
                "objectives": ([f"Plan and build: {c}" for c in concepts] + ["Test, document and present the project"]
                               if is_project else
                               [f"Explain {c}" if i == 0 else f"Use {c} correctly" for i, c in enumerate(concepts)]
                               + [f"Apply {title} in a small {spec['name']} program"]),
            })
            prev_title = title
    titles = {t["title"] for t in topics}
    for t in topics:
        missing = [p for p in t["prereqs"] if p not in titles]
        if missing:
            raise ValueError(f"{slug}: '{t['title']}' has unknown prerequisites {missing}")
    return topics


def all_roadmaps() -> dict[str, list[dict]]:
    return {slug: parse_roadmap(slug) for slug in ROADMAPS}
