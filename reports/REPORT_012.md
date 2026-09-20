# MONAD REPORT — 012 (Skill، Agent و Product زیر ریشه؛ مهاجرت داده)
تاریخ: ۱۴۰۵/۰۶/۳۰ (2026-09-21) — تصمیم علی: «انجام» (گام ۳ از گزارش ۰۱۱)

## ۱. چه چیزی فهمیدم؟
- FACT: هر سه نوع فقط در *نام* فیلد با ریشه فرق داشتند: Skill `recorded`، Agent و Product `created`؛ هیچ‌کدام `id` و `kind` و `origin` نداشتند.
- FACT: هویتِ Skill در registry «name@version» است و یک رکورد منطقی چند بار append می‌شود (register → activate → rollback). پس در مهاجرت، همهٔ ردیف‌های یک name@version باید **یک** id بگیرند، وگرنه هر بارگذاری هویت تازه می‌ساخت.
- FACT: `stage`/`outcome` در Product وضعیتِ دامنه است و با `status` ریشه یکی نیست؛ هر دو نگه داشته شدند.

## ۲. چه چیزی ساختم؟
- `SkillSpec(Monad)` kind=skill، `AgentSpec(Monad)` kind=agent، `Product(Monad)` kind=product؛ فیلدهای تکراری (`recorded`, `created`, `status`) حذف و از ریشه ارث‌بری؛ پیش‌فرض‌های خاص هر نوع با `field(kw_only=True)`.
- `scripts/migrate_monad_root.py`: idempotent؛ `recorded→created`، افزودن `kind`/`origin`، یک id پایدار برای هر رکورد منطقی. بازنویسیِ فایل، تنها استثنای append-only است و در git ثبت شده (ماده ۱۲).
- تست‌ها: `test_skill_agent_product_are_monads` و `test_migration_script_moves_old_rows_under_the_root` (اجرای دوباره، RED→GREEN).

## ۳. چه چیزی اکنون قابل استفاده است؟
```
.venv/bin/python scripts/migrate_monad_root.py   # بی‌خطر: اجرای دوم = {0, 0, 0}
.venv/bin/python -m pytest -q                    # 29 passed
```

## ۴. چه چیزی بهتر شد؟
- نوع‌های زیر ریشه: **۳ → ۶** (claim, skill, agent, product, report, link). همهٔ موجودیت‌های ذخیره‌شدهٔ MONAD اکنون یک مناد هستند و origin class دارند (اجرای کامل بند «هر گزارهٔ ذخیره‌شده دقیقاً یک origin class دارد»).
- FACT مهاجرت: ۲۴ ردیف skill و ۳ ردیف product تغییر کرد؛ اجرای دوم صفر. ۹ skill با ۱۲ هویت name@version، ۹ فعال، همه بارگذاری شدند؛ محصول mizan در مرحلهٔ DEPLOYMENT با تاریخ اصلی حفظ شد.
- تست‌ها: **27 → 29 passed**. تکرار ۱۸ سبز.

## ۵. چه چیزی شکست خورد / مسدود است؟
- هیچ. (ریشه هنوز هیچ رفتار مشترکی ندارد — عمدی.)

## ۶. قدم بعد
برنامهٔ ریشه تمام شد. نه ادغام storeها، نه SQLite، نه مناد شمارهٔ صفر — هیچ‌کدام هنوز درد ندارند. قدم بعدیِ واقعی همان قبلی است: اولین استفادهٔ واقعی علی از Mizan (`python3 -m monad serve`) تا سنجهٔ کاربرد از صفر تکان بخورد.
