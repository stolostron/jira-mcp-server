# Tool Specification: `transition_issue`

## Purpose

Move an issue through an available Jira workflow transition.

## Contract

```python
transition_issue(issue_key: str, transition: str) -> IssueResponse
```

| Parameter | Required | Behavior |
|---|---|---|
| `issue_key` | Yes | Issue to transition. |
| `transition` | Yes | Available transition name; matched case-insensitively. |

## Execution

1. For names beyond `New`, `Backlog`, and `In Progress`, check fix versions;
   warn when absent without blocking the transition.
2. Fetch available transitions and resolve the requested name to its ID.
3. Transition and refresh through `_async_call`.

## Response

The refreshed [IssueResponse](GET_ISSUE.md).

## Errors

Reject unavailable names with the available transition names. Surface connection,
lookup, permission, workflow, and refresh errors.

## Verification Requirements

- Case-insensitive matching and unavailable-name errors.
- Early-status bypass and nonblocking fix-version warnings.
- Transition execution, refreshed response, and Jira failures.
