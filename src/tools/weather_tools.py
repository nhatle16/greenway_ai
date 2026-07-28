import os
import requests

from dotenv import load_dotenv
from typing import Dict, Any
from langchain.tools import tool
from .location_tools import _geocode_impl

load_dotenv()


def _fetch_open_meteo_impl(
    lat: float,
    lng: float,
    units: str = 'metric',
    include_daily: bool = False,
    forecast_days: int = 3
) -> Dict[str, Any]:
    """_summary_

    Args:
        lat (float): _description_
        lng (float): _description_
        units (str, optional): _description_. Defaults to 'metric'.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    
    temp_unit = "fahrenheit" if units == "imperial" else "celsius"
    wind_unit = "mph" if units == "imperial" else "kmh"
    
    params = {
        "latitude": lat,
        "longitude": lng,
        "timezone": "auto",
        "temperature_unit": temp_unit,
        "wind_speed_unit": wind_unit
    }
    
    
    # Daily forecast mode
    if include_daily:
        params["daily"] = [
            "temperature_2m_max",
            "temperature_2m_min",
            "apparent_temperature_mean",
            "precipitation_probability_max",
            "rain_sum",
            "weather_code"
        ]
        params["forecast_days"] = forecast_days

    # Current weather condition mode
    else:
        params["current"] = [
            "temperature_2m",
            "apparent_temperature",
            "relative_humidity_2m",
            "dew_point_2m",
            "wind_speed_10m",
            "weather_code"
        ]
        
    try:
        response = requests.get(url, params)
        response.raise_for_status()
        data = response.json()
        
        if include_daily and "daily" in data:
            daily = data["daily"]
            units_info = data.get("daily_units", {})
            temp_symbol = units_info.get("apparent_temperature_mean", "°C")
            
            forecast_list = []
            
            for i in range(len(daily["time"])):
                code = daily["weather_code"][i]
                forecast_list.append({
                    "date": daily["time"][i],
                    "max_temp": f"{daily['temperature_2m_max'][i]} {temp_symbol}",
                    "min_temp": f"{daily['temperature_2m_min'][i]} {temp_symbol}",
                    "apparent_temp": f"{daily['apparent_temperature_mean'][i]} {temp_symbol}",
                    "condition": code,
                    "rain_chance": f"{daily['precipitation_probability_max'][i]} %",
                    "rain_amount": f"{daily['rain_sum'][i]} mm"
                })
            
            return {"forecast": forecast_list}
        
        current = data.get("current", {})
        units_info = data.get("current_units", {})
        code = current.get("weather_code", 0)
        
        return {
            "temperature": f"{current.get('temperature_2m')} {units_info.get('temperature_2m', '')}".strip(),
            "feels_like": f"{current.get('apparent_temperature')} {units_info.get('apparent_temperature', '')}".strip(),
            "humidity": f"{current.get('relative_humidity_2m')}%",
            "condition": code,
            "dew_point": f"{current.get('dew_point_2m')} {units_info.get('dew_point_2m', '')}".strip(),
            "wind_speed": f"{current.get('wind_speed_10m')} {units_info.get('wind_speed_10m', '')}".strip()
        }
        
    except requests.RequestException as e:
        return {"error": f"Open-Meteo HTTP request failed: {str(e)}"}


@tool
def get_weather_current(location: str, units: str = 'metric'):
    """Get the current weather for any city or region name.

    Args:
        location (str): The name of the location or city (e.g., 'Saskatoon', 'Vancouver, BC')
        units (str, optional): Unit system to use, either 'metric' (°C, km/h) or 'imperial' (°F, mph). Defaults to 'metric'.
    """
    coords = _geocode_impl(location)
    if "error" in coords:
        return coords
    
    weather = _fetch_open_meteo_impl(coords["lat"], coords["lng"], units)
    if "error" in weather:
        return weather
    
    weather["location"] = location
    return weather


@tool
def get_weather_forecast(location: str, days: int = 3, units: str = 'metric'):
    """Get the weather daily forecast for a city or region name during the upcoming days.

    Args:
        location (str): The name of the location or city (e.g., 'Saskatoon', 'Vancouver, BC')
        days (int, optional): Number of forecast days (1 to 7). Defaults to 3.
        units (str, optional): Unit system to use, either 'metric' (°C, km/h) or 'imperial' (°F, mph). Defaults to 'metric'.
    """
    coords = _geocode_impl(location)
    if "error" in coords:
        return coords
    
    # Fetch daily weather forecast
    forecast_data = _fetch_open_meteo_impl(
        lat=coords["lat"],
        lng=coords["lng"],
        units=units,
        include_daily=True,
        forecast_days=days
    )
    
    if "error" in forecast_data:
        return forecast_data
    
    return {
        "location": location,
        "forecast_days": days,
        "daily_forecast": forecast_data["forecast"]
    }
