"""Main MCP server implementation for Jira."""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP, Context
from pydantic import BaseModel

from .config import JiraConfig
from .client import JiraClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for structured responses
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

class ProjectResponse(BaseModel):
    key: str
    name: str
    description: str
    lead: str

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
            max_results: Optional[int] = None,
            ctx: Optional[Context] = None
        ) -> List[IssueResponse]:
            """Search for Jira issues using JQL (Jira Query Language).
            
            Args:
                jql: JQL query string (e.g., 'project = PROJ AND status = Open')
                max_results: Maximum number of results to return
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
            issue_type: str = "Task",
            priority: Optional[str] = None,
            assignee: Optional[str] = None,
            labels: Optional[List[str]] = None,
            ctx: Optional[Context] = None
        ) -> IssueResponse:
            """Create a new Jira issue.
            
            Args:
                project_key: Project key (e.g., 'PROJ')
                summary: Issue summary/title
                description: Issue description
                issue_type: Issue type (e.g., 'Bug', 'Task', 'Story')
                priority: Issue priority
                assignee: Username of assignee
                labels: List of labels to add
                ctx: MCP context for progress reporting
            """
            if ctx:
                await ctx.info(f"Creating issue in project {project_key}")
            
            fields = {}
            if priority:
                fields['priority'] = {'name': priority}
            if assignee:
                fields['assignee'] = {'name': assignee}
            if labels:
                fields['labels'] = [{'add': label} for label in labels]
            
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
            summary: Optional[str] = None,
            description: Optional[str] = None,
            priority: Optional[str] = None,
            assignee: Optional[str] = None,
            labels: Optional[List[str]] = None,
            ctx: Optional[Context] = None
        ) -> IssueResponse:
            """Update an existing Jira issue.
            
            Args:
                issue_key: Jira issue key (e.g., 'PROJ-123')
                summary: New summary/title
                description: New description
                priority: New priority
                assignee: New assignee username
                labels: New labels list
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
                fields['labels'] = [{'set': [{'add': label} for label in labels]}]
            
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
            ctx: Optional[Context] = None
        ) -> CommentResponse:
            """Add a comment to a Jira issue.
            
            Args:
                issue_key: Jira issue key (e.g., 'PROJ-123')
                comment: Comment text
                ctx: MCP context for progress reporting
            """
            if ctx:
                await ctx.info(f"Adding comment to issue: {issue_key}")
            
            try:
                comment_data = await self.client.add_comment(issue_key, comment)
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
    
