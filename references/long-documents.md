# Long documents

Applies from roughly fifteen pages or six thousand words up — install
guides, specifications, books. The failures at this size are not translation
failures: terminology drifts between chapter three and chapter nine, a
section is lost, the agent runs out of context and restarts from a different
set of decisions. Everything here exists to make those three impossible.

## Terminology first

Before drafting any body text:

1. Read enough of the source to name the **job** and the **subject**
   (DevOps + nginx). Announce both with the level. There is no domain
   pack to select.
2. Scan the whole source for candidate terms. Classify each with the
   decision procedure in `terminology.md`. The inferred job and subject
   lexicon stays English.
3. Write `terms.tsv` in the working tree — source term, chosen output
   form, decision step, occurrence count, optional forbidden calque:

   ```text
   source	output	step	count	forbidden_fa
   location	location	3 subject-lexicon	84	مکان
   proxy_pass	proxy_pass	3 subject-lexicon	40
   deployment	deployment	3 job-lexicon	22	استقرار
   security	امنیت	5 prose	41
   Introduction	مقدمه	0 chrome	1
   ```

   Fill `forbidden_fa` when a Persian calque of a keep-English term is
   obvious, so `--terms` can fail the build on it. Do not write
   `glossary.local.md`. Do not append to `glossary.md`. `terms.tsv` is
   job memory and is discarded with the working tree.
4. Show the user the rows that were close calls, then translate.

This step is the fix for the recorded `password` / گذرواژه drift: the body
kept `password` while a caption used گذرواژه, because the decision was
made twice, seventy pages apart. Deciding once, in a file, costs minutes;
repairing it after a 174-page build costs a rebuild.

## Sectioning

One file per top-level section, numbered in reading order, in the working
tree from `source-ingest.md`:

```text
parts/01-overview.tex   parts/05-networking.tex
parts/02-environment.tex   parts/06-glossary.tex
```

Aim for 1500–3000 words per part. Assemble with `\input` from a thin
`doc.tex` that holds only the preamble, title, TOC, and the input list —
for HTML, concatenate parts in order into `doc.html`.

A book or long report **prints** the source table of contents, translated
(`فهرست مطالب`). TeX: `\renewcommand{\contentsname}{فهرست مطالب}` then
`\tableofcontents`. HTML: a `<nav class="toc">` after the cover, matching
the source entries; live page numbers via CSS `target-counter` (the
template already has the rule). Do not copy folio numbers from the English
PDF — those are the source's pages, not yours. Do not skip the contents
because “the PDF outline is enough”; the printed page is the deliverable.

Lint each part as it is finished, not at the end:

```bash
scripts/check-fa.py parts/03-*.tex --level system-docs --terms terms.tsv --strict
```

A part that lints clean stays clean. A 174-page document linted once at the
end produces a finding list nobody works through.

## Progress ledger

`progress.md`, updated as each part changes state, because a fresh agent
must be able to resume without re-deriving anything:

```text
| part | state | lint | notes |
| 01-overview | done | clean | — |
| 02-environment | done | clean | 2 ambiguities queued |
| 03-identity | drafting | — | stopped mid-section, line 240 |
| 04-image | todo | — | — |
```

States: `todo`, `drafting`, `done`, `needs-review`. On resume, read
`progress.md` and `terms.tsv` first, then the part in `drafting`. Never
restart a `done` part; never re-decide a term already in `terms.tsv`.

## Ambiguity queue

Stopping to ask forty times does not work at this length, and guessing
silently is worse. Split by consequence:

- **Blocks.** Anything that would change a scientific or normative claim:
  scope of a negation, a conditional's antecedent, a units mismatch, a
  number that contradicts the surrounding text. Stop and ask.
- **Queued.** Everything else. Translate the best reading, mark the spot
  with `% TODO(ambiguity): …` in the `.tex` (an HTML comment in HTML), and
  append a row to `questions.md`.

Report the queue once, with locations, in the final chat message. Do not
leave a `TODO` marker in the compiled PDF text.

## Context budget

Read the source part you are translating and `terms.tsv` — not the whole
source and not previously finished parts. If a decision needs an earlier
part, look it up in `terms.tsv` first; that is what the file is for.

## Assembly and verification

1. Lint every part, then the assembled document.
2. Build once with `scripts/build-pdf.sh`.
3. Verify the artifact, not the source: page count against `inventory.md`,
   embedded fonts, and rasterised sample pages (`build-pdf.sh --verify`
   does all three).
4. Check the figure count against `manifest.txt`.
5. Report the path, the page count, and the queued questions.

If the user asked for a page range, not the whole PDF, extract it with
`scripts/extract-pdf-pages.py in.pdf out.pdf 1-20` after the build. That
script copies a contiguous range in **one** operation so fonts and images
stay shared. Never loop `insert_pdf` (or equivalent) one page at a time —
each iteration duplicates every XObject and a 2 MB file becomes 40 MB.
