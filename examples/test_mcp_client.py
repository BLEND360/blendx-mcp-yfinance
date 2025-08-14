#!/usr/bin/env python3
"""
Simple MCP client to test your deployed yfinance MCP service.

This script demonstrates how to connect to and use your MCP tools.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp.client.session import ClientSession


async def test_mcp_tools(service_url: str):
    """Test all available MCP tools."""
    print(f"🔗 Connecting to MCP service: {service_url}")
    print("=" * 50)
    
    try:
        async with ClientSession(service_url) as session:
            print("✅ Connected successfully!")
            
            # Test get_stock_info
            print("\n🧪 Testing get_stock_info...")
            result = await session.call_tool("get_stock_info", {"ticker": "AAPL"})
            print(f"Result: {json.dumps(result, indent=2)}")
            
            # Test get_historical_data
            print("\n🧪 Testing get_historical_data...")
            result = await session.call_tool("get_historical_data", {"ticker": "AAPL", "period": "1mo", "interval": "1d"})
            print(f"Result: {json.dumps(result, indent=2)}")
            
            # Test get_dividends
            print("\n🧪 Testing get_dividends...")
            result = await session.call_tool("get_dividends", {"ticker": "AAPL"})
            print(f"Result: {json.dumps(result, indent=2)}")
            
            # Test compare_stocks
            print("\n🧪 Testing compare_stocks...")
            result = await session.call_tool("compare_stocks", {"tickers": ["AAPL", "MSFT", "GOOGL"], "period": "1mo"})
            print(f"Result: {json.dumps(result, indent=2)}")
            
            # Test calculate_correlation
            print("\n🧪 Testing calculate_correlation...")
            series1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            series2 = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
            result = await session.call_tool("calculate_correlation", {"series1": series1, "series2": series2})
            print(f"Result: {json.dumps(result, indent=2)}")
            
            print("\n✅ All tests completed successfully!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    return True


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test MCP yfinance tools")
    parser.add_argument("--url", help="MCP service URL")
    parser.add_argument("--local", action="store_true", help="Test local server")
    
    args = parser.parse_args()
    
    if args.local or not args.url:
        service_url = "http://localhost:8081"
    else:
        service_url = args.url
    
    print("🚀 MCP yfinance Tool Testing")
    print("=" * 50)
    print(f"Service URL: {service_url}")
    print("")
    
    # Run the tests
    success = asyncio.run(test_mcp_tools(service_url))
    
    if success:
        print("\n🎉 All tests passed!")
        print("\n📋 Usage Examples:")
        print("1. Local testing: python examples/test_mcp_client.py --local")
        print("2. Remote testing: python examples/test_mcp_client.py --url https://your-service-url")
        print("3. With Claude Desktop: Add the service URL to your Claude config")
    else:
        print("\n❌ Some tests failed. Check the service URL and ensure the server is running.")
        sys.exit(1)


if __name__ == "__main__":
    main() 