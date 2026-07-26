from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

load_dotenv()

system_prompt = "You are a knowledgeable individual, answer user questions at their requests."

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.5
)

# Define a root agent
root_agent = create_agent(
    model=model,
    system_prompt=system_prompt
)
