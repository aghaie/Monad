"""Browser tests for Mizan (Playwright + Chromium). Verifies the constitutional rules
hold in the product: provenance required, contradictions surfaced, export = store schema."""
import json
from pathlib import Path

import pytest

pw = pytest.importorskip("playwright.sync_api")
from monad.knowledge import Claim  # noqa: E402

HTML = (Path(__file__).parent / "index.html").resolve().as_uri()


@pytest.fixture(scope="module")
def page():
    with pw.sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(HTML)
        yield pg
        b.close()


def test_provenance_required(page):
    page.evaluate("mizan.reset()")
    err = page.evaluate("""() => { try { mizan.makeClaim('x','DATA','',0.5,'',[]); return '' } catch(e){ return e.message } }""")
    assert "provenance" in err
    page.evaluate("mizan.addClaim(mizan.makeClaim('چیزی نمی‌دانم','UNKNOWN','',0.1,'',[]))")
    assert page.evaluate("mizan.stats().unknown") == 1


def test_contradictions_surface(page):
    page.evaluate("mizan.reset()")
    page.fill("#text", "این ابزار مفید است"); page.select_option("#originSel", "HYPOTHESIS"); page.fill("#source", "علی")
    page.click("button[type=submit]")
    page.fill("#text", "این ابزار مفید نیست"); page.select_option("#originSel", "EMPIRICAL_RESULT"); page.fill("#source", "نظرسنجی-۱")
    page.click("button[type=submit]")
    assert page.evaluate("mizan.stats()") == {"n": 2, "srcPct": 100, "contradictions": 1, "unknown": 0}
    assert page.locator(".tag.c").count() == 2


def test_export_matches_monad_store_schema(page):
    rows = page.evaluate("mizan.claims")
    for r in rows:
        Claim(**r)  # raises if incompatible with monad.knowledge.Claim
    assert json.dumps(rows, ensure_ascii=False)
