"""
Simplified AgriSmart Backend for Demo
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import numpy as np
from apis.soil_health_simple import router as soil_health_router
from apis.auth_simple import router as auth_router
from apis.weather_simple import router as weather_router
from apis.crop_prediction import router as crop_prediction_router

app = FastAPI(
    title="AgriSmart API",
    description="Backend API for AgriSmart agricultural management platform",
    version="1.0.0"
)

# Include routers
app.include_router(soil_health_router, prefix="/api/soil-health", tags=["Soil Health"])
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(weather_router, prefix="/api/weather", tags=["Weather"])
app.include_router(crop_prediction_router, prefix="/api/crop-prediction", tags=["Crop Prediction"])

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crop data with nutrient requirements and market info
CROP_DATA = {
    "wheat": {
        "name": "Wheat",
        "nutrient_requirements": {"N": 120, "P": 60, "K": 40, "pH_min": 6.0, "pH_max": 7.5},
        "base_yield": 4.5,
        "market_price": 250,
        "growing_season": 120,
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
}

class SoilDataRequest(BaseModel):
    nitrogen: float
    phosphorus: float
    potassium: float
    ph: float
    farm_size: float
    organic_matter: Optional[float] = None

@app.get("/")
async def root():
    return {"status": "healthy", "service": "AgriSmart API"}

@app.post("/api/profitable-crops/predict")
async def predict_profitable_crops(soil_data: SoilDataRequest):
    """Predict most profitable crops based on soil analysis."""
    
    try:
        # Extract soil parameters
        current_n = soil_data.nitrogen
        current_p = soil_data.phosphorus
        current_k = soil_data.potassium
        soil_ph = soil_data.ph
        farm_size = soil_data.farm_size
        
        # Analyze each crop
        crop_analyses = []
        
        for crop_id, crop_info in CROP_DATA.items():
            analysis = analyze_crop_profitability(
                crop_id, crop_info, current_n, current_p, current_k, soil_ph, farm_size
            )
            crop_analyses.append(analysis)
        
        # Sort by ROI
        crop_analyses.sort(key=lambda x: x["roi"], reverse=True)
        
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
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate prediction: {str(e)}")

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
    
    # Calculate yield potential
    nutrient_efficiency = calculate_nutrient_efficiency(current_n, current_p, current_k, crop_info["nutrient_requirements"])
    expected_yield = crop_info["base_yield"] * nutrient_efficiency * ph_factor
    
    # Calculate economics
    revenue_per_ha = expected_yield * crop_info["market_price"]
    
    # Additional costs
    base_costs_per_ha = {
        "wheat": 200, "rice": 250, "corn": 180, 
        "cotton": 300, "soybean": 150
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
        "total_fertilizer_cost": round(fertilizer_cost_per_ha * farm_size, 2)
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
        "ph_suitable": ph_suitable
    }

def calculate_nutrient_efficiency(current_n: float, current_p: float, current_k: float, requirements: dict) -> float:
    """Calculate overall nutrient efficiency factor."""
    n_efficiency = min(1.0, current_n / requirements["N"]) if requirements["N"] > 0 else 1.0
    p_efficiency = min(1.0, current_p / requirements["P"]) if requirements["P"] > 0 else 1.0
    k_efficiency = min(1.0, current_k / requirements["K"]) if requirements["K"] > 0 else 1.0
    
    # Weighted average (N is most important)
    return (n_efficiency * 0.5 + p_efficiency * 0.3 + k_efficiency * 0.2)

def generate_recommendations(top_crops: list) -> list:
    """Generate actionable recommendations."""
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("simple_main:app", host="0.0.0.0", port=8000, reload=True)
