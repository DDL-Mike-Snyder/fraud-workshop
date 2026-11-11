#!/usr/bin/env bash
# Rebuilds support/fraud-workshop-code.zip from this repo, for people who use the
# "upload a zip" option instead of Git. Run from anywhere: bash support/build_zips.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
cd "$ROOT"
# Everything tracked or new (not ignored), minus the guides, support folder and Git metadata
git ls-files -co --exclude-standard \
  | grep -v -E '^(support/|admin-setup-guide\.|fraud-workshop-guide\.|README\.md$)' \
  | while read -r f; do mkdir -p "$STAGE/$(dirname "$f")"; cp "$f" "$STAGE/$f"; done
cp exercises/README.md "$STAGE/README.md"
rm -f support/fraud-workshop-code.zip
(cd "$STAGE" && zip -qr "$ROOT/support/fraud-workshop-code.zip" . -x '.DS_Store')
echo "Wrote support/fraud-workshop-code.zip ($(unzip -l support/fraud-workshop-code.zip | tail -1 | awk '{print $2}') files)"
