from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from tools.search import web_search
from pathlib import Path

load_dotenv()


# Helper function to load prompts
def load_prompt(agent_name: str) -> str:
    """Loads prompt components from the filesystem and assembles them."""
    prompt_dir = Path(__file__).parent / "prompts" / agent_name
    
    prompt_parts = []
    
    system_file = prompt_dir / "system.md"
    if system_file.exists():
        prompt_parts.append(system_file.read_text())
        
    return "\n\n".join(prompt_parts)


# Create a LLM
model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0.5
)


# Define a root agent
root_agent = create_agent(
    model=model,
    tools=[web_search],
    system_prompt=load_prompt("root")
)
