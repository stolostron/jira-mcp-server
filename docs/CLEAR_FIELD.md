# Tool Specification: `clear_field`

## Purpose

Unset one editable Jira field using its schema to choose the empty value.

## Contract

```python
clear_field(issue_key: str, field_name: str) -> IssueResponse
```

| Parameter | Required | Behavior |
|---|---|---|
| `issue_key` | Yes | Issue to update. |
| `field_name` | Yes | Jira field ID, such as `labels`, `assignee`, or `customfield_10855`. |

Discover field IDs using [debug_issue_fields](DEBUG_ISSUE_FIELDS.md).

## Execution

1. Fetch issue edit metadata and reject fields absent from it.
2. Choose `[]` for arrays, `{"originalEstimate": "0m"}` for time tracking,
   and `None` for other schema types.
3. Update and refresh the issue through the async client.

## Response

The refreshed [IssueResponse](GET_ISSUE.md).

## Errors

Reject noneditable fields with a list of available IDs. Surface connection,
metadata, permission, required-field, update, and refresh failures.

## Verification Requirements

- Schema-specific empty values and noneditable-field rejection.
- Field-ID forwarding, refreshed response, and Jira errors.
