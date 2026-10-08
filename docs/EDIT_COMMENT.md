# Tool Specification: `edit_comment`

## Purpose

Replace the body of a specific Jira issue comment while preserving its existing
visibility restriction. Optionally restrict a public comment to the **Red Hat
Employee** group.

Tracked by **ACM-47768**.

## Contract

```python
edit_comment(
    issue_key: str,
    comment_id: str,
    comment: str,
    secure_comment: bool = False,
) -> CommentResponse
```

| Parameter | Required | Behavior |
|---|---|---|
| `issue_key` | Yes | Issue containing the comment; must not be blank. |
| `comment_id` | Yes | Comment ID; must not be blank. |
| `comment` | Yes | Replacement body; must not be blank. Preserve nonblank text exactly, including surrounding whitespace. |
| `secure_comment` | No | Defaults to `False`. When `True`, restrict a public comment to the Red Hat Employee group. |

Obtain comment IDs from the `comments` list returned by `get_issue`.

## Visibility Rules

| Existing visibility | `secure_comment` | Update |
|---|---|---|
| Public | `False` | Body only; remain public. |
| Public | `True` | Body plus Red Hat Employee group restriction. |
| Group-restricted | Either | Body only; preserve restriction. |
| Role-restricted | Either | Body only; preserve restriction. |

When preserving visibility, **omit `visibility` from the update payload**. Do not
copy the fetched restriction into the payload.

The tool must not expose arbitrary security groups, replace existing
restrictions, or provide an option to make comments public.

## Execution

1. Reject blank arguments and require a connected Jira client.
2. Fetch the comment through the issue-scoped API using both identifiers.
3. Inspect its current visibility immediately before updating.
4. Update the body, adding visibility only for the public-to-restricted case.
5. Return the refreshed comment as `CommentResponse`.

All synchronous Jira operations must execute through `_async_call`.

## Response

```json
{
  "id": "10001",
  "body": "Updated comment text",
  "author": "Test User",
  "created": "2026-01-01T00:00:00.000+0000",
  "updated": "2026-01-02T00:00:00.000+0000"
}
```

## Errors

Surface disconnected-client, missing-comment, wrong-issue, permission, and
update failures as tool errors.

The visibility check and update are **not atomic**. Without a supported
conditional update, another actor can change visibility between the read and
the write. A public-to-restricted update can consequently replace a restriction
added concurrently. Body-only updates omit visibility to avoid intentionally
overwriting restrictions.

An error during the post-update refresh does not prove that the write failed.

## Verification Requirements

- Public and restricted visibility cases, including both group and role
  restrictions with each flag value.
- Exact preservation of nonblank replacement text.
- Omission of visibility when preserving restrictions.
- Blank-input rejection and disconnected-client errors.
- Issue-scoped lookup and missing/wrong-issue/permission failures.
- MCP registration, default arguments, and response serialization.
