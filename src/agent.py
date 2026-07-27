from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from tools.search import web_search

load_dotenv()

system_prompt = """You are a knowledgeable assistant.
Always use the web search tool to find the latest and correct information from the web before answering user questions."""

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
