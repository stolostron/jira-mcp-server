# Tool Specification: `add_team`

## Purpose

Add a team or replace an existing team's member list in runtime configuration.

## Contract

```python
add_team(team_name: str, members: List[str]) -> TeamInfoResponse
```

| Parameter | Required | Behavior |
|---|---|---|
| `team_name` | Yes | Configuration key; existing names are overwritten. |
| `members` | Yes | Complete list of Jira member identifiers; an empty list is allowed. |

## Execution

1. Store the supplied member list under the team name.
2. Return all teams; no Jira connection or member validation is performed.

Changes last until restart. Set `JIRA_TEAMS` for persistent configuration.

## Response

`TeamInfoResponse` containing `teams`, the complete team-name-to-members mapping.

## Errors

Surface input type, configuration, or serialization errors.

## Verification Requirements

- Creation, replacement, empty members, and full configuration response.
- Operation without a Jira connection.
