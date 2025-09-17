"""
Simple Weather API for AgriSmart demo
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import random
from datetime import datetime, timedelta

router = APIRouter()

class WeatherRequest(BaseModel):
    location: Optional[str] = "Nadiad, IN"
    days: Optional[int] = 7

class WeatherResponse(BaseModel):
    location: str
    current: Dict
    forecast: List[Dict]
    alerts: List[Dict]
    agricultural_insights: Dict

@router.get("/current")
async def get_current_weather(location: str = "Nadiad, IN"):
    """Get current weather conditions."""
    
    # Mock current weather data
    current_weather = {
        "temperature": 27 + random.randint(-3, 3),
        "humidity": 80 + random.randint(-10, 10),
        "wind_speed": 8 + random.randint(-3, 3),
        "wind_direction": "NW",
        "pressure": 1013 + random.randint(-5, 5),
        "visibility": 10,
        "uv_index": 6,
        "cloud_cover": 40 + random.randint(-20, 20),
        "condition": "Partly Cloudy",
        "feels_like": 29 + random.randint(-2, 2),
        "dew_point": 22,
        "rainfall_today": random.choice([0, 0, 0, 2, 5, 8]),
        "last_updated": datetime.now().isoformat()
    }
    
    return {
        "location": location,
        "current": current_weather,
        "status": "success"
    }

@router.get("/forecast")
async def get_weather_forecast(location: str = "Nadiad, IN", days: int = 7):
    """Get weather forecast for specified days."""
    
    forecast = []
    base_temp = 27
    
    for i in range(days):
        date = datetime.now() + timedelta(days=i)
        
        # Generate realistic weather variations
        temp_variation = random.randint(-4, 4)
        rain_chance = random.choice([0, 0, 10, 20, 30, 60, 80])
        
        day_forecast = {
            "date": date.strftime("%Y-%m-%d"),
            "day": date.strftime("%A"),
            "temperature": {
                "max": base_temp + temp_variation + 3,
                "min": base_temp + temp_variation - 5
            },
            "humidity": 75 + random.randint(-15, 15),
            "wind_speed": 6 + random.randint(-2, 4),
            "rainfall_probability": rain_chance,
            "rainfall_amount": rain_chance * 0.1 if rain_chance > 30 else 0,
            "condition": get_weather_condition(rain_chance),
            "uv_index": random.randint(4, 8),
            "sunrise": "06:15",
            "sunset": "18:45"
        }
        forecast.append(day_forecast)
    
    return {
        "location": location,
        "forecast": forecast,
        "status": "success"
    }

@router.get("/agricultural-insights")
async def get_agricultural_insights(location: str = "Nadiad, IN"):
    """Get weather-based agricultural insights."""
    
    # Get current weather for analysis
    current = await get_current_weather(location)
    current_data = current["current"]
    
    insights = {
        "irrigation_recommendation": get_irrigation_advice(current_data),
        "crop_stress_level": assess_crop_stress(current_data),
        "pest_disease_risk": assess_pest_risk(current_data),
        "field_work_suitability": assess_field_work(current_data),
        "recommendations": generate_weather_recommendations(current_data)
    }
    
    return {
        "location": location,
        "insights": insights,
        "generated_at": datetime.now().isoformat()
    }

@router.get("/alerts")
async def get_weather_alerts(location: str = "Nadiad, IN"):
    """Get weather alerts and warnings."""
    
    # Mock weather alerts
    alerts = []
    
    # Generate random alerts based on conditions
    if random.choice([True, False, False]):  # 33% chance
        alerts.append({
            "id": "HEAT_001",
            "type": "Heat Warning",
            "severity": "Medium",
            "title": "High Temperature Alert",
            "description": "Temperatures expected to reach 35°C. Take precautions for heat-sensitive crops.",
            "start_time": datetime.now().isoformat(),
            "end_time": (datetime.now() + timedelta(days=2)).isoformat(),
            "recommendations": [
                "Increase irrigation frequency",
                "Provide shade for sensitive crops",
                "Avoid field work during peak hours"
            ]
        })
    
    if random.choice([True, False, False, False]):  # 25% chance
        alerts.append({
            "id": "RAIN_001",
            "type": "Heavy Rain Warning",
            "severity": "High",
            "title": "Heavy Rainfall Expected",
            "description": "Heavy rainfall (50-80mm) expected in next 24 hours.",
            "start_time": (datetime.now() + timedelta(hours=6)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=1)).isoformat(),
            "recommendations": [
                "Ensure proper drainage",
                "Postpone spraying activities",
                "Harvest ready crops if possible"
            ]
        })
    
    return {
        "location": location,
        "alerts": alerts,
        "alert_count": len(alerts)
    }

def get_weather_condition(rain_chance):
    """Get weather condition based on rain probability."""
    if rain_chance >= 80:
        return "Heavy Rain"
    elif rain_chance >= 60:
        return "Rain"
    elif rain_chance >= 30:
        return "Partly Cloudy"
    else:
        return "Sunny"

def get_irrigation_advice(weather_data):
    """Generate irrigation recommendations based on weather."""
    temp = weather_data["temperature"]
    humidity = weather_data["humidity"]
    rainfall = weather_data["rainfall_today"]
    
    if rainfall > 5:
        return {
            "recommendation": "Skip irrigation today",
            "reason": "Adequate rainfall received",
            "next_irrigation": "Monitor soil moisture in 2-3 days"
        }
    elif temp > 32 and humidity < 60:
        return {
            "recommendation": "Increase irrigation",
            "reason": "High temperature and low humidity increase water demand",
            "next_irrigation": "Irrigate early morning or evening"
        }
    elif temp < 20:
        return {
            "recommendation": "Reduce irrigation frequency",
            "reason": "Cool weather reduces water demand",
            "next_irrigation": "Check soil moisture before next irrigation"
        }
    else:
        return {
            "recommendation": "Normal irrigation schedule",
            "reason": "Weather conditions are moderate",
            "next_irrigation": "Continue regular irrigation schedule"
        }

def assess_crop_stress(weather_data):
    """Assess crop stress level based on weather conditions."""
    temp = weather_data["temperature"]
    humidity = weather_data["humidity"]
    wind_speed = weather_data["wind_speed"]
    
    stress_score = 0
    
    # Temperature stress
    if temp > 35:
        stress_score += 30
    elif temp > 30:
        stress_score += 15
    elif temp < 15:
        stress_score += 20
    
    # Humidity stress
    if humidity < 40:
        stress_score += 20
    elif humidity > 90:
        stress_score += 15
    
    # Wind stress
    if wind_speed > 15:
        stress_score += 10
    
    if stress_score >= 40:
        level = "High"
    elif stress_score >= 20:
        level = "Medium"
    else:
        level = "Low"
    
    return {
        "level": level,
        "score": min(stress_score, 100),
        "factors": get_stress_factors(temp, humidity, wind_speed)
    }

def assess_pest_risk(weather_data):
    """Assess pest and disease risk based on weather."""
    temp = weather_data["temperature"]
    humidity = weather_data["humidity"]
    
    risk_score = 0
    
    # High humidity increases fungal disease risk
    if humidity > 80:
        risk_score += 25
    elif humidity > 70:
        risk_score += 15
    
    # Optimal temperature for pest activity
    if 25 <= temp <= 30:
        risk_score += 20
    elif 20 <= temp <= 35:
        risk_score += 10
    
    if risk_score >= 35:
        level = "High"
    elif risk_score >= 20:
        level = "Medium"
    else:
        level = "Low"
    
    return {
        "level": level,
        "score": risk_score,
        "primary_risks": get_primary_risks(temp, humidity)
    }

def assess_field_work(weather_data):
    """Assess suitability for field work."""
    temp = weather_data["temperature"]
    wind_speed = weather_data["wind_speed"]
    rainfall = weather_data["rainfall_today"]
    
    if rainfall > 2:
        return {
            "suitability": "Poor",
            "reason": "Recent rainfall makes field conditions unsuitable",
            "recommendation": "Wait 1-2 days for soil to dry"
        }
    elif temp > 35:
        return {
            "suitability": "Limited",
            "reason": "High temperature poses heat stress risk",
            "recommendation": "Work during early morning or evening hours"
        }
    elif wind_speed > 20:
        return {
            "suitability": "Limited",
            "reason": "High wind speed affects spraying and other activities",
            "recommendation": "Postpone spraying activities"
        }
    else:
        return {
            "suitability": "Good",
            "reason": "Weather conditions are favorable",
            "recommendation": "Suitable for all field activities"
        }

def get_stress_factors(temp, humidity, wind_speed):
    """Get specific stress factors."""
    factors = []
    
    if temp > 35:
        factors.append("Extreme heat stress")
    elif temp > 30:
        factors.append("Heat stress")
    elif temp < 15:
        factors.append("Cold stress")
    
    if humidity < 40:
        factors.append("Low humidity stress")
    elif humidity > 90:
        factors.append("High humidity stress")
    
    if wind_speed > 15:
        factors.append("Wind stress")
    
    return factors if factors else ["No significant stress factors"]

def get_primary_risks(temp, humidity):
    """Get primary pest and disease risks."""
    risks = []
    
    if humidity > 80:
        risks.extend(["Fungal diseases", "Bacterial infections"])
    
    if 25 <= temp <= 30 and humidity > 60:
        risks.extend(["Aphid infestation", "Thrips activity"])
    
    if temp > 30:
        risks.append("Spider mite activity")
    
    return risks if risks else ["Low pest activity"]

def generate_weather_recommendations(weather_data):
    """Generate comprehensive weather-based recommendations."""
    recommendations = []
    
    temp = weather_data["temperature"]
    humidity = weather_data["humidity"]
    rainfall = weather_data["rainfall_today"]
    
    if temp > 32:
        recommendations.append("Apply mulch to reduce soil temperature")
        recommendations.append("Schedule irrigation for early morning")
    
    if humidity > 80:
        recommendations.append("Improve air circulation around crops")
        recommendations.append("Monitor for fungal diseases")
    
    if rainfall == 0 and humidity < 60:
        recommendations.append("Increase irrigation frequency")
    
    if not recommendations:
        recommendations.append("Weather conditions are favorable for normal farming activities")
    
    return recommendations

@router.get("/")
async def weather_info():
    """Get weather API information."""
    return {
        "message": "AgriSmart Weather API",
        "endpoints": [
            "GET /current - Current weather conditions",
            "GET /forecast - Weather forecast",
            "GET /agricultural-insights - Farming recommendations",
            "GET /alerts - Weather alerts and warnings"
        ],
        "features": [
            "Real-time weather data",
            "Agricultural insights",
            "Irrigation recommendations",
            "Pest risk assessment"
        ]
    }
