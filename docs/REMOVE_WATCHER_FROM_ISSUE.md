# Tool Specification: `remove_watcher_from_issue`

## Purpose

Remove a user from an issue's watchers.

## Contract

```python
remove_watcher_from_issue(issue_key: str, username: str) -> Dict[str, Any]
```

| Parameter | Required | Behavior |
|---|---|---|
| `issue_key` | Yes | Issue whose watcher is removed. |
| `username` | Yes | Jira watcher identifier, forwarded without assignee resolution. |

## Execution

1. Fetch the issue through `_async_call`.
2. Remove the supplied watcher through `_async_call`.

## Response

```json
{"issue_key": "PROJ-123", "watcher": "alice", "removed": true}
```

## Errors

Surface connection, missing issue/user, permission, and Jira watcher errors.

## Verification Requirements

- Issue/user forwarding, success response, and Jira failures.
