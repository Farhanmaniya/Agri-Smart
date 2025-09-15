"""
Crop yield API routes for AgriSmart backend.
Handles crop yield predictions and analytics.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import numpy as np
from uuid import uuid4

from app.models.schemas import (
    CropYieldPrediction,
    YieldPredictionRequest,
    CropType,
    CropAnalytics
)
from app.utils.security import get_current_user
from app.utils.logging import log_request, log_error
from app.services.ml import ml_service
from app.database import supabase

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get(
    "/",
    response_model=dict,
    summary="Get crop yield predictions",
    description="Get yield predictions and analytics for user's crops"
)
async def get_crop_yield(current_user: dict = Depends(get_current_user)):
    """Get crop yield predictions for user."""
    log_request(logger, "GET", "/api/crop-yield", str(current_user["id"]))
    
    try:
        # Get user's crop types from profile
        user_crops = current_user.get("main_crops", "").split(",")
        if not user_crops:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No crops found in user profile"
            )

        # Generate mock yield data for each crop
        mock_yields = generate_mock_yield_data(user_crops)
        
        return {
            "yields": mock_yields,
            "summary": generate_yield_summary(mock_yields),
            "recommendations": generate_yield_recommendations(mock_yields)
        }

    except Exception as e:
        log_error(logger, e, "Get crop yield predictions")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch crop yield data"
        )

@router.post(
    "/predict",
    response_model=CropYieldPrediction,
    summary="Predict crop yield",
    description="Get detailed yield prediction for specific crop and conditions"
)
async def predict_crop_yield(
    request: YieldPredictionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Predict crop yield based on input parameters."""
    log_request(logger, "POST", "/api/crop-yield/predict", str(current_user["id"]))
    
    try:
        # In production, this would use the ML model
        # For now, generating realistic predictions
        prediction = generate_mock_yield_prediction(request)
        
        # Store the prediction
        record = {
            "user_id": current_user["id"],
            "prediction": prediction.dict(),
            "created_at": datetime.now().isoformat()
        }
        
        supabase.table("yield_predictions").insert(record).execute()
        
        return prediction
        
    except Exception as e:
        log_error(logger, e, "Generate yield prediction")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate yield prediction"
        )

@router.get(
    "/analytics",
    response_model=List[CropAnalytics],
    summary="Get crop analytics",
    description="Get detailed analytics for each crop"
)
async def get_crop_analytics(current_user: dict = Depends(get_current_user)):
    """Get detailed analytics for user's crops."""
    log_request(logger, "GET", "/api/crop-yield/analytics", str(current_user["id"]))
    
    try:
        user_crops = current_user.get("main_crops", "").split(",")
        analytics = []
        
        for crop in user_crops:
            analytics.append(
                CropAnalytics(
                    crop_type=crop,
                    total_area=100.0,  # Mock area in hectares
                    avg_yield=4.5,     # Mock yield in tons/hectare
                    disease_incidents=2,
                    pest_incidents=1,
                    irrigation_frequency=3.5,  # Times per week
                    recommended_frequency=4,
                    success_rate=85.0,
                    soil_suitability="Good"
                )
            )
            
        return analytics
        
    except Exception as e:
        log_error(logger, e, "Get crop analytics")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch crop analytics"
        )

def generate_mock_yield_data(crops: List[str]) -> List[Dict]:
    """Generate realistic mock yield data."""
    mock_data = []
    current_date = datetime.now()
    
    for month in range(12):
        date = current_date - timedelta(days=30 * month)
        month_data = {
            "month": date.strftime("%b"),
            "predicted": 4.5 + np.random.normal(0, 0.3),
            "actual": 4.2 + np.random.normal(0, 0.2),
            "crop": crops[0] if crops else "wheat"  # Use first crop or default to wheat
        }
        mock_data.append(month_data)
    
    return mock_data

def generate_yield_summary(yields: List[Dict]) -> Dict:
    """Generate summary statistics from yield data."""
    return {
        "average_yield": sum(y["actual"] for y in yields) / len(yields),
        "trend": "increasing" if yields[0]["actual"] > yields[-1]["actual"] else "decreasing",
        "accuracy": 92.5,  # Mock accuracy percentage
        "year_to_date": sum(y["actual"] for y in yields[:datetime.now().month])
    }

def generate_yield_recommendations(yields: List[Dict]) -> List[str]:
    """Generate recommendations based on yield data."""
    recommendations = [
        "Maintain current irrigation schedule for optimal yield",
        "Consider increasing nitrogen application during flowering stage",
        "Monitor soil moisture levels closely during the next growth phase"
    ]
    return recommendations

def generate_mock_yield_prediction(request: YieldPredictionRequest) -> CropYieldPrediction:
    """Generate a realistic mock yield prediction."""
    base_yield = {
        "wheat": 4.5,
        "rice": 5.0,
        "corn": 6.0,
        "cotton": 2.5,
        "sugarcane": 70.0
    }.get(request.crop_type.value, 4.0)
    
    # Add some realistic variations based on input parameters
    moisture_factor = 1.0 + (request.soil_data.get("moisture", 50) - 50) * 0.002
    temperature_factor = 1.0 - abs(request.temperature - 25) * 0.01
    rainfall_factor = 1.0 + (request.rainfall - 100) * 0.001
    
    predicted_yield = base_yield * moisture_factor * temperature_factor * rainfall_factor
    
    return CropYieldPrediction(
        id=uuid4(),
        user_id=uuid4(),  # This would normally come from the current user
        crop_type=request.crop_type,
        predicted_yield=predicted_yield,
        confidence=0.85 + np.random.normal(0, 0.05),
        area=request.area,
        input_parameters={
            "rainfall": request.rainfall,
            "temperature": request.temperature,
            "soil_data": request.soil_data
        },
        recommendations=[
            "Optimal planting time based on current conditions",
            "Recommended fertilizer application schedule",
            "Irrigation recommendations based on rainfall forecast"
        ],
        historical_yields=[base_yield * (1 + np.random.normal(0, 0.1)) for _ in range(5)],
        seasonal_factors={
            "rainfall_adequacy": "optimal",
            "temperature_stress": "low",
            "pest_risk": "medium"
        },
        created_at=datetime.now()
    )