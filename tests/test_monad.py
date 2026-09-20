"""Root entity: every stored thing is a Monad (id, kind, origin, created, status, source, supersedes)."""
import pytest

from monad.core.monad import Monad, Link, MonadStore
from monad.reports import Report, register_reports


def test_monad_root_enforces_origin_class():
    with pytest.raises(ValueError):
        Monad(kind="x", origin="TRUTH")
    m = Monad(kind="x", origin="ENGINEERING_DECISION")
    assert m.id and m.created and m.status == "OPEN" and m.supersedes == "" and m.schema == 1


def test_store_is_append_only_latest_wins_and_tolerates_unknown_fields(tmp_path):
    s = MonadStore(tmp_path / "m.jsonl")
    a = s.add(Monad(kind="x", origin="DATA", source="t"))
    s.add(Monad(kind="x", origin="DATA", source="t", id=a.id, status="STALE"))
    assert [m.status for m in s.all()] == ["STALE"]          # same id → one record, last wins
    with s.path.open("a") as fh:                              # a future field must not break old readers
        fh.write('{"id":"zz","kind":"x","origin":"DATA","source":"t","future_field":1}\n')
    assert {m.id for m in s.all()} == {a.id, "zz"}
    s.add(Link(origin="ENGINEERING_DECISION", source="t", src=a.id, dst="zz", relation="evidence"))
    assert [l.dst for l in s.links(a.id)] == ["zz"]
    assert len(s.by_kind("link")) == 1 and len(s.by_kind("x")) == 2


def test_reports_become_monads_idempotently_and_supersede_on_change(tmp_path):
    (tmp_path / "reports").mkdir()
    f = tmp_path / "reports" / "REPORT_001.md"
    f.write_text("# First report\nbody\n", encoding="utf-8")
    s = MonadStore(tmp_path / "data" / "monads.jsonl")
    new = register_reports(s, tmp_path)
    assert [r.title for r in new] == ["First report"] and new[0].kind == "report"
    assert new[0].source == "reports/REPORT_001.md" and new[0].origin == "RATIONAL_ANALYSIS"
    assert register_reports(s, tmp_path) == []                # unchanged → nothing new
    f.write_text("# First report (edited)\n", encoding="utf-8")
    v2 = register_reports(s, tmp_path)
    assert len(v2) == 1 and v2[0].supersedes == new[0].id     # change → new record, old one kept
    assert len(s.by_kind("report")) == 2 and s.current("reports/REPORT_001.md").id == v2[0].id


def test_claim_is_a_monad_and_old_rows_still_load(tmp_path):
    from monad.knowledge import Claim, KnowledgeStore
    c = Claim(text="x", origin="DATA", source="t")
    assert isinstance(c, Monad) and c.kind == "claim" and c.supersedes == "" and c.schema == 1
    ks = KnowledgeStore(tmp_path / "k.jsonl")
    with ks.path.open("a") as fh:                 # a row written before the root existed
        fh.write('{"text":"old","origin":"DATA","source":"t","id":"old1","created":"2026-01-01T00:00:00+00:00"}\n')
    old = ks.get("old1")
    assert old.kind == "claim" and old.text == "old" and old.created.startswith("2026-01-01")
    assert ks.get(ks.add(c).id).text == "x"
