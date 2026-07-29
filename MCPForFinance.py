import warnings 
warnings.filterwarnings("ignore")


from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from langchain_core.tools import StructuredTool
from langchain.agents.middleware import TodoListMiddleware

import asyncio

from scripts.yahoo_mcp import finance_research


def _finance_researcher(query: str) -> str:
    return asyncio.run(finance_research(query))


async def _finance_researcher_async(query: str) -> str:
    return await finance_research(query)


finance_researcher = StructuredTool.from_function(
    func=_finance_researcher,
    coroutine=_finance_researcher_async,
    name="finance_researcher",
    description=(
        "Research stocks using Yahoo Finance MCP tools (price, company info, "
        "valuation metrics, historical prices). Call this tool wherever you "
        "need to answer a finance related question."
    ),
)

if __name__ == "__main__":
    query = "What is the current stock price and recent performance of Apple (AAPL)? Also show me the latest news."

    print(finance_researcher.invoke({"query": query}))
