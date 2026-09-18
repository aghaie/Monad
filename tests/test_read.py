"""Tests for the two reading skills: web_research (monad.web) and quranic_reference (monad.quran)."""
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
