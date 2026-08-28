# RTL and bidirectional isolation

Precise right-to-left layout is not `text-align: right`. Persian is RTL;
English terms, digits, math, and URLs are LTR. The Unicode Bidirectional
Algorithm will misplace punctuation and parentheses unless every LTR run
is isolated.

**Cursor chat is not the RTL surface.** Do not right-align the
conversation. For papers, articles, and books the deliverable is a
PDF (`references/pdf-output.md`) with maximum bidi precision.

When the print engine is XeLaTeX, isolate with `\lr{…}` / `\en{…}` and
put listings in a `latin` environment (see `assets/rtl-document.tex`).
The HTML rules below apply to an explicit HTML ask or the Chromium /
WeasyPrint print fallback (`assets/rtl-document.html`).

Most of this file is machine-checked. Run
`scripts/check-fa.py doc.tex --level <level> --terms terms.tsv --manifest manifest.txt --strict` before reading
further — it reports un-isolated Latin runs, un-isolated number clusters,
split clusters, RTL listings, mirrored artwork, English `-s` plurals of
kept terms, and leftover Persian ezafe on English tokens, so the reading
below is for the cases that need judgement.

**Engine caveat.** WeasyPrint does not implement `unicode-bidi: isolate`
and warns about it on every run. The `dir="ltr"` **attribute** is what
actually does the work there; keep the CSS property as well for Chromium
and browsers. See the measured cases in `pdf-output.md`.

## Document root

Use `assets/rtl-document.html`. The root must be:

```html
<html lang="fa" dir="rtl">
```

CSS on that template:

- `body`: `direction: rtl; unicode-bidi: isolate;`
- `.ltr`, `pre`, `code`, `kbd`, `samp`, `math`, `img`, `svg`: `direction: ltr; unicode-bidi: isolate;`
- `h1–h4`: `text-align: right` so an English-only heading isolate stays
  on the right edge of a Persian page
- `pre`: `white-space: pre-wrap; word-break: break-word;` — on paper,
  `overflow-x: auto` does nothing and long listing lines are simply cut
  off at the margin

Never set `dir="rtl"` or `text-align: right` on `pre`, `code`, or a
wrapper around a listing.

## Code blocks are never RTL

This is a hard rule. Fenced listings, `pre`, file dumps, REPL
sessions, and algorithm listings stay left-to-right and left-aligned
even though the document is Persian.

```html
<!-- Required HTML shape (Chromium fallback) -->
<pre dir="ltr"><code>def fit(x):
    return x @ w
</code></pre>
```

```tex
% Required XeLaTeX shape (PDF)
\begin{latin}
\begin{Verbatim}[fontsize=\small,frame=single]
def fit(x):
    return x @ w
\end{Verbatim}
\end{latin}
```

```html
<!-- Forbidden -->
<pre dir="rtl">...</pre>
<pre style="text-align: right">...</pre>
<pre>  <!-- inherits RTL from body; still wrong without dir="ltr" -->
```

Also:

- Do not translate comments, identifiers, or strings inside code.
- Do not reorder glyphs, reverse indentation, or convert spaces.
- Inline code in Persian prose is LTR: `<code dir="ltr">fit(x)</code>`
  or wrap with `<span dir="ltr"><code>…</code></span>`.
- Markdown fallback: do not leave a bare ` ``` ` fence inside a
  `dir="rtl"` div. Wrap it in `<pre dir="ltr"><code>`.

## Isolate every LTR run

Wrap each English term, **whole technical collocation**, acronym, number
cluster, citation key, formula, URL, file path, and inline code. A
collocation is one isolate, not one span per word:

```html
<span dir="ltr">composable API</span>ها
<span dir="ltr">Kubernetes cluster</span>
```

```html
<span dir="ltr">gradient descent</span>
<span dir="ltr">Adam (Kingma &amp; Ba, 2015)</span>
<span dir="ltr">p &lt; 0.05</span>
<span dir="ltr">https://doi.org/10.0000/example</span>
```

XeLaTeX (PDF):

```tex
\en{gradient descent}
\en{Adam (Kingma \& Ba, 2015)}
\en{p < 0.05}
```

`<bdi>` is acceptable when the span is a single proper name. Prefer
`<span dir="ltr">` (HTML) or `\lr`/`\en` (TeX) for anything with
parentheses, punctuation, or digits.

A whole English bibliography, code listing, or equation block gets
`dir="ltr"` on the HTML container, or a `latin` environment in TeX,
not a token-by-token wrap.

## Joined LTR runs (one isolate)

If two English tokens are linked by `/`, `-`, `->`, parentheses, **or a
space**, wrap the **whole** cluster. Two LTR isolates with only a space
between them reverse on an RTL page the same way a slash does: a heading
marked up as `3.1` + `The OpenStack services` prints as
`The OpenStack services 3.1`.

This is the one bidi rule confirmed to break real output rather than
merely being risky. Rendered on a Persian page, two spans around `OP_IF`
and `OP_NOTIF` with a slash between them print as `OP_NOTIF/OP_IF`; a
single span around `OP_IF/OP_NOTIF` prints correctly. Two spans around
`3.1` and `The OpenStack services` print reversed; one span around
`3.1 The OpenStack services` prints correctly. Other cases in the same
test — a trailing acronym before the sentence period, a parenthesised
citation, an arrow inside one span — came out right either way. Spend the
attention here.

```html
<!-- Wrong: renders as OP_NOTIF/OP_IF, Title 3.1, and :)2026-08-09( 1.0.1 -->
<span dir="ltr">OP_IF</span>/<span dir="ltr">OP_NOTIF</span>
<h2><span dir="ltr">3.1</span> <span dir="ltr">The OpenStack services</span></h2>
<strong><span dir="ltr">1.0.1</span></strong> (<span dir="ltr">2026-08-09</span>)

<!-- Right -->
<span dir="ltr">OP_IF/OP_NOTIF</span>
<h2><span dir="ltr">3.1 The OpenStack service</span>ها</h2>
<span dir="ltr">1.0.1 (2026-08-09)</span>
<span dir="ltr">STARTED -&gt; LOCKED_IN</span>
<span dir="ltr">1109/2016 (55%)</span>
<span dir="ltr">256/257</span>
```

```tex
\en{OP_IF/OP_NOTIF}
\en{3.1 The OpenStack service}ها
\en{1.0.1 (2026-08-09)}
\en{STARTED -> LOCKED_IN}
```

Same rule for `Taproot/P2TR`, `300-400`, `2017–2024`,
`Adam (Kingma \& Ba, 2015)`, and a numbered English heading
(`3.2.1 Conceptual architecture`). Persian separators between Persian
words (`سیاست/پالایه`, `و/یا`) stay outside LTR spans.

Do not treat `pdftotext` as visual truth on an RTL PDF. Rasterize a page
(`pdftoppm -png -f 1 -l 1 file.pdf /tmp/p`) and look at the PNG.

## Wrong vs right

Parentheses and the sentence period are the usual failures.

```html
<!-- Wrong: parens and the period attach to the English run -->
الگوریتم Adam (Kingma &amp; Ba, 2015) استفاده شد.

<!-- Right -->
الگوریتم <span dir="ltr">Adam (Kingma &amp; Ba, 2015)</span> استفاده شد.
```

```tex
الگوریتم \en{Adam (Kingma \& Ba, 2015)} استفاده شد.
```

```html
<!-- Wrong: trailing English steals the Persian period -->
نتایج با RMSE بهتر شد.

<!-- Right -->
نتایج با <span dir="ltr">RMSE</span> بهتر شد.
```

If a sentence *ends* on an LTR span and the period still renders on the
wrong side after isolation, append an RLM (U+200F) immediately after the
closing `</span>` and before `.`:

```html
این روش بر پایه <span dir="ltr">backpropagation</span>‏.
```

Do not scatter RLM/LRM through the file as decoration. Isolation first;
RLM only for a leftover end-of-sentence period.

## What must stay LTR

| Content | How |
| --- | --- |
| Technical English terms | `<span dir="ltr">` |
| Western digits and numeric ranges | `<span dir="ltr">3.14</span>`, `<span dir="ltr">2017–2024</span>` |
| Display/inline math | `dir="ltr"` on the math container; keep LaTeX source unchanged |
| Fenced code / `pre` | `dir="ltr"` on `<pre>` plus left-align; never RTL |
| XeLaTeX listing | `latin` + `verbatim` / `Verbatim`; never an RTL wrap |
| Inline `code` | `dir="ltr"` on `code`, or `\lr{\texttt{…}}` |
| Images / SVG | unchanged pixels; `dir="ltr"` on `<img>`; flatten alpha |
| URLs, DOIs, emails | `<span dir="ltr">` or `<a dir="ltr">` |
| File paths and identifiers | `<span dir="ltr">` |
| Reference list | a `dir="ltr"` section |

## Headings, lists, tables, figures

- Headings are RTL prose and stay physically right-aligned, even when the
  title is an English isolate. A numbered English title is **one** isolate:
  `<h2><span dir="ltr">3.1 The OpenStack service</span>ها</h2>`,
  never `3.1` in one span and the title in another. Two spans reverse on
  the page; WeasyPrint also packs a lone LTR heading to the left unless
  the heading has `text-align: right` (the HTML template sets that).
- Lists inherit RTL from `body`. Isolate LTR items or fragments per item.
- Table captions are RTL (`جدول 2. …`). Isolate the number: `جدول <span dir="ltr">2</span>.`
- Numeric table cells are LTR. Persian prose cells stay RTL.
- Do not reverse column order unless the user asks.
- Figure captions: `شکل <span dir="ltr">3</span>. …` Isolate any English
  term inside the caption. Do not end the caption with an English isolate
  followed by a Persian period (the period jumps left). End on Persian, or
  drop that period.
- The `<img>` / `<svg>` itself is not RTL content. Give it `dir="ltr"`
  (HTML) or wrap `\includegraphics` in `LTR` (XeLaTeX). Do not mirror it
  (`transform: scaleX(-1)` is forbidden). Center it on the page
  (`margin-inline: auto`); a block-level LTR image otherwise sits on the
  physical left. Width/height follow the artwork aspect. Flatten PNG alpha
  onto white before the print build (`scripts/prepare-figures.py`);
  engines composite leftover alpha onto black. Never embed a full source
  page as the figure.

```html
<figure>
  <img dir="ltr" src="figures/artwork/fig-3.png" alt="…" width="720" height="420">
  <figcaption>شکل <span dir="ltr">3</span>. معماری
  <span dir="ltr">transformer</span></figcaption>
</figure>
```

## Markdown fallback

Only when the user demands Markdown:

```html
<div lang="fa" dir="rtl">

متن فارسی با <span dir="ltr">transformer</span>.

<pre dir="ltr"><code>print(x)</code></pre>

<figure>
  <img dir="ltr" src="figures/artwork/fig-3.png" alt="…" width="720" height="420">
  <figcaption>شکل <span dir="ltr">3</span>. …</figcaption>
</figure>

</div>
```

GitHub-flavored Markdown will still break some bidi cases. Say so, and
prefer HTML. A bare Markdown fence inside a RTL container is not
enough; wrap listings in `<pre dir="ltr">`.

Never reverse English letter order by hand. Never rewrite `(Adam)` as
`)Adam(` to “fix” RTL.

## Self-check

0. Run `scripts/check-fa.py --level <level> --terms terms.tsv --manifest manifest.txt --strict` on the source file
   and clear every error. Steps 1–6 are the part it cannot see.
1. Open the HTML file or a rasterized PDF page, not the chat transcript
   and not `pdftotext` alone.
2. Scan every English island: parentheses enclose the English, not the
   Persian.
3. Sentence-final periods sit at the right edge of the Persian sentence.
4. Slash-, space-, or date-joined English still reads left-to-right
   (`OP_IF/OP_NOTIF`, `3.1 The OpenStack service`, `1.0.1 (2026-08-09)`).
5. Code blocks are LTR, left-aligned, and optically identical to the
   source listing. Images are the source pixels, unmirrored, uninverted,
   in source order — not a black rectangle.
6. No `ك` / `ي` introduced while editing markup.
