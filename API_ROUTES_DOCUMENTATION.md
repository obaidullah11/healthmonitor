# API Routes Documentation - Health Monitoring System

## Overview

This document provides a clear overview of all routes available in the Health Monitoring System, including REST API endpoints and frontend routes.

---

## 🔗 REST API Routes

### Base URL
```
http://localhost:8000
```

### API Version Prefix
```
/api/v1
```

---

## 📍 API Endpoints

### 1. Root Endpoint
**GET /**
- **Description**: API information and health check links
- **Authentication**: None required
- **Response**:
```json
{
  "message": "Health Monitoring System API",
  "version": "1.0.0",
  "docs": "/docs",
  "health_check": "/api/v1/health"
}
```

---

### 2. Health Prediction 🏥
**POST /api/v1/predict-health**
- **Description**: Analyze health parameters and predict status
- **Request Body**:
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
- **Response**:
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
      },
      "risk_factors": {
        "critical": [],
        "warning": []
      }
    }
  }
}
```

---

### 3. System Health Check ✅
**GET /api/v1/health**
- **Description**: Check API and model status
- **Response**:
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

---

### 4. Model Comparison 🤖
**POST /api/v1/compare-models**
- **Description**: Compare predictions from all available models
- **Request Body**: Same as `/predict-health`
- **Response**:
```json
{
  "success": true,
  "message": "Model comparison completed successfully",
  "data": {
    "input_data": {
      "heart_rate": 75,
      "temperature": 36.8,
      "spo2": 98,
      "age": 35,
      "blood_pressure_systolic": 120,
      "blood_pressure_diastolic": 80,
      "cholesterol": 180
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

---

### 5. Model Information ℹ️
**GET /api/v1/model-info**
- **Description**: Get information about available models
- **Response**:
```json
{
  "success": true,
  "message": "Model information retrieved successfully",
  "data": {
    "models_loaded": true,
    "available_models": [
      {
        "name": "Random Forest",
        "type": "ensemble",
        "advantages": ["Fast inference", "Good interpretability", "Handles missing data"],
        "best_for": "Real-time predictions with good accuracy"
      },
      {
        "name": "Neural Network",
        "type": "deep_learning",
        "advantages": ["Better pattern recognition", "Scalable", "Optimized for edge devices"],
        "best_for": "Complex patterns and edge deployment"
      },
      {
        "name": "Rule-based",
        "type": "fallback",
        "advantages": ["Always available", "Fast", "Interpretable"],
        "best_for": "Fallback when ML models are unavailable"
      }
    ]
  }
}
```

---

### 6. Input Validation 🔍
**POST /api/v1/validate-input**
- **Description**: Validate health data without making predictions
- **Request Body**: Same as `/predict-health`
- **Response**:
```json
{
  "success": true,
  "message": "Input validation completed",
  "data": {
    "is_valid": true,
    "errors": [],
    "warnings": [],
    "input_data": {
      "heart_rate": 75,
      "temperature": 36.8,
      "spo2": 98,
      "age": 35,
      "blood_pressure_systolic": 120,
      "blood_pressure_diastolic": 80,
      "cholesterol": 180
    }
  }
}
```

---

## 📱 Frontend Routes & API Integration

### Frontend File Structure
```
frontend/
├── index.html      # Main page
├── styles.css      # Styling
└── script.js       # API integration
```

### Frontend → API Communication Flow

```javascript
// 1. User enters data in form
// 2. Frontend validates input
// 3. Frontend makes API call

class HealthMonitor {
    apiBaseUrl = 'http://localhost:8000/api/v1';
    
    // Main prediction call
    async predictHealth(healthData) {
        const response = await fetch(`${this.apiBaseUrl}/predict-health`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(healthData)
        });
        return response.json();
    }
    
    // Health check
    async checkAPIHealth() {
        const response = await fetch(`${this.apiBaseUrl}/health`);
        return response.json();
    }
    
    // Model comparison
    async compareModels(healthData) {
        const response = await fetch(`${this.apiBaseUrl}/compare-models`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(healthData)
        });
        return response.json();
    }
}
```

---

## 🔄 API Documentation Routes

### Interactive API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📊 Route Summary Table

| Method | Endpoint | Purpose | Input Required |
|--------|----------|---------|----------------|
| GET | / | API info | No |
| GET | /api/v1/health | System health | No |
| POST | /api/v1/predict-health | Health prediction | Yes (7 params) |
| POST | /api/v1/compare-models | Model comparison | Yes (7 params) |
| GET | /api/v1/model-info | Model details | No |
| POST | /api/v1/validate-input | Input validation | Yes (7 params) |
| GET | /docs | Swagger UI | No |
| GET | /redoc | ReDoc UI | No |

---

## 🚀 Quick Start Examples

### Using cURL

#### Health Prediction
```bash
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
```

#### System Health Check
```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

### Using JavaScript (Frontend)

```javascript
// Initialize health data
const healthData = {
    heart_rate: parseFloat(document.getElementById('heartRate').value),
    temperature: parseFloat(document.getElementById('temperature').value),
    spo2: parseFloat(document.getElementById('spo2').value),
    age: parseInt(document.getElementById('age').value),
    blood_pressure_systolic: parseFloat(document.getElementById('bpSystolic').value),
    blood_pressure_diastolic: parseFloat(document.getElementById('bpDiastolic').value),
    cholesterol: parseFloat(document.getElementById('cholesterol').value)
};

// Make API call
fetch('http://localhost:8000/api/v1/predict-health', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(healthData)
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('Health Status:', data.data.health_status);
        console.log('Confidence:', data.data.confidence_score);
        console.log('Action:', data.data.suggested_action);
    }
});
```

---

## 🔒 Error Responses

All endpoints return standardized error responses:

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "data": null
}
```

### Common Error Codes
- `VALIDATION_ERROR`: Invalid input parameters
- `PREDICTION_ERROR`: Model prediction failed
- `INTERNAL_ERROR`: Server error
- `MODEL_INFO_ERROR`: Cannot retrieve model information

---

## 📝 Notes

1. **CORS**: Enabled for all origins (configure for production)
2. **Response Time**: All endpoints target <500ms response
3. **Content Type**: All POST requests require `Content-Type: application/json`
4. **Validation**: Input validation occurs at multiple levels
5. **Model Selection**: API automatically selects best available model

---

## 🔧 Testing the Routes

### 1. Start the API Server
```bash
python main.py
```

### 2. Open Frontend
Open `frontend/index.html` in your browser

### 3. Access API Documentation
Navigate to http://localhost:8000/docs

### 4. Test Endpoints
Use the Swagger UI or the frontend interface to test all endpoints

---

*This documentation covers all available routes in the Health Monitoring System API v1.0.0*

