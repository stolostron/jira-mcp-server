# Tool Specification: `create_issue`

## Purpose

Create a Jira issue, optionally adding configured team members as watchers.
Creation produces a permanent record; use only when explicitly requested.

## Contract

```python
create_issue(
    project_key: str,
    summary: str,
    description: str,
    priority: str = "Normal",
    activity_type: Optional[str] = None,
    components: Optional[List[str]] = None,
    target_version: Optional[List[str]] = None,
    issue_type: str = "Task",
    due_date: Optional[str] = None,
    assignee: Optional[str] = None,
    team: Optional[str] = None,
    labels: Optional[List[str]] = None,
    fix_versions: Optional[List[str]] = None,
    security_level: Optional[str] = "Red Hat Employee",
    target_start: Optional[str] = None,
    target_end: Optional[str] = None,
    original_estimate: Optional[str] = None,
    story_points: Optional[float] = None,
    git_commit: Optional[str] = None,
    git_pull_requests: Optional[str] = None,
    parent: Optional[str] = None,
    epic_name: Optional[str] = None,
) -> IssueResponse
```

| Parameter | Required | Behavior |
|---|---|---|
| `project_key`, `summary`, `description` | Yes | Target project and content; summary/description must not be blank. |
| `priority`, `issue_type` | No | Default to `Normal` and `Task`. |
| `activity_type` | No | Recognized global label or numeric option ID; Jira may require a project-specific ID. |
| `components` | No | Component names or configured aliases. |
| `target_version`, `fix_versions` | No | Version names; a supplied fix-version list must not be empty. |
| `due_date`, `target_start`, `target_end` | No | Dates in `YYYY-MM-DD` format. |
| `assignee` | No | Nonblank user identifier resolved to a Cloud account ID. |
| `team` | No | Configured team to add as watchers after creation. |
| `labels` | No | Issue labels. |
| `security_level` | No | Defaults to `Red Hat Employee`; `None` omits issue security. |
| `original_estimate`, `story_points` | No | Jira duration, such as `1h 30m`, and numeric points. |
| `git_commit`, `git_pull_requests` | No | 40/64-character hexadecimal SHA and comma-separated PR URLs. |
| `parent`, `epic_name` | No | Parent issue key; Epic Name where required by Jira. |

## Execution

1. Validate content, supplied assignee/fix versions, and commit SHA.
2. Resolve assignee, activity option ID, and component aliases; map Jira fields.
3. Create through `_async_call`; convert duration estimates to minute strings.
4. If requested, add team watchers; watcher failures do not roll back creation.

## Response

The created [IssueResponse](GET_ISSUE.md). Team watcher exceptions generate a
warning; per-member failures are not included in this response.

## Errors

Surface validation, assignee-resolution, disconnected-client, permission, and
Jira creation errors. Jira enforces project/issue-type required fields.

## Verification Requirements

- Defaults, required-content validation, field mappings, and SHA validation.
- Alias/activity/assignee resolution and estimate conversion.
- Creation errors and watcher failures after successful creation.
