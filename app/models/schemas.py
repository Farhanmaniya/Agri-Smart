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

# User Models
class UserCreate(BaseModel):
    """User registration model."""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str
    region: str = Field(..., max_length=100)
    farm_size: float = Field(..., ge=0)
    main_crops: str = Field(..., max_length=200)
    password: str = Field(..., min_length=6)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        pattern = r"^[A-Za-z\d@$!%*#?&]{6,}$"
        if not re.match(pattern, v):
            raise ValueError('Password must be at least 6 characters with letters, numbers, and special characters')
        return v

class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr
    password: str

class GoogleAuthRequest(BaseModel):
    """Google OAuth request model."""
    token: str

class UserResponse(BaseModel):
    """User response model."""
    id: UUID
    name: str
    email: str
    phone: str
    region: str
    farm_size: float
    main_crops: str
    member_since: int
    predictions_count: int = 0
    accuracy_rate: str = "0%"
    last_prediction: str = "Never"
    created_at: datetime

class TokenResponse(BaseModel):
    """JWT token response model."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Prediction Models
class PredictionRequest(BaseModel):
    """Base prediction request model."""
    prediction_type: PredictionType
    crop_type: Optional[CropType] = None
    area: float = Field(..., ge=0)
    soil_data: Dict[str, Any] = {}
    weather_data: Dict[str, Any] = {}
    additional_params: Optional[Dict[str, Any]] = {}

class YieldPredictionRequest(PredictionRequest):
    """Enhanced yield prediction request matching your crop_yield_model.pkl."""
    prediction_type: PredictionType = PredictionType.YIELD
    crop_type: CropType
    
    # Core parameters for your Decision Tree model (6 features)
    rainfall: float = Field(..., ge=0, description="Rain Fall (mm)")
    fertilizer_amount: float = Field(50.0, ge=0, description="Fertilizer amount")
    temperature: float = Field(..., ge=-50, le=60, description="Temperature")
    nitrogen: float = Field(..., ge=0, description="Nitrogen (N)")
    phosphorus: float = Field(..., ge=0, description="Phosphorus (P)")  
    potassium: float = Field(..., ge=0, description="Potassium (K)")
    
    # Additional parameters for API compatibility
    sowing_date: str
    soil_ph: float = Field(..., ge=0, le=14)
    
    @field_validator('sowing_date')
    @classmethod
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')

class CropRecommendationRequest(BaseModel):
    """New model for your crop_recommendation_model.pkl (Random Forest with 11 features)."""
    prediction_type: PredictionType = PredictionType.CROP_RECOMMENDATION
    area: float = Field(..., ge=0)
    
    # 11 features required by your Random Forest model
    nitrogen: float = Field(..., ge=0, description="Nitrogen (N)")
    phosphorus: float = Field(..., ge=0, description="Phosphorus (P)")
    potassium: float = Field(..., ge=0, description="Potassium (K)")
    ph: float = Field(..., ge=0, le=14, description="Soil pH")
    ec: float = Field(..., ge=0, description="Electrical Conductivity")
    sulfur: float = Field(..., ge=0, description="Sulfur (S)")
    copper: float = Field(..., ge=0, description="Copper (Cu)")
    iron: float = Field(..., ge=0, description="Iron (Fe)")
    manganese: float = Field(..., ge=0, description="Manganese (Mn)")
    zinc: float = Field(..., ge=0, description="Zinc (Zn)")
    boron: float = Field(..., ge=0, description="Boron (B)")
    
    # Optional metadata
    region: Optional[str] = None
    season: Optional[str] = None
    climate_data: Optional[Dict[str, Any]] = {}

class DiseasePredictionRequest(PredictionRequest):
    """Disease prediction specific request."""
    prediction_type: PredictionType = PredictionType.DISEASE
    crop_type: CropType
    symptoms: List[str] = []
    affected_area_percentage: float = Field(..., ge=0, le=100)
    days_since_symptoms: int = Field(..., ge=0)

class PestPredictionRequest(PredictionRequest):
    """Pest prediction specific request."""
    prediction_type: PredictionType = PredictionType.PEST
    crop_type: CropType
    pest_description: str
    damage_level: str = Field(..., pattern=r"^(low|medium|high)$")  # FIXED: Changed regex to pattern
    treatment_history: Optional[List[str]] = []
    # Image analysis fields (optional to maintain backward compatibility)
    image_data: Optional[str] = Field(None, description="Base64 encoded image data")
    image_type: Optional[str] = Field(None, pattern=r"^(jpeg|jpg|png)$", description="Image file type")
    image_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional image metadata like resolution, capture time, etc."
    )

class RainfallPredictionRequest(BaseModel):
    """Rainfall prediction request model."""
    prediction_type: PredictionType = PredictionType.RAINFALL
    year: int = Field(2024, ge=2000, le=2030, description="Year")
    subdivision: int = Field(1, ge=1, le=10, description="Subdivision/Region code")
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    current_rainfall: float = Field(0.0, ge=0, description="Current month rainfall in mm")
    
    # Optional metadata
    location: Optional[str] = None
    elevation: Optional[float] = None
    
    # Historical data (optional, enhances prediction accuracy)
    historical_rainfall: Optional[List[float]] = Field(
        None,
        description="Previous months' rainfall data in mm (up to 12 months)"
    )
    seasonal_pattern: Optional[str] = Field(
        None,
        pattern=r"^(monsoon|winter|summer|spring)$",
        description="Current seasonal pattern"
    )
    soil_moisture_percentage: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Current soil moisture percentage"
    )

class SoilTypePredictionRequest(BaseModel):
    """Soil type prediction request model."""
    prediction_type: PredictionType = PredictionType.SOIL_TYPE
    nitrogen: float = Field(..., ge=0, description="Nitrogen content")
    phosphorus: float = Field(..., ge=0, description="Phosphorus content")
    potassium: float = Field(..., ge=0, description="Potassium content")
    temperature: float = Field(..., ge=-50, le=60, description="Temperature in Celsius")
    moisture: float = Field(..., ge=0, le=100, description="Moisture percentage")
    humidity: float = Field(..., ge=0, le=100, description="Humidity percentage")
    
    # Optional metadata
    location: Optional[str] = None
    depth: Optional[float] = Field(None, ge=0, description="Soil depth in cm")
    texture: Optional[str] = None
    
    # Enhanced soil properties (optional)
    ph_level: Optional[float] = Field(
        None,
        ge=0,
        le=14,
        description="Soil pH level (0-14 scale)"
    )
    organic_matter: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Organic matter content percentage"
    )
    electrical_conductivity: Optional[float] = Field(
        None,
        ge=0,
        description="Electrical conductivity in dS/m"
    )

class PredictionResponse(BaseModel):
    """Enhanced prediction response model."""
    id: UUID
    user_id: UUID
    prediction_type: str
    crop_type: Optional[str] = None
    predictions: Dict[str, Any]
    confidence: float
    recommendations: Dict[str, Any]
    model_info: Optional[Dict[str, Any]] = {}
    created_at: datetime
    
    model_config = {"protected_namespaces": ()}  # FIX PYDANTIC WARNING

class CropRecommendationResponse(BaseModel):
    """Specific response for crop recommendation."""
    id: UUID
    user_id: UUID
    recommended_crop: str
    confidence: float
    alternative_crops: List[str]
    crop_probabilities: Optional[Dict[str, float]] = {}
    recommendations: Dict[str, Any]
    soil_analysis: Dict[str, Any]
    model_info: Dict[str, Any]
    created_at: datetime
    
    model_config = {"protected_namespaces": ()}  # FIX PYDANTIC WARNING

class RainfallPredictionResponse(BaseModel):
    """Specific response for rainfall prediction."""
    id: UUID
    user_id: UUID
    prediction_type: str
    predicted_rainfall: float
    rainfall_category: str
    confidence: float
    recommendations: Dict[str, Any]
    model_info: Dict[str, Any]
    created_at: datetime
    
    model_config = {"protected_namespaces": ()}  # FIX PYDANTIC WARNING

class SoilTypePredictionResponse(BaseModel):
    """Specific response for soil type prediction."""
    id: UUID
    user_id: UUID
    prediction_type: str
    predicted_soil_type: str
    confidence: float
    alternative_soil_types: List[str]
    soil_probabilities: Optional[Dict[str, float]] = {}
    recommendations: Dict[str, Any]
    model_info: Dict[str, Any]
    created_at: datetime
    
    model_config = {"protected_namespaces": ()}  # FIX PYDANTIC WARNING

# Model Management
class ModelInfo(BaseModel):
    """Information about a loaded ML model."""
    name: str
    type: str
    algorithm: str
    input_features: List[str]
    feature_count: int
    output_type: str
    loaded: bool
    is_fallback: bool = False
    file_path: Optional[str] = None
    accuracy: Optional[float] = None
    last_updated: Optional[datetime] = None

class ModelListResponse(BaseModel):
    """Response for listing available models."""
    models: Dict[str, ModelInfo]
    total_models: int
    loaded_models: int
    fallback_models: int

class AddModelRequest(BaseModel):
    """Request to add a new model."""
    model_name: str = Field(..., min_length=1, max_length=100)
    model_path: str
    model_type: str = Field(..., pattern=r"^(regressor|classifier|custom)$")
    description: Optional[str] = None
    expected_features: Optional[List[str]] = []
    
    model_config = {"protected_namespaces": ()}  # FIX PYDANTIC WARNING

class ModelResponse(BaseModel):
    """Model operation response."""
    model_name: str
    loaded: bool
    message: str
    
    model_config = {"protected_namespaces": ()}  # FIX PYDANTIC WARNING

# Irrigation Models
class IrrigationRequest(BaseModel):
    """Irrigation schedule request model."""
    crop_type: CropType
    area: float = Field(..., ge=0)
    soil_moisture: float = Field(..., ge=0, le=100)
    rainfall: float = Field(..., ge=0)
    temperature: float = Field(..., ge=-50, le=60)
    last_irrigation: str
    
    # Additional parameters for better scheduling
    growth_stage: Optional[str] = Field(None, pattern=r"^(seedling|vegetative|flowering|fruiting|maturity)$")  # FIXED
    irrigation_method: Optional[str] = Field(None, pattern=r"^(drip|sprinkler|flood|furrow)$")  # FIXED
    
    @field_validator('last_irrigation')
    @classmethod
    def validate_last_irrigation(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')

class IrrigationResponse(BaseModel):
    """Irrigation schedule response model."""
    schedule_date: datetime
    duration_minutes: int
    water_volume: float
    recommendations: Dict[str, Any]
    next_irrigation: Optional[datetime] = None
    efficiency_score: Optional[float] = None

# Dashboard Models
class DashboardStats(BaseModel):
    """Enhanced dashboard statistics model."""
    total_predictions: int = 0
    accuracy_rate: str = "0%"
    last_prediction: str = "Never"
    irrigation_count: int = 0
    member_since: int = 2025
    recent_predictions: List[PredictionResponse] = []
    
    # Enhanced stats
    models_available: int = 0
    crop_recommendations: int = 0
    yield_predictions: int = 0
    disease_detections: int = 0
    pest_classifications: int = 0

class CropAnalytics(BaseModel):
    """Enhanced crop analytics model."""
    crop_type: str
    total_area: float
    avg_yield: float
    disease_incidents: int
    pest_incidents: int
    irrigation_frequency: float
    
    # New analytics
    recommended_frequency: int = 0
    success_rate: float = 0.0
    soil_suitability: Optional[str] = None

# Soil and Weather Data Models
class SoilQualityMetrics(BaseModel):
    """Soil quality metrics model."""
    quality_score: float = Field(..., ge=0, le=100)
    fertility_index: float = Field(..., ge=0, le=100)
    organic_content: float = Field(..., ge=0, le=100)
    biological_activity: float = Field(..., ge=0, le=100)
    compaction: float = Field(..., ge=0, le=100)
    updated_at: datetime

    model_config = {"protected_namespaces": ()}

class SoilHealthHistory(BaseModel):
    """Historical soil health data model."""
    dates: List[datetime]
    metrics: Dict[str, List[float]]
    trends: Dict[str, str]
    alerts: List[Dict[str, Any]] = []
    
    model_config = {"protected_namespaces": ()}

class SoilNutrientLevels(BaseModel):
    """Detailed soil nutrient levels."""
    nitrogen: float = Field(..., ge=0)
    phosphorus: float = Field(..., ge=0)
    potassium: float = Field(..., ge=0)
    calcium: float = Field(..., ge=0)
    magnesium: float = Field(..., ge=0)
    sulfur: float = Field(..., ge=0)
    zinc: float = Field(..., ge=0)
    manganese: float = Field(..., ge=0)
    iron: float = Field(..., ge=0)
    copper: float = Field(..., ge=0)
    boron: float = Field(..., ge=0)
    
    model_config = {"protected_namespaces": ()}

class EnhancedSoilData(BaseModel):
    """Enhanced soil data model matching your crop recommendation model."""
    # Primary nutrients
    nitrogen: float = Field(..., ge=0, description="Nitrogen (N)")
    phosphorus: float = Field(..., ge=0, description="Phosphorus (P)")
    potassium: float = Field(..., ge=0, description="Potassium (K)")
    
    # Soil properties
    ph: float = Field(..., ge=0, le=14, description="Soil pH")
    ec: float = Field(..., ge=0, description="Electrical Conductivity")
    organic_matter: Optional[float] = Field(None, ge=0)
    moisture: Optional[float] = Field(None, ge=0, le=100)
    
    # Micronutrients (for your model)
    sulfur: float = Field(..., ge=0, description="Sulfur (S)")
    copper: float = Field(..., ge=0, description="Copper (Cu)")
    iron: float = Field(..., ge=0, description="Iron (Fe)")
    manganese: float = Field(..., ge=0, description="Manganese (Mn)")
    zinc: float = Field(..., ge=0, description="Zinc (Zn)")
    boron: float = Field(..., ge=0, description="Boron (B)")
    
    # Additional properties
    texture: Optional[str] = None
    drainage: Optional[str] = None
    depth: Optional[float] = None
    
    # Quality metrics
    quality_metrics: Optional[SoilQualityMetrics] = None
    nutrient_levels: Optional[SoilNutrientLevels] = None
    last_updated: datetime = Field(default_factory=datetime.now)
    
    model_config = {"protected_namespaces": ()}

class WeatherCondition(str, Enum):
    """Weather condition types."""
    CLEAR = "clear"
    PARTLY_CLOUDY = "partly_cloudy"
    CLOUDY = "cloudy"
    RAIN = "rain"
    THUNDERSTORM = "thunderstorm"
    SNOW = "snow"
    MIST = "mist"

class WeatherData(BaseModel):
    """Weather data model."""
    temperature: float = Field(..., description="Temperature in Celsius")
    feels_like: float = Field(..., description="Feels like temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity percentage")
    rainfall: float = Field(..., ge=0, description="Rainfall in mm")
    wind_speed: float = Field(..., ge=0, description="Wind speed in m/s")
    wind_direction: float = Field(..., ge=0, le=360, description="Wind direction in degrees")
    pressure: float = Field(..., ge=0, description="Atmospheric pressure in hPa")
    visibility: float = Field(..., ge=0, description="Visibility in meters")
    condition: WeatherCondition
    date: datetime
    
    # Additional weather parameters
    uv_index: Optional[float] = Field(None, ge=0, le=11)
    evapotranspiration: Optional[float] = Field(None, ge=0)
    dew_point: Optional[float] = None
    cloud_cover: Optional[int] = Field(None, ge=0, le=100)
    
    model_config = {"protected_namespaces": ()}

class WeatherAlert(BaseModel):
    """Weather alert model."""
    alert_type: str
    severity: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    affected_areas: List[str]
    recommendations: Optional[List[str]] = None
    source: str = "OpenWeather"
    certainty: str = Field(..., pattern="^(Observed|Likely|Possible|Unlikely)$")
    
    model_config = {"protected_namespaces": ()}

class WeatherForecast(BaseModel):
    """Detailed weather forecast model."""
    hourly: List[WeatherData]
    daily: List[WeatherData]
    precipitation_probability: List[float]
    weather_warnings: Optional[List[WeatherAlert]] = None
    
    model_config = {"protected_namespaces": ()}

class WeatherResponse(BaseModel):
    """Weather API response model."""
    location: str
    coordinates: Dict[str, float]
    timezone: str
    current: WeatherData
    forecast: WeatherForecast
    alerts: Optional[List[WeatherAlert]] = None
    last_updated: datetime
    
    model_config = {"protected_namespaces": ()}

# Market Data Models
class MarketData(BaseModel):
    """Market data model for current prices and trends."""
    crop_type: str
    current_price: float
    currency: str = "USD"
    unit: str = "ton"
    price_change: float
    price_change_percentage: float
    volume: int
    market_cap: float
    updated_at: datetime
    
    model_config = {"protected_namespaces": ()}

class PriceHistory(BaseModel):
    """Historical price data model."""
    crop_type: str
    prices: List[float]
    volumes: List[int]
    dates: List[str]
    currency: str = "USD"
    unit: str = "ton"
    
    model_config = {"protected_namespaces": ()}

class MarketTrends(BaseModel):
    """Market trends and analysis model."""
    crop_type: str
    price_trend: str
    demand_trend: str
    supply_status: str
    market_sentiment: str
    price_volatility: str
    trading_volume_trend: str
    seasonal_factors: List[str]
    key_influences: List[str]
    
    model_config = {"protected_namespaces": ()}

class DemandForecast(BaseModel):
    """Demand forecast model."""
    crop_type: str
    current_demand: float
    forecasted_demand: List[Dict[str, Any]]
    factors_affecting_demand: List[str]
    confidence_level: float
    unit: str = "ton"
    updated_at: datetime
    
    model_config = {"protected_namespaces": ()}

# Weather Forecast Models
class HourlyForecast(BaseModel):
    """Hourly weather forecast model."""
    hour: int = Field(..., ge=0, le=23)
    temperature: float
    precipitation_chance: float = Field(..., ge=0, le=100)
    weather_condition: WeatherCondition
    wind_speed: float
    
    model_config = {"protected_namespaces": ()}

class DailyForecast(BaseModel):
    """Daily weather forecast model."""
    date: datetime
    temp_max: float
    temp_min: float
    sunrise: datetime
    sunset: datetime
    weather_condition: WeatherCondition
    precipitation_chance: float = Field(..., ge=0, le=100)
    rainfall: float = Field(..., ge=0)
    uv_index: float = Field(..., ge=0)
    
    model_config = {"protected_namespaces": ()}

class WeatherForecastResponse(BaseModel):
    """Detailed weather forecast response."""
    location: str
    current_time: datetime
    timezone: str
    hourly_forecast: List[HourlyForecast]
    daily_forecast: List[DailyForecast]
    alerts: Optional[List[WeatherAlert]] = None
    
    model_config = {"protected_namespaces": ()}

# Error Response Models
class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    status_code: int

class ValidationErrorResponse(BaseModel):
    """Validation error response model."""
    error: str = "validation_error"
    details: List[Dict[str, Any]]
    status_code: int = 422

# Success Response Models
class SuccessResponse(BaseModel):
    """Generic success response model."""
    message: str
    status_code: int = 200
    data: Optional[Dict[str, Any]] = None