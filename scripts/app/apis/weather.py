"""
Weather API routes for AgriSmart backend.
Handles weather data and forecasts.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta
import logging
import httpx
import os

from app.models.schemas import WeatherResponse
from app.utils.security import get_current_user
from app.utils.logging import log_request, log_error
from app.database import db_ops

logger = logging.getLogger(__name__)

router = APIRouter()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

@router.get(
    "/current",
    response_model=WeatherResponse,
    summary="Get current weather",
    description="Get current weather data for user's farm location"
)
async def get_current_weather(current_user: dict = Depends(get_current_user)):
    """Get current weather for user's location."""
    try:
        if not OPENWEATHER_API_KEY:
            logger.error("OpenWeather API key not configured")
            # Return mock data for development
            return WeatherResponse(
                temperature=25.0,
                humidity=65.0,
                precipitation=0.0,
                wind_speed=3.5,
                location=current_user.get('region', 'Unknown'),
                forecast=[{
                    "timestamp": datetime.now() + timedelta(hours=i),
                    "temperature": 25.0 + (i % 5),
                    "precipitation": 0.0,
                    "humidity": 65.0,
                    "wind_speed": 3.5
                } for i in range(24)]
            )

        # Get coordinates from user's region (you might want to implement geocoding here)
        # For now using default coordinates
        lat, lon = 51.5074, -0.1278  # Default to London coordinates
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.openweathermap.org/data/2.5/weather",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": OPENWEATHER_API_KEY,
                    "units": "metric"
                }
            )
            response.raise_for_status()
            weather_data = response.json()

            # Get forecast data
            forecast_response = await client.get(
                f"https://api.openweathermap.org/data/2.5/forecast",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": OPENWEATHER_API_KEY,
                    "units": "metric"
                }
            )
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()

            # Convert the data to our schema
            return WeatherResponse(
                temperature=weather_data["main"]["temp"],
                humidity=weather_data["main"]["humidity"],
                precipitation=weather_data.get("rain", {}).get("1h", 0.0),
                wind_speed=weather_data["wind"]["speed"],
                location=weather_data["name"],
                forecast=[{
                    "timestamp": datetime.fromtimestamp(item["dt"]),
                    "temperature": item["main"]["temp"],
                    "precipitation": item.get("rain", {}).get("3h", 0.0) / 3,  # Convert 3h to 1h
                    "humidity": item["main"]["humidity"],
                    "wind_speed": item["wind"]["speed"]
                } for item in forecast_data.get("list", [])]
            )

    except httpx.HTTPError as e:
        logger.error(f"Weather API request failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weather service unavailable"
        )
    except Exception as e:
        logger.error(f"Error fetching weather data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch weather data"
        )
    log_request(logger, "GET", "/api/weather/current", str(current_user["id"]))
    
    try:
        # Get user's region from profile
        region = current_user.get("region", "")
        if not region:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User region not set"
            )
        
        # For now, return mock data
        # TODO: Integrate with actual weather API
        mock_weather = {
            "temperature": 25.5,
            "humidity": 65,
            "rainfall": 0.0,
            "wind_speed": 12,
            "forecast": "Clear sky",
            "alerts": [],
            "last_updated": datetime.now().isoformat()
        }
        
        return WeatherResponse(**mock_weather)
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(logger, e, "Get current weather")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve weather data"
        )