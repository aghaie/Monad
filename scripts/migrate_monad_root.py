"""One-time, idempotent migration: bring data/skills|agents|products.jsonl under the Monad root.
recorded→created · add kind/origin · one stable id per logical record (name[@version]).
Rewriting a store is the sole exception to append-only, and it is recorded in git (Article 12).
Usage: python scripts/migrate_monad_root.py [repo root]"""
import json
import sys
import uuid
from pathlib import Path

STORES = (("skills.jsonl", "skill", ("name", "version")),
          ("agents.jsonl", "agent", ("name",)),
          ("products.jsonl", "product", ("name",)))


def migrate(root: Path) -> dict[str, int]:
    changed = {}
    for fname, kind, key in STORES:
        path = root / "data" / fname
        if not path.exists():
            continue
        rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        ids: dict[tuple, str] = {}
        n = 0
        for r in rows:
            before = dict(r)
            if "recorded" in r:
                r["created"] = r.pop("recorded")
            r.setdefault("kind", kind)
            r.setdefault("origin", "ENGINEERING_DECISION")
            k = tuple(r[x] for x in key)
            ids.setdefault(k, r.get("id") or uuid.uuid4().hex[:12])
            r.setdefault("id", ids[k])
            n += r != before
        if n:
            path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
        changed[fname] = n
    return changed


if __name__ == "__main__":
    print(migrate(Path(sys.argv[1] if len(sys.argv) > 1 else ".")))
