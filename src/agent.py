from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from src.state import AgentState
from src.tools.location_tools import geocode
from src.tools.search import web_search
from src.tools.state_tools import (
    update_active_trip,
    update_current_weather,
    update_travel_preferences,
    update_user_location,
    update_user_profile,
    save_user_fact,
    get_user_facts
)
from src.tools.travel_tools import (
    get_flight_options,
    get_ground_route,
    get_nearest_airport,
)
from src.tools.weather_tools import (
    get_weather_current,
    get_weather_forecast,
    get_weather_hourly,
)

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
    tools=[
        web_search,
        geocode,
        get_weather_current,
        get_weather_forecast,
        get_weather_hourly,
        get_ground_route,
        get_flight_options,
        get_nearest_airport,
        update_user_profile,
        update_user_location,
        update_travel_preferences,
        update_active_trip,
        update_current_weather,
        save_user_fact,
        get_user_facts
    ],
    state_schema=AgentState,
    system_prompt=load_prompt("root")
)
