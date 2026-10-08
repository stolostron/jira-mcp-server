# Tool Specification: `get_issue`

## Purpose

Retrieve a Jira issue as normalized structured data, including comment IDs.

## Contract

```python
get_issue(issue_key: str) -> IssueResponse
```

| Parameter | Required | Behavior |
|---|---|---|
| `issue_key` | Yes | Jira issue key, such as `PROJ-123`. |

## Execution

1. Fetch the issue through `_async_call`, expanding changelog, transitions,
   and comments.
2. Normalize Jira fields into `IssueResponse`.

## Response

`IssueResponse` contains:

- Identity/content: `key`, `summary`, `description`, `status`, `priority`,
  `issue_type`, `project`, `url`.
- People/timestamps: `assignee`, `reporter`, `created`, `updated`, `resolution`.
- Classification: `labels`, `components`, `fix_versions`, `target_version`,
  `activity_type`, `security_level`.
- Planning: `due_date`, `target_start`, `target_end`, `original_estimate`,
  `story_points`.
- References: `git_commit`, `git_pull_requests`, `parent`, `subtasks`.
- `comments`: objects with `id`, `body`, `author`, `created`, and `updated`.
  Use `id` with [edit_comment](EDIT_COMMENT.md) or [delete_comment](DELETE_COMMENT.md).

Nullable fields represent missing values; list fields may be empty.

## Errors

Surface disconnected-client, missing/inaccessible-issue, permission, and Jira errors.

## Verification Requirements

- Issue-key forwarding, optional fields, hierarchy, and comment IDs.
- Structured response serialization and lookup failures.
