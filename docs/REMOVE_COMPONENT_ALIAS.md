# Tool Specification: `remove_component_alias`

## Purpose

Remove a runtime component shortcut without changing Jira components.

## Contract

```python
remove_component_alias(alias: str) -> ComponentAliasResponse
```

| Parameter | Required | Behavior |
|---|---|---|
| `alias` | Yes | Existing shortcut key to remove. |

## Execution

1. Reject unknown aliases and remove the selected entry.
2. Return remaining aliases; no Jira connection is needed.

Removal is runtime-only; restart reloads `JIRA_COMPONENT_ALIASES`.

## Response

`ComponentAliasResponse` containing `aliases`, the remaining alias-to-name mapping.

## Errors

Reject unknown aliases with `ValueError`; surface configuration/serialization errors.

## Verification Requirements

- Existing/unknown aliases and remaining mapping response.
- Operation without Jira component changes or a Jira connection.
