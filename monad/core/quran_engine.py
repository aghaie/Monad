"""Quranic Decision Engine.

A permanent layer that checks significant decisions against the Constitution's
principles. It returns VALID / INVALID / UNVERIFIED with explainable reasons.

It does NOT attach verses to technical decisions. Every Qur'anic connection recorded
here is at the level of principle and must be explainable; the principle names below
are the explanation.
"""
from __future__ import annotations

from dataclasses import dataclass, field

# Principle → the check it grounds. Origin: QURANIC_PRINCIPLE (principle level),
# mapping to checks is UNDERSTANDING.
PRINCIPLES = {
    "truth_over_falsehood": "no distortion or concealment of truth",
    "justice_no_oppression": "no zulm: no one's right is violated",
    "no_corruption": "no fasad: no harm to people, systems, or the earth",
    "no_deception": "no fraud, hidden agenda, or misleading appearance",
    "trust_and_covenant": "no betrayal of trust; promises are kept",
    "no_waste": "no israf: no wasteful use of resources",
    "knowledge_over_conjecture": "based on knowledge/evidence, not mere guess",
    "human_dignity": "karamah: the human is not degraded or owned",
    "reform_not_appearance": "real islah, not cosmetic change",
    "better_purer_path": "a cleaner alternative was actually looked for",
}


@dataclass
class Decision:
    title: str
    description: str
    answers: dict[str, bool | None]   # principle key → True (ok) / False (violates) / None (unknown)
    origin: str = "ENGINEERING_DECISION"
    is_significant: bool = True


@dataclass
class Check:
    result: str                       # VALID | INVALID | UNVERIFIED
    violations: list[str] = field(default_factory=list)
    unverified: list[str] = field(default_factory=list)
    explanation: str = ""


def check(decision: Decision) -> Check:
    if not decision.is_significant:
        return Check("VALID", explanation="not significant; constitutional check not required")
    violations = [f"{k}: {PRINCIPLES[k]}" for k, v in decision.answers.items()
                  if k in PRINCIPLES and v is False]
    unverified = [f"{k}: {PRINCIPLES[k]}" for k in PRINCIPLES
                  if decision.answers.get(k) is None]
    if violations:
        return Check("INVALID", violations, unverified,
                     "decision violates a constitutional principle; it is recorded and not executed")
    if unverified:
        return Check("UNVERIFIED", [], unverified,
                     "not enough is known to validate; MONAD says 'I don't know' rather than approving")
    return Check("VALID", explanation="all principles answered and satisfied")
