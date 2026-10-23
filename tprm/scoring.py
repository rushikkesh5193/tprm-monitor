"""Inherent risk, tiering and questionnaire (control) scoring.

The model is deliberately simple and transparent so a reviewer can explain
every number. Weights and thresholds live in config.json.
"""
from __future__ import annotations

ANSWER_VALUE = {"yes": 1.0, "partial": 0.5, "no": 0.0}   # "na" is excluded


def inherent_score(v, cfg) -> float:
    """0-100. Combines data sensitivity, business criticality and access level."""
    ds = max((cfg["data_scores"].get(t, 0) for t in v.data_types), default=0)
    acc = cfg["access_scores"].get(v.access, 0)
    w = cfg["weights"]
    raw = (w["data"] * ds / 4 + w["criticality"] * v.criticality / 4
           + w["access"] * acc / 3)
    return round(100 * raw, 1)


def tier_for(score: float, cfg) -> int:
    t = cfg["tier_thresholds"]
    if score >= t["1"]:
        return 1
    if score >= t["2"]:
        return 2
    if score >= t["3"]:
        return 3
    return 4


def control_score(v, cfg):
    """Weighted questionnaire score 0-100, or None when too few answers.

    Unanswered questions and 'na' are excluded from the score, but if the
    answered weight is below min_questionnaire_coverage of the total, the
    questionnaire is treated as incomplete (None) rather than guessing.
    """
    total = sum(q["weight"] for q in cfg["questionnaire"])
    got = answered = 0.0
    for q in cfg["questionnaire"]:
        a = v.answers.get(q["id"])
        if a in ANSWER_VALUE:
            answered += q["weight"]
            got += q["weight"] * ANSWER_VALUE[a]
    if total == 0 or answered / total < cfg["min_questionnaire_coverage"]:
        return None
    return round(100 * got / answered, 1)


def domain_scores(v, cfg) -> dict:
    """Per-domain score (for spotting which area is weak)."""
    acc = {}
    for q in cfg["questionnaire"]:
        a = v.answers.get(q["id"])
        if a in ANSWER_VALUE:
            g, t = acc.get(q["domain"], (0.0, 0.0))
            acc[q["domain"]] = (g + q["weight"] * ANSWER_VALUE[a], t + q["weight"])
    return {d: round(100 * g / t, 1) for d, (g, t) in acc.items()}


def residual_score(inherent: float, control, cfg) -> float:
    """Inherent risk reduced by control strength; unknown controls give no credit."""
    if control is None:
        return inherent
    return round(inherent * (1 - cfg["control_effect"] * control / 100), 1)
