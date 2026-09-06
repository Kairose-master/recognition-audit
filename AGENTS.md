# AGENTS.md — recognition-audit

Same epistemic rules as proof-path-invariance, restated for a
domain-independent tool.

1. **Declared, not inferred.** An equivalence is an input of the audit,
   declared by the user (or certified by a formal layer). The tool never
   guesses which inputs are equivalent.
2. **Order relations only.** The readout is the decision `pos > neg` and
   pairwise preferences between tests; no thresholds, no metrics on logits.
3. **One-sided statistics.** `S < 1` is reached by accuracy alone; only
   `S > 1` is diagnostic. `V` (tests where gold ties) is the
   beyond-accuracy measure. Say so in every report.
4. **Controls.** Every reported number ships with a synthetic invariant
   recognizer (must score exactly 0 on declared equivalences) and, where a
   non-reading model is available, a non-reading control.
5. **Closure.** Report whether the test family is closed under one-step
   extension; if not, report the witness. Never call rows with identical
   profiles "equivalent to the model"; call them "not separated by T".
6. **Preregister.** Statistics and predictions are committed before data;
   failed predictions stay in the record.
7. **Labels.** PROVED (Lean, in recognition-paths), OBSERVED, HYPOTHESIS,
   OPEN, CONFOUND.
