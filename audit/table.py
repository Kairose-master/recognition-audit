"""Rows x tests -> prompts.

A `Row` is a base input plus a declared variant (`kind` in {base, same,
differ}).  A `Test` is a continuation (extra items appended) plus a query.
The table renders every (row, test) into a prompt through a user renderer
and records gold where the user supplies a reference function.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable


@dataclass
class Row:
    row_id: str
    base_id: str
    kind: str            # base | same | differ
    variant: str
    items: list[Any]


@dataclass
class Test:
    test_id: str
    continuation: list[Any]
    query: Any
    depth: int = 0


@dataclass
class Table:
    rows: list[Row]
    tests: list[Test]
    render: Callable[[list[Any], Any], str]
    gold: Callable[[list[Any], Any], bool] | None = None
    candidates: tuple[str, str] = (" YES", " NO")
    cells: list[dict] = field(default_factory=list)

    @classmethod
    def from_declarations(cls, bases: dict[str, list[Any]], variants: Callable[[list[Any]], list[dict]],
                          continuations: dict[str, list[Any]], queries: dict[str, Any],
                          render, gold=None, candidates=(" YES", " NO")) -> "Table":
        rows = []
        for bid, items in bases.items():
            rows.append(Row(f"{bid}-base", bid, "base", "base", list(items)))
            for v in variants(list(items)):
                rows.append(Row(f"{bid}-{v['variant']}", bid, v["kind"], v["variant"], list(v["items"])))
        tests = [Test(f"{c}-{q}", list(cont), query, depth=len(cont))
                 for c, cont in continuations.items() for q, query in queries.items()]
        t = cls(rows=rows, tests=tests, render=render, gold=gold, candidates=candidates)
        t.materialize()
        return t

    def materialize(self) -> None:
        self.cells = []
        for r in self.rows:
            for t in self.tests:
                items = r.items + t.continuation
                self.cells.append({
                    "row_id": r.row_id, "base_id": r.base_id, "kind": r.kind, "variant": r.variant,
                    "test_id": t.test_id, "continuation_id": t.test_id.rsplit("-", 1)[0],
                    "query_id": t.test_id.rsplit("-", 1)[1], "depth": t.depth,
                    "prompt": self.render(items, t.query),
                    "gold": (bool(self.gold(items, t.query)) if self.gold else None),
                    "candidates": {"pos": self.candidates[0], "neg": self.candidates[1]},
                })

    def write_jsonl(self, path) -> None:
        import json
        with open(path, "w", encoding="utf-8") as f:
            for c in self.cells:
                f.write(json.dumps(c, ensure_ascii=False, sort_keys=True) + "\n")
