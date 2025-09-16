"""
Tests for Pydantic schema models.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from app.models.schemas import (
    # Enums
    PredictionType, CropType, WeatherCondition,
    
    # User Models
    UserCreate, UserLogin, UserResponse, TokenResponse,
    
    # Prediction Models
    YieldPredictionRequest, CropRecommendationRequest,
    DiseasePredictionRequest, PestPredictionRequest,
    RainfallPredictionRequest, SoilTypePredictionRequest,
    
    # Weather Models
    WeatherData, WeatherAlert, WeatherForecast, WeatherResponse,
    HourlyForecast, DailyForecast, WeatherForecastResponse,
    
    # Soil Models
    EnhancedSoilData, SoilQualityMetrics, SoilHealthHistory,
    SoilNutrientLevels,
    
    # Market Models
    MarketData, PriceHistory, MarketTrends, DemandForecast
)

# Test Data
VALID_UUID = uuid4()
CURRENT_TIME = datetime.now()
FUTURE_TIME = CURRENT_TIME + timedelta(days=1)

def test_user_create():
    """Test UserCreate model validation."""
    # Valid data
    valid_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890",
        "region": "North",
        "farm_size": 100.5,
        "main_crops": "wheat,rice",
        "password": "Password123!"
    }
    user = UserCreate(**valid_data)
    assert user.name == valid_data["name"]
    
    # Invalid password
    with pytest.raises(ValueError):
        UserCreate(**{**valid_data, "password": "weak"})

def test_weather_data():
    """Test WeatherData model validation."""
    valid_data = {
        "temperature": 25.5,
        "feels_like": 26.0,
        "humidity": 65,
        "rainfall": 0.0,
        "wind_speed": 5.2,
        "wind_direction": 180,
        "pressure": 1013,
        "visibility": 10000,
        "condition": WeatherCondition.CLEAR,
        "date": CURRENT_TIME
    }
    weather = WeatherData(**valid_data)
    assert weather.temperature == valid_data["temperature"]
    
    # Test invalid humidity
    with pytest.raises(ValueError):
        WeatherData(**{**valid_data, "humidity": 101})

def test_soil_quality_metrics():
    """Test SoilQualityMetrics model validation."""
    valid_data = {
        "quality_score": 85.5,
        "fertility_index": 78.0,
        "organic_content": 45.2,
        "biological_activity": 65.0,
        "compaction": 30.0,
        "updated_at": CURRENT_TIME
    }
    metrics = SoilQualityMetrics(**valid_data)
    assert metrics.quality_score == valid_data["quality_score"]
    
    # Test invalid score
    with pytest.raises(ValueError):
        SoilQualityMetrics(**{**valid_data, "quality_score": 101})

def test_market_data():
    """Test MarketData model validation."""
    valid_data = {
        "crop_type": "wheat",
        "current_price": 250.50,
        "price_change": 5.25,
        "price_change_percentage": 2.1,
        "volume": 1000,
        "market_cap": 250500.0,
        "updated_at": CURRENT_TIME
    }
    market = MarketData(**valid_data)
    assert market.crop_type == valid_data["crop_type"]
    assert market.currency == "USD"  # Test default value

def test_weather_alert():
    """Test WeatherAlert model validation."""
    valid_data = {
        "alert_type": "storm",
        "severity": "high",
        "title": "Severe Storm Warning",
        "description": "Strong winds and heavy rain expected",
        "start_time": CURRENT_TIME,
        "end_time": FUTURE_TIME,
        "affected_areas": ["North Region", "Central Region"],
        "certainty": "Likely"
    }
    alert = WeatherAlert(**valid_data)
    assert alert.alert_type == valid_data["alert_type"]
    
    # Test invalid certainty
    with pytest.raises(ValueError):
        WeatherAlert(**{**valid_data, "certainty": "Maybe"})

def test_crop_yield_request():
    """Test YieldPredictionRequest model validation."""
    valid_data = {
        "prediction_type": PredictionType.YIELD,
        "crop_type": CropType.WHEAT,
        "area": 100.0,
        "rainfall": 45.5,
        "fertilizer_amount": 60.0,
        "temperature": 25.0,
        "nitrogen": 40,
        "phosphorus": 35,
        "potassium": 30,
        "sowing_date": "2025-03-15",
        "soil_ph": 6.5
    }
    request = YieldPredictionRequest(**valid_data)
    assert request.crop_type == CropType.WHEAT
    
    # Test invalid date format
    with pytest.raises(ValueError):
        YieldPredictionRequest(**{**valid_data, "sowing_date": "15-03-2025"})

def test_soil_health_history():
    """Test SoilHealthHistory model validation."""
    valid_data = {
        "dates": [CURRENT_TIME, FUTURE_TIME],
        "metrics": {
            "ph": [6.5, 6.7],
            "nitrogen": [45, 48]
        },
        "trends": {
            "ph": "increasing",
            "nitrogen": "stable"
        }
    }
    history = SoilHealthHistory(**valid_data)
    assert len(history.dates) == 2
    assert "ph" in history.metrics

def test_daily_forecast():
    """Test DailyForecast model validation."""
    valid_data = {
        "date": CURRENT_TIME,
        "temp_max": 30.5,
        "temp_min": 20.5,
        "sunrise": CURRENT_TIME,
        "sunset": FUTURE_TIME,
        "weather_condition": WeatherCondition.PARTLY_CLOUDY,
        "precipitation_chance": 30.0,
        "rainfall": 0.0,
        "uv_index": 6.0
    }
    forecast = DailyForecast(**valid_data)
    assert forecast.weather_condition == WeatherCondition.PARTLY_CLOUDY
    
    # Test invalid precipitation chance
    with pytest.raises(ValueError):
        DailyForecast(**{**valid_data, "precipitation_chance": 101})

def test_demand_forecast():
    """Test DemandForecast model validation."""
    valid_data = {
        "crop_type": "wheat",
        "current_demand": 1000.0,
        "forecasted_demand": [
            {"month": "January", "demand": 1100.0},
            {"month": "February", "demand": 1200.0}
        ],
        "factors_affecting_demand": ["Season", "Export Demand"],
        "confidence_level": 0.85,
        "updated_at": CURRENT_TIME
    }
    forecast = DemandForecast(**valid_data)
    assert forecast.crop_type == valid_data["crop_type"]
    assert len(forecast.forecasted_demand) == 2

def test_enhanced_pest_prediction():
    """Test enhanced PestPredictionRequest model with image data."""
    # Test basic request (backward compatibility)
    basic_data = {
        "prediction_type": PredictionType.PEST,
        "crop_type": CropType.TOMATO,
        "pest_description": "Small green insects on leaves",
        "damage_level": "medium",
        "treatment_history": ["Neem oil spray"],
        "area": 100.5  # Required field from PredictionRequest
    }
    basic_request = PestPredictionRequest(**basic_data)
    assert basic_request.damage_level == "medium"
    
    # Test with image data
    enhanced_data = {
        **basic_data,
        "image_data": "base64_encoded_string",
        "image_type": "jpeg",
        "image_metadata": {
            "resolution": "1920x1080",
            "capture_time": "2025-09-15T10:00:00"
        }
    }
    enhanced_request = PestPredictionRequest(**enhanced_data)
    assert enhanced_request.image_type == "jpeg"
    assert "resolution" in enhanced_request.image_metadata

def test_enhanced_rainfall_prediction():
    """Test enhanced RainfallPredictionRequest model with historical data."""
    # Test basic request (backward compatibility)
    basic_data = {
        "prediction_type": PredictionType.RAINFALL,
        "year": 2025,
        "subdivision": 5,
        "month": 9,
        "current_rainfall": 45.5,
        "location": "North Region"
    }
    basic_request = RainfallPredictionRequest(**basic_data)
    assert basic_request.current_rainfall == 45.5
    
    # Test with historical data
    enhanced_data = {
        **basic_data,
        "historical_rainfall": [42.0, 38.5, 55.2],
        "seasonal_pattern": "monsoon",
        "soil_moisture_percentage": 75.5
    }
    enhanced_request = RainfallPredictionRequest(**enhanced_data)
    assert len(enhanced_request.historical_rainfall) == 3
    assert enhanced_request.seasonal_pattern == "monsoon"

def test_enhanced_soil_prediction():
    """Test enhanced SoilTypePredictionRequest model with additional properties."""
    # Test basic request (backward compatibility)
    basic_data = {
        "prediction_type": PredictionType.SOIL_TYPE,
        "nitrogen": 45.5,
        "phosphorus": 28.2,
        "potassium": 62.8,
        "temperature": 25.5,
        "moisture": 65.2,
        "humidity": 72.4,
        "location": "Field A12"
    }
    basic_request = SoilTypePredictionRequest(**basic_data)
    assert basic_request.nitrogen == 45.5
    
    # Test with enhanced properties
    enhanced_data = {
        **basic_data,
        "ph_level": 6.8,
        "organic_matter": 3.5,
        "electrical_conductivity": 1.2
    }
    enhanced_request = SoilTypePredictionRequest(**enhanced_data)
    assert enhanced_request.ph_level == 6.8
    assert enhanced_request.organic_matter == 3.5
    
    # Test invalid pH level
    with pytest.raises(ValueError):
        SoilTypePredictionRequest(**{**enhanced_data, "ph_level": 15.0})

if __name__ == "__main__":
    pytest.main([__file__])