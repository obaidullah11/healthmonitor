# Heart Disease Risk Assessment System

An AI-powered cardiovascular disease risk assessment system that provides comprehensive heart disease risk predictions based on vital signs and health parameters. The system uses multiple risk assessment methods including traditional risk factors, Framingham Risk Score, and machine learning models to determine your 10-year cardiovascular disease risk.

## Features

- **Cardiovascular Risk Assessment**: Get comprehensive 10-year heart disease risk predictions
- **Multiple Risk Scoring Methods**: 
  - Traditional cardiovascular risk factors
  - Modified Framingham Risk Score
  - AI-based risk assessment using ML models
- **6 Key Health Parameters**: Heart rate, temperature, SpO2, age, blood pressure, and cholesterol
- **Personalized Recommendations**: Specific actionable advice based on your risk factors
- **Risk Factor Identification**: Identifies both modifiable and non-modifiable risk factors
- **Dual Prediction System**: Both general health status and specific heart disease risk
- **Cleveland Heart Disease Dataset**: Trained on real cardiovascular patient data
- **Modern Web Interface**: Beautiful, responsive frontend with detailed risk visualization
- **REST API**: Well-documented API with heart disease specific endpoints
- **Performance Optimized**: Sub-100ms response times for risk calculations

## System Architecture

```
Health Monitoring System/
├── Backend (FastAPI)
│   ├── REST API endpoints
│   ├── ML model management
│   ├── Data validation
│   └── Prediction service
├── Frontend (HTML/CSS/JS)
│   ├── Modern UI interface
│   ├── Real-time validation
│   └── Dynamic results display
└── ML Models
    ├── Random Forest (Scikit-learn)
    ├── Neural Network (TensorFlow Lite)
    └── Rule-based fallback
```

## Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd health-monitoring-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Train the models**
   ```bash
   python train_models.py
   ```

4. **Start the API server**
   ```bash
   python main.py
   ```

5. **Open the frontend**
   - Navigate to `frontend/index.html` in your browser
   - Or serve it using a local server

### Environment Variables

Create a `.env` file in the root directory:

```env
HOST=0.0.0.0
PORT=8000
DEBUG=False
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

## API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### 1. Health Prediction
**POST** `/predict-health`

Predict general health status based on vital signs.

#### 2. Heart Disease Risk Assessment
**POST** `/predict-heart-disease`

Comprehensive cardiovascular disease risk assessment.

**Request Body:**
```json
{
  "heart_rate": 85,
  "temperature": 36.8,
  "spo2": 96,
  "age": 55,
  "blood_pressure_systolic": 145,
  "blood_pressure_diastolic": 92,
  "cholesterol": 250
}
```

**Response:**
```json
{
  "success": true,
  "message": "Heart disease risk assessment completed",
  "data": {
    "risk_level": "High",
    "risk_percentage": 18.5,
    "confidence_score": 0.85,
    "risk_factors": [
      {
        "factor": "Hypertension",
        "severity": "Major",
        "value": "145/92 mmHg",
        "target": "<120/80 mmHg",
        "modifiable": true
      },
      {
        "factor": "High Cholesterol",
        "severity": "Major",
        "value": "250 mg/dL",
        "target": "<200 mg/dL",
        "modifiable": true
      }
    ],
    "recommendations": [
      "🚨 Schedule an appointment with a cardiologist within 2 weeks",
      "📊 Request complete cardiac workup including ECG and stress test",
      "🩺 Monitor blood pressure daily and maintain a log",
      "🥗 Adopt a heart-healthy diet (Mediterranean or DASH)",
      "💊 Discuss blood pressure and cholesterol medications with your doctor"
    ],
    "risk_scores": {
      "traditional": {"score": 8, "level": "high"},
      "framingham": {"percentage": 18.5, "level": "moderate"},
      "ai_based": {"percentage": 20.0, "level": "high", "ml_based": true}
    }
  }
}
```

**Request Body (Original Health Prediction):**
```json
{
  "heart_rate": 75,
  "temperature": 36.8,
  "spo2": 98,
  "age": 35,
  "blood_pressure_systolic": 120,
  "blood_pressure_diastolic": 80,
  "cholesterol": 180
}
```

**Response:**
```json
{
  "success": true,
  "message": "Health prediction completed successfully",
  "data": {
    "health_status": "Normal",
    "confidence_score": 0.95,
    "suggested_action": "Normal – no action needed",
    "prediction_details": {
      "model_used": "random_forest",
      "prediction_time_ms": 45.2,
                      "features": {
                    "heart_rate": 75,
                    "temperature": 36.8,
                    "spo2": 98,
                    "age": 35,
                    "blood_pressure": "120/80",
                    "cholesterol": 180
                }
    }
  }
}
```

#### 2. Health Check
**GET** `/health`

Check API and model status.

**Response:**
```json
{
  "success": true,
  "message": "API is healthy and running",
  "data": {
    "api_status": "healthy",
    "model_status": {
      "models_loaded": true,
      "random_forest_available": true,
      "neural_network_available": true,
      "fallback_available": true
    },
    "timestamp": 1640995200.0
  }
}
```

#### 3. Model Comparison
**POST** `/compare-models`

Compare predictions from all available models.

**Request Body:** Same as `/predict-health`

**Response:**
```json
{
  "success": true,
  "message": "Model comparison completed successfully",
  "data": {
    "input_data": {
      "heart_rate": 75,
      "temperature": 36.8,
      "spo2": 98
    },
    "model_predictions": {
      "rule_based": {
        "health_status": "Normal",
        "confidence_score": 0.95,
        "prediction_time_ms": 1.2
      },
      "random_forest": {
        "health_status": "Normal",
        "confidence_score": 0.92,
        "prediction_time_ms": 45.2
      },
      "neural_network": {
        "health_status": "Normal",
        "confidence_score": 0.89,
        "prediction_time_ms": 78.5
      }
    }
  }
}
```

#### 4. Model Information
**GET** `/model-info`

Get information about available models.

#### 5. Input Validation
**POST** `/validate-input`

Validate health data input without making predictions.

## Testing

### Using cURL

```bash
# Health prediction
curl -X POST "http://localhost:8000/api/v1/predict-health" \
  -H "Content-Type: application/json" \
  -d '{
    "heart_rate": 75,
    "temperature": 36.8,
    "spo2": 98,
    "age": 35,
    "blood_pressure_systolic": 120,
    "blood_pressure_diastolic": 80,
    "cholesterol": 180
  }'

# Health check
curl -X GET "http://localhost:8000/api/v1/health"

# Model comparison
curl -X POST "http://localhost:8000/api/v1/compare-models" \
  -H "Content-Type: application/json" \
  -d '{
    "heart_rate": 110,
    "temperature": 37.8,
    "spo2": 93,
    "age": 45,
    "blood_pressure_systolic": 140,
    "blood_pressure_diastolic": 90,
    "cholesterol": 220
  }'
```

### Using Postman

1. Import the following collection:

```json
{
  "info": {
    "name": "Health Monitoring API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Predict Health",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"heart_rate\": 75,\n  \"temperature\": 36.8,\n  \"spo2\": 98\n}"
        },
        "url": {
          "raw": "http://localhost:8000/api/v1/predict-health",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "v1", "predict-health"]
        }
      }
    },
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": {
          "raw": "http://localhost:8000/api/v1/health",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "v1", "health"]
        }
      }
    }
  ]
}
```

## Health Parameter Ranges

### Heart Rate (BPM)
- **Normal**: 60-100 (age-adjusted)
- **Warning**: 40-59 or 101-140
- **Critical**: <40 or >140
- **Valid Range**: 30-200

### Body Temperature (°C)
- **Normal**: 36.1-37.2
- **Warning**: 35.0-36.0 or 37.3-38.0
- **Critical**: <35.0 or >38.0
- **Valid Range**: 35.0-42.0

### Blood Oxygen Level (SpO₂ %)
- **Normal**: 95-100
- **Warning**: 90-94
- **Critical**: <90
- **Valid Range**: 70-100

### Age (years)
- **Valid Range**: 1-120
- **Age Groups**: Child (1-12), Teen (13-19), Adult (20-59), Senior (60+)

### Blood Pressure (mmHg)
- **Normal**: Systolic 90-120, Diastolic 60-80
- **Warning**: Systolic 121-139, Diastolic 81-89
- **Critical**: Systolic <90 or ≥140, Diastolic <60 or ≥90
- **Valid Range**: Systolic 70-250, Diastolic 40-150

### Total Cholesterol (mg/dL)
- **Normal**: <200
- **Warning**: 200-239
- **Critical**: ≥240
- **Valid Range**: 100-400

## Machine Learning Models

### Random Forest
- **Type**: Ensemble learning
- **Advantages**: Fast inference, good interpretability
- **Use Case**: Primary model for real-time predictions
- **Performance**: ~45ms inference time

### Neural Network
- **Type**: Deep learning (TensorFlow Lite)
- **Advantages**: Better pattern recognition, scalable
- **Use Case**: Secondary model for complex patterns
- **Performance**: ~80ms inference time

### Rule-based Fallback
- **Type**: Expert system
- **Advantages**: Always available, interpretable
- **Use Case**: Fallback when ML models unavailable
- **Performance**: ~1ms inference time

## Deployment

### Local Development
```bash
python main.py
```

### Production Deployment

#### Using Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

#### Using Cloud Platforms

**AWS Lambda + API Gateway:**
- Package the application as a Lambda function
- Configure API Gateway for REST API
- Set up environment variables

**Google Cloud Run:**
- Build and push Docker image
- Deploy to Cloud Run
- Configure environment variables

**PythonAnywhere:**
- Upload source code
- Install dependencies
- Configure WSGI file

## Performance

- **Response Time**: <500ms (target)
- **Model Loading**: ~2-3 seconds on startup
- **Memory Usage**: ~200MB (including models)
- **Concurrent Requests**: 100+ (depending on hardware)

## Security Considerations

- Input validation and sanitization
- Rate limiting (implement as needed)
- HTTPS enforcement in production
- Data encryption at rest
- HIPAA compliance framework (for medical use)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the health check endpoint at `/health`

## Roadmap

- [ ] Real-time data streaming
- [ ] Mobile app development
- [ ] Integration with wearable devices
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] User authentication and profiles
- [ ] Historical data tracking
- [ ] Alert system for critical values



