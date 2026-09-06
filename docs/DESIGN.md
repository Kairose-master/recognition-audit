# Design — first two audits

Status: draft; to be frozen (statistics and predictions) before any model data.

## Common instrument

Rows: a base input and its declared variants (`same`: permutations,
duplications, declared paraphrases or redundant additions; `differ`: one
minimal declared-relevant change). Tests: continuations (extra items
appended) at depth 0–1 and a small query set. Readout: decision and pairwise
preference bits. Statistics: `S` (one-sided), `V` (free columns), `E` (exact
identities), closure of the depth-0 family with witness. Controls: the
synthetic invariant recognizer (must be 0) and gold-plus-noise (calibrates
`S`, `V`); a non-reading model where one exists.

## Audit 1 — option order in an LLM-as-judge

Base: a comparison prompt with `k` candidate answers as a declared set;
query: "is option X best?" for each X, read as the logit pair. `same`:
option permutations. `differ`: replace one option by a clearly worse
version (declared-relevant change). Prediction to be recorded: `S > 1` for
small instruction-tuned models (order effects exceed a quality change), as
Set-LLM's baseline numbers suggest.

## Audit 2 — document order in a RAG answerer

Base: a question with `k` retrieved passages as a declared set; query: a
factual yes/no about the passages. `same`: passage permutations and one
duplicated passage. `differ`: swap the supporting passage for a
contradicting one. Prediction to be recorded: `S > 1` under permutations
that move the supporting passage away from the end.

## What the audit will not claim

Identical profiles are "not separated by these tests". `S < 1` is not
invariance. No witness on sampled rows establishes only sampled stability. Global
identification additionally requires the universal closure assumptions; see
`IDENTIFICATION_SCOPE.md`.

