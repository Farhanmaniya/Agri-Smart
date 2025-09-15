"""
Pydantic models and schemas for AgriSmart API.
Fixed for Pydantic v2 compatibility.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import re
from uuid import UUID

# All enums and classes from before...

# Add the missing CropYieldPrediction class
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

# Add CropAnalytics class
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