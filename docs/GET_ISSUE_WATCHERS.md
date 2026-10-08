# Tool Specification: `get_issue_watchers`

## Purpose

List users watching a Jira issue.

## Contract

```python
get_issue_watchers(issue_key: str) -> List[WatcherResponse]
```

| Parameter | Required | Behavior |
|---|---|---|
| `issue_key` | Yes | Issue whose watchers are requested. |

## Execution

1. Fetch issue watchers through `_async_call`.
2. Normalize watcher identity, email, and active status.

## Response

List of `WatcherResponse` objects with `username`, `display_name`, nullable
`email`, and `active`. May be empty.

## Errors

Surface connection, missing/inaccessible-issue, permission, and Jira errors.

## Verification Requirements

- Issue-key forwarding, empty results, and optional email handling.
- Watcher serialization and Jira failures.
