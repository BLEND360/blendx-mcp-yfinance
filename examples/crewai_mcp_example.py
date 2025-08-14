#!/usr/bin/env python3
"""
Simple CrewAI example using MCP yfinance tools.

This example demonstrates how to use MCP yfinance tools with CrewAI agents.
"""

from crewai import Crew, Agent, Task
from crewai_tools import MCPServerAdapter
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# MCP Server Parameters
server_params = {
    "url": f"http://{os.getenv('MCP_HOST', 'localhost')}:{os.getenv('MCP_PORT', '8081')}/sse"
}

# Create MCP server adapter
mcp_server_adapter = MCPServerAdapter(server_params)
tools = mcp_server_adapter.tools

# Filter tools for specific agents
stock_analysis_tools = [tool for tool in tools if tool.name in ['get_stock_info', 'get_historical_data']]
financial_analysis_tools = [tool for tool in tools if tool.name in ['get_dividends', 'compare_stocks', 'calculate_correlation']]

# Create Agents
StockAnalystAgent = Agent(
    name="Stock Analyst",
    role="Stock Market Analysis Specialist",
    description="A specialist that analyzes stock information and historical data.",
    goal="Analyze stock information and provide detailed market insights.",
    backstory="You are an expert in stock market analysis with deep knowledge of "
              "financial markets, technical analysis, and market trends. You can "
              "analyze stock data and provide detailed insights about company "
              "performance, market movements, and investment opportunities.",
    tools=stock_analysis_tools,
    allow_delegation=False,
    verbose=True
)

FinancialAnalystAgent = Agent(
    name="Financial Analyst",
    role="Financial Analysis Specialist",
    description="A specialist that analyzes financial metrics and compares investments.",
    goal="Analyze financial metrics and provide investment comparison insights.",
    backstory="You are a financial analysis expert with expertise in dividend "
              "analysis, stock comparison, and correlation analysis. You can "
              "analyze financial data and provide insights about investment "
              "opportunities, risk assessment, and portfolio optimization.",
    tools=financial_analysis_tools,
    allow_delegation=False,
    verbose=True
)

# Create Tasks
StockAnalysisTask = Task(
    description=("Analyze Apple Inc. (AAPL) stock. Use get_stock_info to get basic "
                "company information and get_historical_data to analyze recent "
                "price movements and trends."),
    expected_output="Comprehensive stock analysis report including company info, "
                   "recent price performance, and market trend insights.",
    agent=StockAnalystAgent,
)

FinancialAnalysisTask = Task(
    description=("Analyze Apple Inc. (AAPL) financial metrics. Use get_dividends "
                "to analyze dividend information and compare_stocks to compare "
                "AAPL with Microsoft (MSFT) and Google (GOOGL)."),
    expected_output="Detailed financial analysis report including dividend analysis, "
                   "stock comparison, and investment recommendations.",
    agent=FinancialAnalystAgent,
)

# Create Crew
analysisCrew = Crew(
    agents=[StockAnalystAgent, FinancialAnalystAgent],
    tasks=[StockAnalysisTask, FinancialAnalysisTask],
    verbose=True
)

def main():
    """Main function to run the CrewAI analysis."""
    # Load environment variables from .env file
    load_dotenv()
    
    print("🚀 CrewAI MCP yfinance Analysis")
    print("=" * 50)
    print("Available MCP Tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    print("=" * 50)
    
    # Run the analysis
    print("Starting analysis...")
    result = analysisCrew.kickoff()
    
    print("\n📊 Analysis Results:")
    print("=" * 50)
    print(result)

if __name__ == "__main__":
    main() 