"""An invariant recognizer must score 0 on declared-same variants; an accurate
non-invariant one must not reach V near 0."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from audit.table import Table
from audit.equivalences import permutations, declared_set
from audit.readout import boolean_profiles
from audit.stats import audit_report, closure_check
from audit.adapters.synthetic import invariant_recognizer, gold_plus_noise


def horn_gold(items, query):
    known = {query[0]}; changed = True
    while changed:
        changed = False
        for b, h in items:
            if b in known and h not in known:
                known.add(h); changed = True
    return query[1] in known


def render(items, query):
    return "; ".join(f"{b}->{h}" for b, h in items) + f" ? {query[0]}=>{query[1]} Answer:"


def build():
    bases = {"chain": [("a", "b"), ("b", "c"), ("c", "d")], "skip": [("a", "c"), ("c", "e"), ("b", "d")]}
    def variants(items):
        vs = permutations(items, max_variants=3)
        flips = [[(h, b) if i == j else (b, h) for j, (b, h) in enumerate(items)] for i in range(len(items))]
        vs += declared_set(items, same=[items + [("a", "d")]] if horn_gold(items, ("a", "d")) else [], differ=flips)
        return vs
    conts = {"none": [], "d_e": [("d", "e")], "b_c": [("b", "c")]}
    queries = {"ad": ("a", "d"), "ae": ("a", "e"), "bd": ("b", "d")}
    t = Table.from_declarations(bases, variants, conts, queries, render, gold=horn_gold)
    for c in t.cells:  # give the synthetic recognizers the items
        row = next(r for r in t.rows if r.row_id == c["row_id"]); test = next(x for x in t.tests if x.test_id == c["test_id"])
        c["_items"] = row.items + test.continuation
    meta = {r.row_id: {"base_id": r.base_id, "kind": r.kind} for r in t.rows}
    return t, meta


ATOMS = "abcde"


def closure_key(c):
    """Theory-level key: the full entailment table of the items (ideal recognizer)."""
    items = c["_items"]
    return (tuple(horn_gold(items, (x, y)) for x in ATOMS for y in ATOMS if x != y), c["query_id"])


def test_set_invariant_scores_zero_on_syntactic_sames():
    t, meta = build()
    res = invariant_recognizer(t.cells)          # keyed on the item set: syntactic invariance only
    prof, free, cols = boolean_profiles(res)
    rep = audit_report(prof, free, meta)
    syntactic = [r for r in t.rows if r.kind == "same" and not r.variant.startswith("same")]
    assert all(hamming_zero(prof, f"{r.base_id}-base", r.row_id) for r in syntactic)
    # the semantic same (redundant derivable clause) is NOT identified by a set-keyed recognizer
    semantic = [r for r in t.rows if r.variant.startswith("same")]
    assert semantic and not all(hamming_zero(prof, f"{r.base_id}-base", r.row_id) for r in semantic)


def test_ideal_recognizer_scores_zero_on_all_sames():
    t, meta = build()
    res = invariant_recognizer(t.cells, key=closure_key)   # keyed on the closure: logical invariance
    prof, free, cols = boolean_profiles(res)
    rep = audit_report(prof, free, meta)
    assert rep["identical_same_variants"] == rep["same_variants"], rep


def hamming_zero(prof, u, v):
    return int((prof[u] != prof[v]).sum()) == 0


def test_accurate_noninvariant_is_not_identified():
    t, meta = build()
    res = gold_plus_noise(t.cells)
    prof, free, cols = boolean_profiles(res)
    rep = audit_report(prof, free, meta)
    assert rep["identical_same_variants"] < rep["same_variants"]
    cc = closure_check(prof, cols, max_depth=1)
    assert not cc["global_identification_established"]


if __name__ == "__main__":
    test_set_invariant_scores_zero_on_syntactic_sames(); test_ideal_recognizer_scores_zero_on_all_sames(); test_accurate_noninvariant_is_not_identified(); print("ok")

