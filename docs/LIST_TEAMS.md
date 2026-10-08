# Tool Specification: `list_teams`

## Purpose

List configured teams and their member identifiers.

## Contract

```python
list_teams() -> TeamInfoResponse
```

No caller parameters.

## Execution

1. Read the current in-memory team configuration; no Jira connection is needed.
2. Return the team-name-to-members mapping.

Initial teams come from `JIRA_TEAMS`; runtime changes are not persisted.

## Response

```json
{"teams": {"engineering": ["alice", "bob"]}}
```

Typed as `TeamInfoResponse`; `teams` may be empty.

## Errors

Surface configuration or response serialization errors.

## Verification Requirements

- Empty/populated mappings and visibility of runtime configuration changes.
- Typed serialization without a Jira connection.
