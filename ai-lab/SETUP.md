# Setup — AI in Industry Lab

**Do this before the session, not on the day.** It takes about 15 minutes and you only need a web browser. If something fails, message the coordinator — do not wait until the session starts.

Nothing installs on your own computer. Everything runs on Google's servers. A slow or old laptop is fine.

---

## Part 1 — Get a free API key (5 minutes)

You need a key to talk to the AI model. It is free and **no credit card is required.**

1. Open **<https://console.groq.com>** in your browser.
2. Click **Sign in** and choose **Continue with Google**. Use any Google account.
3. Once you are signed in, look at the menu on the left and click **API Keys**.
4. Click the **Create API Key** button.
5. Give it any name — type `lab` — and click **Submit**.
6. A long string starting with `gsk_` appears. **Click the copy button now.**

> **This is the one thing you cannot undo.** The key is shown only once. If you close the box without copying it, delete that key and create another one. That is fine and costs nothing.

7. Paste it somewhere you can get it back from — a note on your phone, a text file, a WhatsApp message to yourself.

**What a key looks like:** `gsk_` followed by about 50 letters and numbers. If yours does not start with `gsk_`, you copied the wrong thing.

**Never share your key or put it in a screenshot.** Anyone who has it can use your account.

---

## Part 2 — Open the lab in Google Colab (10 minutes)

Google Colab runs Python in your browser. You do not install anything.

### 2.1 — Sign in to Google

Open **<https://colab.research.google.com>**. If it asks you to sign in, use the same Google account as before.

If you see a pop-up saying "Open notebook", close it with the **Cancel** button or the **X**.

### 2.2 — Open the lab notebook

Click this link. The notebook opens straight in Colab — you do not need a GitHub account.

**<https://colab.research.google.com/github/coolMukul/rough/blob/main/ai-lab/lab.ipynb>**


You are now looking at the lab. It is made of **cells** — grey boxes containing code, and white boxes containing instructions.

### 2.3 — Make your own copy — do not skip this

At the top of the screen, click **File** → **Save a copy in Drive**.

A new tab opens with `Copy of ...` in the title. **Work in this new tab and close the old one.**

> Without this step, nothing you type is saved. Your copy stays in your Google Drive permanently — you can come back to it next month.

### 2.4 — Learn the one control you need

Hover your mouse over the first grey code cell. A **▶ play button** appears on its left. Click it.

That runs the cell. A spinner turns while it works, then output appears underneath.

**Keyboard shortcut:** `Shift + Enter` runs the cell you are in and moves to the next one. You will use this constantly.

> The **first** cell you run takes 20–30 seconds, because Colab is starting a machine for you. Later cells are much faster. This is normal — do not click the button repeatedly.

### 2.5 — Store your API key in Colab

Do **not** paste your key directly into a code cell. Colab has a proper place for it.

1. On the far left edge of the screen, find the **🔑 key icon** and click it. The panel is called **Secrets**.
2. Click **+ Add new secret**.
3. In the **Name** box type exactly: `LLM_API_KEY`
   - All capitals, with underscores. Copy and paste it to be safe.
4. In the **Value** box, paste your `gsk_...` key.
5. Turn **on** the toggle in the **Notebook access** column.

> **The single most common mistake** is a space at the start or end of the pasted key. If your key fails later, delete the secret and paste it again carefully.

### 2.6 — Run the setup cell

Find the cell near the top labelled **Setup** and run it. It downloads the lab files and installs what is needed.

**It takes 2–3 minutes the first time.** It is downloading a small language model. Let it finish — you will see `All checks passed` at the end.

You are done. **Do not close the tab without checking your copy is in Drive.**

---

## The documents we will use

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

## Part 3 — Check it worked

Run the check cell:

```python
!python verify_setup.py
```

You want to see seven `PASS` lines:

```
  Python 3.9 or newer.........................PASS  3.11.9
  Required packages installed.................PASS  all present
  Corpus files present........................PASS  148 chunks
  Embeddings match the corpus.................PASS  148 x 384
  Embedding model loads.......................PASS  all-MiniLM-L6-v2
  API key found...............................PASS  from Colab secrets, ...a3f9
  The model answers...........................PASS  The wire works

  All checks passed. You are ready for the session.
```

If anything says `FAIL`, the message underneath tells you what to fix. See the table at the bottom of this page.

**That is the whole setup. Stop here.** You do not need to understand the code yet — that is what the session is for.

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
