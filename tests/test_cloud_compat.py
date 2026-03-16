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

"""Tests for Jira Cloud compatibility: assignee resolution and
GDPR-compliant user search."""

import json
from typing import Any, Dict, List

import pytest

from jira_mcp_server.client import JiraClient
from jira_mcp_server.config import JiraConfig


# ---------------------------------------------------------------------------
# Reusable fakes
# ---------------------------------------------------------------------------

class FakeResponse:
    """Minimal stand-in for a ``requests.Response``."""

    def __init__(self, data: Any, status_code: int = 200):
        self._data = data
        self.status_code = status_code
        self.text = json.dumps(data) if not isinstance(data, str) else data

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 300

    def json(self) -> Any:
        return self._data


class FakeSession:
    """Fake HTTP session that records ``get`` calls and returns canned data."""

    def __init__(self) -> None:
        self.get_calls: List[str] = []
        self._responses: Dict[str, FakeResponse] = {}

    def register(self, url_substring: str, response: FakeResponse) -> None:
        self._responses[url_substring] = response

    def get(self, url: str) -> FakeResponse:
        self.get_calls.append(url)
        for substring, response in self._responses.items():
            if substring in url:
                return response
        return FakeResponse({"errorMessages": ["no canned response"]}, 404)


class FakeJira:
    """In-memory stand-in for ``jira.JIRA``.

    Supports the subset of the API used by ``JiraClient``: the ``_options``
    dict and the ``_session`` for raw REST calls.
    """

    def __init__(self, server_url: str = "https://redhat.atlassian.net"):
        self._options: Dict[str, Any] = {"server": server_url}
        self._session = FakeSession()


def _make_config() -> JiraConfig:
    return JiraConfig(
        server_url="https://redhat.atlassian.net",
        access_token="fake-token",
        email="bot@redhat.com",
    )


def _make_client(fake_jira: FakeJira | None = None) -> JiraClient:
    config = _make_config()
    client = JiraClient(config)
    client._jira = fake_jira or FakeJira()
    return client


# ---------------------------------------------------------------------------
# search_users
# ---------------------------------------------------------------------------

class TestSearchUsers:
    @pytest.fixture
    def client(self):
        fake = FakeJira()
        fake._session.register(
            "/rest/api/2/user/search",
            FakeResponse([
                {
                    "accountId": "abc:123",
                    "name": None,
                    "displayName": "Alice A",
                    "emailAddress": "alice@redhat.com",
                    "active": True,
                },
            ]),
        )
        return _make_client(fake_jira=fake)

    @pytest.mark.asyncio
    async def test_uses_query_parameter(self, client):
        results = await client.search_users("alice")
        assert len(results) == 1
        assert results[0]["account_id"] == "abc:123"
        assert results[0]["display_name"] == "Alice A"

        calls = client._jira._session.get_calls
        assert len(calls) == 1
        assert "query=alice" in calls[0]
        assert "username" not in calls[0]

    @pytest.mark.asyncio
    async def test_http_error_raises(self):
        fake = FakeJira()
        fake._session.register(
            "/rest/api/2/user/search",
            FakeResponse("GDPR strict mode error", 400),
        )
        client = _make_client(fake_jira=fake)

        with pytest.raises(ValueError, match="User search failed"):
            await client.search_users("bob")


# ---------------------------------------------------------------------------
# resolve_assignee
# ---------------------------------------------------------------------------

class TestResolveAssignee:
    @pytest.mark.asyncio
    async def test_account_id_passthrough(self):
        client = _make_client()
        result = await client.resolve_assignee("70121:0ea5df61-abcd-1234")
        assert result == {"accountId": "70121:0ea5df61-abcd-1234"}

    @pytest.mark.asyncio
    async def test_resolves_display_name_via_search(self):
        fake = FakeJira()
        fake._session.register(
            "/rest/api/2/user/search",
            FakeResponse([
                {
                    "accountId": "abc:999",
                    "name": None,
                    "displayName": "Alice A",
                    "emailAddress": "alice@redhat.com",
                    "active": True,
                },
            ]),
        )
        client = _make_client(fake_jira=fake)

        result = await client.resolve_assignee("Alice A")
        assert result == {"accountId": "abc:999"}

    @pytest.mark.asyncio
    async def test_resolves_email_via_search(self):
        fake = FakeJira()
        fake._session.register(
            "/rest/api/2/user/search",
            FakeResponse([
                {
                    "accountId": "abc:888",
                    "name": None,
                    "displayName": "Bob B",
                    "emailAddress": "bob@redhat.com",
                    "active": True,
                },
            ]),
        )
        client = _make_client(fake_jira=fake)

        result = await client.resolve_assignee("bob@redhat.com")
        assert result == {"accountId": "abc:888"}

    @pytest.mark.asyncio
    async def test_no_match_raises(self):
        fake = FakeJira()
        fake._session.register(
            "/rest/api/2/user/search",
            FakeResponse([]),
        )
        client = _make_client(fake_jira=fake)

        with pytest.raises(ValueError, match="No Jira user found"):
            await client.resolve_assignee("nonexistent")

    @pytest.mark.asyncio
    async def test_prefers_exact_match(self):
        fake = FakeJira()
        fake._session.register(
            "/rest/api/2/user/search",
            FakeResponse([
                {
                    "accountId": "abc:wrong",
                    "name": None,
                    "displayName": "Alice Wonderland",
                    "emailAddress": "alice.w@redhat.com",
                    "active": True,
                },
                {
                    "accountId": "abc:right",
                    "name": None,
                    "displayName": "Alice",
                    "emailAddress": "alice@redhat.com",
                    "active": True,
                },
            ]),
        )
        client = _make_client(fake_jira=fake)

        result = await client.resolve_assignee("Alice")
        assert result == {"accountId": "abc:right"}

    @pytest.mark.asyncio
    async def test_missing_account_id_raises(self):
        fake = FakeJira()
        fake._session.register(
            "/rest/api/2/user/search",
            FakeResponse([
                {
                    "accountId": None,
                    "name": None,
                    "displayName": "Ghost User",
                    "emailAddress": "ghost@redhat.com",
                    "active": False,
                },
            ]),
        )
        client = _make_client(fake_jira=fake)

        with pytest.raises(ValueError, match="has no accountId"):
            await client.resolve_assignee("Ghost User")
