# The whole lab as one script

The lab itself is **`lab.ipynb`** — a notebook you work down one cell at a time,
where the code is visible and meant to be edited. That is what the session uses.

This folder holds one thing: `full_flow.py`, the same application written as a
single script that runs top to bottom without stopping. It is useful for
checking the whole pipeline still works after a change, and for reading the
twelve steps as one continuous piece of code rather than as notebook cells.

```python
!python steps/full_flow.py --upto 8    # stop after step 8
!python steps/full_flow.py --quick     # everything, shorter eval
!python steps/full_flow.py --upto 0    # set-up only, no API calls
```

Pacing is 2.5 seconds between calls by default, which keeps a free-tier key
under its per-minute limit:

```python
!LAB_DELAY=4 python steps/full_flow.py --quick
```

**Watch the cost.** The full run includes the evaluation, which is thirty API
calls. Use `--quick` or `--upto` unless you actually want the eval.

---

## Two things in here are not finished

**Steps 9 and 10, the agent loop, do not work reliably.** `gpt-oss-120b` and
`qwen3` are reasoning models. Asked to reply with only a JSON tool call, they
either bury the JSON in a separate `reasoning` field and return empty content,
or skip the tools entirely and invent an answer — in testing one claimed *"you
are eligible, your attendance and CGPA meet the criteria"* having read no
record at all.

Native tool calling fixes it and is verified working on both models. But that
changes what step 9 teaches — from *"the model emits JSON, your code parses
it"* to *"the model returns a structured `tool_calls` field"*. It is a teaching
decision, not just a fix, so it is still open. These steps are in the script
but not in the notebook.

**Step 7 does not show the win it was designed to show.** The plan was: TF-IDF
fails on a paraphrased question, embeddings fix it. Six paraphrasings across
two embedding models say otherwise — embeddings do not reliably beat TF-IDF on
this corpus and are sometimes worse. The right clause is there; it just ranks
below other attendance clauses that look equally plausible.

The step still runs and still puts the two retrievers side by side. It just
does not end in a clean win, and the notebook now says so rather than
pretending. Which is arguably the better lesson: *you cannot tell whether a
change helped without measuring it* walks straight into step 11.
