from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any
import time

from app.models.health_model import HealthDataInput, APIResponse, HealthPrediction
from app.services.prediction_service import PredictionService
from app.utils.validators import validate_health_data

# Initialize router
router = APIRouter()

# Initialize prediction service
prediction_service = PredictionService()

@router.post("/predict-health", response_model=APIResponse)
async def predict_health_status(health_data: HealthDataInput):
    """
    Predict health status based on input vital signs.
    
    This endpoint accepts heart rate, body temperature, and blood oxygen level
    and returns a health status prediction with confidence score and suggested action.
    
    **Parameters:**
    - heart_rate: Heart rate in BPM (30-200)
    - temperature: Body temperature in Celsius (35.0-42.0)
    - spo2: Blood oxygen level in percentage (70-100)
    
    **Returns:**
    - health_status: Normal, Warning, or Critical
    - confidence_score: Prediction confidence (0.0-1.0)
    - suggested_action: Recommended action based on prediction
    - prediction_details: Additional prediction information
    """
    try:
        # Validate input data
        validation_result = validate_health_data(health_data)
        if not validation_result["valid"]:
            return APIResponse(
                success=False,
                message="Invalid input data",
                error_code="VALIDATION_ERROR",
                data={"errors": validation_result["errors"]}
            )
        
        # Make prediction
        prediction = prediction_service.predict_health_status(health_data)
        
        # Also get heart disease risk assessment
        cvd_risk = prediction_service.predict_heart_disease_risk(health_data)
        
        # Check if prediction time exceeds threshold
        prediction_time = prediction.prediction_details["prediction_time_ms"]
        if prediction_time > 500:
            print(f"Warning: Prediction time ({prediction_time}ms) exceeds 500ms threshold")
        
        # Prepare heart disease summary
        heart_disease_summary = {
            "risk_level": cvd_risk["risk_level"],
            "risk_percentage": cvd_risk["risk_percentage"],
            "major_risk_factors": [
                factor["factor"] for factor in cvd_risk["risk_factors"] 
                if factor["severity"] == "Major"
            ][:3],  # Top 3 major risk factors
            "primary_recommendation": cvd_risk["recommendations"][0] if cvd_risk["recommendations"] else None
        }
        
        return APIResponse(
            success=True,
            message="Health prediction completed successfully",
            data={
                "health_status": prediction.health_status,
                "confidence_score": prediction.confidence_score,
                "suggested_action": prediction.suggested_action,
                "prediction_details": prediction.prediction_details,
                "heart_disease_assessment": heart_disease_summary
            }
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Error processing prediction: {str(e)}",
            error_code="PREDICTION_ERROR"
        )

@router.get("/health", response_model=APIResponse)
async def health_check():
    """
    Health check endpoint for the API service.
    
    Returns the status of the API and loaded ML models.
    """
    try:
        model_status = prediction_service.get_model_status()
        
        return APIResponse(
            success=True,
            message="API is healthy and running",
            data={
                "api_status": "healthy",
                "model_status": model_status,
                "timestamp": time.time()
            }
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Health check failed: {str(e)}",
            error_code="HEALTH_CHECK_ERROR"
        )

@router.post("/compare-models", response_model=APIResponse)
async def compare_model_predictions(health_data: HealthDataInput):
    """
    Compare predictions from all available models.
    
    This endpoint returns predictions from all loaded models (Random Forest,
    Neural Network, and rule-based fallback) for comparison purposes.
    """
    try:
        # Validate input data
        validation_result = validate_health_data(health_data)
        if not validation_result["valid"]:
            return APIResponse(
                success=False,
                message="Invalid input data",
                error_code="VALIDATION_ERROR",
                data={"errors": validation_result["errors"]}
            )
        
        # Get predictions from all models
        comparisons = prediction_service.compare_predictions(health_data)
        
        return APIResponse(
            success=True,
            message="Model comparison completed successfully",
            data={
                "input_data": {
                    "heart_rate": health_data.heart_rate,
                    "temperature": health_data.temperature,
                    "spo2": health_data.spo2
                },
                "model_predictions": comparisons
            }
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Error comparing models: {str(e)}",
            error_code="COMPARISON_ERROR"
        )

@router.post("/predict-heart-disease", response_model=APIResponse)
async def predict_heart_disease_risk(health_data: HealthDataInput):
    """
    Predict cardiovascular disease risk using multiple assessment methods.
    
    This endpoint provides specialized heart disease risk assessment using:
    - Traditional cardiovascular risk factors
    - Modified Framingham Risk Score
    - AI-based pattern recognition
    - Cleveland Heart Disease Dataset patterns
    
    **Parameters:**
    - heart_rate: Heart rate in BPM (30-200)
    - temperature: Body temperature in Celsius (35.0-42.0)
    - spo2: Blood oxygen level in percentage (70-100)
    - age: Age in years (1-120)
    - blood_pressure_systolic: Systolic BP (70-250 mmHg)
    - blood_pressure_diastolic: Diastolic BP (40-150 mmHg)
    - cholesterol: Total cholesterol (100-400 mg/dL)
    
    **Returns:**
    - risk_level: Low/Moderate/High/Very High
    - risk_percentage: 10-year cardiovascular risk percentage
    - risk_factors: Identified cardiovascular risk factors
    - recommendations: Personalized heart health recommendations
    - risk_scores: Detailed breakdown of risk assessments
    """
    try:
        # Validate input data
        validation_result = validate_health_data(health_data)
        if not validation_result["valid"]:
            return APIResponse(
                success=False,
                message="Invalid input data",
                error_code="VALIDATION_ERROR",
                data={"errors": validation_result["errors"]}
            )
        
        # Calculate heart disease risk
        risk_assessment = prediction_service.predict_heart_disease_risk(health_data)
        
        return APIResponse(
            success=True,
            message="Heart disease risk assessment completed",
            data=risk_assessment
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Error assessing heart disease risk: {str(e)}",
            error_code="HEART_DISEASE_PREDICTION_ERROR"
        )

@router.get("/model-info", response_model=APIResponse)
async def get_model_information():
    """
    Get information about available models and their performance.
    
    Returns details about loaded models, their status, and performance metrics.
    """
    try:
        model_status = prediction_service.get_model_status()
        
        # Add model information
        model_info = {
            "models_loaded": model_status["models_loaded"],
            "available_models": [],
            "recommendations": []
        }
        
        if model_status["random_forest_available"]:
            model_info["available_models"].append({
                "name": "Random Forest",
                "type": "ensemble",
                "advantages": ["Fast inference", "Good interpretability", "Handles missing data"],
                "best_for": "Real-time predictions with good accuracy"
            })
        
        if model_status["neural_network_available"]:
            model_info["available_models"].append({
                "name": "Neural Network",
                "type": "deep_learning",
                "advantages": ["Better pattern recognition", "Scalable", "Optimized for edge devices"],
                "best_for": "Complex patterns and edge deployment"
            })
        
        if model_status["fallback_available"]:
            model_info["available_models"].append({
                "name": "Rule-based",
                "type": "fallback",
                "advantages": ["Always available", "Fast", "Interpretable"],
                "best_for": "Fallback when ML models are unavailable"
            })
        
        return APIResponse(
            success=True,
            message="Model information retrieved successfully",
            data=model_info
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Error retrieving model information: {str(e)}",
            error_code="MODEL_INFO_ERROR"
        )

@router.post("/predict-complete-health", response_model=APIResponse)
async def predict_complete_health_assessment(health_data: HealthDataInput):
    """
    Unified comprehensive health assessment combining general health status and detailed CVD risk analysis.
    
    This endpoint provides a complete health evaluation including:
    - General health status classification (Normal/Warning/Critical)
    - Comprehensive cardiovascular disease risk assessment
    - Detailed risk factors and personalized recommendations
    - Combined processing from multiple assessment methods
    
    **Parameters:**
    - heart_rate: Heart rate in BPM (30-200)
    - temperature: Body temperature in Celsius (35.0-42.0)
    - spo2: Blood oxygen level in percentage (70-100)
    - age: Age in years (1-120)
    - blood_pressure_systolic: Systolic BP (70-250 mmHg)
    - blood_pressure_diastolic: Diastolic BP (40-150 mmHg)
    - cholesterol: Total cholesterol (100-400 mg/dL)
    
    **Returns:**
    - general_health_assessment: Quick health status with immediate recommendations
    - comprehensive_cvd_assessment: Detailed cardiovascular risk analysis
    - combined_meta: Processing metadata and API version info
    """
    try:
        start_time = time.time()
        
        # Validate input data
        validation_result = validate_health_data(health_data)
        if not validation_result["valid"]:
            return APIResponse(
                success=False,
                message="Invalid input data",
                error_code="VALIDATION_ERROR",
                data={"errors": validation_result["errors"]}
            )
        
        # Get general health assessment
        general_prediction = prediction_service.predict_health_status(health_data)
        
        # Get comprehensive CVD risk assessment
        cvd_assessment = prediction_service.predict_heart_disease_risk(health_data)
        
        # Calculate total processing time
        total_processing_time = (time.time() - start_time) * 1000
        
        # Combine results into unified response
        unified_response = {
            "general_health_assessment": {
                "health_status": general_prediction.health_status,
                "confidence_score": general_prediction.confidence_score,
                "suggested_action": general_prediction.suggested_action,
                "prediction_details": general_prediction.prediction_details,
                "risk_summary": {
                    "risk_level": cvd_assessment["risk_level"],
                    "risk_percentage": cvd_assessment["risk_percentage"],
                    "major_risk_factors": [
                        factor["factor"] for factor in cvd_assessment["risk_factors"] 
                        if factor["severity"] == "Major"
                    ][:3]  # Top 3 major risk factors
                }
            },
            "comprehensive_cvd_assessment": {
                "risk_level": cvd_assessment["risk_level"],
                "risk_percentage": cvd_assessment["risk_percentage"],
                "confidence_score": cvd_assessment["confidence_score"],
                "risk_factors": cvd_assessment["risk_factors"],
                "recommendations": cvd_assessment["recommendations"],
                "risk_scores": cvd_assessment["risk_scores"],
                "processing_time_ms": cvd_assessment["processing_time_ms"]
            },
            "combined_meta": {
                "api_version": "1.0.0",
                "total_processing_time_ms": round(total_processing_time, 2),
                "assessment_timestamp": time.time(),
                "models_used": {
                    "general_health": general_prediction.prediction_details.get("model_used", "unknown"),
                    "cvd_assessment": "multi_method_combined"
                },
                "input_parameters": {
                    "heart_rate": health_data.heart_rate,
                    "temperature": health_data.temperature,
                    "spo2": health_data.spo2,
                    "age": health_data.age,
                    "blood_pressure": f"{health_data.blood_pressure_systolic}/{health_data.blood_pressure_diastolic}",
                    "cholesterol": health_data.cholesterol
                }
            }
        }
        
        return APIResponse(
            success=True,
            message="Complete health assessment completed successfully",
            data=unified_response
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Error in complete health assessment: {str(e)}",
            error_code="COMPLETE_HEALTH_ASSESSMENT_ERROR"
        )

@router.post("/validate-input", response_model=APIResponse)
async def validate_input_data(health_data: HealthDataInput):
    """
    Validate health data input without making predictions.
    
    This endpoint can be used to validate input data before making predictions.
    """
    try:
        validation_result = validate_health_data(health_data)
        
        return APIResponse(
            success=validation_result["valid"],
            message="Input validation completed",
            data={
                "is_valid": validation_result["valid"],
                "errors": validation_result.get("errors", []),
                "warnings": validation_result.get("warnings", []),
                "input_data": {
                    "heart_rate": health_data.heart_rate,
                    "temperature": health_data.temperature,
                    "spo2": health_data.spo2
                }
            }
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Error validating input: {str(e)}",
            error_code="VALIDATION_ERROR"
        )

