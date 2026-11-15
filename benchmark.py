"""
benchmark.py -- empirical comparison of deterministic vs randomized Quicksort.

For every input distribution and input size it measures
  * wall-clock running time (median of several runs, time.perf_counter)
  * number of key comparisons (machine-independent)
and writes the results to results/results.csv. Then run plot_results.py
to draw the charts.

Run:   python benchmark.py            (full experiment, a few minutes)
       python benchmark.py --quick    (small sizes, a few seconds)
"""

import argparse
import csv
import os
import random
import statistics
import sys
import time

from quicksort import Counter, deterministic_quicksort, randomized_quicksort

SIZES_FULL = [1000, 2000, 4000, 8000, 16000]
SIZES_QUICK = [250, 500, 1000, 2000]
REPEATS = 3


def make_input(dist, n, rng):
    """Build an input list of length n for the given distribution."""
    if dist == "random":
        return [rng.randint(0, 10 * n) for _ in range(n)]
    if dist == "sorted":
        return list(range(n))
    if dist == "reverse":
        return list(range(n, 0, -1))
    if dist == "few_unique":           # many duplicates: only 10 distinct keys
        return [rng.randint(0, 9) for _ in range(n)]
    raise ValueError(dist)


DISTRIBUTIONS = ["random", "sorted", "reverse", "few_unique"]


def run_one(algorithm, data, seed):
    """Sort a copy of data; return (seconds, comparisons)."""
    if algorithm == "deterministic":
        timed = list(data)
        start = time.perf_counter()
        deterministic_quicksort(timed)
        elapsed = time.perf_counter() - start
        c = Counter()
        deterministic_quicksort(list(data), counter=c)
    else:
        timed = list(data)
        start = time.perf_counter()
        randomized_quicksort(timed, seed=seed)
        elapsed = time.perf_counter() - start
        c = Counter()
        randomized_quicksort(list(data), counter=c, seed=seed)
    assert timed == sorted(data), "sort produced wrong output"
    return elapsed, c.comparisons


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true",
                        help="use small sizes for a fast smoke test")
    args = parser.parse_args()
    sizes = SIZES_QUICK if args.quick else SIZES_FULL

    os.makedirs("results", exist_ok=True)
    out_path = os.path.join("results", "results.csv")
    rng = random.Random(2026)
    rows = []

    print(f"Python {sys.version.split()[0]}  |  sizes={sizes}  "
          f"repeats={REPEATS}\n")
    print(f"{'distribution':<12}{'n':>7}  {'algorithm':<14}"
          f"{'median s':>10}{'comparisons':>14}")
    for dist in DISTRIBUTIONS:
        for n in sizes:
            for algorithm in ("deterministic", "randomized"):
                times, comps = [], []
                for rep in range(REPEATS):
                    data = make_input(dist, n, rng)   # fresh input each run
                    t, c = run_one(algorithm, data, seed=rep)
                    times.append(t)
                    comps.append(c)
                row = {
                    "distribution": dist,
                    "n": n,
                    "algorithm": algorithm,
                    "median_seconds": statistics.median(times),
                    "median_comparisons": int(statistics.median(comps)),
                }
                rows.append(row)
                print(f"{dist:<12}{n:>7}  {algorithm:<14}"
                      f"{row['median_seconds']:>10.4f}"
                      f"{row['median_comparisons']:>14,}")

    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved {out_path}")


if __name__ == "__main__":
    main()
