"""CLI: recording an Engine judgment as a claim (`monad claim`)."""
import json
import pytest

from monad import cli


def test_claim_records_engine_judgment_with_provenance(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    assert cli.main(["claim", "DATA", "https://x.test/", "the page said A",
                     "--conf", "0.6", "--evidence", "abc123", "--tags", "extracted"]) == 0
    row = json.loads((tmp_path / "data" / "knowledge.jsonl").read_text(encoding="utf-8").splitlines()[-1])
    assert row["origin"] == "DATA" and row["source"] == "https://x.test/"
    assert row["text"] == "the page said A" and row["confidence"] == 0.6
    assert row["evidence"] == ["abc123"]
    assert "extracted" in row["tags"] and "engine:session" in row["tags"]


def test_claim_refuses_origin_outside_the_constitution(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    with pytest.raises(ValueError):
        cli.main(["claim", "TRUTH", "https://x.test/", "anything"])


def test_an_answered_unknown_stops_counting_as_unknown(tmp_path, monkeypatch):
    """A question is open until something answers it: the answering claim supersedes it."""
    from monad.knowledge import Claim, KnowledgeStore
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    ks = KnowledgeStore(tmp_path / "data" / "knowledge.jsonl")
    q = ks.add(Claim(text="unknown: is the file version 1.1?", origin="UNKNOWN", source="MANIFEST.md"))
    assert [c.id for c in ks.unknowns()] == [q.id]

    assert cli.main(["claim", "EMPIRICAL_RESULT", "measured", "6230 of 6236 ayat match",
                     "--supersedes", q.id]) == 0
    assert ks.unknowns() == []
    assert [c.id for c in ks.resolved_unknowns()] == [q.id]   # answering is progress, and counted
    assert ks.get(q.id) is not None          # append-only: the question is kept, not erased
