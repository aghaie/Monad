"""Agent Factory.

An agent is a named bundle of skills operating under the Constitution. The factory
decides whether a new agent is *needed* (not merely possible) and records why.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

from monad.skills.registry import SkillRegistry


@dataclass
class AgentSpec:
    name: str
    purpose: str
    skills: list[str]
    why_needed: str
    test_plan: str
    retire_when: str
    constraints: list[str] = field(default_factory=lambda: ["MONAD_CONSTITUTION.md"])
    status: str = "PROPOSED"  # PROPOSED | ACTIVE | RETIRED
    created: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AgentFactory:
    def __init__(self, path: str | Path, skills: SkillRegistry):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)
        self.skills = skills

    def _all(self) -> dict[str, AgentSpec]:
        out: dict[str, AgentSpec] = {}
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                a = AgentSpec(**json.loads(line))
                out[a.name] = a
        return out

    def _append(self, a: AgentSpec) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(a), ensure_ascii=False) + "\n")

    def is_needed(self, spec: AgentSpec) -> tuple[bool, str]:
        """An agent is needed only if it has a stated reason, a test plan, a retirement
        condition, and does not duplicate an existing active agent's skill set."""
        if not spec.why_needed.strip():
            return False, "no reason given"
        if not spec.test_plan.strip() or not spec.retire_when.strip():
            return False, "agents without a test plan and retirement condition are not created"
        for a in self._all().values():
            if a.status == "ACTIVE" and set(a.skills) == set(spec.skills):
                return False, f"duplicates active agent {a.name}"
        return True, "ok"

    def create(self, spec: AgentSpec) -> AgentSpec:
        needed, reason = self.is_needed(spec)
        if not needed:
            raise ValueError(f"agent not created: {reason}")
        missing = self.skills.gaps(spec.skills)
        spec.status = "PROPOSED" if missing else "ACTIVE"
        self._append(spec)
        return spec

    def retire(self, name: str, reason: str) -> AgentSpec:
        a = self._all()[name]
        a.status = "RETIRED"
        a.retire_when = f"{a.retire_when} | retired: {reason}"
        self._append(a)
        return a

    def list(self) -> list[AgentSpec]:
        return list(self._all().values())
