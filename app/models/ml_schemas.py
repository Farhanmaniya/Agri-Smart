"""
Machine Learning schemas for AgriSmart backend.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from uuid import UUID

class PredictionType(str, Enum):
    """Supported prediction types."""
    YIELD = "yield"
    DISEASE = "disease"
    PEST = "pest"
    CROP_RECOMMENDATION = "crop_recommendation"
    RAINFALL = "rainfall"
    SOIL_TYPE = "soil_type"

class CropType(str, Enum):
    """Supported crop types."""
    WHEAT = "wheat"
    RICE = "rice"
    CORN = "corn"
    COTTON = "cotton"
    SUGARCANE = "sugarcane"
    TOMATO = "tomato"
    POTATO = "potato"
    ONION = "onion"
    MAIZE = "maize"
    BARLEY = "barley"
    SOYBEAN = "soybean"
    CHICKPEA = "chickpea"
    LENTIL = "lentil"
    GROUNDNUT = "groundnut"

# Base Models
class PredictionRequest(BaseModel):
    """Base prediction request model."""
    area: float = Field(..., ge=0, description="Area in hectares")
    prediction_type: Optional[PredictionType] = None

class CropYieldPrediction(BaseModel):
    """Crop yield prediction response model."""
    id: UUID
    user_id: UUID
    crop_type: CropType
    predicted_yield: float = Field(..., ge=0, description="Predicted yield in tons/hectare")
    confidence_score: float = Field(..., ge=0, le=1, description="Model confidence score")
    prediction_date: datetime = Field(default_factory=datetime.now)
    harvest_window: Dict[str, datetime] = Field(
        ...,
        description="Predicted harvest window with start and end dates"
    )
    factors: Dict[str, float] = Field(
        ...,
        description="Contributing factors and their importance scores"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recommendations for yield optimization"
    )
    historical_comparison: Optional[Dict[str, float]] = Field(
        None,
        description="Comparison with historical yields"
    )

class CropAnalytics(BaseModel):
    """Crop analytics response model."""
    crop_type: CropType
    total_area: float = Field(..., ge=0, description="Total area under cultivation in hectares")
    current_growth_stage: str
    health_index: float = Field(..., ge=0, le=100, description="Overall crop health index")
    stress_factors: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of identified stress factors"
    )
    growth_timeline: Dict[str, datetime] = Field(
        ...,
        description="Key growth stage dates"
    )
    yield_forecast: Optional[float] = Field(
        None,
        ge=0,
        description="Forecasted yield in tons/hectare"
    )
    recommendations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Action recommendations"
    )

class YieldPredictionRequest(PredictionRequest):
    """Yield prediction specific request."""
    prediction_type: PredictionType = PredictionType.YIELD
    crop_type: CropType
    rainfall: float = Field(..., ge=0)
    fertilizer_amount: float = Field(..., ge=0)
    temperature: float = Field(..., ge=-50, le=60)
    nitrogen: float = Field(..., ge=0)
    phosphorus: float = Field(..., ge=0)
    potassium: float = Field(..., ge=0)
    sowing_date: str
    soil_ph: float = Field(..., ge=0, le=14)

class PestPredictionRequest(PredictionRequest):
    """Pest prediction specific request."""
    prediction_type: PredictionType = PredictionType.PEST
    crop_type: CropType
    pest_description: str
    damage_level: str = Field(..., pattern=r"^(low|medium|high)$")
    treatment_history: Optional[List[str]] = []
    image_data: Optional[str] = Field(None, description="Base64 encoded image data")
    image_type: Optional[str] = Field(None, pattern=r"^(jpeg|jpg|png)$", description="Image file type")
    image_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional image metadata like resolution, capture time, etc."
    )

class RainfallPredictionRequest(BaseModel):
    """Rainfall prediction request model."""
    prediction_type: PredictionType = PredictionType.RAINFALL
    year: int = Field(2024, ge=2000, le=2030)
    subdivision: int = Field(1, ge=1, le=10)
    month: int = Field(..., ge=1, le=12)
    current_rainfall: float = Field(0.0, ge=0)
    location: Optional[str] = None
    elevation: Optional[float] = None
    historical_rainfall: Optional[List[float]] = None
    seasonal_pattern: Optional[str] = Field(
        None,
        pattern=r"^(monsoon|winter|summer|spring)$"
    )
    soil_moisture_percentage: Optional[float] = Field(None, ge=0, le=100)

class SoilTypePredictionRequest(BaseModel):
    """Soil type prediction request model."""
    prediction_type: PredictionType = PredictionType.SOIL_TYPE
    nitrogen: float = Field(..., ge=0)
    phosphorus: float = Field(..., ge=0)
    potassium: float = Field(..., ge=0)
    temperature: float = Field(..., ge=-50, le=60)
    moisture: float = Field(..., ge=0, le=100)
    humidity: float = Field(..., ge=0, le=100)
    location: Optional[str] = None
    depth: Optional[float] = Field(None, ge=0)
    texture: Optional[str] = None
    ph_level: Optional[float] = Field(None, ge=0, le=14)
    organic_matter: Optional[float] = Field(None, ge=0, le=100)
    electrical_conductivity: Optional[float] = Field(None, ge=0)

class PredictionResponse(BaseModel):
    """Generic prediction response model."""
    id: UUID
    user_id: UUID
    prediction_type: str
    crop_type: Optional[str] = None
    predictions: Dict[str, Any]
    confidence: float
    recommendations: Dict[str, Any]
    model_info: Optional[Dict[str, Any]] = {}
    created_at: datetime