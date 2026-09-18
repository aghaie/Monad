"""web_research skill v0.2 — MONAD's first act of reading the world (اقرأ).

Engine-free: fetches a URL with the stdlib, strips it to text, and stores what the
source *said* as a DATA claim with full provenance (url, sha256, fetch time).
It never asserts that the content is true — that is a later, evidence-based step.
"""
from __future__ import annotations

import hashlib
import re
import urllib.request
from html.parser import HTMLParser
from typing import Callable

from monad.knowledge import Claim, KnowledgeStore

USER_AGENT = "MONAD/0.2 (+reading the world; contact: repo owner)"


class _Text(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg"}

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip = 0
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip += 1
        self._in_title = tag == "title"

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skip:
            self._skip -= 1
        self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif not self._skip:
            self.parts.append(data)


def html_to_text(html: str) -> tuple[str, str]:
    """Return (title, text) with whitespace collapsed."""
    p = _Text()
    p.feed(html)
    text = re.sub(r"\s+", " ", " ".join(p.parts)).strip()
    return p.title.strip(), text


def fetch(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 — caller supplies URL
        return r.read()


def read_url(store: KnowledgeStore, url: str, *, fetcher: Callable[[str], bytes] = fetch,
             excerpt_chars: int = 500, expires_days: int = 30) -> Claim:
    """Read one source and record it. The claim text is what the source said (excerpt);
    origin DATA; confidence 1.0 means "this is really what the URL returned", not "it is true"."""
    raw = fetcher(url)
    title, text = html_to_text(raw.decode("utf-8", errors="replace"))
    digest = hashlib.sha256(raw).hexdigest()
    return store.add(Claim(
        text=f"{title or url} said: {text[:excerpt_chars]}",
        origin="DATA", confidence=1.0, source=url,
        tags=["web_research", f"sha256:{digest}", f"chars:{len(text)}"],
        expires_days=expires_days))
