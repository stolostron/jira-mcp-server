# Tool Specification: `link_issue`

## Purpose

Create a directed Jira issue link, optionally including a comment.

## Contract

```python
link_issue(
    link_type: str,
    inward_issue: str,
    outward_issue: str,
    comment: Optional[str] = None,
    security_level: Optional[str] = None,
) -> LinkResponse
```

| Parameter | Required | Behavior |
|---|---|---|
| `link_type` | Yes | Jira link type name, such as `Blocks` or `Relates`. |
| `inward_issue`, `outward_issue` | Yes | Issue keys passed as Jira's inward/outward endpoints. |
| `comment` | No | Comment accompanying link creation. |
| `security_level` | No | Group restriction for the supplied comment; default is unrestricted. |

Use [get_link_types](GET_LINK_TYPES.md) to inspect directional descriptions.

## Execution

1. Build optional comment data and group visibility.
2. Create the link through `_async_call`.
3. Fetch link types to resolve inward/outward descriptions case-insensitively.

## Response

`LinkResponse` with `link_type`, `inward_issue`, `outward_issue`, nullable
`inward_description`, `outward_description`, `comment`, and `created: true`.

## Errors

Surface connection, invalid link type, missing issues, permission, and Jira errors.
A description lookup failure after creation does not roll back the link.

## Verification Requirements

- Endpoint direction, optional comment visibility, and type descriptions.
- Response serialization and creation/post-creation lookup failures.
