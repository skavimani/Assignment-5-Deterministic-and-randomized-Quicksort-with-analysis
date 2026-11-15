"""
quicksort.py
============

Deterministic and randomized Quicksort for MSCS-532 Assignment 5.

Both versions share the same partition routine (Lomuto partition, Hoare 1962
describes the original scheme), so the ONLY difference between them is how
the pivot is chosen:

* deterministic_quicksort  -> always uses the LAST element of the subarray.
* randomized_quicksort     -> swaps a uniformly random element of the
                              subarray into the last position first, then
                              partitions exactly like the deterministic one.

Keeping everything else identical means any difference we measure in the
experiments comes from the pivot rule alone.

Design choices
--------------
1. In-place sorting. The list is rearranged inside itself, so no extra
   copies of the data are made (O(1) extra memory apart from the call stack).
2. Recurse on the smaller side, loop on the larger side. After partitioning,
   we make a recursive call only for the smaller of the two pieces and
   handle the larger piece with the while-loop. This keeps the recursion
   depth at O(log n) even in the worst case (Sedgewick, 1978), so Python's
   recursion limit is never hit on sorted input -- the running time can
   still be quadratic, but the program does not crash.
3. Comparison counting. Every function accepts an optional Counter object.
   Counting comparisons gives a machine-independent measure of work that we
   can compare directly with the theory (~n^2/2 worst case, ~1.39 n log2 n
   average case).

Usage
-----
    >>> from quicksort import deterministic_quicksort, randomized_quicksort
    >>> data = [5, 2, 9, 1, 5, 6]
    >>> deterministic_quicksort(data)   # sorts in place, also returns the list
    [1, 2, 5, 5, 6, 9]
"""

import random


class Counter:
    """Simple mutable counter used to tally key comparisons."""

    def __init__(self):
        self.comparisons = 0


def partition(arr, low, high, counter=None):
    """Lomuto partition of arr[low..high] around the pivot arr[high].

    After the call, for the returned index p:
        arr[low .. p-1]  <= pivot
        arr[p]           == pivot   (the pivot is in its final sorted place)
        arr[p+1 .. high] >  pivot

    Runs in Theta(high - low) time: exactly (high - low) comparisons.
    """
    pivot = arr[high]
    i = low - 1                      # end of the "<= pivot" region
    for j in range(low, high):       # scan every element except the pivot
        if counter is not None:
            counter.comparisons += 1
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]   # put pivot in place
    return i + 1


def _quicksort(arr, low, high, choose_pivot, counter):
    """Shared driver: sort arr[low..high] in place.

    choose_pivot(arr, low, high) must move the chosen pivot to arr[high].
    """
    while low < high:
        choose_pivot(arr, low, high)
        p = partition(arr, low, high, counter)
        # Recurse into the smaller part; loop on the larger part.
        if p - low < high - p:
            _quicksort(arr, low, p - 1, choose_pivot, counter)
            low = p + 1
        else:
            _quicksort(arr, p + 1, high, choose_pivot, counter)
            high = p - 1


# ---------------------------------------------------------------------------
# Pivot rules
# ---------------------------------------------------------------------------

def _last_element_pivot(arr, low, high):
    """Deterministic rule: the pivot is already arr[high]; nothing to do."""
    return None


def _make_random_pivot(rng):
    """Return a pivot rule that swaps a random element into arr[high]."""
    def _random_pivot(arr, low, high):
        r = rng.randint(low, high)          # uniform over the subarray
        arr[r], arr[high] = arr[high], arr[r]
    return _random_pivot


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def deterministic_quicksort(arr, counter=None):
    """Sort arr in place using the last element as the pivot.

    Best/average case: O(n log n).  Worst case: O(n^2), which happens on
    already-sorted or reverse-sorted input because the pivot is then always
    the largest or smallest element.

    Returns arr for convenience.
    """
    _quicksort(arr, 0, len(arr) - 1, _last_element_pivot, counter)
    return arr


def randomized_quicksort(arr, counter=None, seed=None):
    """Sort arr in place choosing each pivot uniformly at random.

    Expected running time is O(n log n) for EVERY input, because the
    pivot no longer depends on the order of the input (Hoare, 1962, already
    recommended choosing the pivot at random). The worst case is still O(n^2), but it now requires an extremely
    unlucky sequence of random choices rather than a particular input.

    seed: optional integer so that experiments can be repeated exactly.
    Returns arr for convenience.
    """
    rng = random.Random(seed)
    _quicksort(arr, 0, len(arr) - 1, _make_random_pivot(rng), counter)
    return arr


if __name__ == "__main__":
    sample = [38, 27, 43, 3, 9, 82, 10, 3]
    print("Input:          ", sample)
    print("Deterministic:  ", deterministic_quicksort(sample.copy()))
    print("Randomized:     ", randomized_quicksort(sample.copy(), seed=1))
