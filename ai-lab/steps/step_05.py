"""
STEP 5 - Answer from the retrieved text only
[slide S15]
Retrieve, paste into the prompt, instruct it to stay inside. That is RAG.
Run it:   python steps/step_05.py
In Colab: !python steps/step_05.py
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from labcore import corpus, tfidf, grounded, banner, show, calls

banner("STEP 5 - Answer from the retrieved text only")

chunks, texts, _ = corpus()
ask = grounded(tfidf(texts))

QUESTION = ("At VFSTR, what is the minimum attendance required in a course, "
            "and what happens if I fall below it?")

show("grounded answer", ask(QUESTION, k=4, show_context=True))

print("Compare this with step 2. Same model, same question - the only")
print("difference is that we pasted the right paragraph into the prompt.")
print(f"\n[{calls()} API calls]")
