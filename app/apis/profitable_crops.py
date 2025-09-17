"""
Profitable Crops API - Smart crop recommendation based on soil nutrients and profitability
"""

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
import logging
from typing import Dict, List, Optional
import numpy as np
from uuid import uuid4

from app.models.schemas import ErrorResponse
from app.utils.security import get_current_user
from app.utils.logging import log_request, log_error
from app.database import supabase

logger = logging.getLogger(__name__)
router = APIRouter()

# Crop data with nutrient requirements and market info
CROP_DATA = {
    "wheat": {
        "name": "Wheat",
        "nutrient_requirements": {"N": 120, "P": 60, "K": 40, "pH_min": 6.0, "pH_max": 7.5},
        "base_yield": 4.5,  # tons per hectare
        "market_price": 250,  # USD per ton
        "growing_season": 120,  # days
        "water_requirement": "medium"
    },
    "rice": {
        "name": "Rice", 
        "nutrient_requirements": {"N": 100, "P": 50, "K": 50, "pH_min": 5.5, "pH_max": 7.0},
        "base_yield": 5.0,
        "market_price": 350,
        "growing_season": 150,
        "water_requirement": "high"
    },
    "corn": {
        "name": "Corn",
        "nutrient_requirements": {"N": 150, "P": 70, "K": 60, "pH_min": 6.0, "pH_max": 7.0},
        "base_yield": 6.0,
        "market_price": 175,
        "growing_season": 100,
        "water_requirement": "medium"
    },
    "cotton": {
        "name": "Cotton",
        "nutrient_requirements": {"N": 80, "P": 40, "K": 80, "pH_min": 5.8, "pH_max": 8.0},
        "base_yield": 2.5,
        "market_price": 1200,
        "growing_season": 180,
        "water_requirement": "high"
    },
    "sugarcane": {
        "name": "Sugarcane",
        "nutrient_requirements": {"N": 200, "P": 80, "K": 160, "pH_min": 6.0, "pH_max": 7.5},
        "base_yield": 70.0,
        "market_price": 35,
        "growing_season": 365,
        "water_requirement": "very_high"
    },
    "soybean": {
        "name": "Soybean",
        "nutrient_requirements": {"N": 60, "P": 80, "K": 100, "pH_min": 6.0, "pH_max": 7.0},
        "base_yield": 3.0,
        "market_price": 400,
        "growing_season": 120,
        "water_requirement": "medium"
    }
}

FERTILIZER_PRICES = {
    "urea": 25,      # USD per 50kg bag (46% N)
    "dap": 35,       # USD per 50kg bag (46% P2O5, 18% N)
    "mop": 20,       # USD per 50kg bag (60% K2O)
    "organic": 15    # USD per 50kg bag
}

@router.post(
    "/predict",
    summary="Predict most profitable crops",
    description="Get ranked crop recommendations based on soil nutrients and profitability analysis"
)
async def predict_profitable_crops(
    soil_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Predict most profitable crops based on soil analysis."""
    log_request(logger, "POST", "/api/profitable-crops/predict", str(current_user["id"]))
    
    try:
        # Validate input data
        required_fields = ["nitrogen", "phosphorus", "potassium", "ph", "farm_size"]
        for field in required_fields:
            if field not in soil_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )
        
        # Extract soil parameters
        current_n = float(soil_data["nitrogen"])
        current_p = float(soil_data["phosphorus"]) 
        current_k = float(soil_data["potassium"])
        soil_ph = float(soil_data["ph"])
        farm_size = float(soil_data["farm_size"])
        
        # Analyze each crop
        crop_analyses = []
        
        for crop_id, crop_info in CROP_DATA.items():
            analysis = analyze_crop_profitability(
                crop_id, crop_info, current_n, current_p, current_k, soil_ph, farm_size
            )
            crop_analyses.append(analysis)
        
        # Sort by ROI (Return on Investment)
        crop_analyses.sort(key=lambda x: x["roi"], reverse=True)
        
        # Store prediction in database
        prediction_record = {
            "user_id": current_user["id"],
            "prediction_type": "profitable_crops",
            "crop_type": "multiple",
            "input_data": soil_data,
            "predictions": crop_analyses[:3],  # Top 3 crops
            "confidence": 0.85,
            "recommendations": generate_recommendations(crop_analyses[:3]),
            "created_at": datetime.now().isoformat()
        }
        
        supabase.table("predictions").insert(prediction_record).execute()
        
        return {
            "status": "success",
            "soil_analysis": {
                "nitrogen": current_n,
                "phosphorus": current_p,
                "potassium": current_k,
                "ph": soil_ph,
                "farm_size": farm_size
            },
            "top_crops": crop_analyses[:5],
            "summary": {
                "best_crop": crop_analyses[0]["crop_name"],
                "max_roi": crop_analyses[0]["roi"],
                "total_investment_needed": crop_analyses[0]["total_cost"],
                "expected_profit": crop_analyses[0]["net_profit"]
            },
            "recommendations": generate_recommendations(crop_analyses[:3])
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input data: {str(e)}"
        )
    except Exception as e:
        log_error(logger, e, "Predict profitable crops")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate crop profitability analysis"
        )

def analyze_crop_profitability(crop_id: str, crop_info: dict, current_n: float, 
                             current_p: float, current_k: float, soil_ph: float, farm_size: float) -> dict:
    """Analyze profitability for a specific crop."""
    
    # Check pH suitability
    ph_suitable = crop_info["nutrient_requirements"]["pH_min"] <= soil_ph <= crop_info["nutrient_requirements"]["pH_max"]
    ph_factor = 1.0 if ph_suitable else 0.7
    
    # Calculate nutrient deficiencies
    n_deficit = max(0, crop_info["nutrient_requirements"]["N"] - current_n)
    p_deficit = max(0, crop_info["nutrient_requirements"]["P"] - current_p)
    k_deficit = max(0, crop_info["nutrient_requirements"]["K"] - current_k)
    
    # Calculate fertilizer requirements (kg per hectare)
    urea_needed = n_deficit / 0.46  # Urea is 46% N
    dap_needed = p_deficit / 0.46   # DAP is 46% P2O5
    mop_needed = k_deficit / 0.60   # MOP is 60% K2O
    
    # Calculate fertilizer costs per hectare
    fertilizer_cost_per_ha = (
        (urea_needed / 50) * FERTILIZER_PRICES["urea"] +
        (dap_needed / 50) * FERTILIZER_PRICES["dap"] +
        (mop_needed / 50) * FERTILIZER_PRICES["mop"]
    )
    
    # Calculate yield potential based on nutrient availability
    nutrient_efficiency = calculate_nutrient_efficiency(current_n, current_p, current_k, crop_info["nutrient_requirements"])
    expected_yield = crop_info["base_yield"] * nutrient_efficiency * ph_factor
    
    # Calculate economics
    revenue_per_ha = expected_yield * crop_info["market_price"]
    
    # Additional costs (seeds, labor, etc.)
    base_costs_per_ha = {
        "wheat": 200, "rice": 250, "corn": 180, 
        "cotton": 300, "sugarcane": 500, "soybean": 150
    }
    other_costs = base_costs_per_ha.get(crop_id, 200)
    
    total_cost_per_ha = fertilizer_cost_per_ha + other_costs
    net_profit_per_ha = revenue_per_ha - total_cost_per_ha
    
    # Scale to farm size
    total_revenue = revenue_per_ha * farm_size
    total_cost = total_cost_per_ha * farm_size
    net_profit = net_profit_per_ha * farm_size
    
    # Calculate ROI
    roi = (net_profit / total_cost * 100) if total_cost > 0 else 0
    
    # Generate fertilizer plan
    fertilizer_plan = {
        "urea_bags": round(urea_needed * farm_size / 50, 1),
        "dap_bags": round(dap_needed * farm_size / 50, 1),
        "mop_bags": round(mop_needed * farm_size / 50, 1),
        "total_fertilizer_cost": round(fertilizer_cost_per_ha * farm_size, 2),
        "application_schedule": get_application_schedule(crop_id)
    }
    
    return {
        "crop_id": crop_id,
        "crop_name": crop_info["name"],
        "suitability_score": round(nutrient_efficiency * ph_factor * 100, 1),
        "expected_yield": round(expected_yield, 2),
        "total_yield": round(expected_yield * farm_size, 2),
        "market_price": crop_info["market_price"],
        "total_revenue": round(total_revenue, 2),
        "total_cost": round(total_cost, 2),
        "net_profit": round(net_profit, 2),
        "roi": round(roi, 1),
        "fertilizer_plan": fertilizer_plan,
        "growing_season_days": crop_info["growing_season"],
        "water_requirement": crop_info["water_requirement"],
        "ph_suitable": ph_suitable,
        "nutrient_deficits": {
            "nitrogen": round(n_deficit, 1),
            "phosphorus": round(p_deficit, 1),
            "potassium": round(k_deficit, 1)
        }
    }

def calculate_nutrient_efficiency(current_n: float, current_p: float, current_k: float, requirements: dict) -> float:
    """Calculate overall nutrient efficiency factor."""
    n_efficiency = min(1.0, current_n / requirements["N"]) if requirements["N"] > 0 else 1.0
    p_efficiency = min(1.0, current_p / requirements["P"]) if requirements["P"] > 0 else 1.0
    k_efficiency = min(1.0, current_k / requirements["K"]) if requirements["K"] > 0 else 1.0
    
    # Weighted average (N is most important)
    return (n_efficiency * 0.5 + p_efficiency * 0.3 + k_efficiency * 0.2)

def get_application_schedule(crop_id: str) -> list:
    """Get fertilizer application schedule for crop."""
    schedules = {
        "wheat": ["Pre-sowing: 50% N, 100% P, 100% K", "Tillering: 25% N", "Grain filling: 25% N"],
        "rice": ["Transplanting: 50% N, 100% P, 100% K", "Tillering: 25% N", "Panicle initiation: 25% N"],
        "corn": ["Planting: 30% N, 100% P, 100% K", "V6 stage: 40% N", "Tasseling: 30% N"],
        "cotton": ["Planting: 25% N, 100% P, 50% K", "Squaring: 50% N, 50% K", "Flowering: 25% N"],
        "sugarcane": ["Planting: 33% N, 100% P, 50% K", "Tillering: 33% N, 50% K", "Grand growth: 34% N"],
        "soybean": ["Planting: 100% P, 100% K", "Flowering: 100% N", "Pod filling: Monitor only"]
    }
    return schedules.get(crop_id, ["Pre-planting: 100% fertilizer"])

def generate_recommendations(top_crops: list) -> list:
    """Generate actionable recommendations based on analysis."""
    recommendations = []
    
    if top_crops:
        best_crop = top_crops[0]
        recommendations.append(f"Plant {best_crop['crop_name']} for maximum profitability (ROI: {best_crop['roi']}%)")
        
        if best_crop['fertilizer_plan']['total_fertilizer_cost'] > 0:
            recommendations.append(f"Invest ${best_crop['fertilizer_plan']['total_fertilizer_cost']} in fertilizers for optimal yield")
        
        if not best_crop['ph_suitable']:
            recommendations.append("Consider soil pH adjustment for better crop performance")
        
        if len(top_crops) > 1:
            second_crop = top_crops[1]
            recommendations.append(f"Alternative: {second_crop['crop_name']} (ROI: {second_crop['roi']}%)")
    
    recommendations.append("Monitor market prices regularly for timing your sales")
    recommendations.append("Consider crop rotation to maintain soil health")
    
    return recommendations
