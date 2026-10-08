# Tool Specification: `get_project_components`

## Purpose

List the components available in a Jira project.

## Contract

```python
get_project_components(project_key: str) -> List[ComponentResponse]
```

| Parameter | Required | Behavior |
|---|---|---|
| `project_key` | Yes | Project whose components are requested. |

## Execution

1. Fetch project components through `_async_call`.
2. Normalize component identity and assignment information.

## Response

List of `ComponentResponse` objects with `id`, `name`, `description`, `lead`,
`assignee_type`, and `is_assignee_type_valid`. May be empty.

## Errors

Surface connection, missing/inaccessible-project, permission, and Jira errors.

## Verification Requirements

- Project-key forwarding and empty/populated results.
- Component serialization and Jira failures.
