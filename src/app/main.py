"""
AgriSmart Backend - Smart Irrigation and Crop Monitoring System
SIH25044 - Smart India Hackathon 2025

FastAPI application for AI-powered agriculture management system.
Handles authentication, ML predictions, irrigation scheduling, analytics,
weather monitoring, soil health, crop yield predictions, and market data.
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv
import time

from apis import (
    auth,
    predictions,
    irrigation,
    dashboard,
    weather,
    crop_yield,
    soil_health,
    market_data
)
from utils.logging import setup_logger
from database import init_database, check_database_connection

# Load environment variables
load_dotenv()

# Initialize logger
logger = setup_logger(__name__)

# Create FastAPI instance
app = FastAPI(
    title="AgriSmart API",
    description="AI-powered agriculture management system for Smart India Hackathon 2025",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS Configuration
origins = [
    "https://agrismart-phi.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://localhost:3000",
    "http://localhost:4028"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Middleware for request timing
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers and handle errors globally."""
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error": str(e) if os.getenv("DEBUG", "false").lower() == "true" else None
            }
        )

# Include routers with dependencies and error handlers
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"],
    responses={401: {"description": "Authentication failed"}}
)
app.include_router(
    predictions.router,
    prefix="/api/predictions",
    tags=["Predictions"],
    responses={500: {"description": "ML model error"}}
)
app.include_router(
    irrigation.router,
    prefix="/api/irrigation",
    tags=["Irrigation"],
    responses={503: {"description": "Irrigation system unavailable"}}
)
app.include_router(
    dashboard.router,
    prefix="/api/dashboard",
    tags=["Dashboard"],
    responses={404: {"description": "Data not found"}}
)
app.include_router(
    weather.router,
    prefix="/api/weather",
    tags=["Weather"],
    responses={503: {"description": "Weather service unavailable"}}
)
app.include_router(
    crop_yield.router,
    prefix="/api/crop-yield",
    tags=["Crop Yield"],
    responses={500: {"description": "Prediction error"}}
)
app.include_router(
    soil_health.router,
    prefix="/api/soil-health",
    tags=["Soil Health"],
    responses={500: {"description": "Soil analysis error"}}
)
app.include_router(
    market_data.router,
    prefix="/api/market-data",
    tags=["Market Data"],
    responses={503: {"description": "Market data service unavailable"}}
)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting AgriSmart Backend...")
    
    # Initialize database and verify connection
    try:
        await init_database()
        if not await check_database_connection():
            raise Exception("Database connection check failed")
        logger.info("Database initialization completed")
        
        # Initialize ML models and verify
        from app.services.ml import init_ml_models
        await init_ml_models()
        logger.info("ML models initialized successfully")
        
    except Exception as e:
        logger.error(f"Startup initialization failed: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down AgriSmart Backend...")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AgriSmart API - Smart Irrigation and Crop Monitoring System",
        "version": "1.0.0",
        "project": "SIH25044",
        "hackathon": "Smart India Hackathon 2025",
        "documentation": "/api/docs",
        "endpoints": {
            "auth": "/api/auth",
            "predictions": "/api/predictions", 
            "irrigation": "/api/irrigation",
            "dashboard": "/api/dashboard",
            "weather": "/api/weather",
            "soil_health": "/api/soil-health",
            "crop_yield": "/api/crop-yield",
            "market_data": "/api/market-data"
        },
        "ml_models": {
            "pest_detection": "pest_model.h5 (TensorFlow/Keras)",
            "rainfall_prediction": "rainfall_model.joblib (scikit-learn)",
            "soil_classification": "soil_model.joblib (scikit-learn)"
        },
        "features": {
            "weather_monitoring": "Real-time weather data and forecasts",
            "soil_health": "Soil quality monitoring and recommendations",
            "crop_yield": "AI-powered yield predictions",
            "market_data": "Crop prices and market trends",
            "irrigation": "Smart irrigation scheduling",
            "pest_detection": "AI-based pest detection",
            "analytics": "Comprehensive agricultural analytics"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check database connection
        db_status = "connected" if await check_database_connection() else "disconnected"
        
        # Check ML models
        from app.services.ml import check_ml_models
        ml_status = "ready" if await check_ml_models() else "not ready"
        
        status = "healthy" if db_status == "connected" and ml_status == "ready" else "degraded"
        
        return {
            "status": status,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "database": db_status,
            "ml_models": ml_status,
            "version": "1.0.0",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e) if os.getenv("DEBUG", "false").lower() == "true" else "Health check failed"
        }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )
