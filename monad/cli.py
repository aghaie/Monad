"""`python -m monad <command>`"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from monad.core.loop import MonadLoop, report
from monad.skills import SkillSpec

ROOT = Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    cmd = argv[0] if argv else "help"
    loop = MonadLoop(ROOT)
    if cmd == "iterate":
        print(report(loop.iterate()))
    elif cmd == "status":
        rec = loop.state.get("last")
        print(json.dumps(rec, ensure_ascii=False, indent=2) if rec else "no iteration yet")
    elif cmd == "skill" and len(argv) >= 3 and argv[1] == "add":
        spec = SkillSpec(**json.loads(Path(argv[2]).read_text(encoding="utf-8")))
        loop.skills.register(spec, why="cli", expected_benefit="see spec")
        print(f"registered {spec.name}@{spec.version}")
    elif cmd == "skills":
        for n in loop.skills.names():
            c = loop.skills.current(n)
            print(f"{n:28s} {c.version if c else '-':8s} {c.status if c else 'ROLLED_BACK'}")
    elif cmd == "read" and len(argv) >= 2:
        from monad.web import read_url
        c = read_url(loop.knowledge, argv[1])
        print(f"[{c.origin}] {c.text[:200]}\n   source={c.source} tags={c.tags[1:]}")
    elif cmd == "claim" and len(argv) >= 4:
        from monad.knowledge import Claim
        pos, flags, rest = [], {}, iter(argv[1:])
        for a in rest:
            if a.startswith("--"):
                flags[a[2:]] = next(rest, "")
            else:
                pos.append(a)
        c = loop.knowledge.add(Claim(
            text=" ".join(pos[2:]), origin=pos[0], source=pos[1],
            supersedes=flags.get("supersedes") or "",
            confidence=float(flags.get("conf") or 0.6),
            evidence=(flags.get("evidence") or "").split(",") if flags.get("evidence") else [],
            tags=((flags.get("tags") or "").split(",") if flags.get("tags") else []) + ["engine:session"]))
        print(f"{c.id} [{c.origin}] {c.text[:120]}")
    elif cmd == "quran" and len(argv) >= 2:
        from monad.quran import Quran
        q = Quran()
        hits = q.search(" ".join(argv[2:])) if argv[1] == "search" else [q.verse(*map(int, argv[1].split(":")))]
        for v in hits:
            print(f"{v.tags[1]:8s} {v.text}")
        print(f"-- {len(hits)} ayah(s), origin=REVELATION, source={q and 'tanzil:quran-simple'}")
    elif cmd == "ask" and len(argv) >= 2:
        from monad.core.engine import Pending
        try:
            print(f"[{loop.engine.name}] " + loop.engine.complete(" ".join(argv[1:])))
        except Pending as p:  # not known yet: recorded, not invented
            print(f"[{loop.engine.name}] {p}")
            return 1
    elif cmd == "qa":
        for q in loop.engine.pending():
            print(f"{q['id']}  {q['prompt'][:160]}")
    elif cmd == "answer" and len(argv) >= 3:
        from monad.core.engine import answer as record
        if not hasattr(loop.engine, "path"):
            print(f"engine {loop.engine.name} does not queue questions")
            return 1
        record(loop.engine.path, argv[1], " ".join(argv[2:]))
        print(f"answered {argv[1]}")
    elif cmd == "serve":
        from monad.serve import serve
        serve(ROOT, int(argv[1]) if len(argv) >= 2 else 8765)
    elif cmd == "ingest":
        from monad.usage import ingest, newest_export, usage
        path = Path(argv[1]) if len(argv) >= 2 else newest_export()
        if not path or not path.exists():
            print("no export found: in Mizan press «خروجی JSON», then run: python3 -m monad ingest [file]")
            return 1
        print(f"ingested {ingest(loop.knowledge, path)} new claim(s) from {path}\nusage: {usage(loop.knowledge)}")
    elif cmd == "monads":
        kind = argv[1] if len(argv) >= 2 else None
        for m in loop.monads.all():
            if kind is None or m.kind == kind:
                print(f"{m.id}  {m.kind:8s} [{m.origin}] {m.source}" + (f"  ⇐ {m.supersedes}" if m.supersedes else ""))
    elif cmd == "contradictions":
        for a, b in loop.knowledge.contradictions():
            print(f"[{a.origin}] {a.text}\n   ⟂ [{b.origin}] {b.text}")
    else:
        print("usage: python -m monad iterate | status | skills | contradictions | read <url> | claim <ORIGIN> <source> <text> [--conf c --evidence id,id --tags a,b --supersedes id] | quran <sura:ayah> | quran search <term> | ask <prompt> | qa | answer <id> <text> | serve [port] | ingest [export.jsonl] | monads [kind] | skill add <spec.json>")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
