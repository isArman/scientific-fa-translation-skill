#!/usr/bin/env python3
"""Detect visual-order (reversed) Persian in a PDF text stream.

Chromium --print-to-pdf and typical WeasyPrint runs paint RTL correctly
but write the *visual* glyph order into the content stream. Copy-paste
and `pdftotext -raw` then reverse the Persian. XeLaTeX + xepersian writes
logical order.

CSS dir=rtl does not fix extraction. This script compares Persian phrases
from the print source with `pdftotext -raw` (content-stream order, not the
default bidi "reading order").

Usage:
    check-pdf-text-order.py doc.pdf --source doc.tex
    check-pdf-text-order.py --extracted dump.txt --source doc.tex

Exit 0: logical order, or not enough evidence.
Exit 1: usage / missing tools.
Exit 2: visual order — copy-paste will reverse Persian.
"""
from __future__ import annotations

import argparse
import html as html_mod
import re
import subprocess
import sys
from pathlib import Path

ARABIC_WORD = re.compile(
    r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF"
    r"\uFB50-\uFDFF\uFE70-\uFEFF\u200c]+"
)
_BIDI_MARKS = dict.fromkeys(
    map(
        ord,
        "\u200e\u200f\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069",
    )
)


def strip_bidi(s: str) -> str:
    return s.translate(_BIDI_MARKS)


def fold(s: str) -> str:
    return re.sub(r"\s+", "", strip_bidi(s).replace("\u200c", ""))


def strip_tex(text: str) -> str:
    lines = []
    for line in text.splitlines():
        out = []
        i = 0
        while i < len(line):
            if line[i] == "%" and (i == 0 or line[i - 1] != "\\"):
                break
            out.append(line[i])
            i += 1
        lines.append("".join(out))
    text = "\n".join(lines)
    text = re.sub(
        r"\\begin\{latin\}.*?\\end\{latin\}", " ", text, flags=re.S
    )
    for _ in range(8):
        nxt = re.sub(
            r"\\(?:lr|en|texttt|textbf|textit)\{([^{}]*)\}", " ", text
        )
        if nxt == text:
            break
        text = nxt
    text = re.sub(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?", " ", text)
    return re.sub(r"[{}\\]", " ", text)


def strip_html(text: str) -> str:
    text = re.sub(r"(?is)<script\b.*?</script>", " ", text)
    text = re.sub(r"(?is)<style\b.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return html_mod.unescape(text)


def source_plain(path: Path, text: str | None = None) -> str:
    if text is None:
        text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix in {".tex", ".ltx"}:
        return strip_tex(text)
    if suffix in {".html", ".htm"}:
        return strip_html(text)
    return text


def persian_windows(plain: str, min_letters: int = 12) -> list[list[str]]:
    words = [fold(w) for w in ARABIC_WORD.findall(plain)]
    windows: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()
    for i in range(len(words)):
        letters = 0
        acc: list[str] = []
        for w in words[i:]:
            if not w:
                continue
            acc.append(w)
            letters += len(w)
            if letters >= min_letters:
                key = tuple(acc)
                if key not in seen:
                    seen.add(key)
                    windows.append(acc)
                break
    return windows


def classify(
    windows: list[list[str]], extracted: str, min_letters: int = 12
) -> str:
    hay = fold(extracted)
    if not hay or not windows:
        return "inconclusive"
    logical = visual = 0
    for acc in windows:
        logi = "".join(acc)
        if len(logi) < min_letters:
            continue
        char_vis = logi[::-1]
        word_vis = "".join(reversed(acc))
        in_log = logi in hay
        in_vis = (char_vis in hay and char_vis != logi) or (
            word_vis in hay and word_vis != logi
        )
        if in_log and not in_vis:
            logical += 1
        elif in_vis and not in_log:
            visual += 1
    if visual >= 1 and visual > logical:
        return "visual"
    if logical >= 1 and logical > visual:
        return "logical"
    return "inconclusive"


def pdf_raw_text(pdf: Path) -> str:
    try:
        proc = subprocess.run(
            ["pdftotext", "-raw", "-nopgbrk", str(pdf), "-"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        print("check-pdf-text-order: pdftotext not found (poppler-utils)",
              file=sys.stderr)
        sys.exit(1)
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        print(f"check-pdf-text-order: pdftotext failed: {err}", file=sys.stderr)
        sys.exit(1)
    return proc.stdout or ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    ap.add_argument("pdf", nargs="?", type=Path, help="PDF to inspect")
    ap.add_argument("--source", type=Path, required=True,
                    help="print source (.tex or .html)")
    ap.add_argument("--extracted", type=Path,
                    help="use this text dump instead of pdftotext -raw")
    ap.add_argument("--min-letters", type=int, default=12)
    args = ap.parse_args()

    if not args.source.is_file():
        print(f"check-pdf-text-order: not a file: {args.source}", file=sys.stderr)
        return 1
    if args.extracted is None and args.pdf is None:
        print("check-pdf-text-order: pass a PDF or --extracted", file=sys.stderr)
        return 1

    plain = source_plain(args.source)
    windows = persian_windows(plain, min_letters=args.min_letters)
    if args.extracted is not None:
        extracted = args.extracted.read_text(encoding="utf-8")
    else:
        if not args.pdf.is_file():
            print(f"check-pdf-text-order: not a file: {args.pdf}", file=sys.stderr)
            return 1
        extracted = pdf_raw_text(args.pdf)

    kind = classify(windows, extracted, min_letters=args.min_letters)
    n = len(windows)
    print(
        f"check-pdf-text-order: {kind} ({n} Persian phrase probes)",
        file=sys.stderr,
    )
    if kind == "visual":
        print(
            "check-pdf-text-order: PDF text stream is visual order; "
            "copy-paste will reverse Persian. Rebuild with XeLaTeX.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
