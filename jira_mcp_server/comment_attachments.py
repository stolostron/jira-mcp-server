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

"""Helpers for Jira Cloud comment bodies with inline images."""

from __future__ import annotations

import mimetypes
import os
from typing import Any, Dict, List, Optional


def build_wiki_comment_body(
    comment: str,
    inline_filenames: List[str],
) -> str:
    """Build a Jira wiki comment body that embeds uploaded attachments inline.

    Jira Cloud converts ``!filename|thumbnail!`` to ADF ``mediaSingle`` nodes when
    the attachment already exists on the issue (upload before posting comment).
    """
    text = (comment or "").strip()
    markers = [f"!{name}|thumbnail!" for name in inline_filenames if name]
    if not markers:
        return text
    if not text:
        return "\n".join(markers)
    return f"{text}\n\n" + "\n".join(markers)


def resolve_inline_filenames(
    uploaded: List[Dict[str, Any]],
    inline_attachment_paths: Optional[List[str]],
    attachment_paths: Optional[List[str]],
) -> List[str]:
    """Determine which uploaded filenames to embed inline in the comment."""
    if inline_attachment_paths is not None:
        requested = {os.path.basename(p) for p in inline_attachment_paths}
        return [u["filename"] for u in uploaded if u["filename"] in requested]
    if attachment_paths:
        return [u["filename"] for u in uploaded]
    return []


def guess_mime_type(path: str) -> str:
    """Guess MIME type for an attachment path."""
    mime, _ = mimetypes.guess_type(path)
    return mime or "application/octet-stream"
