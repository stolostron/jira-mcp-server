# Tool Specification: `list_component_aliases`

## Purpose

List configured shortcuts for Jira component names.

## Contract

```python
list_component_aliases() -> ComponentAliasResponse
```

No caller parameters.

## Execution

1. Read the current in-memory aliases; no Jira connection is needed.
2. Return the alias-to-component-name mapping.

Initial aliases come from `JIRA_COMPONENT_ALIASES`; runtime changes are not persisted.

## Response

```json
{"aliases": {"ui": "User Interface"}}
```

Typed as `ComponentAliasResponse`; `aliases` may be empty.

## Errors

Surface configuration or response serialization errors.

## Verification Requirements

- Empty/populated mappings and runtime configuration changes.
- Typed serialization without a Jira connection.
