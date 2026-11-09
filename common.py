"""Shared helpers for the OM demographics figures: data loading, style, colors.

Participant CSV format (one row per participant, header required):

    id,sex,age,height_m,mass_kg
    S01,F,40,1.60,53
    S02,M,26,1.76,61

`sex` accepts M / Male / F / Female (case-insensitive); anything else is
shown as "Other".
"""
import argparse
import csv
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV = os.path.join(HERE, "subjects.csv")

SEX_ORDER = ["Male", "Female", "Other"]
SEX_COLOR = {"Male": "#3F76CC", "Female": "#DE6E40", "Other": "#8C8C8C"}
SEX_MARKER = {"Male": "o", "Female": "D", "Other": "s"}

AXIS_GRAY = "#7A7A7A"
TEXT_GRAY = "#444444"
GRID_GRAY = "#E2E2DE"


def _norm_sex(s):
    s = s.strip().lower()
    if s in ("m", "male", "man"):
        return "Male"
    if s in ("f", "female", "woman"):
        return "Female"
    return "Other"


def load_participants(path):
    """Read the participant CSV into a list of dicts with typed fields."""
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append({
                "id": r["id"].strip(),
                "sex": _norm_sex(r["sex"]),
                "age": float(r["age"]),
                "height_m": float(r["height_m"]),
                "mass_kg": float(r["mass_kg"]),
            })
    if not rows:
        raise ValueError(f"No participants found in {path}")
    return rows


def apply_style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Times", "STIXGeneral", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10.5,
        "xtick.labelsize": 9.5,
        "ytick.labelsize": 9.5,
        "axes.edgecolor": AXIS_GRAY,
        "axes.linewidth": 0.8,
        "xtick.color": AXIS_GRAY,
        "ytick.color": AXIS_GRAY,
        "xtick.labelcolor": TEXT_GRAY,
        "ytick.labelcolor": TEXT_GRAY,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "pdf.fonttype": 42,  # embed TrueType so text stays editable/searchable
        "ps.fonttype": 42,
    })


def cli(description, default_out):
    """Standard --csv / --out arguments shared by every script."""
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--csv", default=DEFAULT_CSV,
                   help="participant CSV (default: participants.csv next to this script)")
    p.add_argument("--out", default=os.path.join(HERE, default_out),
                   help="output PDF path")
    return p.parse_args()


def save(fig, out):
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    fig.savefig(out, format="pdf", bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    print(f"wrote {out}")
