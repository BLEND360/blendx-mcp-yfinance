"""
MCP Server implementation for the tool template.

This module provides a proper MCP server that can be deployed locally or in containers
and follows the Model Context Protocol specification.
"""

import json
import logging
import os
import platform
import psutil
from datetime import datetime, UTC
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
from collections import defaultdict, Counter
import yfinance as yf
import httpx
import uvicorn
import pandas as pd
import numpy as np


from config.config_manager import ConfigManager
from utils.logging_utils import setup_logging

# Initialize logging
logger = setup_logging()

# Initialize configuration
config_manager = ConfigManager()

# Create an MCP server
mcp = FastMCP("yfinance")




@mcp.tool()
async def get_stock_info(ticker: str) -> str:
    """Get basic information about a stock/ticker including company name, sector, industry, etc.

    Dependencies:
        yfinance
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Extract key information
        result = {
            "ticker": ticker,
            "name": info.get("shortName", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "current_price": info.get("currentPrice", info.get("regularMarketPrice", "N/A")),
            "pe_ratio": info.get("trailingPE", "N/A"),
            "dividend_yield": info.get("dividendYield", "N/A"),
            "52_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "52_week_low": info.get("fiftyTwoWeekLow", "N/A")
        }
          2
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error retrieving stock info for {ticker}: {str(e)}"})


@mcp.tool()
async def get_historical_data(ticker: str, period: str = "1y", interval: str = "1d") -> str:
    """Get historical price data for a stock over a specified period.

    Dependencies:
        yfinance
    """
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period=period, interval=interval)
        
        if history.empty:
            return json.dumps({"error": f"No historical data available for {ticker}"})
            
        # Calculate basic statistics
        stats = {
            "start_date": history.index[0].strftime("%Y-%m-%d"),
            "end_date": history.index[-1].strftime("%Y-%m-%d"),
            "start_price": round(history["Close"].iloc[0], 2),
            "end_price": round(history["Close"].iloc[-1], 2),
            "min_price": round(history["Low"].min(), 2),
            "max_price": round(history["High"].max(), 2),
            "price_change": round(history["Close"].iloc[-1] - history["Close"].iloc[0], 2),
            "price_change_pct": round(((history["Close"].iloc[-1] / history["Close"].iloc[0]) - 1) * 100, 2),
            "avg_volume": round(history["Volume"].mean(), 2)
        }
        
        # Sample data points (limit to 30 points to avoid overwhelming response)
        max_points = 30
        if len(history) > max_points:
            step = len(history) // max_points
            sample_data = history.iloc[::step].tail(max_points)
        else:
            sample_data = history
            
        sample_data_dict = sample_data[["Open", "High", "Low", "Close", "Volume"]].reset_index()
        sample_data_dict["Date"] = sample_data_dict["Date"].astype(str)
        
        result = {
            "ticker": ticker,
            "period": period,
            "interval": interval,
            "stats": stats,
            "sample_data": sample_data_dict.to_dict("records")
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error retrieving historical data for {ticker}: {str(e)}"})


@mcp.tool()
async def get_dividends(ticker: str) -> str:
    """Get historical dividends for a stock.

    Dependencies:
        yfinance
    """
    try:
        stock = yf.Ticker(ticker)
        dividends = stock.dividends
        
        if dividends is None or dividends.empty:
            return json.dumps({
                "ticker": ticker,
                "has_dividends": False,
                "message": "This stock does not pay dividends."
            })
            
        # Get the last four quarters if available
        last_year_divs = dividends.tail(4)
        ttm_dividend = last_year_divs.sum()
        
        # Get current price for yield calculation
        current_price = stock.info.get("currentPrice", stock.info.get("regularMarketPrice", 0))
        
        # Calculate current yield
        current_yield = (ttm_dividend / current_price) * 100 if current_price > 0 else 0
        
        # Format dividend history
        div_items = [(idx.strftime("%Y-%m-%d"), float(val)) for idx, val in dividends.items()]
        div_items.sort(key=lambda x: x[0], reverse=True)
        recent_dividends = div_items[:8]
        
        result = {
            "ticker": ticker,
            "has_dividends": True,
            "dividend_yield_percent": round(current_yield, 2),
            "ttm_dividend": float(ttm_dividend),
            "current_price": current_price,
            "dividend_history": [{"date": date, "amount": amount} for date, amount in recent_dividends]
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error retrieving dividend information for {ticker}: {str(e)}"})


@mcp.tool()
async def compare_stocks(tickers: List[str], period: str = "1y") -> str:
    """Compare performance and key metrics of multiple stocks.

    Dependencies:
        yfinance
    """
    try:
        if not isinstance(tickers, list):
            return json.dumps({"error": "Tickers must be provided as a list."})
            
        # Limit the number of tickers to compare
        max_tickers = 5
        if len(tickers) > max_tickers:
            tickers = tickers[:max_tickers]
            
        stock_data = {}
        for ticker in tickers:
            stock = yf.Ticker(ticker)
            info = stock.info
            history = stock.history(period=period)
            
            if not history.empty:
                start_price = history["Close"].iloc[0]
                end_price = history["Close"].iloc[-1]
                price_change = end_price - start_price
                price_change_pct = (price_change / start_price) * 100
            else:
                start_price = end_price = price_change = price_change_pct = "N/A"
                
            stock_data[ticker] = {
                "name": info.get("shortName", "N/A"),
                "sector": info.get("sector", "N/A"),
                "market_cap": info.get("marketCap", "N/A"),
                "current_price": info.get("currentPrice", info.get("regularMarketPrice", "N/A")),
                "pe_ratio": info.get("trailingPE", "N/A"),
                "dividend_yield": info.get("dividendYield", "N/A"),
                "52_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
                "52_week_low": info.get("fiftyTwoWeekLow", "N/A"),
                "start_price": start_price,
                "end_price": end_price,
                "price_change": price_change,
                "price_change_pct": round(price_change_pct, 2) if isinstance(price_change_pct, (int, float)) else price_change_pct
            }
            
        result = {
            "tickers": tickers,
            "period": period,
            "comparison": stock_data
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error comparing stocks: {str(e)}"})


@mcp.tool()
async def calculate_correlation(series1: List[float], series2: List[float]) -> str:
    """Calculate correlation between two time series.

    Args:
        series1: First time series as a list of float values
        series2: Second time series as a list of float values

    Returns:
        JSON string containing correlation coefficient and analysis
    """
    try:
        if not isinstance(series1, list) or not isinstance(series2, list):
            return json.dumps({"error": "Both inputs must be lists of numbers"})
            
        if len(series1) != len(series2):
            return json.dumps({"error": "Both series must have the same length"})
            
        if len(series1) < 2:
            return json.dumps({"error": "Need at least 2 data points to calculate correlation"})
            
        # Convert to numpy arrays for calculation
        arr1 = np.array(series1)
        arr2 = np.array(series2)
        
        # Calculate correlation coefficient
        correlation = np.corrcoef(arr1, arr2)[0, 1]
        
        # Calculate additional statistics
        result = {
            "correlation": round(correlation, 4),
            "series_length": len(series1),
            "series1_stats": {
                "mean": round(float(np.mean(arr1)), 4),
                "std": round(float(np.std(arr1)), 4)
            },
            "series2_stats": {
                "mean": round(float(np.mean(arr2)), 4),
                "std": round(float(np.std(arr2)), 4)
            }
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error calculating correlation: {str(e)}"})


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can serve the provided mcp server with SSE."""
    sse = SseServerTransport("/messages/")
    
    async def handle_sse(request: Request):
        try:
            async with sse.connect_sse(
                request.scope, request._receive, request._send,
            ) as (read_stream, write_stream):
                await mcp_server.run(
                    read_stream, write_stream, mcp_server.create_initialization_options(),
                )
            # Return a proper response after successful SSE connection
            from starlette.responses import Response
            return Response(status_code=200)
        except Exception as e:
            # Return a proper error response instead of letting it bubble up
            from starlette.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={"error": f"SSE connection failed: {str(e)}"}
            )
    
    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


def main():
    """Main function to run the MCP server."""
    import argparse
    import uvicorn
    
    parser = argparse.ArgumentParser(description="Run MCP SSE-based server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8081, help="Port to listen on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()
    
    # Get MCP server instance
    mcp_server = mcp._mcp_server
    
    # Create Starlette app
    starlette_app = create_starlette_app(mcp_server, debug=args.debug)
    
    # Add health check endpoint
    @starlette_app.route("/health")
    async def health_check(request):
        from starlette.responses import JSONResponse
        return JSONResponse({"status": "healthy", "service": "mcp-server"})
    
    # Run the server
    logger.info(f"Starting MCP server on {args.host}:{args.port}")
    logger.info(f"Available tools: {list(mcp._tool_manager._tools.keys())}")
    
    uvicorn.run(starlette_app, host=args.host, port=args.port)


if __name__ == "__main__":
    main() 