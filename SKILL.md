---
name: scientific-fa-translation-skill
description: >
  Translate scientific documents, papers, articles, books, and technical
  docs into academic Persian (Farsi) with strict RTL/bidi and untranslated
  English technical terms. Also reviews an existing Persian translation
  against these rules. Use when the user asks to ترجمه, translate a
  paper/article/book/docs, راست‌چین, RTL, PDF, چاپ, Persian scientific
  translation, or invokes scientific-fa-translation /
  scientific-fa-translation-skill.
  Do NOT use for coding, explaining code, commit messages, UI copy,
  literary translation, or casual Persian chat.
---

# Scientific Persian translation

English → academic Persian for papers, articles, books, and technical
documentation. Accuracy, consistent terminology, and print-ready RTL outrank
literary fluency. Cursor chat is not the RTL surface.

## When to use

- Translate a scientific or technical document into Persian.
- Review a finished Persian translation against these rules
  (`references/review.md`).
- User mentions ترجمه علمی, راست‌چین, RTL, PDF, چاپ, paper, article, book.

Not for: writing or explaining code, commit messages, PRs, UI copy, literary
or marketing translation, casual Persian conversation.

## Locked defaults

Override only when the user says so.

| Decision | Default |
| --- | --- |
| Direction | English → فارسی علمی |
| Register | Formal فارسی معیار. Clear and readable, not ornate. No colloquial forms. |
| Terminology | `journal` for papers, theses, review articles; `system-docs` (default) for books, install guides, specs, RFCs, runbooks. Announce the level, **three jobs**, and the **subject**. Checker `--level` must match. |
| First mention | No gloss for English terms unless the level says otherwise |
| Output | Printable PDF at `/home/$USER/Documents/books/<slug>.pdf`. Chat is a short pointer, not RTL. |
| PDF engine | XeLaTeX + `xepersian`; Chromium then WeasyPrint on the HTML template when TeX is absent |
| HTML | Only on request, or as that fallback |
| Digits | Western (`3.14`, not `۳٫۱۴`) |
| Dates | Source calendar and format, one isolate. No Jalali conversion unless asked. |
| Figures/tables | `شکل 3`, `جدول 2` — label translated, number unchanged |
| Images | Same pixels as the **artwork** on the source page (diagram, screenshot, photo), not the whole page. Flatten alpha. `dir="ltr"` / `LTR`, centered (`margin-inline: auto`). Never mirror, redraw, drop, or ship a pdfimages negative. Never embed a full source page (headers, body text, page numbers, English caption) as a figure — crop to the artwork with `scripts/crop-source-figures.py`. |
| Code blocks | Always LTR and left-aligned |
| Abstract/footnotes | Translate |
| Bibliography | Do not translate (authors, titles, journals, DOIs, URLs) |
| Ambiguity | Claim-changing ambiguity blocks and is asked; the rest is queued (`references/long-documents.md`) |
| Books | Translate and print the source table of contents (`فهرست مطالب`). Do not drop it. |

## Workflow

1. **Preflight.** `scripts/preflight.sh` — know which engine and fonts
   exist before promising a build. Confirm source, target, and level.
   Jobs and subject are inferred from the source in step 3, not chosen
   from a list.
2. **Ingest.** `references/source-ingest.md`: fetch the source, extract
   figures, run `scripts/crop-source-figures.py`, flatten with
   `scripts/prepare-figures.py figures/`, then
   `scripts/prepare-figures.py figures/ --check`. Write
   `inventory.md` and `manifest.txt` in the working tree.
   Never translate from memory when a fetch fails. Never ship a black
   pdfimages dump. Never ship a full source-page raster as a figure.
   A book `contents` / `brief contents` page is inventory chrome, not
   optional: translate it and print it.
3. **Terminology first.** Read enough of the source to name **three jobs**
   (practices the source actually covers: DevOps, networking, Linux, …)
   and the **subject** (the product or protocol: nginx, …). Announce all
   four with the level. Keep those jobs' and that subject's lexicon
   English (`location`, `proxy_pass`, `deployment` — not مکان /
   گذرگاه پیش‌رو / استقرار). Ordinary prose stays Persian. Apply
   `references/terminology.md`. Do not write `glossary.local.md` and do
   not append to `glossary.md`. Write `terms.tsv` in the working tree
   (discarded with the job) **before** drafting — keep-English rows must
   include `forbidden_fa`. Show close calls to the user first. Lint
   always with `--terms terms.tsv`.
4. **Read** `references/scientific-style.md` and `references/rtl-bidi.md`.
   For anything past ~15 pages also `references/long-documents.md`.
5. **Translate** with the ensemble in `references/ensemble.md`: Composer
   and Grok draft, Luna judges diffs only. Do not add, omit, or soften
   claims; preserve hedges (`may`, `might`, `suggest`, `remain unknown`).
6. **Isolate** every LTR run in the print source — whole clusters, one
   isolate each (`references/rtl-bidi.md`).
7. **Lint.** `scripts/check-fa.py doc.tex --level <level> --terms terms.tsv
   --manifest manifest.txt --strict` and clear every error. `--strict`
   will not run without those two files. Lint each part as you finish it,
   not at the end. `--pairs FILE` *adds* rows; it does not replace
   `term-pairs.tsv`.
8. **Build and verify.** `scripts/build-pdf.sh doc.tex <slug> --verify`
   lints again, checks `figures/` when that directory exists, and will
   not copy a PDF if lint, figure check, or `--verify` fail. Look at the
   rasterised pages. Run the judgement checklist below.

If the user asks for HTML only, use `assets/rtl-document.html`. If they ask
for Markdown, wrap the body in `<div lang="fa" dir="rtl">`, still isolate
LTR spans, and say print RTL will be weaker than PDF. Reverse translation
(FA→EN) only on explicit request; then drop the RTL rules and keep technical
terms in English.

## Terminology in one paragraph

Full policy and the field-term test: `references/terminology.md`. Infer
**three jobs** and one **subject** from the source; there is no domain pack. Ordered,
first match wins: generic document chrome (`Abstract`, `Figure`) is always
Persian; named artifacts and acronyms are English; a 2–5 word technical
label is English as **one whole isolate**; the inferred subject's lexicon
is English at every level (`nginx`, `location`, `proxy_pass`); the jobs'
lexicon is English at `system-docs` (`deployment`, `reverse proxy`) and
Persian at `journal` unless it is also the subject. Everything else is
Persian. Never half-translate (`خوشه Kubernetes`, `بلوک location`).
A kept-term plural is the singular stem plus `ها` (`\en{service}ها`,
`\en{location}ها`, `\en{API}ها`), never `services` / `locations` / `APIs`;
ezafe on Latin is still forbidden (`Goی`). Never mix two forms of one
concept in a document. Forbidden calques are enforced from
`references/term-pairs.tsv` plus this job's `terms.tsv`.

Example (`system-docs`, jobs DevOps / networking / Linux, subject nginx): «برای \en{proxy_pass}
در هر \en{location} از یک \en{upstream} استفاده کنید.» — not «برای گذرگاه
پیش‌رو در هر مکان».

Example (`journal`): «این پیاده‌سازی از \en{gradient descent} برای کمینه
کردن تابع هزینه استفاده می‌کند.»

## Persian mechanics

Full rules: `references/scientific-style.md`. UTF-8; `ک` not `ك`, `ی` not
`ي`; نیم‌فاصله in `می‌شود`, `می‌توان`, `نمی‌کند`, `داده‌ها`; punctuation
`،` `؛` `؟` `«»`. Formal verb forms only (register is judgement). Letters,
ZWNJ on the listed verbs and plurals, Western digits, Latin punct, and
unisolated number clusters are machine-checked.

## RTL

Full rules: `references/rtl-bidi.md`; engines and measured limits:
`references/pdf-output.md`. Chat does not need to be RTL.

On the PDF, non-negotiable: isolate every English term, whole collocation,
number cluster, formula, URL, and inline code with `\lr{…}` (or
`<span dir="ltr">`). Slash-, space-, arrow-, or parenthesis-joined English
(`OP_IF/OP_NOTIF`, `3.1 The OpenStack service`, `STARTED -> LOCKED_IN`,
`1.0.1 (2026-08-09)`) is **one** isolate — split across two spans it
renders reversed on the page. Listings are LTR and left-aligned. Math
stays LTR. Do not mirror images. After a trailing English insertion the
Persian period must belong to the Persian sentence.

## Output

Default: printable PDF at `/home/$USER/Documents/books/<slug>.pdf`
(`$HOME/Documents/books`, created if needed). Report that absolute path, the
page count, and the engine used.

1. Read `references/pdf-output.md`. Prefer `assets/rtl-document.tex`.
2. Persian prose in the `.tex`; English runs in `\lr{…}` / `\en{…}`.
3. Listings in `\begin{latin}…\end{latin}`. Captions translated,
   identifiers kept (`Figure 3` → `شکل 3`).
4. `\includegraphics` each cropped artwork file inside `LTR`; HTML `<img dir="ltr">`
   with `margin-inline: auto`. Flatten alpha. Order, aspect, and subfigure
   layout preserved. Never point at a full `pdftoppm` of the source page.
5. Bibliography in a `latin` section, source language. Fill the colophon
   with source, licence, and retrieval date.
6. `scripts/build-pdf.sh path/to/doc.tex <slug> --verify`. Without TeX the
   same script takes the filled-in `assets/rtl-document.html`; embed
   Vazirmatn with `scripts/fetch-vazirmatn.sh` and never the UI-FD cut.
   A page-range PDF is `scripts/extract-pdf-pages.py in.pdf out.pdf 1-20`
   — one range, never a per-page loop (`references/pdf-output.md`).

## Quality gate

**Machine-checked** — `scripts/check-fa.py --level <level> --terms terms.tsv
--manifest manifest.txt --strict` must exit 0. It covers orthography
(`ک`/`ی`, نیم‌فاصله on listed verbs/plurals,
Western digits, Persian punctuation), forbidden calques at that level,
half-translated noun phrases, English `-s` plurals of kept terms, leftover
Latin ezafe (`Goی`), split
isolates, un-isolated Latin runs, un-isolated number clusters (ranges and
dates reverse on an RTL page), listing direction, mirrored artwork,
missing images, figure direction, full-page figure rasters, and terminology drift inside isolates.
Do not re-check these by hand. `--pairs` and `--terms` merge onto the house list.

**Judgement** — only these five, and they are the whole point:

- [ ] No added, omitted, or softened scientific claim; hedges intact
- [ ] Terminology consistent: one form per concept; inferred jobs and
      subject lexicon stayed English; consistent with `terms.tsv`
- [ ] Every source figure present, unmirrored, in source order, with a
      translated caption, showing the artwork (not a black box, not a dump
      of the English source page around it)
- [ ] Rasterised pages actually read correctly (periods, parentheses,
      listings, no missing-glyph boxes) — not judged from `pdftotext`
- [ ] Claim-changing ambiguities were asked, not guessed; the rest are
      reported

**Delivery** — final PDF at `/home/$USER/Documents/books/<slug>.pdf`, chat is a short
pointer with the path, page count, engine, and queued questions.
