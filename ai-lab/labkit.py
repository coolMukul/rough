"""
Shared plumbing: find the key, and find a model that actually works.

Providers retire model names without notice - Groq dropped
llama-3.3-70b-versatile from the free tier mid-2026 - and a hardcoded name
turns into sixty simultaneous 404s on the morning of a session. So the model
is discovered at runtime and only falls back to a hardcoded guess if
discovery itself fails.

    from labkit import load_key, resolve_model
"""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent

DEFAULT_BASE = "https://api.groq.com/openai/v1/chat/completions"

# Preference order, best first. Matching is by substring, so a version bump
# such as llama-3.3-70b -> llama-3.4-70b still matches "llama" and ranks
# above an unknown model. Nothing here is required to exist.
PREFERRED = [
    "llama-4-maverick", "llama-4-scout",
    "llama-3.3-70b", "llama-3.1-70b", "llama-3-70b",
    "qwen", "deepseek", "mixtral", "gemma",
    "llama-3.1-8b", "llama",
]

# Never pick these for chat: they are audio, vision-only, or safety filters.
EXCLUDE = ("whisper", "tts", "guard", "prompt-guard", "safety", "embed", "vision")


def load_key():
    """Key from the environment, a .env file, or Colab secrets - in that order."""
    key = os.environ.get("LLM_API_KEY", "").strip()
    if key:
        return key

    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("LLM_API_KEY="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                if value:
                    return value

    try:
        from google.colab import userdata          # type: ignore
        value = (userdata.get("LLM_API_KEY") or "").strip()
        if value:
            return value
    except Exception:
        pass

    sys.exit("No API key found. See SETUP.md.")


def list_models(key, base_url=None):
    """Ask the provider what this key may actually use. [] if it cannot say."""
    base = (base_url or os.environ.get("LLM_BASE_URL", DEFAULT_BASE))
    url = base.split("/chat/completions")[0].rstrip("/") + "/models"
    request = urllib.request.Request(url, headers={"Authorization": "Bearer " + key})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read())
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return []
    return [m.get("id", "") for m in payload.get("data", []) if m.get("id")]


def rank(model_id):
    """Lower is better. Unknown-but-usable models sort after every preference."""
    lowered = model_id.lower()
    for position, name in enumerate(PREFERRED):
        if name in lowered:
            return position
    return len(PREFERRED)


def resolve_model(key, explicit=None, verbose=False):
    """
    Decide which model to call.

    An explicitly configured LLM_MODEL wins, but only if the provider still
    lists it - otherwise we would hand back a name that 404s on every call.
    """
    explicit = explicit or os.environ.get("LLM_MODEL", "").strip()
    available = list_models(key)

    if not available:
        # Discovery failed. Trust whatever was configured and let the call fail
        # with a real error rather than guessing blindly here.
        return explicit or "llama-3.3-70b-versatile"

    usable = [m for m in available if not any(bad in m.lower() for bad in EXCLUDE)]

    if explicit and explicit in available:
        return explicit
    if explicit and verbose:
        print(f"      '{explicit}' is not available on this key - choosing another")

    if not usable:
        return explicit or available[0]

    chosen = sorted(usable, key=lambda m: (rank(m), len(m)))[0]
    if verbose:
        print(f"      {len(usable)} chat models available, using: {chosen}")
    return chosen


if __name__ == "__main__":
    api_key = load_key()
    models = list_models(api_key)
    if not models:
        sys.exit("Could not list models - check the key and the base URL.")
    print(f"{len(models)} models visible to this key:\n")
    for model in sorted(models, key=lambda m: (rank(m), m)):
        marker = "  " if any(b in model.lower() for b in EXCLUDE) else "->"
        print(f"  {marker} {model}")
    print(f"\nWould use: {resolve_model(api_key)}")
