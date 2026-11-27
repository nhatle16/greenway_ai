from tavily import TavilyClient
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()


@tool
def web_search(query: str):
    """Search information from the web."""
    # Created per call so a missing TAVILY_API_KEY only fails this tool, not the app's startup
    return TavilyClient().search(query=query)
