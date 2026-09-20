"""Skill Factory registry.

A skill is a versioned, testable capability. Registering a new version keeps the old
one so ROLLBACK is always possible (Constitution Articles 12–14).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path

from monad.core.monad import Monad

# `tests` may be empty at SPEC stage; activation then refuses (see activate()).
REQUIRED = ("name", "purpose", "inputs", "outputs", "tools",
            "limitations", "evaluation", "version")


@dataclass
class SkillSpec(Monad):
    """A Monad of kind `skill`; identity (id) is shared by all records of one name@version."""
    name: str
    purpose: str
    inputs: list[str]
    outputs: list[str]
    tools: list[str]
    dependencies: list[str]
    limitations: list[str]
    tests: str                      # path to tests; empty means not ACTIVE-able
    evaluation: str                 # metric + threshold
    version: str = "0.1.0"
    changelog: list[dict] = field(default_factory=list)
    kind: str = field(default="skill", kw_only=True)
    origin: str = field(default="ENGINEERING_DECISION", kw_only=True)
    status: str = field(default="SPEC", kw_only=True)   # SPEC | ACTIVE | ROLLED_BACK

    def validate(self) -> list[str]:
        problems = []
        for k in REQUIRED:
            if getattr(self, k) in ("", [], None):
                problems.append(f"missing {k}")
        parts = self.version.split(".")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            problems.append("version must be semver MAJOR.MINOR.PATCH")
        return problems


class SkillRegistry:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def _records(self) -> list[SkillSpec]:
        out = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                out.append(SkillSpec(**json.loads(line)))
        return out

    def _append(self, spec: SkillSpec) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(spec), ensure_ascii=False) + "\n")

    def register(self, spec: SkillSpec, why: str, expected_benefit: str) -> SkillSpec:
        problems = spec.validate()
        if problems:
            raise ValueError("; ".join(problems))
        spec.changelog.append({
            "version": spec.version, "why": why, "what": "registered",
            "expected_benefit": expected_benefit, "actual_result": "pending",
        })
        self._append(spec)
        return spec

    def activate(self, name: str, version: str, test_passed: bool) -> SkillSpec:
        """A skill becomes ACTIVE only if its tests passed (Article 4, 7)."""
        spec = self.get(name, version)
        if spec is None:
            raise KeyError(f"{name}@{version}")
        if not spec.tests or not test_passed:
            spec.status = "SPEC"
            spec.changelog.append({"version": version, "what": "activation refused",
                                   "actual_result": "tests missing or failing"})
        else:
            spec.status = "ACTIVE"
            spec.changelog.append({"version": version, "what": "activated",
                                   "actual_result": "tests passed"})
        self._append(spec)
        return spec

    def rollback(self, name: str, reason: str) -> SkillSpec | None:
        """Mark the current version ROLLED_BACK; the previous version becomes current."""
        versions = self.versions(name)
        if not versions:
            return None
        current = versions[-1]
        current.status = "ROLLED_BACK"
        current.changelog.append({"version": current.version, "what": "rollback", "why": reason})
        self._append(current)
        return versions[-2] if len(versions) > 1 else None

    def versions(self, name: str) -> list[SkillSpec]:
        latest: dict[str, SkillSpec] = {}
        for r in self._records():
            if r.name == name:
                latest[r.version] = r
        return sorted(latest.values(), key=lambda s: tuple(int(p) for p in s.version.split(".")))

    def current(self, name: str) -> SkillSpec | None:
        live = [v for v in self.versions(name) if v.status != "ROLLED_BACK"]
        return live[-1] if live else None

    def get(self, name: str, version: str) -> SkillSpec | None:
        for v in self.versions(name):
            if v.version == version:
                return v
        return None

    def names(self) -> list[str]:
        return sorted({r.name for r in self._records()})

    def gaps(self, required: list[str]) -> list[str]:
        """Capability gap = required skill with no ACTIVE version."""
        return [n for n in required if (c := self.current(n)) is None or c.status != "ACTIVE"]
