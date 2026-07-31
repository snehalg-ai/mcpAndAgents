"""Google Sheets MCP Test and Analysis."""

import sys
from pathlib import Path

from dotenv import load_dotenv

root_dir = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root_dir))

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.messages import HumanMessage

from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
from datetime import datetime, timedelta

# Desktop OAuth client JSON (same style as Calendar MCP). Token is stored separately.
_CREDENTIALS_PATH = Path.home() / ".gmail-mcp" / "gcp-oauth.keys.json"
_TOKEN_PATH = Path.home() / ".gmail-mcp" / "google-sheets-token.json"

model = ChatGoogleGenerativeAI(model="gemini-3-flash-preview")

# -------------------------
# Google Sheets Prompt
# -------------------------
GOOGLE_SHEETS_PROMPT = """You are a helpful Google Sheets assistant.

You have access to Google Sheets tools. When the user asks about spreadsheets:
- Use the list_spreadsheets tool to list all spreadsheets
- Use get_sheet_data to read sheet data
- Use create_spreadsheet to create new sheets

IMPORTANT: You MUST use the available tools to complete user requests. Do not try to answer without using tools."""


async def get_tools():
    """Load Google Sheets MCP tools."""
    client = MultiServerMCPClient(
        {
            # mcp-google-sheets still imports mcp.server.fastmcp; mcp>=1.28 removed it.
            "google-sheets": {
                "transport": "stdio",
                "command": "uvx",
                "args": [
                    "--with",
                    "mcp>=1.8.0,<1.28",
                    "mcp-google-sheets@latest",
                ],
                "env": {
                    "CREDENTIALS_PATH": str(_CREDENTIALS_PATH),
                    "TOKEN_PATH": str(_TOKEN_PATH),
                },
            }
        }
    )

    tools = await client.get_tools()
    print(f"Tools Loaded : {len(tools)}")
    return tools


async def analyze_sheet(query: str):
    tools = await get_tools()
    agent = create_agent(model, tools, system_prompt=GOOGLE_SHEETS_PROMPT)
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
        await analyze_sheet(query)


if __name__ == "__main__":
    asyncio.run(ask())
