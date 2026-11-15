"""
plot_results.py -- draw charts from results/results.csv.

Creates:
  results/runtime_by_distribution.png   (running time, one panel per input type)
  results/comparisons_vs_theory.png     (comparison counts vs theoretical curves)

Run after benchmark.py:   python plot_results.py
"""

import csv
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE, ORANGE = "#2a78d6", "#eb6834"        # series colours (fixed order)
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
TITLES = {
    "random": "Random input",
    "sorted": "Already sorted",
    "reverse": "Reverse sorted",
    "few_unique": "Many duplicates (10 distinct keys)",
}

plt.rcParams.update({
    "font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False,
})


def load():
    data = {}
    with open(os.path.join("results", "results.csv")) as f:
        for r in csv.DictReader(f):
            key = (r["distribution"], r["algorithm"])
            data.setdefault(key, []).append(
                (int(r["n"]), float(r["median_seconds"]),
                 int(r["median_comparisons"])))
    return data


def set_n_axis(ax, ns):
    """Log-2 x axis labelled with the actual input sizes."""
    ax.set_xscale("log", base=2)
    ax.set_xticks(ns)
    ax.set_xticklabels([f"{n:,}" for n in ns])
    ax.minorticks_off()


def style(ax):
    ax.grid(True, which="major", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def runtime_chart(data):
    fig, axes = plt.subplots(2, 2, figsize=(9, 6.6), sharex=True, sharey=True)
    for ax, dist in zip(axes.flat, TITLES):
        for alg, color, marker in (("deterministic", BLUE, "o"),
                                   ("randomized", ORANGE, "s")):
            pts = data[(dist, alg)]
            ax.plot([p[0] for p in pts], [p[1] for p in pts], color=color,
                    linewidth=2, marker=marker, markersize=6,
                    label=alg.capitalize())
        set_n_axis(ax, [p[0] for p in pts])
        ax.set_yscale("log")
        ax.set_title(TITLES[dist], fontsize=10, color=INK, loc="left")
        style(ax)
    for ax in axes[1]:
        ax.set_xlabel("Input size n (log scale)")
    for ax in axes[:, 0]:
        ax.set_ylabel("Median time, seconds (log scale)")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False,
               bbox_to_anchor=(0.5, 0.995))
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(os.path.join("results", "runtime_by_distribution.png"), dpi=200)
    plt.close(fig)


def comparisons_chart(data):
    fig, ax = plt.subplots(figsize=(8, 5))
    ns = [p[0] for p in data[("sorted", "deterministic")]]
    worst = [n * (n - 1) / 2 for n in ns]
    # Exact expected comparisons for random pivots: 2(n+1)H_n - 4n
    avg = [2 * (n + 1) * sum(1 / k for k in range(1, n + 1)) - 4 * n
           for n in ns]
    ax.plot(ns, worst, color=MUTED, linestyle="--", linewidth=1.5)
    ax.plot(ns, avg, color=MUTED, linestyle=":", linewidth=1.5)
    ax.text(ns[-1] * 1.18, worst[-1], "n(n−1)/2", color=MUTED, va="center")
    ax.text(ns[-1] * 1.18, avg[-1], "2(n+1)Hₙ − 4n", color=MUTED, va="center")

    series = [
        ("sorted", "deterministic", BLUE, "o", "Deterministic, sorted"),
        ("reverse", "deterministic", BLUE, "^", "Deterministic, reverse"),
        ("random", "deterministic", BLUE, "D", "Deterministic, random"),
        ("sorted", "randomized", ORANGE, "o", "Randomized, sorted"),
        ("reverse", "randomized", ORANGE, "^", "Randomized, reverse"),
        ("random", "randomized", ORANGE, "D", "Randomized, random"),
    ]
    for dist, alg, color, marker, label in series:
        pts = data[(dist, alg)]
        if alg == "deterministic":   # hollow, larger: stays visible if overlapped
            kw = dict(markersize=12, markerfacecolor="none",
                      markeredgecolor=color, markeredgewidth=2)
        else:
            kw = dict(markersize=7, markeredgecolor="white", markeredgewidth=1)
        ax.plot([p[0] for p in pts], [p[2] for p in pts], color=color,
                marker=marker, linewidth=0, label=label, **kw)
    set_n_axis(ax, ns)
    ax.set_yscale("log")
    ax.set_xlim(ns[0] * 0.8, ns[-1] * 2.6)
    ax.set_xlabel("Input size n (log scale)")
    ax.set_ylabel("Key comparisons (log scale)")
    style(ax)
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join("results", "comparisons_vs_theory.png"), dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    d = load()
    runtime_chart(d)
    comparisons_chart(d)
    print("Saved charts to results/")
