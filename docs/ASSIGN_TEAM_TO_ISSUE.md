# Tool Specification: `assign_team_to_issue`

## Purpose

Add configured team members as issue watchers; this does not change the assignee.

## Contract

```python
assign_team_to_issue(issue_key: str, team_name: str) -> TeamAssignmentResponse
```

| Parameter | Required | Behavior |
|---|---|---|
| `issue_key` | Yes | Issue receiving the watchers. |
| `team_name` | Yes | Existing configured team. |

## Execution

1. Resolve the team's members and require a connected Jira client.
2. Add each member through the async watcher client, continuing after failures.
3. Aggregate successes and failures; an empty team yields zero counts.

## Response

`TeamAssignmentResponse` with `issue_key`, `team_name`, `successes` (usernames),
`failures` (objects with `username` and `error`), `total_added`, and `total_failed`.

## Errors

Unknown teams and disconnected clients fail the tool. Per-member Jira errors
are returned in `failures`, allowing partial success.

## Verification Requirements

- Team resolution, empty teams, and member-by-member watcher calls.
- Partial failures, aggregate counts, and typed serialization.
