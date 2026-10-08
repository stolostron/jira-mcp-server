# Tool Specification: `add_comment`

## Purpose

Add a comment to a Jira issue with optional group-restricted visibility.

## Contract

```python
add_comment(
    issue_key: str,
    comment: str,
    security_level: Optional[str] = "Red Hat Employee",
) -> CommentResponse
```

| Parameter | Required | Behavior |
|---|---|---|
| `issue_key` | Yes | Issue receiving the comment. |
| `comment` | Yes | Comment body. |
| `security_level` | No | Visibility group; defaults to `Red Hat Employee`. `None` omits restriction. |

## Execution

1. Fetch the issue through `_async_call`.
2. Add the body, including group visibility when a security level is supplied.
3. Normalize the created comment.

## Response

`CommentResponse` with `id`, `body`, `author`, `created`, and `updated`.
Use the returned ID with [edit_comment](EDIT_COMMENT.md) or
[delete_comment](DELETE_COMMENT.md).

## Errors

Surface disconnected-client, issue lookup, invalid group, permission, and
comment creation errors. Jira validates the body.

## Verification Requirements

- Default restriction, explicit group, and unrestricted creation.
- Body forwarding, comment serialization, and Jira errors.
