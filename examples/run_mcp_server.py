#!/usr/bin/env python3
"""
Example script to run the MCP server.

This script demonstrates how to start the MCP server and provides
examples of how to interact with it.
"""

import asyncio
import json
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_server import main


def run_server():
    """Run the MCP server with default settings."""
    print("Starting MCP Server...")
    print("=" * 50)
    print("Available tools:")
    print("- example_tool: Process text input")
    print("- text_analyzer: Analyze text statistics")
    print("- data_processor: Process numerical data")
    print("- correlation_analyzer: Calculate correlation between series")
    print("=" * 50)
    print("Server will be available at: http://localhost:8081")
    print("SSE endpoint: http://localhost:8081/sse")
    print("=" * 50)
    
    # Run the server
    main()


if __name__ == "__main__":
    run_server() 