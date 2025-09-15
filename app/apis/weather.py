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