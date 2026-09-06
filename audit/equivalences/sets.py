from __future__ import annotations

from typing import Any


def declared_set(base: list[Any], same: list[list[Any]], differ: list[list[Any]]) -> list[dict]:
    """Arbitrary declared variants.

    `same`   : item lists the user declares equivalent to `base`
               (paraphrases, reorderings, redundant additions);
    `differ` : item lists that change exactly one declared-relevant thing
               (the reference scale for `S`).
    """
    out = [{"kind": "same", "variant": f"same{i}", "items": v} for i, v in enumerate(same)]
    out += [{"kind": "differ", "variant": f"differ{i}", "items": v} for i, v in enumerate(differ)]
    return out
