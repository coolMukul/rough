"""
STEP 11 - Score it
[slides S32, S33]
Ten questions with known answers. The part nobody does.
Run it:   python steps/step_11.py
In Colab: !python steps/step_11.py
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from labcore import corpus, tfidf, embed, grounded, banner, calls

banner("STEP 11 - Score it")

chunks, texts, _ = corpus()

# Ground truth verified by hand against the R22.1 PDF.
#   75% attendance = clause 4        condonation 10% = clause 4(b)
#   21/60 formative = clause 5.2(ii)  CGPA bands     = clause 10, Table 11
EVAL = [
    ("What is the minimum attendance required in each course?", "75", "lookup"),
    ("How many credits are required for the B.Tech degree?", "160", "lookup"),
    ("I have 68% attendance because of placement drives. What happens?",
     ["condon", "10"], "two-docs"),
    ("I scored 18 out of 60 in formative assessment. What grade do I get?",
     ["R", "21"], "two-docs"),
    ("What are the hostel mess timings?", "REFUSE", "not-in-corpus"),
    ("How much is the tuition fee per semester?", "REFUSE", "not-in-corpus"),
    ("Can I get an exemption if I miss too many classes?", "condon", "paraphrased"),
    ("What do I need to score to not fail the internals?", "21", "paraphrased"),
    ("My attendance is exactly 75%. Am I eligible for the end sem?", "75", "edge"),
    ("My CGPA is exactly 7.0. What class do I get?", "distinction", "edge"),
]


def grade(answer, expected):
    low = answer.lower()
    if expected == "REFUSE":
        return "could not find" in low
    needed = expected if isinstance(expected, list) else [expected]
    return all(n.lower() in low for n in needed)


def score(ask, k, label):
    passed = 0
    print(f"\n  {label}")
    for question, expected, category in EVAL:
        ok = grade(ask(question, k=k), expected)
        passed += ok
        print(f"    {'PASS' if ok else 'FAIL'}  [{category:13}] {question[:50]}")
    print(f"    -> {passed}/{len(EVAL)}")
    return passed


a = score(grounded(tfidf(texts)), 1, "TF-IDF, k=1")
b = score(grounded(tfidf(texts)), 6, "TF-IDF, k=6")
c = score(grounded(embed(texts)), 6, "embeddings, k=6")

print(f"\n  TF-IDF k=1 {a}/10    TF-IDF k=6 {b}/10    embeddings k=6 {c}/10")
print("  Now the argument about k is evidence instead of opinion.")
print("  This is the sentence that gets you hired.")
print(f"\n[{calls()} API calls]")
