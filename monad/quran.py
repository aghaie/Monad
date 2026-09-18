"""quranic_reference skill v0.2 — verse-level, citable reference layer.

Reads the Qur'an text (data/quran/quran-simple.csv, Tanzil) and returns REVELATION
claims with exact provenance (sura:ayah). Lookup and term search only; *explaining*
a link from a principle to a verse remains a human/engine step (never forced onto
technical decisions — Constitution, Epistemic Foundation).
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

from monad.knowledge import Claim

DATA = Path(__file__).resolve().parent.parent / "data" / "quran" / "quran-simple.csv"
SOURCE = "tanzil:quran-simple"
_MARKS = re.compile(r"[ً-ْٰـ]")  # harakat, superscript alef, tatweel


def strip_marks(s: str) -> str:
    return _MARKS.sub("", s)


class Quran:
    def __init__(self, path: Path = DATA):
        self.ayat: dict[tuple[int, int], str] = {}
        with path.open(encoding="utf-8") as fh:
            for sura, ayah, text, *_ in csv.reader(fh):
                self.ayat[(int(sura), int(ayah))] = text

    def verse(self, sura: int, ayah: int) -> Claim:
        text = self.ayat[(sura, ayah)]  # KeyError = honest "no such verse"
        return Claim(text=text, origin="REVELATION", confidence=1.0,
                     source=f"{SOURCE}#{sura}:{ayah}", tags=["quran", f"{sura}:{ayah}"])

    def search(self, term: str, limit: int = 50) -> list[Claim]:
        """Substring search ignoring vowel marks. ponytail: linear scan over 6236 ayat,
        index it if search ever matters for speed."""
        key = strip_marks(term)
        hits = [self.verse(s, a) for (s, a), t in self.ayat.items() if key in strip_marks(t)]
        return hits[:limit]
