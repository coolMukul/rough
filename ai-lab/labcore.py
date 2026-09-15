"""
The building blocks every step needs.

This is the "replay" the checkpoint design depends on: a step script imports
what earlier steps produced, in one line, and then contains only its own new
code. That keeps each script short enough to type, while still letting a
student who skipped three steps run the fourth and be caught up.

    from labcore import chat, corpus, tfidf, embed, grounded

Nothing here is the lesson. The lesson is in the step scripts.
"""

import json
import os
import sys
import time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT))

DELAY = float(os.environ.get("LAB_DELAY", "2.5"))     # free tiers are ~30/min

_calls = 0
_last = 0.0
_model = None


def banner(title):
    print(f"\n{'=' * 72}\n{title}\n{'=' * 72}")


def show(label, text):
    print(f"\n--- {label} ---\n{text}\n")


def calls():
    return _calls


# --------------------------------------------------------------------------
# The API. One function. This really is the whole thing.
# --------------------------------------------------------------------------
def chat(messages, temperature=0, retries=4, **extra):
    """Send a list of messages, get back the assistant's text."""
    global _calls, _last, _model
    import requests
    from labkit import load_key, resolve_model

    key = load_key()
    if _model is None:
        _model = resolve_model(key)
    url = os.environ.get("LLM_BASE_URL",
                         "https://api.groq.com/openai/v1/chat/completions")

    gap = time.time() - _last
    if gap < DELAY:
        time.sleep(DELAY - gap)
    _last = time.time()

    body = {"model": _model, "messages": messages, "temperature": temperature}
    body.update(extra)

    for attempt in range(retries):
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + key,
                     "Content-Type": "application/json"},
            json=body, timeout=90)
        if response.status_code == 429:
            wait = 4 * (attempt + 1)
            print(f"    [rate limited, waiting {wait}s]")
            time.sleep(wait)
            continue
        if response.status_code != 200:
            raise RuntimeError(f"HTTP {response.status_code}: {response.text[:300]}")
        _calls += 1
        message = response.json()["choices"][0]["message"]
        if extra.get("tools"):
            return message
        return message.get("content") or ""
    raise RuntimeError("still rate limited after retries")


def model_name():
    global _model
    if _model is None:
        from labkit import load_key, resolve_model
        _model = resolve_model(load_key())
    return _model


# --------------------------------------------------------------------------
# The corpus and the two retrievers.
# --------------------------------------------------------------------------
def corpus():
    """The regulations, already chunked. Returns (chunks, texts, manifest)."""
    chunks = json.loads((DATA / "chunks.json").read_text(encoding="utf-8"))
    manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
    return chunks, [c["text"] for c in chunks], manifest


def tfidf(texts=None):
    """Word-matching retrieval. Returns retrieve(query, k) -> [(text, score)]."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    texts = texts if texts is not None else corpus()[1]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(texts)

    def retrieve(query, k=4):
        scores = cosine_similarity(vectorizer.transform([query]), matrix)[0]
        return [(texts[i], float(scores[i])) for i in scores.argsort()[::-1][:k]]

    return retrieve


def embed(texts=None):
    """Meaning-based retrieval, using the vectors shipped with the repo."""
    import numpy as np
    from sentence_transformers import SentenceTransformer

    chunks, all_texts, manifest = corpus()
    texts = texts if texts is not None else all_texts
    vectors = np.load(DATA / "embeddings.npy")
    model = SentenceTransformer(manifest["embedding_model"])

    def retrieve(query, k=4):
        q = model.encode([query], normalize_embeddings=True)[0]
        scores = vectors @ q             # vectors are normalised: dot == cosine
        return [(texts[i], float(scores[i])) for i in scores.argsort()[::-1][:k]]

    return retrieve


SYSTEM = ("You answer questions about VFSTR academic regulations using ONLY the "
          "context provided. If the context does not contain the answer, say "
          "exactly: \"I could not find that in the regulations.\" Never use "
          "outside knowledge. Quote the rule you relied on.")


def grounded(retriever):
    """Turn a retriever into ask(query, k, show_context) -> answer. This is RAG."""
    def ask(query, k=4, show_context=False):
        hits = retriever(query, k)
        context = "\n\n".join(f"[{i + 1}] {t}" for i, (t, _) in enumerate(hits))
        if show_context:
            show("context handed to the model", context[:1200] + " ...")
        return chat([{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}])
    return ask


# --------------------------------------------------------------------------
# The student records the agent steps read. Invented, not real people.
# --------------------------------------------------------------------------
STUDENT_DB = {
    "24BCE0142": {"name": "A. Sravanthi", "cgpa": 7.1, "credits_earned": 82,
                  "attendance": {"Operating Systems": 68, "DBMS": 91, "Networks": 77},
                  "formative_60": {"Operating Systems": 34, "DBMS": 48, "Networks": 19},
                  "backlogs": []},
    "24BCE0207": {"name": "K. Rahul", "cgpa": 5.4, "credits_earned": 71,
                  "attendance": {"Operating Systems": 82, "DBMS": 61, "Networks": 88},
                  "formative_60": {"Operating Systems": 40, "DBMS": 25, "Networks": 33},
                  "backlogs": ["Data Structures"]},
}


def get_student_record(roll_no):
    return STUDENT_DB.get(roll_no, {"error": "no such student"})
