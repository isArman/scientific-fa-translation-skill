# scientific-fa-translation-skill

This repository is a single Cursor skill. `SKILL.md` is at the clone
root so it is discoverable when cloned into `/home/$USER/.cursor/skills`:

```text
/home/$USER/.cursor/skills/scientific-fa-translation-skill/SKILL.md
```

Cursor only looks one level deep. Do not nest this clone under another
folder inside `/home/$USER/.cursor/skills`, and do not clone it *as*
`/home/$USER/.cursor/skills` itself.

When the user wants to translate a paper, article, book, or technical
document into scientific Persian — or asks for RTL, چاپ, or a PDF, or
asks whether a finished Persian translation follows the rules — read and
follow `SKILL.md` before producing output. Do this even if
`/scientific-fa-translation-skill` is missing from the slash menu.

Do not use that skill for coding, commits, UI copy, or casual chat.

## Working on the skill itself

- The terminology policy has one owner: `references/terminology.md`.
  Lists live in `glossary.md`; forbidden Persian calques live in
  `references/term-pairs.tsv`. Infer a document's specialty from the
  source; do not add a domain pack. Do not restate the policy in a
  second file.
- A new rule that a machine could check belongs in `scripts/check-fa.py`
  with a fixture in `tests/fixtures/`, not only in prose. Run
  `bash tests/run.sh` after touching the checker or a fixture. Pass
  `--level journal` when the fixture is a paper, not a sysadmin guide.
- Keep `SKILL.md` short. It is loaded in full whenever the skill
  triggers; detail belongs in `references/`.

## Cursor Cloud specific instructions

This repo is tooling for a Cursor skill, not a running service. The dev
loop is lint → test → build a PDF; there is nothing to keep running.

- Lint / test / build commands live in `README.md` and
  `.github/workflows/ci.yml`; use those rather than reinventing them.
  Lint is `shellcheck -S warning $(git ls-files '*.sh')` plus
  `python3 -m py_compile $(git ls-files '*.py')`; tests are
  `bash tests/run.sh`; the deliverable is built with
  `scripts/build-pdf.sh <file.tex|file.html> <slug> --verify` after
  `scripts/check-fa.py <file> --strict`. Run `scripts/preflight.sh` to
  see which engines/fonts/tools the machine has.
- No repository-level package deps: everything is Python 3 stdlib or
  system packages baked into the environment (`shellcheck`,
  `python3-pil`/Pillow, `poppler-utils`, `fonts-vazirmatn`,
  `texlive-xetex` + `texlive-lang-arabic` for xepersian, `latexmk`,
  `google-chrome`). The boot-time update script is intentionally a no-op.
- Preferred `.tex`/XeLaTeX path is currently blocked by a toolchain
  mismatch, not a missing dependency: the shipped `assets/rtl-document.tex`
  sets a Latin `\setdigitfont` (Western digits, by design), which TeX
  Live 2023's xepersian 25.0 rejects with
  `xepersian-mathdigitspec Error: The font "TeX Gyre Termes" does not
  contain U+06F0`. Build via the documented HTML path instead
  (`scripts/build-pdf.sh doc.html <slug> --verify`, Chromium engine) to
  produce a print-ready RTL PDF. Only touch the template's digit-font
  handling if the `.tex` path itself is the task.
- Headless `google-chrome` prints harmless `dbus`/`UPower` errors to
  stderr in this VM; the PDF is still written — look for the
  "bytes written to file …" line, not the noise.
- `scripts/fetch-vazirmatn.sh fonts/` reuses the installed Vazirmatn
  system face offline (no network needed) to drop the TTFs beside an
  HTML build. `--verify` rasterises sample pages to PNG; judge RTL from
  those images, never from `pdftotext`.
- A page-range PDF is `scripts/extract-pdf-pages.py in.pdf out.pdf 1-20`
  after the full build. Never loop `insert_pdf` per page — that
  duplicates XObjects and explodes file size.
