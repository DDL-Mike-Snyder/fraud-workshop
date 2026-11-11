#!/usr/bin/env bash
set -euo pipefail

# Optional add-on app - separate from the core workshop's app.sh at the repo root.
# to use, run PORT=8501 bash exercises/e_AgentAddOn/app.sh
# requires ANTHROPIC_API_KEY set as a project/app environment variable.

PORT="${PORT:-${1:-8888}}"

if ! pkill -f streamlit 2>/dev/null; then
  echo "No existing Streamlit process found."
else
  echo "Previous Streamlit process killed."
fi

mkdir -p .streamlit
cat > .streamlit/config.toml <<EOF
[browser]
gatherUsageStats = true
[server]
address = "0.0.0.0"
port = $PORT
enableCORS = false
enableXsrfProtection = false
[theme]
primaryColor = "#543FDD"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#FAFAFA"
textColor = "#2E2E38"
EOF

streamlit run exercises/e_AgentAddOn/app.py
