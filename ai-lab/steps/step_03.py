"""
STEP 3 - Load the regulations
[slides S15, S16]
227 clauses, already chunked. No API calls in this step.
Run it:   python steps/step_03.py
In Colab: !python steps/step_03.py
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from labcore import corpus, banner, show

banner("STEP 3 - Load the regulations")

chunks, texts, manifest = corpus()

print(f"{len(chunks)} chunks from {manifest['source_pdf']}")
print(f"pages {min(c['page'] for c in chunks)}-{max(c['page'] for c in chunks)}, "
      f"median {sorted(len(t) for t in texts)[len(texts) // 2]} chars")
show("chunk 0", texts[0][:300] + " ...")

print("Each chunk is prefixed with its section name, e.g. [Attendance].")
print("That is what lets a search for 'attendance' find them at all.")
