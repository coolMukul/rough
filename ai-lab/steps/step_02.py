"""
STEP 2 - Without your data, it invents
[slide S13 - misconception 2]
The wrong answer arrives in the same confident tone as a right one.
Run it:   python steps/step_02.py
In Colab: !python steps/step_02.py
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from labcore import chat, banner, show, calls

banner("STEP 2 - Ask about VFSTR with no context")

QUESTION = ("At VFSTR, what is the minimum attendance required in a course, "
            "and what happens if I fall below it?")

show("no context", chat([{"role": "user", "content": QUESTION}]))

print("Confident, plausible, specific - and none of it came from the")
print("regulations. Some may even be right, which is the dangerous part.")
print("Open the PDF and check it yourself.")
print(f"\n[{calls()} API calls]")
