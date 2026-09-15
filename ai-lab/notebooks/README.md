# The lab, step by step

**One notebook per step.** Open it, read the explanation at the top, then run the cells one at a time — the code is right there for you to read and change.

Every notebook stands alone. It sets itself up, so **if one gives you trouble, skip it and open the next.** You will not fall behind.

| # | Open it | What you take away | Cost |
|---|---|---|---|
| **1** | [The model has no memory](https://colab.research.google.com/github/coolMukul/rough/blob/main/ai-lab/notebooks/step_01.ipynb) | There is no memory on the server. Everything that feels like a conversation is a Python list your own code re-sends every time. | 3 calls |
| **2** | [Without your data, it invents](https://colab.research.google.com/github/coolMukul/rough/blob/main/ai-lab/notebooks/step_02.ipynb) | A wrong answer arrives in exactly the same confident tone as a right one. You cannot tell them apart by reading. | 1 calls |
| **3** | [Load the regulations](https://colab.research.google.com/github/coolMukul/rough/blob/main/ai-lab/notebooks/step_03.ipynb) | How a document gets turned into something searchable, and why each chunk carries its section name. | free |
| **4** | [Retrieve with TF-IDF](https://colab.research.google.com/github/coolMukul/rough/blob/main/ai-lab/notebooks/step_04.ipynb) | Retrieval is ordinary search — the DBMS material you already know, with a different relevance score. | free |
| **5** | [Answer from the retrieved text](https://colab.research.google.com/github/coolMukul/rough/blob/main/ai-lab/notebooks/step_05.ipynb) | That is all RAG is. Retrieve, stuff into the prompt, instruct the model to stay inside it. | 1 calls |
| **6** | [Break the retrieval](https://colab.research.google.com/github/coolMukul/rough/blob/main/ai-lab/notebooks/step_06.ipynb) | Most of the time "the AI is wrong", the retrieval was wrong. This is the most useful debugging instinct in the session. | 3 calls |
| **7** | [Swap in embeddings](https://colab.research.google.com/github/coolMukul/rough/blob/main/ai-lab/notebooks/step_07.ipynb) | What embeddings are for — and that swapping in a fancier technique does not automatically make a system better. | 1 calls |
| **8** | [A workflow](https://colab.research.google.com/github/coolMukul/rough/blob/main/ai-lab/notebooks/step_08.ipynb) | How a model becomes part of ordinary software: it turns prose into JSON that an `if` statement can act on. | 4 calls |
| **11** | [Score it](https://colab.research.google.com/github/coolMukul/rough/blob/main/ai-lab/notebooks/step_11.ipynb) | How to tell whether a change made things better, with a number instead of an opinion. Almost nobody does this. | 30 calls |

Steps 3 and 4 make **no API calls at all** — use those to explore your regulations as much as you like.

---

## Before your first notebook

You need a free API key, once. It takes three minutes:

1. **[console.groq.com](https://console.groq.com/keys)** → sign in with Google → **API Keys** → **Create API Key**
2. Copy it. It starts `gsk_` and is shown **only once**.
3. In any step notebook: click the **🔑 key icon** on the far left → **+ Add new secret**
   - Name: `LLM_API_KEY` (exactly — all capitals, two underscores)
   - Value: your key
   - **Notebook access: ON** ← starts off, and is the most common failure

The key is stored against your Google account, so you do it once and every notebook can use it. **But the Notebook access toggle is per-notebook**, so you may need to switch it on again each time you open a new step.

---

## How to actually use these

Reading code teaches you very little. **Changing it teaches you a lot.**

Every notebook ends with a *"Now change it yourself"* cell. That one matters more than all the others. Change a number, run it again, and watch what moves.

---

## Steps 9 and 10

The agent loop. **Not written yet** — see [../steps/README.md](../steps/README.md) for why.
