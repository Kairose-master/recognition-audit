"""Logit pairs -> Boolean profiles, read through order relations only."""

from __future__ import annotations

import itertools
from collections import defaultdict

import numpy as np


def boolean_profiles(results: list[dict]):
    """`results`: cells with `row_id`, `continuation_id`, `query_id`, `gold`,
    `observation` = [pos_logit, neg_logit].

    Returns (profiles, free_mask, columns): for each row a Boolean vector of
    decisions [pos > neg] per (continuation, query) and preferences
    [margin(q1) > margin(q2)] per (continuation, query pair); `free_mask`
    marks preference columns whose gold ties for that row; `columns` names
    them with their depth."""
    obs, gold, depth = defaultdict(dict), defaultdict(dict), {}
    for r in results:
        obs[r["row_id"]][(r["continuation_id"], r["query_id"])] = r["observation"][0] - r["observation"][1]
        gold[r["row_id"]][(r["continuation_id"], r["query_id"])] = r.get("gold")
        depth[r["continuation_id"]] = r.get("depth", 0)
    conts = sorted(depth)
    queries = sorted({k[1] for d in obs.values() for k in d})
    qpairs = list(itertools.combinations(queries, 2))
    columns = []
    for c in conts:
        columns += [("D", c, q, depth[c]) for q in queries]
        columns += [("P", c, a, b, depth[c]) for a, b in qpairs]
    profiles, free = {}, {}
    for row, m in obs.items():
        v, f = [], []
        for c in conts:
            for q in queries:
                v.append(m[(c, q)] > 0); f.append(False)
            for a, b in qpairs:
                v.append(m[(c, a)] > m[(c, b)])
                ga, gb = gold[row].get((c, a)), gold[row].get((c, b))
                f.append(ga is not None and ga == gb)
        profiles[row] = np.array(v); free[row] = np.array(f)
    return profiles, free, columns
