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
