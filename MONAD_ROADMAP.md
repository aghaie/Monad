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
- [x] 2026-09-18: git remote https://github.com/aghaie/Monad.git — history now lives outside the sandbox
- [x] 2026-09-18: founder decision — no online host; product 1 is deployed as a local file (Pages workflow removed)
- [ ] Wire a real Engine adapter (needs an API key from Ali) — provider-agnostic interface already exists
- [x] 2026-09-18: `monad serve` (stdlib http.server, no Flask) — Mizan on localhost with zero-step usage sync (`POST /sync`); verified end-to-end in Chromium
- [x] 2026-09-18: usage hook — Mizan export → `python3 -m monad ingest` → claims tagged `usage:mizan` → `usage` in every iteration + `usage_claims` metric (0 until Ali exports for real)
- [ ] Scheduled iterations (Ali can create a scheduled task that re-runs `python -m monad iterate`)

## v0.3 — World Observer
- [x] 2026-09-18: first reading (اقرأ) — `monad read <url>` (web_research 0.2.0) and `monad quran` (quranic_reference 0.2.0), engine-free
- [x] 2026-09-18: World Observer v0.2 — `data/sources.txt` re-read each iteration; new/changed/unchanged by text hash; failures recorded as BLOCKED
- [ ] Source ingestion (GitHub, papers) with SOURCE_EVALUATION skill — evaluation part still needs Engine
- [ ] Automated need/opportunity discovery scoring (Human Need, Truth, Utility, Impact, Feasibility, Cost, Risk, Reach, Urgency)
- [ ] Contradiction and staleness sweeps over the knowledge store

## v0.4 — Self-improvement under measurement
- [x] 2026-09-18: `/monad` public skill (skills/monad/SKILL.md) — MONAD's cycle applied to any external project; RED/GREEN tested on a fixture project
- [ ] Skill Factory creates skills from capability gaps automatically, with generated tests
- [ ] Agent Factory spawns specialised agents (Research, Coding, Testing, Security) under constitution
- [x] 2026-09-18: every iteration is scored against the previous one (7 metrics, DEPLOY/ROLLBACK/INCONCLUSIVE) — report section 4 is no longer empty
- [ ] A/B comparison of MONAD *code* versions on a fixed evaluation suite

## Later
Telegram interface · API · desktop · local AI runtime · distributed agents · robotics interface
