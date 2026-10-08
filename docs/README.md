# MCP Tool Specifications

Each specification uses the same core layout: **Purpose**, **Contract**,
**Execution**, **Response**, **Errors**, and **Verification Requirements**.
Tool-specific sections describe visibility, confirmation, or MCP annotations.

Contracts omit the server-injected `ctx` progress-reporting argument. Jira-backed
tools require a connected client and run synchronous Jira calls through
`_async_call` with rate limiting. Configuration-only tools operate in memory.
Errors are surfaced as MCP tool errors unless a spec describes partial success.
Verification sections describe expected checks, not a claim of existing coverage.

## Issues

- [search_issues](SEARCH_ISSUES.md)
- [search_issues_by_team](SEARCH_ISSUES_BY_TEAM.md)
- [get_issue](GET_ISSUE.md)
- [create_issue](CREATE_ISSUE.md)
- [update_issue](UPDATE_ISSUE.md)
- [clear_field](CLEAR_FIELD.md)
- [transition_issue](TRANSITION_ISSUE.md)
- [debug_issue_fields](DEBUG_ISSUE_FIELDS.md)

## Comments and Work Logs

- [add_comment](ADD_COMMENT.md)
- [edit_comment](EDIT_COMMENT.md)
- [delete_comment](DELETE_COMMENT.md)
- [log_time](LOG_TIME.md)

## Projects, Links, and Users

- [get_projects](GET_PROJECTS.md)
- [get_project_versions](GET_PROJECT_VERSIONS.md)
- [get_project_components](GET_PROJECT_COMPONENTS.md)
- [link_issue](LINK_ISSUE.md)
- [get_link_types](GET_LINK_TYPES.md)
- [search_users](SEARCH_USERS.md)

## Watchers and Teams

- [assign_team_to_issue](ASSIGN_TEAM_TO_ISSUE.md)
- [add_watcher_to_issue](ADD_WATCHER_TO_ISSUE.md)
- [remove_watcher_from_issue](REMOVE_WATCHER_FROM_ISSUE.md)
- [get_issue_watchers](GET_ISSUE_WATCHERS.md)
- [list_teams](LIST_TEAMS.md)
- [add_team](ADD_TEAM.md)
- [remove_team](REMOVE_TEAM.md)

## Component Aliases

- [list_component_aliases](LIST_COMPONENT_ALIASES.md)
- [add_component_alias](ADD_COMPONENT_ALIAS.md)
- [remove_component_alias](REMOVE_COMPONENT_ALIAS.md)
