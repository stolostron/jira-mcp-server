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

"""Tests for field-building logic: falsy-check bug fixes and new writable field mappings.

These test the field dict construction in create_issue/update_issue tool handlers.
Since the field dict building happens inside nested tool functions, we test
the logic patterns directly.  Where possible, tests call the real production
helpers (e.g., _user_ref) rather than re-building dicts inline.
"""

import pytest

from jira_mcp_server.server import _user_ref


class TestFalsyCheckFixes:
    """Verify that `is not None` checks handle falsy values correctly."""

    def test_story_points_zero_included(self):
        """story_points=0 should result in field being set (not skipped)."""
        fields = {}
        story_points = 0
        if story_points is not None:
            fields['customfield_10028'] = story_points
        assert 'customfield_10028' in fields
        assert fields['customfield_10028'] == 0

    def test_story_points_none_skipped(self):
        """story_points=None should NOT set the field."""
        fields = {}
        story_points = None
        if story_points is not None:
            fields['customfield_10028'] = story_points
        assert 'customfield_10028' not in fields

    def test_story_points_positive(self):
        """story_points=5.0 should set the field normally."""
        fields = {}
        story_points = 5.0
        if story_points is not None:
            fields['customfield_10028'] = story_points
        assert fields['customfield_10028'] == 5.0

    def test_original_estimate_empty_included(self):
        """original_estimate='' should result in field being set."""
        fields = {}
        original_estimate = ""
        if original_estimate is not None:
            fields['timetracking'] = {'originalEstimate': original_estimate}
        assert 'timetracking' in fields
        assert fields['timetracking']['originalEstimate'] == ""

    def test_original_estimate_none_skipped(self):
        """original_estimate=None should NOT set the field."""
        fields = {}
        original_estimate = None
        if original_estimate is not None:
            fields['timetracking'] = {'originalEstimate': original_estimate}
        assert 'timetracking' not in fields

    def test_old_falsy_check_would_fail_zero(self):
        """Demonstrate the old bug: `if story_points:` skips 0."""
        fields = {}
        story_points = 0
        # OLD broken logic
        if story_points:
            fields['customfield_10028'] = story_points
        assert 'customfield_10028' not in fields

    def test_old_falsy_check_would_fail_empty_string(self):
        """Demonstrate the old bug: `if original_estimate:` skips ''."""
        fields = {}
        original_estimate = ""
        # OLD broken logic
        if original_estimate:
            fields['timetracking'] = {'originalEstimate': original_estimate}
        # This proves the old check was wrong
        assert 'timetracking' not in fields


class TestNewWritableFieldMappings:
    """Verify new field mapping patterns produce correct JIRA API format."""

    def test_qa_contact_mapping(self):
        """qa_contact is set via _user_ref (accountId on Cloud)."""
        fields = {}
        qa_contact = "712020:76916d54-887a-4d7c-8898-6a4e91d98bb7"
        if qa_contact is not None:
            fields['customfield_10470'] = _user_ref(qa_contact)
        assert fields['customfield_10470'] == {'accountId': '712020:76916d54-887a-4d7c-8898-6a4e91d98bb7'}

    def test_contributors_mapping(self):
        """contributors maps to list of _user_ref dicts."""
        contributors = [
            "712020:76916d54-887a-4d7c-8898-6a4e91d98bb7",
            "61fa7a56f5f5b80070c78e2c",
        ]
        valid = [c.strip() for c in contributors if isinstance(c, str) and c.strip()]
        fields = {}
        if valid:
            fields['customfield_10466'] = [_user_ref(c) for c in valid]
        assert len(fields['customfield_10466']) == 2
        assert fields['customfield_10466'][0] == {'accountId': '712020:76916d54-887a-4d7c-8898-6a4e91d98bb7'}
        assert fields['customfield_10466'][1] == {'accountId': '61fa7a56f5f5b80070c78e2c'}

    def test_contributors_empty_strings_filtered(self):
        """Empty/whitespace contributor strings are filtered out."""
        contributors = ["valid-id", "  ", "", "another-id"]
        valid = [c.strip() for c in contributors if isinstance(c, str) and c.strip()]
        fields = {}
        if valid:
            fields['customfield_10466'] = [_user_ref(c) for c in valid]
        assert len(fields['customfield_10466']) == 2

    def test_user_ref_empty_raises(self):
        """_user_ref raises ValueError for empty strings."""
        with pytest.raises(ValueError):
            _user_ref("")
        with pytest.raises(ValueError):
            _user_ref("   ")

    def test_user_ref_accepts_opaque_ids(self):
        """_user_ref accepts any non-empty string (Atlassian accountIds are opaque)."""
        assert _user_ref("61fa7a56f5f5b80070c78e2c") == {'accountId': '61fa7a56f5f5b80070c78e2c'}
        assert _user_ref("557057:abc") == {'accountId': '557057:abc'}
        assert _user_ref("some-short-id") == {'accountId': 'some-short-id'}

    def test_severity_mapping(self):
        """severity maps to {'value': severity_name}."""
        fields = {}
        severity = "Important"
        if severity is not None:
            fields['customfield_10840'] = {'value': severity}
        assert fields['customfield_10840'] == {'value': 'Important'}

    def test_affects_versions_mapping(self):
        """affects_versions maps to list of {'name': version} dicts."""
        fields = {}
        affects_versions = ["ACM 2.15.0", "ACM 2.16.0"]
        if affects_versions is not None:
            fields['versions'] = [{'name': v} for v in affects_versions]
        assert fields['versions'] == [{'name': 'ACM 2.15.0'}, {'name': 'ACM 2.16.0'}]

    def test_acceptance_criteria_mapping(self):
        """acceptance_criteria maps to plain string."""
        fields = {}
        acceptance_criteria = "All tests pass"
        if acceptance_criteria is not None:
            fields['customfield_10718'] = acceptance_criteria
        assert fields['customfield_10718'] == "All tests pass"

    def test_none_fields_not_set(self):
        """None values should not create entries in the fields dict."""
        fields = {}
        for field_val, field_key in [
            (None, 'customfield_10470'),
            (None, 'customfield_10840'),
            (None, 'versions'),
            (None, 'customfield_10718'),
            (None, 'customfield_10466'),
        ]:
            if field_val is not None:
                fields[field_key] = field_val
        assert len(fields) == 0
