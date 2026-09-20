# MONAD ARCHITECTURE

Version 0.1 (never "final"). Origin: ENGINEERING_DECISION unless marked.

## Design goals
Model-agnostic · provider-agnostic · self-hostable · portable · versioned · auditable · reversible · small first, powerful later, never merely bigger.

## Layered view

```
┌──────────────────────────────────────────────────────────────┐
│  INTERFACES   CLI (now) · Web/API (next) · Desktop/Mobile/    │
│               Telegram/Distributed agents (later)             │
├──────────────────────────────────────────────────────────────┤
│  CORE LOOP    observe → understand → question → research →    │
│               discover → design → build → test → release →    │
│               measure → learn → improve → repeat              │
├──────────────┬──────────────┬──────────────┬─────────────────┤
│ WORLD        │ PRODUCT      │ IMPROVEMENT  │ QURANIC         │
│ OBSERVER     │ DISCOVERY    │ ENGINE       │ DECISION ENGINE │
├──────────────┴──────────────┴──────────────┴─────────────────┤
│  FACTORIES    Skill Factory · Agent Factory · Software Factory │
├──────────────────────────────────────────────────────────────┤
│  KNOWLEDGE ENGINE   claims · origin class · evidence · links · │
│                     confidence · contradictions · provenance   │
├──────────────────────────────────────────────────────────────┤
│  EVALUATION ENGINE  metrics · candidate vs baseline · verdict  │
├──────────────────────────────────────────────────────────────┤
│  ENGINE ADAPTERS    SessionEngine (no provider) · NullEngine · │
│                     (LM Studio | Anthropic | OpenAI | local)  │
├──────────────────────────────────────────────────────────────┤
│  MEMORY             git (history) · JSONL stores · reports     │
└──────────────────────────────────────────────────────────────┘
```

## Modules (Python package `monad/`)

| Module | Responsibility | Status |
|---|---|---|
| `monad/knowledge/store.py` | Knowledge Engine: append-only JSONL claim store with origin class, evidence links, confidence, contradiction detection, staleness | RUNNING, tested |
| `monad/skills/registry.py` | Skill Factory: skill spec (name, purpose, inputs, outputs, tools, dependencies, limitations, tests, evaluation, version, changelog), register/version/rollback | RUNNING, tested |
| `monad/agents/factory.py` | Agent Factory: agent spec bound to skills and constitutional constraints; necessity check | RUNNING, tested |
| `monad/factory/software.py` | Software Factory: product pipeline record (problem → requirements → … → observation) with WHY/WHO/PROBLEM/SOLUTION/MEASUREMENT | RUNNING, tested |
| `monad/evaluation/evaluator.py` | Evaluation Engine: compare candidate metrics vs baseline; verdict DEPLOY / ROLLBACK / INCONCLUSIVE | RUNNING, tested |
| `monad/core/quran_engine.py` | Quranic Decision Engine: constitutional checklist for significant decisions, returns VALID / INVALID / UNVERIFIED with reasons | RUNNING, tested |
| `monad/core/loop.py` | Global Creation Loop: one iteration = observe → read sources → … → compare with previous iteration (Article 14, via Evaluation Engine) → report, with state persisted | RUNNING, tested |
| `monad/core/engine.py` | Engine adapters: NullEngine · SessionEngine (the terminal itself reasons; Q&A in `data/engine_qa.jsonl`, pending questions reported, never invented) · LMStudioEngine | RUNNING, tested |
| `monad/web.py` | World Observer v0.2: read one URL (stdlib), store DATA claim with url + text-sha256 + staleness; loop re-reads `data/sources.txt` and stores only changes | RUNNING, tested |
| `monad/quran.py` | Qur'anic reference layer: Tanzil text → REVELATION claims by sura:ayah, term search | RUNNING, tested |
| `monad/cli.py` | `python -m monad …` | RUNNING |

## Dependencies and alternatives (Article: provider-agnostic)
| Dependency | Role | Alternatives recorded |
|---|---|---|
| Python 3 stdlib | runtime | Node/TypeScript port possible later |
| git | memory/rollback | none needed — git is itself the portable standard |
| LLM engine (optional) | reasoning *acceleration*, never identity | session (default, no provider), Anthropic, OpenAI, Gemini, local (llama.cpp/Ollama). All behind `Engine` interface |
| pytest | testing | stdlib unittest |

## Data
Everything is plain JSONL/Markdown in the repo: readable by a human, diffable by git, portable to any host.

## Evolution path
CLI (v0.1) → local web app (Flask already available) → API → self-hosted runtime with scheduled iterations → Telegram interface (existing skill of the founder) → distributed agents.
