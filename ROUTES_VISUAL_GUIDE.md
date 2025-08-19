# Visual Route Guide - Health Monitoring System

## 🗺️ Route Map Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    HEALTH MONITORING SYSTEM                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Frontend (Browser)          API Server (FastAPI)           │
│  ┌─────────────────┐        ┌────────────────────┐        │
│  │  index.html     │        │  localhost:8000    │        │
│  │  ┌───────────┐  │        │                    │        │
│  │  │   Form    │  │───────►│  /api/v1/*         │        │
│  │  │ 6 inputs  │  │        │                    │        │
│  │  └───────────┘  │        └────────────────────┘        │
│  └─────────────────┘                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🚦 Frontend Routes (What Users See)

### Single Page Application
```
frontend/
└── index.html ──► Main Page
    ├── Input Form (6 health parameters)
    ├── Submit Button
    └── Results Display Area
```

### Frontend Flow
```
1. User Opens: frontend/index.html
                    ↓
2. User Enters: 6 Health Parameters
                    ↓
3. JavaScript: Validates Input
                    ↓
4. JavaScript: Calls API
                    ↓
5. Display: Results/Error
```

## 🛣️ API Routes (Backend Endpoints)

### Route Hierarchy
```
http://localhost:8000/
│
├── /                           [GET]  → API Info
├── /docs                       [GET]  → Swagger UI
├── /redoc                      [GET]  → ReDoc UI
│
└── /api/v1/
    ├── /health                 [GET]  → System Status
    ├── /predict-health         [POST] → Main Prediction
    ├── /compare-models         [POST] → Model Comparison
    ├── /model-info             [GET]  → Model Details
    └── /validate-input         [POST] → Input Validation
```

## 🔄 Request/Response Flow

### Main Prediction Flow
```
Frontend Form
    │
    ├─► Collect 6 Parameters:
    │   • Heart Rate (BPM)
    │   • Temperature (°C)
    │   • SpO2 (%)
    │   • Age (years)
    │   • Blood Pressure (mmHg)
    │   • Cholesterol (mg/dL)
    │
    ▼
JavaScript Validation
    │
    ▼
POST /api/v1/predict-health
    │
    ├─► API Validation
    ├─► ML Model Prediction
    ├─► Risk Analysis
    │
    ▼
Response (JSON)
    │
    ├─► Health Status
    ├─► Confidence Score
    ├─► Suggested Action
    └─► Risk Factors
```

## 📋 Route Quick Reference

### For Frontend Developers
```javascript
// Base configuration
const API_BASE = 'http://localhost:8000/api/v1';

// Available endpoints
const endpoints = {
    predict: `${API_BASE}/predict-health`,      // POST
    health: `${API_BASE}/health`,               // GET
    compare: `${API_BASE}/compare-models`,      // POST
    modelInfo: `${API_BASE}/model-info`,        // GET
    validate: `${API_BASE}/validate-input`      // POST
};
```

### For API Testing
```bash
# 1. Check if API is running
curl http://localhost:8000/api/v1/health

# 2. Get model information
curl http://localhost:8000/api/v1/model-info

# 3. Make a prediction
curl -X POST http://localhost:8000/api/v1/predict-health \
  -H "Content-Type: application/json" \
  -d @health_data.json
```

## 🎯 Route Purposes

| Route | What It Does | When To Use |
|-------|--------------|-------------|
| **/** | Shows API version and links | First-time connection |
| **/health** | Checks if system is working | Before making predictions |
| **/predict-health** | Main health analysis | Primary use case |
| **/compare-models** | Shows all model predictions | Testing/debugging |
| **/model-info** | Lists available models | Understanding system |
| **/validate-input** | Checks if input is valid | Pre-validation |

## 🔐 Route Security

### Current Setup
- ✅ CORS enabled (all origins)
- ✅ Input validation
- ✅ Error handling
- ⚠️ No authentication (add for production)

### Production Recommendations
```python
# Add to routes for production:
- Authentication headers
- Rate limiting
- API keys
- HTTPS only
```

## 📱 Frontend Integration Points

### HTML Form Elements
```html
<!-- Maps to API parameters -->
<input id="heartRate" name="heartRate">           → heart_rate
<input id="temperature" name="temperature">       → temperature
<input id="spo2" name="spo2">                    → spo2
<input id="age" name="age">                      → age
<input id="bpSystolic" name="bpSystolic">        → blood_pressure_systolic
<input id="bpDiastolic" name="bpDiastolic">      → blood_pressure_diastolic
<input id="cholesterol" name="cholesterol">       → cholesterol
```

### JavaScript API Calls
```javascript
// Route: POST /api/v1/predict-health
async function predictHealth() {
    const data = collectFormData();
    const response = await fetch(endpoints.predict, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return response.json();
}
```

## 🚀 Quick Start Guide

1. **Start Backend**
   ```bash
   cd "project_folder"
   python main.py
   ```

2. **Access Routes**
   - API Docs: http://localhost:8000/docs
   - Frontend: Open frontend/index.html

3. **Test Flow**
   - Fill form → Submit → See results
   - Check /health first
   - Use /docs for testing

## 📊 Route Response Times

| Route | Target | Actual |
|-------|--------|--------|
| /health | <100ms | ~10ms |
| /predict-health | <500ms | ~45ms |
| /compare-models | <500ms | ~150ms |
| /model-info | <100ms | ~5ms |
| /validate-input | <100ms | ~20ms |

---

*This visual guide shows all routes and their connections in the Health Monitoring System*
