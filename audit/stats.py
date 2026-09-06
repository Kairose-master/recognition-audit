"""Statistics on Boolean profiles: Hamming, S, V, exact identities, closure."""

from __future__ import annotations

import itertools
from collections import defaultdict

import numpy as np


def hamming(a, b) -> int:
    return int(np.count_nonzero(a != b))


def hamming_free(prof, free, u, v) -> int:
    m = free[u] & free[v]
    return int(np.count_nonzero(prof[u][m] != prof[v][m]))


def audit_report(profiles, free, rows_meta) -> dict:
    """`rows_meta`: row_id -> {base_id, kind}.

    Per base: d_same = median Hamming(base, same-variants), d_differ =
    median Hamming(base, differ-variants); S = median over bases of
    d_same / d_differ (one-sided: only S > 1 is diagnostic); V the same on
    free columns; E = number of same-variants with identical profiles."""
    by_base = defaultdict(lambda: {"base": None, "same": [], "differ": []})
    for rid, m in rows_meta.items():
        if m["kind"] == "base":
            by_base[m["base_id"]]["base"] = rid
        else:
            by_base[m["base_id"]][m["kind"]].append(rid)
    per, S, V = {}, [], []
    ident = total = 0
    for b, g in by_base.items():
        base = g["base"]
        ds = [hamming(profiles[base], profiles[r]) for r in g["same"]]
        dd = [hamming(profiles[base], profiles[r]) for r in g["differ"]]
        fs = [hamming_free(profiles, free, base, r) for r in g["same"]]
        fd = [hamming_free(profiles, free, base, r) for r in g["differ"]]
        ident += sum(d == 0 for d in ds); total += len(ds)
        s = (np.median(ds) / np.median(dd)) if dd and np.median(dd) > 0 else None
        v = (np.median(fs) / np.median(fd)) if fd and np.median(fd) > 0 else None
        per[b] = {"d_same": float(np.median(ds)) if ds else None, "d_differ": float(np.median(dd)) if dd else None,
                  "S": s, "V": v, "n_same": len(ds), "n_differ": len(dd)}
        if s is not None: S.append(s)
        if v is not None: V.append(v)
    allrows = list(profiles)
    mat = np.array([profiles[r] for r in allrows])
    nonconst = int((mat.any(axis=0) & ~mat.all(axis=0)).sum()) if len(allrows) else 0
    return {"S_median": float(np.median(S)) if S else None, "S_note": "one-sided: only S > 1 is diagnostic",
            "nonconstant_columns": nonconst, "columns": int(mat.shape[1]) if len(allrows) else 0,
            "V_median": float(np.median(V)) if V else None, "identical_same_variants": ident, "same_variants": total,
            "per_base": per}


def closure_check(profiles, columns, max_depth: int) -> dict:
    """Check sampled depth refinement, not global contextual closure.

    A witness separates sampled rows at the next depth. Absence of a
    witness does not establish Lean's universally quantified Closed.
    """
    if isinstance(max_depth, bool) or not isinstance(max_depth, int) or max_depth < 1:
        raise ValueError("max_depth must be a positive integer")
    d = np.array([c[-1] for c in columns])
    if any(isinstance(c[-1], bool) or not isinstance(c[-1], int) or c[-1] < 0 for c in columns):
        raise ValueError("column depths must be nonnegative integers")
    low, high = d <= max_depth - 1, d == max_depth
    if not low.any() or not high.any():
        raise ValueError("both lower-depth and next-depth columns are required")
    profiles = {r: np.asarray(p) for r, p in profiles.items()}
    if any(p.shape != (len(columns),) or p.dtype != np.dtype(bool) for p in profiles.values()):
        raise ValueError("each profile must be a Boolean vector matching columns")
    rows = sorted(profiles)
    ident = viol = 0; witness = None
    for u, v in itertools.combinations(rows, 2):
        if hamming(profiles[u][low], profiles[v][low]) == 0:
            ident += 1
            h = hamming(profiles[u][high], profiles[v][high])
            if h:
                viol += 1
                if witness is None or h > witness["separating_columns"]:
                    k = int(np.argmax(profiles[u][high] != profiles[v][high]))
                    witness = {"rows": [u, v], "separating_columns": h,
                               "column": columns[np.where(high)[0][k]]}
    status = ("separation_found" if viol else
              "no_comparable_pairs" if ident == 0 else "no_separation_observed")
    return {"schema_version": 2, "scope": "sampled_rows_and_columns",
            "status": status, "global_identification_established": False,
            "identical_on_lower_family": ident, "separated_at_depth": viol,
            "sampled_stable": viol == 0, "vacuous": ident == 0,
            "rows_checked": len(rows), "lower_columns": int(low.sum()),
            "next_columns": int(high.sum()), "witness": witness}

