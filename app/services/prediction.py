"""
Prediction service for managing prediction records
"""
from typing import Dict, Any, Optional
from datetime import datetime

from ..models.schemas import PredictionType
from ..database import DatabaseManager

# Initialize database
db = DatabaseManager()

async def create_prediction_record(
    user_id: str,
    prediction_type: PredictionType,
    result: Dict[str, Any],
    confidence: float,
    input_data: Dict[str, Any],
    location: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """Create a prediction record in the database"""
    prediction_data = {
        "user_id": user_id,
        "prediction_type": prediction_type.value,
        "result": result,
        "confidence": confidence,
        "input_data": input_data,
        "location": location,
        "created_at": datetime.utcnow().isoformat()
    }
    
    return await db.save_prediction(prediction_data)

async def get_latest_predictions(user_id: str) -> Dict[str, Any]:
    """Get latest predictions for each type for a user"""
    predictions = await db.get_user_predictions(user_id)
    
    # Group predictions by type
    latest = {}
    for pred in predictions:
        pred_type = pred["prediction_type"]
        if pred_type not in latest or pred["created_at"] > latest[pred_type]["created_at"]:
            latest[pred_type] = pred
            
    return {
        "soil": latest.get(PredictionType.SOIL.value, {}).get("result", {}),
        "rainfall": latest.get(PredictionType.RAINFALL.value, {}).get("result", {}),
        "pests": [p["result"] for p in predictions if p["prediction_type"] == PredictionType.PEST.value][-5:],
        "yields": [p["result"] for p in predictions if p["prediction_type"] == PredictionType.CROP_YIELD.value][-5:]
    }