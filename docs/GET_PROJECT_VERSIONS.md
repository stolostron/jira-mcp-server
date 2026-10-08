# Tool Specification: `get_project_versions`

## Purpose

List project versions to discover valid fix-version and target-version names.

## Contract

```python
get_project_versions(project_key: str) -> List[VersionResponse]
```

| Parameter | Required | Behavior |
|---|---|---|
| `project_key` | Yes | Project whose versions are requested. |

## Execution

1. Fetch project versions through `_async_call`.
2. Normalize each version, including release/archive status.

## Response

List of `VersionResponse` objects with `id`, `name`, `description`, `released`,
`archived`, and nullable `release_date`. May be empty.

## Errors

Surface connection, missing/inaccessible-project, permission, and Jira errors.

## Verification Requirements

- Project-key forwarding, empty results, and optional release dates.
- Version serialization and Jira failures.
