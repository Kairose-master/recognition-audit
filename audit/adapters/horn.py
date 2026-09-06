"""Exact definite-Horn oracle; clauses are (body_atoms, head_atoms).

Empty bodies are facts; multiple heads are conjunctions. Negation and
constraints are not supported. Atom names are strings in a fixed universe.
"""
from itertools import combinations


def _validated(clauses, atoms):
    atoms = tuple(sorted(atoms))
    if len(atoms) != len(set(atoms)) or any(not isinstance(a, str) for a in atoms):
        raise ValueError("atoms must be distinct strings")
    universe = frozenset(atoms)
    clauses = tuple((frozenset(b), frozenset(h)) for b, h in clauses)
    if any(not (b | h) <= universe for b, h in clauses):
        raise ValueError("clause contains an undeclared atom")
    return clauses, atoms


def closure(clauses, assumptions, atoms):
    clauses, atoms = _validated(clauses, atoms)
    known = set(assumptions)
    if not known <= set(atoms):
        raise ValueError("assumption contains an undeclared atom")
    while True:
        expanded = known | {a for b, h in clauses if b <= known for a in h}
        if expanded == known:
            return frozenset(known)
        known = expanded


def semantic_key(clauses, atoms):
    """Complete closure function on all assumption subsets, not just singletons.

    Exponential in atom count: intended for small-world validation only.
    """
    clauses, atoms = _validated(clauses, atoms)
    return (atoms, tuple(tuple(sorted(closure(clauses, subset, atoms)))
                        for n in range(len(atoms) + 1)
                        for subset in combinations(atoms, n)))


def observe(clauses, assumptions, targets, atoms):
    """Return exact YES/NO logits from entailment, with no fitted parameters."""
    atoms = tuple(atoms)
    targets = frozenset(targets)
    if not targets <= set(atoms):
        raise ValueError("target contains an undeclared atom")
    yes = targets <= closure(clauses, assumptions, atoms)
    return [1.0, 0.0] if yes else [0.0, 1.0]
