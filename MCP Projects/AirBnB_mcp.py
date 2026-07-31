import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))




from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.messages import HumanMessage

from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

load_dotenv()
model = ChatGoogleGenerativeAI(model="gemini-3-flash-preview")


def extract_text(message) -> str:
    """Pull plain text from a LangChain/Gemini message or content blocks."""
    if hasattr(message, "text"):
        text = str(message.text)
        if text:
            return text

    content = message.content if hasattr(message, "content") else message
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block if isinstance(block, str) else block.get("text", "")
            for block in content
            if isinstance(block, str) or block.get("type") == "text"
        )
    return str(content)

# -------------------------
# Airbnb MCP Prompt
# -------------------------
AIRBNB_PROMPT = """
You are a travel planning assistant.

Instructions:
- Use airbnb_search for all accommodation requests
- Use airbnb_listing_details when the user asks about a specific listing
- Use defaults: adults=2, no dates if not specified
- Present top 5 results with link: https://www.airbnb.com/rooms/{listing_id}
- Be proactive, don't ask for details unless search fails
"""

async def getTools():
    client = MultiServerMCPClient(
        {
            "airbnb": {
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
            }
        }
    )

    tools = await client.get_tools()

    print(f"Tools Loaded : {len(tools)}")

    return tools

async def hotelSearch(query: str):
    tools = await getTools()

    agent = create_agent(model, tools, system_prompt=AIRBNB_PROMPT)

    response = await agent.ainvoke({"messages": [HumanMessage(query)]})

    message = response["messages"][-1]
    hotels = extract_text(message)
    print("\n============== Output =============")
    print(hotels)

async def ask():
    print("\n Chat mode started. Type 'q' to exit\n")

    while True:
        query = input("Question : ").strip()

        if query.lower() == 'q':
            print("Exiting Chat Mode")
            break

        await hotelSearch(query)

if __name__ == "__main__":
    asyncio.run(ask())