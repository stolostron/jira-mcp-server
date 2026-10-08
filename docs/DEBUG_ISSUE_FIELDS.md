# Tool Specification: `debug_issue_fields`

## Purpose

Inspect Jira field IDs and values beyond the normalized issue response.

## Contract

```python
debug_issue_fields(issue_key: str) -> Dict[str, Any]
```

| Parameter | Required | Behavior |
|---|---|---|
| `issue_key` | Yes | Issue whose fields are inspected. |

## Execution

1. Fetch the issue through `_async_call`.
2. Inspect nonprivate, non-null field attributes and simplify complex values
   to names, values, or strings.
3. Include field count and issue identity.

## Response

Dictionary with `issue_key`, `raw_fields` (field ID to simplified value), and
`field_count`. Individual field-access failures appear as error strings.
Values are diagnostic representations, not lossless raw REST JSON.

## Errors

Surface connection, missing/inaccessible-issue, permission, and Jira lookup errors.

## Verification Requirements

- Field IDs, scalar/list/object conversion, and omitted null/private attributes.
- Field-access error strings, counts, and lookup failures.
