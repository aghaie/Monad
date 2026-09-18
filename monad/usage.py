"""Real usage measurement (Article 20) — local, no server.

A product's users export its data (Mizan: `mizan-knowledge.jsonl` from the browser);
`monad ingest` pulls that file into the knowledge store tagged `usage:<name>`, and the
loop turns those claims into usage numbers. Nothing here invents usage: no export → 0.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json

from monad.knowledge import Claim, KnowledgeStore

DOWNLOADS = Path.home() / "Downloads"


def newest_export(folder: Path = DOWNLOADS, pattern: str = "mizan-knowledge*.jsonl") -> Path | None:
    files = sorted(folder.glob(pattern), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def ingest(store: KnowledgeStore, path: Path, product: str = "mizan") -> int:
    """Append claims from a product export; ids already in the store are skipped (append-only, idempotent)."""
    text = path.read_text(encoding="utf-8").strip()
    rows = json.loads(text) if text.startswith("[") else [json.loads(l) for l in text.splitlines() if l.strip()]
    known = {c.id for c in store.all()}
    tag, n = f"usage:{product}", 0  # not product:<name>: that tag marks claims ABOUT the product
    for r in rows:
        if r.get("id") in known:
            continue
        r["tags"] = list(dict.fromkeys(r.get("tags", []) + [tag]))
        r["created"] = r.get("created", "").replace("Z", "+00:00")  # browser toISOString → Python isoformat
        store.add(Claim(**r))
        n += 1
    return n


def usage(store: KnowledgeStore, product: str = "mizan") -> dict:
    """What real users actually did: claims logged, share with a source, contradictions, rate per week."""
    tag = f"usage:{product}"
    rows = [c for c in store.all() if tag in c.tags]
    if not rows:
        return {"claims": 0}
    ids = {c.id for c in rows}
    pairs = {tuple(sorted((c.id, o))) for c in rows for o in c.contradicts if o in ids}
    first = min(datetime.fromisoformat(c.created) for c in rows)
    days = max((datetime.now(timezone.utc) - first.astimezone(timezone.utc)).days, 1)
    return {"claims": len(rows), "with_source_pct": round(100 * sum(1 for c in rows if c.source) / len(rows)),
            "contradictions": len(pairs), "per_week": round(len(rows) * 7 / days, 2), "since": first.date().isoformat()}
