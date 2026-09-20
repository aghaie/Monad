# MONAD REPORT — 010 (موجودیت ریشه: هر چیزِ ذخیره‌شده یک مناد است)
تاریخ: ۱۴۰۵/۰۶/۳۰ (2026-09-21) — پرسش علی: «آیا می‌شود entity بنیادینی به نام monad داشت که ریشهٔ همهٔ entityها باشد؟ … بساز؛ برای شروع همین گزارش‌ها را موجودیت کن.»
ارزیابیِ پیش از اجرا: `docs/monad-root-entity-2026-09-21.md` (سه پرسش: ریشه، هزاران موجودیت، دیتابیس ده‌ساله)

## ۱. چه چیزی فهمیدم؟
- FACT: پنج موجودیت ذخیره‌شونده (Claim, SkillSpec, AgentSpec, Product, IterationRecord) هیچ ریشهٔ مشترکی نداشتند؛ «زمان ساخت» با سه نام (`created`, `recorded`, `started`) و شناسه با سه شکل (`id`, `name`, `number`).
- FACT: قانون اساسی می‌گوید «هر گزارهٔ ذخیره‌شده دقیقاً یک origin class دارد» ولی فقط Claim به آن پایبند بود.
- FACT: گزارش‌های خودِ MONAD (`reports/*.md`, `docs/*.md`) هیچ‌جا به‌عنوان داده ثبت نمی‌شدند؛ سیستم از تولیدات خودش بی‌خبر بود.
- محدودیت محیط: تست‌ها با Python 3.9.6 اجرا می‌شوند (pyproject ≥3.10 می‌گوید) → `kw_only` در دسترس نیست؛ ریشه با فیلدهای همه‌default ساخته شد و اعتبارسنجی در `__post_init__`.

## ۲. چه چیزی ساختم؟
- `monad/core/monad.py`: `Monad` (id · kind · origin · created · status · source · supersedes · schema) — فقط فیلد، بدون رفتار مشترک. `Link` = رابطه به‌صورت رکورد (src, dst, relation, origin). `MonadStore` = JSONL افزایشی؛ هیچ ویرایش/حذفی؛ تغییر = رکورد جدید با `supersedes`؛ فیلد ناشناخته نادیده گرفته می‌شود (تکامل schema فقط افزایشی).
- `monad/reports.py`: نوع `report`. هر Markdown در `reports/` و `docs/` با path + sha256 ثبت می‌شود؛ idempotent؛ ویرایش فایل ⇒ رکورد جدید که قبلی را supersede می‌کند.
- حلقه: هر تکرار اول گزارش‌ها را ثبت می‌کند (`reports_registered`) و `monads` را می‌شمارد. CLI: `python3 -m monad monads [kind]`.
- تست: `tests/test_monad.py` (۳ تست، اول RED سپس GREEN): اجبار origin، append-only/last-wins/tolerant reader/links، ثبت idempotent و زنجیرهٔ supersedes.

## ۳. چه چیزی اکنون قابل استفاده است؟
```
python3 -m monad monads            # همهٔ منادها
python3 -m monad monads report     # فقط گزارش‌ها (با ⇐ id قبلی اگر نسخهٔ جدید باشد)
python3 -m monad iterate           # هر تکرار گزارش‌های تازه/تغییریافته را خودکار ثبت می‌کند
```

## ۴. چه چیزی بهتر شد؟
- موجودیت‌های ثبت‌شده با ریشهٔ مشترک: **۰ → ۱۲** (FACT: تکرار ۱۶، `reports_registered: 12`)، به‌علاوهٔ همین گزارش (و نسخهٔ اصلاح‌شدهٔ همین گزارش که رکورد قبلی‌اش را supersede می‌کند — اولین زنجیرهٔ واقعی).
- تست‌ها: **23 → 26 passed**، بدون شکست.

## ۵. چه چیزی شکست خورد / مسدود است؟
- هنوز Claim/Skill/Agent/Product از ریشه ارث نمی‌برند (گام ۲ و ۳ برنامه). دلیل توقف: بدون `kw_only` ارث‌بری Claim (فیلدهای اجباری `text, origin`) در 3.9 ممکن نیست؛ یا Python تست‌ها باید ≥3.10 شود، یا این نوع‌ها با فیلدهای default بازنویسی شوند. تصمیم با مؤسس.
- `monads.jsonl` جدا از `knowledge.jsonl` است؛ ادغام وقتی Claim مناد شد.

## ۶. قدم بعد
Python تست‌ها را به ≥3.10 ببر (یا pyproject را به 3.9 پایین بیاور — تصمیم)، سپس Claim ← Monad بدون از‌دست‌دادن فیلد (تست Mizan سبز بماند)، سپس بقیه یکی‌یکی با migration داده.
