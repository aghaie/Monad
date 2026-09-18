# MONAD

بسم الله الرحمن الرحیم

A living, evolving engine for understanding the world, separating truth from claim, discovering real needs, building software, measuring its real effect, and improving. No version is final.

Founder: Ali Aghaei. Constitution: `MONAD_CONSTITUTION.md` (immutable core).

## Run
```
python3 -m pytest -q          # 20 tests (core + reading + observer + comparison + product)
python3 -m monad iterate      # one cycle of the creation loop + MONAD REPORT
python3 -m monad status | skills | contradictions
python3 -m monad read <url>                # اقرأ: read one web source → DATA claim with provenance
python3 -m monad quran 96:1 | quran search اقرأ   # verse-level REVELATION reference
python3 -m monad ingest [export.jsonl]     # real usage: Mizan «خروجی JSON» (default: newest in ~/Downloads) → knowledge store
python3 scripts/seed_skills.py
```
First product: `products/mizan/index.html` — open it in any browser (offline, no server). That file *is* the deployment (local, by founder decision). Press «خروجی JSON» now and then, run `python3 -m monad ingest`: that is how MONAD measures real use.

## Map
| File | What |
|---|---|
| MONAD_CONSTITUTION.md | 21 immutable articles, nine origin classes |
| MONAD_ARCHITECTURE.md | layers, modules, dependencies + alternatives |
| MONAD_ROADMAP.md | v0.1 done → v0.2 needs from Ali → v0.3/v0.4 |
| CAPABILITY_MAP.md | capability status + gap analysis |
| SKILL_REGISTRY.md | human mirror of `data/skills.jsonl` |
| monad/ | runtime: knowledge, skills, agents, factory, evaluation, core |
| data/*.jsonl | append-only memory (claims, skills, agents, products) |
| data/quran/ | Qur'an text (Tanzil) + manifest — origin REVELATION |
| data/sources.txt | World Observer sources: re-read every `iterate`, stored only when the text changes |
| reports/ | MONAD REPORTs and per-iteration JSON |
| products/ | real products, each with tests |

Git is memory: every commit records WHY / WHAT / EXPECTED BENEFIT / ACTUAL RESULT.
