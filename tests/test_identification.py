import itertools
import unittest
import numpy as np

from audit.stats import closure_check
from audit.adapters.horn import closure, semantic_key, observe


class RefinementTests(unittest.TestCase):
    columns = [("D", "empty", "q", 0), ("D", "a", "q", 1)]

    def check(self, a, b):
        return closure_check({"u": np.array(a), "v": np.array(b)}, self.columns, 1)

    def test_witness(self):
        r = self.check([False, False], [False, True])
        self.assertEqual(r["status"], "separation_found")
        self.assertEqual(r["witness"]["column"], self.columns[1])

    def test_no_witness_is_not_global(self):
        r = self.check([False, False], [False, False])
        self.assertEqual(r["status"], "no_separation_observed")
        self.assertFalse(r["global_identification_established"])
        self.assertNotIn("closed", r)

    def test_vacuity(self):
        self.assertEqual(self.check([False, False], [True, True])["status"],
                         "no_comparable_pairs")

    def test_incomplete_depths_rejected(self):
        with self.assertRaises(ValueError):
            closure_check({"u": np.array([True])}, self.columns[:1], 1)

    def test_delayed_separator(self):
        # A depth-1 audit misses a distinction that appears at depth 2.
        self.assertTrue(self.check([False, False], [False, False])["sampled_stable"])
        cols = self.columns + [("D", "aa", "q", 2)]
        r = closure_check({"u": np.array([False, False, False]),
                           "v": np.array([False, False, True])}, cols, 2)
        self.assertEqual(r["status"], "separation_found")


class HornTests(unittest.TestCase):
    atoms = ("a", "b", "c")

    def test_semantic_rewrites_and_contexts(self):
        base = [(('a',), ('b',)), (('b',), ('c',))]
        variants = [base[::-1], base * 2, base + [(('a',), ('c',))]]
        for context in [[], [((), ('a',))], [(('c',), ('a',))]]:
            key = semantic_key(base + context, self.atoms)
            for v in variants:
                self.assertEqual(key, semantic_key(v + context, self.atoms))
        self.assertNotEqual(semantic_key(base, self.atoms),
                            semantic_key([(('b',), ('a',)), base[1]], self.atoms))

    def test_singletons_miss_conjunction(self):
        gate = [(('a', 'b'), ('c',))]
        for atom in self.atoms:
            self.assertEqual(closure(gate, [atom], self.atoms),
                             closure([], [atom], self.atoms))
        self.assertNotEqual(semantic_key(gate, self.atoms), semantic_key([], self.atoms))

    def test_forward_chaining_against_truth_tables(self):
        # Independent propositional-model oracle for every subset of four rules.
        rules = [((), ('a',)), (('a',), ('b',)),
                 (('a', 'b'), ('c',)), (('c',), ('a', 'b'))]
        worlds = [set(a for a, bit in zip(self.atoms, bits) if bit)
                  for bits in itertools.product([False, True], repeat=3)]
        for bits in itertools.product([False, True], repeat=len(rules)):
            theory = [r for r, bit in zip(rules, bits) if bit]
            models = [w for w in worlds if all(not set(b) <= w or set(h) <= w
                                               for b, h in theory)]
            for assumptions in worlds:
                for target in self.atoms:
                    expected = all(target in w for w in models if assumptions <= w)
                    self.assertEqual(observe(theory, assumptions, [target], self.atoms)[0] > 0,
                                     expected)


if __name__ == '__main__':
    unittest.main()
