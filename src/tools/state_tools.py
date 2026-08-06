from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.types import Command


@tool
def update_user_profile(
    username: str | None,
    language: str | None,
    runtime: ToolRuntime
) -> Command:
    """Updates the user's name and/or preferred language in the system state."""
    state_updates = {}
    if username:
        state_updates["user_name"] = username
    if language:
        state_updates["language"] = language

    if not state_updates:
        msg = "No profile updates were provided."
    else:
        msg = f"Successfully updated user profile: {', '.join(state_updates.keys())}"

    return Command(
        update={
            "messages": [ToolMessage(msg, tool_call_id=runtime.tool_call_id)],
            **state_updates
        }
    )


@tool
def update_user_location(lat: float, lng: float, city: str, country: str, runtime: ToolRuntime) -> Command:
    """Updates the user current location"""
    new_location = {"lat": lat, "lng": lng, "city": city, "country": country}
    
    return Command(
        update={
            "messages": [ToolMessage("Successfully updated user location.", tool_call_id=runtime.tool_call_id)],
            "user_location": new_location
        }
    )
