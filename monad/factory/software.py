"""Software Factory + Product Discovery.

A product moves through a fixed pipeline. Every product must have WHY / WHO / PROBLEM /
SOLUTION / MEASUREMENT. Discovery scores a candidate problem on twelve dimensions so
the choice of what to build does not rest on taste alone.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

PIPELINE = ("PROBLEM", "REQUIREMENTS", "RESEARCH", "ARCHITECTURE", "PROTOTYPE",
            "IMPLEMENTATION", "TEST", "SECURITY_REVIEW", "USER_EXPERIENCE",
            "DEPLOYMENT", "OBSERVATION", "IMPROVEMENT")

DIMENSIONS = ("human_need", "truth", "utility", "impact", "feasibility", "cost",
              "risk", "reach", "urgency", "existing_solutions", "existing_failures",
              "potential_improvement")
# dimensions where a LOW score is good
INVERTED = {"cost", "risk", "existing_solutions"}


@dataclass
class ProblemCandidate:
    title: str
    description: str
    scores: dict[str, int]          # each dimension 1..5
    evidence: list[str] = field(default_factory=list)  # knowledge claim ids / sources

    def validate(self) -> list[str]:
        problems = [f"missing dimension {d}" for d in DIMENSIONS if d not in self.scores]
        problems += [f"{d} out of range" for d, v in self.scores.items() if not 1 <= v <= 5]
        return problems

    def total(self) -> float:
        s = 0.0
        for d in DIMENSIONS:
            v = self.scores[d]
            s += (6 - v) if d in INVERTED else v
        return round(s / len(DIMENSIONS), 2)


def rank(candidates: list[ProblemCandidate]) -> list[tuple[float, ProblemCandidate]]:
    for c in candidates:
        if (p := c.validate()):
            raise ValueError(f"{c.title}: {'; '.join(p)}")
    return sorted(((c.total(), c) for c in candidates), key=lambda t: -t[0])


@dataclass
class Product:
    name: str
    why: str
    who: str
    problem: str
    solution: str
    measurement: str
    stage: str = "PROBLEM"
    history: list[dict] = field(default_factory=list)
    outcome: str = "UNKNOWN"   # UNKNOWN | USEFUL | NOT_USEFUL (real-world, not claimed)
    created: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def validate(self) -> list[str]:
        return [f"missing {k}" for k in ("why", "who", "problem", "solution", "measurement")
                if not getattr(self, k).strip()]

    def advance(self, to_stage: str, note: str, blocked: bool = False) -> None:
        if to_stage not in PIPELINE:
            raise ValueError(to_stage)
        if PIPELINE.index(to_stage) < PIPELINE.index(self.stage):
            raise ValueError("pipeline moves forward; use a new product cycle for rework")
        self.history.append({"from": self.stage, "to": to_stage, "note": note,
                             "blocked": blocked,
                             "at": datetime.now(timezone.utc).isoformat()})
        if not blocked:
            self.stage = to_stage

    def record_outcome(self, useful: bool, evidence: str) -> None:
        """Real result beats appearance (Article 7). Failure is recorded, not hidden."""
        self.outcome = "USEFUL" if useful else "NOT_USEFUL"
        self.history.append({"outcome": self.outcome, "evidence": evidence,
                             "at": datetime.now(timezone.utc).isoformat()})


class SoftwareFactory:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def save(self, p: Product) -> Product:
        if (problems := p.validate()):
            raise ValueError("; ".join(problems))
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(p), ensure_ascii=False) + "\n")
        return p

    def products(self) -> list[Product]:
        latest: dict[str, Product] = {}
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                p = Product(**json.loads(line))
                latest[p.name] = p
        return list(latest.values())
