"""
Market data API routes for AgriSmart backend.
Handles crop prices, market trends, and demand forecasts.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import numpy as np
from uuid import uuid4

from app.models.schemas import MarketData, PriceHistory, MarketTrends, DemandForecast
from app.utils.security import get_current_user
from app.utils.logging import log_request, log_error
from app.database import supabase

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get(
    "/",
    response_model=Dict[str, MarketData],
    summary="Get current market data",
    description="Get current market prices and trends for crops"
)
async def get_market_data(
    crop_types: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get current market data for specified crops."""
    log_request(logger, "GET", "/api/market-data", str(current_user["id"]))
    
    try:
        # Use user's crops if none specified
        if not crop_types:
            crop_types = current_user.get("main_crops", "wheat,rice,corn")
        
        crops = [c.strip() for c in crop_types.split(",")]
        market_data = {}
        
        for crop in crops:
            market_data[crop] = generate_mock_market_data(crop)
            
        return market_data
        
    except Exception as e:
        log_error(logger, e, "Get market data")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch market data"
        )

@router.get(
    "/price-history/{crop_type}",
    response_model=PriceHistory,
    summary="Get price history",
    description="Get historical price data for a specific crop"
)
async def get_price_history(
    crop_type: str,
    days: Optional[int] = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get historical price data for a crop."""
    log_request(logger, "GET", f"/api/market-data/price-history/{crop_type}", str(current_user["id"]))
    
    try:
        return generate_mock_price_history(crop_type, days)
        
    except Exception as e:
        log_error(logger, e, "Get price history")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch price history"
        )

@router.get(
    "/trends",
    response_model=List[MarketTrends],
    summary="Get market trends",
    description="Get market trends and analysis for crops"
)
async def get_market_trends(current_user: dict = Depends(get_current_user)):
    """Get market trends and analysis."""
    log_request(logger, "GET", "/api/market-data/trends", str(current_user["id"]))
    
    try:
        user_crops = current_user.get("main_crops", "").split(",")
        trends = []
        
        for crop in user_crops:
            trends.append(generate_mock_market_trends(crop))
            
        return trends
        
    except Exception as e:
        log_error(logger, e, "Get market trends")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch market trends"
        )

@router.get(
    "/demand-forecast/{crop_type}",
    response_model=DemandForecast,
    summary="Get demand forecast",
    description="Get demand forecast for a specific crop"
)
async def get_demand_forecast(
    crop_type: str,
    current_user: dict = Depends(get_current_user)
):
    """Get demand forecast for a crop."""
    log_request(logger, "GET", f"/api/market-data/demand-forecast/{crop_type}", str(current_user["id"]))
    
    try:
        return generate_mock_demand_forecast(crop_type)
        
    except Exception as e:
        log_error(logger, e, "Get demand forecast")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch demand forecast"
        )

def generate_mock_market_data(crop_type: str) -> MarketData:
    """Generate realistic mock market data."""
    base_prices = {
        "wheat": 250,
        "rice": 350,
        "corn": 175,
        "cotton": 1200,
        "sugarcane": 35
    }
    
    base_price = base_prices.get(crop_type.lower(), 200)
    current_price = base_price * (1 + np.random.normal(0, 0.05))
    
    return MarketData(
        crop_type=crop_type,
        current_price=current_price,
        currency="USD",
        unit="ton",
        price_change=current_price - base_price,
        price_change_percentage=((current_price - base_price) / base_price) * 100,
        volume=int(np.random.normal(1000, 200)),
        market_cap=current_price * 1000,
        updated_at=datetime.now()
    )

def generate_mock_price_history(crop_type: str, days: int) -> PriceHistory:
    """Generate mock historical price data."""
    base_price = 250  # Base price in USD
    prices = []
    volumes = []
    dates = []
    
    current_date = datetime.now()
    
    for day in range(days):
        date = current_date - timedelta(days=day)
        price = base_price * (1 + np.random.normal(0, 0.02))
        volume = int(np.random.normal(1000, 100))
        
        prices.append(price)
        volumes.append(volume)
        dates.append(date.strftime("%Y-%m-%d"))
    
    return PriceHistory(
        crop_type=crop_type,
        prices=prices,
        volumes=volumes,
        dates=dates,
        currency="USD",
        unit="ton"
    )

def generate_mock_market_trends(crop_type: str) -> MarketTrends:
    """Generate mock market trends data."""
    return MarketTrends(
        crop_type=crop_type,
        price_trend="increasing" if np.random.random() > 0.5 else "decreasing",
        demand_trend="stable",
        supply_status="adequate",
        market_sentiment="positive",
        price_volatility="low",
        trading_volume_trend="increasing",
        seasonal_factors=[
            "Harvest season approaching",
            "Weather conditions favorable",
            "Export demand stable"
        ],
        key_influences=[
            "Global supply chains stable",
            "Regional weather patterns",
            "Government policies supportive"
        ]
    )

def generate_mock_demand_forecast(crop_type: str) -> DemandForecast:
    """Generate mock demand forecast data."""
    base_demand = 1000  # Base demand in tons
    forecasts = []
    
    for month in range(6):
        # Add some seasonality and trend
        seasonal_factor = 1 + 0.1 * np.sin(2 * np.pi * month / 12)
        trend_factor = 1 + 0.02 * month
        noise = np.random.normal(0, 0.05)
        
        forecast = base_demand * seasonal_factor * trend_factor * (1 + noise)
        
        forecasts.append({
            "month": (datetime.now() + timedelta(days=30 * month)).strftime("%B"),
            "demand": int(forecast),
            "confidence": 0.9 - (0.05 * month)  # Confidence decreases with time
        })
    
    return DemandForecast(
        crop_type=crop_type,
        current_demand=base_demand,
        forecasted_demand=forecasts,
        factors_affecting_demand=[
            "Seasonal consumption patterns",
            "Export market demand",
            "Processing industry requirements"
        ],
        confidence_level=0.85,
        unit="ton",
        updated_at=datetime.now()
    )