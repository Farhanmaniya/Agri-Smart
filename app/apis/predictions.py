"""
Prediction API endpoints for AgriSmart
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import Dict, Any
import logging

from ..models.schemas import (
    UserResponse,
    PestPredictionRequest,
    RainfallPredictionRequest,
    SoilTypePredictionRequest,
    PredictionResponse,
    PredictionType
)
from ..services.auth import get_current_user
from ..services.ml import MLModelManager
from ..services.prediction import create_prediction_record

logger = logging.getLogger(__name__)
router = APIRouter()
model_manager = MLModelManager()

@router.post("/pest", response_model=PredictionResponse)
async def predict_pest(
    image: UploadFile = File(...),
    data: PestPredictionRequest = Depends(),
    current_user: UserResponse = Depends(get_current_user)
):
    """Predict pest from image"""
    try:
        # Process image and make prediction
        prediction = await model_manager.predict_pest(image, data.crop_type)
        
        # Save prediction to database
        prediction_record = await create_prediction_record(
            user_id=current_user.id,
            prediction_type=PredictionType.PEST,
            result=prediction,
            location=data.location,
            input_data={"image_url": data.image_url, "crop_type": data.crop_type}
        )
        
        return prediction_record
    except Exception as e:
        logger.error(f"Error in pest prediction: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing pest prediction"
        )

@router.post("/rainfall", response_model=PredictionResponse)
async def predict_rainfall(
    data: RainfallPredictionRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Predict rainfall based on weather parameters"""
    try:
        # Make rainfall prediction
        prediction = await model_manager.predict_rainfall(
            temperature=data.temperature,
            humidity=data.humidity,
            pressure=data.pressure,
            wind_speed=data.wind_speed,
            cloud_cover=data.cloud_cover
        )
        
        # Save prediction to database
        prediction_record = await create_prediction_record(
            user_id=current_user.id,
            prediction_type=PredictionType.RAINFALL,
            result=prediction,
            location=data.location,
            input_data=data.dict(exclude={"user_id", "location", "timestamp"})
        )
        
        return prediction_record
    except Exception as e:
        logger.error(f"Error in rainfall prediction: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing rainfall prediction"
        )

@router.post("/soil", response_model=PredictionResponse)
async def predict_soil_health(
    data: SoilTypePredictionRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Predict soil health based on NPK values"""
    try:
        # Make soil prediction
        prediction = await model_manager.predict_soil_health(
            nitrogen=data.nitrogen,
            phosphorus=data.phosphorus,
            potassium=data.potassium,
            ph=data.ph,
            moisture=data.moisture
        )
        
        # Save prediction to database
        prediction_record = await create_prediction_record(
            user_id=current_user.id,
            prediction_type=PredictionType.SOIL,
            result=prediction,
            location=data.location,
            input_data=data.dict(exclude={"user_id", "location", "timestamp"})
        )
        
        return prediction_record
    except Exception as e:
        logger.error(f"Error in soil prediction: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing soil prediction"
        )