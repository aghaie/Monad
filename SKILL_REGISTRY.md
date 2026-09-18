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
| web_research | 0.1.0 | Ingest and evaluate web sources | SPEC ONLY — needs Engine + ingestion |
| quranic_reference | 0.1.0 | Explainable link from a principle to a Qur'anic basis | SPEC ONLY — must be explainable, never forced |

Template for a new skill: `skills/SKILL_TEMPLATE.md`. Register with `python -m monad skill add <spec.json>`.
