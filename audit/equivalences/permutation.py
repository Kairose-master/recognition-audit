from __future__ import annotations

import itertools
from typing import Any


def permutations(items: list[Any], max_variants: int = 5, seed: int = 0) -> list[dict]:
    """Non-identity permutations of a declared set, tagged `same`.

    Deterministic: takes the first `max_variants` non-identity permutations in
    lexicographic order of index tuples, after the full reversal, which is
    always included first.
    """
    n = len(items)
    out = [{"kind": "same", "variant": "rev", "items": list(reversed(items))}]
    for perm in itertools.permutations(range(n)):
        if perm == tuple(range(n)) or perm == tuple(reversed(range(n))):
            continue
        out.append({"kind": "same", "variant": "".join(str(i) for i in perm), "items": [items[i] for i in perm]})
        if len(out) >= max_variants:
            break
    return out


def duplication(items: list[Any]) -> list[dict]:
    """Repeat each item once in place, tagged `same` (idempotence)."""
    return [{"kind": "same", "variant": f"dup{i}", "items": items[: i + 1] + [items[i]] + items[i + 1 :]}
            for i in range(len(items))]


def adjacent_swaps(items: list[Any]) -> list[dict]:
    """Swap each adjacent pair, tagged `same` (minimal surface reorder)."""
    out = []
    for i in range(len(items) - 1):
        v = list(items); v[i], v[i + 1] = v[i + 1], v[i]
        out.append({"kind": "same", "variant": f"swap{i}", "items": v})
    return out
