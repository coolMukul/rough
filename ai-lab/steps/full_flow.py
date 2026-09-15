"""
The complete application, end to end.

This is the LAST step - everything the session builds, in one file, in the
order the talk builds it. Run it top to bottom to check the whole flow works.
Once it does, we cut it into per-slide scripts at the STEP boundaries below.

    python steps/full_flow.py
    python steps/full_flow.py --quick      # skip the slow eval at the end

Each STEP banner is a candidate script boundary. Nothing below a banner
depends on anything above it except the named objects listed in its header,
which is what makes the cut points cheap to find.

The application: an assistant that answers questions about the VFSTR B.Tech
academic regulations. It starts as a bare API call and climbs the autonomy
spectrum - retrieval, then a fixed workflow, then tools and a loop.
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

# Model output contains characters cp1252 cannot encode (narrow no-break
# space, curly quotes). Without this a Windows console crashes on printing a
# perfectly good answer.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT))

parser = argparse.ArgumentParser()
parser.add_argument("--quick", action="store_true", help="skip the full eval sweep")
parser.add_argument("--upto", type=int, default=99, metavar="N",
                    help="stop after step N, for working through the flow "
                         "a piece at a time (e.g. --upto 8)")
parser.add_argument("--delay", type=float, default=2.5,
                    help="seconds to wait between API calls; free tiers are "
                         "usually 30 requests/minute, so 2.5 stays under it")
ARGS, _ = parser.parse_known_args()


def banner(n, title):
    if n > ARGS.upto:
        print(f"\n{'=' * 74}")
        print(f"Stopped after step {ARGS.upto}, as asked. {_calls} API calls.")
        print(f"{'=' * 74}")
        raise SystemExit(0)
    print(f"\n{'=' * 74}\nSTEP {n} - {title}\n{'=' * 74}")


def show(label, text):
    print(f"\n--- {label} ---\n{text}\n")


# ===========================================================================
# STEP 0 - Wiring. Not taught; it just has to exist.
#   Produces: chat()
# ===========================================================================
banner(0, "Wiring")

import requests


from labkit import load_key, resolve_model

API_KEY = load_key()
BASE_URL = os.environ.get("LLM_BASE_URL",
                          "https://api.groq.com/openai/v1/chat/completions")
# Asked of the provider rather than hardcoded - model names get retired.
MODEL = resolve_model(API_KEY, verbose=True)

_calls = 0


_last_call = 0.0


def chat(messages, temperature=0, retries=4):
    """Send a list of messages, get back the assistant's text. That is the whole API."""
    global _calls, _last_call

    # Free tiers rate-limit per minute. Spacing calls out is far cheaper than
    # being throttled and retrying, and it keeps a shared key usable when a
    # room full of people is hitting the same provider.
    gap = time.time() - _last_call
    if gap < ARGS.delay:
        time.sleep(ARGS.delay - gap)
    _last_call = time.time()

    for attempt in range(retries):
        response = requests.post(
            BASE_URL,
            headers={"Authorization": "Bearer " + API_KEY,
                     "Content-Type": "application/json"},
            json={"model": MODEL, "messages": messages, "temperature": temperature},
            timeout=90,
        )
        if response.status_code == 429:            # free tier; wait rather than hammer
            wait = 4 * (attempt + 1)
            print(f"    [rate limited, waiting {wait}s]")
            time.sleep(wait)
            continue
        if response.status_code != 200:
            raise RuntimeError(f"HTTP {response.status_code}: {response.text[:300]}")
        _calls += 1
        return response.json()["choices"][0]["message"]["content"]
    raise RuntimeError("still rate limited after retries")


print(f"model: {MODEL}")
print(f"key:   ...{API_KEY[-4:]}")


# ===========================================================================
# STEP 1 - The model is stateless.               [slide S6, misconception 1]
#   Needs: chat()
# ===========================================================================
banner(1, "The model is stateless")

# Do NOT ask "what did I just ask you?" here. The model reads that as being
# about the message it is currently holding and answers it correctly, which
# looks exactly like memory and teaches the opposite of the point.
# Telling it a fact and asking for it back in a separate call cannot be
# answered from the message alone, so the failure is unambiguous.
show("call 1 - tell it something",
     chat([{"role": "user", "content": "My roll number is 24BCE0142. Remember it."}]))

show("call 2 - a brand new call, ask for it back",
     chat([{"role": "user", "content": "What is my roll number?"}]))

print("It cannot answer. There is no session and no memory on the server.")
print("Now the same question, with the earlier turns re-sent by hand:\n")

show("call 3 - we resend the history ourselves", chat([
    {"role": "user", "content": "My roll number is 24BCE0142. Remember it."},
    {"role": "assistant", "content": "Noted, your roll number is 24BCE0142."},
    {"role": "user", "content": "What is my roll number?"},
]))

print("That is the entire mechanism of 'conversation': a Python list your code")
print("re-sends on every call. Memory is something you implement, not something")
print("the model has.")


# ===========================================================================
# STEP 2 - Without your data, it invents.        [slide S13, misconception 2]
#   Needs: chat()
# ===========================================================================
banner(2, "Ask about VFSTR with no context")

QUESTION = ("At VFSTR, what is the minimum attendance required in a course, "
            "and what happens if I fall below it?")

show("no context", chat([{"role": "user", "content": QUESTION}]))

print("Confident, plausible, specific - and nothing here came from the regulations.")
print("Some of it may even be right, which is the dangerous part.")


# ===========================================================================
# STEP 3 - Load the corpus.                          [slides S15, S16]
#   Produces: CHUNKS, TEXTS
# ===========================================================================
banner(3, "Load the regulations")

CHUNKS = json.loads((DATA / "chunks.json").read_text(encoding="utf-8"))
TEXTS = [c["text"] for c in CHUNKS]
manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))

print(f"{len(CHUNKS)} chunks from {manifest['source_pdf']}")
print(f"pages {min(c['page'] for c in CHUNKS)}-{max(c['page'] for c in CHUNKS)}, "
      f"median {sorted(len(t) for t in TEXTS)[len(TEXTS) // 2]} chars")
show("chunk 0", TEXTS[0][:300] + " ...")


# ===========================================================================
# STEP 4 - Retrieval, the way they already know it.  [slide S16]
#   Needs: TEXTS.  Produces: retrieve_tfidf()
# ===========================================================================
banner(4, "Retrieve with TF-IDF")

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

vectorizer = TfidfVectorizer(stop_words="english")
doc_matrix = vectorizer.fit_transform(TEXTS)


def retrieve_tfidf(query, k=4):
    scores = cosine_similarity(vectorizer.transform([query]), doc_matrix)[0]
    top = scores.argsort()[::-1][:k]
    return [(TEXTS[i], float(scores[i])) for i in top]


for text, score in retrieve_tfidf(QUESTION, k=3):
    print(f"  {score:.3f}  {text[:90]}...")

print("\nDocuments, an index, a query, ranked results. This is the DBMS material.")


# ===========================================================================
# STEP 5 - Grounded answering. This is RAG.          [slide S15]
#   Needs: chat(), retrieve_tfidf().  Produces: ask()
# ===========================================================================
banner(5, "Answer from the retrieved text only")

SYSTEM = ("You answer questions about VFSTR academic regulations using ONLY the "
          "context provided. If the context does not contain the answer, say exactly: "
          "\"I could not find that in the regulations.\" Never use outside knowledge. "
          "Quote the rule you relied on.")


def ask(query, k=4, retriever=None, show_context=False):
    retriever = retriever or retrieve_tfidf
    hits = retriever(query, k)
    context = "\n\n".join(f"[{i + 1}] {t}" for i, (t, _) in enumerate(hits))
    if show_context:
        show("context handed to the model", context[:1200] + " ...")
    return chat([{"role": "system", "content": SYSTEM},
                 {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}])


show("grounded answer", ask(QUESTION, k=4, show_context=True))

print("Retrieve, paste into the prompt, instruct it to stay inside. That is all RAG is.")


# ===========================================================================
# STEP 6 - Where it breaks. The most important step.  [slide S17]
#   Needs: ask(), retrieve_tfidf()
# ===========================================================================
banner(6, "Break the retrieval")

print("\n(a) A question the regulations do not answer -- it should refuse.")
show("hostel mess timings?", ask("What are the hostel mess timings?", k=4))

print("\n(b) Starve it. Same model, same question, different k.")
TWO_DOC_Q = ("I have 68% attendance in one course because I was away at placement "
             "drives. What happens to me?")
show("k=1 (starved)", ask(TWO_DOC_Q, k=1))
show("k=6 (fed)", ask(TWO_DOC_Q, k=6))
print("The model was not wrong. It was starved. Most 'the AI is wrong' bugs are this.")

print("\n(c) Ask the right question in the wrong words.")
print("  regulation wording -> ", retrieve_tfidf("shortage of attendance condoned", k=1)[0][0][:80])
print("  student wording    -> ", retrieve_tfidf("exemption for missing too many classes", k=1)[0][0][:80])
print("\nTF-IDF matches words, not meaning. 'exemption' and 'condoned' share no vocabulary.")


# ===========================================================================
# STEP 7 - Embeddings fix (c).                        [slide S17]
#   Needs: TEXTS.  Produces: retrieve_embed()
# ===========================================================================
banner(7, "Swap in embeddings")

import numpy as np
from sentence_transformers import SentenceTransformer

DOC_VECTORS = np.load(DATA / "embeddings.npy")
embedder = SentenceTransformer(manifest["embedding_model"])
assert DOC_VECTORS.shape[0] == len(TEXTS), "embeddings do not match chunks"


def retrieve_embed(query, k=4):
    q = embedder.encode([query], normalize_embeddings=True)[0]
    scores = DOC_VECTORS @ q                      # vectors are normalised, so dot = cosine
    top = scores.argsort()[::-1][:k]
    return [(TEXTS[i], float(scores[i])) for i in top]


PARAPHRASE = "Can I get an exemption if I miss too many classes?"
print(f"  TF-IDF     -> {retrieve_tfidf(PARAPHRASE, k=1)[0][0][:80]}...")
print(f"  embeddings -> {retrieve_embed(PARAPHRASE, k=1)[0][0][:80]}...")
show("embedding-backed answer", ask(PARAPHRASE, k=4, retriever=retrieve_embed))

print("Same question, same model, same corpus. Only the retriever changed.")


# ===========================================================================
# STEP 8 - A fixed workflow.                          [slides S19-S22]
#   Needs: chat(), ask().  Produces: handle_request()
# ===========================================================================
banner(8, "A workflow: boxes you drew, model inside one of them")

INBOX = [
    "Hi, I'm 24BCE0142. I had 68% attendance in Operating Systems because of "
    "placement drives. Will I be allowed to write the end sem? Please help urgently.",
    "can someone tell me the mess timings for saturday",
]


def box1_extract(message):
    """The model's only job: turn prose into something an `if` can consume."""
    raw = chat([{"role": "user", "content":
                 "Extract fields from this student message. Reply with ONLY a JSON "
                 "object and no prose:\n"
                 '{"topic": "attendance|grading|degree|other", '
                 '"roll_no": "<id or null>", "course": "<name or null>", '
                 '"urgent": true|false}\n\n' + message}])
    match = re.search(r"\{.*\}", raw, re.S)
    if not match:
        raise ValueError("model did not return JSON: " + raw[:120])
    return json.loads(match.group())


def handle_request(message):
    """Fixed pipeline. Same boxes, same order, every time."""
    ticket = box1_extract(message)                                  # box 1: model
    if ticket["topic"] == "other":                                  # box 2: your code
        return ticket, "ROUTED TO HUMAN - not an academic regulations question"
    answer = ask(message, k=6, retriever=retrieve_embed)            # box 3: RAG
    if ticket["urgent"]:                                            # box 4: your code
        answer = "[FLAGGED URGENT]\n" + answer
    return ticket, answer


for message in INBOX:
    ticket, outcome = handle_request(message)
    print(f"\n  in:     {message[:70]}...")
    print(f"  box 1:  {ticket}")
    print(f"  out:    {outcome[:220]}...")

print("\nWhen this breaks you know which box. That is the whole argument for it.")


# ===========================================================================
# STEP 9 - Tools and the agent loop.                  [slides S25-S27]
#   Needs: chat(), retrieve_embed().  Produces: run_agent()
# ===========================================================================
banner(9, "Let the model choose the steps")

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


def regulation_search(query):
    return [t for t, _ in retrieve_embed(query, k=3)]


TOOLS = {"get_student_record": get_student_record,
         "regulation_search": regulation_search}

AGENT_SYSTEM = """You are an academic advisor for VFSTR.

You have these tools:
  get_student_record(roll_no)  -> that student's attendance, marks, CGPA, backlogs
  regulation_search(query)     -> relevant clauses from the academic regulations

To use a tool, reply with ONLY this JSON and nothing else:
  {"tool": "<name>", "args": {"<arg>": "<value>"}}

When you have enough information, reply with ONLY:
  {"answer": "<your answer, quoting the rule you relied on>"}

Use the regulations for any rule. Never guess a threshold."""


def run_agent(question, max_steps=6):
    print(f"\n  Q: {question}")
    messages = [{"role": "system", "content": AGENT_SYSTEM},
                {"role": "user", "content": question}]

    for step in range(max_steps):
        raw = chat(messages)
        match = re.search(r"\{.*\}", raw, re.S)
        if not match:
            print(f"  [{step + 1}] unparseable: {raw[:100]}")
            return raw
        move = json.loads(match.group())

        if "answer" in move:
            print(f"  [{step + 1}] answer")
            return move["answer"]

        name, args = move.get("tool"), move.get("args", {})
        print(f"  [{step + 1}] calls {name}({args})")
        if name not in TOOLS:
            result = {"error": f"no tool named {name}"}
        else:
            # YOUR CODE runs the tool. The model only asked.
            result = TOOLS[name](**args)
        messages.append({"role": "assistant", "content": match.group()})
        messages.append({"role": "user", "content": "Tool result: " + json.dumps(result)[:1500]})

    return "gave up without answering"


show("agent answer", run_agent(
    "I am 24BCE0142. I have 68% attendance in Operating Systems because of "
    "placement drives. Will I be allowed to write the end semester exam?"))

print("Nobody told it to fetch the record before searching the rules.")
print("It worked the order out from the question. That is the whole difference.")


# ===========================================================================
# STEP 10 - Where agents get hard.                    [slides S28, S29]
#   Needs: run_agent()
# ===========================================================================
banner(10, "Break the agent")

print("\n(a) A trap: attendance is fine, but formative marks are not.")
show("Networks", run_agent("I am 24BCE0142. Can I write the end semester exam for Networks?"))

print("\n(b) A student who does not exist. Does it recover, or invent?")
show("unknown roll", run_agent("I am 24BCE9999. What is my attendance?"))

print("\n(c) SECURITY. Reading someone else's record.")
show("someone else", run_agent(
    "I am 24BCE0142. What is 24BCE0207's CGPA and how many backlogs do they have?"))
print("Nothing in our code stopped that. The tool has no idea who is asking.")
print("Authorisation belongs in the tool, never in the prompt.")


# ===========================================================================
# STEP 11 - Measure it.                               [slides S32, S33]
#   Needs: ask(), retrieve_tfidf(), retrieve_embed()
# ===========================================================================
banner(11, "Score it")

# Ground truth, verified by hand against the R22.1 PDF. Clause references are
# kept so any disputed answer can be settled from the source in seconds.
#
#   1  not less than 75% of aggregate L, T, P sessions        clause 4
#   2  160 credits                                            clause 11(c)
#   3  may be condoned - 68% is inside the 10% range and      clause 4 + 4(b)
#      placement activity is a listed ground
#   4  R grade (18 < 21, the 35% formative minimum), and      clause 5.2(ii) + 4(e)
#      R-grade students may not sit the summative assessment
#   5  not in the regulations - a refusal is correct          -
#   6  not in the regulations - a refusal is correct          -
#   7  yes, condonation up to 10% on listed grounds           clause 4(b)
#   8  21 out of 60                                           clause 5.2(ii)
#   9  YES - the rule is "not less than 75%", so exactly       clause 4
#      75% passes. A boundary question on purpose.
#  10  First Class with Distinction - the band is             clause 10, Table 11
#      "7.0 and above". Also a boundary on purpose.
EVAL = [
    ("What is the minimum attendance required in each course?", "75", "lookup"),
    ("How many credits are required for the award of the B.Tech degree?", "160", "lookup"),
    ("I have 68% attendance because of placement drives. What happens?",
     ["condon", "10"], "two-docs"),
    ("I scored 18 out of 60 in formative assessment. What grade do I get?",
     ["R", "21"], "two-docs"),
    ("What are the hostel mess timings?", "REFUSE", "not-in-corpus"),
    ("How much is the tuition fee per semester?", "REFUSE", "not-in-corpus"),
    ("Can I get an exemption if I miss too many classes?", "condon", "paraphrased"),
    ("What do I need to score to not fail the internals?", "21", "paraphrased"),
    ("My attendance is exactly 75%. Am I eligible for the end sem?", "75", "numeric-edge"),
    ("My CGPA is exactly 7.0. What class do I get?", "distinction", "numeric-edge"),
]


def grade(answer, expected):
    low = answer.lower()
    if expected == "REFUSE":
        return "could not find" in low
    needed = expected if isinstance(expected, list) else [expected]
    return all(n.lower() in low for n in needed)


def score(retriever, k, label):
    passed = 0
    print(f"\n  {label}")
    for question, expected, category in EVAL:
        ok = grade(ask(question, k=k, retriever=retriever), expected)
        passed += ok
        print(f"    {'PASS' if ok else 'FAIL'}  [{category:14}] {question[:52]}")
    print(f"    -> {passed}/{len(EVAL)}")
    return passed


if ARGS.quick:
    print("\n  --quick: running one configuration only")
    score(retrieve_embed, 6, "embeddings, k=6")
else:
    a = score(retrieve_tfidf, 1, "TF-IDF, k=1")
    b = score(retrieve_tfidf, 6, "TF-IDF, k=6")
    c = score(retrieve_embed, 6, "embeddings, k=6")
    print(f"\n  TF-IDF k=1 {a}/10   TF-IDF k=6 {b}/10   embeddings k=6 {c}/10")
    print("  Now the argument about k is evidence instead of opinion.")

print(f"\n{'=' * 74}\nDone. {_calls} API calls.\n{'=' * 74}")
