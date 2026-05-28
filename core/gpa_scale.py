"""
core/gpa_scale.py
-----------------
GPA Scale definition, conversion logic, and persistent save/load.
Users can define custom scales via the GUI editor — stored in JSON.
"""

import json
import os
from pathlib import Path

# ─────────────────────────────────────────────
#  Default Scale  (85 → 4.0  system)
#  Each entry: (min_marks, max_marks, gpa_value, label)
# ─────────────────────────────────────────────
DEFAULT_SCALE_ROWS = [
    (85, 100, 4.0,  "85 – 100  →  4.0  (A+)"),
    (84, 84,  3.9,  "84        →  3.9  (A)"),
    (83, 83,  3.8,  "83        →  3.8  (A)"),
    (82, 82,  3.7,  "82        →  3.7  (A-)"),
    (81, 81,  3.6,  "81        →  3.6  (A-)"),
    (80, 80,  3.5,  "80        →  3.5  (B+)"),
    (79, 79,  3.4,  "79        →  3.4  (B+)"),
    (78, 78,  3.3,  "78        →  3.3  (B+)"),
    (77, 77,  3.2,  "77        →  3.2  (B)"),
    (76, 76,  3.1,  "76        →  3.1  (B)"),
    (75, 75,  3.0,  "75        →  3.0  (B)"),
    (72, 74,  2.9,  "72 – 74   →  2.9  (B-)"),
    (70, 71,  2.8,  "70 – 71   →  2.8  (C+)"),
    (68, 69,  2.7,  "68 – 69   →  2.7  (C+)"),
    (66, 67,  2.6,  "66 – 67   →  2.6  (C)"),
    (65, 65,  2.5,  "65        →  2.5  (C)"),
    (62, 64,  2.4,  "62 – 64   →  2.4  (C-)"),
    (60, 61,  2.3,  "60 – 61   →  2.3  (C-)"),
    (58, 59,  2.2,  "58 – 59   →  2.2  (D+)"),
    (56, 57,  2.1,  "56 – 57   →  2.1  (D)"),
    (55, 55,  2.0,  "55        →  2.0  (D)"),
    (53, 54,  1.9,  "53 – 54   →  1.9  (D-)"),
    (51, 52,  1.8,  "51 – 52   →  1.8  (D-)"),
    (50, 50,  1.7,  "50        →  1.7  (D-)"),
    (0,  49,  0.0,  "0  – 49   →  0.0  (F)"),
]

# Preset scales for popular university systems
PRESET_SCALES = {
    "Default (85→4.0)": DEFAULT_SCALE_ROWS,
    "Custom (80→4.0)": [
        (80, 100, 4.0,  "80 – 100  →  4.0  (A+)"),
        (79, 79,  3.9,  "79        →  3.9  (A)"),
        (78, 78,  3.8,  "78        →  3.8  (A)"),
        (77, 77,  3.7,  "77        →  3.7  (A-)"),
        (76, 76,  3.6,  "76        →  3.6  (A-)"),
        (75, 75,  3.5,  "75        →  3.5  (B+)"),
        (74, 74,  3.4,  "74        →  3.4  (B+)"),
        (73, 73,  3.3,  "73        →  3.3  (B+)"),
        (72, 72,  3.2,  "72        →  3.2  (B)"),
        (71, 71,  3.1,  "71        →  3.1  (B)"),
        (70, 70,  3.0,  "70        →  3.0  (B)"),
        (67, 69,  2.9,  "67 – 69   →  2.9  (B-)"),
        (65, 66,  2.8,  "65 – 66   →  2.8  (C+)"),
        (63, 64,  2.7,  "63 – 64   →  2.7  (C+)"),
        (61, 62,  2.6,  "61 – 62   →  2.6  (C)"),
        (60, 60,  2.5,  "60        →  2.5  (C)"),
        (57, 59,  2.4,  "57 – 59   →  2.4  (C-)"),
        (55, 56,  2.3,  "55 – 56   →  2.3  (C-)"),
        (53, 54,  2.2,  "53 – 54   →  2.2  (D+)"),
        (51, 52,  2.1,  "51 – 52   →  2.1  (D)"),
        (50, 50,  2.0,  "50        →  2.0  (D)"),
        (0,  49,  0.0,  "0  – 49   →  0.0  (F)"),
    ],
}

SCALE_FILE = Path(__file__).parent.parent / "data" / "custom_scale.json"


def marks_to_gpa(marks: float, scale_rows: list) -> float:
    """Convert integer marks to GPA using the given scale rows."""
    m = int(round(marks))
    for (lo, hi, gpa, _) in scale_rows:
        if lo <= m <= hi:
            return gpa
    return 0.0


def grade_letter(gpa: float) -> str:
    """Return letter grade for a GPA value."""
    if gpa >= 4.0: return "A+"
    if gpa >= 3.7: return "A"
    if gpa >= 3.5: return "A-"
    if gpa >= 3.3: return "B+"
    if gpa >= 3.0: return "B"
    if gpa >= 2.7: return "B-"
    if gpa >= 2.3: return "C+"
    if gpa >= 2.0: return "C"
    if gpa >= 1.7: return "C-"
    if gpa >= 1.3: return "D+"
    if gpa >= 1.0: return "D"
    if gpa >  0.0: return "D-"
    return "F"


def save_scale(scale_rows: list):
    """Save custom scale rows to JSON file."""
    SCALE_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = [{"min": lo, "max": hi, "gpa": gpa, "label": label}
            for (lo, hi, gpa, label) in scale_rows]
    with open(SCALE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_scale() -> list:
    """Load scale from JSON if it exists, else return default."""
    if SCALE_FILE.exists():
        try:
            with open(SCALE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            rows = [(d["min"], d["max"], d["gpa"], d["label"]) for d in data]
            if rows:
                return rows
        except Exception:
            pass
    return list(DEFAULT_SCALE_ROWS)


def build_label(lo: int, hi: int, gpa: float) -> str:
    """Auto-generate a label string from range and GPA."""
    if lo == hi:
        return f"{lo}        →  {gpa:.1f}"
    return f"{lo} – {hi}   →  {gpa:.1f}"
