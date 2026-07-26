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

system_prompt = """

You are a knowledgeable individual, answer user questions at their requests.

Using the web search tool, find the latest and correct information from the web to answer user.

"""

question = HumanMessage(content="Who is the current Prime Minister of Canada?")

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.5
)


# Define a root agent
root_agent = create_agent(
    model=model,
    tools=[web_search],
    system_prompt=system_prompt
)

response = root_agent.invoke({"messages": [question]})


# Print the conversation
for m in response["messages"]:
    m.pretty_print()
