"""
test_quicksort.py -- unit tests for both Quicksort versions.

Run with:   python -m unittest -v
"""

import random
import unittest

from quicksort import Counter, deterministic_quicksort, randomized_quicksort

SORTS = {
    "deterministic": deterministic_quicksort,
    "randomized": randomized_quicksort,
}


class TestQuicksort(unittest.TestCase):

    def check(self, data):
        """Every sort must match Python's built-in sorted()."""
        for name, sort in SORTS.items():
            with self.subTest(sort=name, data=data[:10]):
                self.assertEqual(sort(list(data)), sorted(data))

    def test_empty_and_single(self):
        self.check([])
        self.check([7])

    def test_small_examples(self):
        self.check([2, 1])
        self.check([3, 1, 2])
        self.check([5, 2, 9, 1, 5, 6])

    def test_duplicates_and_negatives(self):
        self.check([4, -1, 4, 0, -1, 4, 4, 2])
        self.check([1] * 50)

    def test_sorted_and_reverse_sorted(self):
        # Large enough that plain recursion would exceed Python's
        # default recursion limit (1000) in the worst case.
        self.check(list(range(3000)))
        self.check(list(range(3000, 0, -1)))

    def test_random_lists(self):
        rng = random.Random(42)
        for n in (10, 100, 1000):
            self.check([rng.randint(-1000, 1000) for _ in range(n)])

    def test_floats_and_strings(self):
        self.check([3.5, -2.25, 0.0, 9.75, 1.5])
        self.check(["pear", "apple", "fig", "banana"])

    def test_sorts_in_place(self):
        for sort in SORTS.values():
            data = [3, 1, 2]
            sort(data)
            self.assertEqual(data, [1, 2, 3])

    def test_worst_case_comparison_count(self):
        # Deterministic Quicksort on sorted input makes exactly n(n-1)/2
        # comparisons -- the textbook worst case.
        n = 500
        c = Counter()
        deterministic_quicksort(list(range(n)), counter=c)
        self.assertEqual(c.comparisons, n * (n - 1) // 2)

    def test_randomized_avoids_worst_case_on_sorted_input(self):
        n = 2000
        c = Counter()
        randomized_quicksort(list(range(n)), counter=c, seed=0)
        self.assertLess(c.comparisons, n * (n - 1) // 2 // 10)

    def test_seed_reproducible(self):
        data = list(range(200, 0, -1))
        c1, c2 = Counter(), Counter()
        randomized_quicksort(list(data), counter=c1, seed=7)
        randomized_quicksort(list(data), counter=c2, seed=7)
        self.assertEqual(c1.comparisons, c2.comparisons)


if __name__ == "__main__":
    unittest.main()
