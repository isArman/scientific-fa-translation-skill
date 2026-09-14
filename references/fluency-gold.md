# Fluency gold paragraphs

Regression targets for the Canonical manner in `scientific-style.md`
(locked register band: human-like technical Persian — not MT, not
colloquial, not literary). When changing register rules or the
fluency-reader brief, re-read these and confirm a good draft still
matches them and the reject lines still fail. They are **voice examples
across software/science genres**, not a product-specific style guide and
not a checklist for `check-fa.py`.

The skill applies to any scientific or technical book (especially
software): libraries, databases, distributed systems, ML, compilers,
protocol specs, papers, HTML/CSS docs. Infer jobs/subjects per source;
do not assume nginx, Kubernetes, or any other stack.

Placeholders use `\en{…}` as in print TeX. In fluency-reader prompts,
strip isolates to `‹EN›`.

## G1 — Error handling (tutorial / system-docs)

> وقتی `\en{client}` می‌خواهد به یک `\en{URI}` برسد که یکی از این
> خطاها را می‌دهد (مثلاً `\en{file}`ای که روی `\en{server}` نیست و
> خطای `\en{404}` می‌گیرد)، برنامه باید صفحهٔ مربوط به آن کد خطا را
> نشان بدهد. ولی `\en{error page}` را مستقیم برای `\en{client}`
> نمی‌فرستد؛ به‌جایش با `\en{URI}` جدید یک `\en{request}` کاملاً تازه
> شروع می‌کند.

Reject: برمی‌انگیزد / ارائه کند / آغاز می‌کند / سندی یا پرونده‌ای /
one unbroken calque of the English period.

## G2 — Library / API docs

> اگر آرگومان `\en{None}` باشد، تابع `\en{ValueError}` می‌دهد. برای
> ادامه، `\en{batch}` را به `\en{DataLoader}` بدهید و یک `\en{epoch}`
> `\en{train}` کنید.

Reject: literary padding («مبادرت به آموزش مدل نمایید») or Persianising
kept library terms.

## G3 — Hedge preserved (paper)

> این نتیجه ممکن است به اندازهٔ نمونه بستگی داشته باشد و هنوز
> نمی‌توان `\en{causal effect}` را قطعی دانست.

Reject: hardening to «ثابت می‌کند» or dropping «ممکن است».

## G4 — Job lexicon kept English (system-docs)

> برای هر `\en{deployment}` یک `\en{replica}` جدا `\en{configure}`
> کنید و `\en{request}`ها را از طریق `\en{Service}` بفرستید.

Reject: استقرار / رونوشت as calques for those kept terms; also reject
«اقدام به ارسال درخواست نمایید».

## G5 — Ordinary prose not over-Englished

> امنیت را با محدود کردن دسترسی افزایش دهید؛ اگر فایل پیکربندی
> موجود نباشد، فرایند متوقف می‌شود.

Here `security` is ordinary prose → امنیت. Keep `\en{file}` only when
`terms.tsv` locks the tooling sense; otherwise Persian is fine — stay
consistent with `terms.tsv`.

## G6 — Database / query reference

> `\en{query}` را روی `\en{index}` اجرا کنید؛ اگر ردیفی نباشد،
> `\en{NULL}` برمی‌گردد و در `\en{log}` نوشته می‌شود.

Reject: mega-sentence calques; «مبادرت به اجرای پرس‌وجو نمایید».

## G7 — Collocation: return / send / call

> اگر کلید نباشد، `\en{404}` برمی‌گرداند. سپس یک `\en{request}` تازه
> می‌فرستد و `\en{callback}` را صدا می‌زند.

Reject: «مبادرت به بازگرداندن ۴۰۴ می‌کند» / «درخواست را ارسال می‌نماید».

## G8 — Web / HTML tutorial (high isolate density)

Calibrate MDN-like and browser-docs prose. Terms stay English; glue is
plain Persian. Same register band as G1–G7 (not colloquial, not literary).

> برای تعریف یک اصطلاح، از `\en{<dfn>}` و `\en{id}` استفاده کنید تا
> بقیهٔ صفحه با `\en{href}` به آن اشاره کند. اگر فقط یک‌بار واژه را
> می‌آورید و پیوند لازم نیست، `\en{<dfn>}` به‌تنهایی کافی است. متن
> داخل `\en{<dfn>}` باید همان اصطلاحی باشد که بعداً به آن ارجاع
> می‌دهید — نه یک جملهٔ توضیحی بلند.

Reject: «مبادرت به تعریف اصطلاح می‌نماید» / «ارائهٔ تعریف را آغاز
می‌کند» / chatty «می‌خواد تگ بذاره» / a wall of `\en{…}` with almost
no Persian frame.

## Literary / ornate rejects (any gold)

These fail fluency even when terminology is correct:

- برمی‌انگیزد، می‌نماید، نایل شود، مبادرت ورزد، ارائه نماید
- آغاز می‌کند / ارائه کند as elevated filler where شروع / نشان بدهد fits
- Essay padding that adds rhythm but not meaning

## How to use

1. Fluency reader brief points here as the gold standard beside Canonical
   manner (including the locked register band in `scientific-style.md`).
2. After a register/ensemble edit, score a draft of G1–G3 or G8 (or the
   bake-off span) and expect `OK` on gold-like prose and `FLAG` on the
   reject lines.
3. Pick the gold id that matches the book's genre; do not force
   web-server wording onto an ML or database text — but **do** keep the
   same plain scholarly band everywhere.
4. Do not paste this whole file into every translator prompt — only the
   relevant gold id when calibrating.
