"""Synthetic recognizers for controls and tests."""

from __future__ import annotations

import hashlib
import random


def invariant_recognizer(cells: list[dict], key=lambda c: (tuple(sorted(map(str, c["_items"]))), c["query_id"])) -> list[dict]:
    """Depends only on the declared-equivalence key (default: the item multiset
    as a set plus the query): must score exactly 0 on `same` variants."""
    out = []
    for c in cells:
        h = int(hashlib.sha256(repr(key(c)).encode()).hexdigest(), 16)
        out.append({**{k: c[k] for k in c if k != "prompt"}, "observation": [10 + (h % 1000) / 100, 10.0]})
    return out


def gold_plus_noise(cells: list[dict], sd: float = 0.3, seed: int = 0) -> list[dict]:
    """Accurate, non-invariant: gold-driven margin plus symmetric noise.
    Calibrates S (reaches ~0.5 by accuracy alone) and V (~1)."""
    rng = random.Random(seed)
    out = []
    for c in cells:
        m = (1 if c["gold"] else -1) * 0.5 + rng.gauss(0, sd)
        out.append({**{k: c[k] for k in c if k != "prompt"}, "observation": [10 + m, 10.0]})
    return out
