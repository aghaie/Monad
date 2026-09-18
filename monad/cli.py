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
    elif cmd == "quran" and len(argv) >= 2:
        from monad.quran import Quran
        q = Quran()
        hits = q.search(" ".join(argv[2:])) if argv[1] == "search" else [q.verse(*map(int, argv[1].split(":")))]
        for v in hits:
            print(f"{v.tags[1]:8s} {v.text}")
        print(f"-- {len(hits)} ayah(s), origin=REVELATION, source={q and 'tanzil:quran-simple'}")
    elif cmd == "contradictions":
        for a, b in loop.knowledge.contradictions():
            print(f"[{a.origin}] {a.text}\n   ⟂ [{b.origin}] {b.text}")
    else:
        print("usage: python -m monad iterate | status | skills | contradictions | read <url> | quran <sura:ayah> | quran search <term> | skill add <spec.json>")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
