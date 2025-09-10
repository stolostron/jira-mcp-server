#!/usr/bin/env python3
"""
Example SSE client for the Jira MCP Server.

This demonstrates how to connect to the Jira MCP server using SSE transport
and perform basic operations.
"""

import asyncio
import json
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession


async def main():
    """Main function demonstrating SSE client usage."""
    server_url = "http://127.0.0.1:8000/sse"
    
    print(f"Connecting to Jira MCP Server at {server_url}")
    
    try:
        # Connect to the SSE server
        async with sse_client(url=server_url) as transport:
            read_stream, write_stream = transport
            
            # Create a client session
            async with ClientSession(read_stream, write_stream) as session:
                print("Connected successfully!")
                
                # Initialize the session
                init_result = await session.initialize()
                print(f"Server info: {init_result.server_info}")
                
                # List available tools
                tools = await session.list_tools()
                print(f"\nAvailable tools:")
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                # Example: Get projects
                print("\n--- Getting Jira Projects ---")
                try:
                    result = await session.call_tool("get_projects")
                    print("Projects:")
                    for project in result.content:
                        if hasattr(project, 'text'):
                            # Parse the JSON response
                            projects_data = json.loads(content.text)
                            for project in projects_data:
                                print(f"  - {project['key']}: {project['name']}")
                        else:
                            print(f"  - {project}")
                except Exception as e:
                    print(f"Error getting projects: {e}")
                
                # Example: Search for issues
                print("\n--- Searching for Issues ---")
                try:
                    # Search for recent issues (adjust JQL as needed)
                    result = await session.call_tool(
                        "search_issues", 
                        {"jql": "created >= -30d ORDER BY created DESC", "max_results": 5}
                    )
                    print("Recent issues:")
                    for content in result.content:
                        if hasattr(content, 'text'):
                            # Parse the JSON response
                            issues_data = json.loads(content.text)
                            for issue in issues_data:
                                print(f"  - {issue['key']}: {issue['summary']}")
                        else:
                            print(f"  - {content}")
                except Exception as e:
                    print(f"Error searching issues: {e}")
                    print("Note: Make sure you have proper Jira credentials configured")
                
                print("\nDemo completed successfully!")
                
    except Exception as e:
        print(f"Connection failed: {e}")
        print("Make sure the Jira MCP server is running with SSE transport:")
        print("  jira-mcp-server --transport sse")


if __name__ == "__main__":
    asyncio.run(main())