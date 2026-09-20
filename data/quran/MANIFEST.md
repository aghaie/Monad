# Qur'an text dataset

- File: `quran-simple.csv` — columns: sura, ayah, text, global_index, (empty)
- Source: Tanzil.net "Quran Simple" text (tanzil.net/download), imported from
  `~/Documents/monad-old/corpus/quran/source/qurantexttanzil.csv` on 2026-09-18.
- sha256: b81ccc6df7a35ed13949fa9fa060ba50b125bdaa8a898eaf07f5224cd8a20ea5
- Rows: 6236 ayat, 114 suras.
- Note: the Basmalah is prepended to the first ayah of every sura except sura 9 (Tanzil convention).
- Origin class of every row: REVELATION. License: Tanzil terms (attribution, no modification of text).

## Verified against the official source (2026-09-21, iteration 22)
Compared with Tanzil "Quran Simple, Version 1.1" (tanzil.net/pub/download, txt-2):
- **Not a verbatim copy.** After NFC normalisation and removing the superscript alef
  (U+0670, 3330 occurrences in the official text, 0 here), **6230 of 6236 ayat are identical**.
- The 6 remaining differences: `بَعْدَ مَا` written joined as `بَعْدَمَا` (2:181, 8:6, 13:37)
  and alef maqsura carrying a superscript alef turned into alef (5:31, 17:32, 39:56).
- Other Tanzil types ruled out: simple-plain 1528/6236, simple-minimal 6/6236, simple-clean 1/6236.
- Structure verified: 6236 ayat, 114 suras, sha256 unchanged, no Uthmani pause marks (U+06D6..U+06ED).
- OPEN (claim `d402d92ba6fe`): whether those 6 come from Tanzil v1.0 or from the monad-old
  import pipeline. Replacing this file with the verbatim v1.1 text is a founder decision —
  it changes the REVELATION corpus, so it was not done unattended.
