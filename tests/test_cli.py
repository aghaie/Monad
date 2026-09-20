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
