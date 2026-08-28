#!/usr/bin/env bash
# Regression tests for scripts/check-fa.py and the build-pdf lint gate.
#
# The `good` fixtures must lint clean; the `bad` fixtures must report every
# check id listed below. Run before changing a rule so a loosened regex
# cannot pass silently.
set -uo pipefail

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
lint="$here/../scripts/check-fa.py"
fixtures="$here/fixtures"
fail=0

expect_clean() {
  local file=$1
  shift
  local out rc
  out=$(python3 "$lint" "$file" "$@" 2>&1)
  rc=$?
  if [[ $rc -ne 0 ]]; then
    echo "FAIL $(basename "$file") ${*}: expected clean, got:"
    echo "$out" | sed 's/^/    /'
    fail=1
  else
    echo "ok   $(basename "$file") ${*} lints clean"
  fi
}

expect_checks() {
  local file=$1
  shift
  local out rc missing=()
  out=$(python3 "$lint" "$file" 2>&1)
  rc=$?
  if [[ $rc -eq 0 ]]; then
    echo "FAIL $(basename "$file"): expected a non-zero exit"
    fail=1
  fi
  local id
  for id in "$@"; do
    grep -q -- "$id" <<<"$out" || missing+=("$id")
  done
  if [[ ${#missing[@]} -gt 0 ]]; then
    echo "FAIL $(basename "$file"): checks not reported: ${missing[*]}"
    fail=1
  else
    echo "ok   $(basename "$file") reports ${#@} expected checks"
  fi
}

expect_no_errors() {
  local file=$1 out errs
  out=$(python3 "$lint" "$file" 2>&1)
  errs=$(sed -n 's/^check-fa: \([0-9]*\) error.*/\1/p' <<<"$out")
  if [[ ${errs:-1} -ne 0 ]]; then
    echo "FAIL $(basename "$file"): expected 0 errors, got ${errs:-?}"
    echo "$out" | sed 's/^/    /'
    fail=1
  else
    echo "ok   $(basename "$file") has no errors"
  fi
}

empty_terms="$fixtures/terms-empty.tsv"
empty_manifest="$fixtures/manifest-empty.txt"
good_manifest="$fixtures/manifest-good.txt"
strict_good=(--strict --terms "$empty_terms" --manifest "$good_manifest")
strict_journal=(--level journal --strict --terms "$empty_terms"
                --manifest "$empty_manifest")

expect_clean "$fixtures/good.tex" "${strict_good[@]}"
expect_clean "$fixtures/good.html" "${strict_good[@]}"
expect_clean "$fixtures/journal.tex" "${strict_journal[@]}"

# The shipped templates must not trigger errors. Placeholder TITLE sits in
# an isolate (TeX) or in <title> (HTML).
expect_no_errors "$here/../assets/rtl-document.tex"
expect_no_errors "$here/../assets/rtl-document.html"

expect_checks "$fixtures/bad.tex" \
  arabic-letters eastern-digits zwnj-verb zwnj-plural latin-punct \
  forbidden-fa half-translation fa-morphology en-plural split-isolate \
  unisolated-latin unisolated-number code-direction missing-image \
  bookmark-guard figure-direction full-page-figure

expect_checks "$fixtures/bad.html" \
  arabic-letters eastern-digits zwnj-verb forbidden-fa half-translation \
  fa-morphology en-plural split-isolate unisolated-latin unisolated-number \
  code-direction html-root mirrored-image missing-image print-css \
  figure-direction full-page-figure

# Journal-correct field nouns must fail at the default system-docs level.
journal_out=$(python3 "$lint" "$fixtures/journal.tex" 2>&1) || true
if grep -q forbidden-fa <<<"$journal_out"; then
  echo "ok   journal.tex reports forbidden-fa at system-docs"
else
  echo "FAIL journal.tex: expected forbidden-fa at system-docs"
  echo "$journal_out" | sed 's/^/    /'
  fail=1
fi

# --pairs must merge, not replace, the house list.
extra=$(mktemp)
printf 'english\tforbidden_fa\tscope\tlevels\nfoo\tبار\tuniversal\tall\n' >"$extra"
merge_out=$(python3 "$lint" "$fixtures/journal.tex" --pairs "$extra" 2>&1) || true
rm -f "$extra"
if grep -q forbidden-fa <<<"$merge_out" && grep -q گره <<<"$merge_out"; then
  echo "ok   --pairs merges house term-pairs.tsv"
else
  echo "FAIL --pairs dropped house rows"
  echo "$merge_out" | sed 's/^/    /'
  fail=1
fi

# --strict without a terms ledger (or sidecar) is a usage error.
strict_rc=0
strict_out=$(python3 "$lint" "$fixtures/nginx-calque.tex" --strict 2>&1) \
  || strict_rc=$?
if [[ $strict_rc -eq 2 ]] && grep -q -- '--terms' <<<"$strict_out"; then
  echo "ok   --strict requires --terms"
else
  echo "FAIL --strict without --terms: expected exit 2"
  echo "$strict_out" | sed 's/^/    /'
  fail=1
fi

strict_man_rc=0
strict_man_out=$(python3 "$lint" "$fixtures/nginx-calque.tex" --strict \
  --terms "$empty_terms" 2>&1) || strict_man_rc=$?
if [[ $strict_man_rc -eq 2 ]] && grep -q -- '--manifest' <<<"$strict_man_out"; then
  echo "ok   --strict requires --manifest"
else
  echo "FAIL --strict without --manifest: expected exit 2"
  echo "$strict_man_out" | sed 's/^/    /'
  fail=1
fi

# Keep-English rows with empty forbidden_fa fail closed, they are not skipped.
inc_rc=0
inc_out=$(python3 "$lint" "$fixtures/nginx-calque.tex" \
  --terms "$fixtures/terms-incomplete.tsv" \
  --manifest "$empty_manifest" 2>&1) || inc_rc=$?
if [[ $inc_rc -eq 2 ]] && grep -q terms-calque <<<"$inc_out" \
    && grep -q proxy_pass <<<"$inc_out"; then
  echo "ok   keep-English row without forbidden_fa is terms-calque"
else
  echo "FAIL incomplete terms.tsv: expected terms-calque exit 2"
  echo "$inc_out" | sed 's/^/    /'
  fail=1
fi

# --terms reads keep-English calques; Persian-output rows stay ignored.
terms_out=$(python3 "$lint" "$fixtures/nginx-calque.tex" \
  --terms "$fixtures/terms-nginx.tsv" \
  --manifest "$empty_manifest" --strict 2>&1) || true
if grep -q forbidden-fa <<<"$terms_out" && grep -q مکان <<<"$terms_out" \
    && grep -q بالادست <<<"$terms_out"; then
  echo "ok   --terms reports job lexicon calques"
else
  echo "FAIL --terms missed nginx calques"
  echo "$terms_out" | sed 's/^/    /'
  fail=1
fi
house_out=$(python3 "$lint" "$fixtures/journal.tex" \
  --terms "$fixtures/terms-nginx.tsv" 2>&1) || true
if grep -q گره <<<"$house_out"; then
  echo "ok   --terms keeps house term-pairs.tsv"
else
  echo "FAIL --terms dropped house rows"
  echo "$house_out" | sed 's/^/    /'
  fail=1
fi

# Manifest names that never appear in the translation are missing-image.
man_out=$(python3 "$lint" "$fixtures/journal.tex" --level journal \
  --terms "$empty_terms" --manifest "$fixtures/manifest-missing.txt" \
  --strict 2>&1) || true
if grep -q missing-image <<<"$man_out" && grep -q fig-never.png <<<"$man_out"; then
  echo "ok   --manifest reports omitted figures"
else
  echo "FAIL --manifest missed omitted figure"
  echo "$man_out" | sed 's/^/    /'
  fail=1
fi

# prepare-figures.py: flatten alpha onto white so the print PDF matches the source.
if python3 -c "import PIL.Image" 2>/dev/null; then
  mkdir -p "$fixtures/figures"
  alpha="$fixtures/figures/alpha.png"
  python3 - "$alpha" <<'PY'
import struct, zlib, sys
from pathlib import Path
path = Path(sys.argv[1])
w, h = 4, 2
# RGBA: first pixel transparent black (the Cairo/WeasyPrint trap), rest white.
row = bytes([
    0,  # filter
    0, 0, 0, 0,
    255, 255, 255, 255,
    255, 255, 255, 255,
    255, 255, 255, 255,
])
raw = b"".join(row for _ in range(h))

def chunk(tag, data):
    c = tag + data
    return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)

path.write_bytes(
    b"\x89PNG\r\n\x1a\n"
    + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
    + chunk(b"IDAT", zlib.compress(raw))
    + chunk(b"IEND", b"")
)
PY
  prep="$here/../scripts/prepare-figures.py"
  check_out=$(python3 "$prep" "$alpha" --check 2>&1) || check_rc=$?
  if [[ ${check_rc:-0} -ne 0 ]] && grep -q alpha <<<"$check_out"; then
    echo "ok   prepare-figures --check reports alpha"
  else
    echo "FAIL prepare-figures --check missed alpha"
    echo "$check_out" | sed 's/^/    /'
    fail=1
  fi
  python3 "$prep" "$alpha" >/tmp/prep.out 2>&1 || true
  mode=$(python3 -c "from PIL import Image; print(Image.open('$alpha').mode)")
  if [[ $mode == RGB ]]; then
    echo "ok   prepare-figures flattened alpha to RGB"
  else
    echo "FAIL prepare-figures left mode=$mode"
    fail=1
  fi
  rm -f "$alpha" "$alpha.orig"
else
  echo "skip prepare-figures (no Pillow)"
fi

# build-pdf.sh must not copy a PDF when lint fails.
build="$here/../scripts/build-pdf.sh"
build_rc=0
build_out=$("$build" "$fixtures/nginx-calque.tex" lint-gate-must-not-write \
  --terms "$fixtures/terms-nginx.tsv" \
  --manifest "$empty_manifest" 2>&1) || build_rc=$?
if [[ $build_rc -ne 0 ]] && grep -q forbidden-fa <<<"$build_out" \
    && grep -q 'lint failed' <<<"$build_out" \
    && [[ ! -f ${HOME}/Documents/books/lint-gate-must-not-write.pdf ]]; then
  echo "ok   build-pdf refuses a document that fails lint"
else
  echo "FAIL build-pdf lint gate"
  echo "$build_out" | sed 's/^/    /'
  fail=1
fi
missing_terms_rc=0
missing_terms_out=$("$build" "$fixtures/nginx-calque.tex" \
  --manifest "$empty_manifest" 2>&1) || missing_terms_rc=$?
if [[ $missing_terms_rc -ne 0 ]] && grep -q terms.tsv <<<"$missing_terms_out"; then
  echo "ok   build-pdf requires terms.tsv"
else
  echo "FAIL build-pdf without terms.tsv"
  echo "$missing_terms_out" | sed 's/^/    /'
  fail=1
fi

help_out=$(python3 "$here/../scripts/crop-source-figures.py" --help 2>&1) || help_rc=$?
if [[ ${help_rc:-0} -eq 0 ]] && grep -q crop-source-figures <<<"$help_out"; then
  echo "ok   crop-source-figures.py --help"
else
  echo "FAIL crop-source-figures.py --help"
  echo "$help_out" | sed 's/^/    /'
  fail=1
fi

help_out=$(python3 "$here/../scripts/extract-pdf-pages.py" --help 2>&1) || help_rc=$?
if [[ ${help_rc:-0} -eq 0 ]] && grep -q extract-pdf-pages <<<"$help_out"; then
  echo "ok   extract-pdf-pages.py --help"
else
  echo "FAIL extract-pdf-pages.py --help"
  echo "$help_out" | sed 's/^/    /'
  fail=1
fi

# Template must compile: digit font is a Persian face, not TeX Gyre Termes.
if command -v xelatex >/dev/null 2>&1 \
    && command -v kpsewhich >/dev/null 2>&1 \
    && kpsewhich xepersian.sty >/dev/null 2>&1; then
  smoke=$(mktemp -d)
  cp "$here/../assets/rtl-document.tex" "$smoke/smoke.tex"
  if (cd "$smoke" && xelatex -interaction=nonstopmode -halt-on-error \
        smoke.tex >/dev/null 2>&1); then
    echo "ok   rtl-document.tex compiles with XeLaTeX"
  else
    echo "FAIL rtl-document.tex did not compile"
    if [[ -f $smoke/smoke.log ]]; then
      grep -E '^!|U\+06F0' "$smoke/smoke.log" | head -20 | sed 's/^/    /'
    fi
    fail=1
  fi
  rm -rf "$smoke"
else
  echo "skip rtl-document.tex compile (no xelatex/xepersian)"
fi

if [[ $fail -eq 0 ]]; then
  echo "all tests passed"
else
  echo "tests failed"
fi
exit $fail
