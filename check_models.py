#!/usr/bin/env python3
"""Check model features and requirements."""

import joblib
import os

def check_rainfall_model():
    """Check rainfall model features."""
    try:
        model = joblib.load('app/ml_models/saved_models/rainfall_model.joblib')
        print("Rainfall Model:")
        print(f"  Type: {type(model).__name__}")
        print(f"  Expected features: {model.n_features_in_ if hasattr(model, 'n_features_in_') else 'Unknown'}")
        print(f"  Feature names: {model.feature_names_in_ if hasattr(model, 'feature_names_in_') else 'No feature names'}")
        return model
    except Exception as e:
        print(f"Error loading rainfall model: {e}")
        return None

def check_soil_model():
    """Check soil model features."""
    try:
        model = joblib.load('app/ml_models/saved_models/soil_model.joblib')
        print("\nSoil Model:")
        print(f"  Type: {type(model).__name__}")
        print(f"  Expected features: {model.n_features_in_ if hasattr(model, 'n_features_in_') else 'Unknown'}")
        print(f"  Feature names: {model.feature_names_in_ if hasattr(model, 'feature_names_in_') else 'No feature names'}")
        return model
    except Exception as e:
        print(f"Error loading soil model: {e}")
        return None

if __name__ == "__main__":
    print("Checking model features...")
    rainfall_model = check_rainfall_model()
    soil_model = check_soil_model()
