"""
Check that this machine is ready for the lab.

    python verify_setup.py

Runs eight checks and prints PASS or FAIL for each, with the fix for
anything that fails. Safe to run as many times as you like.

In Google Colab, run this instead, in a cell:

    !python verify_setup.py
"""

import json
import os
import sys
from pathlib import Path

# Quieten the model loader so it does not interleave with the check lines.
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

results = []


def check(name):
    """Decorator: run a check, catch anything, record PASS/FAIL + a hint."""
    def wrap(fn):
        sys.stdout.write(f"  {name:.<44}")
        sys.stdout.flush()
        try:
            detail = fn()
            print(f"PASS  {detail or ''}")
            results.append((name, True, ""))
        except Exception as exc:
            print("FAIL")
            results.append((name, False, str(exc)))
        return fn
    return wrap


def load_key():
    """Key from the environment, a .env file, or Colab secrets - in that order."""
    key = os.environ.get("LLM_API_KEY", "").strip()
    if key:
        return key, "environment"

    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("LLM_API_KEY="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                if value:
                    os.environ.setdefault("LLM_API_KEY", value)
                    for other in ("LLM_BASE_URL", "LLM_MODEL"):
                        pass
                    return value, ".env file"

    try:
        from google.colab import userdata          # type: ignore
        value = userdata.get("LLM_API_KEY")
        if value:
            return value.strip(), "Colab secrets"
    except Exception:
        pass

    raise RuntimeError(
        "no API key found. Set LLM_API_KEY in a .env file (local) "
        "or add it to the Colab secrets panel (key icon, left sidebar)."
    )


def load_env_file():
    """Pull LLM_BASE_URL / LLM_MODEL out of .env if present."""
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        if value:
            os.environ.setdefault(name.strip(), value)


print("\nChecking your setup for the AI in Industry lab\n")
load_env_file()

IN_COLAB = "google.colab" in sys.modules or os.path.exists("/content")
print(f"  running in: {'Google Colab' if IN_COLAB else 'local machine'}\n")


@check("Python 3.9 or newer")
def _python():
    if sys.version_info < (3, 9):
        raise RuntimeError(f"found {sys.version.split()[0]}; install Python 3.9+")
    return sys.version.split()[0]


@check("Required packages installed")
def _packages():
    import importlib
    missing = []
    for mod, pip_name in [("requests", "requests"), ("numpy", "numpy"),
                          ("sklearn", "scikit-learn"),
                          ("sentence_transformers", "sentence-transformers")]:
        try:
            importlib.import_module(mod)
        except ImportError:
            missing.append(pip_name)
    if missing:
        raise RuntimeError("missing: " + ", ".join(missing)
                           + "  ->  pip install -r requirements.txt")
    return "all present"


@check("Corpus files present")
def _corpus():
    for name in ("chunks.json", "embeddings.npy", "manifest.json"):
        if not (DATA / name).exists():
            raise RuntimeError(f"data/{name} is missing; re-download the repo")
    chunks = json.loads((DATA / "chunks.json").read_text(encoding="utf-8"))
    return f"{len(chunks)} chunks"


@check("Embeddings match the corpus")
def _embeddings():
    import numpy as np
    chunks = json.loads((DATA / "chunks.json").read_text(encoding="utf-8"))
    vectors = np.load(DATA / "embeddings.npy")
    manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
    if vectors.shape[0] != len(chunks):
        raise RuntimeError(f"{vectors.shape[0]} vectors vs {len(chunks)} chunks; "
                           "run tools/build_corpus.py")
    if manifest.get("embedding_dim") != vectors.shape[1]:
        raise RuntimeError("manifest dimension disagrees with embeddings.npy")
    return f"{vectors.shape[0]} x {vectors.shape[1]}"


@check("Embedding model loads")
def _model():
    from sentence_transformers import SentenceTransformer
    manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
    name = manifest["embedding_model"]
    model = SentenceTransformer(name)          # cached after the first run
    vec = model.encode(["attendance requirement"], normalize_embeddings=True)
    if vec.shape[1] != manifest["embedding_dim"]:
        raise RuntimeError("model returns a different dimension than the shipped "
                           "vectors; the corpus was built with a different model")
    return name.split("/")[-1]


@check("API key found")
def _key():
    key, source = load_key()
    if len(key) < 20:
        raise RuntimeError("key looks too short; check for a missing character")
    if key != key.strip():
        raise RuntimeError("key has whitespace around it; re-copy it")
    return f"from {source}, ...{key[-4:]}"


@check("A usable model is available")
def _model_pick():
    from labkit import resolve_model
    key, _ = load_key()
    chosen = resolve_model(key, verbose=False)
    if not chosen:
        raise RuntimeError("provider listed no usable chat model")
    os.environ["LLM_MODEL_RESOLVED"] = chosen
    return chosen


@check("The model answers")
def _call():
    import requests
    key, _ = load_key()
    url = os.environ.get("LLM_BASE_URL",
                         "https://api.groq.com/openai/v1/chat/completions")
    model = os.environ.get("LLM_MODEL_RESOLVED") or os.environ.get("LLM_MODEL", "")

    response = requests.post(
        url,
        headers={"Authorization": "Bearer " + key,
                 "Content-Type": "application/json"},
        json={"model": model,
              "messages": [{"role": "user",
                            "content": "Reply with exactly three words: the wire works"}],
              "temperature": 0},
        timeout=60,
    )
    if response.status_code == 401:
        raise RuntimeError("401 unauthorised - the key is wrong or was revoked")
    if response.status_code == 404:
        raise RuntimeError(f"404 - model '{model}' was listed but will not serve; "
                           "run  python labkit.py  to see what this key can use")
    if response.status_code == 429:
        raise RuntimeError("429 rate limited - wait a minute and run this again")
    if response.status_code != 200:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text[:200]}")
    return response.json()["choices"][0]["message"]["content"].strip()[:40]


failed = [(n, hint) for n, ok, hint in results if not ok]
print()
if not failed:
    print("  All checks passed. You are ready for the session.\n")
    sys.exit(0)

print(f"  {len(failed)} check(s) failed:\n")
for name, hint in failed:
    print(f"    {name}\n      {hint}\n")
print("  Fix these before the session. If you are stuck, message the "
      "coordinator - do not wait until the day.\n")
sys.exit(1)
