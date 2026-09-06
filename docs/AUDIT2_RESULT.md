# Audit 2 result — document order in a RAG answerer

Status: **RUN AS PREREGISTERED (`docs/AUDIT2_PREREG.md`).** Raw results in
`results/rag_order.*.jsonl.gz`, reports in `results/rag_order.*.report.json`.

| recognizer | comparative acc. | decision acc. | `S` | `V` | `E` (of 112) | non-constant cols | depth-0 closed |
|---|---:|---:|---:|---:|---:|---:|:---:|
| Pythia-70M (control) | 0.48 | 0.47 | 1.00 | 0.50 | 46 | 12 / 16 | no (604 / 317) |
| Qwen2.5-0.5B | 0.97 | 0.97 | 0.25 | 1.50 | 32 | 16 / 16 | no (1894 / 836) |
| Qwen2.5-1.5B | 0.92 | 0.59 | 0.37 | 1.00 | 21 | 16 / 16 | no (1076 / 853) |

Decision accuracy by position of the queried passage (exploratory,
depth-0 cells): 0.5B first 0.99 / middle 0.99 / last 0.97; 1.5B first 0.38
/ middle 0.61 / last 0.74; control 0.78 / 0.39 / 0.33.

## Predictions against outcomes

- Control at chance with degenerate columns: held (comparative accuracy
  0.48; 12 of 16 columns non-constant; its `E` of 46 is degeneracy).
- Qwen-0.5B: comparative accuracy > 0.9 (0.97), `S < 1` (0.25), `V`
  0.5–1.5 (1.50, at the edge), `E` 5–40 (32), not closed: all held.
  Exploratory lost-in-the-middle prediction (middle worse than first and
  last): **failed**; accuracy is flat across positions (0.99 / 0.99 / 0.97).
- Qwen-1.5B: comparative accuracy > 0.9 (0.92), `V` 0.5–1.5 (1.00), not
  closed: held. `E` above 0.5B's: **failed** (21 < 32). Position effect
  smaller than 0.5B's: **failed**; the 1.5B has a large monotone recency
  effect on its decisions (0.38 → 0.61 → 0.74).

## Reading

The 1.5B's decisions are biased: with the raw YES/NO logit comparison it
answers NO on 478 of the 544 gold-YES cells (0.5B: 544 of 544 correct),
while its comparative ordering of margins is still right 92 % of the
time. Its position effect is therefore an effect on where a NO-biased
threshold is crossed, not a change in what it reads; the 0.5B, whose
decisions are calibrated on this task, shows no position effect at all.
Neither model treats reorderings as identities: on the target passages
`V` is 1.0–1.5, i.e. reordering or duplicating the four passages moves the
recognizer's free-column preferences as much as (0.5B: more than) replacing
the relevant passage with one stating a different year. Neither depth-0
family is closed; every witness pair is separated by the extra-passage
column, so the extra irrelevant passage is itself an input the answerer
does not identify away.

Practical reading for RAG use at this scale: which passage answers the
question is read correctly regardless of order (0.5B), but the answerer's
output is not a function of the passage *set*; duplication and order leave
a trace as large as a substantive change to the evidence, and the larger
model adds a decision bias that depends on where the evidence sits.

## Limits

Sixteen bases, four passages each, one rendering, no chat template, models
to 1.5B, 20 tests per row. The 1.5B decision-accuracy numbers are dominated
by its NO bias; a calibrated threshold was not preregistered and is not
reported.
