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

"""Tests for issue attachments and inline comment uploads."""

import json
from unittest.mock import MagicMock, patch

import pytest

from jira_mcp_server.client import JiraClient
from jira_mcp_server.config import JiraConfig


class FakeUploadResponse:
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code
        self.text = json.dumps(data)

    @property
    def ok(self):
        return 200 <= self.status_code < 300

    def json(self):
        return self._data


class FakeCommentResponse:
    def __init__(self, data, status_code=201):
        self._data = data
        self.status_code = status_code
        self.text = json.dumps(data)

    @property
    def ok(self):
        return 200 <= self.status_code < 300

    def json(self):
        return self._data


@pytest.fixture
def client():
    config = JiraConfig(
        server_url="https://redhat.atlassian.net",
        access_token="fake-token",
        email="ashafi@redhat.com",
    )
    c = JiraClient(config)
    c._jira = MagicMock()
    c._jira._options = {"server": "https://redhat.atlassian.net"}
    c._jira._session = MagicMock()
    return c


@pytest.mark.asyncio
async def test_add_issue_attachments_uploads_via_requests(tmp_path, client):
    image = tmp_path / "proof.png"
    image.write_bytes(b"\x89PNG\r\n")

    upload_payload = [
        {
            "id": "99",
            "filename": "proof.png",
            "mimeType": "image/png",
            "size": 8,
            "content": "https://redhat.atlassian.net/rest/api/3/attachment/content/99",
        }
    ]

    with patch("jira_mcp_server.client.requests.post") as mock_post:
        mock_post.return_value = FakeUploadResponse(upload_payload)
        result = await client.add_issue_attachments("ACM-1", [str(image)])

    assert len(result) == 1
    assert result[0]["filename"] == "proof.png"
    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args.kwargs
    assert call_kwargs["headers"]["X-Atlassian-Token"] == "no-check"
    assert "file" in call_kwargs["files"]


@pytest.mark.asyncio
async def test_add_comment_with_inline_attachment_uses_wiki_v2(tmp_path, client):
    image = tmp_path / "screenshot.png"
    image.write_bytes(b"\x89PNG\r\n")

    upload_payload = [
        {
            "id": "100",
            "filename": "screenshot.png",
            "mimeType": "image/png",
            "size": 10,
            "content": "https://redhat.atlassian.net/rest/api/3/attachment/content/100",
        }
    ]
    comment_payload = {
        "id": "17001",
        "author": {"displayName": "Atif Shafi"},
        "created": "2026-05-20T18:00:00.000+0000",
        "updated": "2026-05-20T18:00:00.000+0000",
        "body": "wiki converted",
    }

    with patch("jira_mcp_server.client.requests.post") as mock_post:
        mock_post.return_value = FakeUploadResponse(upload_payload)
        client._jira._session.post.return_value = FakeCommentResponse(comment_payload)

        result = await client.add_comment(
            "ACM-29818",
            "Verified on 2.17.0-DOWNSTREAM-2026-05-20 (CSV 2.17.0), closing the ticket.",
            attachment_paths=[str(image)],
            inline_attachment_paths=[str(image)],
        )

    assert result["id"] == "17001"
    assert result["inline_filenames"] == ["screenshot.png"]
    assert len(result["attachments_uploaded"]) == 1

    wiki_post = client._jira._session.post
    wiki_post.assert_called_once()
    posted = wiki_post.call_args.kwargs["json"]
    assert "Verified on 2.17.0-DOWNSTREAM" in posted["body"]
    assert "!screenshot.png|thumbnail!" in posted["body"]


@pytest.mark.asyncio
async def test_add_comment_without_attachments_uses_jira_library(client):
    issue = MagicMock()
    comment_obj = MagicMock()
    comment_obj.id = "1"
    comment_obj.body = "plain text"
    comment_obj.author.displayName = "Atif Shafi"
    comment_obj.created = "2026-05-20T18:00:00.000+0000"
    comment_obj.updated = "2026-05-20T18:00:00.000+0000"

    client._jira.issue.return_value = issue
    client._jira.add_comment.return_value = comment_obj

    result = await client.add_comment("ACM-1", "hello")

    assert result["body"] == "plain text"
    assert result["attachments_uploaded"] == []
    client._jira.add_comment.assert_called_once()
