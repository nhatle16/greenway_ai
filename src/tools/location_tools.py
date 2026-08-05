import os
from typing import Any

import requests
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()


def _geocode_impl(location: str) -> dict[str, Any]:
    """Convert the location name into the exact geographic coordinates

    Args:
        location (str): The location name.

    Returns:
        Dict[str, Any]: Latitude and longitude of the location if API call succeeds, error message otherwise.
    """
    api_key = os.getenv("GOOGLE_MAPS_SERVER_KEY")
    if not api_key:
        return {"error": "Missing GOOGLE_MAPS_SERVER_KEY."}
    
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": location,
        "key": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "OK" and data.get("results"):
            loc = data["results"][0]["geometry"]["location"]
            return {
                "lat": loc["lat"],
                "lng": loc["lng"]
            }
        return {"error": f"Geocoding failed for {location}: {data.get('status')}"}
    except Exception as e:
        return {"error": f"HTTP Error: {e!s}"}
    
    
@tool
def geocode(location: str) -> dict[str, Any]:
    """Get exact latitude and longitude coordinates for an address, location or landmark."""
    return _geocode_impl(location)
