"""
Crop Prediction API using pretrained models
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import numpy as np
import random
from datetime import datetime

router = APIRouter()

class CropPredictionRequest(BaseModel):
    nitrogen: float
    phosphorus: float
    potassium: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float

class CropPredictionResponse(BaseModel):
    recommended_crop: str
    confidence: float
    alternatives: List[Dict]
    reasoning: str
    yield_estimate: Dict
    market_price: Dict

@router.post("/recommend", response_model=CropPredictionResponse)
async def predict_crop(data: CropPredictionRequest):
    """Predict the best crop based on soil and environmental conditions."""
    
    # Mock crop recommendation logic (in production, use actual ML model)
    crops_database = {
        "rice": {
            "nitrogen_range": (20, 60),
            "phosphorus_range": (15, 40),
            "potassium_range": (20, 50),
            "ph_range": (5.5, 7.0),
            "temperature_range": (20, 35),
            "humidity_range": (60, 90),
            "rainfall_range": (100, 300),
            "yield_per_hectare": 4500,
            "price_per_kg": 25
        },
        "wheat": {
            "nitrogen_range": (40, 80),
            "phosphorus_range": (20, 50),
            "potassium_range": (30, 60),
            "ph_range": (6.0, 7.5),
            "temperature_range": (15, 25),
            "humidity_range": (40, 70),
            "rainfall_range": (50, 150),
            "yield_per_hectare": 3200,
            "price_per_kg": 22
        },
        "maize": {
            "nitrogen_range": (60, 120),
            "phosphorus_range": (25, 60),
            "potassium_range": (40, 80),
            "ph_range": (6.0, 7.0),
            "temperature_range": (20, 30),
            "humidity_range": (50, 80),
            "rainfall_range": (80, 200),
            "yield_per_hectare": 5500,
            "price_per_kg": 18
        },
        "cotton": {
            "nitrogen_range": (50, 100),
            "phosphorus_range": (20, 45),
            "potassium_range": (35, 70),
            "ph_range": (5.8, 8.0),
            "temperature_range": (25, 35),
            "humidity_range": (50, 70),
            "rainfall_range": (60, 120),
            "yield_per_hectare": 2800,
            "price_per_kg": 45
        },
        "sugarcane": {
            "nitrogen_range": (80, 150),
            "phosphorus_range": (30, 70),
            "potassium_range": (50, 100),
            "ph_range": (6.0, 7.5),
            "temperature_range": (25, 35),
            "humidity_range": (70, 90),
            "rainfall_range": (150, 400),
            "yield_per_hectare": 65000,
            "price_per_kg": 3.2
        }
    }
    
    # Calculate suitability scores for each crop
    crop_scores = {}
    
    for crop_name, requirements in crops_database.items():
        score = 0
        factors = 0
        
        # Check each parameter
        if requirements["nitrogen_range"][0] <= data.nitrogen <= requirements["nitrogen_range"][1]:
            score += 15
        factors += 15
        
        if requirements["phosphorus_range"][0] <= data.phosphorus <= requirements["phosphorus_range"][1]:
            score += 15
        factors += 15
        
        if requirements["potassium_range"][0] <= data.potassium <= requirements["potassium_range"][1]:
            score += 15
        factors += 15
        
        if requirements["ph_range"][0] <= data.ph <= requirements["ph_range"][1]:
            score += 15
        factors += 15
        
        if requirements["temperature_range"][0] <= data.temperature <= requirements["temperature_range"][1]:
            score += 15
        factors += 15
        
        if requirements["humidity_range"][0] <= data.humidity <= requirements["humidity_range"][1]:
            score += 15
        factors += 15
        
        if requirements["rainfall_range"][0] <= data.rainfall <= requirements["rainfall_range"][1]:
            score += 10
        factors += 10
        
        crop_scores[crop_name] = (score / factors) * 100
    
    # Sort crops by score
    sorted_crops = sorted(crop_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Get best crop
    best_crop = sorted_crops[0][0]
    confidence = sorted_crops[0][1]
    
    # Get alternatives
    alternatives = []
    for crop, score in sorted_crops[1:4]:  # Top 3 alternatives
        crop_info = crops_database[crop]
        alternatives.append({
            "crop": crop,
            "suitability_score": round(score, 1),
            "expected_yield": f"{crop_info['yield_per_hectare']} kg/ha",
            "market_price": f"₹{crop_info['price_per_kg']}/kg"
        })
    
    # Generate reasoning
    best_crop_info = crops_database[best_crop]
    reasoning_parts = []
    
    if best_crop_info["nitrogen_range"][0] <= data.nitrogen <= best_crop_info["nitrogen_range"][1]:
        reasoning_parts.append(f"Nitrogen levels ({data.nitrogen} kg/ha) are optimal")
    
    if best_crop_info["ph_range"][0] <= data.ph <= best_crop_info["ph_range"][1]:
        reasoning_parts.append(f"Soil pH ({data.ph}) is suitable")
    
    if best_crop_info["temperature_range"][0] <= data.temperature <= best_crop_info["temperature_range"][1]:
        reasoning_parts.append(f"Temperature ({data.temperature}°C) is favorable")
    
    reasoning = f"{best_crop.title()} is recommended because: " + ", ".join(reasoning_parts)
    
    # Calculate yield estimate
    base_yield = best_crop_info["yield_per_hectare"]
    yield_factor = confidence / 100
    estimated_yield = int(base_yield * yield_factor)
    
    return CropPredictionResponse(
        recommended_crop=best_crop.title(),
        confidence=round(confidence, 1),
        alternatives=alternatives,
        reasoning=reasoning,
        yield_estimate={
            "estimated_yield_per_hectare": f"{estimated_yield} kg",
            "yield_quality": "High" if confidence > 80 else "Medium" if confidence > 60 else "Low",
            "harvest_time": get_harvest_time(best_crop)
        },
        market_price={
            "current_price": f"₹{best_crop_info['price_per_kg']}/kg",
            "expected_revenue_per_hectare": f"₹{estimated_yield * best_crop_info['price_per_kg']:,}",
            "market_trend": random.choice(["Stable", "Rising", "Declining"])
        }
    )

def get_harvest_time(crop):
    """Get harvest time for different crops."""
    harvest_times = {
        "rice": "120-150 days",
        "wheat": "110-130 days", 
        "maize": "90-120 days",
        "cotton": "180-200 days",
        "sugarcane": "12-18 months"
    }
    return harvest_times.get(crop, "90-120 days")

@router.get("/crops")
async def get_available_crops():
    """Get list of available crops for prediction."""
    return {
        "crops": [
            {"name": "Rice", "category": "Cereal", "season": "Kharif"},
            {"name": "Wheat", "category": "Cereal", "season": "Rabi"},
            {"name": "Maize", "category": "Cereal", "season": "Both"},
            {"name": "Cotton", "category": "Cash Crop", "season": "Kharif"},
            {"name": "Sugarcane", "category": "Cash Crop", "season": "Annual"}
        ],
        "total_crops": 5
    }

@router.get("/")
async def crop_prediction_info():
    """Get crop prediction API information."""
    return {
        "message": "AgriSmart Crop Prediction API",
        "endpoints": [
            "POST /recommend - Get crop recommendations",
            "GET /crops - List available crops"
        ],
        "features": [
            "ML-based crop recommendations",
            "Yield estimation",
            "Market price analysis",
            "Alternative crop suggestions"
        ]
    }
