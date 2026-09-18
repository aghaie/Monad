"""The public `/monad` skill: frontmatter valid, every stage of the cycle present, install path documented."""
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / "skills" / "monad" / "SKILL.md"


def test_monad_skill_is_complete():
    text = SKILL.read_text(encoding="utf-8")
    head, body = text.split("---\n")[1:3]
    assert "name: monad" in head and head.strip().split("description:")[1].strip().startswith("Use when")
    assert len(head) <= 1024
    for stage in ("OBSERVE", "LEVEL", "PROPOSE", "EXECUTE", "MEASURE", "REPORT"):
        assert f"— {stage}" in body, stage
    for verdict in ("DEPLOY", "ROLLBACK", "INCONCLUSIVE"):
        assert verdict in body
    assert "<out>/PROPOSAL-<YYYY-MM-DD>.md" in body and "<out>/REPORT-<YYYY-MM-DD>.md" in body
    assert "gitignored" in body and "production" in body  # files must survive; never touch prod
    assert "/monad" in (SKILL.parent.parent.parent / "README.md").read_text(encoding="utf-8")
