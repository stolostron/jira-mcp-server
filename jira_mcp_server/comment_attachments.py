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
import re
from typing import Any, Dict, List, Optional

# Jira wiki inline image syntax (Cloud converts to ADF mediaSingle when attached).
_WIKI_INLINE_IMAGE = re.compile(r"!\s*([^|!\n]+?)\s*\|thumbnail!", re.IGNORECASE)


def strip_existing_inline_image_markers(text: str) -> str:
    """Remove wiki ``!file|thumbnail!`` markers from comment text.

    Callers should not duplicate markers in ``comment`` when using
    ``inline_attachment_paths``; MCP appends them once after upload.
    """
    without_markers = _WIKI_INLINE_IMAGE.sub("", text or "")
    lines = [line.rstrip() for line in without_markers.splitlines()]
    collapsed: List[str] = []
    for line in lines:
        if not line.strip():
            if collapsed and collapsed[-1] != "":
                collapsed.append("")
            continue
        collapsed.append(line)
    while collapsed and collapsed[-1] == "":
        collapsed.pop()
    return "\n".join(collapsed).strip()


def build_wiki_comment_body(
    comment: str,
    inline_filenames: List[str],
) -> str:
    """Build a Jira wiki comment body that embeds uploaded attachments inline.

    Jira Cloud converts ``!filename|thumbnail!`` to ADF ``mediaSingle`` nodes when
    the attachment already exists on the issue (upload before posting comment).
    """
    text = strip_existing_inline_image_markers(comment)
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
