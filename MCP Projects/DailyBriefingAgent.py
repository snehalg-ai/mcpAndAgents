"""Daily Briefing Agent."""

import sys
from pathlib import Path

from dotenv import load_dotenv

root_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_dir))

load_dotenv()

from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

from scripts.base_tools import get_weather, web_search

_OAUTH_KEYS = Path.home() / ".gmail-mcp" / "gcp-oauth.keys.json"
_GMAIL_TOKEN = Path.home() / ".gmail-mcp" / "gmail-token.json"
_YAHOO_SERVER = root_dir / "scripts" / "yahoo_finance_server.py"

model = ChatGoogleGenerativeAI(model="gemini-3-flash-preview")


def get_daily_briefing_prompt():
    """Generate daily briefing prompt with current date context."""
    today = datetime.now()

    return f"""You are a daily briefing assistant.
            Default Location: Mumbai, India
            Today: {str(today.date())}

            Tools: Gmail, Yahoo Finance, Google Calendar, weather, web search

            Instructions:
            - Fetch today's weather for the default location (or the location the user names)
            - Read today's calendar events from Google Calendar
            - Summarize unread emails from Gmail
            - Show top news headlines using web_search; use Yahoo Finance tools for market context
            - Present information in a clear, organized format
            - If a tool fails or auth is missing, say so and continue with the other sections"""


async def get_tools():
    """Load MCP servers + local weather/web-search tools."""
    client = MultiServerMCPClient(
        {
            # https://github.com/MindMadeLab/mcp-google-gmail — pin mcp for FastMCP import
            "gmail": {
                "transport": "stdio",
                "command": "uvx",
                "args": [
                    "--with",
                    "mcp>=1.8.0,<1.28",
                    "mcp-google-gmail@latest",
                ],
                "env": {
                    "GMAIL_CREDENTIALS_PATH": str(_OAUTH_KEYS),
                    "GMAIL_TOKEN_PATH": str(_GMAIL_TOKEN),
                },
            },
            "yahoo-finance": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(_YAHOO_SERVER)],
            },
            # https://github.com/nspady/google-calendar-mcp
            "google-calendar": {
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "@cocal/google-calendar-mcp"],
                "env": {
                    "GOOGLE_OAUTH_CREDENTIALS": str(_OAUTH_KEYS),
                },
            },
        }
    )

    mcp_tools = await client.get_tools()
    tools = [*mcp_tools, get_weather, web_search]
    print(f"Tools Loaded : {len(tools)}")
    return tools


async def get_daily_briefing(query: str):
    tools = await get_tools()
    agent = create_agent(model, tools, system_prompt=get_daily_briefing_prompt())
    response = await agent.ainvoke({"messages": [HumanMessage(query)]})
    message = response["messages"][-1]
    print("\n============== Output =============")
    print(message.content)
    print("\n==================================\n")
    return message.content


async def ask():
    while True:
        query = input("Enter your query: ")
        if query.lower() == "exit":
            break
        await get_daily_briefing(query)


if __name__ == "__main__":
    asyncio.run(ask())
