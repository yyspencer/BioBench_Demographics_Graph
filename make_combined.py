"""Combined three-panel demographics figure: (a) age, (b) sex, (c) stature vs. mass.

    python make_combined.py --csv participants.csv --out om_demographics.pdf

To refresh the figure used in the paper:
    python make_combined.py --out ../om_demographics.pdf
"""
import matplotlib.pyplot as plt

import plot_age
import plot_sex
import plot_mass
from common import apply_style, cli, load_participants, save

if __name__ == "__main__":
    args = cli(__doc__, "om_demographics.pdf")
    apply_style()
    people = load_participants(args.csv)

    fig, axes = plt.subplots(1, 3, figsize=(8.6, 2.8),
                             gridspec_kw=dict(width_ratios=[1.15, 0.85, 1.15], wspace=0.45))
    plot_age.draw(axes[0], people)
    plot_sex.draw(axes[1], people)
    plot_mass.draw(axes[2], people)
    save(fig, args.out)
