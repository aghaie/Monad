# SKILL REGISTRY

Human-readable mirror of `data/skills.jsonl` (machine source of truth, managed by the Skill Factory). Every skill has: NAME · PURPOSE · INPUTS · OUTPUTS · TOOLS · DEPENDENCIES · LIMITATIONS · TESTS · EVALUATION · VERSION · CHANGELOG. Skills are composable; the Skill Factory can create skills that create skills.

| Name | Version | Purpose | Status |
|---|---|---|---|
| claim_classification | 1.0.0 | Assign one of the nine constitutional origin classes to a statement | ACTIVE, tested |
| contradiction_detection | 1.0.0 | Find claims in the store that contradict a new claim | ACTIVE, tested |
| constitutional_check | 1.0.0 | Run the Quranic Decision Engine checklist over a decision | ACTIVE, tested |
| candidate_evaluation | 1.0.0 | Compare candidate metrics vs baseline → DEPLOY/ROLLBACK/INCONCLUSIVE | ACTIVE, tested |
| product_scoring | 1.0.0 | Score a problem on 12 discovery dimensions | ACTIVE, tested |
| skill_creation | 1.0.0 | Register, version, and roll back skills (meta-skill) | ACTIVE, tested |
| web_research | 0.2.0 | Read a web source → DATA claim with provenance (url, sha256, time); records what it *said*, not that it is true | ACTIVE, tested (`monad/web.py`) — no search, no JS; evaluation with Engine later |
| quranic_reference | 0.2.0 | Verse-level citable reference: lookup sura:ayah / search term → REVELATION claims | ACTIVE, tested (`monad/quran.py`) — explaining a principle→verse link stays human/engine work |
| monad | 0.1.1 | Public Claude Code skill: improve any project one measured level at a time (observe→level→propose→execute→measure→report) | ACTIVE, tested (`tests/test_skill_monad.py`) — `skills/monad/SKILL.md`, install via symlink to ~/.claude/skills |

Template for a new skill: `skills/SKILL_TEMPLATE.md`. Register with `python -m monad skill add <spec.json>`.
