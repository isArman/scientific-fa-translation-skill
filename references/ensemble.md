# Ensemble translation

How this skill uses three Cursor models without spending tokens on five
full drafts of the same book. Terminology still belongs only in
`terminology.md`. Mechanical checks still belong only in `check-fa.py`.
This file owns **who writes** and **who picks**.

Override the model slugs only when the user names different ones.

## Roles

| Role | Model | Cursor slug | May write the print source? |
| --- | --- | --- | --- |
| Translator A | Composer | `composer-2.5` | Yes, a candidate |
| Translator B | Grok | `cursor-grok-4.6-high` | Yes, a candidate |
| Judge | Luna | `gpt-5.6-luna-medium` | **No** — select or mix, never a third draft |

The parent agent (whatever the user is chatting with) is the
orchestrator: ingest, `terms.tsv`, launching subagents, lint, copy of
the winner into `parts/`, `build-pdf.sh`. Do not spend Composer, Grok,
or Luna on ingest.

If a slug is not in the Task tool's allowed list, skip that role and
tell the user which models were available; do not silently substitute
Claude or GPT-5.6 Sol.

## Token rule

Spend tokens on **disagreement**, not on rewriting the whole source
three times.

- Do **not** paste `SKILL.md` or the `references/` tree into a
  translator or judge prompt. They get: the English span they must
  translate or compare, `terms.tsv`, the level, the three jobs and
  subject, and the short brief below.
- `check-fa.py --strict --terms --manifest` runs on every candidate
  **before** Luna sees it. A failing candidate is out. Luna does not
  re-check orthography, calques, isolates, or figures.
- Luna never receives five full texts. Align by sentence (or by
  paragraph when a sentence split does not line up) and send only the
  rows that differ, each with the English source sentence.
- Raster / PDF verification stays at the end, on the orchestrator.

## Brief for translators (paste as-is)

```text
Translate this English span into academic Persian for a print .tex
(or .html) part. Follow terms.tsv exactly: keep-English output stays
in one \en{…} / dir=ltr isolate; forbidden_fa strings must not appear.
Do not add, omit, or soften claims; keep hedges (may, might, suggest,
remain unknown). Western digits. Write only the translation for this
span, not a glossary and not a chat essay. If a claim-changing
ambiguity would change the meaning, leave % TODO(ambiguity): … and
do not guess.
```

## Brief for Luna (paste as-is)

```text
You are the judge, not a translator. Do not write a new Persian draft.
Each row is English plus Composer vs Grok (only the rows that differ,
and only candidates that already passed check-fa.py). For this
document's five judgement items, pick winner: composer, grok, or mix
with explicit sentence ranges. Prefer the reading that does not add,
drop, or harden a claim and that keeps terms.tsv. One short reason
per contested row. Output only the decision.
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

4. **Lock.** Orchestrator writes the chosen text into `parts/NN-*.tex`,
   lints once more, sets `progress.md` to `done`. Composer and Grok
   do not touch that file again.

Chat stays a short pointer. Do not paste competing drafts into chat.

## What Luna is not for

Luna does not invent terminology, does not flatten figures, does not
run XeLaTeX, and does not "improve" a green candidate into a third
style. Review of a **finished** PDF is still `review.md` (orchestrator
+ checker + rasters), not a second Luna pass over the whole book.
