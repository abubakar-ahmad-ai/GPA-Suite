"""
core/calculator.py
------------------
Pure calculation logic — no GUI imports.
SGPA, CGPA, Target Planner strategies.
"""

DEFAULT_FUTURE_CREDITS = 15.0


def safe_float(s, default=None):
    try:
        return float(s)
    except Exception:
        return default


def safe_int(s, default=None):
    v = safe_float(s, None)
    if v is None or int(v) != v:
        return default
    return int(v)


# ─────────────────────────────────────────────
#  SGPA / CGPA
# ─────────────────────────────────────────────

def compute_sgpa(subjects: list) -> tuple:
    """
    subjects: list of dicts {gpa, credits}
    Returns (sgpa, total_credits, total_points)
    """
    total_credits = 0.0
    total_points = 0.0
    for s in subjects:
        g = s.get("gpa")
        c = s.get("credits")
        if g is None or c is None or c <= 0:
            continue
        total_credits += c
        total_points += g * c
    sgpa = (total_points / total_credits) if total_credits > 0 else 0.0
    return sgpa, total_credits, total_points


def compute_cgpa(semesters: list) -> tuple:
    """
    semesters: list of dicts {gpa (=sgpa), credits}
    Returns (cgpa, total_credits, total_points)
    """
    return compute_sgpa(semesters)


# ─────────────────────────────────────────────
#  Target CGPA Planner
# ─────────────────────────────────────────────

def required_avg_gpa(target_cgpa, total_credits, achieved_points, remaining_credits):
    if remaining_credits <= 0:
        return None
    target_points = target_cgpa * total_credits
    return (target_points - achieved_points) / remaining_credits


def strategy_balanced(req_gpa, n):
    """Same GPA every semester."""
    clamped = max(0.0, min(4.0, req_gpa))
    return [clamped] * n


def strategy_progressive(req_gpa, n):
    """Start lower, increase gradually."""
    if n <= 0: return []
    if n == 1: return [max(0.0, min(4.0, req_gpa))]
    center = (n - 1) / 2.0
    positions = [i - center for i in range(n)]
    max_pos = max(abs(p) for p in positions) or 1.0
    shift = min(0.30, req_gpa * 0.75, (4.0 - req_gpa) * 0.75)
    step = shift / max_pos
    return [max(0.0, min(4.0, req_gpa + p * step)) for p in positions]


def strategy_flexible(req_gpa, n):
    """Alternating high-low pattern."""
    if n <= 0: return []
    if n == 1: return [max(0.0, min(4.0, req_gpa))]
    headroom = min(req_gpa, 4.0 - req_gpa)
    amp = min(0.35, headroom * 0.85)
    values = []
    for i in range(n):
        if n % 2 == 1 and i == n - 1:
            values.append(req_gpa)
            continue
        pair_i = i // 2
        a = max(0.05, amp - pair_i * 0.08)
        offset = a if i % 2 == 0 else -a
        values.append(max(0.0, min(4.0, req_gpa + offset)))
    return values


def strategy_front_loaded(req_gpa, n):
    """Work harder early, coast later."""
    if n <= 0: return []
    headroom = min(req_gpa, 4.0 - req_gpa)
    amp = min(0.4, headroom * 0.9)
    values = []
    for i in range(n):
        decay = (n - 1 - i) / max(n - 1, 1)
        values.append(max(0.0, min(4.0, req_gpa + amp * decay - amp * 0.5)))
    # re-center so average == req_gpa
    if values:
        avg = sum(values) / len(values)
        diff = req_gpa - avg
        values = [max(0.0, min(4.0, v + diff)) for v in values]
    return values
