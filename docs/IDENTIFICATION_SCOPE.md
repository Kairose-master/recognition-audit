# Identification scope and next research gates

## Implemented: sampled refinement (schema 2)

`closure_check` compares only supplied Boolean rows and columns. It reports
`separation_found`, `no_separation_observed`, or `no_comparable_pairs`.
The last case is vacuous. Missing lower or next-depth columns are rejected.
`sampled_stable` is descriptive, and `global_identification_established` is
always false. The former `closed` key is removed to prevent accidental use
as a certificate. Existing archived reports retain their historical schema;
their `closed` field must be read as sampled stability, not global closure.

A next-depth separator is an observed distinction. Interpreting it as a
counterexample to the Lean closure condition additionally requires correct
continuation semantics and coverage of the relevant lower test family.
Checking a subset of columns is not agreement on every bounded-length test.

## OPEN: finite-state bridge (proof outline, not Lean-certified here)

Assume a known finite deterministic realization S, a total transition for
every symbol, an output for every query, and complete state/transition access.
Let P_0 equate states with equal query outputs, and refine by

P_(k+1)(s,t) iff P_0(s,t) and for every a, P_k(delta(s,a),delta(t,a)).

Induction identifies P_k with agreement on every continuation of length at
most k. A stable partition is transition-compatible; induction on words
then establishes full contextual agreement. Every strict refinement adds
at least one block, so a realization with n >= 1 states and b initial
blocks stabilizes after at most n-b strict refinements (hence n-1).
For an executable finite enumeration, the alphabet and query family must
also be finite, or their comparisons discharged by another complete oracle.

These assumptions are not established by sampled LLM prompts. A state bound
without coverage/conformance evidence is not a certificate. Next formal task:
prove this bridge in recognition-paths and expose its assumptions explicitly.

## Implemented: semantic oracle control

`audit/adapters/horn.py` computes definite-Horn closure by forward chaining.
Its semantic key evaluates closure for ALL assumption subsets of a fixed
atom universe. Singleton antecedents are insufficient for conjunctions:
the empty theory and {a AND b -> c} agree on singleton closures but differ
on the assumption {a,b}. Facts, conjunction heads, and cycles are supported.
Tests compare entailment against independent truth-table model enumeration.

This is an exact small-world control, not evidence of learned invariance.
No new LLM results or preregistered empirical endpoints are claimed here.
The next instrument integration must use the same frozen tables/readout as
the learned recognizers and retain S's one-sided interpretation. A zero
denominator makes S or V undefined, not zero or a successful gate.

## Execution order

1. Review schema migration and scope wording; keep historical measurements.
2. Integrate this control into the frozen Horn-table runner and validate
   semantic rewrites, logical flips, and all reported denominators.
3. Formalize the finite-state bridge with state coverage assumptions.
4. Freeze new structure/length holdouts before further learned-model runs.
5. Quantitative geometry or monads require additional independently justified
   structure; neither is implied by this finite Boolean audit.
