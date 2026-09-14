#!/usr/bin/env python3
"""Write a logical-order plain-text sidecar next to a Persian PDF.

Uses pdftotext (default bidi reconstruction, not -raw), then NFKC-folds
Arabic presentation forms so editors get nominal letters. Strips bidi
marks. Intended for users whose PDF viewer (often Chrome/Edge) pastes
visual-order Persian.

Usage:
    write-copy-txt.py doc.pdf [out.txt]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import unicodedata
from pathlib import Path

_BIDI = dict.fromkeys(
    map(
        ord,
        "\u200e\u200f\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069",
    )
)


def extract(pdf: Path) -> str:
    try:
        proc = subprocess.run(
            ["pdftotext", "-nopgbrk", str(pdf), "-"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        print("write-copy-txt: pdftotext not found (poppler-utils)",
              file=sys.stderr)
        sys.exit(1)
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        print(f"write-copy-txt: pdftotext failed: {err}", file=sys.stderr)
        sys.exit(1)
    text = unicodedata.normalize("NFKC", proc.stdout or "")
    return text.translate(_BIDI)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    ap.add_argument("pdf", type=Path)
    ap.add_argument("out", type=Path, nargs="?",
                    help="default: <pdf-stem>.txt beside the PDF")
    args = ap.parse_args()
    if not args.pdf.is_file():
        print(f"write-copy-txt: not a file: {args.pdf}", file=sys.stderr)
        return 1
    out = args.out or args.pdf.with_suffix(".txt")
    out.write_text(extract(args.pdf), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
