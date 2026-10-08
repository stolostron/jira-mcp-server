# Tool Specification: `remove_team`

## Purpose

Remove a team from runtime configuration without changing Jira watchers.

## Contract

```python
remove_team(team_name: str) -> TeamInfoResponse
```

| Parameter | Required | Behavior |
|---|---|---|
| `team_name` | Yes | Existing configuration key to remove. |

## Execution

1. Reject unknown team names and remove the selected entry.
2. Return all remaining teams; no Jira connection is needed.

Removal is runtime-only; restart reloads `JIRA_TEAMS`.

## Response

`TeamInfoResponse` containing `teams`, the remaining team-name-to-members mapping.

## Errors

Reject unknown teams with `ValueError`; surface configuration/serialization errors.

## Verification Requirements

- Existing/unknown names and remaining configuration response.
- Operation without Jira watcher changes or a Jira connection.
