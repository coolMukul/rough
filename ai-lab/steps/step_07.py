"""
STEP 7 - Swap in embeddings
[slide S17]
Only the retriever changes. Read the open question in steps/README.md.
Run it:   python steps/step_07.py
In Colab: !python steps/step_07.py
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from labcore import corpus, tfidf, embed, grounded, banner, show, calls

banner("STEP 7 - Swap in embeddings")

chunks, texts, _ = corpus()
by_word = tfidf(texts)
by_meaning = embed(texts)

PARAPHRASE = "Can I get an exemption if I miss too many classes?"

print(f"  TF-IDF     -> {by_word(PARAPHRASE, k=1)[0][0][:80]}...")
print(f"  embeddings -> {by_meaning(PARAPHRASE, k=1)[0][0][:80]}...")

show("embedding-backed answer", grounded(by_meaning)(PARAPHRASE, k=4))

print("Same question, same model, same corpus. Only the retriever changed.")
print("NOTE: on this corpus embeddings do NOT reliably beat TF-IDF.")
print("That is a real result, not a bug - and it is the argument for step 11.")
print(f"\n[{calls()} API calls]")
