"""Tests for client helper methods: _extract_sprint, _parse_issue_links, _extract_user_display_name."""

from unittest.mock import MagicMock

import pytest

from jira_mcp_server.client import JiraClient
from jira_mcp_server.config import JiraConfig


@pytest.fixture
def client():
    """Create a JiraClient instance (not connected) for testing helper methods."""
    config = JiraConfig(server_url="https://test.example.com", access_token="test")
    return JiraClient(config)


# --- _extract_sprint tests (Jira Cloud format: array of sprint name strings) ---

class TestExtractSprint:
    def test_single_sprint(self, client):
        """Single sprint name in array is returned."""
        assert JiraClient._extract_sprint(["ACM Console 2.17 - 1"]) == "ACM Console 2.17 - 1"

    def test_multiple_sprints_returns_last(self, client):
        """With multiple sprints, returns the last one (most recent)."""
        sprint_data = ["ACM Console 2.16 - 2", "ACM Console 2.17 - 1"]
        assert JiraClient._extract_sprint(sprint_data) == "ACM Console 2.17 - 1"

    def test_none_returns_none(self, client):
        """None input returns None."""
        assert JiraClient._extract_sprint(None) is None

    def test_empty_list_returns_none(self, client):
        """Empty list returns None."""
        assert JiraClient._extract_sprint([]) is None

    def test_non_list_returns_string(self, client):
        """Non-list value is converted to string."""
        assert JiraClient._extract_sprint("Sprint 1") == "Sprint 1"

    def test_sprint_objects_with_name(self, client):
        """Sprint objects with .name attribute return the name."""
        sprint_obj = MagicMock()
        sprint_obj.name = "ACM Console 2.17 - 1"
        assert JiraClient._extract_sprint([sprint_obj]) == "ACM Console 2.17 - 1"

    def test_multiple_sprint_objects_returns_last(self, client):
        """Multiple sprint objects return the last one's name."""
        old = MagicMock()
        old.name = "ACM Console 2.16 - 2"
        current = MagicMock()
        current.name = "ACM Console 2.17 - 1"
        assert JiraClient._extract_sprint([old, current]) == "ACM Console 2.17 - 1"


# --- _extract_user_display_name tests ---

class TestExtractUserDisplayName:
    def test_none_returns_none(self, client):
        """None input returns None."""
        assert JiraClient._extract_user_display_name(None) is None

    def test_string_returns_string(self, client):
        """Plain string is returned as-is."""
        assert JiraClient._extract_user_display_name("Atif Shafi") == "Atif Shafi"

    def test_object_with_display_name(self, client):
        """Object with displayName attribute returns the display name."""
        user = MagicMock()
        user.displayName = "Atif Shafi"
        assert JiraClient._extract_user_display_name(user) == "Atif Shafi"

    def test_empty_string_returns_none(self, client):
        """Empty string returns None."""
        assert JiraClient._extract_user_display_name("") is None


# --- _parse_issue_links tests ---

class TestParseIssueLinks:
    def test_outward_link(self, client):
        """Outward issue link is parsed correctly."""
        link = MagicMock()
        link_type = MagicMock()
        link_type.name = "Blocks"
        link.type = link_type
        outward = MagicMock()
        outward.key = "ACM-100"
        outward.fields.summary = "Blocked issue"
        link.outwardIssue = outward
        # Ensure inwardIssue is absent
        del link.inwardIssue

        result = client._parse_issue_links([link])
        assert len(result) == 1
        assert result[0] == {
            'type': 'Blocks',
            'direction': 'outward',
            'key': 'ACM-100',
            'summary': 'Blocked issue'
        }

    def test_inward_link(self, client):
        """Inward issue link is parsed correctly."""
        link = MagicMock()
        link_type = MagicMock()
        link_type.name = "Relates"
        link.type = link_type
        inward = MagicMock()
        inward.key = "ACM-200"
        inward.fields.summary = "Related issue"
        link.inwardIssue = inward
        del link.outwardIssue

        result = client._parse_issue_links([link])
        assert len(result) == 1
        assert result[0] == {
            'type': 'Relates',
            'direction': 'inward',
            'key': 'ACM-200',
            'summary': 'Related issue'
        }

    def test_mixed_links(self, client):
        """Both inward and outward links are parsed correctly."""
        link_out = MagicMock()
        lt_out = MagicMock()
        lt_out.name = "Blocks"
        link_out.type = lt_out
        out_issue = MagicMock()
        out_issue.key = "ACM-100"
        out_issue.fields.summary = "Blocked"
        link_out.outwardIssue = out_issue
        del link_out.inwardIssue

        link_in = MagicMock()
        lt_in = MagicMock()
        lt_in.name = "Cloners"
        link_in.type = lt_in
        in_issue = MagicMock()
        in_issue.key = "ACM-300"
        in_issue.fields.summary = "Cloned from"
        link_in.inwardIssue = in_issue
        del link_in.outwardIssue

        result = client._parse_issue_links([link_out, link_in])
        assert len(result) == 2
        assert result[0]['direction'] == 'outward'
        assert result[1]['direction'] == 'inward'

    def test_empty_list(self, client):
        """Empty links list returns empty list."""
        assert client._parse_issue_links([]) == []
