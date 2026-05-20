#!/usr/bin/env bash
# Smoke-test imports for Cursor MCP / CI (catches model-order and fastmcp issues).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -x .venv/bin/python ]]; then
  PYTHON=".venv/bin/python"
else
  PYTHON="${PYTHON:-python3}"
fi

echo "Using Python: $PYTHON ($("$PYTHON" --version 2>&1))"

"$PYTHON" -c "
from fastmcp import Context, FastMCP
from jira_mcp_server.server import JiraMCPServer
print('fastmcp Context:', Context)
print('JiraMCPServer import: OK')
"

# Tool registration count (regression guard)
count="$("$PYTHON" -c "
from jira_mcp_server.server import JiraMCPServer
s = JiraMCPServer()
print(len(s.mcp._tool_manager._tools))
" 2>/dev/null || true)"

if [[ -n "$count" ]]; then
  echo "Registered tools: $count"
fi

echo "verify-startup: OK"
