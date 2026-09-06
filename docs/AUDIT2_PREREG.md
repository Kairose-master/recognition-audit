# Audit 2 preregistration — document order in a RAG answerer

Status: **FROZEN BEFORE ANY MODEL RESULT IS READ.** Table:
`runs/rag_order.cells.jsonl` (built by `audits/rag_order.py build`).

## Table

16 bases. Each: four passages "<Entity> was completed in <year>." about
fictional entities (no parametric knowledge), four queries asking whether
an entity was completed in a stated year (two true years, two false), gold
= the passage is present and states the asked year. Variants: 5
permutations + 2 duplications (`same`, 112 rows), and the passage behind
the first true query replaced by one stating a different year (`differ`,
16 rows, that query's gold becomes NO). Continuations: none; one extra
irrelevant passage (depth 1). 144 rows × 8 cells = 1152 prompts; 20 Boolean
tests per row.

Reading check on 8 bases (base rows, depth 0): Qwen2.5-0.5B comparative
accuracy 0.97, Qwen2.5-1.5B 0.94. The task is read.

Calibration on gold-plus-noise: `S` 0.35, `V` 1.75, `E` 4 of 112.

## Statistics

As in Audit 1b: `S` (one-sided), `V` (free columns), `E`, non-constant
columns, depth-0 closure with witness, decision and comparative accuracy.
Exploratory: decision accuracy by position of the queried passage
(first / middle / last), depth-0 cells only.

## Predictions

- Pythia-70M: comparative accuracy near 0.5; degenerate columns.
- Qwen2.5-0.5B: comparative accuracy > 0.9; `S < 1`; `V` 0.5–1.5; `E`
  5–40; not closed. Exploratory: accuracy lower for middle positions than
  for first or last.
- Qwen2.5-1.5B: comparative accuracy > 0.9; `E` higher than 0.5B's; `V`
  0.5–1.5; not closed; position effect smaller than 0.5B's.
