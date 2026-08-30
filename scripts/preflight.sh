#!/usr/bin/env bash
# Report which PDF engines, fonts, and extraction tools exist on this machine
# and what to install for the missing ones. Run before planning a build.
#
#   preflight.sh [--require-tex]
set -uo pipefail

require_tex=0
[[ ${1:-} == --require-tex ]] && require_tex=1

ok()   { printf '  yes   %-22s %s\n' "$1" "${2:-}"; }
no()   { printf '  NO    %-22s %s\n' "$1" "${2:-}"; }

have() { command -v "$1" >/dev/null 2>&1; }

tex=0 chrome=0 weasy=0 fa_font=0

echo "PDF engines"
if have xelatex; then
  if have kpsewhich && ! kpsewhich xepersian.sty >/dev/null 2>&1; then
    no "xepersian.sty" "xelatex is present but the Persian package is not"
  else
    ok "xelatex + xepersian" "$(xelatex --version 2>/dev/null | head -1)"
    tex=1
  fi
else
  no "xelatex" "preferred engine unavailable"
fi
have latexmk && ok "latexmk" "used for reruns and bibliography"

for c in chromium chromium-browser google-chrome google-chrome-stable; do
  if have "$c"; then ok "$c" "HTML print fallback"; chrome=1; break; fi
done
[[ $chrome -eq 0 ]] && no "chromium" "no browser print fallback"

if have weasyprint || python3 -c "import weasyprint" >/dev/null 2>&1; then
  ok "weasyprint" "$(weasyprint --version 2>/dev/null || echo 'python module')"
  weasy=1
  echo "        note: ignores unicode-bidi: isolate — rely on dir=\"ltr\""
  echo "        attributes and keep every cluster in one isolate"
else
  no "weasyprint" "venv: python3 -m venv … && pip install weasyprint"
fi

echo
echo "Fonts"
if have fc-list; then
  faces=$(fc-list :lang=fa family 2>/dev/null | tr ',' '\n' | sort -u \
          | grep -v '^$' | head -8 | paste -sd, - | sed 's/,/, /g')
  if [[ -n $faces ]]; then
    ok "fa-capable faces" "$faces"
    fc-list :lang=fa family 2>/dev/null | grep -qi vazirmatn \
      && ok "Vazirmatn" "preferred text face" \
      || no "Vazirmatn" "run scripts/fetch-vazirmatn.sh fonts"
    fa_font=1
  else
    no "fa-capable face" "run scripts/fetch-vazirmatn.sh fonts"
  fi
  fc-list :lang=fa family 2>/dev/null | grep -qi 'UI-FD\|Farsi.*Digit' \
    && echo "        warn: a Farsi-digit cut is installed; never select it"
else
  no "fc-list" "install fontconfig to detect fonts"
fi

echo
echo "Source extraction and verification"
for t in pdftotext pdfimages pdftoppm pdfinfo pdffonts curl unzip; do
  have "$t" && ok "$t" || no "$t"
done
have python3 && ok "python3" "required by scripts/check-fa.py" \
             || no "python3" "check-fa.py will not run"
if python3 -c "import PIL.Image" >/dev/null 2>&1; then
  ok "Pillow" "scripts/prepare-figures.py"
elif have magick || have convert; then
  ok "ImageMagick" "scripts/prepare-figures.py fallback"
else
  no "Pillow/ImageMagick" "figures cannot be flattened; pip install pillow"
fi
if python3 -c "import pymupdf" >/dev/null 2>&1; then
  ok "PyMuPDF" "scripts/crop-source-figures.py"
else
  no "PyMuPDF" "cannot crop PDF artwork; pip install pymupdf"
fi

echo
echo "Verdict"
if [[ $tex -eq 1 ]]; then
  echo "  build .tex with XeLaTeX — best print RTL, selectable text"
elif [[ $chrome -eq 1 ]]; then
  echo "  no TeX: build .html with Chromium (display RTL only;"
  echo "  copy-paste will reverse Persian)"
elif [[ $weasy -eq 1 ]]; then
  echo "  no TeX and no Chromium: build .html with WeasyPrint, and keep"
  echo "  every English cluster in a single dir=\"ltr\" isolate"
  echo "  (copy-paste will reverse Persian)"
else
  echo "  no engine can produce a PDF — stop and tell the user"
fi
[[ $fa_font -eq 0 ]] && echo "  fetch a Persian font before building"

if [[ $tex -eq 0 ]]; then
  echo
  echo "Install the preferred engine (Debian/Ubuntu):"
  echo "  sudo apt install texlive-xetex texlive-lang-arabic \\"
  echo "                  texlive-fonts-recommended latexmk"
fi

if [[ $require_tex -eq 1 && $tex -eq 0 ]]; then
  exit 1
fi
exit 0
