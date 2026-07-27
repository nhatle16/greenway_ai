from langchain.tools import tool
from tavily import TavilyClient

tavily_client = TavilyClient()

@tool
def web_search(query: str):
    """Search information from the web."""
    return tavily_client.search(query=query)
