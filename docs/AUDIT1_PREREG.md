# Audit 1 preregistration — option order in an LLM-as-judge

Status: **FROZEN BEFORE ANY MODEL OUTPUT IS READ** (runs launched in the same
minute as this commit; no result file opened before the commit).

## Table (`audits/judge_order.py`, seed 0)

16 arithmetic questions (two-digit `+`, `-`, `*`), four candidate answers
each, one correct. Query per candidate value `v`: "Is `v` the correct answer
among the candidates?" Gold: `v` is listed and correct. Rows per question:
base, 5 permutations (reversal first), 2 duplications (`same`), and one
`differ` row in which the correct option is replaced by a fresh wrong value.
Continuations: none, and one extra wrong option appended (depth 1). 144
rows × 8 cells = 1152 prompts; 20 Boolean tests per row (8 decisions, 12
preferences). One rendering.

## Statistics

`S` = median over questions of d_same / d_differ (one-sided; only `S > 1`
diagnostic). `V` on preference columns whose gold ties. `E` = number of
`same` rows (of 112) with a profile identical to their base. Closure of
the depth-0 family against the depth-1 column. Decision accuracy and
comparative accuracy.

Calibration on the gold-plus-noise control (run before any model):
`S` 0.50, `V` 1.00, `E` 2 of 112. So `E` up to about 2 is chance on 20
bits; `S` 0.5 is what accuracy alone gives.

## Recognizers

Pythia-70M (`step143000`, non-reading control), Qwen2.5-0.5B-Instruct,
Qwen2.5-1.5B-Instruct; raw prompts, one forward pass, float32.

## Recorded predictions

- Pythia-70M: comparative accuracy near 0.5; `S` near 1; `E` ≤ 3.
- Qwen2.5-0.5B: comparative accuracy 0.6–0.8; **`S > 1`** (reordering or
  duplicating the candidates moves the judge more than removing the
  correct answer does); `V > 1`; `E` ≤ 3.
- Qwen2.5-1.5B: comparative accuracy above 0.8; `S` between 0.7 and 1.3;
  `E` ≤ 3.
- Depth-0 family not closed for any recognizer (some row pairs identical on
  the 4 direct decisions but separated by the extra-option column).

## Interpretation boundary

`S > 1` for a reader means candidate order outweighs candidate correctness
in this judge's verification. `S < 1` is not invariance. Identical
profiles mean "not separated by these 20 tests".
