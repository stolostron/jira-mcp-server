# Copyright 2025 Red Hat, Inc.
#
# Integration tests for issue attachment list/download.
# Skipped unless JIRA_EMAIL, JIRA_ACCESS_TOKEN, and JIRA_SERVER_URL are set.

import os

import pytest
import pytest_asyncio

from jira_mcp_server.client import JiraClient
from jira_mcp_server.config import JiraConfig

pytestmark = pytest.mark.skipif(
    not all(
        os.environ.get(k)
        for k in ("JIRA_EMAIL", "JIRA_ACCESS_TOKEN", "JIRA_SERVER_URL")
    ),
    reason="JIRA credentials not in environment",
)

ISSUE_KEY = os.environ.get("JIRA_ATTACHMENT_TEST_ISSUE", "ACM-26935")


@pytest_asyncio.fixture
async def connected_client():
    client = JiraClient(JiraConfig.from_env())
    await client.connect()
    yield client


@pytest.mark.asyncio
async def test_list_attachments_on_acm_26935(connected_client):
    items = await connected_client.list_issue_attachments(ISSUE_KEY)
    assert len(items) >= 1
    first = items[0]
    assert first["id"]
    assert first["filename"]
    assert first.get("content_url")


@pytest.mark.asyncio
async def test_get_issue_includes_attachment_details(connected_client):
    issue = await connected_client.get_issue(ISSUE_KEY)
    assert issue["attachments"]
    assert issue["attachment_details"]
    assert issue["attachment_details"][0]["id"]
    assert issue["attachment_details"][0]["filename"] in issue["attachments"]


@pytest.mark.asyncio
async def test_download_attachment_by_id(tmp_path, connected_client):
    items = await connected_client.list_issue_attachments(ISSUE_KEY)
    dest = tmp_path / "downloaded.png"
    result = await connected_client.download_issue_attachment(
        ISSUE_KEY,
        attachment_id=items[0]["id"],
        save_path=str(dest),
    )
    assert dest.is_file()
    assert dest.stat().st_size == result["size"]
    assert result["size"] > 0
    assert result["filename"] == items[0]["filename"]


@pytest.mark.asyncio
async def test_download_attachment_by_filename_substring(tmp_path, connected_client):
    items = await connected_client.list_issue_attachments(ISSUE_KEY)
    needle = "Screenshot"
    matches = [i for i in items if needle in i["filename"]]
    assert len(matches) == 1

    dest = tmp_path / "by-name.png"
    result = await connected_client.download_issue_attachment(
        ISSUE_KEY,
        filename=needle,
        save_path=str(dest),
    )
    assert dest.is_file()
    assert matches[0]["filename"] == result["filename"]
