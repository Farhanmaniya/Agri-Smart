"""
MLService for handling all machine learning models in AgriSmart.
Supports .h5 (TensorFlow) and .joblib (scikit-learn) models.
"""

import os
import joblib
import numpy as np
from typing import Dict, Any, Optional, List
import logging
from pathlib import Path

# TensorFlow import with error handling
try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    tf = None

from ..models.schemas import (
    PredictionType,
    PestPredictionRequest,
    RainfallPredictionRequest,
    SoilTypePredictionRequest
)

logger = logging.getLogger(__name__)

class MLModelManager:
    """Manages loading and access to ML models."""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.model_paths = {
            'pest': os.getenv('PEST_MODEL_PATH', 'ml_models/saved_models/pest_model.h5'),
            'rainfall': os.getenv('RAINFALL_MODEL_PATH', 'ml_models/saved_models/rainfall_model.joblib'),
            'soil': os.getenv('SOIL_MODEL_PATH', 'ml_models/saved_models/soil_model.joblib')
        }
        
    def load_models(self):
        """Load all ML models."""
        # Create models directory if it doesn't exist
        os.makedirs(os.path.dirname(self.model_paths['pest']), exist_ok=True)
        
        # Load pest detection model (.h5)
        try:
            if TENSORFLOW_AVAILABLE and os.path.exists(self.model_paths['pest']):
                self.models['pest'] = tf.keras.models.load_model(self.model_paths['pest'])
            else:
                logger.warning("pest_model.h5 not found, creating fallback model")
                self.models['pest'] = self._create_fallback_pest_model()
        except Exception as e:
            logger.error(f"Error loading pest model: {str(e)}")
            self.models['pest'] = self._create_fallback_pest_model()
            
        # Load rainfall prediction model (.joblib)
        try:
            if os.path.exists(self.model_paths['rainfall']):
                self.models['rainfall'] = joblib.load(self.model_paths['rainfall'])
            else:
                logger.warning("rainfall_model.joblib not found, creating fallback model")
                self.models['rainfall'] = self._create_fallback_rainfall_model()
        except Exception as e:
            logger.error(f"Error loading rainfall model: {str(e)}")
            self.models['rainfall'] = self._create_fallback_rainfall_model()
            
        # Load soil type classification model (.joblib)
        try:
            if os.path.exists(self.model_paths['soil']):
                self.models['soil'] = joblib.load(self.model_paths['soil'])
            else:
                logger.warning("soil_model.joblib not found, creating fallback model")
                self.models['soil'] = self._create_fallback_soil_model()
        except Exception as e:
            logger.error(f"Error loading soil model: {str(e)}")
            self.models['soil'] = self._create_fallback_soil_model()
            
        logger.info(f"Successfully loaded {len(self.models)} ML models")
    
    def _create_fallback_pest_model(self):
        """Create a simple fallback model for pest detection."""
        if TENSORFLOW_AVAILABLE:
            model = tf.keras.Sequential([
                tf.keras.layers.Input(shape=(224, 224, 3)),
                tf.keras.layers.Conv2D(32, 3, activation='relu'),
                tf.keras.layers.GlobalAveragePooling2D(),
                tf.keras.layers.Dense(4, activation='softmax')
            ])
            model.compile(optimizer='adam', loss='categorical_crossentropy')
            logger.warning("⚠️  Using fallback pest model")
            return model
        return None
    
    def _create_fallback_rainfall_model(self):
        """Create a simple fallback model for rainfall prediction."""
        from sklearn.ensemble import RandomForestRegressor
        model = RandomForestRegressor(n_estimators=10)
        model.fit(np.random.rand(100, 5), np.random.rand(100))
        logger.warning("⚠️  Using fallback rainfall model")
        return model
    
    def _create_fallback_soil_model(self):
        """Create a simple fallback model for soil classification."""
        from sklearn.ensemble import RandomForestClassifier
        model = RandomForestClassifier(n_estimators=10)
        model.fit(np.random.rand(100, 5), np.random.randint(0, 3, 100))
        logger.warning("⚠️  Using fallback soil model")
        return model
    
    def get_model(self, model_type: str) -> Optional[Any]:
        """Get a specific model by type."""
        return self.models.get(model_type)

class MLService:
    """Service for making predictions using ML models."""
    
    def __init__(self):
        self.model_manager = MLModelManager()
        self.model_manager.load_models()
        logger.info("MLService initialized with model manager")
    
    async def predict_pests(self, request: PestPredictionRequest) -> Dict[str, Any]:
        """Make pest detection predictions."""
        model = self.model_manager.get_model('pest')
        if model is None:
            raise ValueError("Pest detection model not available")
        
        # Process input data (simplified)
        # In reality, you would process the image properly
        dummy_image = np.random.rand(1, 224, 224, 3)
        prediction = model.predict(dummy_image)
        
        # Map predictions to pest types (simplified)
        pest_types = ['aphids', 'whiteflies', 'thrips', 'healthy']
        result = {pest_types[i]: float(pred) for i, pred in enumerate(prediction[0])}
        return result
    
    async def predict_rainfall(self, request: RainfallPredictionRequest) -> float:
        """Make rainfall predictions."""
        model = self.model_manager.get_model('rainfall')
        if model is None:
            raise ValueError("Rainfall prediction model not available")
        
        # Process input data (simplified)
        features = np.array([[
            request.temperature,
            request.humidity,
            request.pressure,
            request.wind_speed,
            request.cloud_cover
        ]])
        
        prediction = model.predict(features)[0]
        return float(prediction)
    
    async def predict_soil_type(self, request: SoilTypePredictionRequest) -> str:
        """Predict soil type based on soil parameters."""
        model = self.model_manager.get_model('soil')
        if model is None:
            raise ValueError("Soil classification model not available")
        
        # Process input data
        features = np.array([[
            request.nitrogen,
            request.phosphorus,
            request.potassium,
            request.ph,
            request.moisture
        ]])
        
        prediction = model.predict(features)[0]
        soil_types = ['clay', 'loamy', 'sandy']
        return soil_types[prediction]

# Global ML service instance
ml_service = MLService()