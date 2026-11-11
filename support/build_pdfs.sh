#!/usr/bin/env bash
# Builds fraud-workshop-guide.pdf and admin-setup-guide.pdf from the HTML guides, using headless
# Google Chrome. Run after editing a guide: bash support/build_pdfs.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
[ -x "$CHROME" ] || CHROME="$(command -v google-chrome || command -v chromium || true)"
[ -n "$CHROME" ] || { echo "Chrome not found; set CHROME=/path/to/chrome"; exit 1; }
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
for name in fraud-workshop-guide admin-setup-guide; do
  # Open every <details> so the PDF shows all content
  sed 's/<details>/<details open>/g' "$ROOT/$name.html" > "$TMP/$name.html"
  "$CHROME" --headless=new --disable-gpu --no-pdf-header-footer --run-all-compositor-stages-before-draw \
    --virtual-time-budget=15000 --print-to-pdf="$ROOT/$name.pdf" "file://$TMP/$name.html" >/dev/null 2>&1
  echo "Wrote $name.pdf"
done
