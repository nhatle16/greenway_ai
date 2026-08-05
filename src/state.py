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


# Weather Context Schema
class WeatherContext(TypedDict, total=False):
    location_name: str | None
    temperature: float | None
    condition: str | None
    precipitation_mm: float | None
    humidity: float | None
    wind_speed: float | None
    is_outdoor_friendly: bool | None        # Helper flag for biking/walking suitability
    

# Agent State Schema
class AgentState(TypedDict, total=False):
    """Custom State schema for Greenway AI Agent.
    
    Tracks conversation history along with contextual user data (location, units, user profile).
    """
    messages: list[AnyMessage]
    user_location: UserLocation | None
    units: str
    user_id: str | None
    user_name: str | None
    language: str | None
    preferences: TravelPreferences | None
    active_trip: TripState | None
    weather_context: WeatherContext | None
