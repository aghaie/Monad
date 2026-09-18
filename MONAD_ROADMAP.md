# MONAD ROADMAP

No version is final. Each is a stage.

## v0.1 — Genesis (this iteration)
- [x] Environment report, repository, git as memory
- [x] Constitution, Architecture, Roadmap, Capability Map + Gap Analysis, Skill Registry
- [x] Knowledge Engine (claim store with origin classes, contradictions, provenance)
- [x] Skill Factory, Agent Factory, Software Factory scaffolds with versioning + rollback
- [x] Evaluation Engine (candidate vs baseline, DEPLOY/ROLLBACK verdict)
- [x] Quranic Decision Engine (constitutional check → VALID / INVALID / UNVERIFIED)
- [x] Core Loop runnable end-to-end with persisted state
- [x] First product discovered, built, tested (see products/)
- [x] MONAD REPORT 001

## v0.2 — First real users
- [ ] BLOCKED→needs Ali: git remote (GitHub) so history leaves the sandbox
- [ ] BLOCKED→needs Ali: a host (VPS / Cloudflare / Vercel) for public release of product 1
- [ ] Wire a real Engine adapter (needs an API key from Ali) — provider-agnostic interface already exists
- [ ] Web UI (Flask) for the first product, Persian RTL
- [ ] Real usage measurement hooks → feed back into Knowledge Engine
- [ ] Scheduled iterations (Ali can create a scheduled task that re-runs `python -m monad iterate`)

## v0.3 — World Observer
- [x] 2026-09-18: first reading (اقرأ) — `monad read <url>` (web_research 0.2.0) and `monad quran` (quranic_reference 0.2.0), engine-free
- [ ] Source ingestion (web, GitHub, papers) with SOURCE_EVALUATION skill — evaluation part still needs Engine
- [ ] Automated need/opportunity discovery scoring (Human Need, Truth, Utility, Impact, Feasibility, Cost, Risk, Reach, Urgency)
- [ ] Contradiction and staleness sweeps over the knowledge store

## v0.4 — Self-improvement under measurement
- [ ] Skill Factory creates skills from capability gaps automatically, with generated tests
- [ ] Agent Factory spawns specialised agents (Research, Coding, Testing, Security) under constitution
- [ ] A/B comparison of MONAD versions on a fixed evaluation suite

## Later
Telegram interface · API · desktop · local AI runtime · distributed agents · robotics interface
