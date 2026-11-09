"""(b) Sex composition: a single stacked bar with counts inside each segment,
category names above and percentages below.

    python plot_sex.py --csv participants.csv --out sex_composition.pdf
"""
import matplotlib.pyplot as plt

from common import (SEX_COLOR, SEX_ORDER, TEXT_GRAY, apply_style, cli,
                    load_participants, save)


def draw(ax, people, title="(b) Sex"):
    n = len(people)
    counts = [(s, sum(p["sex"] == s for p in people)) for s in SEX_ORDER]
    counts = [(s, c) for s, c in counts if c > 0]

    gap = 0.02 * n  # white gap between segments, in data units
    left = 0.0
    last = len(counts) - 1
    for i, (sex, c) in enumerate(counts):
        w = c - (gap if i < last else 0)
        ax.barh(0, w, left=left, height=1.0, color=SEX_COLOR[sex], lw=0)
        ax.text(left + w / 2, 0, f"{c}", ha="center", va="center",
                color="white", fontsize=17)
        # Outer labels hug the bar ends; any middle ones sit centered.
        if i == 0:
            x, ha = left, "left"
        elif i == last:
            x, ha = left + w, "right"
        else:
            x, ha = left + w / 2, "center"
        ax.text(x, 0.62, sex, ha=ha, va="bottom", fontsize=11.5)
        ax.text(x, -0.62, f"{100 * c / n:.0f}%", ha=ha, va="top",
                fontsize=10.5, color=TEXT_GRAY, style="italic")
        left += c

    ax.text(n / 2, -1.75, f"{n} participants", ha="center", va="center",
            fontsize=11, color=TEXT_GRAY)
    ax.set_xlim(-0.03 * n, n * 1.03)
    ax.set_ylim(-2.4, 1.8)
    ax.axis("off")
    ax.set_title(title)


if __name__ == "__main__":
    args = cli(__doc__, "sex_composition.pdf")
    apply_style()
    fig, ax = plt.subplots(figsize=(2.0, 2.3))
    draw(ax, load_participants(args.csv))
    save(fig, args.out)
