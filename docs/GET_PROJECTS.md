# Tool Specification: `get_projects`

## Purpose

List Jira projects accessible to the authenticated user.

## Contract

```python
get_projects() -> List[ProjectResponse]
```

No caller parameters.

## Execution

1. Fetch projects through `_async_call`.
2. Normalize project information into structured responses.

## Response

List of `ProjectResponse` objects with `key`, `name`, `description`, and `lead`.
May be empty.

## Errors

Surface disconnected-client, permission, and Jira listing errors.

## Verification Requirements

- Empty/populated lists, project serialization, and Jira failures.
