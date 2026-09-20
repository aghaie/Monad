# MONAD

بسم الله الرحمن الرحیم

A living, evolving engine for understanding the world, separating truth from claim, discovering real needs, building software, measuring its real effect, and improving. No version is final.

Founder: Ali Aghaei. Constitution: `MONAD_CONSTITUTION.md` (immutable core).

## Run
```
python3 -m pytest -q          # 26 tests (core + reading + observer + comparison + product + root entity)
python3 -m monad iterate      # one cycle of the creation loop + MONAD REPORT
python3 -m monad status | skills | contradictions
python3 -m monad read <url>                # اقرأ: read one web source → DATA claim with provenance
python3 -m monad quran 96:1 | quran search اقرأ   # verse-level REVELATION reference
python3 -m monad serve                     # Mizan at http://127.0.0.1:8765 — every change syncs into data/ (real usage, zero steps)
python3 -m monad ingest [export.jsonl]     # fallback when opened as file://: Mizan «خروجی JSON» (default: newest in ~/Downloads)
python3 scripts/seed_skills.py
```
## `/monad` — the public skill
`skills/monad/SKILL.md` turns any Claude Code session into a MONAD improver for *any* project: observe → level (L0–L5) → propose one step → execute → measure → report, with FACT/HYPOTHESIS/UNKNOWN labels and DEPLOY/ROLLBACK verdicts. Install:
```
ln -s "$(pwd)/skills/monad" ~/.claude/skills/monad     # then: /monad <project path>   (or: /monad <path> propose only)
```
Tested TDD-style: the same fixture project was improved by an agent without the skill (bundled six fixes, no baseline, no proposal, no report file) and with it (reproduced defects first, L1→L2 in one measured step, proposal + report files, WHY/WHAT/EXPECTED/ACTUAL commit).

First product: `products/mizan/index.html` — open it in any browser (offline, no server). That file *is* the deployment (local, by founder decision). Easiest: `python3 -m monad serve` and open http://127.0.0.1:8765 — every claim you log lands in `data/usage/mizan.jsonl` and the knowledge store (tag `usage:mizan`). That is how MONAD measures real use.

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
