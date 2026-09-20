"""Kind `report`: every Markdown report/analysis MONAD produces is itself a Monad.
Registration is idempotent (path + sha256); an edited file yields a new record that
supersedes the old one — nothing is overwritten (Articles 12–14)."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from monad.core.monad import Monad, MonadStore, KINDS

DIRS = ("reports", "docs")


@dataclass
class Report(Monad):
    kind: str = "report"
    origin: str = "RATIONAL_ANALYSIS"
    title: str = ""
    sha256: str = ""
    bytes: int = 0


KINDS["report"] = Report


def _title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return fallback


def register_reports(store: MonadStore, root: str | Path, dirs=DIRS) -> list[Report]:
    root = Path(root)
    new: list[Report] = []
    for d in dirs:
        for f in sorted((root / d).glob("*.md")):
            raw = f.read_bytes()
            sha = hashlib.sha256(raw).hexdigest()
            rel = f.relative_to(root).as_posix()
            cur = store.current(rel, "report")
            if cur is not None and cur.sha256 == sha:      # type: ignore[attr-defined]
                continue
            r = Report(source=rel, title=_title(raw.decode("utf-8", "replace"), f.stem),
                       sha256=sha, bytes=len(raw), supersedes=cur.id if cur else "")
            new.append(store.add(r))                          # type: ignore[arg-type]
    return new
