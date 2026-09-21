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
from monad.core.engine import Pending, get_engine
from monad.evaluation import Metric, evaluate
from monad.core.quran_engine import Decision, check
from monad.web import content_sha, fetch, html_to_text, read_url
from monad.usage import ingest, usage
from monad.core.monad import MonadStore
from monad.reports import register_reports

# What "better" means for an iteration, measured against the previous one (Article 14).
ITERATION_METRICS = [
    Metric("active_skills"), Metric("sources_read"), Metric("judged_sources"), Metric("unknowns_resolved"), Metric("products"),
    Metric("unverified_principles", higher_is_better=False),
    Metric("usage_claims"),   # Article 20: real use by real users, ingested from product exports
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
        "judged_sources": obs.get("judged_sources", 0),
        "unknowns_resolved": obs.get("unknowns_resolved", 0),
        # iterations before this metric existed hardcoded exactly two unanswered principles,
        # so their honest reading is 2 — not 0, which would flatter the past.
        "unverified_principles": obs.get("unverified_principles", 2),
        "products": obs.get("products", 0),
        "usage_claims": sum(u.get("claims", 0) for u in obs.get("usage", {}).values()),
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
    def __init__(self, root: str | Path, engine: str | None = None):
        self.root = Path(root)
        data = self.root / "data"
        self.knowledge = KnowledgeStore(data / "knowledge.jsonl")
        self.skills = SkillRegistry(data / "skills.jsonl")
        self.agents = AgentFactory(data / "agents.jsonl", self.skills)
        self.factory = SoftwareFactory(data / "products.jsonl")
        self.monads = MonadStore(data / "monads.jsonl")   # root store: every stored thing is a Monad
        self.engine = get_engine(engine)
        self.state_path = data / "loop_state.json"
        self.state = json.loads(self.state_path.read_text()) if self.state_path.exists() else {"iterations": 0}

    # ---- steps -------------------------------------------------------------
    def observe_world(self, rec: IterationRecord) -> None:
        # v0.1: MONAD observes *itself* and its repository (Section XXV). External
        # observation requires the web_research skill — recorded as a gap.
        rec.observations["reports_registered"] = len(register_reports(self.monads, self.root))
        rec.observations = {
            **rec.observations,
            "monads": len(self.monads.all()),
            "claims": len(self.knowledge.all()),
            "skills": len(self.skills.names()),
            "active_skills": len([n for n in self.skills.names()
                                  if (c := self.skills.current(n)) and c.status == "ACTIVE"]),
            "agents": len(self.agents.list()),
            "products": len(self.factory.products()),
            "git_head": self._git("rev-parse", "--short", "HEAD"),
            "usage": {p.name: self._usage(p.name) for p in self.factory.products()},
        }

    def _usage(self, product: str) -> dict:
        snap = self.root / "data" / "usage" / f"{product}.jsonl"
        if snap.exists():
            ingest(self.knowledge, snap, product)  # idempotent: `serve` usually ingested already
        return usage(self.knowledge, product)

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
            claim = read_url(self.knowledge, url, fetcher=lambda _u, raw=raw: raw)
            rec.observations["sources"][url] = "changed" if url in seen else "new"
            self.judge_source(rec, claim, raw)

    JUDGE_SYSTEM = ("You extract what a web page states. Reply with a JSON array of at most 3 short, "
                    "self-contained factual statements the page makes, in the page's language. "
                    "No opinions, no inference, no commentary. JSON only.")

    def judge_source(self, rec: IterationRecord, claim: Claim, raw: bytes) -> None:
        """First real Engine use: extract what a new/changed source states → DATA claims about
        the source (confidence 0.6: the model may misread). Engine failure is recorded, not hidden."""
        if self.engine.name == "null":
            return
        _, text = html_to_text(raw.decode("utf-8", errors="replace"))
        # The question carries the version of the page it is about. An engine that remembers
        # answers by question (SessionEngine does) would otherwise hand back yesterday's answer
        # for a page that changed past the excerpt — a judgement of text nobody judged.
        # ponytail: the engine still sees only the first 6000 chars; widen it if a source's tail
        # ever carries the news.
        prompt = f"[{content_sha(raw)}] {text[:6000]}"
        try:
            reply = self.engine.complete(prompt, system=self.JUDGE_SYSTEM)
            statements = json.loads(reply[reply.find("["):reply.rfind("]") + 1])
        except Pending:  # asked, not answered yet: counted once, by identify_capability_gaps.
            return       # An async engine answers after this run, so the extraction waits for
                         # the next change of the page. Known ceiling, recorded not hidden.
        except Exception as e:  # unreachable server, bad JSON, ...
            rec.blocked.append(f"engine {self.engine.name} failed on {claim.source}: {str(e)[:120]}")
            return
        for st in statements[:3]:
            if isinstance(st, str) and st.strip():
                self.knowledge.add(Claim(text=f"{claim.source} states: {st.strip()}", origin="DATA",
                                         confidence=0.6, source=claim.source, evidence=[claim.id],
                                         tags=["extracted", f"engine:{self.engine.name}"], expires_days=30))
        rec.learned.append(f"extracted {min(len(statements), 3)} statements from {claim.source}")

    def identify_unknowns(self, rec: IterationRecord) -> None:
        rec.unknowns = [c.text for c in self.knowledge.unknowns()]
        rec.observations["unknowns_resolved"] = len(self.knowledge.resolved_unknowns())
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
        elif q := self.engine.pending():  # asked, nobody answered: a gap, said out loud
            rec.blocked.append(f"{len(q)} unanswered question(s) for engine {self.engine.name}: "
                               f"`python3 -m monad qa`")

    def select_problem(self, rec: IterationRecord) -> None:
        rec.products = [{"name": p.name, "stage": p.stage, "outcome": p.outcome}
                        for p in self.factory.products()]

    def self_check(self, rec: IterationRecord) -> None:
        """Eight principles the loop itself can honour by construction; two ask for a
        judgement — «real reform, not cosmetics» and «was a cleaner path looked for» — and a
        literal `True` there would be the very self-deception they forbid. So they are read
        from the Engine's recorded answer (a claim tagged `selfcheck:<principle>`, with its
        reason and source) and expire with that claim: no self-approval outlives its evidence."""
        judged = {"reform_not_appearance": None, "better_purer_path": None}
        for c in self.knowledge.all():
            for key in judged:
                if f"selfcheck:{key}" in c.tags and not c.is_stale():
                    judged[key] = "answer:true" in c.tags
        d = Decision("run iteration", "continue the creation loop", {
            "truth_over_falsehood": True, "justice_no_oppression": True,
            "no_corruption": True, "no_deception": True, "trust_and_covenant": True,
            "no_waste": True, "knowledge_over_conjecture": True, "human_dignity": True,
            **judged,
        })
        result = check(d)
        rec.observations["unverified_principles"] = len(result.unverified)
        rec.learned.append(f"constitutional self-check: {result.result}")
        if result.result != "VALID":   # said out loud, not buried in a log line
            rec.blocked.append(f"constitutional self-check {result.result}: "
                               f"{', '.join(result.unverified + result.violations)}")

    def learn(self, rec: IterationRecord) -> None:
        self.knowledge.add(Claim(
            text=f"iteration {rec.number}: {len(rec.capability_gaps)} capability gaps, "
                 f"{rec.contradictions} contradictions, engine={rec.engine}",
            origin="DATA", confidence=1.0, source="monad.core.loop.iterate",
            tags=["self-observation"], expires_days=30))
        sources = rec.observations.get("sources", {})
        # A judgement is about the text that was read, not about the URL: when a watched page
        # changes, its newest raw claim has no judgement yet and the source is unjudged again.
        claims = self.knowledge.all()
        newest, sha_of = {}, {}
        for c in claims:
            if "web_research" in c.tags:
                sha_of[c.id] = next((t for t in c.tags if t.startswith("sha256:")), "")
                if c.created >= newest.get(c.source, ("",))[0]:
                    newest[c.source] = (c.created, sha_of[c.id])
        # keyed by the text's hash, not by the fetch: re-reading the same page is not a new
        # version, and a judgement of that text stays valid however often it is fetched.
        judged = {c.source for c in claims if "extracted" in c.tags
                  and newest.get(c.source, ("", ""))[1] in [sha_of.get(e, "") for e in c.evidence]}
        unjudged = [u for u in sources if u not in judged]
        rec.observations["judged_sources"] = len(sources) - len(unjudged)
        rec.did_real_work = bool(rec.capability_gaps) or bool(rec.products) or bool(sources)
        no_usage = [p for p, u in rec.observations.get("usage", {}).items() if not u.get("claims")]
        rec.next_step = (
            f"close gap: {rec.capability_gaps[0]}" if rec.capability_gaps
            else "add sources to data/sources.txt" if not sources
            else f"first real use of {no_usage[0]}: `python3 -m monad serve`, then work in the product (it syncs itself)" if no_usage
            else f"judge what this source said (needs Engine): {unjudged[0]} — `python3 -m monad claim DATA <url> <what it states> --evidence <raw claim id> --tags extracted`" if unjudged
            else f"resolve unknown: {rec.unknowns[0][:120]}" if rec.unknowns
            else "contradictions/staleness sweep")

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
