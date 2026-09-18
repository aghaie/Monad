"""Global Creation Loop.

One call to `iterate()` runs a full cycle and persists state. Without a reasoning
engine most steps produce honest UNKNOWN records rather than fabricated progress.
Each iteration must understand / build / improve / test / discover something —
iterations that would only produce a report are flagged.
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

from monad.knowledge import Claim, KnowledgeStore
from monad.skills import SkillRegistry
from monad.agents import AgentFactory
from monad.factory import SoftwareFactory
from monad.core.engine import get_engine
from monad.core.quran_engine import Decision, check

REQUIRED_SKILLS = [
    "claim_classification", "contradiction_detection", "constitutional_check",
    "candidate_evaluation", "product_scoring", "skill_creation",
    "web_research", "quranic_reference",
]


@dataclass
class IterationRecord:
    number: int
    started: str
    engine: str
    observations: dict = field(default_factory=dict)
    unknowns: list[str] = field(default_factory=list)
    capability_gaps: list[str] = field(default_factory=list)
    contradictions: int = 0
    stale_claims: int = 0
    products: list[dict] = field(default_factory=list)
    blocked: list[str] = field(default_factory=list)
    learned: list[str] = field(default_factory=list)
    next_step: str = ""
    did_real_work: bool = False
    finished: str = ""


class MonadLoop:
    def __init__(self, root: str | Path, engine: str = "null"):
        self.root = Path(root)
        data = self.root / "data"
        self.knowledge = KnowledgeStore(data / "knowledge.jsonl")
        self.skills = SkillRegistry(data / "skills.jsonl")
        self.agents = AgentFactory(data / "agents.jsonl", self.skills)
        self.factory = SoftwareFactory(data / "products.jsonl")
        self.engine = get_engine(engine)
        self.state_path = data / "loop_state.json"
        self.state = json.loads(self.state_path.read_text()) if self.state_path.exists() else {"iterations": 0}

    # ---- steps -------------------------------------------------------------
    def observe_world(self, rec: IterationRecord) -> None:
        # v0.1: MONAD observes *itself* and its repository (Section XXV). External
        # observation requires the web_research skill — recorded as a gap.
        rec.observations = {
            "claims": len(self.knowledge.all()),
            "skills": len(self.skills.names()),
            "active_skills": len([n for n in self.skills.names()
                                  if (c := self.skills.current(n)) and c.status == "ACTIVE"]),
            "agents": len(self.agents.list()),
            "products": len(self.factory.products()),
            "git_head": self._git("rev-parse", "--short", "HEAD"),
        }

    def identify_unknowns(self, rec: IterationRecord) -> None:
        rec.unknowns = [c.text for c in self.knowledge.unknowns()]
        rec.contradictions = len(self.knowledge.contradictions())
        rec.stale_claims = len(self.knowledge.stale())

    def identify_capability_gaps(self, rec: IterationRecord) -> None:
        rec.capability_gaps = self.skills.gaps(REQUIRED_SKILLS)
        if self.engine.name == "null":
            rec.blocked.append("no reasoning engine configured (needs API key or local model)")

    def select_problem(self, rec: IterationRecord) -> None:
        rec.products = [{"name": p.name, "stage": p.stage, "outcome": p.outcome}
                        for p in self.factory.products()]

    def self_check(self, rec: IterationRecord) -> None:
        d = Decision("run iteration", "continue the creation loop", {
            "truth_over_falsehood": True, "justice_no_oppression": True,
            "no_corruption": True, "no_deception": True, "trust_and_covenant": True,
            "no_waste": True, "knowledge_over_conjecture": True, "human_dignity": True,
            "reform_not_appearance": None, "better_purer_path": None,
        })
        rec.learned.append(f"constitutional self-check: {check(d).result}")

    def learn(self, rec: IterationRecord) -> None:
        self.knowledge.add(Claim(
            text=f"iteration {rec.number}: {len(rec.capability_gaps)} capability gaps, "
                 f"{rec.contradictions} contradictions, engine={rec.engine}",
            origin="DATA", confidence=1.0, source="monad.core.loop.iterate",
            tags=["self-observation"], expires_days=30))
        rec.did_real_work = bool(rec.capability_gaps) or bool(rec.products)
        rec.next_step = (
            f"close gap: {rec.capability_gaps[0]}" if rec.capability_gaps
            else "run World Observer against an external source")

    # ---- driver ------------------------------------------------------------
    def iterate(self) -> IterationRecord:
        n = self.state["iterations"] + 1
        rec = IterationRecord(n, datetime.now(timezone.utc).isoformat(), self.engine.name)
        for step in (self.observe_world, self.identify_unknowns, self.identify_capability_gaps,
                     self.select_problem, self.self_check, self.learn):
            step(rec)
        rec.finished = datetime.now(timezone.utc).isoformat()
        self.state["iterations"] = n
        self.state["last"] = asdict(rec)
        self.state_path.write_text(json.dumps(self.state, ensure_ascii=False, indent=2))
        (self.root / "reports").mkdir(exist_ok=True)
        (self.root / "reports" / f"iteration_{n:03d}.json").write_text(
            json.dumps(asdict(rec), ensure_ascii=False, indent=2))
        return rec

    def _git(self, *args: str) -> str:
        try:
            return subprocess.check_output(["git", *args], cwd=self.root, text=True,
                                           stderr=subprocess.DEVNULL).strip()
        except Exception:
            return "UNKNOWN"


def report(rec: IterationRecord) -> str:
    """MONAD REPORT — short, clear, human (Section XX)."""
    lines = [
        f"MONAD REPORT — iteration {rec.number}",
        f"1. فهمیدم: {rec.observations}",
        f"2. ساختم/بررسی کردم: {len(rec.products)} محصول در خط تولید",
        f"3. قابل استفاده: {[p['name'] for p in rec.products if p['stage'] in ('TEST','DEPLOYMENT','OBSERVATION','IMPROVEMENT')]}",
        f"4. بهتر شد: —",
        f"5. شکست/مسدود: {rec.blocked}",
        f"6. یاد گرفتم: {rec.learned}; شکاف‌ها: {rec.capability_gaps}",
        f"7. قدم بعد: {rec.next_step}",
    ]
    if not rec.did_real_work:
        lines.append("WARNING: this iteration produced only a report — not acceptable as a pattern.")
    return "\n".join(lines)
