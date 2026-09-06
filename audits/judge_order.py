#!/usr/bin/env python3
"""Audit 1 — option order in an LLM-as-judge (verification form).

Base: an arithmetic question with four candidate answers, one correct.
Query per candidate value v: "Is v the correct answer among the candidates?"
Gold: v is listed AND v is arithmetically correct.

Declared variants of the candidate list:
  same   : permutations (reversal + 4 more) and duplication of one option
  differ : the correct option replaced by a fresh wrong value (gold row changes)
Continuations: none; one extra wrong option appended (depth 1).

  python3 audits/judge_order.py build  --out runs/judge_order.cells.jsonl
  python3 audits/judge_order.py run    --cells ... --model Qwen/Qwen2.5-0.5B-Instruct --out runs/judge_order.qwen05b.jsonl
  python3 audits/judge_order.py report --results ... --out runs/judge_order.qwen05b.report.json
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audit.table import Table                                   # noqa: E402
from audit.equivalences import permutations, duplication, declared_set  # noqa: E402
from audit.readout import boolean_profiles                      # noqa: E402
from audit.stats import audit_report, closure_check             # noqa: E402

N_BASES = 16

CAPITALS = {"France": "Paris", "Germany": "Berlin", "Italy": "Rome", "Spain": "Madrid", "Japan": "Tokyo",
            "Canada": "Ottawa", "Australia": "Canberra", "Brazil": "Brasilia", "Egypt": "Cairo", "Kenya": "Nairobi",
            "Norway": "Oslo", "Sweden": "Stockholm", "Poland": "Warsaw", "Greece": "Athens", "Turkey": "Ankara",
            "Mexico": "Mexico City"}


def make_capital_bases(seed=0):
    """Audit 1b: capital-city verification (readable by small instruction-tuned models)."""
    rng = random.Random(seed)
    caps = list(CAPITALS.values())
    bases, meta = {}, {}
    for i, (country, ans) in enumerate(CAPITALS.items()):
        wrong = rng.sample([x for x in caps if x != ans], 5)
        opts = [ans] + wrong[:3]; rng.shuffle(opts)
        bid = f"c{i:02d}"
        bases[bid] = opts
        meta[bid] = {"question": f"What is the capital of {country}?", "answer": ans, "extra_wrong": wrong[3], "differ_wrong": wrong[4]}
    return bases, meta


def make_bases(seed=0):
    rng = random.Random(seed)
    bases, meta = {}, {}
    while len(bases) < N_BASES:
        a, b = rng.randint(11, 49), rng.randint(11, 49)
        op = rng.choice(["+", "-", "*"])
        if op == "-" and a < b:
            a, b = b, a
        ans = eval(f"{a}{op}{b}")
        wrongs = set()
        while len(wrongs) < 5:
            w = ans + rng.choice([-11, -9, -3, -2, -1, 1, 2, 3, 9, 11, 10, -10])
            if w != ans and w > 0:
                wrongs.add(w)
        wrongs = sorted(wrongs); rng.shuffle(wrongs)
        bid = f"q{len(bases):02d}"
        opts = [ans] + wrongs[:3]; rng.shuffle(opts)
        bases[bid] = opts
        meta[bid] = {"question": f"What is {a} {op} {b}?", "answer": ans, "extra_wrong": wrongs[3], "differ_wrong": wrongs[4]}
    return bases, meta


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["build", "run", "report"])
    ap.add_argument("--cells"); ap.add_argument("--results"); ap.add_argument("--model"); ap.add_argument("--revision", default="main")
    ap.add_argument("--out", required=True); ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--task", choices=["arithmetic", "capitals"], default="arithmetic")
    a = ap.parse_args()

    if a.cmd == "build":
        bases, meta = make_bases() if a.task == "arithmetic" else make_capital_bases()
        cells = []
        for bid, opts in bases.items():
            m = meta[bid]
            def variants(items, m=m):
                vs = permutations(items, max_variants=5) + duplication(items)[:2]
                wrong_only = [m["differ_wrong"] if x == m["answer"] else x for x in items]
                vs += declared_set(items, same=[], differ=[wrong_only])
                return vs
            def render(items, query, m=m):
                body = "\n".join(f"- {x}" for x in items)
                return (f"Question: {m['question']}\nCandidate answers:\n{body}\n"
                        f"Is {query} the correct answer among the candidates? Answer exactly YES or NO.\nAnswer:")
            def gold(items, query, m=m):
                return (query in items) and (query == m["answer"])
            t = Table.from_declarations({bid: opts}, variants, {"none": [], "extra": [m["extra_wrong"]]},
                                        {f"v{i}": v for i, v in enumerate(opts)}, render, gold=gold)
            cells += t.cells
        with open(a.out, "w", encoding="utf-8") as f:
            for c in cells:
                f.write(json.dumps(c, ensure_ascii=False, sort_keys=True) + "\n")
        kinds = {}
        for c in cells:
            kinds[c["kind"]] = kinds.get(c["kind"], 0) + 1
        print(f"wrote {len(cells)} cells; rows by kind (x8 cells): { {k: v // 8 for k, v in kinds.items()} }")

    elif a.cmd == "run":
        import torch
        torch.set_num_threads(a.threads)
        from audit.adapters.hf_local import run_hf
        cells = [json.loads(l) for l in open(a.cells, encoding="utf-8")]
        res = run_hf(cells, a.model, a.revision)
        with open(a.out, "w", encoding="utf-8") as f:
            for r in res:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"wrote {len(res)} results for {a.model}")

    else:
        res = [json.loads(l) for l in open(a.results, encoding="utf-8")]
        prof, free, cols = boolean_profiles(res)
        meta = {r["row_id"]: {"base_id": r["base_id"], "kind": r["kind"]} for r in res}
        rep = audit_report(prof, free, meta)
        rep["closure_depth0"] = closure_check(prof, cols, max_depth=1)
        # accuracy on decision columns and comparative accuracy on defined pairs
        dec = [(r["observation"][0] > r["observation"][1]) == r["gold"] for r in res]
        rep["decision_accuracy"] = sum(dec) / len(dec)
        by = {}
        for r in res:
            by.setdefault((r["row_id"], r["continuation_id"]), {})[r["query_id"]] = (r["observation"][0] - r["observation"][1], r["gold"])
        corr = tot = 0
        for d in by.values():
            qs = sorted(d)
            for i in range(len(qs)):
                for j in range(i + 1, len(qs)):
                    (m1, g1), (m2, g2) = d[qs[i]], d[qs[j]]
                    if g1 != g2:
                        tot += 1; corr += (m1 > m2) == (g1 > g2)
        rep["comparative_accuracy"] = corr / tot if tot else None
        rep["rows"] = len(prof); rep["columns"] = len(cols)
        Path(a.out).write_text(json.dumps(rep, indent=2, default=float) + "\n")
        print(json.dumps({k: rep[k] for k in ("S_median", "V_median", "identical_same_variants", "same_variants",
                                                "decision_accuracy", "comparative_accuracy")}, indent=1),
              "closure:", rep["closure_depth0"]["closed"], rep["closure_depth0"]["identical_on_lower_family"], rep["closure_depth0"]["separated_at_depth"])


if __name__ == "__main__":
    main()
