# Tool Specification: `add_watcher_to_issue`

## Purpose

Add a user as a Jira issue watcher.

## Contract

```python
add_watcher_to_issue(issue_key: str, username: str) -> Dict[str, Any]
```

| Parameter | Required | Behavior |
|---|---|---|
| `issue_key` | Yes | Issue to watch. |
| `username` | Yes | Jira watcher identifier, forwarded without assignee resolution. |

## Execution

1. Fetch the issue through `_async_call`.
2. Add the supplied watcher through `_async_call`.

## Response

```json
{"issue_key": "PROJ-123", "watcher": "alice", "added": true}
```

## Errors

Surface connection, missing issue/user, permission, and Jira watcher errors.

## Verification Requirements

- Issue/user forwarding, success response, and Jira failures.
