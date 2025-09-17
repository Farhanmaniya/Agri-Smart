"""
Simple Soil Health API for AgriSmart demo
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import random
import numpy as np

router = APIRouter()

class SoilAnalysisRequest(BaseModel):
    nitrogen: float
    phosphorus: float
    potassium: float
    ph: float
    organic_matter: Optional[float] = None
    moisture: Optional[float] = None
    location: Optional[str] = None

class SoilHealthResponse(BaseModel):
    soil_health_score: float
    classification: str
    nutrient_levels: Dict[str, Dict[str, str]]
    recommendations: List[str]
    deficiencies: List[str]
    improvements: List[str]
    next_test_date: str

@router.post("/analyze")
async def analyze_soil_health(soil_data: SoilAnalysisRequest):
    """Analyze soil health based on nutrient levels."""
    
    try:
        # Calculate soil health score
        score = calculate_soil_health_score(soil_data)
        
        # Determine classification
        classification = get_soil_classification(score)
        
        # Analyze nutrient levels
        nutrient_levels = analyze_nutrients(soil_data)
        
        # Generate recommendations
        recommendations = generate_recommendations(soil_data, score)
        
        # Identify deficiencies
        deficiencies = identify_deficiencies(soil_data)
        
        # Suggest improvements
        improvements = suggest_improvements(soil_data, score)
        
        return SoilHealthResponse(
            soil_health_score=round(score, 1),
            classification=classification,
            nutrient_levels=nutrient_levels,
            recommendations=recommendations,
            deficiencies=deficiencies,
            improvements=improvements,
            next_test_date="2025-03-17"  # 6 months from now
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Soil analysis failed: {str(e)}")

def calculate_soil_health_score(soil_data: SoilAnalysisRequest) -> float:
    """Calculate overall soil health score (0-100)."""
    
    # Optimal ranges for different nutrients
    optimal_ranges = {
        'nitrogen': (40, 80),
        'phosphorus': (20, 50),
        'potassium': (30, 70),
        'ph': (6.0, 7.5)
    }
    
    scores = []
    
    # Score each nutrient
    for nutrient, (min_val, max_val) in optimal_ranges.items():
        value = getattr(soil_data, nutrient)
        
        if min_val <= value <= max_val:
            nutrient_score = 100
        elif value < min_val:
            # Below optimal - score decreases as it gets further from range
            nutrient_score = max(0, 100 - (min_val - value) * 2)
        else:
            # Above optimal - score decreases as it gets further from range
            nutrient_score = max(0, 100 - (value - max_val) * 2)
        
        scores.append(nutrient_score)
    
    # Add bonus for organic matter if provided
    if soil_data.organic_matter:
        if soil_data.organic_matter >= 3.0:
            scores.append(100)
        else:
            scores.append(soil_data.organic_matter * 33.33)  # Scale to 100
    
    # Add bonus for moisture if provided
    if soil_data.moisture:
        if 25 <= soil_data.moisture <= 45:
            scores.append(100)
        else:
            scores.append(max(0, 100 - abs(35 - soil_data.moisture) * 2))
    
    return sum(scores) / len(scores)

def get_soil_classification(score: float) -> str:
    """Get soil health classification based on score."""
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 55:
        return "Fair"
    elif score >= 40:
        return "Poor"
    else:
        return "Very Poor"

def analyze_nutrients(soil_data: SoilAnalysisRequest) -> Dict[str, Dict[str, str]]:
    """Analyze individual nutrient levels."""
    
    def get_level_status(value: float, low: float, high: float) -> str:
        if value < low:
            return "Low"
        elif value > high:
            return "High"
        else:
            return "Optimal"
    
    return {
        "nitrogen": {
            "value": f"{soil_data.nitrogen} kg/ha",
            "status": get_level_status(soil_data.nitrogen, 40, 80),
            "recommendation": "Apply nitrogen fertilizer" if soil_data.nitrogen < 40 else "Maintain current levels"
        },
        "phosphorus": {
            "value": f"{soil_data.phosphorus} kg/ha",
            "status": get_level_status(soil_data.phosphorus, 20, 50),
            "recommendation": "Add phosphorus supplement" if soil_data.phosphorus < 20 else "Good levels"
        },
        "potassium": {
            "value": f"{soil_data.potassium} kg/ha",
            "status": get_level_status(soil_data.potassium, 30, 70),
            "recommendation": "Apply potash fertilizer" if soil_data.potassium < 30 else "Adequate levels"
        },
        "ph": {
            "value": f"{soil_data.ph}",
            "status": get_level_status(soil_data.ph, 6.0, 7.5),
            "recommendation": "Apply lime to increase pH" if soil_data.ph < 6.0 else "Good pH balance"
        }
    }

def generate_recommendations(soil_data: SoilAnalysisRequest, score: float) -> List[str]:
    """Generate soil health recommendations."""
    recommendations = []
    
    if soil_data.nitrogen < 40:
        recommendations.append("Apply 60-80 kg/ha of nitrogen fertilizer before planting")
    
    if soil_data.phosphorus < 20:
        recommendations.append("Add 40-50 kg/ha of phosphorus supplement")
    
    if soil_data.potassium < 30:
        recommendations.append("Apply 50-60 kg/ha of potash fertilizer")
    
    if soil_data.ph < 6.0:
        recommendations.append("Apply agricultural lime to raise soil pH to 6.5-7.0")
    elif soil_data.ph > 7.5:
        recommendations.append("Add sulfur or organic matter to lower pH")
    
    if score < 70:
        recommendations.append("Incorporate organic compost to improve soil structure")
        recommendations.append("Consider crop rotation to enhance soil health")
    
    if not recommendations:
        recommendations.append("Maintain current soil management practices")
        recommendations.append("Regular monitoring every 6 months recommended")
    
    return recommendations

def identify_deficiencies(soil_data: SoilAnalysisRequest) -> List[str]:
    """Identify nutrient deficiencies."""
    deficiencies = []
    
    if soil_data.nitrogen < 30:
        deficiencies.append("Severe nitrogen deficiency - immediate attention needed")
    elif soil_data.nitrogen < 40:
        deficiencies.append("Moderate nitrogen deficiency")
    
    if soil_data.phosphorus < 15:
        deficiencies.append("Phosphorus deficiency affecting root development")
    
    if soil_data.potassium < 25:
        deficiencies.append("Potassium deficiency - may affect disease resistance")
    
    if soil_data.ph < 5.5:
        deficiencies.append("Acidic soil limiting nutrient availability")
    
    if not deficiencies:
        deficiencies.append("No major nutrient deficiencies detected")
    
    return deficiencies

def suggest_improvements(soil_data: SoilAnalysisRequest, score: float) -> List[str]:
    """Suggest soil improvement strategies."""
    improvements = []
    
    if score < 60:
        improvements.extend([
            "Add 2-3 tons/ha of well-decomposed farmyard manure",
            "Practice green manuring with leguminous crops",
            "Implement minimum tillage to preserve soil structure"
        ])
    
    if soil_data.organic_matter and soil_data.organic_matter < 2.5:
        improvements.append("Increase organic matter through compost application")
    
    improvements.extend([
        "Use cover crops during fallow periods",
        "Implement drip irrigation for water efficiency",
        "Regular soil testing every 6 months for monitoring"
    ])
    
    return improvements

@router.get("/")
async def get_soil_health_info():
    """Get general soil health information."""
    return {
        "message": "Soil Health Analysis API",
        "features": [
            "Comprehensive nutrient analysis",
            "Soil health scoring",
            "Personalized recommendations",
            "Deficiency identification"
        ],
        "supported_parameters": [
            "nitrogen", "phosphorus", "potassium", "ph", 
            "organic_matter", "moisture", "location"
        ]
    }
