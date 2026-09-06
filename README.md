# recognition-audit

Invariance audits for language models under **declared equivalences**.

You declare which parts of an input are interchangeable (a set of premises,
a list of retrieved documents, the options of a multiple-choice question,
paraphrases of one claim). The audit builds a Boolean Hankel table from
your model's answer logits, reads it through order relations only
(threshold-free, offset-invariant), and reports:

- how many tests separate inputs that your declaration says are the same,
  against how many separate inputs that differ in one declared-relevant
  way (the one-sided statistic `S` of `proof-path-invariance`);
- the beyond-accuracy statistic `V` on tests where correctness imposes
  nothing;
- whether the finite test family is *closed* under one-step extension, i.e.
  whether it has decided the question or needs a longer test, with the
  witness (`recognition-paths`, `Identification.lean`).

The theory is in [recognition-paths](https://github.com/Kairose-master/recognition-paths)
(Lean 4, machine-checked); the Horn-logic instrument and results are in
[proof-path-invariance](https://github.com/Kairose-master/proof-path-invariance).
This repository is the domain-independent tool layer.

## Status

Audit 1b (option order in an LLM-as-judge, capital-city verification) is
run and reported: `docs/AUDIT1B_RESULT.md`. Decisions are largely
order-invariant for Qwen2.5-0.5B/1.5B; preferences among wrong candidates
are not; no finite family tried is closed. Audit 1 (arithmetic) was
uninformative because no model read it (`docs/AUDIT1_RESULT.md`). Next:
document order in a RAG answerer (`docs/DESIGN.md`).

## Layout

```
audit/equivalences/   declared equivalence classes (permutation, duplication, paraphrase sets)
audit/table.py        rows x tests -> prompts, with gold where a reference exists
audit/readout.py      logit pairs -> Boolean profiles (decision, preference)
audit/stats.py        Hamming, S, V, exact-identity counts, closure check with witness
audit/adapters/       model backends (local HF; API adapters that expose logprobs)
docs/                 design, preregistrations, results
tests/                synthetic-recognizer tests (an invariant recognizer must score 0)
```

## Discipline

`AGENTS.md`: labels PROVED / OBSERVED / HYPOTHESIS / OPEN / CONFOUND;
preregister before data; a non-reading control for every statistic; `S`
is one-sided; identical profiles mean "not separated by these tests".
