from tavily import TavilyClient
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

tavily_client = TavilyClient()


@tool
def web_search(query: str):
    """Search information from the web."""
    return tavily_client.search(query=query)
