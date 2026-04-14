# Work Plan - 2026-04-14

## Summary

Added `get_project_versions` MCP tool to the Jira MCP server and created a Spike issue for Agentic SDLC work.

## Completed

### 1. Created Jira Spike - ACM-32882
- **Summary:** Build an Agentic SDLC services for executing Agent instructions: Ambient & KubeOpenCode
- **Type:** Spike
- **Assignee:** Joshua Packer
- **Work Type:** Future Sustainability
- **Component:** ACM AI
- **Story Points:** 3
- **Target Dates:** Q2 2026 (2026-04-01 to 2026-06-30)
- **Watcher:** Joydeep Banerjee

### 2. Added `get_project_versions` MCP Tool
- **Problem:** No way to query valid version names when setting `fix_versions` or `target_version` on issues. Setting an invalid version name (e.g., "OCP 5") resulted in a 400 error with no way to discover valid options.
- **Solution:** Added a new `get_project_versions` tool following the existing `get_project_components` pattern.
- **Files changed:**
  - `jira_mcp_server/client.py` - Added `get_project_versions()` method calling `self._jira.project_versions(project_key)`
  - `jira_mcp_server/server.py` - Added `VersionResponse` Pydantic model and `get_project_versions` MCP tool registration
- **Fields returned:** id, name, description, released, archived, release_date

## Implementation Details

### `get_project_versions` Tool

#### client.py - `get_project_versions()` method (line 258)

```python
async def get_project_versions(self, project_key: str) -> List[Dict[str, Any]]:
    """Get all versions for a specific project."""
    if not self._jira:
        raise RuntimeError("Not connected to Jira")

    try:
        versions = await self._async_call(
            lambda: self._jira.project_versions(project_key)
        )
        return [
            {
                'id': version.id,
                'name': version.name,
                'description': getattr(version, 'description', '') or '',
                'released': getattr(version, 'released', False),
                'archived': getattr(version, 'archived', False),
                'release_date': getattr(version, 'releaseDate', None),
            }
            for version in versions
        ]
    except JIRAError as e:
        raise ValueError(f"Failed to get versions for project {project_key}: {e}")
```

#### server.py - `VersionResponse` model (line 111)

```python
class VersionResponse(BaseModel):
    id: str
    name: str
    description: str
    released: bool
    archived: bool
    release_date: Optional[str]
```

#### server.py - Tool registration (line 768)

```python
@self.mcp.tool()
async def get_project_versions(
    project_key: str,
    ctx: Optional[Context] = None
) -> List[VersionResponse]:
    """Get all versions available in a specific Jira project.

    Useful for finding valid version names when setting fix_versions
    or target_version on issues.

    Args:
        project_key: Project key (e.g., 'ACM', 'PROJ')
        ctx: MCP context for progress reporting
    """
    if ctx:
        await ctx.info(f"Fetching versions for project: {project_key}")

    try:
        versions = await self.client.get_project_versions(project_key)
        if ctx:
            await ctx.info(f"Found {len(versions)} versions in project {project_key}")
        return [VersionResponse(**version) for version in versions]
    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to get versions for project {project_key}: {str(e)}")
        raise
```

#### Design decisions
- Follows the identical pattern as `get_project_components` for consistency
- Uses `self._jira.project_versions()` from the jira Python library
- Uses `getattr` with defaults for optional fields to avoid AttributeError
- Returns all versions (released, unreleased, archived) so the caller can filter as needed

## Notes
- The ACM project has no "Q2" or "OCP 5" version. Closest Q2 2026 versions are ACM 2.16.0 (no date) and ACM 2.17.0 (2026-06-03).
- Target version was cleared per user request after discovering no matching version exists.
