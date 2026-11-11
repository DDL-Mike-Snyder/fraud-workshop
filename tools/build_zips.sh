#!/usr/bin/env bash
# Rebuilds user/downloads/fraud-workshop-code.zip from this repo, for people who use the
# "upload a zip" option instead of Git. Run from anywhere: bash tools/build_zips.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="user/downloads/fraud-workshop-code.zip"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
cd "$ROOT"
# The Domino project files only: leave out the admin and user folders, the tools and the root README
git ls-files -co --exclude-standard \
  | grep -v -E '^(admin/|user/|tools/|README\.md$)' \
  | while read -r f; do mkdir -p "$STAGE/$(dirname "$f")"; cp "$f" "$STAGE/$f"; done
cp exercises/README.md "$STAGE/README.md"
rm -f "$OUT"
(cd "$STAGE" && zip -qr "$ROOT/$OUT" . -x '.DS_Store')
echo "Wrote $OUT ($(unzip -l "$OUT" | tail -1 | awk '{print $2}') files)"
