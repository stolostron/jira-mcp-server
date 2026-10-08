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

"""Regression tests for editing and deleting Jira issue comments."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from jira.exceptions import JIRAError

from jira_mcp_server.client import JiraClient
from jira_mcp_server.config import JiraConfig


def make_comment(visibility=None):
    comment = SimpleNamespace(
        id="10001",
        body="Original text",
        author=SimpleNamespace(displayName="Test User"),
        created="2026-01-01T00:00:00.000+0000",
        updated="2026-01-01T00:00:00.000+0000",
        visibility=visibility,
    )

    def update(**kwargs):
        comment.body = kwargs["body"]
        if "visibility" in kwargs:
            comment.visibility = kwargs["visibility"]

    comment.update = Mock(side_effect=update)
    comment.delete = Mock(return_value=SimpleNamespace(status_code=204, text=""))
    return comment


@pytest.fixture
def jira_client():
    client = JiraClient(
        JiraConfig(server_url="https://jira.example", access_token="token")
    )
    client._jira = Mock()
    client._async_call = AsyncMock(side_effect=lambda operation: operation())
    return client


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("visibility", "secure_comment", "expected_visibility"),
    [
        (None, False, None),
        (None, True, {"type": "group", "value": "Red Hat Employee"}),
        ({"type": "group", "value": "Engineering"}, False, None),
        ({"type": "role", "value": "Administrators"}, True, None),
    ],
)
async def test_edit_comment_visibility_rules(
    jira_client, visibility, secure_comment, expected_visibility
):
    comment_obj = make_comment(visibility)
    jira_client._jira.comment.return_value = comment_obj

    result = await jira_client.edit_comment(
        "TEST-1", "10001", "  replacement text  ", secure_comment
    )

    jira_client._jira.comment.assert_called_once_with("TEST-1", "10001")
    update_kwargs = comment_obj.update.call_args.kwargs
    assert update_kwargs["body"] == "  replacement text  "
    if expected_visibility is None:
        assert "visibility" not in update_kwargs
    else:
        assert update_kwargs["visibility"] == expected_visibility
    assert result == {
        "id": "10001",
        "body": "  replacement text  ",
        "author": "Test User",
        "created": "2026-01-01T00:00:00.000+0000",
        "updated": "2026-01-01T00:00:00.000+0000",
    }
    assert jira_client._async_call.await_count == 2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("issue_key", "comment_id", "body"),
    [("  ", "10001", "text"), ("TEST-1", "\t", "text"), ("TEST-1", "1", " \n")],
)
async def test_edit_comment_rejects_blank_values(jira_client, issue_key, comment_id, body):
    with pytest.raises(ValueError, match="must not be blank"):
        await jira_client.edit_comment(issue_key, comment_id, body)
    jira_client._jira.comment.assert_not_called()


@pytest.mark.asyncio
async def test_comment_operations_require_connection():
    client = JiraClient(
        JiraConfig(server_url="https://jira.example", access_token="token")
    )
    with pytest.raises(RuntimeError, match="Not connected"):
        await client.edit_comment("TEST-1", "10001", "Updated")
    with pytest.raises(RuntimeError, match="Not connected"):
        await client.delete_comment("TEST-1", "10001")


@pytest.mark.asyncio
async def test_wrong_issue_or_inaccessible_comment_error_is_surfaced(jira_client):
    jira_client._jira.comment.side_effect = JIRAError("Comment not found", status_code=404)

    with pytest.raises(ValueError, match="Failed to edit comment 10001 on TEST-1"):
        await jira_client.edit_comment("TEST-1", "10001", "Updated")

    jira_client._jira.comment.assert_called_once_with("TEST-1", "10001")


@pytest.mark.asyncio
async def test_edit_permission_error_is_surfaced(jira_client):
    comment_obj = make_comment()
    comment_obj.update.side_effect = JIRAError("Forbidden", status_code=403)
    jira_client._jira.comment.return_value = comment_obj

    with pytest.raises(ValueError, match="Failed to edit comment 10001 on TEST-1"):
        await jira_client.edit_comment("TEST-1", "10001", "Updated")


@pytest.mark.asyncio
async def test_delete_comment_uses_issue_scoped_resource_and_accepts_empty_204(
    jira_client,
):
    comment_obj = make_comment()
    jira_client._jira.comment.return_value = comment_obj

    result = await jira_client.delete_comment("TEST-1", "10001")

    jira_client._jira.comment.assert_called_once_with("TEST-1", "10001")
    comment_obj.delete.assert_called_once_with()
    assert result == {"issue_key": "TEST-1", "comment_id": "10001", "deleted": True}


@pytest.mark.asyncio
@pytest.mark.parametrize(("issue_key", "comment_id"), [(" ", "10001"), ("TEST-1", "")])
async def test_delete_comment_rejects_blank_identifiers(
    jira_client, issue_key, comment_id
):
    with pytest.raises(ValueError, match="must not be blank"):
        await jira_client.delete_comment(issue_key, comment_id)
    jira_client._jira.comment.assert_not_called()


@pytest.mark.asyncio
async def test_delete_comment_surfaces_missing_comment_and_permission_errors(
    jira_client,
):
    jira_client._jira.comment.side_effect = JIRAError("Not found", status_code=404)
    with pytest.raises(ValueError, match="Failed to delete comment 10001 on TEST-1"):
        await jira_client.delete_comment("TEST-1", "10001")

    comment_obj = make_comment()
    comment_obj.delete.side_effect = JIRAError("Forbidden", status_code=403)
    jira_client._jira.comment.side_effect = None
    jira_client._jira.comment.return_value = comment_obj
    with pytest.raises(ValueError, match="Failed to delete comment 10001 on TEST-1"):
        await jira_client.delete_comment("TEST-1", "10001")


@pytest.mark.asyncio
async def test_delete_without_jira_confirmation_does_not_report_success(jira_client):
    comment_obj = make_comment()
    comment_obj.delete.return_value = None
    jira_client._jira.comment.return_value = comment_obj

    with pytest.raises(RuntimeError, match="did not confirm deletion"):
        await jira_client.delete_comment("TEST-1", "10001")
