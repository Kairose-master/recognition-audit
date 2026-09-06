# Audit 1b preregistration — option order in an LLM-as-judge (capital cities)

Status: **FROZEN BEFORE ANY MODEL OUTPUT IS READ.** A 32-cell reading check
(8 countries, base rows only) was run first: Qwen2.5-0.5B comparative
accuracy 1.00, Qwen2.5-1.5B 1.00. That check is not part of the audit
and its cells are regenerated here with a different seed layout.

## Table

Same design as Audit 1 (`docs/AUDIT1_PREREG.md`) with the arithmetic
questions replaced by 16 capital-city questions and candidate capitals.
144 rows (base, 5 permutations, 2 duplications, 1 correct-option
replacement per question) × 8 cells = 1152 prompts; 20 Boolean tests per
row. Calibration on gold-plus-noise: `S` 0.47, `V` 1.00, `E` 1 of 112 (corrected from a typo before any result was read; the arithmetic table gave 2).

## Recorded predictions

- Pythia-70M: comparative accuracy near 0.5; `S` near 1; profiles
  degenerate (many identical), reported with the non-constant-column count.
- Qwen2.5-0.5B: comparative accuracy above 0.9. `S < 1` (removing the
  correct option moves the judge more than reordering does), which is not
  diagnostic; `V` between 0.7 and 1.3; `E` between 5 and 30 of 112
  (strong reading on 20 bits makes exact identities likely, above the
  chance baseline of about 3).
- Qwen2.5-1.5B: comparative accuracy near 1.0; `E` higher than for 0.5B;
  `V` between 0.7 and 1.3.
- Depth-0 family not closed for the Qwen models: some row pairs agree on
  the four direct decisions and differ on the extra-option column.

## What would be a finding

`S > 1` for a reader (order outweighs correctness) would be the strong
finding and is not predicted here. `E` well above chance with `V` near 1
would mean: the judge's decisions are exactly order-invariant on many
rows, while its preferences among wrong candidates are not.
