"""
STEP 6 - Break the retrieval
[slide S17] THE MOST IMPORTANT STEP
Most 'the AI is wrong' bugs are retrieval bugs.
Run it:   python steps/step_06.py
In Colab: !python steps/step_06.py
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from labcore import corpus, tfidf, grounded, banner, show, calls

banner("STEP 6 - Break the retrieval")

chunks, texts, _ = corpus()
retrieve = tfidf(texts)
ask = grounded(retrieve)

print("\n(a) A question the regulations do not answer. It should refuse.")
show("hostel mess timings?", ask("What are the hostel mess timings?", k=4))
print("Refusing correctly is a PASSING score, not a failure.")

print("\n(b) Starve it. Same model, same question, different k.")
Q = ("I have 68% attendance in one course because I was away at placement "
     "drives. What happens to me?")
show("k=1 (starved)", ask(Q, k=1))
show("k=6 (fed)", ask(Q, k=6))
print("The model was not wrong. It was starved. It never saw the clause")
print("saying shortage can be condoned up to 10% for placement activities.")

print("\n(c) Ask the right question in the wrong words.")
print("  regulation wording ->", retrieve("shortage of attendance condoned", k=1)[0][0][:80])
print("  student wording    ->", retrieve("exemption for missing too many classes", k=1)[0][0][:80])
print("\nTF-IDF matches words, not meaning. 'exemption' and 'condoned'")
print("share no vocabulary at all.")
print(f"\n[{calls()} API calls]")
