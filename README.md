# scientific-fa-translation-skill

A [Cursor Agent Skill](https://cursor.com/docs/skills) for academic
English → scientific Persian, with a print-ready RTL PDF.

This repository is the Linux/macOS skill. On **Windows**, use
[KiaroSama/scientific-fa-translation-skill](https://github.com/KiaroSama/scientific-fa-translation-skill)
instead — that fork carries the PowerShell toolchain.

Canonical clone:
[isArman/scientific-fa-translation-skill](https://github.com/isArman/scientific-fa-translation-skill).

Cursor discovers skills at `/home/$USER/.cursor/skills/<skill-name>/SKILL.md`,
exactly one level deep. This repository **is** that skill: `SKILL.md`
sits at the clone root, so the install is a clone *into* the skills
directory — not *as* it.

## Install

```bash
mkdir -p /home/$USER/.cursor/skills
cd /home/$USER/.cursor/skills
git clone https://github.com/isArman/scientific-fa-translation-skill.git
```

That yields:

```text
/home/$USER/.cursor/skills/scientific-fa-translation-skill/SKILL.md
```

Do **not** clone this repository as `/home/$USER/.cursor/skills` itself.
Then `SKILL.md` would sit at the skills root and Cursor would not load it.

In Agent chat, ask to translate, or type `/scientific-fa-translation-skill`.
If the slash menu is empty — common on Cloud Agent follow-ups — write it
in prose: "use the scientific-fa-translation-skill". After `git pull`,
start a **new** agent on `main`; follow-ups in a running agent do not
reliably reload skills.

## What it does

Translates papers, articles, books, and technical documentation into
formal scientific Persian, and reviews finished translations against the
same rules. Cursor chat is only a short status note plus the output path;
it is not the RTL surface.

**Deliverable.** A printable PDF at `/home/$USER/Documents/books/<slug>.pdf`.
Preferred engine XeLaTeX + `xepersian` (selectable text); Chromium then WeasyPrint on the
RTL HTML template when TeX is absent (display-correct; copy-paste reverses Persian). Run `scripts/preflight.sh` to see
which of those exist on the machine before planning a build.

**A job.** Infer **three jobs** and one **subject** from the source
(DevOps, networking, Linux + nginx — not a pack). Lock keep-English
calques in that tree's `terms.tsv` before drafting. Composer and Grok
draft; Luna judges diffs only
([`references/ensemble.md`](references/ensemble.md)). Then
`scripts/build-pdf.sh` lints and will not copy a PDF if check, figure
prep, or `--verify` fail.

**Terminology.** Named artifacts, acronyms, formulas, the subject's
lexicon at every level, and — at `system-docs` — those jobs' field terms
and their operation verbs stay English in an LTR isolate. Generic
document chrome, narrative verbs, and conceptual explanation are Persian.
The ordered decision procedure is
[`references/terminology.md`](references/terminology.md); house lists
are in `glossary.md`. Nothing restates the policy, so there is one place
to change it.

**Enforcement.** `scripts/check-fa.py --level <level> --terms terms.tsv
--manifest manifest.txt --strict` fails the build on the mechanical
rules (orthography, calques, half-translations, English `-s` plurals,
split isolates, un-isolated Latin and number clusters, listing
direction, missing images, figure direction, full-page rasters,
terminology drift). `--strict` requires the terms ledger and the figure
manifest. The checklist in `SKILL.md` is only the five items a machine
cannot judge. `tests/run.sh` keeps the checker honest.

```bash
scripts/preflight.sh
scripts/check-fa.py doc.tex --level system-docs --terms terms.tsv --manifest manifest.txt --strict
scripts/build-pdf.sh doc.tex my-slug --verify
bash tests/run.sh
```

## Cursor token estimate

These numbers are for **Cursor Agent** usage with this skill (input +
output tokens Cursor counts in the editor). They are not OpenAI API
pricing, not a ChatGPT session, and not a quote. Tool calls that only
run `check-fa.py` or XeLaTeX cost **CPU, not tokens**. Retries, a second
agent after `git pull`, or pasting the whole source into chat will push
the real figure up; the Cursor usage dashboard is the source of truth.

**Unit.** English **source words** in the body that will be translated
(skip the bibliography count; it is copied, not rewritten). Pages are a
rough check only: technical prose is about **400 English words per
source page** (figures, listings, and whitespace make pages a worse
meter than `wc -w` on the extracted text).

**Rule of thumb**, following [`references/ensemble.md`](references/ensemble.md)
(Composer + Grok bake-off on ~700 words, one primary for the rest,
runner-up on ~10 % deltas, Luna on diffs only, parent agent loads
`SKILL.md` once):

```text
Cursor tokens ≈ 7 × (English source words) + 15,000
```

The `15,000` is roughly skill load + the bake-off. The `7×` covers
reading the source, writing Persian + TeX/`<span dir="ltr">` markup,
orchestrator notes, and the small second-pass. A short piece (under
~800 words) is **only** the bake-off: both translators run on the whole
span, so use about **10 × words + 8,000** instead.

| Source (order of magnitude) | Words | Pages (~400 w/p) | Cursor tokens |
| --- | ---: | ---: | ---: |
| Short paper / chapter | 3,000 | ~8 | ~40,000 |
| Install guide / long article | 16,000 | ~40 | ~130,000 |
| Book (e.g. ~174 pp) | 70,000 | ~175 | ~500,000 |

Expect a band of roughly **0.6× to 1.5×** that column: dense code and
tables inflate markup; a clean narrative sits lower; Cloud Agent
follow-ups that reload the skill sit higher.

## Layout

```text
SKILL.md
assets/rtl-document.tex        assets/rtl-document.html
references/terminology.md      policy: keep English vs write Persian
references/glossary.md         house lists
references/term-pairs.tsv      forbidden calques, machine-readable
references/scientific-style.md register, orthography, mechanics
references/rtl-bidi.md         isolation rules
references/pdf-output.md       engines, fonts, verification
references/source-ingest.md    fetching and extracting the source
references/long-documents.md   sectioning, resume, ambiguity queue
references/ensemble.md         Composer + Grok draft; Luna judges diffs
references/review.md           reviewing a finished translation
scripts/preflight.sh           what this machine can build
scripts/check-fa.py            mechanical checker
scripts/check-pdf-text-order.py  copy-paste order (pdftotext -raw)
scripts/prepare-figures.py     flatten alpha; catch pdfimages negatives
scripts/crop-source-figures.py crop artwork; never embed a full source page
scripts/extract-pdf-pages.py   page-range PDF without duplicating XObjects
scripts/build-pdf.sh           lint, compile, and verify (fails closed)
scripts/fetch-vazirmatn.sh     font for the HTML path
tests/                         checker regression tests
```

## License

MIT. See [LICENSE](LICENSE). Vazirmatn, fetched by
`scripts/fetch-vazirmatn.sh`, is under the SIL Open Font License 1.1; keep
its licence beside the font files when shipping HTML.
