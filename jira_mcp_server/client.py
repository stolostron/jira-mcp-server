"""Jira client wrapper for MCP server."""

import asyncio
from typing import List, Dict, Any, Optional
from jira import JIRA
from jira.exceptions import JIRAError
from asyncio_throttle import Throttler

from .config import JiraConfig


class JiraClient:
    """Async wrapper for Jira client with rate limiting."""
    
    def __init__(self, config: JiraConfig):
        """Initialize Jira client with configuration."""
        self.config = config
        self._jira: Optional[JIRA] = None
        self.throttler = Throttler(rate_limit=10, period=1.0)  # 10 requests per second
    
    async def connect(self) -> None:
        """Connect to Jira server using personal access token authentication."""
        try:
            self._jira = JIRA(
                server=self.config.server_url,
                token_auth=self.config.access_token,
                options={
                    'verify': self.config.verify_ssl,
                    'timeout': self.config.timeout
                }
            )
            # Test connection
            await self._async_call(lambda: self._jira.myself())
        except JIRAError as e:
            raise ConnectionError(f"Failed to connect to Jira: {e}")
    
    async def _async_call(self, func):
        """Execute synchronous Jira calls asynchronously with throttling."""
        async with self.throttler:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, func)
    
    async def search_issues(self, jql: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search for issues using JQL."""
        if not self._jira:
            raise RuntimeError("Not connected to Jira")
        
        max_results = max_results or self.config.max_results
        
        try:
            issues = await self._async_call(
                lambda: self._jira.search_issues(
                    jql,
                    maxResults=max_results,
                    expand='changelog'
                )
            )
            
            return [self._issue_to_dict(issue) for issue in issues]
        except JIRAError as e:
            raise ValueError(f"JQL search failed: {e}")
    
    async def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """Get a specific issue by key."""
        if not self._jira:
            raise RuntimeError("Not connected to Jira")
        
        try:
            issue = await self._async_call(
                lambda: self._jira.issue(
                    issue_key,
                    expand='changelog,transitions,comments'
                )
            )
            return self._issue_to_dict(issue)
        except JIRAError as e:
            raise ValueError(f"Failed to get issue {issue_key}: {e}")
    
    async def create_issue(self, project_key: str, summary: str, description: str, 
                          issue_type: str = "Task", **fields) -> Dict[str, Any]:
        """Create a new issue."""
        if not self._jira:
            raise RuntimeError("Not connected to Jira")
        
        issue_dict = {
            'project': {'key': project_key},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issue_type},
            **fields
        }
        
        try:
            issue = await self._async_call(
                lambda: self._jira.create_issue(fields=issue_dict)
            )
            return self._issue_to_dict(issue)
        except JIRAError as e:
            raise ValueError(f"Failed to create issue: {e}")
    
    async def update_issue(self, issue_key: str, **fields) -> Dict[str, Any]:
        """Update an existing issue."""
        if not self._jira:
            raise RuntimeError("Not connected to Jira")
        
        try:
            issue = await self._async_call(lambda: self._jira.issue(issue_key))
            await self._async_call(lambda: issue.update(fields=fields))
            # Return updated issue
            return await self.get_issue(issue_key)
        except JIRAError as e:
            raise ValueError(f"Failed to update issue {issue_key}: {e}")
    
    async def transition_issue(self, issue_key: str, transition: str) -> Dict[str, Any]:
        """Transition an issue to a new status."""
        if not self._jira:
            raise RuntimeError("Not connected to Jira")
        
        try:
            issue = await self._async_call(lambda: self._jira.issue(issue_key))
            transitions = await self._async_call(lambda: self._jira.transitions(issue))
            
            # Find transition by name
            transition_id = None
            for t in transitions:
                if t['name'].lower() == transition.lower():
                    transition_id = t['id']
                    break
            
            if not transition_id:
                available = [t['name'] for t in transitions]
                raise ValueError(f"Transition '{transition}' not available. Available: {available}")
            
            await self._async_call(
                lambda: self._jira.transition_issue(issue, transition_id)
            )
            
            return await self.get_issue(issue_key)
        except JIRAError as e:
            raise ValueError(f"Failed to transition issue {issue_key}: {e}")
    
    async def add_comment(self, issue_key: str, comment: str) -> Dict[str, Any]:
        """Add a comment to an issue."""
        if not self._jira:
            raise RuntimeError("Not connected to Jira")
        
        try:
            issue = await self._async_call(lambda: self._jira.issue(issue_key))
            comment_obj = await self._async_call(
                lambda: self._jira.add_comment(issue, comment)
            )
            
            return {
                'id': comment_obj.id,
                'body': comment_obj.body,
                'author': comment_obj.author.displayName,
                'created': comment_obj.created,
                'updated': comment_obj.updated
            }
        except JIRAError as e:
            raise ValueError(f"Failed to add comment to {issue_key}: {e}")
    
    async def log_work(self, issue_key: str, time_spent: str, comment: str, started: Optional[str] = None) -> Dict[str, Any]:
        """Log work time on an issue with a comment."""
        if not self._jira:
            raise RuntimeError("Not connected to Jira")
        
        try:
            issue = await self._async_call(lambda: self._jira.issue(issue_key))
            
            # Prepare work log parameters
            work_log_params = {
                'timeSpent': time_spent,
                'comment': comment
            }
            
            # Add started time if provided
            if started:
                work_log_params['started'] = started
            
            # Log the work using direct parameters instead of a dictionary
            work_log_obj = await self._async_call(
                lambda: self._jira.add_worklog(issue, **work_log_params)
            )
            
            return {
                'id': work_log_obj.id,
                'time_spent': work_log_obj.timeSpent,
                'comment': work_log_obj.comment,
                'author': work_log_obj.author.displayName,
                'created': work_log_obj.created,
                'started': work_log_obj.started
            }
        except JIRAError as e:
            raise ValueError(f"Failed to log work on {issue_key}: {e}")
    
    async def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects."""
        if not self._jira:
            raise RuntimeError("Not connected to Jira")
        
        try:
            projects = await self._async_call(lambda: self._jira.projects())
            return [
                {
                    'key': project.key,
                    'name': project.name,
                    'description': getattr(project, 'description', ''),
                    'lead': getattr(project.lead, 'displayName', '') if hasattr(project, 'lead') else ''
                }
                for project in projects
            ]
        except JIRAError as e:
            raise ValueError(f"Failed to get projects: {e}")
    
    def _extract_custom_field_value(self, field_value):
        """Extract string value from custom field that might be a CustomFieldOption object."""
        if field_value is None:
            return None
        
        # Debug: log the type for troubleshooting
        field_type = type(field_value).__name__
        
        # Handle CustomFieldOption objects from Jira library
        if hasattr(field_value, 'value'):
            return str(field_value.value)
        # Handle dict-like objects that might have a 'value' key
        if isinstance(field_value, dict) and 'value' in field_value:
            return str(field_value['value'])
        # Handle string values directly
        if isinstance(field_value, str):
            return field_value
        # Handle objects with name attribute (common in Jira)
        if hasattr(field_value, 'name'):
            return str(field_value.name)
        
        # For CustomFieldOption specifically, try to access its string representation or properties
        if 'CustomFieldOption' in field_type:
            # Try various common attributes
            for attr in ['value', 'name', 'displayName', 'id']:
                if hasattr(field_value, attr):
                    val = getattr(field_value, attr)
                    if val is not None:
                        return str(val)
        
        # Fallback to string conversion
        return str(field_value)
    
    def _seconds_to_time_string(self, seconds: int) -> str:
        """Convert seconds to Jira time format (e.g., '1h 30m')."""
        if seconds is None:
            return None
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        if hours > 0 and minutes > 0:
            return f"{hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h"
        elif minutes > 0:
            return f"{minutes}m"
        else:
            return "0m"
    
    def _issue_to_dict(self, issue) -> Dict[str, Any]:
        """Convert Jira issue object to dictionary."""
        return {
            'key': issue.key,
            'summary': issue.fields.summary,
            'description': getattr(issue.fields, 'description', ''),
            'status': issue.fields.status.name,
            'priority': getattr(issue.fields.priority, 'name', '') if issue.fields.priority else '',
            'issue_type': issue.fields.issuetype.name,
            'project': issue.fields.project.key,
            'assignee': issue.fields.assignee.displayName if issue.fields.assignee else None,
            'reporter': issue.fields.reporter.displayName if issue.fields.reporter else None,
            'created': issue.fields.created,
            'updated': issue.fields.updated,
            'resolution': issue.fields.resolution.name if issue.fields.resolution else None,
            'labels': getattr(issue.fields, 'labels', []),
            'components': [comp.name for comp in getattr(issue.fields, 'components', [])],
            'comments': [
                {
                    'id': comment.id,
                    'body': comment.body,
                    'author': comment.author.displayName,
                    'created': comment.created,
                    'updated': comment.updated
                }
                for comment in getattr(getattr(issue.fields, 'comment', None), 'comments', []) or []
            ],
            'url': f"{self.config.server_url}/browse/{issue.key}",
            'fix_versions': [version.name for version in getattr(issue.fields, 'fixVersions', [])],
            'work_type': self._extract_custom_field_value(getattr(issue.fields, 'customfield_12320040', None)),  # Work type custom field
            'security_level': getattr(issue.fields.security, 'name', None) if getattr(issue.fields, 'security', None) else None,
            'due_date': getattr(issue.fields, 'duedate', None),
            'target_start': getattr(issue.fields, 'customfield_12313941', None),  # Target Start custom field
            'target_end': getattr(issue.fields, 'customfield_12313942', None),  # Target End custom field
            'original_estimate': self._seconds_to_time_string(getattr(issue.fields, 'timeoriginalestimate', None)),
            'story_points': getattr(issue.fields, 'customfield_12310243', None),  # Story points custom field
            'git_commit': getattr(issue.fields, 'customfield_12317372', None),  # Git Commit custom field
            'git_pull_requests': getattr(issue.fields, 'customfield_12310220', None)  # Git Pull Requests custom field
        }