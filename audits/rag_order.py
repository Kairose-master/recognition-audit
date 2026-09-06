#!/usr/bin/env python3
"""Audit 2 — document order in a RAG answerer.

Base: four retrieved passages, each a synthetic fact "<Entity> was completed
in <year>." about a fictional entity (no parametric knowledge applies).
Queries: one per passage, asking whether its entity was completed in a
stated year; two ask the true year (gold YES), two a false year (gold NO).
Gold: the passage is present and states the asked year.

Declared variants of the passage list:
  same   : permutations (reversal + 4 more) and duplication of one passage
  differ : the passage behind the first YES query replaced by one stating a
           different year (that query's gold becomes NO)
Continuations: none; one extra irrelevant passage appended (depth 1).

Exploratory (not a gate): d_same by the position of the queried passage.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audit.table import Table                                          # noqa: E402
from audit.equivalences import permutations, duplication, declared_set  # noqa: E402
from audit.readout import boolean_profiles                             # noqa: E402
from audit.stats import audit_report, closure_check                    # noqa: E402

N_BASES = 16
NAMES = ["the Velmar dam", "Kestrel Tower", "the Orin bridge", "Halden Station", "the Sorrel canal", "Marrow Hall",
         "the Ibis viaduct", "Cardo Arena", "the Tessa reservoir", "Lorne Observatory", "the Quill tunnel", "Pellam Library",
         "the Nara aqueduct", "Vantor Stadium", "the Ember lighthouse", "Osric Chapel", "the Brill causeway", "Talus Gate",
         "the Wyre pier", "Corvin Market", "the Aster spire", "Dunmore Mill", "the Fenn dock", "Lyra Terminal",
         "the Moss weir", "Rook Hall", "the Sable ferry", "Ilex Court", "the Cinder forge", "Bramble Inn",
         "the Gale windmill", "Thorne Depot", "the Umber mine", "Perry Bathhouse", "the Coil rail", "Nile Row",
         "the Drift harbour", "Sedge Barracks", "the Warden wall", "Juniper Hall", "the Ash kiln", "Vex Tower",
         "the Larch sluice", "Mirren Gate", "the Onyx pit", "Wren Hospice", "the Peat bridge", "Kell Yard",
         "the Rime bridge", "Sorley Hall", "the Vane tower", "Ashby Gate", "the Crane dock", "Ulla Station",
         "the Fell canal", "Harrow Mill", "the Grit quarry", "Nimbus Hall", "the Loam depot", "Cass Tower",
         "the Sere pier", "Tamsin Row", "the Plume gate", "Dover Kiln", "the Hollow mill", "Ivy Court",
         "the Kite bridge", "Muir Hall", "the Rush weir", "Elder Station", "the Brine dock", "Fable Gate",
         "the Slate tunnel", "Orris Hall", "the Moth bridge", "Quay Hall", "the Bend lock", "Roan Tower",
         "the Hazel ford", "Merrow Court"]


def make_bases(seed=0):
    rng = random.Random(seed)
    names = NAMES[:]; rng.shuffle(names)
    bases, meta = {}, {}
    for i in range(N_BASES):
        ents = names[5 * i: 5 * i + 5]           # 4 passages + 1 extra
        years = rng.sample(range(1900, 2020), 5)
        passages = [f"{e[0].upper() + e[1:]} was completed in {y}." for e, y in zip(ents[:4], years[:4])]
        extra = f"{ents[4][0].upper() + ents[4][1:]} was completed in {years[4]}."
        asked = []
        for k, (e, y) in enumerate(zip(ents[:4], years[:4])):
            if k in (0, 2):
                asked.append((e, y, True))
            else:
                fy = y + rng.choice([-7, -4, 4, 7])
                asked.append((e, fy, False))
        bid = f"r{i:02d}"
        bases[bid] = passages
        differ_year = years[0] + rng.choice([9, 12, -9, -12])
        meta[bid] = {"entities": ents[:4], "years": years[:4], "asked": asked, "extra": extra,
                     "differ_passage": f"{ents[0][0].upper() + ents[0][1:]} was completed in {differ_year}."}
    return bases, meta


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["build", "run", "report"])
    ap.add_argument("--cells"); ap.add_argument("--results"); ap.add_argument("--model"); ap.add_argument("--revision", default="main")
    ap.add_argument("--out", required=True); ap.add_argument("--threads", type=int, default=4)
    a = ap.parse_args()

    if a.cmd == "build":
        bases, meta = make_bases()
        cells = []
        for bid, passages in bases.items():
            m = meta[bid]
            def variants(items, m=m):
                vs = permutations(items, max_variants=5) + duplication(items)[:2]
                swapped = [m["differ_passage"] if x.startswith(m["entities"][0][0].upper() + m["entities"][0][1:]) else x for x in items]
                vs += declared_set(items, same=[], differ=[swapped])
                return vs
            def render(items, query, m=m):
                body = "\n".join(f"- {x}" for x in items)
                e, y, _ = query
                return (f"Passages:\n{body}\nQuestion: Was {e} completed in {y}? Use only the passages. "
                        f"Answer exactly YES or NO.\nAnswer:")
            def gold(items, query, m=m):
                e, y, _ = query
                head = e[0].upper() + e[1:]
                return any(x.startswith(head + " was completed in ") and x.endswith(f"in {y}.") for x in items)
            queries = {f"q{k}": q for k, q in enumerate(m["asked"])}
            t = Table.from_declarations({bid: passages}, variants, {"none": [], "extra": [m["extra"]]}, queries, render, gold=gold)
            for c in t.cells:
                row = next(r for r in t.rows if r.row_id == c["row_id"])
                qe = queries[c["query_id"]][0]
                head = qe[0].upper() + qe[1:]
                pos = next((i for i, x in enumerate(row.items) if x.startswith(head + " was")), None)
                c["_queried_position"] = pos; c["_n_items"] = len(row.items)
            cells += t.cells
        with open(a.out, "w", encoding="utf-8") as f:
            for c in cells:
                f.write(json.dumps(c, ensure_ascii=False, sort_keys=True) + "\n")
        kinds = {}
        for c in cells:
            kinds[c["kind"]] = kinds.get(c["kind"], 0) + 1
        golds = sum(c["gold"] for c in cells)
        print(f"wrote {len(cells)} cells; rows by kind: { {k: v // 8 for k, v in kinds.items()} }; gold YES {golds}/{len(cells)}")

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
        # exploratory: decision accuracy by position of the queried passage (depth-0 cells)
        pos = {}
        for r in res:
            if r["continuation_id"] != "none" or r.get("_queried_position") is None:
                continue
            key = "first" if r["_queried_position"] == 0 else ("last" if r["_queried_position"] == r["_n_items"] - 1 else "middle")
            pos.setdefault(key, []).append((r["observation"][0] > r["observation"][1]) == r["gold"])
        rep["exploratory_decision_accuracy_by_queried_position"] = {k: sum(v) / len(v) for k, v in pos.items()}
        rep["rows"] = len(prof); rep["columns"] = len(cols)
        Path(a.out).write_text(json.dumps(rep, indent=2, default=float) + "\n")
        print(json.dumps({k: rep[k] for k in ("S_median", "V_median", "identical_same_variants", "same_variants",
                                                "nonconstant_columns", "decision_accuracy", "comparative_accuracy",
                                                "exploratory_decision_accuracy_by_queried_position")}, indent=1),
              "closure:", rep["closure_depth0"]["closed"], rep["closure_depth0"]["identical_on_lower_family"], rep["closure_depth0"]["separated_at_depth"])


if __name__ == "__main__":
    main()
