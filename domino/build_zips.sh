#!/usr/bin/env bash
# Rebuilds user/downloads/fraud-workshop-code.zip from domino/project/ (the workshop's code).
# Run from anywhere after changing anything in domino/project/: bash domino/build_zips.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="user/downloads/fraud-workshop-code.zip"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
cd "$ROOT"
# Copy domino/project/ (including dotfiles) to the zip root, skipping ignored files
git ls-files -co --exclude-standard domino/project \
  | while read -r f; do rel="${f#domino/project/}"; mkdir -p "$STAGE/$(dirname "$rel")"; cp "$f" "$STAGE/$rel"; done
cp .gitignore "$STAGE/.gitignore"
rm -f "$OUT"
(cd "$STAGE" && zip -qr "$ROOT/$OUT" . -x '.DS_Store')
echo "Wrote $OUT ($(unzip -l "$OUT" | tail -1 | awk '{print $2}') files)"
