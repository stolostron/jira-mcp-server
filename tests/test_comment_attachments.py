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

"""Tests for inline attachment comment helpers."""

from jira_mcp_server.comment_attachments import (
    build_wiki_comment_body,
    resolve_inline_filenames,
)


def test_build_wiki_comment_body_with_inline():
    body = build_wiki_comment_body(
        "Verified on 2.17.0-DOWNSTREAM-2026-05-20 (CSV 2.17.0), closing the ticket.",
        ["screenshot.png"],
    )
    assert "closing the ticket." in body
    assert body.endswith("!screenshot.png|thumbnail!")


def test_build_wiki_comment_body_markers_only():
    body = build_wiki_comment_body("", ["a.png", "b.jpg"])
    assert body == "!a.png|thumbnail!\n!b.jpg|thumbnail!"


def test_resolve_inline_filenames_defaults_to_all_uploaded():
    uploaded = [
        {"filename": "one.png", "id": "1"},
        {"filename": "two.png", "id": "2"},
    ]
    assert resolve_inline_filenames(
        uploaded, None, ["/tmp/one.png", "/tmp/two.png"]
    ) == [
        "one.png",
        "two.png",
    ]


def test_resolve_inline_filenames_subset():
    uploaded = [
        {"filename": "one.png", "id": "1"},
        {"filename": "two.png", "id": "2"},
    ]
    assert resolve_inline_filenames(uploaded, ["/tmp/two.png"], ["/tmp/one.png"]) == [
        "two.png"
    ]
