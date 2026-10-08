# Tool Specification: `add_component_alias`

## Purpose

Add or replace a runtime shortcut used when creating/updating issue components.

## Contract

```python
add_component_alias(alias: str, component_name: str) -> ComponentAliasResponse
```

| Parameter | Required | Behavior |
|---|---|---|
| `alias` | Yes | Shortcut key; an existing entry is overwritten. |
| `component_name` | Yes | Jira component name to substitute. |

## Execution

1. Store the alias-to-name mapping without validating the component in Jira.
2. Return all aliases; no Jira connection is needed.

Changes last until restart. Set `JIRA_COMPONENT_ALIASES` for persistence.

## Response

`ComponentAliasResponse` containing `aliases`, the complete alias-to-name mapping.

## Errors

Surface input type, configuration, or serialization errors. Jira validates
component names when an issue operation uses them.

## Verification Requirements

- Creation/replacement, alias resolution, and complete mapping response.
- Operation without a Jira connection.
