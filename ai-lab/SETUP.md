# Setup — AI in Industry Lab

**Do this before the session, not on the day.** It takes about 15 minutes and you only need a web browser. If something fails, message the coordinator — do not wait until the session starts.

Nothing installs on your own computer. Everything runs on Google's servers. A slow or old laptop is fine.

---

## Part 1 — Open the lab in Google Colab (5 minutes)

Google Colab runs Python in your browser. Nothing installs on your machine.

### 1.1 — Sign in to Google

Open **<https://colab.research.google.com>**. If it asks you to sign in, use any Google account.

If a pop-up appears saying "Open notebook", close it with **Cancel** or the **X**.

### 1.2 — Open the lab notebook

Click this link. It opens straight in Colab — you do not need a GitHub account.

**<https://colab.research.google.com/github/coolMukul/rough/blob/main/ai-lab/lab.ipynb>**

You are now looking at the lab. It is made of **cells** — grey boxes containing code, white boxes containing instructions.

### 1.3 — Make your own copy — do not skip this

Click **File** → **Save a copy in Drive**.

A new tab opens, titled **`Copy of lab.ipynb`**.

> **Now close the tab you were in before.** You have two tabs open and they look almost identical. The old one is not yours — nothing you type there is saved, and it is easy to spend a whole session working in the wrong tab and lose it all.
>
> Check the title at the top left reads **`Copy of lab.ipynb`** before you go on.

Your copy stays in your Google Drive permanently — you can reopen it next month.

**Do not run anything yet.** The first cell needs a key, and you do not have one yet. That is the next part.

---

## Part 2 — Get a free API key (5 minutes)

This is the key the lab uses to talk to the AI model. It is free and **no credit card is required.**

1. Open **<https://console.groq.com>** in a new tab.
2. Click **Sign in** → **Continue with Google**. Any Google account works.
3. In the menu on the left, click **API Keys**.
4. Click **Create API Key**.
5. Give it any name — type `lab` — and click **Submit**.
6. A long string starting with `gsk_` appears. **Click the copy button now.**

> **This is the one thing you cannot undo.** The key is shown only once. If you close the box without copying it, delete that key and create another. That is free and takes ten seconds.

**What a key looks like:** `gsk_` followed by about 50 letters and numbers. If yours does not start with `gsk_`, you copied the wrong thing.

**Never share your key or put it in a screenshot.** Anyone who has it can use your account.

---

## Part 3 — Store the key in Colab (2 minutes)

Go back to your Colab tab. Do **not** paste the key into a code cell — Colab has a proper place for it.

1. On the **far left edge** of the screen, click the **🔑 key icon**. The panel is called **Secrets**.
2. Click **+ Add new secret**.
3. A row appears with four columns. Fill in the middle two, then switch on the first:

| Column | What to do |
|---|---|
| **Name** | Type `LLM_API_KEY` — all capitals, two underscores |
| **Value** | Paste your `gsk_...` key |
| **Notebook access** | **Click the toggle so it turns on** |
| Actions | Leave alone |

### The two things that go wrong here

**The Notebook access toggle starts OFF.** It shows a grey ✕ until you click it. Leave it off and the notebook cannot see your key — Setup fails at stage 4 even though the secret looks saved. This is the single most common failure.

**The Name box is narrow and hides the end of what you typed.** It can display `LLM_API` whether or not you typed the whole thing. Click into the box and press `End` to check. It must read `LLM_API_KEY` exactly — close is not good enough.

**Also watch for a space** at either end of the pasted key. That produces a `401 unauthorised` later, not an obvious error here.

---

## Part 4 — Run the Setup cell (3 minutes)

Now you can run something.

Scroll to the grey cell labelled **Setup**. Hover over it and a **▶ play button** appears on its left. Click it.

> **Keyboard shortcut:** `Shift + Enter` runs the cell you are in and moves to the next. You will use this constantly during the session.

The cell downloads the lab files, installs what is needed, and checks everything. It prints five numbered stages.

**It takes 2–3 minutes the first time and will look frozen during stage 3.** It is downloading a small language model. Let it finish — do not click the button again.

You want it to end with:

```
  READY. Took 154 seconds.
```

If a stage fails, it prints the specific fix underneath. Follow that, then run the cell again.

---

## Part 5 — Check it worked

The Setup cell already ran this for you. To run it again at any time:

```python
!python verify_setup.py
```

You want to see seven `PASS` lines:

```
  Python 3.9 or newer.........................PASS  3.11.9
  Required packages installed.................PASS  all present
  Corpus files present........................PASS  227 chunks
  Embeddings match the corpus.................PASS  227 x 384
  Embedding model loads.......................PASS  all-MiniLM-L6-v2
  API key found...............................PASS  from Colab secrets, ...a3f9
  The model answers...........................PASS  The wire works

  All checks passed. You are ready for the session.
```

If anything says `FAIL`, the message underneath tells you what to fix. See the table at the bottom of this page.

**That is the whole setup. Stop here.** You do not need to understand the code yet — that is what the session is for.

---

## The documents we will use

*(Reference — nothing to install.)*

The lab answers questions about **your own B.Tech academic regulations**. You do not need to download anything for the session — the text is already bundled in the repo — but keep the PDF open in another tab so you can check the answers yourself.

That habit is the whole point: an answer you cannot verify is not an answer.

| Regulation | Applies to | PDF |
|---|---|---|
| **R22.1** | 2022–2024 admissions — **most likely yours** | [download](https://vignan.ac.in/2023pdf/R22.1-B.Tech%20Regulations.pdf) |
| R25 | 2025 admissions | [download](https://vignan.ac.in/2023pdf/R25_Regulations%20Final%20For%20BTech.pdf) |
| R26 | 2026 admissions | [download](https://vignan.ac.in/2023pdf/R26_Regulations_B.Tech.pdf) |

All of them are listed on the university's own page: <https://vignan.ac.in/newvignan/Regulations.php>

> Not sure which applies to you? Ask your department. It changes very little here — the rules this lab uses (75% attendance, 10% condonation, 60:40 marks split, 160 credits) are **identical in all three**.

---

## Running on your own machine instead (optional)

Only if you would rather not use Colab. Colab is the supported path and what the session will demo.

```bash
git clone https://github.com/coolMukul/rough.git
cd rough/ai-lab

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env               # Windows: copy .env.example .env
# open .env and paste your key after LLM_API_KEY=

python verify_setup.py
```

Needs Python 3.9 or newer. The first run downloads about 90 MB for the embedding model.

`.env` is gitignored and will not be committed. Never put a real key in any other file.

---

## When something breaks

| What you see | What it means | What to do |
|---|---|---|
| `401 unauthorised` | The key is wrong, or was deleted | Create a new key and update the secret. Check for a space at either end. |
| `429 rate limited` | You sent too many requests | Wait 60 seconds and run the cell again. **Do not** keep clicking — that makes it worse. |
| `404 model not available` | The provider retired that model | Tell the coordinator. One line in the config fixes it for everyone. |
| `no API key found` | The secret name is wrong, or the toggle is off | Name must be exactly `LLM_API_KEY`. Check the **Notebook access** toggle is on. |
| `NameError: name 'chat' is not defined` | You skipped an earlier cell | Run **Runtime → Run all**, then carry on from where you were. |
| Everything suddenly fails | Colab disconnected you for being idle | **Runtime → Restart and run all.** Your typed code is safe. |
| The page looks completely different | You are in the original, not your copy | Go back to **File → Save a copy in Drive**. |

### During the session

**If your setup breaks, do not stop and debug it.** Each step of the lab is a fresh script that sets itself up from scratch. Skip the broken one, run the next, and you will be caught up automatically. You will never be stranded because one step failed.

---

## For the lecturer

Regenerate the shipped corpus after changing the source PDF or the chunking:

```bash
python tools/build_corpus.py                    # chunks + embeddings
python tools/build_corpus.py --skip-embeddings  # fast chunking iteration
```

Writes `data/chunks.json`, `data/embeddings.npy` and `data/manifest.json`. The manifest pins the embedding model name, and `verify_setup.py` fails loudly if a query would be embedded by a different model than the documents were — that mismatch otherwise returns quiet nonsense rather than an error.

Source PDFs and planning notes are kept in the private working repository.
