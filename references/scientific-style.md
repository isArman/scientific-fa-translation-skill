# Academic Persian style

Register, orthography, and document mechanics. Terminology is not decided
here — `terminology.md` owns the keep-English split, and bidi is
`rtl-bidi.md`.

## Register

Locked default voice for every draft (override only if the user asks).
Target: clear formal Persian a careful non-specialist can read straight
through, with field terms kept English per `terminology.md`.

- Formal written Persian (`فارسی معیار`). No spoken reductions: not
  `میشه`, `می‌خواد`, `چونکه` as a default, `اصلاً` as filler.
- **Plain scholarly, not literary.** Prefer everyday verbs and short
  clauses. When two accurate readings exist, take the one you would say
  explaining the idea to a colleague — not the elevated synonym.

  | Prefer | Avoid |
  | --- | --- |
  | می‌خواهد / می‌رسد / می‌دهد | تلاش می‌کند دسترسی یابد / برمی‌انگیزد / ارائه می‌کند |
  | نشان بدهد / شروع می‌کند | ارائه کند / آغاز می‌کند |
  | ولی / به‌جایش | اما … در عوض (when the soft pair reads finer) |
  | می‌دهد / می‌دهند | فراهم می‌کند / فراهم می‌کنند |
  | نگاه کنید | بنگرید، ملاحظه نمایید، ملاحظه فرمایید |
  | لازم است | ایجاب می‌کند |
  | مهم است | حائز اهمیت |
  | باید گفت | لازم به ذکر است |
  | ارزیابی می‌کنیم | انجام یک ارزیابی از |

  Do **not** enforce this by grepping a fixed list. The fluency reader
  in `ensemble.md` judges the whole sentence.
- **Split long English sentences.** One English period may become two
  Persian sentences (or a short clause after `؛`). Do not keep a
  parenthesis-stuffed English mega-sentence as one Persian blob.
- **Lead with a Persian frame, keep terms English.** Prefer «وقتی
  `\en{client}` می‌خواهد به یک `\en{URI}` برسد…» or «وقتی مدل را
  `\en{train}` می‌کنید…» over calqued order or Persianising the field
  noun. Do not invent calques for job/subject terms of art — keep them
  English. Ordinary dictionary words stay Persian (`terminology.md`).
- **Avoid ugly Latin+Persian glue.** Prefer «یک `\en{URI}`» / «آن
  `\en{API}`» / «یک `\en{tensor}`» over bare «`…`ای» when the sentence
  allows. Never attach ezafe or ی to a Latin isolate (`Goی`, `URIی`).
  Plurals are still `\en{Pod}ها`, `\en{tensor}ها`.
- Prefer clear scientific prose over sentence-level calques. Do not copy
  English *clause* order when it produces unreadable Persian.
- Keep the author's epistemic stance. `may` / `might` / `suggest` /
  `appear to` / `remain unknown` must not become certainty.
- Do not add background, examples, or conclusions the source lacks.
- Do not drop hedges, limitations, negative results, or sample-size
  caveats to sound smoother.

### Canonical manner (always)

Default voice for every translator brief. Same claim, clearer wording.
The skill is **not** tied to one product — subjects are whatever the
book is about (web servers, libraries, databases, ML systems, compilers,
protocol specs, papers, …). The paragraphs below only illustrate the
*voice*.

**Tutorial / system-docs (tooling):**

> وقتی `\en{client}` می‌خواهد به یک `\en{URI}` برسد که یکی از این
> خطاها را می‌دهد (مثلاً `\en{file}`ای که روی `\en{server}` نیست و
> خطای `\en{404}` می‌گیرد)، برنامه باید صفحهٔ مربوط به آن کد خطا را
> نشان بدهد. ولی `\en{error page}` را مستقیم برای `\en{client}`
> نمی‌فرستد؛ به‌جایش با `\en{URI}` جدید یک `\en{request}` کاملاً تازه
> شروع می‌کند.

**Library / API docs:**

> اگر آرگومان `\en{None}` باشد، تابع `\en{ValueError}` می‌دهد. برای
> ادامه، `\en{batch}` را به `\en{DataLoader}` بدهید و یک `\en{epoch}`
> `\en{train}` کنید.

**Paper (hedged):**

> این تفاوت ممکن است به اندازهٔ نمونه بستگی داشته باشد و هنوز
> نمی‌توان `\en{causal effect}` را قطعی دانست.

Reject drafts that sound like: برمی‌انگیزد، ارائه کند، آغاز می‌کند،
سندی یا پرونده‌ای (when the source means a kept `file`), or one
unbroken calqued sentence where the exemplar would have split.

### Genre → tone

Announce one genre with terminology. It does **not** change keep-English
rules; it only shifts connectors and density:

| Genre | Tone |
| --- | --- |
| `tutorial` | Canonical manner as written: short clauses, `ولی` / `به‌جایش`, direct address OK when the source uses it |
| `reference` | Same plain verbs; fewer soft connectors; tighter, definition-like sentences |
| `paper` | Same plain verbs; hedges preserved densely; slightly more nominal abstracts OK if the source is nominal — still split mega-sentences |

### Collocations (preferred patterns)

Lock recurring verb+term patterns when both readings are accurate.
Write close calls into `terms.tsv` `admitted` / notes if needed. Defaults
for software and scientific tooling prose (any stack — not one product):

| English pattern | Prefer | Avoid |
| --- | --- | --- |
| send / issue a `request` | `\en{request}` بفرستد / بدهد | درخواست را ارسال نماید |
| return `404` / an error / raise | `\en{404}` / خطا بدهد / `\en{Exception}` بدهد | مبادرت به بازگرداندن خطا کند |
| call / invoke a `function` | `\en{function}` را صدا بزند / فراخوانی کند | مبادرت به فراخوانی تابع نماید |
| train a `model` | `\en{model}` را `\en{train}` کند | مدل را تحت آموزش قرار دهد |
| start / begin a `request` / job | `\en{request}` / کار را شروع کند | `\en{request}` را آغاز نماید |
| access a `URI` / endpoint | به `\en{URI}` برسد / دسترسی پیدا کند | به `\en{URI}` نایل شود |
| show / serve a page / result | نشان بدهد | ارائه کند |
| configure `X` | `\en{X}` را `\en{configure}` کند when the verb is kept; otherwise پیکربندی کند | اقدام به پیکربندی `X` نماید |

### Do not over-English

Keep isolates for **terms of art**, not for ordinary dictionary words.
If a Latin isolate is just a common noun the job/subject lexicon does
not claim (`security` → امنیت, narrative `file` when not the tooling
sense), write Persian. Fluency reader must FLAG spans that feel like
English stuffed into Persian function words without a terminology
reason.

### Fluency pass

After terminology is locked in `terms.tsv` and a part is drafted and
lint-clean, run the **fluency reader** step in `ensemble.md` (default
Grok when Composer wrote the part). Gold standard is the Canonical
manner above **and** the paragraphs in `fluency-gold.md`. The model
decides whether the Persian matches that voice; the primary revises
only flagged spans. Also fix the five EN→FA structure failures below
when they show up. Do not use that pass to soften hedges or invent
glosses.

## Common EN→FA failures

Faithfulness is the first rule, but these five patterns produce prose that
is technically accurate and still unreadable.

1. **English passive kept as Persian passive.** `The model was trained on…`
   → «مدل روی … آموزش داده شد» is fine; a chain of three passives in one
   sentence is not. Recast the middle one as active when the agent of the
   sentence is obvious.
2. **Ezafe chains.** More than three linked اضافه constructions
   («بررسی نتایج ارزیابی کارایی سیستم») force the reader to re-parse.
   Break the chain with a verb or a preposition.
3. **Over-nominalisation.** English science nominalises freely; Persian
   reads better with the verb restored. `perform an evaluation of` →
   «ارزیابی می‌کنیم», not «انجام یک ارزیابی از».
4. **Bidi-heavy sentences.** With this skill's terminology policy a
   sentence can end up more English than Persian. Prefer a Persian
   subject or preposition first. A sentence **may** start with an LTR
   isolate when that isolate is the grammatical subject — a kept field
   term (`Cloud provider`ها …, `CLI`ها …). If more than about half a
   sentence is isolates, split it.
5. **First person.** Keep the source's stance: `we trained` → «آموزش
   دادیم», `it is assumed` → «فرض می‌شود». Do not promote an impersonal
   source to first person or the reverse.

## Orthography

- Encoding UTF-8.
- Persian letters: `ک` not `ك`, `ی` not `ي`. Normalise Arabic forms that
  appear in a draft.
- نیم‌فاصله (U+200C) where Persian orthography requires it: `می‌شود`,
  `می‌توان`, `نمی‌کند`, `شده‌اند`, plural `داده‌ها`, and standard
  adjectival compounds.
- Punctuation `،` `؛` `؟` `!` `«»`. Not Latin `,` `;` `?` `"` in Persian
  prose. `…` sparingly.
- Scientific numbers stay Western: `3.14`, `2e-5`, `95%`. Never `۳٫۱۴`.
- Decimal point stays `.`; Persian `٫` is not used.
- SI units stay SI (`km`, `ms`, `°C`). Do not convert unit systems.

`scripts/check-fa.py` fails the build on the letters, ZWNJ verbs and
plurals, Latin comma/semicolon/question mark, Eastern digits, and Arabic
decimal separators in this section. Register fluency is a model
judgement (`ensemble.md` fluency reader), not a pattern match. SI unit
conversion, hedges, ezafe chains, and the rest of register beyond that
pass are judgement — `review.md`.

## Dates and numerals

- Dates stay in the source calendar and format: `2026-08-09` remains
  `2026-08-09`, isolated as one LTR run. Do not convert to Jalali unless
  the user asks; if they do, add the Gregorian in parentheses inside the
  same isolate on first mention.
- Version strings, RFC numbers, and port numbers are identifiers, not
  quantities. Never reformat them.
- Ranges keep the source dash and are one isolate: `2017–2024`,
  `300-400`.
- Percentages keep the Latin sign: `55%`.

## Cross-references and labels

| Source | Persian |
| --- | --- |
| Figure 3 | شکل 3 |
| Table 2 | جدول 2 |
| Equation (4) | معادله (4) |
| Section 3.2 | بخش 3.2 |
| Appendix A | پیوست A |
| Contents | فهرست مطالب |
| Theorem / Lemma / Proof | قضیه / لم / اثبات |

Do not localise the numeral, and keep it in an LTR isolate. Prefer real
`\ref` / `\label` over typed numbers when the translation renumbers
anything; a hand-typed number silently rots.

## Headings

Generic labels take the Persian in `glossary.md`. A heading that *is* a
named artifact or a technical label stays English in one isolate — `The
OpenStack serviceها`, `Conceptual architecture`, `Host networking`, `Get
started with OpenStack`. Do not Persianise the generic word and leave the
name behind.

## Figures

The translation must *show* the same figures the source shows.

- Copy or crop the original artwork (PNG, JPEG, SVG, a **clip** of the
  PDF page). Point `\includegraphics` or `img src` at those files. Do not
  redraw, screenshot-replace, or generate a substitute.
- A full `pdftoppm` of the source page is not a figure. It contains
  English headers, body, captions, and page numbers. Crop with
  `scripts/crop-source-figures.py` to the diagram, screenshot, or photo.
  Cover: illustration only. Author: headshot only.
- Run `scripts/prepare-figures.py figures/artwork --check` after ingest.
  Flatten PNG alpha onto white. If a file is a near-black dump, compare it
  with a `pdftoppm` of the source page; invert only when that page is
  light (`--invert-dark`).
- HTML: `dir="ltr"` on every `<img>`, and center it (`margin-inline:
  auto` — the HTML template does this). `dir="ltr"` plus `display:block`
  without auto margins hugs the physical left of an RTL page. XeLaTeX:
  `\includegraphics` inside `LTR`. The checker fails without `dir="ltr"` /
  `LTR`, and on `srcpage-N` / `page-N` filenames.
- Keep document order, subfigure layout (`a`/`b`/`c`), and the artwork's
  aspect ratio. Crop away page chrome; do not crop away labels that belong
  to the figure.
- Never mirror or rotate for RTL.
- Text baked into the image stays as in the source. Do not edit pixels to
  Persianise axis labels or legends.
- Translate the caption and the prose that refers to the figure. Do not
  put a Persian period immediately after an English isolate at the end of
  a caption — it jumps to the left. End the caption on a Persian word, or
  omit that period.
- `alt` may be a short Persian description; it must not replace the image.
- If a file is missing or unreadable, leave a visible comment at that spot
  and tell the user. Do not invent a figure. The checker fails on an
  `\includegraphics` target that is not on disk.

## Tables

- Persian prose cells are RTL; numeric cells are LTR and left-aligned.
- Do not reverse column order unless the user asks.
- A table that runs past one page needs `longtable` with a repeated
  header, not a manually split table. Real documents (port lists,
  requirement matrices) hit this constantly.
- A caption that is a technical label stays English whole; only the
  `جدول N.` prefix is Persian.

## Footnotes, quotes, and links

- Footnote markers follow the Persian text direction; the note body
  follows its own content. An English-only note stays in a `latin`
  environment.
- Quote Persian prose with `«»`. An English title inside Persian prose
  keeps its own quoting from the source and sits in one isolate.
- URLs are isolates and must be allowed to break, or they overflow the
  page silently: `\url` plus `xurl` in TeX, `overflow-wrap: break-word` in
  CSS. Note `word-break: break-word` is not a valid CSS value and
  WeasyPrint drops it.
- A long URL broken mid-string inside a Persian paragraph is legible but
  reads badly — the `https://` fragment ends up alone at the far end of
  the previous line. Prefer giving a long URL its own block-level line, a
  footnote, or the bibliography, rather than burying it in running RTL
  prose.

## Citations

Keep citation keys in source form, isolated as LTR: `(Smith et al., 2021)`,
`[12]`, DOI links. Do not translate `et al.`, and do not convert Harvard to
Vancouver or the reverse.

Bibliography entries are not translated: authors, titles, journals, years,
publishers, DOIs, URLs.

## Ambiguity

If a pronoun, the scope of a negation, or a technical reading would change
the science, stop and ask. Do not pick the more fluent reading.

For a document long enough that stopping forty times is impractical, use
the queue in `long-documents.md`: a claim-changing ambiguity blocks, and
everything else is recorded and reported once at the end.

If the source is truncated, OCR-garbled, or a formula is unreadable, leave a
comment at that spot and tell the user. Do not invent the missing science.
