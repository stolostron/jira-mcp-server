# Tool Specification: `get_link_types`

## Purpose

List Jira issue link types and their directional descriptions.

## Contract

```python
get_link_types() -> List[LinkTypeResponse]
```

No caller parameters.

## Execution

1. Fetch issue link types through `_async_call`.
2. Normalize each type and its inward/outward descriptions.

## Response

List of `LinkTypeResponse` objects with `id`, `name`, `inward`, and `outward`.
Use `name` with [link_issue](LINK_ISSUE.md).

## Errors

Surface disconnected-client, permission, and Jira listing errors.

## Verification Requirements

- Empty/populated results, directional descriptions, and Jira failures.
