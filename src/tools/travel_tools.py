import os
import requests

from dotenv import load_dotenv
from typing import Dict, Any, Literal
from langchain.tools import tool
from .location_tools import geocode

load_dotenv()

TravelMode = Literal["driving", "motorcycle", "transit", "bicycling", "walking"]

def _get_ground_route_impl(
    origin: Dict[str, float],
    destination: Dict[str, float],
    mode: TravelMode = "driving"
) -> Dict[str, Any]:
    """Calculate ground routing between two lat/lng points using Google Routes API

    Args:
        origin (Dict[str, float]): Coordinates of the origin - {"lat": float, "lng": float}
        destination (Dict[str, float]): Coordinates of the destination - {"lat": float, "lng": float}
        mode (str, optional): Ground transportation mode. Defaults to "driving".

    Returns:
        Dict[str, Any]: Route metrics (distance, duration, summary) or error message.
    """
    api_key = os.getenv("GOOGLE_MAPS_SERVER_KEY")
    if not api_key:
        return {"error": "Missing GOOGLE_MAPS_SERVER_KEY."}
    
    # Map generic modes to Google Routes API internal values
    mode_mapping = {
        "driving": "DRIVE",
        "motorcycle": "TWO_WHEELER",
        "transit": "TRANSIT",
        "bicycling": "BICYCLE",
        "walking": "WALK"
    }

    # Get the actual Google Routes API 
    google_mode = mode_mapping.get(mode, "DRIVE")
    
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.description"     # configure filters
    }
    
    body = {
        "origin": {
            "location": {
                "latLng": {
                    "latitude": origin["lat"],
                    "longitude": origin["lng"]
                }
            }
        },
        "destination": {
            "location": {
                "latLng": {
                    "latitude": destination["lat"],
                    "longitude": destination["lng"]
                }
            }
        },
        "travelMode": google_mode,
        "routingPreference": "TRAFFIC_AWARE" if google_mode in ["DRIVE", "TWO_WHEELER"] else "ROUTING_PREFERENCE_UNSPECIFIED"
    }
    
    try:
        response = requests.get(url, headers=headers, json=body, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "routes" in data and len(data["routes"] > 0):
            route = data["routes"][0]
            distance_meters = route.get("distanceMeters", 0)
            duration_seconds = int(route.get("duration", "0s").replace("s", ""))

            return {
                "mode": mode,
                "distance_km": round(distance_meters / 1000, 2),
                "distance_miles": round(distance_meters / 1609.34, 2),
                "duration_minutes": round(duration_seconds / 60),
                "summary": route.get("description", "Route found")
            }

        return {"error": f"No routes found for mode '{mode}'."}
        
    except requests.RequestException as e:
        return {"error": f"Routes API HTTP Error: {str(e)}"}


@tool
def get_ground_route(
    origin: Dict[str, float],
    destination: Dict[str, float],
    mode: TravelMode = 'driving'
) -> Dict[str, Any]:
    """Calculate ground travel routes, distance, and ETA between two latitude/longitude points.
    Supports driving, motorcycle (two-wheeler), public transit, bicycling, and walking via Google Maps Routes API.

    Args:
        origin (Dict[str, float]): Coordinates of the origin - {"lat": float, "lng": float}
        destination (Dict[str, float]): Coordinates of the destination - {"lat": float, "lng": float}
        mode (str, optional): Ground transportation mode. Defaults to "driving".

    Returns:
        Dict[str, Any]: Route metrics (distance, duration, summary) or error message.
    """
    return _get_ground_route_impl(origin=origin, destination=destination, mode=mode)
