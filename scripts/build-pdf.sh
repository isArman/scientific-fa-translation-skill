#!/usr/bin/env bash
# Compile a Persian print document and copy the PDF to $HOME/Documents/books.
#
#   build-pdf.sh <file.tex|file.html> [slug] [--verify] [--engine ENGINE]
#                [--level system-docs|journal] [--terms FILE] [--manifest FILE]
#
# Lints with check-fa.py --strict before any engine runs, and will not copy
# a PDF to Documents/books if lint, figure check, compile, or --verify fail.
#
# Engine order for .tex: XeLaTeX (via latexmk when present). For .html:
# Chromium, then WeasyPrint. A missing engine falls back; a *failing* engine
# does not — it reports the error and stops, so a broken build is never
# quietly downgraded.
#
# Chromium and WeasyPrint paint RTL correctly but store visual order in the
# text stream; copy-paste reverses Persian. Selectable text requires XeLaTeX.
# --verify fails an HTML-engine PDF when XeLaTeX is installed.
set -uo pipefail

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

usage() {
  echo "usage: build-pdf.sh <file.tex|file.html> [slug] [--verify]" \
       "[--engine tex|chromium|weasyprint]" \
       "[--level system-docs|journal] [--terms FILE] [--manifest FILE]" >&2
  exit 2
}

[[ $# -ge 1 ]] || usage

src=""
slug=""
verify=0
engine=""
used_engine=""
level=system-docs
terms=""
manifest=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --verify) verify=1; shift ;;
    --engine)
      [[ $# -ge 2 ]] || usage
      engine=$2; shift 2 ;;
    --level)
      [[ $# -ge 2 ]] || usage
      level=$2; shift 2 ;;
    --terms)
      [[ $# -ge 2 ]] || usage
      terms=$2; shift 2 ;;
    --manifest)
      [[ $# -ge 2 ]] || usage
      manifest=$2; shift 2 ;;
    -h|--help) usage ;;
    -*) echo "build-pdf.sh: unknown option: $1" >&2; usage ;;
    *) if [[ -z $src ]]; then src=$1; elif [[ -z $slug ]]; then slug=$1;
       else usage; fi; shift ;;
  esac
done

[[ -n $src ]] || usage
if [[ ! -f $src ]]; then
  echo "build-pdf.sh: not a file: $src" >&2
  exit 1
fi
if [[ $level != system-docs && $level != journal ]]; then
  echo "build-pdf.sh: --level must be system-docs or journal" >&2
  exit 2
fi

src_dir=$(cd "$(dirname "$src")" && pwd)
src_base=$(basename "$src")
ext=${src_base##*.}
stem_src=${src_base%.*}
stem=${slug:-$stem_src}
dest_dir="${HOME}/Documents/books"
dest="${dest_dir}/${stem}.pdf"
local_pdf="${src_dir}/${stem_src}.pdf"
[[ -n $terms ]] || terms="${src_dir}/terms.tsv"
[[ -n $manifest ]] || manifest="${src_dir}/manifest.txt"

log() { printf 'build-pdf: %s\n' "$*" >&2; }

if [[ ! -f $terms ]]; then
  log "no terms.tsv at ${terms} — write it before drafting (SKILL.md)"
  exit 1
fi
if [[ ! -f $manifest ]]; then
  log "no manifest.txt at ${manifest} — write it at ingest (source-ingest.md)"
  exit 1
fi

python3 "$here/check-fa.py" "${src_dir}/${src_base}" \
  --level "$level" --terms "$terms" --manifest "$manifest" --strict || {
  log "lint failed; not writing ${dest}"
  exit 1
}

if [[ -d ${src_dir}/figures ]]; then
  python3 "$here/prepare-figures.py" "${src_dir}/figures" --check || {
    log "figure check failed; flatten with prepare-figures.py, then retry"
    exit 1
  }
fi

cd "$src_dir" || exit 1

have_xelatex() {
  command -v xelatex >/dev/null 2>&1 || return 1
  # xepersian is the part that is usually missing on a bare TeX install.
  if command -v kpsewhich >/dev/null 2>&1; then
    kpsewhich xepersian.sty >/dev/null 2>&1 || return 1
  fi
  return 0
}

find_chrome() {
  local c
  for c in chromium chromium-browser google-chrome google-chrome-stable; do
    if command -v "$c" >/dev/null 2>&1; then printf '%s\n' "$c"; return 0; fi
  done
  return 1
}

warn_html_copy_order() {
  log "HTML engine stores RTL in visual order; copy-paste will reverse Persian"
  log "  Selectable text requires XeLaTeX + xepersian"
}

show_tex_error() {
  local logfile=$1
  [[ -f $logfile ]] || return 0
  log "--- first TeX errors in ${logfile} ---"
  grep -n '^!' "$logfile" | head -20 >&2 || true
  log "--- last 25 log lines ---"
  tail -25 "$logfile" >&2
}

# 0 = built, 1 = engine unavailable, 2 = engine present but failed.
compile_tex() {
  have_xelatex || return 1
  local pdf="${stem_src}.pdf"
  if command -v latexmk >/dev/null 2>&1; then
    log "engine: latexmk -xelatex"
    latexmk -xelatex -interaction=nonstopmode -halt-on-error \
            -silent "$src_base" >/dev/null 2>&1 || {
      show_tex_error "${stem_src}.log"; return 2; }
  else
    log "engine: xelatex (two passes)"
    xelatex -interaction=nonstopmode -halt-on-error "$src_base" \
      >/dev/null 2>&1 || { show_tex_error "${stem_src}.log"; return 2; }
    xelatex -interaction=nonstopmode -halt-on-error "$src_base" \
      >/dev/null 2>&1 || { show_tex_error "${stem_src}.log"; return 2; }
  fi
  [[ -f $pdf ]] || { log "expected PDF missing: ${src_dir}/${pdf}"; return 2; }
  used_engine=xelatex
  return 0
}

html_to_pdf() {
  local html=$1 out=$2 chrome crc
  if [[ $engine != weasyprint ]] && chrome=$(find_chrome); then
    log "engine: $chrome --print-to-pdf"
    # Without a virtual-time budget Chromium can print before the webfonts
    # finish loading, which produces fallback boxes for Persian.
    # --disable-gpu paints raster images as black rectangles; do not pass it.
    # Headless Chrome often hangs after writing the PDF; accept a non-empty
    # file even when timeout kills the process.
    crc=0
    if command -v timeout >/dev/null 2>&1; then
      timeout 90 "$chrome" --headless=new --no-pdf-header-footer \
        --virtual-time-budget=10000 \
        --run-all-compositor-stages-before-draw \
        --print-to-pdf="$out" "file://$(realpath "$html")" || crc=$?
    else
      "$chrome" --headless=new --no-pdf-header-footer \
        --virtual-time-budget=10000 \
        --run-all-compositor-stages-before-draw \
        --print-to-pdf="$out" "file://$(realpath "$html")" || crc=$?
    fi
    if [[ ! -s $out ]]; then
      log "chromium produced no PDF (exit ${crc})"
      return 2
    fi
    used_engine=chromium
    warn_html_copy_order
    return 0
  fi
  if command -v weasyprint >/dev/null 2>&1; then
    log "engine: weasyprint (keeps its bidi warnings; read them)"
    weasyprint "$html" "$out" || return 2
    used_engine=weasyprint
    warn_html_copy_order
    return 0
  fi
  if python3 -c "import weasyprint" >/dev/null 2>&1; then
    log "engine: weasyprint (python module)"
    python3 -c 'from weasyprint import HTML; import sys;
HTML(sys.argv[1]).write_pdf(sys.argv[2])' "$html" "$out" || return 2
    used_engine=weasyprint
    warn_html_copy_order
    return 0
  fi
  log "no HTML engine: install Chromium, or WeasyPrint in a venv"
  log "  (python3 -m venv … && pip install weasyprint; see pdf-output.md)"
  return 1
}

_first_glob() {
  local f
  for f in "$@"; do
    if [[ -e "$f" && -s "$f" ]]; then
      printf '%s\n' "$f"
      return 0
    fi
  done
  return 1
}

verify_pdf() {
  local pdf=$1
  [[ -s $pdf ]] || { log "VERIFY FAIL: $pdf is empty"; return 1; }

  if ! command -v pdfinfo >/dev/null 2>&1; then
    log "VERIFY FAIL: pdfinfo not found (poppler-utils)"
    return 1
  fi
  if ! command -v pdffonts >/dev/null 2>&1; then
    log "VERIFY FAIL: pdffonts not found (poppler-utils)"
    return 1
  fi
  if ! command -v pdftoppm >/dev/null 2>&1; then
    log "VERIFY FAIL: pdftoppm not found (poppler-utils)"
    return 1
  fi

  local pages
  pages=$(pdfinfo "$pdf" 2>/dev/null | awk '/^Pages:/{print $2}')
  log "pages: ${pages:-unknown}"
  if [[ -z ${pages} || ${pages} -lt 1 ]]; then
    log "VERIFY FAIL: could not read page count"
    return 1
  fi

  log "embedded fonts:"
  pdffonts "$pdf" 2>/dev/null | sed -n '1,8p' >&2
  if ! pdffonts "$pdf" 2>/dev/null | tail -n +3 | grep -q 'yes'; then
    log "VERIFY FAIL: no embedded font; Persian may render as boxes"
    return 1
  fi

  local out_prefix="${src_dir}/verify-${stem}"
  rm -f -- "${out_prefix}-first-1.png" "${out_prefix}-first-01.png" \
           "${out_prefix}-last-1.png" "${out_prefix}-last-01.png" \
           "${out_prefix}-mid-1.png" "${out_prefix}-mid-01.png"
  pdftoppm -png -r 110 -f 1 -l 1 "$pdf" "${out_prefix}-first" || {
    log "VERIFY FAIL: pdftoppm first page failed"
    return 1
  }
  if ! _first_glob "${out_prefix}-first-1.png" "${out_prefix}-first-01.png"; then
    log "VERIFY FAIL: first-page raster was not written"
    return 1
  fi
  if [[ $pages -gt 1 ]]; then
    pdftoppm -png -r 110 -f "$pages" -l "$pages" "$pdf" \
      "${out_prefix}-last" || {
      log "VERIFY FAIL: pdftoppm last page failed"
      return 1
    }
    if ! _first_glob "${out_prefix}-last-1.png" "${out_prefix}-last-01.png"; then
      log "VERIFY FAIL: last-page raster was not written"
      return 1
    fi
  fi
  if [[ $pages -gt 2 ]]; then
    local mid=$(( (pages + 1) / 2 ))
    pdftoppm -png -r 110 -f "$mid" -l "$mid" "$pdf" \
      "${out_prefix}-mid" || {
      log "VERIFY FAIL: pdftoppm middle page failed"
      return 1
    }
    if ! _first_glob "${out_prefix}-mid-1.png" "${out_prefix}-mid-01.png"; then
      log "VERIFY FAIL: middle-page raster was not written"
      return 1
    fi
  fi
  log "rasterised samples: ${out_prefix}-*.png — look at them, do not"
  log "  judge *display* RTL from pdftotext"

  local order_rc=0 order_out="" visual=0 logical=0
  if command -v pdftotext >/dev/null 2>&1; then
    order_out=$(python3 "$here/check-pdf-text-order.py" "$pdf" \
      --source "${src_dir}/${src_base}" 2>&1) || order_rc=$?
    if [[ -n $order_out ]]; then
      while IFS= read -r line; do
        log "$line"
      done <<<"$order_out"
    fi
  else
    log "VERIFY WARN: pdftotext missing; cannot check copy-paste text order"
  fi
  if [[ $order_rc -eq 1 ]]; then
    log "VERIFY FAIL: check-pdf-text-order could not run"
    return 1
  fi
  grep -q 'check-pdf-text-order: visual' <<<"$order_out" && visual=1
  grep -q 'check-pdf-text-order: logical' <<<"$order_out" && logical=1

  if [[ $visual -eq 1 ]]; then
    if have_xelatex; then
      log "VERIFY FAIL: PDF text stream is visual order (copy-paste reverses Persian)"
      log "  Rebuild from the .tex with XeLaTeX. HTML engines cannot store logical RTL."
      return 1
    fi
    log "VERIFY WARN: copy-paste will reverse Persian (HTML engine, no XeLaTeX)"
  elif [[ $logical -eq 0 && ( $used_engine == chromium || $used_engine == weasyprint ) ]] \
      && have_xelatex; then
    log "VERIFY FAIL: HTML-engine PDF while XeLaTeX is installed"
    log "  Chromium/WeasyPrint store visual order. Build the .tex instead."
    return 1
  fi
  return 0
}

rc=0
case "$ext" in
  tex)
    if [[ $engine == chromium || $engine == weasyprint ]]; then
      html="${stem_src}.html"
      [[ -f $html ]] || { log "no $html next to the .tex"; exit 1; }
      html_to_pdf "$html" "$local_pdf"; rc=$?
    else
      compile_tex; rc=$?
      if [[ $rc -eq 2 ]]; then
        log "XeLaTeX is installed but the document failed to compile."
        log "Fix the TeX error above. Not falling back — a fallback here"
        log "  would hide a real error in the .tex."
        exit 1
      fi
      if [[ $rc -eq 1 ]]; then
        log "xelatex or xepersian not available (see scripts/preflight.sh)"
        html="${stem_src}.html"
        if [[ -f $html ]]; then
          log "falling back to $html"
          html_to_pdf "$html" "$local_pdf"; rc=$?
        else
          log "write the HTML from assets/rtl-document.html and retry:"
          log "  $0 ${src_dir}/${html} ${stem}"
          exit 1
        fi
      fi
    fi
    ;;
  html|htm)
    html_to_pdf "$src_base" "$local_pdf"; rc=$?
    ;;
  *)
    echo "build-pdf.sh: expected .tex or .html, got: $src_base" >&2
    exit 2
    ;;
esac

if [[ $rc -ne 0 ]]; then
  log "build failed"
  exit 1
fi

[[ -s $local_pdf ]] || { log "expected PDF missing: ${local_pdf}"; exit 1; }

if [[ $verify -eq 1 ]]; then
  verify_pdf "$local_pdf" || exit 1
fi

mkdir -p "$dest_dir"
cp -f "$local_pdf" "$dest" || exit 1

echo "$dest"
