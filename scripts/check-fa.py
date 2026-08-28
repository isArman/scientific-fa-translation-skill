#!/usr/bin/env python3
"""fa-lint: mechanical checks for scientific Persian translation output.

Usage:
    check-fa.py FILE [FILE ...] [--level system-docs|journal]
                [--pairs FILE] [--terms FILE] [--strict] [--manifest FILE]

Accepts `.tex` and `.html`/`.htm` sources. Every rule here is one of the
mechanical items from the skill's quality checklist, so the checklist that
stays in SKILL.md is only the part a machine cannot judge.

`--level journal` drops one-word field-noun bans (`گره`, `پیاده‌سازی`,
`مجموعه داده`, …) so a paper that follows terminology.md does not fail.
`--pairs FILE` is added on top of `references/term-pairs.tsv`, never a
replacement. `--terms FILE` reads a job `terms.tsv`. Keep-English rows
must name a `forbidden_fa` calque; an empty calque column is an error,
not a skip. `--strict` requires `--terms` and `--manifest` (or
`terms.tsv` / `manifest.txt` next to the source). English `-s` plurals
of kept terms (`services`, `APIs`) fail; the stem plus ها after the
isolate is the surviving form.

Exit codes: 0 clean, 1 findings at error level, 2 usage error.

Suppress one finding by putting `fa-lint: allow <check-id>` (or
`fa-lint: allow all`) in a comment on the same or preceding line.
"""

from __future__ import annotations

import argparse
import bisect
import os
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

ZWNJ = "\u200c"
FA_RANGE = "\u0600-\u06ff\ufb50-\ufdff\ufe70-\ufeff"
FA_CHAR = re.compile(f"[{FA_RANGE}]")

ERROR, WARN = "error", "warn"

# Persian head nouns that, immediately followed by a Latin run, mean the
# source noun phrase was half-translated. Deliberately narrow: heads like
# «الگوریتم Adam» and «معماری transformer» are correct and must not fire.
HALF_TRANSLATION_HEADS = [
    "خوشه",
    "خوشه‌های",
    "سرویس‌های",
    "بسته‌های",
    "بستهٔ",
    "مخزن",
    "مخازن",
    "گره‌های",
    "نیازمندی‌های",
    "جریان‌های",
    "دیوارهای",
    "بلوک",
    "بلوک‌های",
]

# ZWNJ-less spellings of common verb forms. An explicit list avoids the false
# positives a generic «می» rule would produce on میان / میز / میلاد.
ZWNJ_VERBS = [
    "میشود", "میشوند", "میشد", "میکند", "میکنند", "میکنید", "میکنم",
    "میکرد", "میتوان", "میتواند", "میتوانند", "میتوانید", "میدهد",
    "میدهند", "میگیرد", "میگیرند", "میباشد", "میباشند", "میگردد",
    "میرود", "میآید", "میسازد", "میخواهد", "میگوید", "میداند",
    "میآورد", "میماند", "میافتد", "میپردازد", "میکنیم", "میدانیم",
    "نمیشود", "نمیشوند", "نمیکند", "نمیکنند", "نمیتوان", "نمیتواند",
    "نمیدهد", "نمیباشد", "نمیگردد", "نمیآید",
]

# TeX plumbing that is Latin but is not prose: units, float placements,
# environment and size keywords. Excluded from the unisolated-Latin scan.
TEX_STOPWORDS = {
    "pt", "em", "ex", "cm", "mm", "bp", "dd", "cc", "sp", "true",
    "htbp", "htb", "hbp", "tbp", "here", "center", "left", "right",
    "linewidth", "textwidth", "columnwidth", "paperwidth", "paperheight",
    "figure", "table", "tabular", "longtable", "itemize", "enumerate",
    "description", "quote", "quotation", "flushleft", "flushright",
    "small", "footnotesize", "scriptsize", "tiny", "large", "Large",
    "LARGE", "huge", "Huge", "normalsize", "single", "frame", "framesep",
    "fontsize", "baselinestretch", "numbers", "none", "width", "height",
    "scale", "angle", "keepaspectratio", "page", "trim", "clip",
}

# Names and non-plurals that end in s. A regular kept-term plural is the
# singular stem plus ها, but Kubernetes / HTTPS / analysis are not plurals.
EN_PLURAL_EXCEPTIONS = frozenset({
    "windows", "kubernetes", "redis", "postgres", "ios", "macos",
    "https", "http", "tls", "ssl", "aws", "gcs", "nfs", "dns", "bios",
    "cosmos", "analysis", "thesis", "basis", "crisis", "physics",
    "mathematics", "economics", "news", "series", "species", "means",
    "always", "towards", "perhaps", "plus", "minus", "canvas", "atlas",
    "this", "is", "was", "has", "does", "his", "its", "as", "us",
    "across", "process", "access", "address", "status", "bus",
})


def english_plural_stem(word: str) -> str | None:
    """Singular stem if *word* is a regular English plural, else None."""
    if re.fullmatch(r"[A-Z]{2,}s", word):
        return word[:-1]
    if len(word) < 4 or word.isupper():
        return None
    lower = word.lower()
    if lower in EN_PLURAL_EXCEPTIONS:
        return None
    if lower.endswith("ies") and len(word) > 4:
        return word[:-3] + ("Y" if word[-4].isupper() else "y")
    if lower.endswith("es") and len(word) > 4:
        if lower.endswith(("ches", "shes")) or lower[-3] in "sxz":
            return word[:-2]
    if lower.endswith("s") and not lower.endswith("ss"):
        if lower.endswith(("us", "is", "os", "as")):
            return None
        return word[:-1]
    return None


DEFAULT_PAIRS = [
    ("node", "گره"),
    ("deployment", "استقرار"),
    ("configuration", "پیکربندی"),
    ("implementation", "پیاده‌سازی"),
    ("integration", "یکپارچه‌سازی"),
    ("firewall", "دیوار آتش"),
    ("encryption", "رمزنگاری"),
    ("command", "فرمان"),
]


@dataclass
class Finding:
    level: str
    check: str
    line: int
    message: str
    excerpt: str = ""


class Source:
    """A translation file plus the regions where prose rules do not apply."""

    def __init__(self, path: Path):
        self.path = path
        self.text = path.read_text(encoding="utf-8")
        self.kind = "tex" if path.suffix.lower() == ".tex" else "html"
        self.line_starts = [0] + [
            m.end() for m in re.finditer(r"\n", self.text)
        ]
        self.lines = self.text.splitlines()
        self.protected: list[tuple[int, int]] = []
        self.comments: list[tuple[int, int]] = []
        self.isolates: list[tuple[int, int, str]] = []
        self.preamble_end = 0
        self._scan()

    def line_of(self, pos: int) -> int:
        return bisect.bisect_right(self.line_starts, pos)

    def in_preamble(self, pos: int) -> bool:
        return pos < self.preamble_end

    def inert(self, pos: int) -> bool:
        """Preamble or comment: structural checks must not fire here.

        Templates and real documents both carry commented-out examples and
        `% TODO(ambiguity)` markers; those are not output.
        """
        if pos < self.preamble_end:
            return True
        return any(start <= pos < end for start, end in self.comments)

    def excerpt(self, pos: int, width: int = 60) -> str:
        start = max(0, pos - width // 3)
        return self.text[start:start + width].replace("\n", " ").strip()

    def is_protected(self, pos: int) -> bool:
        for start, end in self.protected:
            if start <= pos < end:
                return True
        return False

    def suppressed(self, pos: int, check: str) -> bool:
        line = self.line_of(pos)
        for candidate in (line, line - 1):
            if 1 <= candidate <= len(self.lines):
                text = self.lines[candidate - 1]
                for m in re.finditer(r"fa-lint:\s*allow\s+([\w-]+)", text):
                    if m.group(1) in (check, "all"):
                        return True
        return False

    # -- region scanning ---------------------------------------------------

    def _protect(self, start: int, end: int) -> None:
        if end > start:
            self.protected.append((start, end))

    def _match_brace(self, open_pos: int) -> int:
        depth = 0
        i = open_pos
        while i < len(self.text):
            ch = self.text[i]
            if ch == "\\":
                i += 2
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return i
            i += 1
        return len(self.text)

    def _scan(self) -> None:
        if self.kind == "tex":
            self._scan_tex()
        else:
            self._scan_html()
        self.protected.sort()

    def _scan_tex(self) -> None:
        body = re.search(r"\\begin\{document\}", self.text)
        if body:
            self.preamble_end = body.end()
            self._protect(0, body.end())

        for m in re.finditer(r"(?<!\\)%.*$", self.text, re.M):
            self._protect(m.start(), m.end())
            self.comments.append((m.start(), m.end()))

        for env in ("verbatim", "Verbatim", "lstlisting", "latin",
                    "equation", "equation*", "align", "align*", "minted"):
            pattern = re.compile(
                r"\\begin\{" + re.escape(env) + r"\}.*?\\end\{"
                + re.escape(env) + r"\}", re.S)
            for m in pattern.finditer(self.text):
                self._protect(m.start(), m.end())

        for m in re.finditer(r"\$\$.*?\$\$|(?<!\\)\$.*?(?<!\\)\$"
                             r"|\\\[.*?\\\]|\\\(.*?\\\)", self.text, re.S):
            self._protect(m.start(), m.end())

        arg_only = ("begin", "end", "label", "ref", "eqref", "cite", "url",
                    "href", "input", "include", "includegraphics", "bibitem",
                    "bibliography", "usepackage", "documentclass",
                    "settextfont", "setlatintextfont", "setmonofont",
                    "setdigitfont", "hypersetup", "setlength", "hspace",
                    "vspace", "rule", "newcommand", "renewcommand",
                    "definecolor", "geometry", "addcontentsline",
                    "pdfstringdefDisableCommands", "IfFontExistsTF")
        # Optional arguments (`[width=0.92\linewidth]`) are plumbing, not
        # prose; otherwise unisolated-number fires on every includegraphics.
        for m in re.finditer(r"\\[A-Za-z@]+\*?\s*\[", self.text):
            start = m.end() - 1
            depth = 0
            i = start
            while i < len(self.text):
                ch = self.text[i]
                if ch == "[":
                    depth += 1
                elif ch == "]":
                    depth -= 1
                    if depth == 0:
                        self._protect(start, i + 1)
                        break
                i += 1
        for m in re.finditer(r"\\([A-Za-z@]+)\s*(\[[^\]]*\])?\s*\{",
                             self.text):
            name = m.group(1)
            open_pos = m.end() - 1
            close = self._match_brace(open_pos)
            if name in ("lr", "en", "textenglish", "lasttext"):
                self._protect(open_pos + 1, close)
                if any(s <= m.start() < e for s, e in self.comments):
                    continue
                # Whole `\en{…}` so the gap between two isolates is only
                # the characters *between* the constructs, not `\en{`.
                self.isolates.append((m.start(), close + 1,
                                      self.text[open_pos + 1:close]))
            elif name in arg_only:
                self._protect(m.start(), close + 1)
            else:
                # Protect only the macro name, never its Persian argument.
                self._protect(m.start(), m.end() - 1)

        for m in re.finditer(r"\\[A-Za-z@]+\*?", self.text):
            self._protect(m.start(), m.end())

    def _scan_html(self) -> None:
        for m in re.finditer(r"<!--.*?-->", self.text, re.S):
            self._protect(m.start(), m.end())
            self.comments.append((m.start(), m.end()))
        for tag in ("style", "script", "pre", "code", "kbd", "samp", "math",
                    "title"):
            pattern = re.compile(r"<" + tag + r"\b.*?</" + tag + r"\s*>", re.S)
            for m in pattern.finditer(self.text):
                self._protect(m.start(), m.end())
        # An LTR region is marked either by dir="ltr" or by one of the
        # template's LTR classes (.ltr, .en, .num, .refs), which set
        # `direction` in CSS. Both isolate; treat both as protected.
        container = (r"span|a|bdi|div|section|article|p|td|th|table|tbody"
                     r"|thead|tr|ol|ul|li|dl|figcaption|caption|blockquote"
                     r"|h[1-6]")
        marker = (r"(?:\bdir\s*=\s*[\"']ltr[\"']"
                  r"|\bclass\s*=\s*[\"'][^\"']*\b(?:ltr|en|num|refs)\b)")
        for m in re.finditer(rf"<({container})\b[^>]*{marker}[^>]*>"
                             r"(.*?)</\1\s*>", self.text, re.S):
            if any(s <= m.start() < e for s, e in self.comments):
                continue
            self._protect(m.start(2), m.end(2))
            self.isolates.append((m.start(), m.end(), m.group(2)))
        for m in re.finditer(r"<[^>]+>", self.text):
            self._protect(m.start(), m.end())
        for m in re.finditer(r"&[#\w]+;", self.text):
            self._protect(m.start(), m.end())


def load_pairs(paths: list[Path], level: str
               ) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str]] = set()
    for path in paths:
        if not path.exists():
            continue
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("\t") if p.strip()]
            if len(parts) < 3 or parts[0] == "english":
                continue
            en, fa, scope = parts[0], parts[1], parts[2]
            levels = parts[3] if len(parts) > 3 else "all"
            if levels == "system-docs" and level == "journal":
                continue
            key = (en, fa)
            if key in seen:
                continue
            seen.add(key)
            rows.append((en, fa, scope))
    if rows:
        return rows
    return [(en, fa, "universal") for en, fa in DEFAULT_PAIRS]


def load_terms_pairs(path: Path) -> tuple[list[tuple[str, str, str]], list[str]]:
    """Keep-English rows from a job terms.tsv.

    Columns: source, output, step, count, forbidden_fa.
    A keep-English row (Latin in *output*) must set *forbidden_fa*;
    otherwise this is a contract error, not a silent skip. Persian-output
    rows (prose / chrome) are not calque pairs.
    """
    rows: list[tuple[str, str, str]] = []
    errors: list[str] = []
    if not path.is_file():
        return rows, [f"no such file: {path}"]
    seen: set[tuple[str, str]] = set()
    for lineno, raw in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("\t")]
        if not parts or parts[0] in ("source", "english"):
            continue
        if len(parts) < 2:
            errors.append(f"{path}:{lineno}: need source and output columns")
            continue
        en, output = parts[0], parts[1]
        if not re.search(r"[A-Za-z]", output):
            continue
        forbidden = parts[4] if len(parts) > 4 else ""
        if not forbidden:
            errors.append(
                f"{path}:{lineno}: keep-English {en!r} has empty "
                "forbidden_fa (terms-calque)")
            continue
        key = (en, forbidden)
        if key in seen:
            continue
        seen.add(key)
        rows.append((en, forbidden, "job"))
    return rows, errors


def _sidecar(files: list[Path], name: str) -> Path | None:
    if not files:
        return None
    candidate = files[0].resolve().parent / name
    return candidate if candidate.is_file() else None


def fa_pattern(word: str) -> str:
    """Match a Persian term whether it uses ZWNJ or a plain space.

    Bounded by non-Persian so «گره» does not fire inside «کنگره».
    """
    escaped = [re.escape(part) for part in re.split(f"[{ZWNJ} ]", word)]
    body = f"[{ZWNJ} ]?".join(escaped)
    return rf"(?<![{FA_RANGE}])(?:{body})(?![{FA_RANGE}])"


def _joiner_gap(gap: str) -> bool:
    """True when two LTR isolates have only space/punctuation between them."""
    stripped = gap.replace("&nbsp;", " ").replace("->", "")
    return re.fullmatch(r"[\s~/\(\)\[\]\{\}:.,+=<>\-–—]*", stripped) is not None


def check(src: Source, pairs: list[tuple[str, str, str]],
          manifest: list[str] | None) -> list[Finding]:
    out: list[Finding] = []
    text = src.text

    def add(level: str, check_id: str, pos: int, message: str) -> None:
        if src.suppressed(pos, check_id):
            return
        out.append(Finding(level, check_id, src.line_of(pos), message,
                           src.excerpt(pos)))

    def prose_finditer(pattern: str, flags: int = 0):
        for m in re.finditer(pattern, text, flags):
            if not src.is_protected(m.start()):
                yield m

    def live_finditer(pattern: str, flags: int = 0):
        """Structural scan of the raw text, skipping preamble and comments."""
        for m in re.finditer(pattern, text, flags):
            if not src.inert(m.start()):
                yield m

    # 1. Orthography -----------------------------------------------------
    for m in prose_finditer(r"[\u0643\u064a]"):
        name = unicodedata.name(m.group(0), "?")
        add(ERROR, "arabic-letters", m.start(),
            f"Arabic letter {m.group(0)!r} ({name}); use ک / ی")

    for m in prose_finditer(r"[\u06f0-\u06f9\u0660-\u0669\u066B\u066C]"):
        add(ERROR, "eastern-digits", m.start(),
            f"eastern digit or Arabic decimal {m.group(0)!r}; "
            "digits stay Western (3.14)")

    for verb in ZWNJ_VERBS:
        for m in prose_finditer(rf"(?<![{FA_RANGE}]){re.escape(verb)}"):
            add(ERROR, "zwnj-verb", m.start(),
                f"missing ZWNJ in {verb!r}; write "
                f"{verb[:2] + ZWNJ + verb[2:]!r}")

    for m in prose_finditer(rf"[{FA_RANGE}]ه(ها|های|هایی)(?![{FA_RANGE}])"):
        add(ERROR, "zwnj-plural", m.start(),
            f"{m.group(0)!r} looks like a missing ZWNJ before the plural")

    for m in prose_finditer(rf"[{FA_RANGE}]\s?[,;]|[,;]\s?[{FA_RANGE}]"):
        add(ERROR, "latin-punct", m.start(),
            "Latin comma/semicolon in Persian prose; use ، or ؛")

    for m in prose_finditer(rf"[{FA_RANGE}]\s?\?"):
        add(ERROR, "latin-punct", m.start(),
            "Latin question mark in Persian prose; use ؟")

    # 2. Terminology -----------------------------------------------------
    # Longest form first, so «دیوارهای آتش» is reported once rather than also
    # matching a shorter row that overlaps it.
    consumed: list[tuple[int, int]] = []
    for en, fa, scope in sorted(pairs, key=lambda r: -len(r[1])):
        for m in prose_finditer(fa_pattern(fa)):
            if any(s < m.end() and m.start() < e for s, e in consumed):
                continue
            consumed.append((m.start(), m.end()))
            add(ERROR, "forbidden-fa", m.start(),
                f"{m.group(0)!r} is a calque of {en!r} ({scope}); "
                f"keep {en!r} in an LTR isolate")

    heads = "|".join(fa_pattern(h) for h in HALF_TRANSLATION_HEADS)
    latin_start = (r"(?:\\(?:lr|en|textenglish)\s*\{|<span[^>]*>|<bdi>|)"
                   r"\s*[A-Za-z]")
    for m in prose_finditer(rf"(?:{heads})\s*{latin_start}"):
        add(ERROR, "half-translation", m.start(),
            "Persian head noun in front of an English name; keep the whole "
            "source noun phrase English in one isolate")

    for m in live_finditer(
            rf"(?:\}}|</span>|</bdi>|[A-Za-z])(?!ها)(ی)"
            rf"(?![{FA_RANGE}])"):
        add(ERROR, "fa-morphology", m.start(),
            f"Persian suffix {m.group(1)!r} attached to an English token; "
            "do not add ezafe (Goی). Plurals are ها after the isolate "
            "(serviceها, platformها, APIها)")

    for pos, _end, body in src.isolates:
        if "/" in body or "://" in body or "@" in body or "->" in body:
            continue
        for token in re.finditer(r"[A-Za-z]+", body):
            word = token.group(0)
            stem = english_plural_stem(word)
            if stem is None:
                continue
            add(ERROR, "en-plural", pos,
                f"English plural {word!r}; write the singular stem in the "
                f"isolate and Persian ها after it ({stem}ها, not {word})")

    # Adjacent LTR isolates reverse on an RTL page. Compare isolate *ranges*
    # so `\textbf{درست} \en{node}` is not a false split, while
    # `\en{1.0.1}~(\en{2026-08-09})` still is.
    ordered = sorted(src.isolates, key=lambda r: r[0])
    for i in range(len(ordered) - 1):
        _start_a, end_a, _body_a = ordered[i]
        start_b, _end_b, _body_b = ordered[i + 1]
        if start_b <= end_a:
            continue
        gap = text[end_a:start_b]
        if _joiner_gap(gap):
            add(ERROR, "split-isolate", end_a,
                "two LTR isolates with only space or punctuation between them; "
                "wrap the whole cluster in one isolate "
                "(3.1 Title, OP_IF/OP_NOTIF, 1.0.1 (2026-08-09))")

    # 3. Isolation of Latin runs and number clusters ---------------------
    for m in prose_finditer(r"[A-Za-z][A-Za-z0-9._/+-]{2,}"):
        run = m.group(0)
        if run in TEX_STOPWORDS or run.rstrip("0123456789") in TEX_STOPWORDS:
            continue
        add(ERROR, "unisolated-latin", m.start(),
            f"Latin run {run!r} is not inside an LTR isolate")

    for m in prose_finditer(r"\d+(?:[.\-–/:]\d+)*"):
        add(ERROR, "unisolated-number", m.start(),
            f"number cluster {m.group(0)!r} is not inside an LTR isolate "
            "(ranges and dates reverse on an RTL page)")

    seen: dict[str, str] = {}
    for pos, _end, body in src.isolates:
        term = " ".join(body.split())
        if not term or not re.search(r"[A-Za-z]", term):
            continue
        key = re.sub(r"s$", "", term.lower())
        if key in seen and seen[key] != term:
            add(ERROR, "terminology-drift", pos,
                f"isolate {term!r} also appears as {seen[key]!r}; "
                "use one English form per concept")
        seen.setdefault(key, term)

    # 4. Code, images, structure -----------------------------------------
    if src.kind == "html":
        for m in live_finditer(r"<pre\b[^>]*>"):
            if not re.search(r"\bdir\s*=\s*[\"']ltr[\"']", m.group(0)):
                add(ERROR, "code-direction", m.start(),
                    "<pre> without dir=\"ltr\"; listings are never RTL")
        for m in live_finditer(r"<(?:pre|code)\b[^>]*"
                               r"(?:dir\s*=\s*[\"']rtl[\"']"
                               r"|text-align\s*:\s*right)"):
            add(ERROR, "code-direction", m.start(),
                "listing forced RTL or right-aligned")
        if not re.search(r"<html[^>]*\blang\s*=\s*[\"']fa[\"'][^>]*"
                         r"\bdir\s*=\s*[\"']rtl[\"']", text):
            add(ERROR, "html-root", 0,
                "root element must be <html lang=\"fa\" dir=\"rtl\">")
        if "<style" in text and "pre-wrap" not in text:
            add(WARN, "print-css", text.find("<style"),
                "no white-space: pre-wrap on pre; long code lines are "
                "clipped on paper (overflow-x does nothing in print)")
        # CSS mirroring lives inside <style>, which prose checks protect, so
        # scan the raw text here and only skip comments.
        for m in live_finditer(r"scaleX\(\s*-1\s*\)"):
            add(ERROR, "mirrored-image", m.start(),
                "horizontal flip on artwork is forbidden")
        images = []
        for m in live_finditer(r"<img\b[^>]*>"):
            tag = m.group(0)
            srcm = re.search(r"\bsrc\s*=\s*[\"']([^\"']+)[\"']", tag)
            if srcm:
                images.append((m.start(), srcm.group(1)))
                ref = srcm.group(1)
                base = os.path.basename(ref)
                if re.match(r"(?:srcpage|page)-\d+\.(?:png|jpe?g|webp)$",
                            base, re.I):
                    add(ERROR, "full-page-figure", m.start(),
                        f"image {base!r} is a full source-page raster; "
                        "crop to the artwork (scripts/crop-source-figures.py)")
            if not re.search(r"\bdir\s*=\s*[\"']ltr[\"']", tag):
                add(ERROR, "figure-direction", m.start(),
                    "<img> without dir=\"ltr\"; RTL layout can recell or "
                    "paint the figure black")
    else:
        for env in ("verbatim", "Verbatim", "lstlisting"):
            for m in live_finditer(r"\\begin\{" + env + r"\}"):
                window = text[max(0, m.start() - 400):m.start()]
                if "\\begin{latin}" not in window:
                    add(ERROR, "code-direction", m.start(),
                        f"{env} is not wrapped in \\begin{{latin}}; "
                        "listings are never RTL")
        guard = re.search(r"\\(?:section|subsection|subsubsection|chapter"
                          r"|caption)\*?\{[^}]*\\(?:lr|en)\b", text)
        if guard and "pdfstringdefDisableCommands" not in text:
            add(WARN, "bookmark-guard", guard.start(),
                "\\lr/\\en used in a heading or caption without "
                "\\pdfstringdefDisableCommands; hyperref bookmarks will "
                "break")
        images = [(m.start(), m.group(1)) for m in
                  live_finditer(
                      r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")]
        for pos, ref in images:
            base = os.path.basename(ref)
            if re.match(r"(?:srcpage|page)-\d+\.(?:png|jpe?g|webp)$",
                        base, re.I):
                add(ERROR, "full-page-figure", pos,
                    f"image {base!r} is a full source-page raster; "
                    "crop to the artwork (scripts/crop-source-figures.py)")
            before = text[:pos]
            last_begin = max(
                before.rfind("\\begin{LTR}"),
                before.rfind("\\begin{latin}"),
                before.rfind("\\LR{"),
            )
            last_end = max(
                before.rfind("\\end{LTR}"),
                before.rfind("\\end{latin}"),
            )
            if last_begin < 0 or last_begin < last_end:
                add(ERROR, "figure-direction", pos,
                    "\\includegraphics is not inside LTR/latin; xepersian "
                    "can paint the figure black or mirrored")

    base = src.path.parent
    found: list[str] = []
    for pos, ref in images:
        if re.match(r"^(?:https?:|data:)", ref):
            continue
        candidates = [base / ref]
        if not os.path.splitext(ref)[1]:
            candidates += [base / (ref + ext) for ext in
                           (".pdf", ".png", ".jpg", ".jpeg", ".eps")]
        if not any(c.exists() for c in candidates):
            add(ERROR, "missing-image", pos,
                f"image {ref!r} does not exist next to the source")
        found.append(os.path.basename(ref))

    if manifest is not None:
        missing = [n for n in manifest if n not in found]
        for name in missing:
            add(ERROR, "missing-image", 0,
                f"{name!r} is in the source manifest but not in the "
                "translation")

    return out


def main(argv: list[str]) -> int:
    here = Path(__file__).resolve().parent
    house = here.parent / "references" / "term-pairs.tsv"
    ap = argparse.ArgumentParser(
        prog="check-fa.py",
        description="Mechanical checks for scientific Persian output.")
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--level", choices=("system-docs", "journal"),
                    default="system-docs",
                    help="terminology.md level (default system-docs)")
    ap.add_argument("--pairs", type=Path, default=None,
                    help="extra TSV merged on top of term-pairs.tsv")
    ap.add_argument("--terms", type=Path, default=None,
                    help="job terms.tsv; keep-English rows need forbidden_fa")
    ap.add_argument("--manifest", type=Path,
                    help="file listing expected image basenames, one per line")
    ap.add_argument("--strict", action="store_true",
                    help="warnings become errors; requires --terms and "
                         "--manifest (or sidecars next to the source)")
    ap.add_argument("--max", type=int, default=40,
                    help="findings printed per check (default 40)")
    args = ap.parse_args(argv)

    pair_paths = [house]
    if args.pairs is not None:
        pair_paths.append(args.pairs)
    pairs = load_pairs(pair_paths, args.level)
    if args.terms is None:
        args.terms = _sidecar(args.files, "terms.tsv")
    if args.manifest is None:
        args.manifest = _sidecar(args.files, "manifest.txt")
    if args.strict and args.terms is None:
        print("check-fa: --strict requires --terms FILE "
              "(or terms.tsv next to the source)", file=sys.stderr)
        return 2
    if args.strict and args.manifest is None:
        print("check-fa: --strict requires --manifest FILE "
              "(or manifest.txt next to the source)", file=sys.stderr)
        return 2
    if args.terms is not None:
        if not args.terms.is_file():
            print(f"check-fa: no such file: {args.terms}", file=sys.stderr)
            return 2
        extra_pairs, terms_errors = load_terms_pairs(args.terms)
        if terms_errors:
            for err in terms_errors:
                print(f"check-fa: terms-calque: {err}", file=sys.stderr)
            return 2
        seen = {(en, fa) for en, fa, _ in pairs}
        for row in extra_pairs:
            key = (row[0], row[1])
            if key not in seen:
                pairs.append(row)
                seen.add(key)
    manifest = None
    if args.manifest is not None:
        if not args.manifest.is_file():
            print(f"check-fa: no such file: {args.manifest}", file=sys.stderr)
            return 2
        manifest = [l.strip() for l in
                    args.manifest.read_text(encoding="utf-8").splitlines()
                    if l.strip() and not l.startswith("#")]

    errors = warnings = 0
    for path in args.files:
        if not path.exists():
            print(f"check-fa: no such file: {path}", file=sys.stderr)
            return 2
        if path.suffix.lower() not in (".tex", ".html", ".htm"):
            print(f"check-fa: skipping {path} (expected .tex or .html)",
                  file=sys.stderr)
            continue
        src = Source(path)
        findings = check(src, pairs, manifest)
        errors += sum(1 for f in findings if f.level == ERROR)
        warnings += sum(1 for f in findings if f.level == WARN)

        print(f"== {path}")
        if not findings:
            print("   clean")
            continue
        by_check: dict[str, list[Finding]] = {}
        for f in findings:
            by_check.setdefault(f.check, []).append(f)
        for check_id in sorted(by_check,
                               key=lambda c: (by_check[c][0].level != ERROR,
                                              c)):
            group = by_check[check_id]
            head = group[0]
            print(f"   [{head.level}] {check_id} ({len(group)})")
            for f in group[:args.max]:
                print(f"     {path}:{f.line}: {f.message}")
                if f.excerpt:
                    print(f"       … {f.excerpt}")
            if len(group) > args.max:
                print(f"     … {len(group) - args.max} more")

    print(f"\ncheck-fa: {errors} error(s), {warnings} warning(s)")
    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
