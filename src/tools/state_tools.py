from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.types import Command


def _given(**fields) -> dict:
    """Keep only the fields the model actually provided (drop None)."""
    return {k: v for k, v in fields.items() if v is not None}


@tool
def update_user_profile(
    username: str | None, language: str | None, runtime: ToolRuntime
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
            **state_updates,
        }
    )


@tool
def update_user_location(
    lat: float, lng: float, city: str, country: str, runtime: ToolRuntime
) -> Command:
    """Updates the user current location"""
    new_location = {"lat": lat, "lng": lng, "city": city, "country": country}

    return Command(
        update={
            "messages": [
                ToolMessage(
                    "Successfully updated user location.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
            "user_location": new_location,
        }
    )


@tool
def update_travel_preferences(
    runtime: ToolRuntime,
    home_airport: str | None = None,
    preferred_mode: str | None = None,
    cabin_class: str | None = None,
    currency: str | None = None,
    max_budget: float | None = None,
    prioritize_eco: bool | None = None,
) -> Command:
    """Updates the user's travel preferences. Provide only the fields that need updating."""
    updates = _given(
        home_airport=home_airport,
        preferred_mode=preferred_mode,
        cabin_class=cabin_class,
        currency=currency,
        max_budget=max_budget,
        prioritize_eco=prioritize_eco,
    )
    msg = (
        "Successfully updated travel preferences."
        if updates
        else "No travel preferences updates were provided."
    )
    return Command(
        update={
            "messages": [ToolMessage(msg, tool_call_id=runtime.tool_call_id)],
            "preferences": updates,
        }
    )


@tool
def update_active_trip(
    runtime: ToolRuntime,
    origin_city: str | None = None,
    origin_country: str | None = None,
    destination_city: str | None = None,
    destination_country: str | None = None,
    total_carbon_emission_kg: float | None = None,
) -> Command:
    """Updates the user's active trip details. Provide only the fields that need updating."""
    updates = _given(
        origin=_given(city=origin_city, country=origin_country) or None,
        destination=_given(city=destination_city, country=destination_country) or None,
        total_carbon_emission_kg=total_carbon_emission_kg,
    )

    msg = (
        "Successfully updated active trip."
        if updates
        else "No active trip updates were provided."
    )

    return Command(
        update={
            "messages": [ToolMessage(msg, tool_call_id=runtime.tool_call_id)],
            "active_trip": updates,
        }
    )


@tool
def update_current_weather(
    runtime: ToolRuntime,
    location_name: str | None = None,
    temperature: float | None = None,
    condition: str | None = None,
    precipitation_mm: float | None = None,
    humidity: float | None = None,
    wind_speed: float | None = None,
    is_outdoor_friendly: bool | None = None,
) -> Command:
    """Updates the user's current weather context. Provide only the fields that need updating."""
    updates = _given(
        location_name=location_name,
        temperature=temperature,
        condition=condition,
        precipitation_mm=precipitation_mm,
        humidity=humidity,
        wind_speed=wind_speed,
        is_outdoor_friendly=is_outdoor_friendly,
    )

    msg = (
        "Successfully updated weather context."
        if updates
        else "No weather context updates were provided."
    )

    return Command(
        update={
            "messages": [ToolMessage(msg, tool_call_id=runtime.tool_call_id)],
            "weather_context": updates,
        }
    )


@tool
def save_user_fact(key: str, value: str, runtime: ToolRuntime) -> str:
    """Saves a long-term fact about the user (e.g., name, travel preferences)."""
    context = runtime.context or {}
    user_id = context.get("user_id", "default_user")

    store = runtime.store

    if store is None:
        return "Unable to save user fact: long-term memory is unavailable."

    namespace = ("users", user_id)

    # One item per fact: no read-modify-write, so parallel saves can't overwrite each other
    store.put(namespace, key, {"value": value})

    return f"Successfully remembered '{key}: {value}' for user '{user_id}'."


@tool
def get_user_facts(runtime: ToolRuntime) -> dict:
    """Retrieves all saved long-term facts for the current user."""
    # Validate the provided context
    context = runtime.context or {}
    store = runtime.store

    if store is None:
        return {"error": "Long-term memory is unavailable."}

    namespace = ("users", context.get("user_id", "default_user"))

    # shortcut: returns at most 100 facts, page with `offset` if users ever store more
    items = store.search(namespace, limit=100)

    # Skip the legacy single "profile" item, which has no "value" field
    return {item.key: item.value["value"] for item in items if "value" in item.value}
