"""
Market price data API routes for AgriSmart backend.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta
import logging
from typing import List, Dict
import numpy as np

from app.utils.security import get_current_user
from app.utils.logging import log_request, log_error
from app.database import supabase

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get(
    "/prices",
    response_model=Dict,
    summary="Get current market prices",
    description="Get current and historical market prices for agricultural products"
)
async def get_market_prices(current_user: dict = Depends(get_current_user)):
    """Get current market prices and trends."""
    try:
        # In production, this would fetch from a market price API
        # For now, generating realistic mock data
        crops = ["wheat", "rice", "corn", "cotton", "sugarcane"]
        current_date = datetime.now()
        
        # Generate price data for each crop
        price_data = {}
        for crop in crops:
            # Base price for each crop
            base_prices = {
                "wheat": 250,
                "rice": 300,
                "corn": 180,
                "cotton": 450,
                "sugarcane": 200
            }
            
            # Generate historical prices for the last 30 days
            history = []
            base_price = base_prices[crop]
            
            for i in range(30):
                date = current_date - timedelta(days=i)
                # Add some random variation to prices
                price = base_price + np.random.normal(0, base_price * 0.05)
                history.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "price": round(price, 2)
                })
            
            # Calculate trends and statistics
            current_price = history[0]["price"]
            week_ago_price = history[7]["price"]
            month_ago_price = history[-1]["price"]
            
            price_data[crop] = {
                "current_price": current_price,
                "currency": "USD",
                "unit": "per quintal",
                "change_24h": round((current_price - history[1]["price"]) / history[1]["price"] * 100, 2),
                "change_7d": round((current_price - week_ago_price) / week_ago_price * 100, 2),
                "change_30d": round((current_price - month_ago_price) / month_ago_price * 100, 2),
                "history": history,
                "forecast": {
                    "next_week": round(current_price * (1 + np.random.normal(0.02, 0.01)), 2),
                    "next_month": round(current_price * (1 + np.random.normal(0.05, 0.02)), 2)
                },
                "market_analysis": generate_market_analysis(crop, current_price, history)
            }
        
        return {
            "prices": price_data,
            "last_updated": current_date.isoformat(),
            "market_summary": "Market shows stable prices with slight upward trend",
            "recommendations": generate_market_recommendations(price_data)
        }
        
    except Exception as e:
        logger.error(f"Error fetching market prices: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch market prices"
        )

def generate_market_analysis(crop: str, current_price: float, history: List[Dict]) -> str:
    """Generate market analysis based on price history."""
    week_trend = current_price - history[7]["price"]
    month_trend = current_price - history[-1]["price"]
    
    if week_trend > 0 and month_trend > 0:
        return f"{crop.title()} prices show strong upward trend. Consider holding for better prices."
    elif week_trend > 0 and month_trend < 0:
        return f"{crop.title()} prices recovering from monthly lows. Monitor market closely."
    elif week_trend < 0 and month_trend > 0:
        return f"{crop.title()} prices showing short-term weakness despite monthly gains."
    else:
        return f"{crop.title()} prices under pressure. Consider hedging strategies."

def generate_market_recommendations(price_data: Dict) -> List[str]:
    """Generate market recommendations based on price data."""
    recommendations = []
    
    # Analyze price trends and generate recommendations
    for crop, data in price_data.items():
        if data["change_7d"] > 5:
            recommendations.append(f"Consider selling {crop} - prices up {data['change_7d']}% this week")
        elif data["change_7d"] < -5:
            recommendations.append(f"Hold {crop} if possible - prices down {abs(data['change_7d'])}% this week")
        
        if data["forecast"]["next_month"] > data["current_price"] * 1.1:
            recommendations.append(f"Strong positive outlook for {crop} in the coming month")
    
    return recommendations