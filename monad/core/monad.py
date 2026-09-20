"""The root entity. Every stored thing in MONAD is a Monad.

Root = fields only (no shared behaviour): id · kind · origin · created · status · source ·
supersedes · schema. Kinds are typed subclasses. Relations are Links — records, not columns.
Store = append-only JSONL: nothing is edited or deleted; change = new record with `supersedes`.
Readers ignore unknown fields (schema evolution is additive only).
Origin: ENGINEERING_DECISION, docs/monad-root-entity-2026-09-21.md.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict, fields
from datetime import datetime, timezone
from pathlib import Path

from monad.knowledge.store import ORIGIN_CLASSES


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Monad:
    kind: str = ""
    origin: str = ""
    source: str = ""                  # provenance: path, URL, person, command
    status: str = "OPEN"
    supersedes: str = ""              # id of the record this one replaces (append-only change)
    schema: int = 1
    created: str = field(default_factory=_now)
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])

    def __post_init__(self) -> None:
        if not self.kind:
            raise ValueError("kind is required")
        if self.origin not in ORIGIN_CLASSES:
            raise ValueError(f"origin must be one of {ORIGIN_CLASSES}, got {self.origin!r}")


@dataclass
class Link(Monad):
    kind: str = "link"
    src: str = ""
    dst: str = ""
    relation: str = ""                # evidence | contradicts | uses | constrains | ...

    def __post_init__(self) -> None:
        super().__post_init__()
        if not (self.src and self.dst and self.relation):
            raise ValueError("link needs src, dst, relation")


KINDS: dict[str, type[Monad]] = {"link": Link}   # kinds register themselves here


class MonadStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def _load(self, row: dict) -> Monad:
        cls = KINDS.get(row.get("kind", ""), Monad)
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in row.items() if k in known})   # unknown fields ignored

    def all(self) -> list[Monad]:
        latest: dict[str, Monad] = {}
        with self.path.open(encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    m = self._load(json.loads(line))
                    latest[m.id] = m
        return list(latest.values())

    def add(self, m: Monad) -> Monad:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(m), ensure_ascii=False) + "\n")
        return m

    def get(self, id: str) -> Monad | None:
        return next((m for m in self.all() if m.id == id), None)

    def by_kind(self, kind: str) -> list[Monad]:
        return [m for m in self.all() if m.kind == kind]

    def current(self, source: str, kind: str | None = None) -> Monad | None:
        """Newest record with this provenance that nothing supersedes."""
        rows = [m for m in self.all() if m.source == source and (kind is None or m.kind == kind)]
        replaced = {m.supersedes for m in rows}
        live = [m for m in rows if m.id not in replaced]
        return max(live, key=lambda m: m.created) if live else None

    def links(self, id: str, relation: str | None = None) -> list[Link]:
        return [l for l in self.by_kind("link")                      # type: ignore[misc]
                if l.src == id and (relation is None or l.relation == relation)]
