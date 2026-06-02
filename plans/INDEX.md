# Work Sessions

sessions:
# ──────────────────────────────────────────────────────────
- date: "2026-05-06"
  title: "Package Jira MCP server as standalone bundle for agent-containers"
  jira: "ACM-33687"
  jira_url: "https://redhat.atlassian.net/browse/ACM-33687"
  status: "In Progress"
  pr: "https://github.com/jnpacker/agent-containers/pull/new/ACM-33677"
  summary: "Implemented wheel-based distribution via GitHub Releases. Created release workflow, tagged v0.1.0, updated agent-containers to pip install from releases using gh CLI with build-time secret auth"

---
- date: "2026-06-02"
  title: "Update jira-mcp-server repository for Agentic SDLC"
  jira: "ACM-34733"
  jira_url: "https://redhat.atlassian.net/browse/ACM-34733"
  pr: "https://github.com/jnpacker/jira-mcp-server/pull/1"
  summary: "Added 20 server-level MCP tests, ruff linting, GitHub Actions CI (pytest matrix + lint), updated README, removed skills/agents from git tracking, and completed Agentic SDLC onboarding with docs/ARCHITECTURE.md"

---
- date: "2026-06-02"
  title: "Onboard jira-mcp-server to Fleet Engineering Agentic SDLC"
  jira: "ACM-34735"
  jira_url: "https://redhat.atlassian.net/browse/ACM-34735"
  pr: "https://github.com/jnpacker/jira-mcp-server/pull/1"
  summary: "Updated CLAUDE.md with dev commands and agent guidance, created docs/ARCHITECTURE.md with module layout and design decisions, implemented all ACM-34733 work items on branch ACM-34735/chore-agentic-sdlc-onboarding"
