# Copyright 2025 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This file was developed with AI assistance.

"""Main MCP server implementation for Jira."""

import asyncio
import logging
import re
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP, Context
from pydantic import BaseModel

from .config import JiraConfig
from .client import JiraClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _validate_git_commit_sha(sha: str) -> None:
    """Validate that a git commit SHA is either 40 characters (SHA-1) or 64 characters (SHA-256).

    Args:
        sha: The git commit SHA to validate

    Raises:
        ValueError: If the SHA is not a valid length or contains invalid characters
    """
    if not sha:
        return

    # Check if it's all hexadecimal characters
    if not all(c in '0123456789abcdefABCDEF' for c in sha):
        raise ValueError(f"Git commit SHA must contain only hexadecimal characters: {sha}")

    # Check length - must be either 40 (SHA-1) or 64 (SHA-256) characters
    if len(sha) not in [40, 64]:
        raise ValueError(f"Git commit SHA must be either 40 characters (SHA-1) or 64 characters (SHA-256), got {len(sha)} characters: {sha}")


# Pydantic models for structured responses
class SubtaskResponse(BaseModel):
    key: str
    summary: str
    status: str
    issue_type: str

class ParentResponse(BaseModel):
    key: str
    summary: str
    issue_type: str

class IssueResponse(BaseModel):
    key: str
    summary: str
    description: str
    status: str
    priority: str
    issue_type: str
    project: str
    assignee: Optional[str]
    reporter: Optional[str]
    created: str
    updated: str
    resolution: Optional[str]
    labels: List[str]
    components: List[str]
    comments: List["CommentResponse"]
    url: str
    fix_versions: List[str]
    work_type: Optional[str]
    security_level: Optional[str]
    due_date: Optional[str]
    target_start: Optional[str]
    target_end: Optional[str]
    original_estimate: Optional[str]
    story_points: Optional[float]
    git_commit: Optional[str]
    git_pull_requests: Optional[str]
    subtasks: List[SubtaskResponse]
    parent: Optional[ParentResponse]

class ProjectResponse(BaseModel):
    key: str
    name: str
    description: str
    lead: str

class ComponentResponse(BaseModel):
    id: str
    name: str
    description: str
    lead: str
    assignee_type: str
    is_assignee_type_valid: bool

class CommentResponse(BaseModel):
    id: str
    body: str
    author: str
    created: str
    updated: str

class WorkLogResponse(BaseModel):
    id: str
    time_spent: str
    comment: str
    author: str
    created: str
    started: str

class LinkResponse(BaseModel):
    link_type: str
    inward_issue: str
    outward_issue: str
    inward_description: Optional[str]
    outward_description: Optional[str]
    comment: Optional[str]
    created: bool

class LinkTypeResponse(BaseModel):
    id: str
    name: str
    inward: str
    outward: str

class JiraMCPServer:
    """MCP Server for Jira integration."""
    
    def __init__(self):
        """Initialize the Jira MCP server."""
        self.mcp = FastMCP("Jira MCP Server")
        self.config = JiraConfig.from_env()
        self.client = JiraClient(self.config)
        self._setup_tools()
        self._setup_resources()
    
    def _setup_tools(self) -> None:
        """Set up MCP tools for Jira operations."""
        
        @self.mcp.tool()
        async def search_issues(
            jql: str,
            max_results: int = 100,
            ctx: Optional[Context] = None
        ) -> List[IssueResponse]:
            """Search for Jira issues using JQL (Jira Query Language).

            Args:
                jql: JQL query string (e.g., 'project = PROJ AND status = Open')
                max_results: Maximum number of results to return (default: 100)
                ctx: MCP context for progress reporting
            """
            if ctx:
                await ctx.info(f"Searching issues with JQL: {jql}")
            
            try:
                issues = await self.client.search_issues(jql, max_results)
                if ctx:
                    await ctx.info(f"Found {len(issues)} issues")
                return [IssueResponse(**issue) for issue in issues]
            except Exception as e:
                if ctx:
                    await ctx.error(f"Search failed: {str(e)}")
                raise
        
        @self.mcp.tool()
        async def get_issue(
            issue_key: str,
            ctx: Optional[Context] = None
        ) -> IssueResponse:
            """Get detailed information about a specific Jira issue.
            
            Args:
                issue_key: Jira issue key (e.g., 'PROJ-123')
                ctx: MCP context for progress reporting
            """
            if ctx:
                await ctx.info(f"Fetching issue: {issue_key}")
            
            try:
                issue = await self.client.get_issue(issue_key)
                return IssueResponse(**issue)
            except Exception as e:
                if ctx:
                    await ctx.error(f"Failed to get issue {issue_key}: {str(e)}")
                raise
        
        @self.mcp.tool()
        async def create_issue(
            project_key: str,
            summary: str,
            description: str,
            priority: str,
            work_type: str,
            due_date: str,
            components: List[str],
            issue_type: str = "Task",
            assignee: Optional[str] = None,
            labels: Optional[List[str]] = None,
            fix_versions: Optional[List[str]] = None,
            security_level: Optional[str] = "Red Hat Employee",
            target_start: Optional[str] = None,
            target_end: Optional[str] = None,
            original_estimate: Optional[str] = "1h",
            story_points: Optional[float] = 1,
            git_commit: Optional[str] = None,
            git_pull_requests: Optional[str] = None,
            parent: Optional[str] = None,
            ctx: Optional[Context] = None
        ) -> IssueResponse:
            """Create a new Jira issue.

            Args:
                project_key: Project key (e.g., 'PROJ')
                summary: Issue summary/title
                description: Issue description
                issue_type: Issue type (e.g., 'Bug', 'Task', 'Story', 'Sub-task')
                priority: Issue priority (required)
                assignee: Username of assignee
                labels: List of labels to add
                fix_versions: List of fix version names
                work_type: Work type for the issue (required). Available options:
                    - **None** = -1
                    - **Associate Wellness & Development** = 46650
                    - **Future Sustainability** = 48051
                    - **Incident & Support** = 46651
                    - **Quality / Stability / Reliability** = 46653
                    - **Security & Compliance** = 46652
                    - **Product / Portfolio Work** = 46654
                security_level: Security level name
                due_date: Due date in YYYY-MM-DD format (required)
                target_start: Target start date in YYYY-MM-DD format
                target_end: Target end date in YYYY-MM-DD format
                components: List of component names (required)
                original_estimate: Original time estimate (e.g., '1h 30m')
                story_points: Story points value
                git_commit: Git commit hash or reference
                git_pull_requests: Git pull requests, comma separated list of pull requests URLs
                parent: Parent issue key for sub-tasks (e.g., 'PROJ-123')
                ctx: MCP context for progress reporting
            """
            # Validate required fields
            if not summary or not summary.strip():
                raise ValueError("Summary cannot be empty")
            if not description or not description.strip():
                raise ValueError("Description cannot be empty")
            if not priority or not priority.strip():
                raise ValueError("Priority cannot be empty")
            if not work_type or not str(work_type).strip():
                raise ValueError("Work type cannot be empty")
            if not due_date or not due_date.strip():
                raise ValueError("Due date cannot be empty")
            if not components or len(components) == 0:
                raise ValueError("Components cannot be empty")

            # Validate optional fields if provided
            if assignee is not None and (not assignee or not assignee.strip()):
                raise ValueError("Assignee cannot be empty")
            if fix_versions is not None and (not fix_versions or len(fix_versions) == 0):
                raise ValueError("Fix versions cannot be empty")

            if ctx:
                await ctx.info(f"Creating issue in project {project_key}")
            
            fields = {}
            if priority:
                fields['priority'] = {'name': priority}
            if assignee:
                fields['assignee'] = {'name': assignee}
            if labels:
                # Labels are passed as array of strings directly to Jira API
                fields['labels'] = labels
            if fix_versions:
                # Fix versions need to be converted to objects with 'name' property
                fields['fixVersions'] = [{'name': version} for version in fix_versions]
            if work_type:
                fields['customfield_12320040'] = {'id': str(work_type)}  # Work type custom field
            if security_level:
                fields['security'] = {'name': security_level}
            if due_date:
                fields['duedate'] = due_date
            if target_start:
                fields['customfield_12313941'] = target_start  # Target Start custom field
            if target_end:
                fields['customfield_12313942'] = target_end  # Target End custom field
            if components:
                # Components need to be converted to objects with 'name' property
                fields['components'] = [{'name': component} for component in components]
            if original_estimate:
                fields['timetracking'] = {'originalEstimate': original_estimate}
            if story_points:
                fields['customfield_12310243'] = story_points  # Story points custom field
            if git_commit:
                _validate_git_commit_sha(git_commit)
                fields['customfield_12317372'] = git_commit  # Git Commit custom field
            if git_pull_requests:
                fields['customfield_12310220'] = git_pull_requests  # Git Pull Requests custom field
            if parent:
                fields['parent'] = {'key': parent}  # Parent issue for sub-tasks
            
            try:
                issue = await self.client.create_issue(
                    project_key, summary, description, issue_type, **fields
                )
                if ctx:
                    await ctx.info(f"Created issue: {issue['key']}")
                return IssueResponse(**issue)
            except Exception as e:
                if ctx:
                    await ctx.error(f"Failed to create issue: {str(e)}")
                raise
        
        @self.mcp.tool()
        async def update_issue(
            issue_key: str,
            priority: str,
            work_type: str,
            due_date: str,
            components: List[str],
            summary: Optional[str] = None,
            description: Optional[str] = None,
            assignee: Optional[str] = None,
            labels: Optional[List[str]] = None,
            fix_versions: Optional[List[str]] = None,
            security_level: Optional[str] = None,
            target_start: Optional[str] = None,
            target_end: Optional[str] = None,
            original_estimate: Optional[str] = None,
            story_points: Optional[float] = None,
            git_commit: Optional[str] = None,
            git_pull_requests: Optional[str] = None,
            ctx: Optional[Context] = None
        ) -> IssueResponse:
            """Update an existing Jira issue.
            
            Args:
                issue_key: Jira issue key (e.g., 'PROJ-123')
                summary: New summary/title
                description: New description
                priority: New priority (required)
                assignee: New assignee username
                labels: New labels list
                fix_versions: List of fix version names
                work_type: Work type for the issue (required). Available options:
                    - **None** = -1
                    - **Associate Wellness & Development** = 46650
                    - **Future Sustainability** = 48051
                    - **Incident & Support** = 46651
                    - **Quality / Stability / Reliability** = 46653
                    - **Security & Compliance** = 46652
                    - **Product / Portfolio Work** = 46654
                security_level: Security level name
                due_date: Due date in YYYY-MM-DD format (required)
                target_start: Target start date in YYYY-MM-DD format
                target_end: Target end date in YYYY-MM-DD format
                components: List of component names (required)
                original_estimate: Original time estimate (e.g., '1h 30m')
                story_points: Story points value
                git_commit: Git commit hash or reference
                git_pull_requests: Git pull requests, comma separated list of pull requests URLs
                ctx: MCP context for progress reporting
            """
            if ctx:
                await ctx.info(f"Updating issue: {issue_key}")
            
            fields = {}
            if summary:
                fields['summary'] = summary
            if description:
                fields['description'] = description
            if priority:
                fields['priority'] = {'name': priority}
            if assignee:
                fields['assignee'] = {'name': assignee}
            if labels:
                # Labels are passed as array of strings directly to Jira API
                fields['labels'] = labels
            if fix_versions:
                # Fix versions need to be converted to objects with 'name' property
                fields['fixVersions'] = [{'name': version} for version in fix_versions]
            if work_type:
                fields['customfield_12320040'] = {'id': str(work_type)}  # Work type custom field
            if security_level:
                fields['security'] = {'name': security_level}
            if due_date:
                fields['duedate'] = due_date
            if target_start:
                fields['customfield_12313941'] = target_start  # Target Start custom field
            if target_end:
                fields['customfield_12313942'] = target_end  # Target End custom field
            if components:
                # Components need to be converted to objects with 'name' property
                fields['components'] = [{'name': component} for component in components]
            if original_estimate:
                fields['timetracking'] = {'originalEstimate': original_estimate}
            if story_points:
                fields['customfield_12310243'] = story_points  # Story points custom field
            if git_commit:
                _validate_git_commit_sha(git_commit)
                fields['customfield_12317372'] = git_commit  # Git Commit custom field
            if git_pull_requests:
                fields['customfield_12310220'] = git_pull_requests  # Git Pull Requests custom field

            try:
                issue = await self.client.update_issue(issue_key, **fields)
                if ctx:
                    await ctx.info(f"Updated issue: {issue_key}")
                return IssueResponse(**issue)
            except Exception as e:
                if ctx:
                    await ctx.error(f"Failed to update issue {issue_key}: {str(e)}")
                raise
        
        @self.mcp.tool()
        async def transition_issue(
            issue_key: str,
            transition: str,
            ctx: Optional[Context] = None
        ) -> IssueResponse:
            """Transition a Jira issue to a new status.
            
            Args:
                issue_key: Jira issue key (e.g., 'PROJ-123')
                transition: Transition name (e.g., 'Done', 'In Progress')
                ctx: MCP context for progress reporting
            """
            if ctx:
                await ctx.info(f"Transitioning issue {issue_key} to {transition}")
            
            try:
                issue = await self.client.transition_issue(issue_key, transition)
                if ctx:
                    await ctx.info(f"Transitioned issue {issue_key} to {transition}")
                return IssueResponse(**issue)
            except Exception as e:
                if ctx:
                    await ctx.error(f"Failed to transition issue {issue_key}: {str(e)}")
                raise
        
        @self.mcp.tool()
        async def add_comment(
            issue_key: str,
            comment: str,
            security_level: Optional[str] = "Red Hat Employee",
            ctx: Optional[Context] = None
        ) -> CommentResponse:
            """Add a comment to a Jira issue.

            Args:
                issue_key: Jira issue key (e.g., 'PROJ-123')
                comment: Comment text
                security_level: Security level name (default: "Red Hat Employee")
                ctx: MCP context for progress reporting
            """
            if ctx:
                await ctx.info(f"Adding comment to issue: {issue_key}")
            
            try:
                comment_data = await self.client.add_comment(issue_key, comment, security_level)
                if ctx:
                    await ctx.info(f"Added comment to issue: {issue_key}")
                return CommentResponse(**comment_data)
            except Exception as e:
                if ctx:
                    await ctx.error(f"Failed to add comment to {issue_key}: {str(e)}")
                raise
        
        @self.mcp.tool()
        async def log_time(
            issue_key: str,
            time_spent: str,
            comment: str,
            started: Optional[str] = None,
            ctx: Optional[Context] = None
        ) -> WorkLogResponse:
            """Log time spent on a Jira issue with an optional comment.
            
            Args:
                issue_key: Jira issue key (e.g., 'PROJ-123')
                time_spent: Time spent in Jira format (e.g., '1h 30m', '2d 4h', '45m')
                comment: Comment describing the work done
                started: Start date/time in ISO format (optional, defaults to now)
                ctx: MCP context for progress reporting
            """
            if ctx:
                await ctx.info(f"Logging {time_spent} on issue: {issue_key}")
            
            
            try:
                work_log = await self.client.log_work(issue_key, time_spent, comment, started)
                if ctx:
                    await ctx.info(f"Successfully logged time on issue: {issue_key}")
                return WorkLogResponse(**work_log)
            except Exception as e:
                if ctx:
                    await ctx.error(f"Failed to log time on {issue_key}: {str(e)}")
                raise

        @self.mcp.tool()
        async def get_projects(
            ctx: Optional[Context] = None
        ) -> List[ProjectResponse]:
            """Get all Jira projects accessible to the user.

            Args:
                ctx: MCP context for progress reporting
            """
            if ctx:
                await ctx.info("Fetching all projects")

            try:
                projects = await self.client.get_projects()
                if ctx:
                    await ctx.info(f"Found {len(projects)} projects")
                return [ProjectResponse(**project) for project in projects]
            except Exception as e:
                if ctx:
                    await ctx.error(f"Failed to get projects: {str(e)}")
                raise

        @self.mcp.tool()
        async def get_project_components(
            project_key: str,
            ctx: Optional[Context] = None
        ) -> List[ComponentResponse]:
            """Get all components available in a specific Jira project.

            Args:
                project_key: Project key (e.g., 'ACM', 'PROJ')
                ctx: MCP context for progress reporting
            """
            if ctx:
                await ctx.info(f"Fetching components for project: {project_key}")

            try:
                components = await self.client.get_project_components(project_key)
                if ctx:
                    await ctx.info(f"Found {len(components)} components in project {project_key}")
                return [ComponentResponse(**component) for component in components]
            except Exception as e:
                if ctx:
                    await ctx.error(f"Failed to get components for project {project_key}: {str(e)}")
                raise

        @self.mcp.tool()
        async def link_issue(
            link_type: str,
            inward_issue: str,
            outward_issue: str,
            comment: Optional[str] = None,
            security_level: Optional[str] = None,
            ctx: Optional[Context] = None
        ) -> LinkResponse:
            """Create a link between two Jira issues.
            
            Args:
                link_type: The type of link to create (e.g., 'Blocks', 'Relates', 'Duplicates')
                inward_issue: The issue key to link from (e.g., 'PROJ-123')
                outward_issue: The issue key to link to (e.g., 'PROJ-456')
                comment: Optional comment to add when creating the link
                security_level: Optional security level for the comment (default: None)
                ctx: MCP context for progress reporting
            """
            if ctx:
                await ctx.info(f"Creating link: {inward_issue} {link_type} {outward_issue}")
            
            try:
                link_data = await self.client.create_issue_link(
                    link_type, inward_issue, outward_issue, comment, security_level
                )
                if ctx:
                    await ctx.info(f"Successfully created link between {inward_issue} and {outward_issue}")
                return LinkResponse(**link_data)
            except Exception as e:
                if ctx:
                    await ctx.error(f"Failed to create link: {str(e)}")
                raise

        @self.mcp.tool()
        async def get_link_types(
            ctx: Optional[Context] = None
        ) -> List[LinkTypeResponse]:
            """Get all available issue link types.
            
            Args:
                ctx: MCP context for progress reporting
            """
            if ctx:
                await ctx.info("Fetching available link types")
            
            try:
                link_types = await self.client.get_issue_link_types()
                if ctx:
                    await ctx.info(f"Found {len(link_types)} link types")
                return [LinkTypeResponse(**link_type) for link_type in link_types]
            except Exception as e:
                if ctx:
                    await ctx.error(f"Failed to get link types: {str(e)}")
                raise

        @self.mcp.tool()
        async def debug_issue_fields(
            issue_key: str,
            ctx: Optional[Context] = None
        ) -> Dict[str, Any]:
            """Debug function to show all raw Jira fields for an issue.
            
            Args:
                issue_key: Jira issue key (e.g., 'PROJ-123')
                ctx: MCP context for progress reporting
            """
            if ctx:
                await ctx.info(f"Debugging raw fields for issue: {issue_key}")
            
            try:
                raw_issue = await self.client.get_raw_issue_fields(issue_key)
                if ctx:
                    await ctx.info(f"Retrieved raw fields for issue: {issue_key}")
                return raw_issue
            except Exception as e:
                if ctx:
                    await ctx.error(f"Failed to get raw fields for {issue_key}: {str(e)}")
                raise
    
    def _setup_resources(self) -> None:
        """Set up MCP resources for Jira data."""
        
        @self.mcp.resource("jira://issue/{issue_key}")
        async def get_issue_resource(issue_key: str) -> str:
            """Get issue details as a formatted resource.
            
            Args:
                issue_key: Jira issue key (e.g., 'PROJ-123')
            """
            try:
                issue = await self.client.get_issue(issue_key)
                return f"""# {issue['key']}: {issue['summary']}

**Status:** {issue['status']}
**Priority:** {issue['priority']}
**Type:** {issue['issue_type']}
**Project:** {issue['project']}
**Assignee:** {issue['assignee'] or 'Unassigned'}
**Reporter:** {issue['reporter']}

## Description
{issue['description']}

## Details
- **Created:** {issue['created']}
- **Updated:** {issue['updated']}
- **Resolution:** {issue['resolution'] or 'Unresolved'}
- **Labels:** {', '.join(issue['labels']) if issue['labels'] else 'None'}
- **Components:** {', '.join(issue['components']) if issue['components'] else 'None'}
- **Fix Versions:** {', '.join(issue['fix_versions']) if issue['fix_versions'] else 'None'}
- **Work Type:** {issue['work_type'] or 'None'}
- **Security Level:** {issue['security_level'] or 'None'}
- **Due Date:** {issue['due_date'] or 'None'}
- **Target Start:** {issue['target_start'] or 'None'}
- **Target End:** {issue['target_end'] or 'None'}
- **Original Estimate:** {issue['original_estimate'] or 'None'}
- **Story Points:** {issue['story_points'] or 'None'}
- **Git Commit:** {issue['git_commit'] or 'None'}
- **Git Pull Requests:** {issue['git_pull_requests'] or 'None'}

**URL:** {issue['url']}
"""
            except Exception as e:
                return f"Error fetching issue {issue_key}: {str(e)}"
        
        @self.mcp.resource("jira://projects")
        async def get_projects_resource() -> str:
            """Get all projects as a formatted resource."""
            try:
                projects = await self.client.get_projects()
                result = "# Jira Projects\n\n"
                for project in projects:
                    result += f"## {project['key']}: {project['name']}\n"
                    if project['description']:
                        result += f"{project['description']}\n"
                    result += f"**Lead:** {project['lead']}\n\n"
                return result
            except Exception as e:
                return f"Error fetching projects: {str(e)}"
    
    async def start(self) -> None:
        """Start the MCP server."""
        try:
            self.config.validate_required_fields()
            await self.client.connect()
            logger.info("Connected to Jira successfully")
            logger.info(f"Server URL: {self.config.server_url}")
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            raise
    
    def create_sse_app(self, host: str = "127.0.0.1", port: int = 8000):
        """Create SSE HTTP app for the MCP server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
            
        Returns:
            ASGI application configured for SSE transport
        """
        return self.mcp.http_app(transport="sse")
    
    def run_sse_server(self, host: str = "127.0.0.1", port: int = 8000):
        """Run the MCP server with SSE transport.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        import uvicorn
        app = self.create_sse_app(host, port)
        logger.info(f"Starting SSE server on {host}:{port}")
        logger.info(f"SSE endpoint: http://{host}:{port}/sse")
        logger.info(f"Message endpoint: http://{host}:{port}/messages/")
        uvicorn.run(app, host=host, port=port)
    
