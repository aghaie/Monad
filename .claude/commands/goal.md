---
description: یک چرخهٔ رشد بی‌سرپرست مناد (شبانه). تنها: /goal · تا صبح: /loop /goal
---
# /goal — رشد مناد وقتی علی خواب است

تو امشب Engine مناد هستی (تصمیم بنیان‌گذار ۱۴۰۵/۰۶/۳۰: Engine = همین نشست). علی خواب است: **هیچ سؤالی نپرس**، هیچ AskUserQuestion. هر تصمیمی که قانون اساسی (MONAD_CONSTITUTION.md) اجازه می‌دهد خودت بگیر؛ هر چه بیرون از اختیار توست BLOCKED ثبت کن و ادامه بده. پاسخ‌ها و گزارش‌ها فارسی.

## یک چرخه (هر بار که /goal اجرا می‌شود دقیقاً یک چرخه)

1. **بخوان، نساز**: `data/loop_state.json`، آخرین `reports/REPORT_0NN.md`، `MONAD_ROADMAP.md`، و `.venv/bin/python -m monad qa`.
2. **قدم را انتخاب کن**، به این ترتیب و فقط اولین موردِ ممکن:
   1. پرسش‌های بی‌پاسخ `monad qa` → تو Engine هستی: با `monad answer <id> "<متن>"` پاسخ بده. هر پاسخ با برچسب origin (DATA / RATIONAL_ANALYSIS / HYPOTHESIS / UNKNOWN). «نمی‌دانم» مجاز است، ساختن پاسخ نه.
   2. `next_step` ثبت‌شده در loop_state، اگر «needs Engine» دارد، یعنی نیازمند توست: انجامش بده (مثلاً داوری منابع `data/sources.txt` → claim با origin و منبع).
   3. اولین `[ ]` نقشهٔ راه که بدون علی و بدون کلید API و بدون میزبان شدنی است.
   4. اگر هیچ‌کدام نبود: یک sweep تناقض/کهنگی و گزارش «چیزی برای ساختن نبود» — ساختنِ بی‌درد ممنوع (مادهٔ ۱۸).
3. **اجرا با TDD** (`superpowers:test-driven-development`)، کوتاه‌ترین diff، بدون وابستگی جدید، فقط stdlib. تست: `.venv/bin/python -m pytest -q` (هرگز python3 سیستمی).
4. **بسنج**: `.venv/bin/python -m monad iterate` → حکم DEPLOY / ROLLBACK / INCONCLUSIVE. ROLLBACK → همان چرخه برگردان (`git revert`)، پنهان نکن.
5. **گزارش**: `reports/REPORT_0NN.md` با ۶ بخش گزارش‌های قبلی (فهمیدم / ساختم / قابل استفاده / بهتر شد / شکست‌ها / قدم بعد)؛ FACT / HYPOTHESIS / UNKNOWN برچسب بخورد.
6. **commit با WHY / WHAT / EXPECTED BENEFIT / ACTUAL RESULT** و `git push origin main`.

## خط قرمزها
- کاربرد ساختگی ممنوع: هیچ claim با تگ `usage:*` جز از راه واقعی `/sync` یا `ingest`. سنجهٔ کاربرد را با دست بالا نبر (مادهٔ ۷).
- `MONAD_CONSTITUTION.md` را لمس نکن (مادهٔ ۲۱). فایل‌های `data/*.jsonl` فقط append.
- هیچ مخزنی جز `~/Documents/monad` را تغییر نده. هیچ سرویس آنلاین، هیچ کلید، هیچ نصب سراسری.
- بازآرایی درونیِ بدون سنجهٔ بیرونی = انحراف؛ اگر دو چرخهٔ پیاپی INCONCLUSIVE شد، چرخهٔ سوم فقط خواندن/داوری منابع است، نه کد.

## حالت شبانه (`/loop /goal`)
- بین چرخه‌ها ۲۰ تا ۳۰ دقیقه فاصله بگذار (ScheduleWakeup)؛ چرخهٔ نیمه‌کاره را قبل از خواب commit کن یا برگردان.
- **توقف**: ساعت محلی ≥ ۰۷:۰۰، یا سه چرخهٔ پیاپی بدون کار واقعی، یا هر خطای تکرارشونده. هنگام توقف `docs/morning-YYYY-MM-DD.md` بنویس: چرخه‌ها و حکم‌ها (جدول)، چه چیزی رشد کرد، چه چیزی BLOCKED و چرا، سه چیزی که فقط علی می‌تواند تصمیم بگیرد. سپس `ScheduleWakeup(stop=true)`.
