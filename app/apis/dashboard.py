"""
Dashboard API endpoints for AgriSmart
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
import logging

from ..models.schemas import UserResponse
from ..services.auth import get_current_user
from ..services.prediction import get_latest_predictions, get_farm_analytics
from ..services.irrigation import get_irrigation_status

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/analytics")
async def get_dashboard_analytics(current_user: UserResponse = Depends(get_current_user)) -> Dict[str, Any]:
    """Get market and profitability analytics"""
    try:
        analytics = await get_farm_analytics(current_user.id)
        return {
            "marketData": analytics.get("market_data", []),
            "profitableCrops": analytics.get("profitable_crops", [])
        }
    
    except Exception as e:
        logger.error(f"Error getting dashboard analytics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching dashboard analytics"
        )

@router.get("/stats")
async def get_dashboard_stats(current_user: UserResponse = Depends(get_current_user)) -> Dict[str, Any]:
    """Get quick stats for the dashboard"""
    try:
        stats = [
            {
                "title": "Soil Health Index",
                "value": "85",
                "change": "+5%",
                "trend": "up",
                "color": "var(--color-success)"
            },
            {
                "title": "Water Efficiency",
                "value": "92%",
                "change": "+2%",
                "trend": "up",
                "color": "var(--color-primary)"
            },
            {
                "title": "Pest Risk",
                "value": "Low",
                "change": "-10%",
                "trend": "down",
                "color": "var(--color-success)"
            }
        ]
        
        trend_data = [
            {"day": "Mon", "value": 82},
            {"day": "Tue", "value": 85},
            {"day": "Wed", "value": 83},
            {"day": "Thu", "value": 86},
            {"day": "Fri", "value": 85}
        ]
        
        return {
            "stats": stats,
            "trendData": trend_data
        }
    
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching dashboard stats"
        )

@router.get("/overview")
async def get_dashboard_overview(current_user: UserResponse = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get overview data for dashboard including:
    - Recent soil health data
    - Active alerts
    - Weather forecast
    - Crop yield predictions
    """
    try:
        # Get latest predictions
        predictions = await get_latest_predictions(current_user.id)
        
        # Get soil health data
        soil_data = {
            "npk": {
                "nitrogen": predictions.get("soil", {}).get("nitrogen", 0),
                "phosphorus": predictions.get("soil", {}).get("phosphorus", 0),
                "potassium": predictions.get("soil", {}).get("potassium", 0)
            },
            "ph": predictions.get("soil", {}).get("ph", 0),
            "moisture": predictions.get("soil", {}).get("moisture", 0),
            "health_status": "Good" if all([
                45 <= predictions.get("soil", {}).get("nitrogen", 0) <= 75,
                35 <= predictions.get("soil", {}).get("phosphorus", 0) <= 65,
                35 <= predictions.get("soil", {}).get("potassium", 0) <= 65,
                6.0 <= predictions.get("soil", {}).get("ph", 0) <= 7.5,
                60 <= predictions.get("soil", {}).get("moisture", 0) <= 80
            ]) else "Needs Attention"
        }

        # Get alerts based on predictions and thresholds
        alerts = []
        if soil_data["health_status"] == "Needs Attention":
            if predictions.get("soil", {}).get("nitrogen", 0) < 45:
                alerts.append({
                    "type": "warning",
                    "message": "Low nitrogen levels detected",
                    "timestamp": predictions.get("soil", {}).get("timestamp")
                })
            if predictions.get("soil", {}).get("moisture", 0) < 60:
                alerts.append({
                    "type": "warning",
                    "message": "Low soil moisture detected",
                    "timestamp": predictions.get("soil", {}).get("timestamp")
                })

        # Get irrigation status
        irrigation_status = await get_irrigation_status(current_user.id)
        
        return {
            "soil": soil_data,
            "alerts": alerts,
            "irrigation": irrigation_status,
            "predictions": {
                "rainfall": predictions.get("rainfall", {}),
                "pests": predictions.get("pests", []),
                "yields": predictions.get("yields", [])
            }
        }

    except Exception as e:
        logger.error(f"Error getting dashboard overview: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching dashboard data"
        )