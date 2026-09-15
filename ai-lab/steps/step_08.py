"""
STEP 8 - A workflow: boxes you drew
[slides S19-S22]
A flowchart with a model inside one box. You know which box broke.
Run it:   python steps/step_08.py
In Colab: !python steps/step_08.py
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import json, re
from labcore import chat, corpus, embed, grounded, banner, banner as _b, calls

banner("STEP 8 - A workflow: boxes you drew, model inside one of them")

chunks, texts, _ = corpus()
ask = grounded(embed(texts))

INBOX = [
    "Hi, I'm 24BCE0142. I had 68% attendance in Operating Systems because of "
    "placement drives. Will I be allowed to write the end sem? Please help urgently.",
    "can someone tell me the mess timings for saturday",
]


def box1_extract(message):
    """The model's only job: turn prose into something an `if` can consume."""
    raw = chat([{"role": "user", "content":
                 "Extract fields from this student message. Reply with ONLY a "
                 "JSON object and no prose:\n"
                 '{"topic": "attendance|grading|degree|other", '
                 '"roll_no": "<id or null>", "course": "<name or null>", '
                 '"urgent": true|false}\n\n' + message}])
    match = re.search(r"\{.*\}", raw, re.S)
    if not match:
        raise ValueError("model did not return JSON: " + raw[:120])
    return json.loads(match.group())


def handle(message):
    """Fixed pipeline. Same boxes, same order, every time."""
    ticket = box1_extract(message)                          # box 1: the model
    if ticket["topic"] == "other":                          # box 2: your code
        return ticket, "ROUTED TO HUMAN - not a regulations question"
    answer = ask(message, k=6)                              # box 3: RAG
    if ticket["urgent"]:                                    # box 4: your code
        answer = "[FLAGGED URGENT]\n" + answer
    return ticket, answer


for message in INBOX:
    ticket, outcome = handle(message)
    print(f"\n  in:    {message[:68]}...")
    print(f"  box 1: {ticket}")
    print(f"  out:   {outcome[:200]}...")

print("\nOnly box 1 uses a model. Boxes 2 and 4 are plain `if` statements.")
print("When this breaks you know exactly which box. That is the whole point.")
print(f"\n[{calls()} API calls]")
