# app/models/__init__.py
"""
Pydantic models for AgriSmart API
"""

from .ml_schemas import (
    PredictionType,
    CropType,
    PredictionRequest,
    CropYieldPrediction,
    CropAnalytics,
    YieldPredictionRequest,
    PestPredictionRequest,
    RainfallPredictionRequest,
    SoilTypePredictionRequest,
    PredictionResponse
)

__all__ = [
    'PredictionType',
    'CropType',
    'PredictionRequest',
    'CropYieldPrediction',
    'CropAnalytics',
    'YieldPredictionRequest',
    'PestPredictionRequest',
    'RainfallPredictionRequest',
    'SoilTypePredictionRequest',
    'PredictionResponse'
]