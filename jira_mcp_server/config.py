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

"""Configuration management for Jira MCP Server."""

import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class JiraConfig(BaseModel):
    """Configuration for Jira connection."""
    
    server_url: str = Field(..., description="Jira server URL")
    access_token: str = Field(..., description="Jira personal access token")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_results: int = Field(default=100, description="Maximum results per request")
    
    @classmethod
    def from_env(cls) -> "JiraConfig":
        """Create configuration from environment variables."""
        return cls(
            server_url=os.getenv("JIRA_SERVER_URL", ""),
            access_token=os.getenv("JIRA_ACCESS_TOKEN", ""),
            verify_ssl=os.getenv("JIRA_VERIFY_SSL", "true").lower() == "true",
            timeout=int(os.getenv("JIRA_TIMEOUT", "30")),
            max_results=int(os.getenv("JIRA_MAX_RESULTS", "100")),
        )
    
    def validate_required_fields(self) -> None:
        """Validate that required fields are present."""
        if not self.server_url:
            raise ValueError("JIRA_SERVER_URL is required")
        if not self.access_token:
            raise ValueError("JIRA_ACCESS_TOKEN is required")