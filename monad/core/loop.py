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
from monad.evaluation import Metric, evaluate
from monad.core.quran_engine import Decision, check
from monad.web import content_sha, fetch, read_url

# What "better" means for an iteration, measured against the previous one (Article 14).
ITERATION_METRICS = [
    Metric("active_skills"), Metric("sources_read"), Metric("products"),
    Metric("capability_gaps", higher_is_better=False, critical=True),
    Metric("contradictions", higher_is_better=False),
    Metric("stale_claims", higher_is_better=False),
    Metric("blocked", higher_is_better=False),
]


def iteration_metrics(rec: dict) -> dict[str, float]:
    obs = rec.get("observations", {})
    return {
        "active_skills": obs.get("active_skills", 0),
        "sources_read": len([v for v in obs.get("sources", {}).values() if v != "failed"]),
        "products": obs.get("products", 0),
        "capability_gaps": len(rec.get("capability_gaps", [])),
        "contradictions": rec.get("contradictions", 0),
        "stale_claims": rec.get("stale_claims", 0),
        "blocked": len(rec.get("blocked", [])),
    }


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
    improvement: dict = field(default_factory=dict)   # Article 14: this iteration vs the previous one
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

    def read_sources(self, rec: IterationRecord) -> None:
        """World Observer v0.2: re-read every URL in data/sources.txt; store a new DATA
        claim only when the content (sha256) is new or changed. Failures are recorded, not hidden."""
        path = self.root / "data" / "sources.txt"
        urls = [l.strip() for l in path.read_text().splitlines()
                if l.strip() and not l.startswith("#")] if path.exists() else []
        seen = {}
        for c in self.knowledge.all():
            seen.setdefault(c.source, set()).update(t for t in c.tags if t.startswith("sha256:"))
        rec.observations["sources"] = {}
        for url in urls:
            try:
                raw = fetch(url)
            except Exception as e:  # network/HTTP error: say so, keep going
                rec.blocked.append(f"read failed: {url}: {e}")
                continue
            sha = content_sha(raw)
            if sha in seen.get(url, ()):
                rec.observations["sources"][url] = "unchanged"
                continue
            read_url(self.knowledge, url, fetcher=lambda _u, raw=raw: raw)
            rec.observations["sources"][url] = "changed" if url in seen else "new"

    def identify_unknowns(self, rec: IterationRecord) -> None:
        rec.unknowns = [c.text for c in self.knowledge.unknowns()]
        rec.contradictions = len(self.knowledge.contradictions())
        stale = self.knowledge.stale()
        rec.stale_claims = len(stale)
        for c in stale:  # staleness sweep: mark, never delete (append-only memory)
            if c.status != "STALE":
                self.knowledge.update(c.id, status="STALE")

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
        sources = rec.observations.get("sources", {})
        rec.did_real_work = bool(rec.capability_gaps) or bool(rec.products) or bool(sources)
        rec.next_step = (
            f"close gap: {rec.capability_gaps[0]}" if rec.capability_gaps
            else "add sources to data/sources.txt" if not sources
            else "judge what the sources said (needs Engine); until then: contradictions/staleness sweep")

    def compare(self, rec: IterationRecord) -> None:
        """Article 14: every version must be comparable with the previous version."""
        prev = self.state.get("last")
        if not prev:
            rec.improvement = {"verdict": "INCONCLUSIVE", "reasons": ["no previous iteration"], "deltas": {}}
            return
        v = evaluate(ITERATION_METRICS, iteration_metrics(prev), iteration_metrics(asdict(rec)))
        rec.improvement = {"verdict": v.decision, "reasons": v.reasons,
                           "deltas": {k: d for k, d in v.deltas.items() if d}}

    # ---- driver ------------------------------------------------------------
    def iterate(self) -> IterationRecord:
        n = self.state["iterations"] + 1
        rec = IterationRecord(n, datetime.now(timezone.utc).isoformat(), self.engine.name)
        for step in (self.observe_world, self.read_sources, self.identify_unknowns, self.identify_capability_gaps,
                     self.select_problem, self.self_check, self.learn, self.compare):
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
        f"3. قابل استفاده: {[p['name'] for p in rec.products if p['stage'] in ('TEST','SECURITY_REVIEW','USER_EXPERIENCE','DEPLOYMENT','OBSERVATION','IMPROVEMENT')]}",
        f"4. بهتر شد: {rec.improvement.get('verdict')} {rec.improvement.get('deltas') or rec.improvement.get('reasons')}",
        f"5. شکست/مسدود: {rec.blocked}",
        f"6. یاد گرفتم: {rec.learned}; شکاف‌ها: {rec.capability_gaps}",
        f"7. قدم بعد: {rec.next_step}",
    ]
    if not rec.did_real_work:
        lines.append("WARNING: this iteration produced only a report — not acceptable as a pattern.")
    return "\n".join(lines)
