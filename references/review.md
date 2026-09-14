# Review mode

Second entry point of this skill: judging an existing translation instead of
producing one. Trigger it when the user asks whether the skill was applied
correctly, asks for a review or ویرایش of a finished PDF, or hands back an
output with highlights. Do not silently rewrite the document — review first,
then offer the edit.

## Inputs

Best case the working tree from `source-ingest.md` still exists and the
`.tex` / `.html` is available. If only the PDF exists, rasterise it and work
from images plus whatever source text can be recovered; say in the report
that the check was visual and therefore partial.

## Order of work

Follow Mossop-style layers. Finish each layer before the next. Do not
silently rewrite until the report is accepted.

### L0 — Mechanical (machine)

Run the checker over every source file:

```bash
scripts/check-fa.py parts/*.tex --level system-docs --terms terms.tsv --manifest manifest.txt --strict
```

This settles orthography, forbidden / deprecated calques, half-translated
noun phrases, split isolates, English `-s` plurals of kept terms,
leftover Latin ezafe, listing direction, and missing images. Report
counts only — do not spend human review on this list.

### L1 — Transfer (claims and hedges)

Sample abstract / intro, one methods-heavy or procedure-heavy section,
one hedged section, and the conclusion. Compare to the source for added,
dropped, or hardened claims. Hedges (`may`, `might`, `suggest`, `remain
unknown`) and negative results are the usual casualties.

**Back-translation spot-check:** pick about 1–2 % of sentences that
carry hedges or numbers (cap 12). Mentally or on paper render them back
to English and confirm the epistemic force and quantities match. Record
mismatches as transfer findings, not as fluency nits.

### L2 — Content / terminology

Compare the output against concept-oriented `terms.tsv`: one preferred
form per `concept`; jobs/subjects lexicon stayed English; no silent use
of `deprecated` or `admitted` as a second preferred. Without `terms.tsv`,
extract every isolate and look for two forms of one concept, and for any
term that appears both English and Persian.

### L3 — Language / fluency

Run (or re-run) the fluency-reader brief in `ensemble.md` on running
prose, scoring against Canonical manner and `fluency-gold.md` (including
G8 for web/HTML docs) — default Grok when Composer wrote the text. Fail
closed on colloquial **and** literary/ornate Persian; require human-like
short clauses, not translationese. Also flag over-English: Latin
isolates that are ordinary dictionary words, not terms of art, or a
sentence that is mostly `\en{…}` with almost no Persian frame. Glance at
ezafe chains, over-nominalisation, and passive piles. Do not "fix"
fluency by softening hedges.

### L4 — Presentation (visual / RTL)

Rasterise a spread of pages and look at them. Never judge RTL from
`pdftotext`.

```bash
pdftoppm -png -r 110 -f 1 -l 4 out.pdf /tmp/rev-p
pdffonts out.pdf | head
pdfinfo out.pdf | grep Pages
```

Look for: sentence-final periods on the correct side, parentheses that
enclose the English rather than the Persian, numbered English headings
that still read `3.1 Title` (not `Title 3.1`), listings left-aligned,
figures matching the **artwork** on the source page (not black, not
mirrored, not a dump of the English page around the figure) and in
source order, tables whose headers repeat across pages, no missing-glyph
boxes. If a figure still shows a source running header or an English
body paragraph, the crop is wrong.

### L5 — Completeness

Figure count against `manifest.txt`, section list against `inventory.md`,
page count sanity, and the deliverable actually at
`/home/$USER/Documents/books/<slug>.pdf`. For a book, the printed pages
must include `فهرست مطالب` matching the source contents — not only a PDF
outline, and not omitted because it looked like chrome.

## Report shape

Lead with the verdict, then evidence. Four parts, in this order:

- **Verdict** — is it usable as it stands, and if not, why.
- **Findings that must be fixed** — each with a file and line, grouped by
  Mossop layer (L0–L5) and cause rather than by location, so the fix is one edit per group. Put back-translation mismatches under L1.
- **Borderline, not errors** — decisions that look wrong but follow the
  policy, named explicitly so they are not "fixed" later. Ordinary-prose
  «سرویس‌ها» without a preceding English name is the standard example.
- **Engine limits** — anything caused by the PDF engine rather than the
  translation, e.g. WeasyPrint's partial `unicode-bidi: isolate` support,
  or copy-paste reversing Persian in Chrome/Edge built-in PDF viewers
  (viewer limit — Evince/Adobe usually fine; use the `.txt` sidecar).
  Do not report an engine limit as a translation error.

Say which checks were mechanical and which were judgement. A review that
cannot distinguish the two invites a second review of the same file.

## After the report

Offer the repair as a separate step, and when the user accepts, fix by cause
across the whole document rather than at the reported locations only — a
calque found in a glossary caption is almost always present in three other
captions. Re-lint, rebuild, and re-verify; then report the new path and page
count.
