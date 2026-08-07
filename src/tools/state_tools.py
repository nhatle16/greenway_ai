from typing import Annotated

from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.prebuilt import InjectedState
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


@tool
def update_travel_preferences(
    runtime: ToolRuntime,
    state: Annotated[dict, InjectedState],
    home_airport: str | None = None,
    preferred_mode: str | None = None,
    cabin_class: str | None = None,
    currency: str | None = None,
    max_budget: float | None = None,
    prioritize_eco: bool | None = None
) -> Command:
    """Updates the user's travel preferences. Provide only the fields that need updating."""
    current_preferences = state.get("preferences") or {}
    state_updates = {**current_preferences}
    
    updated = False
    if home_airport is not None:
        state_updates["home_airport"] = home_airport
        updated = True
    if preferred_mode is not None:
        state_updates["preferred_mode"] = preferred_mode
        updated = True
    if cabin_class is not None:
        state_updates["cabin_class"] = cabin_class
        updated = True
    if currency is not None:
        state_updates["currency"] = currency
        updated = True
    if max_budget is not None:
        state_updates["max_budget"] = max_budget
        updated = True
    if prioritize_eco is not None:
        state_updates["prioritize_eco"] = prioritize_eco
        updated = True

    if not updated:
        msg = "No travel preferences updates were provided."
    else:
        msg = "Successfully updated travel preferences."

    return Command(
        update={
            "messages": [ToolMessage(msg, tool_call_id=runtime.tool_call_id)],
            "preferences": state_updates
        }
    )


@tool
def update_active_trip(
    runtime: ToolRuntime,
    state: Annotated[dict, InjectedState],
    origin_city: str | None = None,
    origin_country: str | None = None,
    destination_city: str | None = None,
    destination_country: str | None = None,
    total_carbon_emission_kg: float | None = None
) -> Command:
    """Updates the user's active trip details. Provide only the fields that need updating."""
    current_trip = state.get("active_trip") or {}
    state_updates = {**current_trip}
    
    updated = False
    
    if origin_city or origin_country:
        current_origin = state_updates.get("origin") or {}
        new_origin = {**current_origin}
        if origin_city: new_origin["city"] = origin_city
        if origin_country: new_origin["country"] = origin_country
        state_updates["origin"] = new_origin
        updated = True
        
    if destination_city or destination_country:
        current_dest = state_updates.get("destination") or {}
        new_dest = {**current_dest}
        if destination_city: new_dest["city"] = destination_city
        if destination_country: new_dest["country"] = destination_country
        state_updates["destination"] = new_dest
        updated = True
        
    if total_carbon_emission_kg is not None:
        state_updates["total_carbon_emission_kg"] = total_carbon_emission_kg
        updated = True

    if not updated:
        msg = "No active trip updates were provided."
    else:
        msg = "Successfully updated active trip."

    return Command(
        update={
            "messages": [ToolMessage(msg, tool_call_id=runtime.tool_call_id)],
            "active_trip": state_updates
        }
    )
