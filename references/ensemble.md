# Ensemble translation

How this skill uses three Cursor models without spending tokens on five
full drafts of the same book. Terminology still belongs only in
`terminology.md`. Mechanical checks still belong only in `check-fa.py`.
This file owns **who writes**, **who picks**, and **who reads for
fluency**. Register fluency is a model judgement — never a fixed word
list in the checker.

Override the model slugs only when the user names different ones.

## Roles

| Role | Model | Cursor slug | May write the print source? |
| --- | --- | --- | --- |
| Translator A | Composer | `composer-2.5` | Yes, a candidate |
| Translator B | Grok | `cursor-grok-4.6-high` | Yes, a candidate |
| Judge | Luna | `gpt-5.6-luna-medium` | **No** — select or mix, never a third draft |
| Fluency reader | Grok by default | `cursor-grok-4.6-high` | **No** — flags only; primary revises |

The fluency reader must **not** be the model that wrote the locked
Persian. Default: Grok reads when Composer was primary; Composer reads
when Grok was primary. If the user names a fluency model explicitly,
use that slug instead — still never the writer of the text under review.

The parent agent (whatever the user is chatting with) is the
orchestrator: ingest, `terms.tsv`, launching subagents, lint, fluency
read, copy of the winner into `parts/`, `build-pdf.sh`. Do not spend
Composer, Grok, or Luna on ingest.

If a slug is not in the Task tool's allowed list, skip that role and
tell the user which models were available; do not silently substitute
Claude or GPT-5.6 Sol.

## Token rule

Spend tokens on **disagreement**, not on rewriting the whole source
three times.

- Do **not** paste `SKILL.md` or the `references/` tree into a
  translator, judge, or fluency-reader prompt. They get: the English
  span they must translate or compare (translators/Luna), or the
  Persian prose under review (fluency reader), plus `terms.tsv`, the
  level, the jobs and subjects, and the short brief below.
- `check-fa.py --strict --terms --manifest` runs on every candidate
  **before** Luna sees it. A failing candidate is out. Luna does not
  re-check orthography, calques, isolates, or figures.
- Luna never receives five full texts. Align by sentence (or by
  paragraph when a sentence split does not line up) and send only the
  rows that differ, each with the English source sentence.
- The fluency reader sees **Persian prose**, not TeX plumbing. Strip
  `\en{…}` / `\lr{…}` / `dir=ltr` isolates to a placeholder like
  `‹EN›` so bidi markup does not distract the judgement. Do not paste
  the English source unless a flagged line needs claim-check against it.
- Raster / PDF verification stays at the end, on the orchestrator.

## Brief for translators (paste as-is)

```text
Translate this English span into academic Persian for a print .tex
(or .html) part. Follow terms.tsv exactly: keep-English output stays
in one \en{…} / dir=ltr isolate; forbidden_fa and deprecated forms
must not appear; honour preferred status per concept.
Context already announced: level, jobs, subjects, genre
(tutorial|reference|paper).
Locked voice (scientific-style.md Canonical manner + fluency-gold.md):
clear فارسی معیار — short everyday verbs (می‌خواهد، می‌دهد، نشان بدهد،
شروع می‌کند), not elevated ones (برمی‌انگیزد، ارائه کند، آغاز می‌کند).
Split long English sentences. Lead with a Persian frame; keep
job/subject terms English; do not Persianise them and do not
over-English ordinary prose (امنیت not \en{security} unless locked).
Prefer collocations in scientific-style.md (\en{request} بفرستد,
404 بدهد). Prefer «یک URI» over awkward URIای glue; never Latin+ی
ezafe. Do not add, omit, or soften claims; keep hedges (may, might,
suggest, remain unknown). Western digits. Write only the translation
for this span, not a glossary and not a chat essay. If a claim-changing
ambiguity would change the meaning, leave % TODO(ambiguity): … and do
not guess.
```

## Brief for Luna (paste as-is)

```text
You are the judge, not a translator. Do not write a new Persian draft.
Each row is English plus Composer vs Grok (only the rows that differ,
and only candidates that already passed check-fa.py). For this
document's six judgement items, pick winner: composer, grok, or mix
with explicit sentence ranges. Prefer the reading that does not add,
drop, or harden a claim and that keeps terms.tsv preferred forms.
When both readings are equally faithful, prefer Canonical manner +
fluency-gold.md: shorter clauses, everyday scholarly verbs, English
field terms kept, no ornate or translationese Persian, no over-English
of ordinary words. One short reason per contested row. Output only
the decision.
```

## Brief for fluency reader (paste as-is)

```text
You are a fluency reader, not a translator and not a terminology
checker. Read the Persian prose only. Gold standard: Canonical manner
in scientific-style.md and the paragraphs in fluency-gold.md — plain
formal فارسی معیار with short verbs (نشان بدهد / شروع می‌کند, not
ارائه کند / آغاز می‌کند), split sentences, English field terms left
as ‹EN›, collocations like ‹EN› بفرستد / 404 بدهد, no literary padding.
FLAG awkward, ornate, or translationese Persian; FLAG Persian calques
of kept terms; FLAG ugly Latin+ی glue; FLAG over-English (ordinary
dictionary words left as ‹EN› without a terms.tsv reason).
Do not hunt only a fixed word list — judge the whole sentence.
For each problem span, output one line:
  FLAG | <exact Persian span> | <why it feels unnatural> | <optional simpler Persian that keeps the same claim>
If nothing is wrong, output only: OK
Do not rewrite the whole passage. Do not change hedges, numbers, or
kept English terms (shown as ‹EN›). Do not invent science.
```

## Procedure

`terms.tsv` is already written and shown to the user. Then:

1. **Bake-off (once per document).** Take one representative English
   span of about 500–800 words (a claims-heavy stretch with at least
   one hedge, not a contents page). Composer and Grok translate it in
   parallel into sibling files (`bakeoff.composer.tex`,
   `bakeoff.grok.tex`). Lint both. Luna sees the diff only and names
   the **primary** translator and the **runner-up**. If the whole
   source is shorter than that span, the bake-off *is* the
   translation: Luna's winner is the deliverable body; skip step 2.

2. **Rest of the document — primary only.** The primary translates
   each remaining part into `parts/NN-*.tex` (sectioning in
   `long-documents.md`). Lint each part as it finishes. Do not restart
   a `done` part.

3. **Runner-up only on deltas.** The runner-up does **not** retranslate
   the part. Give it only: sentences the primary marked
   `TODO(ambiguity)`, plus at most a fixed sample (10 % of paragraphs
   in that part, cap 12 sentences). Lint those snippets. Luna sees
   those diffs only and may swap in the runner-up's sentence.

4. **Fluency read (required).** After the part is chosen and lints
   clean, send its Persian prose (or, for long parts, every Nth
   paragraph plus any paragraph the orchestrator finds dense — at least
   ~400 words, cap ~1200) to the fluency reader with the brief above (gold: fluency-gold.md).
   The reader returns `OK` or `FLAG` lines. The **primary** revises only
   flagged spans, keeping claims and hedges intact; preferred simpler
   Persian from the FLAG line is a suggestion, not an order. Re-lint.
   If the reader and primary disagree on whether a change softens a
   claim, queue it for the user — do not guess. Record
   `fluency: ok|revised` in `progress.md` for that part.

5. **Lock.** Orchestrator writes the chosen text into `parts/NN-*.tex`,
   lints once more, sets `progress.md` to `done` only when fluency is
   `ok` or `revised`. Composer and Grok do not touch that file again
   except the primary's fluency fixes in step 4.

Chat stays a short pointer. Do not paste competing drafts into chat.

## What Luna and the fluency reader are not for

Luna does not invent terminology, does not flatten figures, does not
run XeLaTeX, and does not "improve" a green candidate into a third
style. The fluency reader does not replace `check-fa.py`, does not
decide keep-English terms, and does not author a new draft of the
chapter. Review of a **finished** PDF is still `review.md`
(orchestrator + checker + rasters + a fluency-reader sample), not a
second full rewrite.
