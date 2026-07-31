import os

from langchain.tools import tool
import ollama
import requests

# -------------------------
# Web Search Tool
# -------------------------
@tool
def web_search(query: str):
    """
    Perform a live web search using Ollama Cloud Web Search API for real-time information and news.

    Input:
        query: search query string

    Output:
        JSON string of top results (max_results=2).
    """
    if not os.getenv("OLLAMA_API_KEY"):
        return (
            "Web search unavailable: set OLLAMA_API_KEY in .env "
            "(Ollama Cloud API key, not local Ollama)."
        )
    try:
        response = ollama.web_search(query=query, max_results=2)
        return response.results
    except Exception as exc:
        return f"Web search failed: {exc}"


# -------------------------
# Weather Tool
# -------------------------
@tool
def get_weather(location: str):
    """Get current weather for a location using WeatherAPI.com.

    Use for queries about weather, temperature, or conditions in any city.
    Examples: "weather in Paris", "temperature in Tokyo", "is it raining in London"

    Args:
        location: City name (e.g., "New York", "London", "Tokyo")

    Returns:
        Current weather information including temperature and conditions.
    """
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return "Weather unavailable: set WEATHER_API_KEY in .env"

    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&aqi=no"

    try:
        response = requests.get(url=url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        return f"Weather request failed: {exc}"
