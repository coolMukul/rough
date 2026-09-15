"""
STEP 4 - Retrieve with TF-IDF
[slide S16]
Documents, an index, a query, ranked results. This is the DBMS material.
Run it:   python steps/step_04.py
In Colab: !python steps/step_04.py
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from labcore import corpus, tfidf, banner

banner("STEP 4 - Retrieve with TF-IDF")

chunks, texts, _ = corpus()
retrieve = tfidf(texts)

QUESTION = "At VFSTR, what is the minimum attendance required in a course?"

for text, score in retrieve(QUESTION, k=3):
    print(f"  {score:.3f}  {text[:88]}...")

print("\nNo model was called. This is pure search - the same problem you")
print("solved in DBMS last year, with a different relevance score.")
