# Tool Specification: `search_users`

## Purpose

Find Jira users by partial name or email using Cloud-compatible search.

## Contract

```python
search_users(query: str, max_results: int = 50) -> List[UserResponse]
```

| Parameter | Required | Behavior |
|---|---|---|
| `query` | Yes | User search text, such as a display name or email. |
| `max_results` | No | Maximum results requested; defaults to `50`. |

## Execution

1. Query `/rest/api/2/user/search` with `query` and `maxResults` through `_async_call`.
2. Normalize matching users.

## Response

List of `UserResponse` objects with nullable `account_id`, `name`,
`email_address`, plus `display_name` and `active`. May be empty; email availability
depends on Jira privacy settings.

## Errors

Surface disconnected-client, HTTP, permission, and Jira search errors.

## Verification Requirements

- Cloud `query` parameter, result limit, and empty results.
- Optional identity/email fields, serialization, and HTTP failures.
