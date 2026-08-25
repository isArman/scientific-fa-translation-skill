# Getting the source in

Every real invocation of this skill starts from a URL, not from pasted text,
and the first thing that goes wrong is ingestion — a page times out, a PDF
loses its figures, a multi-page guide is silently truncated. Do this before
translating a single sentence.

## Working tree

One directory per job, outside the deliverable path:

```text
/home/$USER/Documents/books/_work/<slug>/
  source/            fetched originals, unmodified
  figures/           images copied or extracted from the source
  inventory.md       structure count, written during ingestion
  manifest.txt       one image basename per line
  terms.tsv          long jobs only: source term → chosen form → count
  progress.md        section ledger (see long-documents.md)
  doc.tex / doc.html the translation being built
```

The PDF still lands at `/home/$USER/Documents/books/<slug>.pdf`. Working files are not
the deliverable and never the only copy of anything.

## Fetching

| Source | How |
| --- | --- |
| Web page | the agent's fetch tool first; `curl -fsSL` as fallback |
| PDF | `curl -fsSL -o source/doc.pdf <url>` |
| Multi-page docs site | fetch each page listed in its own nav/TOC, in order |
| Local file | copy into `source/`, never edit in place |

A timeout is not a dead end and not a licence to translate from memory. In
order: retry once, try the print or raw variant of the URL, try the project's
repository copy of the same document, then ask the user for the file. If a
section cannot be fetched, say which one and stop — a translation with a
silently missing section is worse than a late one.

## Extracting a PDF source

```bash
pdftotext -layout source/doc.pdf source/doc.txt   # text, reading order kept
pdfinfo source/doc.pdf                            # page count for inventory
```

`-layout` matters: without it, two-column papers interleave. Do not treat
`pdftotext` output of an RTL document as visual truth — that applies to
checking your own output, not to reading an English source.

## Extracting figures

The destination PDF must show the **same pixels the reader sees on the
figure**, not the whole source page around it.

1. **Prefer the original asset.** If the source is HTML, or the PDF has an
   HTML companion, copy the `<img src>` / SVG files. Those are the figures.
2. **`pdfimages` is last resort**, and it lies. It emits Decode-inverted
   samples (a light diagram becomes a black rectangle) and leftover
   grayscale soft-masks that are not printed figures. Skip mask/smask
   companions. Never ship those.
3. **Rasterise the source page** (`pdftoppm -png -r 150 -f N -l N`) and
   compare each extracted file with that page. If the extract is a
   photographic negative of the figure, it is wrong. That raster is
   **ground truth for checking**, not a file to embed.
4. **Crop to the artwork.** A figure is the diagram, screenshot, or photo.
   It is not the running header, English body, source caption, or page
   number. Never point `<img>` / `\includegraphics` at a full-page
   `pdftoppm` (`srcpage-027.png`, `page-12.png`). Map each figure to its
   PDF page by reading `pdftotext -f N -l N` until the caption (`Figure
   1.1`) appears — do not guess an offset from printed page numbers.

   ```bash
   scripts/crop-source-figures.py source/doc.pdf --out figures/artwork \
       --map figures-map.tsv --cover --author-page 18
   ```

   `figures-map.tsv` is `figure_id`, optional printed page, then **PDF page**.
   Two figures on one page become two rows with the same PDF page; crops
   are top-to-bottom. Cover art is the plate only (no English title
   spine). An author portrait is the headshot, not the “about the author”
   page.
5. **Flatten before the print build:**

   ```bash
   scripts/prepare-figures.py figures/artwork --check
   ```

   `--check` fails on leftover alpha (WeasyPrint/Cairo and xepersian paint
   it onto black) and on mostly-black dumps. After confirming against the
   source page that a dark dump is inverted, not a real dark photograph:

   ```bash
   scripts/prepare-figures.py figures/artwork --invert-dark
   ```

```bash
pdfimages -png -p source/doc.pdf figures/img      # last-resort rasters
pdftoppm -png -r 150 -f 12 -l 12 source/doc.pdf /tmp/page-12  # check only
scripts/crop-source-figures.py source/doc.pdf --out figures/artwork --map figures-map.tsv
scripts/prepare-figures.py figures/artwork --check
```

The checker fails (`full-page-figure`) if the translation still references
`srcpage-N.png` or `page-N.png`.

## Structure inventory

Write `inventory.md` while the source is open, before drafting: counts of
headings, figures, tables, equations, code listings, footnotes, and
references, plus the page or section they live in. **List the table of
contents** (`contents`, `brief contents`) as its own front-matter section
when the source has one. Translate it and print it; dropping those pages
is a missing section. It costs a minute and it is the only way to answer
«is anything missing?» at the end. Then:

```bash
ls figures/ | sed 's/.*\///' > manifest.txt
scripts/check-fa.py doc.tex --level <level> --manifest manifest.txt --strict
```

The checker reports any manifest image that never made it into the
translation, which is the failure mode that a reader notices first.

## Several sources, one document

When the user gives more than one URL and wants a single PDF (a common ask):

- Keep source order as given unless the documents have an obvious
  reading order of their own.
- One top-level section per source, with the source title as the heading —
  translated or kept English by the normal heading rule.
- Do not merge or deduplicate overlapping prose; each source keeps its own
  section even when they repeat each other.
- One shared `terms.tsv` across all sources when the merged document is
  long, so terminology is consistent. Do not write a glossary file.

## Licence and provenance

Capture this during ingestion, not at the end. Record in `inventory.md` and
reproduce it on the colophon page of the PDF: source title, URL, author or
project, licence, and retrieval date. Documentation is usually reusable but
not unattributed — OpenStack docs are CC BY, BIPs carry their own terms, and
a translation is a derivative work. The templates ship a colophon block for
exactly this.
