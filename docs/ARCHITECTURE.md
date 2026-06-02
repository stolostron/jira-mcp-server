# Architecture: Jira MCP Server

## Overview

A Python MCP (Model Context Protocol) server built with [FastMCP](https://github.com/jlowin/fastmcp) that wraps the Jira REST API and exposes it as structured tools for AI assistants.

## Module Layout

```
jira_mcp_server/
├── main.py      # CLI entry point; parses --transport flag; bootstraps JiraMCPServer
├── server.py    # JiraMCPServer: registers all MCP tools and resources via FastMCP decorators
├── client.py    # JiraClient: async wrapper around python-jira with rate limiting (10 req/s)
└── config.py    # JiraConfig: env-var-based config, teams, component alias resolution
```

## Transport Modes

| Mode | Flag | How it works |
|------|------|---|
| stdio | `--transport stdio` (default) | MCP protocol over stdin/stdout; used by Claude Desktop and similar |
| SSE | `--transport sse` | HTTP server (uvicorn + Starlette) at `--host`/`--port`; exposes `/sse` and `/messages/` endpoints |

## Key Data Flow

```
AI client → MCP tool call
  → JiraMCPServer tool handler (server.py)
  → JiraClient async method (client.py)
  → python-jira (sync, run in executor) → Jira REST API
  → Pydantic response model → AI client
```

The Jira client wraps all synchronous python-jira calls via `asyncio.run_in_executor` + `asyncio_throttle` (10 req/s limit).

## Configuration (Environment Variables)

| Variable | Required | Description |
|---|---|---|
| `JIRA_SERVER_URL` | Yes | Jira instance URL |
| `JIRA_ACCESS_TOKEN` | Yes | Personal access token (Server) or API token (Cloud) |
| `JIRA_EMAIL` | Yes | User email (required for Cloud basic auth) |
| `JIRA_VERIFY_SSL` | No | Default `true` |
| `JIRA_TIMEOUT` | No | Default `30` seconds |
| `JIRA_MAX_RESULTS` | No | Default `100` |
| `JIRA_TEAMS` | No | JSON: `{"team-name": ["user1", "user2"]}` |
| `JIRA_COMPONENT_ALIASES` | No | JSON: `{"alias": "Full Component Name"}` |

Copy `.env.example` to `.env` and fill in values before running.

## Custom Jira Field IDs (Red Hat specific)

These are hardcoded in `server.py` — if migrating to a different Jira instance, update them there.

| Field | Jira ID |
|---|---|
| Target Version | `customfield_10855` |
| Work Type (Activity Type) | `customfield_10464` |
| Target Start | `customfield_10022` |
| Target End | `customfield_10023` |
| Story Points | `customfield_10028` |
| Git Commit | `customfield_10583` |
| Git Pull Requests | `customfield_10875` |
| Epic Name | `customfield_10011` |

## Non-obvious Design Decisions

- **Transition guard**: `transition_issue` warns (but does not block) if `fix_version` is unset for statuses beyond "New", "Backlog", "In Progress" — matches Red Hat release-tracking policy.
- **Teams and component aliases are runtime-only**: `add_team`/`remove_team` and `add_component_alias`/`remove_component_alias` mutate the in-memory `JiraConfig` dict. They reset on restart — persist via `JIRA_TEAMS` / `JIRA_COMPONENT_ALIASES` env vars.
- **Update check on startup**: fetches `origin/main` and emits a warning via MCP context if behind; fires once per session via `_update_warning_emitted` guard.
- **Assignee resolution**: `client.py` resolves email/username strings to Jira `accountId` automatically when creating or updating issues.
