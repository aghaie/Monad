"""Knowledge Engine.

Append-only JSONL store of *claims*. Every claim carries exactly one constitutional
origin class, a confidence, provenance, evidence links, and timestamps. Contradictions
are recorded, never hidden. Nothing important is stored without an origin.
"""
from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Iterable

ORIGIN_CLASSES = (
    "REVELATION",
    "QURANIC_PRINCIPLE",
    "UNDERSTANDING",
    "DATA",
    "RATIONAL_ANALYSIS",
    "HYPOTHESIS",
    "EMPIRICAL_RESULT",
    "OPINION",
    "ENGINEERING_DECISION",
    "UNKNOWN",  # Article 16: MONAD must be able to say "I don't know"
)

STATUSES = ("OPEN", "SUPPORTED", "REFUTED", "STALE", "UNKNOWN")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Claim:
    text: str
    origin: str
    confidence: float = 0.5           # 0..1, proportional to evidence (Article 4)
    source: str = ""                  # provenance: URL, file, person, command
    evidence: list[str] = field(default_factory=list)   # ids of supporting claims
    contradicts: list[str] = field(default_factory=list)  # ids of contradicting claims
    tags: list[str] = field(default_factory=list)
    status: str = "OPEN"
    created: str = field(default_factory=_now)
    expires_days: int | None = None   # staleness horizon; None = timeless
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])

    def __post_init__(self) -> None:
        if self.origin not in ORIGIN_CLASSES:
            raise ValueError(f"origin must be one of {ORIGIN_CLASSES}, got {self.origin!r}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be within [0, 1]")
        if self.status not in STATUSES:
            raise ValueError(f"status must be one of {STATUSES}")
        if self.origin != "UNKNOWN" and not self.source:
            raise ValueError("no important knowledge without provenance: source is required")

    def is_stale(self, now: datetime | None = None) -> bool:
        if self.expires_days is None:
            return False
        now = now or datetime.now(timezone.utc)
        created = datetime.fromisoformat(self.created)
        return now - created > timedelta(days=self.expires_days)


_NEG = re.compile(r"\b(not|no|never|isn't|aren't|doesn't|don't|cannot|can't)\b|\bن(می|یست|دارد|باید)", re.I)


def _normalize(text: str) -> str:
    t = _NEG.sub(" ", text.lower())
    return re.sub(r"[^\w؀-ۿ]+", " ", t).strip()


def _has_negation(text: str) -> bool:
    return bool(_NEG.search(text))


class KnowledgeStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    # -- persistence ---------------------------------------------------------
    def _iter(self) -> Iterable[Claim]:
        with self.path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    yield Claim(**json.loads(line))

    def all(self) -> list[Claim]:
        # last record per id wins (append-only updates)
        latest: dict[str, Claim] = {}
        for c in self._iter():
            latest[c.id] = c
        return list(latest.values())

    def get(self, claim_id: str) -> Claim | None:
        for c in self.all():
            if c.id == claim_id:
                return c
        return None

    def _append(self, claim: Claim) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(claim), ensure_ascii=False) + "\n")

    # -- operations ----------------------------------------------------------
    def add(self, claim: Claim) -> Claim:
        """Store a claim and record (not hide) any contradictions it creates."""
        for other in self.find_contradictions(claim):
            if other.id not in claim.contradicts:
                claim.contradicts.append(other.id)
            if claim.id not in other.contradicts:
                other.contradicts.append(claim.id)
                self._append(other)
        self._append(claim)
        return claim

    def update(self, claim_id: str, **changes) -> Claim:
        current = self.get(claim_id)
        if current is None:
            raise KeyError(claim_id)
        data = asdict(current)
        data.update(changes)
        updated = Claim(**data)
        self._append(updated)
        return updated

    def find_contradictions(self, claim: Claim) -> list[Claim]:
        """Heuristic v1: same normalized proposition, opposite polarity.
        Origin: ENGINEERING_DECISION — a cheap, explainable first pass; an Engine-backed
        skill can replace it later (recorded in CAPABILITY_MAP)."""
        key, neg = _normalize(claim.text), _has_negation(claim.text)
        out = []
        for other in self.all():
            if other.id == claim.id:
                continue
            if _normalize(other.text) == key and _has_negation(other.text) != neg:
                out.append(other)
        return out

    def contradictions(self) -> list[tuple[Claim, Claim]]:
        seen, pairs = set(), []
        by_id = {c.id: c for c in self.all()}
        for c in by_id.values():
            for oid in c.contradicts:
                key = tuple(sorted((c.id, oid)))
                if key not in seen and oid in by_id:
                    seen.add(key)
                    pairs.append((c, by_id[oid]))
        return pairs

    def stale(self) -> list[Claim]:
        return [c for c in self.all() if c.is_stale()]

    def unknowns(self) -> list[Claim]:
        return [c for c in self.all() if c.origin == "UNKNOWN" or c.status == "UNKNOWN"]

    def by_origin(self, origin: str) -> list[Claim]:
        return [c for c in self.all() if c.origin == origin]

    def independent_evidence_count(self, claim_id: str) -> int:
        """Article: one fact must not be counted as many independent witnesses.
        Evidence claims sharing the same source count once."""
        claim = self.get(claim_id)
        if claim is None:
            return 0
        sources = set()
        for eid in claim.evidence:
            e = self.get(eid)
            if e:
                sources.add(e.source or e.id)
        return len(sources)
