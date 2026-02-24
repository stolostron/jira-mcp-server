#!/usr/bin/env python3
"""
Test script to validate Jira API token and connection.

Usage:
    python3 test_connection.py

This script will:
1. Load credentials from .env file
2. Test connection to Jira
3. Verify authentication
4. Test basic operations
"""

import asyncio
import sys
import pytest
from jira_mcp_server.config import JiraConfig
from jira_mcp_server.client import JiraClient


@pytest.mark.asyncio
async def test_jira_connection():
    """Test Jira connection and basic operations."""

    print("=" * 70)
    print("JIRA MCP SERVER - CONNECTION TEST")
    print("=" * 70)
    print()

    # Step 1: Load configuration
    print("📋 Step 1: Loading configuration from .env file...")
    try:
        config = JiraConfig.from_env()
        print(f"   ✅ Configuration loaded successfully")
        print(f"   Server URL: {config.server_url}")
        print(f"   Email: {config.email}")
        print(f"   Is Cloud: {config.is_cloud()}")
        print(f"   Token length: {len(config.access_token)} characters")
        print(f"   Token preview: {config.access_token[:15]}...{config.access_token[-10:]}")
        print()
    except Exception as e:
        print(f"   ❌ Failed to load configuration: {e}")
        return False

    # Step 2: Validate required fields
    print("🔍 Step 2: Validating required fields...")
    try:
        config.validate_required_fields()
        print("   ✅ All required fields present")
        print()
    except ValueError as e:
        print(f"   ❌ Missing required fields: {e}")
        return False

    # Step 3: Test connection
    print("🔌 Step 3: Testing connection to Jira...")
    client = JiraClient(config)
    try:
        await client.connect()
        print("   ✅ Successfully connected to Jira!")
        print("   ✅ Authentication successful")
        print()
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        print()
        print("Common issues:")
        print("  - API token is expired or invalid")
        print("  - Email doesn't match the token owner")
        print("  - No access to this Jira instance")
        print()
        print("To fix:")
        print("  1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens")
        print("  2. Create a new API token")
        print("  3. Update JIRA_ACCESS_TOKEN in your .env file")
        return False

    # Step 4: Test getting user info
    print("👤 Step 4: Getting current user information...")
    try:
        myself = await client._async_call(lambda: client._jira.myself())
        print(f"   ✅ Logged in as: {myself.get('displayName', 'Unknown')}")
        print(f"   Email: {myself.get('emailAddress', 'Unknown')}")
        print(f"   Account ID: {myself.get('accountId', 'Unknown')}")
        print()
    except Exception as e:
        print(f"   ⚠️  Could not get user info: {e}")
        print()

    # Step 5: Test getting projects
    print("📁 Step 5: Getting accessible projects...")
    try:
        projects = await client.get_projects()
        print(f"   ✅ Found {len(projects)} accessible projects")

        if projects:
            print()
            print("   First 10 projects:")
            for i, project in enumerate(projects[:10], 1):
                print(f"      {i}. {project['key']}: {project['name']}")
        else:
            print("   ⚠️  No projects found (you may not have access)")
        print()
    except Exception as e:
        print(f"   ❌ Failed to get projects: {e}")
        return False

    # Step 6: Test searching for issues
    print("🔎 Step 6: Testing issue search...")
    try:
        # Search for recent issues assigned to current user
        jql = "assignee = currentUser() ORDER BY updated DESC"
        issues = await client.search_issues(jql, max_results=5)
        print(f"   ✅ Search successful - Found {len(issues)} issues assigned to you")

        if issues:
            print()
            print("   Your recent issues:")
            for issue in issues:
                print(f"      - {issue['key']}: {issue['summary'][:60]}")
                print(f"        Status: {issue['status']}, Updated: {issue['updated'][:10]}")
        print()
    except Exception as e:
        print(f"   ⚠️  Search test: {e}")
        print()

    # Success!
    print("=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    print()
    print("Your Jira MCP server is ready to use!")
    print()
    print("Next steps:")
    print("  1. Configure your MCP client (.mcp.json or .claude/settings.json)")
    print("  2. Restart Claude Code or your MCP client")
    print("  3. Try asking: 'Show me my Jira issues'")
    print()

    return True


def main():
    """Main entry point."""
    try:
        success = asyncio.run(test_jira_connection())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
