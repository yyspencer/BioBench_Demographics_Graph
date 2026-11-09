"""(c) Stature vs. body mass: one marker per participant (shape and color by
sex), each labeled with its ID. Label positions are chosen automatically to
avoid overlapping other labels and markers.

    python plot_stature_mass.py --csv participants.csv --out stature_vs_mass.pdf
"""
import math

import matplotlib.pyplot as plt
from matplotlib.text import Text
from matplotlib.ticker import MultipleLocator

from common import (GRID_GRAY, SEX_COLOR, SEX_MARKER, SEX_ORDER, TEXT_GRAY,
                    apply_style, cli, load_participants, save)

# Label directions (unit dx, dy, ha, va), tried in order at each distance.
_DIRECTIONS = [
    (0, 1, "center", "bottom"),     # above
    (-0.7, 0.7, "right", "bottom"),  # above-left
    (0.7, -0.7, "left", "top"),     # below-right
    (0.7, 0.7, "left", "bottom"),   # above-right
    (0, -1, "center", "top"),       # below
    (-0.7, -0.7, "right", "top"),   # below-left
    (1, 0, "left", "center"),       # right
    (-1, 0, "right", "center"),     # left
]
# Distances from the marker center, in points. The first ring sits right next
# to the marker; farther rings get a thin leader line back to the marker.
_RINGS = [9, 15, 22, 30, 40]
_PAD = 1.5  # extra clearance (points) kept around every label and marker


def _overlaps(b, others):
    return any(not (b[2] < o[0] or b[0] > o[2] or b[3] < o[1] or b[1] > o[3])
               for o in others)


def _grow(b, d):
    return (b[0] - d, b[1] - d, b[2] + d, b[3] + d)


def _marker_boxes(ax, people):
    fig = ax.figure
    r = 6 * fig.dpi / 72  # approx marker radius in display px (generous)
    pts = [ax.transData.transform((p["height_m"], p["mass_kg"])) for p in people]
    return [(x - r, y - r, x + r, y + r) for x, y in pts]


def _place_labels(ax, people):
    """Place each ID so it covers no marker and no other label.

    Tries 8 directions at increasing distances and takes the first clean
    spot. If no clean spot exists anywhere, it falls back to the least-bad
    one and prints a warning naming the subject.
    """
    fig = ax.figure
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    pad = _PAD * fig.dpi / 72
    own_boxes = _marker_boxes(ax, people)
    marker_boxes = [_grow(b, pad) for b in own_boxes]
    axbox = ax.get_window_extent(renderer)
    placed = []

    def count(b, others):
        return sum(_overlaps(b, [o]) for o in others)

    # Label the most crowded points first, while there is still room nearby.
    def crowding(i):
        x, y = (marker_boxes[i][0] + marker_boxes[i][2]) / 2, \
               (marker_boxes[i][1] + marker_boxes[i][3]) / 2
        return -sum(math.hypot(x - (o[0] + o[2]) / 2, y - (o[1] + o[3]) / 2)
                    < 40 * fig.dpi / 72 for o in marker_boxes)
    order = sorted(range(len(people)), key=crowding)

    for i in order:
        p = people[i]
        best = None
        for ring, dist in enumerate(_RINGS):
            for ux, uy, ha, va in _DIRECTIONS:
                arrow = None
                if ring > 0:
                    arrow = dict(arrowstyle="-", color=GRID_GRAY, lw=0.7,
                                 shrinkA=1, shrinkB=5)
                t = ax.annotate(p["id"], (p["height_m"], p["mass_kg"]),
                                xytext=(ux * dist, uy * dist),
                                textcoords="offset points", ha=ha, va=va,
                                fontsize=9.5, color=TEXT_GRAY,
                                arrowprops=arrow, zorder=4)
                # Text-only extent (Annotation's own extent includes the
                # leader line, which always touches the marker).
                t.update_positions(renderer)
                bb = Text.get_window_extent(t, renderer)
                raw = (bb.x0, bb.y0, bb.x1, bb.y1)
                box = _grow(raw, pad)
                inside = (bb.x0 >= axbox.x0 and bb.x1 <= axbox.x1
                          and bb.y0 >= axbox.y0 and bb.y1 <= axbox.y1)
                others = marker_boxes[:i] + marker_boxes[i + 1:]
                # Covering a marker or label is far worse than leaving the
                # axes, which is worse than sitting farther away. The label's
                # own marker is checked without the extra padding.
                hits = (count(box, placed) + count(box, others)
                        + _overlaps(raw, [own_boxes[i]]))
                score = 1000 * hits + 100 * (not inside) + ring
                if best is None or score < best[0]:
                    if best is not None:
                        best[1].remove()
                    best = (score, t, box)
                else:
                    t.remove()
            if best[0] < 100:  # clean, in-axes spot found in this ring
                break
        if best[0] >= 1000:
            print(f"warning: could not place label {p['id']} without "
                  f"overlapping a marker or another label")
        placed.append(best[2])


def draw(ax, people, title="(c) Stature vs. body mass"):
    present = [s for s in SEX_ORDER if any(p["sex"] == s for p in people)]
    for sex in present:
        sub = [p for p in people if p["sex"] == sex]
        ax.scatter([p["height_m"] for p in sub], [p["mass_kg"] for p in sub],
                   s=70 if SEX_MARKER[sex] == "o" else 55,
                   marker=SEX_MARKER[sex], color=SEX_COLOR[sex],
                   edgecolor="white", linewidth=1.0, zorder=3)

    h = [p["height_m"] for p in people]
    m = [p["mass_kg"] for p in people]
    hpad = max((max(h) - min(h)) * 0.25, 0.03)
    mpad = max((max(m) - min(m)) * 0.25, 3)
    ax.set_xlim(min(h) - hpad, max(h) + hpad)
    ax.set_ylim(min(m) - mpad, max(m) + mpad)
    ax.xaxis.set_major_locator(MultipleLocator(0.1))
    ystart = math.floor(min(m) / 10) * 10
    ax.set_yticks(range(ystart, int(max(m) + mpad) + 1, 20))
    ax.grid(True, color=GRID_GRAY, lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.set_xlabel("Stature (m)")
    ax.set_ylabel("Body mass (kg)")
    ax.set_title(title)

    _place_labels(ax, people)


if __name__ == "__main__":
    args = cli(__doc__, "stature_vs_mass.pdf")
    apply_style()
    fig, ax = plt.subplots(figsize=(2.6, 2.3))
    draw(ax, load_participants(args.csv))
    save(fig, args.out)
