# The steps

Each script runs on its own. **You do not need to have run the earlier ones** — every script rebuilds what it needs. If one fails for you, skip it and run the next.

Run one like this:

```python
!python steps/step_06.py
```

| # | Script | What it shows | API calls |
|---|---|---|---|
| 1 | `step_01.py` | The model has no memory. Everything that feels like memory is a list your code re-sends | 3 |
| 2 | `step_02.py` | Ask about VFSTR with no context and watch it invent | 1 |
| 3 | `step_03.py` | Load the 227 regulation clauses | **0** |
| 4 | `step_04.py` | Retrieve with TF-IDF — pure search, no model | **0** |
| 5 | `step_05.py` | Answer using only the retrieved text. This is RAG | 1 |
| 6 | `step_06.py` | **Break it.** Refusal, `k=1` vs `k=6`, and the paraphrase gap | 3 |
| 7 | `step_07.py` | Swap TF-IDF for embeddings | 1 |
| 8 | `step_08.py` | A fixed workflow — model in one box, `if` statements in the others | 4 |
| 9 | — | *The agent loop. Not written yet, see below* | — |
| 10 | — | *Breaking the agent. Not written yet* | — |
| 11 | `step_11.py` | Score it against ten questions with known answers | **30** |

Steps 3 and 4 cost nothing — run them as often as you like.

**Step 11 makes 30 calls** (ten questions across three retriever settings). On a free tier that takes a couple of minutes with the built-in pacing. Don't run it casually.

---

## Running them

```python
!python steps/step_01.py          # one step
!python steps/step_06.py          # the important one
```

Or the whole thing end to end:

```python
!python steps/full_flow.py --upto 8       # stop after step 8
!python steps/full_flow.py --quick        # everything, shorter eval
```

Pacing is 2.5 seconds between calls by default, which keeps a free-tier key under its per-minute limit. To change it:

```python
!LAB_DELAY=4 python steps/step_06.py
```

---

## Steps 9 and 10 are missing on purpose

The agent loop is written in `full_flow.py` but **it does not work reliably**, so it has not been split out yet.

The cause: `gpt-oss-120b` and `qwen3` are reasoning models. Asked to reply with only a JSON tool call, they either bury the JSON in a separate `reasoning` field and return empty content, or skip the tools entirely and invent an answer — in testing one claimed *"you are eligible, your attendance and CGPA meet the criteria"* having read no record at all.

Native tool calling fixes it and is verified working on both models. That changes what step 9 teaches — from *"the model emits JSON, your code parses it"* to *"the model returns a structured `tool_calls` field"* — so it is a decision, not just a fix. Pending.

---

## Known open question — step 7

The plan was: TF-IDF fails on a paraphrased question, embeddings fix it.

**Tested, and it does not hold.** Six paraphrasings across two embedding models; embeddings do not reliably beat TF-IDF on this corpus and are sometimes worse. The right clause is in the corpus — it just ranks below other attendance clauses that look equally plausible.

Step 7 still runs and still shows the two retrievers side by side. It just does not show a clean win. Three ways to respond:

- Change the lesson to match the evidence: *embeddings are not a magic fix, and the only way to know is to measure* — which walks straight into step 11
- Keep hunting for a query where embeddings clearly win
- Cut the step and stay on TF-IDF

Undecided.
