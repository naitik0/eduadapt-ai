"""Local RAG: chunk the knowledge base + every roadmap topic, embed, index in FAISS.

Embeddings: TF-IDF (word 1-2 grams, sublinear tf) densified and L2-normalized, searched with
FAISS inner product = cosine similarity. Fully offline and deterministic. To use neural
embeddings, swap `_embed` for a sentence-transformers model; the FAISS index code is unchanged.
"""
import re
import threading

import faiss
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from ..data.knowledge import KNOWLEDGE
from ..data.parser import all_roadmaps
from ..data.roadmaps import ROADMAPS

_lock = threading.Lock()
_state: dict = {}


def _chunks() -> list[dict]:
    docs = []
    for skill, topic, analogy, body in KNOWLEDGE:
        code = re.search(r"```(\w*)\n(.*?)```", body, re.S)
        prose = re.sub(r"```.*?```", "", body, flags=re.S).strip()
        docs.append({"skill": skill, "topic": topic, "kind": "lesson", "text": prose, "analogy": analogy,
                     "code": code.group(2).strip() if code else "", "lang": code.group(1) if code else "",
                     "source": f"EduAdapt notes: {ROADMAPS[skill]['name']} / {topic}"})
    for skill, topics in all_roadmaps().items():
        for t in topics:
            docs.append({"skill": skill, "topic": t["title"], "kind": "syllabus",
                         "text": f"{t['description']} Learning objectives: {'; '.join(t['objectives'])}. "
                                 f"Prerequisites: {', '.join(t['prereqs']) or 'none'}. Level: {t['level']}.",
                         "analogy": "", "code": "", "lang": "",
                         "source": f"EduAdapt syllabus: {ROADMAPS[skill]['name']} / {t['title']}"})
    return docs


def _build():
    docs = _chunks()
    corpus = [f"{d['topic']} {d['topic']} {d['text']} {d['code']}" for d in docs]
    vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1, stop_words="english")
    X = vec.fit_transform(corpus).astype(np.float32).toarray()
    faiss.normalize_L2(X)
    index = faiss.IndexFlatIP(X.shape[1])
    index.add(X)
    _state.update(docs=docs, vec=vec, index=index)


def _ensure():
    with _lock:
        if not _state:
            _build()


def _embed(texts: list[str]) -> np.ndarray:
    X = _state["vec"].transform(texts).astype(np.float32).toarray()
    faiss.normalize_L2(X)
    return X


def search(query: str, skill: str | None = None, topic: str | None = None, k: int = 4) -> list[dict]:
    """Vector search, then re-rank with a small boost for the student's current skill/topic."""
    _ensure()
    q = f"{topic or ''} {query}"
    scores, idx = _state["index"].search(_embed([q]), min(40, len(_state["docs"])))
    hits = []
    for s, i in zip(scores[0], idx[0]):
        if i < 0:
            continue
        d = _state["docs"][i]
        boost = (0.15 if skill and d["skill"] == skill else 0) + (0.25 if topic and d["topic"] == topic else 0) \
            + (0.05 if d["kind"] == "lesson" else 0)
        hits.append({**d, "score": round(float(s) + boost, 4)})
    hits.sort(key=lambda h: -h["score"])
    return hits[:k]


def stats() -> dict:
    _ensure()
    return {"documents": len(_state["docs"]), "dimensions": int(_state["index"].d), "index": "faiss.IndexFlatIP"}
