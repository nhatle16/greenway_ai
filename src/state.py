from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


# User Location Schema
class UserLocation(TypedDict, total=False):
    lat: float
    lng: float
    city: str | None
    country: str


# Travel Preferences Schema
class TravelPreferences(TypedDict, total=False):
    home_airport: str | None
    preferred_mode: str | None
    cabin_class: str | None
    currency: str
    max_budget: float | None
    prioritize_eco: bool


# Trip State Schema
class TripState(TypedDict, total=False):
    origin: UserLocation | None
    destination: UserLocation | None
    travel_preferences: TravelPreferences | None
    total_carbon_emission_kg: float | None


# Agent State Schema
class AgentState(TypedDict, total=False):
    """Custom State schema for Greenway AI Agent.
    
    Tracks conversation history along with contextual user data (location, units, user profile).
    """
    messages: Annotated[list[AnyMessage], add_messages]
    user_location: UserLocation | None
    units: str
    user_id: str | None
    user_name: str | None
    language: str | None
