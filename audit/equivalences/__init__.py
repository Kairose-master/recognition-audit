"""Declared equivalence classes.

An equivalence is a function from a base item to a list of variants that the
user declares interchangeable, each tagged with a `kind`.  Two kinds are
distinguished by the audit:

- `same`   : declared equivalent to the base (the audit expects invariance);
- `differ` : a minimal declared-relevant change (the reference scale).

The audit never infers equivalence; it measures what the declaration says.
"""
from .permutation import permutations, duplication, adjacent_swaps
from .sets import declared_set

__all__ = ["permutations", "duplication", "adjacent_swaps", "declared_set"]
