"""Local MCP server exposing Yahoo Finance data as tools, backed by yfinance.

Run standalone for debugging: `python scripts/yahoo_finance_server.py`
Normally launched over stdio by scripts.yahoo_mcp.finance_research.
"""

import yfinance as yf
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("yahoo-finance")


@mcp.tool()
def get_quote(ticker: str) -> dict:
    """Get the latest price, day range, and market cap for a stock ticker (e.g. AAPL)."""
    info = yf.Ticker(ticker).fast_info
    return {
        "ticker": ticker.upper(),
        "last_price": info["lastPrice"],
        "currency": info["currency"],
        "previous_close": info["previousClose"],
        "day_high": info["dayHigh"],
        "day_low": info["dayLow"],
        "market_cap": info["marketCap"],
    }


@mcp.tool()
def get_company_info(ticker: str) -> dict:
    """Get company profile (name, sector, industry, business summary) for a stock ticker."""
    info = yf.Ticker(ticker).info
    return {
        "ticker": ticker.upper(),
        "name": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "summary": info.get("longBusinessSummary"),
    }


@mcp.tool()
def get_valuation_metrics(ticker: str) -> dict:
    """Get valuation metrics (P/E ratios, dividend yield, 52-week range) for a stock ticker."""
    info = yf.Ticker(ticker).info
    return {
        "ticker": ticker.upper(),
        "trailing_pe": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "dividend_yield": info.get("dividendYield"),
        "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
        "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
    }


@mcp.tool()
def get_historical_prices(ticker: str, period: str = "1mo") -> str:
    """Get historical daily OHLC prices for a stock ticker as CSV.

    period: one of 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max.
    """
    history = yf.Ticker(ticker).history(period=period)
    return history.to_csv()


if __name__ == "__main__":
    mcp.run(transport="stdio")
