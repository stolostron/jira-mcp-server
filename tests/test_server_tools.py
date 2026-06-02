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

"""Tests for JiraMCPServer tool behaviors and validation."""

import os
from unittest.mock import AsyncMock

import pytest
from fastmcp import Client

from jira_mcp_server.server import JiraMCPServer, _validate_git_commit_sha

# ─── Fixtures ───────────────────────────────────────────────────────────────

FAKE_ENV = {
    "JIRA_SERVER_URL": "https://test.atlassian.net",
    "JIRA_ACCESS_TOKEN": "test-token",
    "JIRA_EMAIL": "bot@test.com",
}

FAKE_ISSUE = {
    "key": "TEST-1",
    "summary": "Fix it",
    "description": "Some description",
    "status": "New",
    "priority": "Normal",
    "issue_type": "Task",
    "project": "TEST",
    "assignee": None,
    "reporter": "bot",
    "created": "2026-01-01T00:00:00.000+0000",
    "updated": "2026-01-01T00:00:00.000+0000",
    "resolution": None,
    "labels": [],
    "components": [],
    "comments": [],
    "url": "https://test.atlassian.net/browse/TEST-1",
    "fix_versions": [],
    "target_version": [],
    "work_type": None,
    "security_level": None,
    "due_date": None,
    "target_start": None,
    "target_end": None,
    "original_estimate": None,
    "story_points": None,
    "git_commit": None,
    "git_pull_requests": None,
    "subtasks": [],
    "parent": None,
}


@pytest.fixture
def server():
    """JiraMCPServer with mocked Jira client (no real connection)."""
    with patch.dict(os.environ, FAKE_ENV):
        srv = JiraMCPServer()
        srv.client = AsyncMock()
        return srv


# pytest.importorskip-style helper so patch.dict works without re-import
from unittest.mock import patch  # noqa: E402 (after imports above)

# ─── _validate_git_commit_sha ────────────────────────────────────────────────


class TestValidateGitCommitSha:
    def test_empty_string_is_ok(self):
        _validate_git_commit_sha("")

    def test_valid_sha1(self):
        _validate_git_commit_sha("a" * 40)

    def test_valid_sha256(self):
        _validate_git_commit_sha("b" * 64)

    def test_uppercase_hex_is_valid(self):
        _validate_git_commit_sha("A" * 40)

    def test_wrong_length_raises(self):
        with pytest.raises(ValueError, match="40 characters"):
            _validate_git_commit_sha("abc123")

    def test_non_hex_characters_raise(self):
        with pytest.raises(ValueError, match="hexadecimal"):
            _validate_git_commit_sha("z" * 40)


# ─── create_issue ────────────────────────────────────────────────────────────


class TestCreateIssue:
    @pytest.mark.asyncio
    async def test_empty_summary_raises(self, server):
        async with Client(server.mcp) as client:
            with pytest.raises(Exception):
                await client.call_tool(
                    "create_issue",
                    {"project_key": "TEST", "summary": "", "description": "desc"},
                )

    @pytest.mark.asyncio
    async def test_whitespace_summary_raises(self, server):
        async with Client(server.mcp) as client:
            with pytest.raises(Exception):
                await client.call_tool(
                    "create_issue",
                    {"project_key": "TEST", "summary": "   ", "description": "desc"},
                )

    @pytest.mark.asyncio
    async def test_empty_description_raises(self, server):
        async with Client(server.mcp) as client:
            with pytest.raises(Exception):
                await client.call_tool(
                    "create_issue",
                    {
                        "project_key": "TEST",
                        "summary": "Valid summary",
                        "description": "",
                    },
                )

    @pytest.mark.asyncio
    async def test_calls_client_on_valid_input(self, server):
        server.client.create_issue = AsyncMock(return_value=FAKE_ISSUE)
        server.client.resolve_assignee = AsyncMock(return_value={"accountId": "abc"})

        async with Client(server.mcp) as client:
            await client.call_tool(
                "create_issue",
                {
                    "project_key": "TEST",
                    "summary": "Fix the bug",
                    "description": "Detailed description",
                },
            )

        server.client.create_issue.assert_called_once()

    @pytest.mark.asyncio
    async def test_invalid_git_sha_raises(self, server):
        async with Client(server.mcp) as client:
            with pytest.raises(Exception):
                await client.call_tool(
                    "create_issue",
                    {
                        "project_key": "TEST",
                        "summary": "Fix it",
                        "description": "desc",
                        "git_commit": "not-a-sha",
                    },
                )


# ─── update_issue ────────────────────────────────────────────────────────────


class TestUpdateIssue:
    @pytest.mark.asyncio
    async def test_no_fields_raises(self, server):
        async with Client(server.mcp) as client:
            with pytest.raises(Exception):
                await client.call_tool("update_issue", {"issue_key": "TEST-1"})

    @pytest.mark.asyncio
    async def test_valid_update_calls_client(self, server):
        server.client.update_issue = AsyncMock(return_value=FAKE_ISSUE)

        async with Client(server.mcp) as client:
            await client.call_tool(
                "update_issue",
                {"issue_key": "TEST-1", "summary": "Updated summary"},
            )

        server.client.update_issue.assert_called_once()
        call_kwargs = server.client.update_issue.call_args
        assert call_kwargs[0][0] == "TEST-1"


# ─── search_issues_by_team ───────────────────────────────────────────────────


class TestSearchIssuesByTeam:
    @pytest.mark.asyncio
    async def test_builds_jql_from_team_members(self, server):
        server.config.teams = {"eng": ["alice", "bob"]}
        server.client.search_issues = AsyncMock(return_value=[])

        async with Client(server.mcp) as client:
            await client.call_tool("search_issues_by_team", {"team_name": "eng"})

        jql = server.client.search_issues.call_args[0][0]
        assert 'assignee = "alice"' in jql
        assert 'assignee = "bob"' in jql

    @pytest.mark.asyncio
    async def test_adds_project_filter_when_provided(self, server):
        server.config.teams = {"eng": ["alice"]}
        server.client.search_issues = AsyncMock(return_value=[])

        async with Client(server.mcp) as client:
            await client.call_tool(
                "search_issues_by_team",
                {"team_name": "eng", "project_key": "MYPROJ"},
            )

        jql = server.client.search_issues.call_args[0][0]
        assert "project = MYPROJ" in jql

    @pytest.mark.asyncio
    async def test_adds_status_filter_when_provided(self, server):
        server.config.teams = {"eng": ["alice"]}
        server.client.search_issues = AsyncMock(return_value=[])

        async with Client(server.mcp) as client:
            await client.call_tool(
                "search_issues_by_team",
                {"team_name": "eng", "status": "In Progress"},
            )

        jql = server.client.search_issues.call_args[0][0]
        assert '"In Progress"' in jql

    @pytest.mark.asyncio
    async def test_unknown_team_raises(self, server):
        server.config.teams = {}

        async with Client(server.mcp) as client:
            with pytest.raises(Exception):
                await client.call_tool(
                    "search_issues_by_team", {"team_name": "unknown"}
                )


# ─── transition_issue ────────────────────────────────────────────────────────


class TestTransitionIssue:
    @pytest.mark.asyncio
    async def test_early_status_skips_fix_version_check(self, server):
        """Transitioning to 'In Progress' should NOT call get_issue."""
        server.client.transition_issue = AsyncMock(return_value=FAKE_ISSUE)

        async with Client(server.mcp) as client:
            await client.call_tool(
                "transition_issue",
                {"issue_key": "TEST-1", "transition": "In Progress"},
            )

        server.client.get_issue.assert_not_called()
        server.client.transition_issue.assert_called_once_with("TEST-1", "In Progress")

    @pytest.mark.asyncio
    async def test_late_status_checks_fix_version(self, server):
        """Transitioning beyond 'In Progress' should call get_issue to check fix_version."""
        server.client.get_issue = AsyncMock(return_value=FAKE_ISSUE)
        server.client.transition_issue = AsyncMock(return_value=FAKE_ISSUE)

        async with Client(server.mcp) as client:
            await client.call_tool(
                "transition_issue",
                {"issue_key": "TEST-1", "transition": "Resolved"},
            )

        server.client.get_issue.assert_called_once_with("TEST-1")


# ─── get_issue ───────────────────────────────────────────────────────────────


class TestGetIssue:
    @pytest.mark.asyncio
    async def test_returns_issue_from_client(self, server):
        server.client.get_issue = AsyncMock(return_value=FAKE_ISSUE)

        async with Client(server.mcp) as client:
            result = await client.call_tool("get_issue", {"issue_key": "TEST-1"})

        server.client.get_issue.assert_called_once_with("TEST-1")
        assert result is not None
