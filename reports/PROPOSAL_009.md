# MONAD — پیشنهاد چرخه ۲۰۲۶-۰۹-۲۰
پرسش علی: «بدون وابستگی به هوش مصنوعی دیگر، همین‌جا خودت را بهبود بده.»

## ۱. سطح فعلی + شواهد (Stage 1)
- **L2 (tested)** — FACT: `python3 -m pytest -q` → `22 passed, 1 skipped in 0.74s`.
- L1 — FACT: `python3 -m monad skills` → ۹ مهارت ACTIVE؛ `python3 -m monad ask "سلام"` → `[null] UNKNOWN: no reasoning engine configured`.
- L4 (in real use) — نه. FACT: `data/loop_state.json` → `usage.mizan.claims = 0`، تنها کاربر = خودِ بنیان‌گذار.
- FACT: در ۱۳ تکرار پیاپی، `blocked` ثابت مانده: `"no reasoning engine configured (needs API key or local model)"`.
- FACT: `monad/core/engine.py` فقط دو آداپتور دارد: `NullEngine` (نمی‌داند) و `LMStudioEngine` (مدل محلی = هوش مصنوعی دیگر).

## ۲. یک گام (و چرا کوچک‌ترین تغییر درست است)
**`SessionEngine`**: آداپتوری که «موتور استدلال» را همین نشست/انسانِ پای ترمینال می‌گیرد. پرسش‌ها در `data/engine_qa.jsonl` به‌صورت PENDING ثبت می‌شوند؛ پاسخ با `python3 -m monad answer <id> "<متن>"` نوشته و برای همیشه بازاستفاده می‌شود (حافظهٔ append-only، مثل بقیهٔ مخزن).

چرا این گام: تنها مانعِ ثابتِ ۱۳ تکرار همین است، و برطرف کردنش نه کلید API می‌خواهد نه مدل محلی → دقیقاً پرسش علی. معماری از پیش گفته است «افزودن provider = یک کلاس + یک خط REGISTRY»، پس گام در مسیر موجود است، نه بازنویسی.
مطابق ماده ۱۶ (توان گفتن «نمی‌دانم»): وقتی پاسخی نیست، موتور دروغ نمی‌سازد؛ پرسشِ معلق را ثبت و به‌صورت blocked گزارش می‌کند.

## ۳. سنجه و مقدار پایه
- سنجه: `python3 -m monad ask "<پرسش>"` چند پاسخِ واقعی و ثبت‌شده می‌دهد **بدون** هیچ provider بیرونی.
- پایه (FACT، امروز): **۰** — خروجی `UNKNOWN: no reasoning engine configured`.
- هدف: ≥۱ پرسشِ پاسخ‌داده‌شده که در اجرای بعدی از فایل بازخوانده شود؛ و در تکرار ۱۴، سطرِ blockedِ «needs API key or local model» دیگر نباشد.
- نگهبان: `pytest` باید ۲۲ passed بماند (+ تست تازهٔ همین موتور).

## ۴. آنچه در این چرخه انجام **نمی‌دهم**
- آداپتور Anthropic/OpenAI (منتظر تصمیم علی دربارهٔ کلید).
- بستن خودکار شکاف مهارت‌ها با موتور، تکرارهای زمان‌بندی‌شده، A/B روی کد MONAD.
- هر کاری برای بالا بردن `usage_claims` مصنوعی؛ استفادهٔ واقعی فقط با کار واقعی علی در Mizan به دست می‌آید.
