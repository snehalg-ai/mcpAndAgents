"""Answer natural-language finance questions using the Yahoo Finance MCP server."""

import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

_SERVER_SCRIPT = Path(__file__).parent / "yahoo_finance_server.py"

system_prompt = """
                You are a financial research assistant helping users analyze stocks using Yahoo Finance data.

                Available Tools:
                - get_quote: Get the latest price, day range, and market cap (ticker required)
                - get_company_info: Get company profile - name, sector, industry, business summary (ticker required)
                - get_valuation_metrics: Get P/E ratios, dividend yield, 52-week range (ticker required)
                - get_historical_prices: Get historical daily OHLC prices as CSV (ticker required, optional: period='1mo')

                Instructions:
                - ALWAYS start by calling relevant tools to gather financial data when user asks about stocks
                - Extract ticker symbol from user query (e.g., AAPL, MSFT, GOOGL)
                - For general stock inquiries, call get_quote and get_company_info together
                - For price trend analysis, use get_historical_prices with appropriate period
                - Present data in a clear, organized format with key insights highlighted
                - Include specific numbers, percentages, and trends in your analysis
                - Be proactive - gather data first, then provide comprehensive analysis
                - If asked for something these tools can't provide (e.g. news, financial statements,
                  options, analyst recommendations), say so plainly instead of guessing
                """

async def finance_research(query: str) -> str:
    """Route a natural-language finance query to the Yahoo Finance MCP tools and return the answer."""
    client = MultiServerMCPClient(
        {
            "yahoo-finance": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(_SERVER_SCRIPT)],
            }
        }
    )
    tools = await client.get_tools()
    model = ChatGoogleGenerativeAI(model="gemini-flash-latest")
    agent = create_agent(model, tools, system_prompt=system_prompt)
    result = await agent.ainvoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content
