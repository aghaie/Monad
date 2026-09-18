# CAPABILITY MAP & GAP ANALYSIS — Iteration 001

Legend: AVAILABLE = usable today in the builder session or the repo · PARTIAL = scaffold exists, not yet autonomous · GAP = missing · BLOCKED = needs authority/resources outside current access.

| Capability | Status | Where | Gap / next step |
|---|---|---|---|
| RESEARCH | AVAILABLE (builder session tools) / PARTIAL (in MONAD runtime) | WebSearch/WebFetch in session; `skills/research.md` spec | Runtime needs an Engine + HTTP ingestion skill |
| WEB_RESEARCH | PARTIAL → reading works (iteration 3) | `monad/web.py`, `monad read <url>` | search/discovery of URLs and evaluation of content need Engine |
| KNOWLEDGE_ACQUISITION | PARTIAL | `monad/knowledge/store.py` | ingestion pipeline from sources |
| SOURCE_EVALUATION | PARTIAL | claim `confidence` + `provenance` fields | scoring rubric skill |
| QURANIC_REASONING | PARTIAL | `monad/core/quran_engine.py` checklist + `monad/quran.py` verse layer (iteration 3) | explainable principle→verse link; must never force verses onto technical decisions |
| LOGICAL_REASONING | PARTIAL | origin-class separation in store | formal argument graphs |
| SCIENTIFIC_REASONING | PARTIAL | HYPOTHESIS → EMPIRICAL_RESULT flow | experiment records |
| SYSTEM_ANALYSIS | AVAILABLE (this document) | | automate |
| SOFTWARE_ARCHITECTURE | AVAILABLE | MONAD_ARCHITECTURE.md | |
| PRODUCT_DISCOVERY | PARTIAL | `monad/factory/software.py` scoring | World Observer feed |
| MARKET_RESEARCH / UX_RESEARCH | GAP | | needs real users + Engine |
| DESIGN | AVAILABLE (builder) | | |
| CODING / CODE_REVIEW / TESTING | AVAILABLE | pytest suite | |
| SECURITY | PARTIAL | no secrets stored; local-only data | threat model per product |
| DATA_ANALYSIS | AVAILABLE (Python) | | |
| AUTOMATION | PARTIAL | `python -m monad iterate` | scheduled trigger (needs Ali) |
| DEPLOYMENT | BLOCKED | no host/remote | Ali supplies host or git remote |
| MONITORING | GAP | | after deployment |
| DOCUMENTATION | AVAILABLE | this repo | |
| VERSION_CONTROL | AVAILABLE | git + origin github.com/aghaie/Monad (2026-09-18) | |
| SELF_EVALUATION | PARTIAL | evaluator + reports/; iteration N vs N-1 verdict in every report (2026-09-18) | fixed eval suite for code versions |
| SELF_IMPROVEMENT | PARTIAL | loop `improve_monad` step records candidates | automated candidate generation needs Engine |
| REPORTING | AVAILABLE | reports/REPORT_001.md | |
| SKILL_CREATION | PARTIAL | Skill Factory registry | auto-generation with tests |
| AGENT_CREATION | PARTIAL | Agent Factory | execution runtime |
| SOFTWARE_CREATION | AVAILABLE (first product built) | products/ | |

## Top gaps ranked by leverage
1. **Engine adapter wired to a real model** — unlocks autonomous research, skill generation, and product discovery inside the runtime (needs an API key: BLOCKED).
2. **Host** — git remote is connected (2026-09-18); a host (even GitHub Pages) is still needed for product 1 to reach real users (BLOCKED).
3. **World Observer ingestion** — the loop now re-reads `data/sources.txt` every iteration and records changes (2026-09-18); choosing *what* to read and judging it still needs an Engine.
4. **Real-user measurement** — follows from 2.
