from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.tools import tool
from tavily import TavilyClient

load_dotenv()


# Create a Tavily client for web search
tavily_client = TavilyClient()


# Define a web search tool
@tool
def web_search(query: str):
    """Search information from the web."""
    return tavily_client.search(query=query)

system_prompt = """You are a knowledgeable assistant.
Always use the web search tool to find the latest and correct information from the web before answering user questions."""

question = HumanMessage(content="Who is the current Prime Minister of Canada?")

model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0.5
)


# Define a root agent
root_agent = create_agent(
    model=model,
    tools=[web_search],
    system_prompt=system_prompt
)
