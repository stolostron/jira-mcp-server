# Tool Specification: `search_issues`

## Purpose

Find Jira issues matching a JQL query.

## Contract

```python
search_issues(jql: str, max_results: int = 100) -> List[IssueResponse]
```

| Parameter | Required | Behavior |
|---|---|---|
| `jql` | Yes | Jira Query Language expression. |
| `max_results` | No | Maximum results requested; defaults to `100`. |

## Execution

1. Search Jira through `_async_call`, expanding changelog information.
2. Normalize matching issues into structured responses.

## Response

List of `IssueResponse` objects; empty when no issues match. See
[get_issue](GET_ISSUE.md) for the response fields.

## Errors

Surface disconnected-client, invalid-JQL, permission, and Jira search failures.

## Verification Requirements

- Query and result-limit forwarding; empty and populated results.
- Issue serialization and Jira error propagation.
