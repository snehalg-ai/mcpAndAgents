"""Travel Planner Agent with MCP Tools."""

import sys
from pathlib import Path

from dotenv import load_dotenv

root_dir = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root_dir))

load_dotenv()
from datetime import datetime, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

_OAUTH_KEYS = Path.home() / ".gmail-mcp" / "gcp-oauth.keys.json"

model = ChatGoogleGenerativeAI(model="gemini-3-flash-preview")

checkpoint = InMemorySaver()


# -------------------------
# Travel Planner Prompt
# -------------------------
def get_travel_planner_prompt():
    """Generate travel planner prompt with current date context."""
    today = datetime.now()
    checkin_date = today
    checkout_date = today + timedelta(days=5)

    return f"""You are a travel planning assistant.

            Today: {str(today.date())}
            Default dates: Check-in {str(checkin_date.date())}, Checkout {str(checkout_date.date())} (5 days)

            Tools: Airbnb search, weather, web search, Google Calendar

            Instructions:
            - Search Airbnb (default: 2 adults, no price filters unless requested)
            - Present listings with https://www.airbnb.com/rooms/{{listing_id}}
            - Add events to Google Calendar with times, locations and itenery descriptions"""


async def get_tools():
    """Get the tools for the agent."""
    mcp_client = MultiServerMCPClient(
        {
            "airbnb": {
                "command": "npx",
                "args": ["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
                "transport": "stdio",
            },
            # https://github.com/nspady/google-calendar-mcp
            "google-calendar": {
                "command": "npx",
                "args": ["-y", "@cocal/google-calendar-mcp"],
                "env": {
                    "GOOGLE_OAUTH_CREDENTIALS": str(_OAUTH_KEYS),
                },
                "transport": "stdio",
            },
        }
    )

    tools = await mcp_client.get_tools()

    print(f"Tools Loaded : {len(tools)}")

    return tools


async def plan_trip(query: str):
    tools = await get_tools()
    systemPrompt = get_travel_planner_prompt()
    agent = create_agent(model, tools, system_prompt=systemPrompt)
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
        await plan_trip(query)


if __name__ == "__main__":
    asyncio.run(ask())
