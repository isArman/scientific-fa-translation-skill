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

1. **Mechanical pass.** Run the checker over every source file:

   ```bash
   scripts/check-fa.py parts/*.tex --level system-docs --strict
   ```

   This settles orthography, forbidden calques, half-translated noun
   phrases, split isolates, English `-s` plurals of kept terms, leftover
   Latin ezafe, listing direction,
   and missing images. Do not spend review effort on anything in that list —
   report the counts.

2. **Visual pass.** Rasterise a spread of pages and look at them. Never
   judge RTL correctness from `pdftotext`.

   ```bash
   pdftoppm -png -r 110 -f 1 -l 4 out.pdf /tmp/rev-p
   pdffonts out.pdf | head        # a real fa face, not a fallback box
   pdfinfo out.pdf | grep Pages
   ```

   Look for: sentence-final periods on the correct side, parentheses that
   enclose the English rather than the Persian, numbered English headings
   that still read `3.1 Title` (not `Title 3.1`), listings left-aligned,
   figures matching the **artwork** on the source page (not black, not
   mirrored, not a dump of the English page around the figure) and in
   source order, tables whose headers repeat across pages, no
   missing-glyph boxes. If a figure still shows a source running header
   or an English body paragraph, the crop is wrong.

3. **Terminology consistency.** Compare the output against `terms.tsv` if
   it exists. Without it, extract every isolate and look for two forms of
   one concept, and for any term that appears both English and Persian.
   This is where real reviews find their findings.

4. **Fidelity spot-check.** Sample sections — abstract, one methods-heavy
   section, one section with hedging, the conclusion — and compare against
   the source for added, dropped, or hardened claims. Hedges and negative
   results are the usual casualties.

5. **Completeness.** Figure count against `manifest.txt`, section list
   against `inventory.md`, page count sanity, and the deliverable actually
   at `/home/$USER/Documents/books/<slug>.pdf`. For a book, the printed
   pages must include `فهرست مطالب` matching the source contents — not
   only a PDF outline, and not omitted because it looked like chrome.

## Report shape

Lead with the verdict, then evidence. Four parts, in this order:

- **Verdict** — is it usable as it stands, and if not, why.
- **Findings that must be fixed** — each with a file and line, grouped by
  cause rather than by location, so the fix is one edit per group.
- **Borderline, not errors** — decisions that look wrong but follow the
  policy, named explicitly so they are not "fixed" later. Ordinary-prose
  «سرویس‌ها» without a preceding English name is the standard example.
- **Engine limits** — anything caused by the PDF engine rather than the
  translation, e.g. WeasyPrint's partial `unicode-bidi: isolate` support.
  Do not report an engine limit as a translation error.

Say which checks were mechanical and which were judgement. A review that
cannot distinguish the two invites a second review of the same file.

## After the report

Offer the repair as a separate step, and when the user accepts, fix by cause
across the whole document rather than at the reported locations only — a
calque found in a glossary caption is almost always present in three other
captions. Re-lint, rebuild, and re-verify; then report the new path and page
count.
