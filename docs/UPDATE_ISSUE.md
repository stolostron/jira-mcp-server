# Tool Specification: `update_issue`

## Purpose

Update supplied Jira issue fields and return the refreshed issue.

## Contract

```python
update_issue(
    issue_key: str,
    priority: Optional[str] = None,
    activity_type: Optional[str] = None,
    components: Optional[List[str]] = None,
    due_date: Optional[str] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    assignee: Optional[str] = None,
    labels: Optional[List[str]] = None,
    fix_versions: Optional[List[str]] = None,
    target_version: Optional[List[str]] = None,
    security_level: Optional[str] = None,
    target_start: Optional[str] = None,
    target_end: Optional[str] = None,
    original_estimate: Optional[str] = None,
    story_points: Optional[float] = None,
    git_commit: Optional[str] = None,
    git_pull_requests: Optional[str] = None,
    parent: Optional[str] = None,
) -> IssueResponse
```

| Parameter | Required | Behavior |
|---|---|---|
| `issue_key` | Yes | Issue to update. |
| `summary`, `description`, `priority`, `security_level` | No | Replacement content or Jira option names. |
| `activity_type` | No | Recognized global label or numeric option ID. |
| `components` | No | Component names or configured aliases. |
| `labels`, `fix_versions`, `target_version` | No | Replacement lists; versions use names. |
| `assignee` | No | User identifier resolved to a Cloud account ID. |
| `due_date`, `target_start`, `target_end` | No | Dates in `YYYY-MM-DD` format. |
| `original_estimate`, `story_points` | No | Jira duration and numeric points. |
| `git_commit`, `git_pull_requests` | No | 40/64-character hexadecimal SHA and comma-separated PR URLs. |
| `parent` | No | Replacement parent issue key. |

## Execution

1. Map supplied fields; resolve assignee, activity option ID, and component aliases.
2. Validate a supplied commit SHA and require at least one effective update.
3. Update and refresh through `_async_call`; convert duration estimates to minutes.

Empty strings/lists and `None` are omitted; `story_points=0` is sent.
Use [clear_field](CLEAR_FIELD.md) to unset fields.

## Response

The refreshed [IssueResponse](GET_ISSUE.md).

## Errors

Reject requests with no effective fields or invalid commit SHAs. Surface
resolution, connection, lookup, permission, update, and refresh failures.

## Verification Requirements

- Field mappings, omitted empty values, zero points, and no-field rejection.
- Alias/activity/assignee resolution, estimate conversion, and refresh behavior.
- Jira failures and structured response serialization.
