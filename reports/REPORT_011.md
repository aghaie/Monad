# MONAD REPORT — 011 (Claim یک مناد است؛ محیط تست روی Python 3.12)
تاریخ: ۱۴۰۵/۰۶/۳۰ (2026-09-21) — تصمیم علی: «تأیید کامل» بر پیشنهاد گزارش ۰۱۰ (Python ≥3.10 برای تست‌ها، سپس Claim زیر Monad)

## ۱. چه چیزی فهمیدم؟
- FACT: `python3` سیستم = 3.9.6 ولی pyproject ≥3.10 می‌خواست؛ Python 3.12 (Homebrew) نصب بود و فقط pytest نداشت. یعنی مانعِ `kw_only` یک مانعِ محیط بود، نه کد.
- FACT: همهٔ ساخت‌های Claim در کد Python با keyword هستند (تنها فراخوانی positional در JS محصول Mizan است) → `origin` می‌تواند keyword-only بماند.
- FACT: Claim از قبل فیلدهای `id, origin, source, status, created` را با همین نام‌ها داشت → ارث‌بری از ریشه **صفر** مهاجرت داده لازم داشت.

## ۲. چه چیزی ساختم؟
- `.venv` با Python 3.12 + pytest (در `.gitignore`)؛ README به `.venv/bin/python -m pytest -q`.
- `Monad` و `Link` و `Report` → `@dataclass(kw_only=True)`. `ORIGIN_CLASSES` به ریشه (`monad/core/monad.py`) منتقل شد و از `monad.knowledge` re-export می‌شود (شکستن حلقهٔ import).
- `Claim(Monad)`: فیلدهای تکراری حذف؛ `kind="claim"`؛ اعتبارسنجی origin از ریشه. `supersedes` و `schema` افزایشی اضافه شدند؛ ردیف‌های قدیمی بدون آن‌ها خوانده می‌شوند.
- تست: `test_claim_is_a_monad_and_old_rows_still_load` (اول RED، سپس GREEN).

## ۳. چه چیزی اکنون قابل استفاده است؟
```
.venv/bin/python -m pytest -q      # 27 passed
.venv/bin/python -m monad iterate  # تکرار ۱۷
```

## ۴. چه چیزی بهتر شد؟
- نوع‌های زیر ریشهٔ مشترک: **۲ (link, report) → ۳ (+claim)**. رکوردهای زندهٔ مناد: ۱۴ + ۳۵ claim.
- FACT: هر ۳۵ claim موجود در `data/knowledge.jsonl` با `kind="claim"` بارگذاری شدند؛ تست Mizan (`Claim(**r)`) سبز.
- تست‌ها: **26 → 27 passed**.

## ۵. چه چیزی شکست خورد / مسدود است؟
- تکرار ۱۷: `reports_registered: 0` درست است (هیچ گزارش تازه‌ای پیش از این فایل نبود)؛ این گزارش در ثبت بعدی مناد می‌شود.
- Skill / Agent / Product هنوز زیر ریشه نیستند: نام فیلدهایشان متفاوت است (`recorded`, `name`, …) → مهاجرت داده لازم دارند (گام ۳).

## ۶. قدم بعد
گام ۳ به همان ترتیب: SkillSpec ← Monad (اسکریپت مهاجرت `recorded→created` در `scripts/`)، سپس AgentSpec، سپس Product؛ هر کدام یک کامیت با تست RED→GREEN.
