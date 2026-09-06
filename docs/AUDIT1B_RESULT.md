# Audit 1b result — option order in an LLM-as-judge (capital cities)

Status: **RUN AS PREREGISTERED (`docs/AUDIT1B_PREREG.md`).** Raw results in
`results/judge_capitals.*.jsonl.gz`, reports in `results/*.report.json`.

| recognizer | comparative acc. | decision acc. | `S` | `V` | `E` (of 112) | non-constant cols | depth-0 closed |
|---|---:|---:|---:|---:|---:|---:|:---:|
| Pythia-70M (control) | 0.43 | 0.22 | 0.50 | 0.75 | 32 | 12 / 20 | no (670 / 444) |
| Qwen2.5-0.5B | 0.997 | 0.65 | 0.28 | 1.00 | 18 | 20 / 20 | no (230 / 145) |
| Qwen2.5-1.5B | 1.000 | 0.96 | 0.40 | 0.55 | 40 | 20 / 20 | no (673 / 327) |

## Predictions against outcomes

- Control at chance with degenerate columns: held (12 of 20 columns
  non-constant; its `E` is degeneracy, not identity).
- Qwen-0.5B: accuracy above 0.9 (0.997), `S < 1` (0.28), `V` 0.7–1.3
  (1.00), `E` 5–30 (18), not closed: all held.
- Qwen-1.5B: accuracy near 1 (1.00), `E` above 0.5B's (40 > 18), not
  closed: held. `V` predicted 0.7–1.3, observed **0.55**: below the range.
  With near-perfect reading, `d_differ` is only 0–6 bits (the correct
  option's removal flips exactly the bits it should), so the ratio has a
  small denominator; read `V` here as "reorderings move the wrong-candidate
  preferences about half as much as removing the right answer does".

## Reading

For both readers, candidate order and duplication move the judge's
**decisions** little: on 18 (0.5B) and 40 (1.5B) of 112 reordered or
duplicated rows the entire 20-bit profile is unchanged, far above the
chance baseline of about 1–3. The **preferences among wrong candidates**
are not order-invariant: for 0.5B they move under reordering as much as
under removing the right answer (`V` 1.0); for 1.5B about half as much
(`V` 0.55). The depth-0 family is not closed for either: rows that agree on
the four direct decisions are separated by the extra-option column (0.5B
witness) or by a preference under the extra option (1.5B witness), so a
one-step-longer test is needed before any row pair can be called
indistinguishable.

Practical reading for LLM-as-judge use: which option is *correct* is
robust to order at this scale; how the judge *ranks the incorrect ones*
is not, and that is the part used in ties and rankings.

## Limits

Sixteen questions, one rendering, no chat template, models to 1.5B, 20
tests per row. Audit 1 (arithmetic verification) was uninformative because
no model read it (`docs/AUDIT1_RESULT.md`); the task had to be changed
before the audit could say anything, which is the Gate R rule working as
intended.
