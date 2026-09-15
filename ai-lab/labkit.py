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
    "gpt-oss-120b", "gpt-oss-20b",
    "llama-4-maverick", "llama-4-scout",
    "llama-3.3-70b", "llama-3.1-70b", "llama-3-70b",
    "qwen3", "qwen", "deepseek", "mixtral", "gemma",
    "llama-3.1-8b", "llama",
    # Last resort. The compound models run their own internal tool loop, which
    # makes the agent step of the lab confusing - our loop stops being the only
    # thing choosing the steps.
    "compound",
]

# Never pick these for chat: audio, speech, safety filters and embedders.
EXCLUDE = ("whisper", "tts", "orpheus", "guard", "prompt-guard", "safeguard",
           "safety", "embed", "vision")


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


def list_models(key, base_url=None, explain=False):
    """
    Ask the provider what this key may actually use.

    Returns [] when it cannot say. Pass explain=True to print why - swallowing
    the cause turns an expired key, a blocked network and a typo in the base
    URL into the same unhelpful sentence.
    """
    base = (base_url or os.environ.get("LLM_BASE_URL", DEFAULT_BASE))
    url = base.split("/chat/completions")[0].rstrip("/") + "/models"

    # A User-Agent is not optional here. Groq sits behind Cloudflare, which
    # rejects urllib's default "Python-urllib/3.x" signature with a 403 and
    # error 1010 - which reads exactly like a permissions problem and is not.
    headers = {"Authorization": "Bearer " + key,
               "User-Agent": "ai-in-industry-lab/1.0"}
    request = urllib.request.Request(url, headers=headers)

    def note(message):
        if explain:
            print(f"  could not list models: {message}")

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read())
    except urllib.error.HTTPError as exc:                 # the server answered
        body = exc.read().decode("utf-8", "replace")[:300]
        hint = {401: "the key is wrong, revoked, or has a stray space",
                403: "this key is not allowed to list models",
                404: f"no models endpoint at {url} - check LLM_BASE_URL",
                429: "rate limited; wait a minute"}.get(exc.code, "")
        note(f"HTTP {exc.code} from {url}"
             + (f" - {hint}" if hint else "") + (f"\n  {body}" if body else ""))
        return []
    except urllib.error.URLError as exc:                  # never reached it
        note(f"cannot reach {url} - {exc.reason}")
        return []
    except (json.JSONDecodeError, TimeoutError) as exc:
        note(f"unreadable reply from {url} - {exc}")
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
    base = os.environ.get("LLM_BASE_URL", DEFAULT_BASE)
    print(f"\nkey      ...{api_key[-4:]}  ({len(api_key)} chars)")
    print(f"endpoint {base}\n")

    models = list_models(api_key, explain=True)
    if not models:
        print("\nNothing to choose from. Most likely causes, in order:")
        print("  1. The key is not reaching this script. In Colab the Setup")
        print("     cell must have run first, in this same session.")
        print("  2. The key is wrong or was revoked - make a new one at")
        print("     https://console.groq.com/keys")
        print("  3. Your project blocks model listing. In the Groq console see")
        print("     Projects -> Limits -> Allow or Block Models.\n")
        sys.exit(1)

    usable = [m for m in models if not any(b in m.lower() for b in EXCLUDE)]
    print(f"{len(models)} models visible, {len(usable)} usable for chat:\n")
    for model in sorted(models, key=lambda m: (rank(m), m)):
        skipped = any(b in model.lower() for b in EXCLUDE)
        print(f"  {'   ' if skipped else '-> '}{model}"
              + ("   (not a chat model)" if skipped else ""))
    print(f"\nThe lab would use: {resolve_model(api_key)}\n")
