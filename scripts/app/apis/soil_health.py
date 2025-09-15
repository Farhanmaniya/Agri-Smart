"""
Soil health monitoring API routes for AgriSmart backend.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta
import logging
from typing import List
import numpy as np

from app.models.schemas import EnhancedSoilData
from app.utils.security import get_current_user
from app.utils.logging import log_request, log_error
from app.services.ml import ml_service
from app.database import supabase

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get(
    "/current",
    response_model=EnhancedSoilData,
    summary="Get current soil health data",
    description="Get comprehensive soil health analysis for user's farm"
)
async def get_soil_health(current_user: dict = Depends(get_current_user)):
    """Get current soil health data for user's farm."""
    try:
        # In production, this would come from soil sensors or recent soil tests
        # For now, generating realistic mock data
        mock_data = EnhancedSoilData(
            nitrogen=45.0 + np.random.normal(0, 5),
            phosphorus=25.0 + np.random.normal(0, 3),
            potassium=30.0 + np.random.normal(0, 4),
            ph=6.8 + np.random.normal(0, 0.2),
            ec=1.2 + np.random.normal(0, 0.1),
            organic_matter=3.5 + np.random.normal(0, 0.3),
            moisture=35.0 + np.random.normal(0, 5),
            sulfur=15.0 + np.random.normal(0, 2),
            copper=1.5 + np.random.normal(0, 0.2),
            iron=85.0 + np.random.normal(0, 10),
            manganese=20.0 + np.random.normal(0, 3),
            zinc=2.5 + np.random.normal(0, 0.3),
            boron=0.8 + np.random.normal(0, 0.1),
            texture="Loamy",
            drainage="Good",
            depth=30.0
        )
        
        # Get soil type prediction using ML model
        soil_features = {
            "nitrogen": mock_data.nitrogen,
            "phosphorus": mock_data.phosphorus,
            "potassium": mock_data.potassium,
            "ph": mock_data.ph,
            "moisture": mock_data.moisture
        }
        
        # Store the soil health record
        record = {
            "user_id": current_user["id"],
            "timestamp": datetime.now().isoformat(),
            "soil_data": mock_data.dict(),
            "recommendations": get_soil_recommendations(mock_data)
        }
        
        supabase.table("soil_health_records").insert(record).execute()
        
        return mock_data
        
    except Exception as e:
        logger.error(f"Error fetching soil health data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch soil health data"
        )

def get_soil_recommendations(soil_data: EnhancedSoilData) -> List[str]:
    """Generate recommendations based on soil health data."""
    recommendations = []
    
    # pH recommendations
    if soil_data.ph < 6.0:
        recommendations.append("Consider adding lime to increase soil pH")
    elif soil_data.ph > 7.5:
        recommendations.append("Consider adding sulfur to decrease soil pH")
        
    # Nutrient recommendations
    if soil_data.nitrogen < 40:
        recommendations.append("Low nitrogen levels. Add nitrogen-rich fertilizer")
    if soil_data.phosphorus < 20:
        recommendations.append("Low phosphorus levels. Add phosphate fertilizer")
    if soil_data.potassium < 25:
        recommendations.append("Low potassium levels. Add potash fertilizer")
        
    # Moisture recommendations
    if soil_data.moisture < 30:
        recommendations.append("Soil moisture is low. Increase irrigation")
    elif soil_data.moisture > 60:
        recommendations.append("Soil moisture is high. Reduce irrigation")
        
    return recommendations

@router.get(
    "/history",
    response_model=List[dict],
    summary="Get soil health history",
    description="Get historical soil health data for trend analysis"
)
async def get_soil_history(current_user: dict = Depends(get_current_user)):
    """Get historical soil health data."""
    try:
        # Generate mock historical data
        history = []
        current_date = datetime.now()
        
        for i in range(30):  # Last 30 days
            date = current_date - timedelta(days=i)
            history.append({
                "date": date.isoformat(),
                "nitrogen": 45.0 + np.random.normal(0, 3),
                "phosphorus": 25.0 + np.random.normal(0, 2),
                "potassium": 30.0 + np.random.normal(0, 2),
                "ph": 6.8 + np.random.normal(0, 0.1),
                "moisture": 35.0 + np.random.normal(0, 3)
            })
            
        return history
        
    except Exception as e:
        logger.error(f"Error fetching soil history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch soil history"
        )