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

"""Tests for custom field support in create_issue and update_issue."""

import pytest
from jira_mcp_server.server import _merge_custom_fields


class TestMergeCustomFields:
    """Test the _merge_custom_fields helper."""

    def test_none_custom_fields_returns_named_unchanged(self):
        named = {"priority": {"name": "High"}, "labels": ["bug"]}
        result = _merge_custom_fields(named, None)
        assert result == named
        assert result is named

    def test_empty_custom_fields_returns_named_unchanged(self):
        named = {"priority": {"name": "High"}}
        result = _merge_custom_fields(named, {})
        assert result == named
        assert result is named

    def test_custom_fields_merged_into_result(self):
        named = {"priority": {"name": "High"}}
        custom = {"customfield_12313140": "PROJ-100"}
        result = _merge_custom_fields(named, custom)
        assert result == {
            "priority": {"name": "High"},
            "customfield_12313140": "PROJ-100",
        }

    def test_named_fields_take_precedence_over_custom_fields(self):
        named = {"customfield_12310243": 5.0}
        custom = {"customfield_12310243": 10.0}
        result = _merge_custom_fields(named, custom)
        assert result["customfield_12310243"] == 5.0

    def test_empty_named_with_custom_fields(self):
        custom = {"customfield_12311140": "EPIC-1"}
        result = _merge_custom_fields({}, custom)
        assert result == {"customfield_12311140": "EPIC-1"}

    def test_multiple_custom_fields(self):
        named = {"summary": "test"}
        custom = {
            "customfield_12313140": "FEAT-1",
            "customfield_12311140": "EPIC-2",
            "customfield_99999999": {"id": "42"},
        }
        result = _merge_custom_fields(named, custom)
        assert result == {
            "summary": "test",
            "customfield_12313140": "FEAT-1",
            "customfield_12311140": "EPIC-2",
            "customfield_99999999": {"id": "42"},
        }

    def test_does_not_mutate_inputs(self):
        named = {"priority": {"name": "High"}}
        custom = {"customfield_12313140": "PROJ-1"}
        named_copy = dict(named)
        custom_copy = dict(custom)

        _merge_custom_fields(named, custom)

        assert named == named_copy
        assert custom == custom_copy
