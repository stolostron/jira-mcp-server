# Tool Specification: `log_time`

## Purpose

Create a work log recording time spent on a Jira issue.

## Contract

```python
log_time(
    issue_key: str,
    time_spent: str,
    comment: str,
    started: Optional[str] = None,
) -> WorkLogResponse
```

| Parameter | Required | Behavior |
|---|---|---|
| `issue_key` | Yes | Issue receiving the work log. |
| `time_spent` | Yes | Jira duration, such as `1h 30m` or `45m`. |
| `comment` | Yes | Description of the work. |
| `started` | No | ISO start timestamp; omitted when `None`, allowing Jira's default. |

## Execution

1. Fetch the issue through `_async_call`.
2. Create a work log with duration, comment, and optional start timestamp.

## Response

`WorkLogResponse` with `id`, `time_spent`, `comment`, `author`, `created`, and
`started`.

## Errors

Surface connection, lookup, duration/timestamp validation, permission, and
work-log creation errors.

## Verification Requirements

- Required fields and optional start timestamp forwarding.
- Work-log serialization and Jira error propagation.
