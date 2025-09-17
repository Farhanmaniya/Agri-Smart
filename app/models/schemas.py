"""
Database and API schemas for AgriSmart Backend.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: str
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class PredictionType(str, Enum):
    PEST = "pest"
    RAINFALL = "rainfall"
    SOIL = "soil"
    CROP_YIELD = "crop_yield"

class BasePredictionRequest(BaseModel):
    user_id: Optional[str] = None
    location: Optional[Dict[str, float]] = None
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)

class PestPredictionRequest(BasePredictionRequest):
    image_url: str
    crop_type: str

class RainfallPredictionRequest(BasePredictionRequest):
    temperature: float
    humidity: float
    pressure: float
    wind_speed: float
    cloud_cover: float

class SoilTypePredictionRequest(BasePredictionRequest):
    nitrogen: float
    phosphorus: float
    potassium: float
    ph: float
    moisture: float

class PredictionResponse(BaseModel):
    id: str
    prediction_type: PredictionType
    result: Dict[str, Any]
    confidence: float
    created_at: datetime
    user_id: Optional[str]

class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None

# Database Table Schemas (for reference)
"""
CREATE TABLE users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE predictions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    prediction_type VARCHAR(50) NOT NULL,
    input_data JSONB NOT NULL,
    result JSONB NOT NULL,
    confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    location JSONB
);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can read their own data" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can read their own predictions" ON predictions
    FOR SELECT USING (auth.uid() = user_id);
"""