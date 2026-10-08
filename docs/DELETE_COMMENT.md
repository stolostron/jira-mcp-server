# Tool Specification: `delete_comment`

## Purpose

Permanently delete one Jira comment identified by its issue key and comment ID.

**This operation is destructive and cannot be undone through this tool.**

Tracked by **ACM-47768**.

## Contract

```python
delete_comment(
    issue_key: str,
    comment_id: str,
) -> DeleteCommentResponse
```

| Parameter | Required | Behavior |
|---|---|---|
| `issue_key` | Yes | Issue containing the comment; must not be blank. |
| `comment_id` | Yes | Comment ID to delete; must not be blank. |

Obtain comment IDs from the `comments` list returned by `get_issue`.

No bulk deletion or comment-body matching is supported.

## Execution

1. Reject blank identifiers and require a connected Jira client.
2. Fetch the comment through the issue-scoped API using both identifiers.
3. Delete that comment resource.
4. Return success only after Jira confirms deletion.

All synchronous Jira operations must execute through `_async_call`.

## Success Confirmation

Accept a confirmed successful HTTP response, including an empty **204 No
Content** response. Do not require a JSON response body.

A missing response, queued operation, or unsuccessful HTTP status must not
produce a success result.

## Response

```json
{
  "issue_key": "PROJ-123",
  "comment_id": "10001",
  "deleted": true
}
```

The response must use the typed `DeleteCommentResponse` model.

## Errors

Surface disconnected-client, missing/inaccessible-comment, wrong-issue,
permission, and deletion failures as tool errors.

Repeated deletion may return a missing-comment error rather than success. If a
connection fails after Jira processes the deletion, the outcome may be
uncertain; inspect the issue before retrying.

## MCP Annotations

```json
{
  "title": "Delete Jira issue comment",
  "destructiveHint": true,
  "idempotentHint": false,
  "openWorldHint": true
}
```

Tool documentation must explicitly describe deletion as permanent and
destructive.

## Verification Requirements

- Blank-identifier rejection and disconnected-client errors.
- Issue-scoped lookup with both identifiers.
- Missing/wrong-issue and permission failures.
- Successful empty HTTP response handling.
- Rejection of absent or unsuccessful deletion responses.
- `_async_call` use for lookup and deletion.
- MCP registration, destructive annotation, and typed response serialization.
