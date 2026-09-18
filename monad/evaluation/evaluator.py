"""Evaluation Engine.

Compares a candidate against a baseline on declared metrics. A new version replaces
the old one only when the metrics show the change is worth it; otherwise ROLLBACK.
Insufficient data yields INCONCLUSIVE — which is *not* a deploy (Article 4, 16).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Metric:
    name: str
    higher_is_better: bool = True
    min_improvement: float = 0.0     # absolute threshold; 0 = any improvement counts
    critical: bool = False           # a regression here alone forces ROLLBACK


@dataclass
class Verdict:
    decision: str                    # DEPLOY | ROLLBACK | INCONCLUSIVE
    reasons: list[str] = field(default_factory=list)
    deltas: dict[str, float] = field(default_factory=dict)


def evaluate(metrics: list[Metric], baseline: dict[str, float],
             candidate: dict[str, float]) -> Verdict:
    reasons, deltas = [], {}
    improved = regressed = 0
    critical_regression = False
    for m in metrics:
        if m.name not in baseline or m.name not in candidate:
            reasons.append(f"{m.name}: missing data")
            continue
        delta = candidate[m.name] - baseline[m.name]
        if not m.higher_is_better:
            delta = -delta
        deltas[m.name] = round(delta, 6)
        if delta >= max(m.min_improvement, 1e-12):
            improved += 1
        elif delta < 0:
            regressed += 1
            reasons.append(f"{m.name}: regressed by {abs(delta):.4g}")
            if m.critical:
                critical_regression = True
    if not deltas:
        return Verdict("INCONCLUSIVE", reasons or ["no comparable metrics"], deltas)
    if critical_regression:
        return Verdict("ROLLBACK", reasons, deltas)
    if regressed and improved == 0:
        return Verdict("ROLLBACK", reasons, deltas)
    if improved and not regressed:
        return Verdict("DEPLOY", reasons or ["all measured metrics improved or held"], deltas)
    if improved and regressed:
        return Verdict("INCONCLUSIVE", reasons + ["mixed result: needs a human or a sharper metric"], deltas)
    return Verdict("INCONCLUSIVE", ["no measurable change"], deltas)
