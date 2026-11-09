"""(a) Age distribution: histogram in fixed-width bins stacked by sex, rug
ticks below the axis colored by sex, and a dashed line at the mean.

    python plot_age.py --csv participants.csv --out age_distribution.pdf
"""
import math

import matplotlib.pyplot as plt
import numpy as np

from common import (GRID_GRAY, SEX_COLOR, SEX_ORDER, TEXT_GRAY, apply_style,
                    cli, load_participants, save)

BIN_WIDTH = 5


def draw(ax, people, bin_width=BIN_WIDTH, title="(a) Age distribution"):
    # Participants who did not disclose their age (age is None) are left out
    # of the histogram, mean and rug, and counted in a note instead.
    undisclosed = sum(p["age"] is None for p in people)
    people = [p for p in people if p["age"] is not None]
    if not people:
        raise ValueError("No participants with a disclosed age")
    ages = np.array([p["age"] for p in people])
    lo = math.floor(ages.min() / bin_width) * bin_width
    hi = math.floor(ages.max() / bin_width) * bin_width + bin_width
    edges = np.arange(lo, hi + bin_width / 2, bin_width)
    counts, _ = np.histogram(ages, bins=edges)
    ymax = counts.max()

    # Stacked bars: one segment per sex, in SEX_ORDER from the bottom up.
    present = [s for s in SEX_ORDER if any(p["sex"] == s for p in people)]
    bottom = np.zeros(len(counts))
    for sex in present:
        sub, _ = np.histogram([p["age"] for p in people if p["sex"] == sex],
                              bins=edges)
        ax.bar(edges[:-1], sub, width=bin_width, bottom=bottom, align="edge",
               color=SEX_COLOR[sex], edgecolor="white", linewidth=1.5,
               zorder=3, label=sex)
        # Segment count inside the segment (only when the bar is split).
        for x0, b, c, tot in zip(edges[:-1], bottom, sub, counts):
            if c and c != tot:
                ax.text(x0 + bin_width / 2, b + c / 2, f"{c}", ha="center",
                        va="center", fontsize=9, color="white", zorder=4)
        bottom += sub

    # Mean line, drawn behind the bars so it only shows in the empty space.
    # Its label sits in the headroom above the tallest bar, centered on the
    # line, so it can never be covered by a bar.
    mean = ages.mean()
    ax.plot([mean, mean], [0, ymax * 1.04], ls="--", lw=1.1,
            color=TEXT_GRAY, zorder=2)
    ax.text(mean, ymax * 1.06, f"mean {mean:.1f}",
            ha="center", va="bottom", fontsize=9.5, color=TEXT_GRAY, zorder=4)

    # Rug: one tick per participant just below the x axis, colored by sex.
    for p in people:
        ax.plot([p["age"], p["age"]], [-0.03 * ymax, -0.10 * ymax],
                color=SEX_COLOR[p["sex"]], lw=1.8, solid_capstyle="butt",
                clip_on=False, zorder=4)

    if undisclosed:
        ax.text(0.99, 0.99, f"{undisclosed} not disclosed",
                transform=ax.transAxes, ha="right", va="top", fontsize=8.5,
                color=TEXT_GRAY, style="italic", zorder=4)

    ax.set_xlim(lo - bin_width * 0.3, hi + bin_width * 0.3)
    ax.set_ylim(0, ymax * 1.2)
    ax.set_xticks(edges)
    ax.set_yticks(range(0, ymax + 1))
    ax.tick_params(axis="x", pad=9)
    ax.yaxis.grid(True, color=GRID_GRAY, lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Participants")
    ax.set_title(title)


if __name__ == "__main__":
    args = cli(__doc__, "age_distribution.pdf")
    apply_style()
    fig, ax = plt.subplots(figsize=(2.6, 2.3))
    draw(ax, load_participants(args.csv))
    save(fig, args.out)
