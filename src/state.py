from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


# User Location Schema
class UserLocation(TypedDict, total=False):
    lat: float
    lng: float
    city: str | None
    country: str


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
