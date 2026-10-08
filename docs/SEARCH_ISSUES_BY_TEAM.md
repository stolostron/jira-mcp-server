# Tool Specification: `search_issues_by_team`

## Purpose

Find issues assigned to members of a configured team.

## Contract

```python
search_issues_by_team(
    team_name: str,
    project_key: Optional[str] = None,
    status: Optional[str] = None,
    max_results: int = 100,
) -> List[IssueResponse]
```

| Parameter | Required | Behavior |
|---|---|---|
| `team_name` | Yes | Existing team with at least one member. |
| `project_key` | No | Restrict results to this project. |
| `status` | No | Restrict results to this status name. |
| `max_results` | No | Maximum results requested; defaults to `100`. |

## Execution

1. Resolve configured members and build an OR clause over their assignees.
2. Combine optional project/status filters using AND.
3. Search Jira through the async client.

## Response

List of `IssueResponse` objects; empty when no issues match. See
[get_issue](GET_ISSUE.md) for the response fields.

## Errors

Reject unknown or empty teams. Surface disconnected-client, JQL, and Jira errors.

## Verification Requirements

- Member OR clause, optional AND filters, and result-limit forwarding.
- Unknown/empty teams, response serialization, and search failures.
