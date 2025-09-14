# AgriSmart Backend - Pre-trained Models Integration

This document describes the integration of pre-trained machine learning models in the AgriSmart backend system.

## Supported Model Formats

The backend now supports multiple model formats:
- **.h5** - TensorFlow/Keras models
- **.joblib** - scikit-learn models  
- **.pkl** - Pickle serialized models

## Pre-trained Models

The following pre-trained models are located in `app/ml_models/saved_models/`:

### 1. Pest Detection Model (`pest_model.h5`)
- **Format**: TensorFlow/Keras (.h5)
- **Type**: Image-based pest classification
- **Purpose**: Detect and classify crop pests from images
- **API Endpoint**: `POST /api/predictions/pest`

### 2. Rainfall Prediction Model (`rainfall_model.joblib`)
- **Format**: scikit-learn (.joblib)
- **Type**: Regression
- **Purpose**: Predict rainfall based on weather conditions
- **API Endpoint**: `POST /api/predictions/rainfall`
- **Input Features**:
  - Temperature (Celsius)
  - Humidity (%)
  - Atmospheric pressure (hPa)
  - Wind speed (km/h)
  - Month (1-12)
  - Day of year (1-365)

### 3. Soil Classification Model (`soil_model.joblib`)
- **Format**: scikit-learn (.joblib)
- **Type**: Classification
- **Purpose**: Classify soil type based on chemical properties
- **API Endpoint**: `POST /api/predictions/soil-type`
- **Input Features**:
  - pH level
  - Nitrogen content
  - Phosphorus content
  - Potassium content
  - Organic matter percentage
  - Soil moisture percentage
  - Soil temperature

## API Usage Examples

### Rainfall Prediction

```bash
curl -X POST "http://localhost:8000/api/predictions/rainfall" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "temperature": 25.0,
    "humidity": 60.0,
    "pressure": 1013.0,
    "wind_speed": 10.0,
    "month": 6,
    "day_of_year": 150
  }'
```

### Soil Type Prediction

```bash
curl -X POST "http://localhost:8000/api/predictions/soil-type" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "ph": 6.5,
    "nitrogen": 40.0,
    "phosphorus": 30.0,
    "potassium": 35.0,
    "organic_matter": 2.5,
    "moisture": 25.0,
    "temperature": 25.0
  }'
```

## Model Management

### List Available Models

```bash
curl -X GET "http://localhost:8000/api/predictions/models" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Add New Model

```bash
curl -X POST "http://localhost:8000/api/predictions/add-model" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "model_name": "my_model",
    "model_path": "/path/to/model.pkl",
    "model_type": "classifier"
  }'
```

## Fallback System

The system includes robust fallback mechanisms:

1. **Model Loading Fallbacks**: If a pre-trained model fails to load, the system creates a fallback model with similar functionality
2. **TensorFlow Fallback**: If TensorFlow is not available, .h5 models will use mock implementations
3. **Prediction Fallbacks**: If model prediction fails, the system provides heuristic-based predictions

## Dependencies

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Key ML dependencies:
- `scikit-learn>=1.3.2` - For .joblib model support
- `tensorflow>=2.15.0` - For .h5 model support (optional)
- `numpy>=1.24.3` - For numerical operations
- `pandas>=2.1.3` - For data manipulation
- `joblib>=1.3.2` - For model serialization

## Testing

Run the model integration test:

```bash
python test_models.py
```

This will test:
- Model loading functionality
- Rainfall prediction
- Soil type prediction
- Fallback mechanisms

## Model Configuration

Models are automatically configured based on their type and features. The system supports:

- **Auto-detection** of model types (classifier/regressor)
- **Feature extraction** from model metadata
- **Algorithm identification** from model objects
- **Input/output validation** based on model requirements

## Error Handling

The system provides comprehensive error handling:

- **Model loading errors**: Graceful fallback to mock models
- **Prediction errors**: Detailed error messages and logging
- **Validation errors**: Clear validation messages for input parameters
- **Dependency errors**: Warnings when optional dependencies are missing

## Performance Considerations

- Models are loaded once at startup for optimal performance
- Fallback models are lightweight and fast
- Prediction caching can be implemented for frequently requested predictions
- Memory usage is optimized for production deployment

## Security

- All model endpoints require authentication
- Input validation prevents malicious data injection
- Model files are stored securely in the application directory
- API responses include confidence scores for transparency
