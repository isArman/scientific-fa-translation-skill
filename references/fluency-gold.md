# Fluency gold paragraphs

Regression targets for the Canonical manner in `scientific-style.md`.
When changing register rules or the fluency-reader brief, re-read these
and confirm a good draft still matches them. They are **examples**, not
a checklist for `check-fa.py`.

Placeholders use `\en{…}` as in print TeX. In fluency-reader prompts,
strip isolates to `‹EN›`.

## G1 — NGINX error_page (tutorial)

> وقتی `\en{client}` می‌خواهد به یک `\en{URI}` برسد که یکی از این
> خطاها را می‌دهد (مثلاً `\en{file}`ای که روی `\en{server}` نیست و
> خطای `\en{404}` می‌گیرد)، `\en{NGINX}` باید صفحهٔ مربوط به آن کد
> خطا را نشان بدهد. ولی `\en{error page}` را مستقیم برای `\en{client}`
> نمی‌فرستد؛ به‌جایش با `\en{URI}` جدید یک `\en{request}` کاملاً تازه
> شروع می‌کند.

Reject: برمی‌انگیزد / ارائه کند / آغاز می‌کند / سندی یا پرونده‌ای /
one unbroken calque of the English period.

## G2 — Hedge preserved (paper)

> این نتیجه ممکن است به اندازهٔ نمونه بستگی داشته باشد و هنوز
> نمی‌توان `\en{causal effect}` را قطعی دانست.

Reject: hardening to «ثابت می‌کند» or dropping «ممکن است».

## G3 — Job lexicon kept English (system-docs)

> برای هر `\en{deployment}` یک `\en{replica}` جدا `\en{configure}`
> کنید و `\en{request}`ها را از طریق `\en{Service}` بفرستید.

Reject: استقرار / رونوشت / پیکربندی کنید as calques for those kept
terms; also reject «اقدام به ارسال درخواست نمایید».

## G4 — Ordinary prose not over-Englished

> امنیت را با محدود کردن دسترسی افزایش دهید؛ اگر `\en{file}` پیکربندی
> موجود نباشد، فرایند متوقف می‌شود.

Here `security` is ordinary prose → امنیت. `file` stays English only
when it is the tooling sense locked in `terms.tsv`; if the row is prose,
Persian پرونده/فایل is fine — be consistent with `terms.tsv`.

## G5 — Split mega-sentence (reference)

Source shape: long English sentence with two parentheses.
Target shape: two Persian sentences or one short clause after `؛`,
plain verbs, kept terms isolated.

> `\en{API}` مقدار را برمی‌گرداند؛ اگر ورودی نامعتبر باشد، خطای
> `\en{400}` می‌دهد و پیامی در `\en{log}` می‌نویسد.

## G6 — Collocation: return / send

> اگر کلید نباشد، `\en{404}` برمی‌گرداند. سپس یک `\en{request}` تازه
> به `\en{upstream}` می‌فرستد.

Reject: «مبادرت به بازگرداندن ۴۰۴ می‌کند» / «درخواست را ارسال می‌نماید».

## How to use

1. Fluency reader brief points here as the gold standard beside Canonical
   manner.
2. After a register/ensemble edit, have the reader score a draft of G1–G3
   (or the bake-off span) and expect `OK` on gold-like prose.
3. Do not paste this whole file into every translator prompt — only the
   relevant gold id when calibrating.
