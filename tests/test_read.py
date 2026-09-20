"""Tests for the two reading skills: web_research (monad.web) and quranic_reference (monad.quran)."""
import pytest

from monad.knowledge import KnowledgeStore
from monad.web import html_to_text, read_url
from monad.quran import Quran, strip_marks


def test_html_to_text_drops_scripts_and_keeps_title():
    title, text = html_to_text("<html><head><title> T </title><script>x=1</script></head>"
                               "<body><p>سلام</p>\n<p>world</p></body></html>")
    assert title == "T" and text == "سلام world"


def test_read_url_records_provenance_not_truth(tmp_path):
    ks = KnowledgeStore(tmp_path / "k.jsonl")
    c = read_url(ks, "https://example.test/a", fetcher=lambda u: b"<title>A</title><p>The sky is green</p>")
    assert c.origin == "DATA" and c.source == "https://example.test/a"
    assert c.text.startswith("A said: The sky is green")
    assert any(t.startswith("sha256:") for t in c.tags)
    assert c.is_stale() is False and c.expires_days == 30
    assert ks.get(c.id) is not None


def test_quran_iqra():
    q = Quran()
    v = q.verse(96, 1)
    assert v.origin == "REVELATION" and v.source == "tanzil:quran-simple#96:1"
    assert "اقرأ" in strip_marks(v.text)
    assert len(q.ayat) == 6236
    hits = q.search("اقرأ")
    assert (96, 1) in {tuple(map(int, h.tags[1].split(":"))) for h in hits}
    assert q.search("zzz-not-in-quran") == []


def test_loop_reads_sources_only_when_changed(tmp_path, monkeypatch):
    from monad.core import loop as L
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "sources.txt").write_text("# comment\nhttps://a.test/\nhttps://down.test/\n")
    pages = {"https://a.test/": b"<p>v1</p>"}

    def fake(url):
        if url not in pages:
            raise OSError("unreachable")
        return pages[url]
    monkeypatch.setattr(L, "fetch", fake)
    r1 = L.MonadLoop(tmp_path).iterate()
    assert r1.observations["sources"]["https://a.test/"] == "new"
    assert any("down.test" in b for b in r1.blocked)
    r2 = L.MonadLoop(tmp_path).iterate()
    assert r2.observations["sources"]["https://a.test/"] == "unchanged"
    pages["https://a.test/"] = b"<p>v2</p>"
    r3 = L.MonadLoop(tmp_path).iterate()
    assert r3.observations["sources"]["https://a.test/"] == "changed"
    ks = L.MonadLoop(tmp_path).knowledge
    assert len([c for c in ks.all() if c.source == "https://a.test/"]) == 2  # v1 + v2, no duplicate for unchanged


def test_loop_marks_stale_claims(tmp_path):
    from monad.core.loop import MonadLoop
    from monad.knowledge import Claim
    loop = MonadLoop(tmp_path)
    c = loop.knowledge.add(Claim(text="old price", origin="DATA", source="s", expires_days=1,
                                 created="2020-01-01T00:00:00+00:00"))
    r = loop.iterate()
    assert r.stale_claims == 1 and loop.knowledge.get(c.id).status == "STALE"


def test_loop_compares_with_previous_iteration(tmp_path, monkeypatch):
    from monad.core import loop as L
    monkeypatch.setattr(L, "fetch", lambda u: b"<p>x</p>")
    r1 = L.MonadLoop(tmp_path).iterate()
    assert r1.improvement["verdict"] == "INCONCLUSIVE"  # nothing to compare against
    (tmp_path / "data" / "sources.txt").write_text("https://a.test/\n")
    r2 = L.MonadLoop(tmp_path).iterate()
    assert r2.improvement["verdict"] == "DEPLOY" and r2.improvement["deltas"] == {"sources_read": 1}
    r3 = L.MonadLoop(tmp_path).iterate()
    assert r3.improvement["verdict"] == "INCONCLUSIVE"  # same as before: no fake progress


def test_lmstudio_engine_and_judge_step(tmp_path, monkeypatch):
    import io, json
    from monad.core import engine as E, loop as L

    class FakeResp(io.BytesIO):
        def __enter__(self): return self
        def __exit__(self, *a): pass
    reply = json.dumps({"choices": [{"message": {"content": '["The sky is blue", "Water is wet"]'}}]}).encode()
    monkeypatch.setattr(E.urllib.request, "urlopen", lambda req, timeout=0: FakeResp(reply))
    eng = E.LMStudioEngine(url="http://x/v1", model="m")
    assert eng.complete("hi") == '["The sky is blue", "Water is wet"]'

    monkeypatch.setenv("MONAD_ENGINE", "lmstudio")
    monkeypatch.setattr(L, "fetch", lambda u: b"<p>page</p>")
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "sources.txt").write_text("https://a.test/\n")
    r = L.MonadLoop(tmp_path).iterate()
    assert r.engine == "lmstudio" and not [b for b in r.blocked if "no reasoning engine" in b]
    extracted = [c for c in L.MonadLoop(tmp_path).knowledge.all() if "extracted" in c.tags]
    assert [c.text for c in extracted] == ["https://a.test/ states: The sky is blue", "https://a.test/ states: Water is wet"]
    assert all(c.confidence == 0.6 and c.evidence for c in extracted)


# ---- Usage measurement (Article 20) -----------------------------------------
def test_ingest_is_idempotent_and_measured(tmp_path):
    from monad.knowledge import KnowledgeStore
    from monad.usage import ingest, usage
    ks = KnowledgeStore(tmp_path / "k.jsonl")
    assert usage(ks) == {"claims": 0}  # no export → no invented usage
    export = tmp_path / "mizan-knowledge.jsonl"
    export.write_text('{"id":"a1","text":"این ابزار مفید است","origin":"HYPOTHESIS","confidence":0.5,"source":"علی","evidence":[],"contradicts":[],"tags":[],"status":"OPEN","created":"2026-09-01T00:00:00.000Z","expires_days":null}\n'
                      '{"id":"b2","text":"این ابزار مفید نیست","origin":"EMPIRICAL_RESULT","confidence":0.7,"source":"نظرسنجی","evidence":[],"contradicts":[],"tags":[],"status":"OPEN","created":"2026-09-02T00:00:00.000Z","expires_days":null}\n')
    assert ingest(ks, export) == 2
    assert ingest(ks, export) == 0
    u = usage(ks)
    assert u["claims"] == 2 and u["with_source_pct"] == 100 and u["contradictions"] == 1 and u["per_week"] > 0
    assert "usage:mizan" in ks.get("a1").tags


def test_serve_sync_snapshots_and_ingests(tmp_path):
    import json, threading, urllib.request
    from monad.serve import make_server
    (tmp_path / "products" / "mizan").mkdir(parents=True)
    (tmp_path / "products" / "mizan" / "index.html").write_text("<h1>mizan</h1>")
    srv = make_server(tmp_path, 0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        base = f"http://127.0.0.1:{srv.server_port}"
        get = urllib.request.build_opener(urllib.request.ProxyHandler({})).open  # macOS system proxy must not swallow loopback
        assert b"mizan" in get(base + "/").read()
        rows = [{"id": "q1", "text": "x", "origin": "UNKNOWN", "confidence": 0.1, "source": "", "evidence": [],
                 "contradicts": [], "tags": [], "status": "OPEN", "created": "2026-09-18T00:00:00.000Z", "expires_days": None}]
        req = urllib.request.Request(base + "/sync", data=json.dumps(rows).encode(), method="POST")
        out = json.load(get(req))
        assert out["ingested"] == 1 and out["claims"] == 1
        assert json.load(get(req))["ingested"] == 0  # idempotent
        assert (tmp_path / "data" / "usage" / "mizan.jsonl").read_text().count("\n") == 1
    finally:
        srv.shutdown()


def test_session_engine_asks_then_remembers(tmp_path, monkeypatch):
    """The reasoning engine can be the session at this terminal: no provider, no API key."""
    from monad.core import engine as E, loop as L

    qa = tmp_path / "engine_qa.jsonl"
    with pytest.raises(E.Pending) as ex:  # nothing known yet → say so, never invent
        E.SessionEngine(qa).complete("۲+۲ چند است؟")
    qid = ex.value.id
    assert E.SessionEngine(qa).pending()[0]["id"] == qid

    E.answer(qa, qid, "۴")
    assert E.SessionEngine(qa).complete("۲+۲ چند است؟") == "۴"   # fresh instance: read from disk
    assert E.SessionEngine(qa).pending() == []

    monkeypatch.setenv("MONAD_ENGINE", "session")
    monkeypatch.setenv("MONAD_QA", str(qa))
    (tmp_path / "data").mkdir()
    r = L.MonadLoop(tmp_path).iterate()
    assert r.engine == "session" and not [b for b in r.blocked if "no reasoning engine" in b]
