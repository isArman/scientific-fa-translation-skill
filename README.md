# scientific-fa-translation-skill

This repository is for Linux and macOS. On **Windows**, use
[KiaroSama/scientific-fa-translation-skill](https://github.com/KiaroSama/scientific-fa-translation-skill)
instead — that fork carries the PowerShell toolchain.

A [Cursor Agent Skill](https://cursor.com/docs/skills) for academic
English → scientific Persian, with print-ready RTL.

Cursor discovers skills at `/home/$USER/.cursor/skills/<skill-name>/SKILL.md`,
exactly one level deep. This repository **is** that skill: `SKILL.md`
sits at the clone root, so the install is a clone *into* the skills
directory — not *as* it.

## Install

```bash
mkdir -p /home/$USER/.cursor/skills
cd /home/$USER/.cursor/skills
git clone https://github.com/<owner>/scientific-fa-translation-skill.git
```

`<owner>` is the GitHub account that hosts this repository (see the
address on the repo page). That yields:

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
Preferred engine XeLaTeX + `xepersian`; Chromium then WeasyPrint on the
RTL HTML template when TeX is absent. Run `scripts/preflight.sh` to see
which of those exist on the machine before planning a build.

**Terminology.** Infer **three jobs** and one **subject** from the source
(DevOps, networking, Linux + nginx, not a pack). Named artifacts, acronyms, formulas, the subject's
lexicon at every level, and — at `system-docs` — those jobs' field terms
and their operation verbs stay English in an LTR isolate. Generic
document chrome, narrative verbs, and conceptual explanation are Persian.
The ordered decision procedure, the field-term test, and the two levels
are in [`references/terminology.md`](references/terminology.md); the
house lists are in `glossary.md`. Nothing restates the policy, so there
is one place to change it.

**Enforcement.** `scripts/check-fa.py --level <level> --terms terms.tsv
--manifest manifest.txt --strict` fails the
build on the mechanical rules — orthography, forbidden calques at that
level, half-translated noun phrases, English `-s` plurals of kept terms,
split isolates, un-isolated Latin runs and number clusters, RTL listings,
mirrored artwork, missing images, figure direction, full-page rasters, terminology drift.
`--pairs` and `--terms` merge onto the house list. `--strict` requires
the terms ledger and the figure manifest. `scripts/build-pdf.sh` runs
that lint (and `prepare-figures.py --check` when `figures/` exists)
before it will copy a PDF. The checklist left in `SKILL.md` is
only the five items a machine cannot judge.
`tests/run.sh` keeps the checker honest with clean and deliberately
broken fixtures.

```bash
scripts/preflight.sh
scripts/check-fa.py doc.tex --level system-docs --terms terms.tsv --manifest manifest.txt --strict
scripts/build-pdf.sh doc.tex my-slug --verify
bash tests/run.sh
```

Layout:

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
references/review.md           reviewing a finished translation
scripts/preflight.sh           what this machine can build
scripts/check-fa.py            mechanical checker
scripts/prepare-figures.py     flatten alpha; catch pdfimages negatives
scripts/crop-source-figures.py crop artwork; never embed a full PDF page
scripts/extract-pdf-pages.py   page-range PDF without duplicating XObjects
scripts/build-pdf.sh           lint, compile, and verify (fails closed)
scripts/fetch-vazirmatn.sh     font for the HTML path
tests/                         checker regression tests
```

## License

MIT. See [LICENSE](LICENSE). Vazirmatn, fetched by
`scripts/fetch-vazirmatn.sh`, is under the SIL Open Font License 1.1; keep
its licence beside the font files when shipping HTML.
