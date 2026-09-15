"""
STEP 1 - The model is stateless
[slides S6 - misconception 1]
Everything that feels like memory is a list your code re-sends.
Run it:   python steps/step_01.py
In Colab: !python steps/step_01.py
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from labcore import chat, banner, show, calls

banner("STEP 1 - The model is stateless")

# Do NOT ask "what did I just ask you?" - the model reads that as being about
# the message it is holding and answers correctly, which looks like memory and
# teaches the opposite. State a fact in one call, ask for it back in another.
show("call 1 - tell it something",
     chat([{"role": "user", "content": "My roll number is 24BCE0142. Remember it."}]))

show("call 2 - a brand new call, ask for it back",
     chat([{"role": "user", "content": "What is my roll number?"}]))

print("It cannot answer. There is no session and no memory on the server.")
print("Now the same question, with the earlier turns re-sent by hand:")

show("call 3 - we resend the history ourselves", chat([
    {"role": "user", "content": "My roll number is 24BCE0142. Remember it."},
    {"role": "assistant", "content": "Noted, your roll number is 24BCE0142."},
    {"role": "user", "content": "What is my roll number?"},
]))

print("That is the whole mechanism of 'conversation': a Python list your code")
print("re-sends every call. Memory is something you implement.")
print(f"\n[{calls()} API calls]")
