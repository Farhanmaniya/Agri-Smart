#!/usr/bin/env python3
"""
Test script to verify the integration with pre-trained models.
Run this script to test if the models are loading correctly.
"""

import sys
import os
import asyncio
import logging

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.ml import ml_service
from app.models.schemas import RainfallPredictionRequest, SoilTypePredictionRequest

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_model_loading():
    """Test if all models are loading correctly."""
    logger.info("Testing model loading...")
    
    # Get available models
    models = ml_service.get_available_models()
    logger.info(f"Available models: {list(models.keys())}")
    
    for model_name, config in models.items():
        logger.info(f"Model: {model_name}")
        logger.info(f"  Type: {config.get('type', 'Unknown')}")
        logger.info(f"  Algorithm: {config.get('algorithm', 'Unknown')}")
        logger.info(f"  Loaded: {config.get('loaded', False)}")
        logger.info(f"  Fallback: {config.get('fallback', False)}")
        logger.info("---")

async def test_rainfall_prediction():
    """Test rainfall prediction."""
    logger.info("Testing rainfall prediction...")
    
    try:
        request = RainfallPredictionRequest(
            year=2024,
            subdivision=1,
            month=6,
            current_rainfall=5.0
        )
        
        predictions, confidence, recommendations = await ml_service.predict_rainfall(request.dict())
        logger.info(f"Rainfall prediction: {predictions}")
        logger.info(f"Confidence: {confidence}")
        logger.info("✅ Rainfall prediction test passed")
        
    except Exception as e:
        logger.error(f"❌ Rainfall prediction test failed: {e}")

async def test_soil_prediction():
    """Test soil type prediction."""
    logger.info("Testing soil type prediction...")
    
    try:
        request = SoilTypePredictionRequest(
            nitrogen=40.0,
            phosphorus=30.0,
            potassium=35.0,
            temperature=25.0,
            moisture=25.0,
            humidity=60.0
        )
        
        predictions, confidence, recommendations = await ml_service.predict_soil_type(request.dict())
        logger.info(f"Soil prediction: {predictions}")
        logger.info(f"Confidence: {confidence}")
        logger.info("✅ Soil prediction test passed")
        
    except Exception as e:
        logger.error(f"❌ Soil prediction test failed: {e}")

async def main():
    """Run all tests."""
    logger.info("Starting AgriSmart Backend Model Integration Test")
    logger.info("=" * 50)
    
    await test_model_loading()
    await test_rainfall_prediction()
    await test_soil_prediction()
    
    logger.info("=" * 50)
    logger.info("Test completed!")

if __name__ == "__main__":
    asyncio.run(main())
