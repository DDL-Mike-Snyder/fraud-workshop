#!/usr/bin/env bash
# Builds user/fraud-workshop-guide.pdf and admin/admin-setup-guide.pdf from the HTML guides,
# using headless Google Chrome. Run after editing a guide: bash domino/build_pdfs.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
[ -x "$CHROME" ] || CHROME="$(command -v google-chrome || command -v chromium || true)"
[ -n "$CHROME" ] || { echo "Chrome not found; set CHROME=/path/to/chrome"; exit 1; }
REPO_URL="${REPO_URL:-https://github.com/DDL-Mike-Snyder/fraud-workshop/blob/main}"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
for f in user/fraud-workshop-guide admin/admin-setup-guide; do
  name="$(basename "$f")"
  # Open every <details>, and point links to the other guide at its PDF on GitHub
  sed -e 's/<details>/<details open>/g' \
      -e "s#href=\"../admin/admin-setup-guide.html[^\"]*\"#href=\"$REPO_URL/admin/admin-setup-guide.pdf\"#g" \
      -e "s#href=\"../user/fraud-workshop-guide.html[^\"]*\"#href=\"$REPO_URL/user/fraud-workshop-guide.pdf\"#g" \
      "$ROOT/$f.html" > "$TMP/$name.html"
  "$CHROME" --headless=new --disable-gpu --no-pdf-header-footer --run-all-compositor-stages-before-draw \
    --virtual-time-budget=15000 --print-to-pdf="$ROOT/$f.pdf" "file://$TMP/$name.html" >/dev/null 2>&1
  echo "Wrote $f.pdf"
done
