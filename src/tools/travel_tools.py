import os
from typing import Any, Literal

import requests
from dotenv import load_dotenv
from langchain.tools import tool

from .location_tools import geocode

load_dotenv()

TravelMode = Literal["driving", "motorcycle", "transit", "bicycling", "walking"]

def _get_ground_route_impl(
    origin: dict[str, float],
    destination: dict[str, float],
    mode: TravelMode = "driving"
) -> dict[str, Any]:
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
        response = requests.post(url, headers=headers, json=body, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "routes" in data and len(data["routes"]) > 0:
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
        return {"error": f"Routes API HTTP Error: {e!s}"}


def _get_nearest_airport_impl(
    location: dict[str, float],
    radius_km: int = 50
) -> dict[str, Any]:
    """Get the nearest (and alternative) airports to the given coordinates.

    Args:
        location (Dict[str, float]): Coordinates of the location. Expected in {'lat': float, 'lng': float}
        radius_km (int, optional): The radius to search within. Defaults to 50.

    Returns:
        Dict[str, Any]: Structured summary of the nearest airport and alternative airports, or error details.
    """
    api_key = os.getenv("DUFFEL_API_KEY")
    if not api_key:
        return {"error": "Missing DUFFEL_API_KEY"}

    lat, lng = location.get("lat"), location.get("lng")
    if lat is None or lng is None:
        return {"error": "Invalid location format. Expected {'lat': float, 'lng': float}"}

    url = "https://api.duffel.com/places/suggestions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Duffel-Version": "v2",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    params = {
        "lat": str(lat),
        "lng": str(lng),
        "rad": str(radius_km * 1000)    # convert km to meters
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        places = data.get("data", [])

        # Get airports
        airports = [p for p in places if p.get("type") == "airport" and p.get("iata_code")]

        if not airports:
            return {"error": f"No airports found within {radius_km}km of ({lat}, {lng})."}

        formatted_airports = []
        for a in airports[:3]:
            formatted_airports.append({
                "name": a.get("name"),
                "iata_code": a.get("iata_code"),
                "city_name": a.get("city_name"),
                "time_zone": a.get("time_zone")
            })

        return {
            "query_location": {"lat": lat, "lng": lng},
            "nearest_airport": formatted_airports[0],
            "alternative_airports": formatted_airports[1:] if len(formatted_airports) > 1 else []
        }

    except requests.RequestException as e:
        return {"error": f"Duffel Places API Error: {e!s}"}


def _get_flights_impl(
    origin: str,
    destination: str,
    departure_date: str,
    passengers: int = 1,
    max_results: int = 5
) -> dict[str, Any]:
    """Search for commercial flights via Duffel API.

    Args:
        origin (str): The IATA code of the origin airport (e.g., 'SFO').
        destination (str): The IATA code of the destination airport (e.g., 'LHR').
        departure_date (str): Date of departure in format: YYYY-MM-DD
        passengers (int, optional): Number of passengers. Defaults to 1.
        max_results (int, optional): Number of return results. Defaults to 5.

    Returns:
        Dict[str, Any]: Structured summary containing flight itineraries or error details.
    """
    api_key = os.getenv("DUFFEL_API_KEY")
    if not api_key:
        return {"error": "Missing DUFFEL_API_KEY environment variable."}

    # Added ?return_offers=true to force Duffel to include offers inline
    url = "https://api.duffel.com/air/offer_requests?return_offers=true"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Duffel-Version": "v2",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    body = {
        "data": {
            "slices": [
                {
                    "origin": origin.strip().upper(),
                    "destination": destination.strip().upper(),
                    "departure_date": departure_date,
                }
            ],
            "passengers": [{"type": "adult"} for _ in range(passengers)]
        }
    }

    try:
        response = requests.post(url, headers=headers, json=body, timeout=30)
        response.raise_for_status()
        data = response.json()

        offers = data.get("data", {}).get("offers", [])
        if not offers:
            return {"error": f"No flight offers found from '{origin}' to '{destination}' on {departure_date}."}

        # List of flight options
        flights = []

        for offer in offers[:max_results]:
            owner_airline = offer.get("owner", {}).get("name", "Unknown")
            total_amount = offer.get("total_amount", "0")
            total_currency = offer.get("total_currency", "USD")

            slices = offer.get("slices", [])
            if not slices:
                continue

            first_slice = slices[0]
            segments = first_slice.get("segments", [])
            if not segments:
                continue

            # Slice-level origin and destination preserve full journey details
            first_segment = segments[0]
            last_segment = segments[-1]

            origin_info = first_segment.get("origin", {})
            dest_info = last_segment.get("destination", {})

            # Construct clean segment (transfer) overview
            segment_details = []
            for seg in segments:
                carrier = seg.get("operating_carrier", {}).get("name") or seg.get("marketing_carrier", {}).get("name", "Airline")
                flight_num = seg.get("marketing_carrier_flight_number", "")
                segment_details.append({
                    "flight_number": f"{seg.get('marketing_carrier', {}).get('iata_code', '')}{flight_num}",
                    "carrier": carrier,
                    "departing_at": seg.get("departing_at"),
                    "arriving_at": seg.get("arriving_at"),
                    "origin": seg.get("origin", {}).get("iata_code"),
                    "destination": seg.get("destination", {}).get("iata_code")
                })

            # Full itinerary - including stops and stop details
            flights.append({
                "airline": owner_airline,
                "stops": len(segments) - 1,
                "origin": f"{origin_info.get('iata_code')}, {origin_info.get('iata_country_code')}",
                "destination": f"{dest_info.get('iata_code')}, {dest_info.get('iata_country_code')}",
                "departure": first_segment.get("departing_at"),
                "arrival": last_segment.get("arriving_at"),
                "total_duration": first_slice.get("duration"),
                "price": total_amount,
                "currency": total_currency,
                "segments": segment_details
            })

        return {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "results_returned": len(flights),
            "flights": flights
        }

    except requests.RequestException as e:
        return {"error": f"Duffel API HTTP Error: {e!s}"}


def _resolve_to_iata(location: str) -> dict[str, Any]:
    """Convert location string or IATA code into a valid 3-letter IATA code."""
    cleaned = location.strip()

    # Verify if input is already a 3-letter IATA code
    if len(cleaned) == 3 and cleaned.isalpha():
        return {"iata": cleaned.upper()}

    try:
        coords = geocode.invoke(location)   # get coordinates of location
        if not isinstance(coords, dict) or "lat" not in coords or "lng" not in coords:
            return {"error": f"Could not geocode location string: '{location}'."}

    except Exception as e:
        return {"error": f"Geocoding failed for '{location}': {e!s}"}

    # Resolve coordinates into nearest commercial airport using internal helper
    airport = _get_nearest_airport_impl(location=coords)
    if "error" in airport:
        return {"error": f"Airport lookup failed for '{location}': {airport['error']}"}

    nearest = airport.get("nearest_airport", {})
    iata_code = nearest.get("iata_code")

    if not iata_code:
        return {"error": f"No valid IATA airport code found near '{location}'."}

    return {"iata": iata_code}


@tool
def get_ground_route(
    origin: dict[str, float],
    destination: dict[str, float],
    mode: TravelMode = 'driving'
) -> dict[str, Any]:
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


@tool
def get_nearest_airport(
    location: dict[str, float],
    radius_km: int = 50
) -> dict[str, Any]:
    """Find the nearest commercial airport and its 3-letter IATA code for geographic coordinates.

    Args:
        location (Dict[str, float]): Latitude and longitude - {"lat": float, "lng": float}
        radius_km (int, optional): Search radius in kilometers. Defaults to 50.

    Returns:
        Dict[str, Any]: Primary nearest airport (IATA code, name, location) and alternatives.
    """
    return _get_nearest_airport_impl(location=location, radius_km=radius_km)


@tool
def get_flight_options(
    origin: str,
    destination: str,
    departure_date: str,
    passengers: int = 1,
    max_results: int = 5
) -> dict[str, Any]:
    """Search commercial flights between two locations.

    Args:
        origin (str): The IATA code of the origin airport (e.g., 'YXE') or city name (e.g., 'Saskatoon').
        destination (str): The IATA code of the destination airport (e.g., 'YYZ') or city name (e.g., 'Toronto').
        departure_date (str): Date of departure in format: YYYY-MM-DD
        passengers (int, optional): Number of passengers. Defaults to 1.
        max_results (int, optional): Number of return results. Defaults to 5.

    Returns:
        Dict[str, Any]: _description_
    """

    origin_res = _resolve_to_iata(origin)
    if "error" in origin_res:
        return origin_res

    dest_res = _resolve_to_iata(destination)
    if "error" in dest_res:
        return dest_res

    origin_iata = origin_res["iata"]
    dest_iata = dest_res["iata"]

    return _get_flights_impl(
        origin=origin_iata,
        destination=dest_iata,
        departure_date=departure_date,
        passengers=passengers,
        max_results=max_results
    )
