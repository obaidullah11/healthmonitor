import numpy as np
import time
from typing import Dict, Any, Tuple
from app.models.health_model import HealthDataInput, HealthPrediction
from app.models.ml_models import HealthMLModels

class PredictionService:
    """Service for making health predictions using trained ML models"""
    
    def __init__(self):
        self.ml_models = HealthMLModels()
        self.status_mapping = {0: "Normal", 1: "Warning", 2: "Critical"}
        self.action_mapping = {
            "Normal": "Normal – no action needed",
            "Warning": "Monitor closely and consider consulting a doctor if symptoms persist",
            "Critical": "Seek immediate medical attention"
        }
        
        # Load models
        try:
            self.ml_models.load_models()
            self.models_loaded = True
        except Exception as e:
            print(f"Warning: Could not load models: {e}")
            self.models_loaded = False
    
    def predict_health_status(self, health_data: HealthDataInput) -> HealthPrediction:
        """Make health status prediction using the best available model"""
        start_time = time.time()
        
        if not self.models_loaded:
            # Fallback to rule-based prediction
            return self._rule_based_prediction(health_data)
        
        # Prepare features (6 features now)
        features = np.array([
            health_data.heart_rate, 
            health_data.temperature, 
            health_data.spo2,
            health_data.age,
            health_data.blood_pressure_systolic,
            health_data.blood_pressure_diastolic,
            health_data.cholesterol
        ])
        
        try:
            # Try Random Forest first (usually faster)
            if self.ml_models.rf_model is not None:
                prediction, confidence = self.ml_models.predict_rf(features)
                model_used = "random_forest"
            elif self.ml_models.nn_model is not None:
                prediction, confidence = self.ml_models.predict_nn(features)
                model_used = "neural_network"
            else:
                # Fallback to rule-based
                return self._rule_based_prediction(health_data)
            
            # Get health status
            health_status = self.status_mapping.get(prediction, "Normal")
            suggested_action = self.action_mapping.get(health_status, "Consult a doctor")
            
            # Calculate prediction time
            prediction_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            return HealthPrediction(
                health_status=health_status,
                confidence_score=float(confidence),
                suggested_action=suggested_action,
                prediction_details={
                    "model_used": model_used,
                    "prediction_time_ms": round(prediction_time, 2),
                    "features": {
                        "heart_rate": health_data.heart_rate,
                        "temperature": health_data.temperature,
                        "spo2": health_data.spo2,
                        "age": health_data.age,
                        "blood_pressure": f"{health_data.blood_pressure_systolic}/{health_data.blood_pressure_diastolic}",
                        "cholesterol": health_data.cholesterol
                    }
                }
            )
            
        except Exception as e:
            print(f"Error in ML prediction: {e}")
            # Fallback to rule-based prediction
            return self._rule_based_prediction(health_data)
    
    def _rule_based_prediction(self, health_data: HealthDataInput) -> HealthPrediction:
        """Enhanced rule-based prediction with all parameters"""
        start_time = time.time()
        
        critical_factors = []
        warning_factors = []
        
        # Age-adjusted heart rate check
        age = health_data.age
        if age < 18:
            hr_normal = (70, 110)
        elif age > 65:
            hr_normal = (60, 90)
        else:
            hr_normal = (60, 100)
        
        if health_data.heart_rate < hr_normal[0] - 20 or health_data.heart_rate > hr_normal[1] + 40:
            critical_factors.append("heart rate")
        elif not (hr_normal[0] <= health_data.heart_rate <= hr_normal[1]):
            warning_factors.append("heart rate")
        
        # Temperature check
        if health_data.temperature < 35.0 or health_data.temperature > 38.0:
            critical_factors.append("temperature")
        elif health_data.temperature < 36.1 or health_data.temperature > 37.2:
            warning_factors.append("temperature")
        
        # SpO2 check
        if health_data.spo2 < 90:
            critical_factors.append("oxygen level")
        elif health_data.spo2 < 95:
            warning_factors.append("oxygen level")
        
        # Blood pressure check
        if health_data.blood_pressure_systolic >= 140 or health_data.blood_pressure_diastolic >= 90:
            critical_factors.append("blood pressure")
        elif health_data.blood_pressure_systolic >= 120 or health_data.blood_pressure_diastolic >= 80:
            warning_factors.append("blood pressure")
        
        # Cholesterol check
        if health_data.cholesterol >= 240:
            critical_factors.append("cholesterol")
        elif health_data.cholesterol >= 200:
            warning_factors.append("cholesterol")
        
        # Determine overall status
        if critical_factors:
            health_status = "Critical"
            confidence = 0.9
            action = f"Seek immediate medical attention. Critical: {', '.join(critical_factors)}"
        elif len(warning_factors) >= 2:
            health_status = "Warning"
            confidence = 0.85
            action = f"Monitor closely and consult a doctor. Concerns: {', '.join(warning_factors)}"
        else:
            health_status = "Normal"
            confidence = 0.95
            action = "Normal – no immediate action needed. Continue regular check-ups."
        
        prediction_time = (time.time() - start_time) * 1000
        
        return HealthPrediction(
            health_status=health_status,
            confidence_score=confidence,
            suggested_action=action,
            prediction_details={
                "model_used": "rule_based",
                "prediction_time_ms": round(prediction_time, 2),
                "features": {
                    "heart_rate": health_data.heart_rate,
                    "temperature": health_data.temperature,
                    "spo2": health_data.spo2,
                    "age": health_data.age,
                    "blood_pressure": f"{health_data.blood_pressure_systolic}/{health_data.blood_pressure_diastolic}",
                    "cholesterol": health_data.cholesterol
                },
                "risk_factors": {
                    "critical": critical_factors,
                    "warning": warning_factors
                }
            }
        )
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get the status of loaded models"""
        return {
            "models_loaded": self.models_loaded,
            "random_forest_available": self.ml_models.rf_model is not None,
            "neural_network_available": self.ml_models.nn_model is not None,
            "fallback_available": True  # Rule-based fallback is always available
        }
    
    def compare_predictions(self, health_data: HealthDataInput) -> Dict[str, Any]:
        """Compare predictions from all available models"""
        results = {}
        
        # Rule-based prediction
        rule_prediction = self._rule_based_prediction(health_data)
        results["rule_based"] = {
            "health_status": rule_prediction.health_status,
            "confidence_score": rule_prediction.confidence_score,
            "prediction_time_ms": rule_prediction.prediction_details["prediction_time_ms"]
        }
        
        if not self.models_loaded:
            return results
        
        features = np.array([
            health_data.heart_rate, 
            health_data.temperature, 
            health_data.spo2,
            health_data.age,
            health_data.blood_pressure_systolic,
            health_data.blood_pressure_diastolic,
            health_data.cholesterol
        ])
        
        # Random Forest prediction
        if self.ml_models.rf_model is not None:
            try:
                start_time = time.time()
                prediction, confidence = self.ml_models.predict_rf(features)
                prediction_time = (time.time() - start_time) * 1000
                
                results["random_forest"] = {
                    "health_status": self.status_mapping.get(prediction, "Normal"),
                    "confidence_score": float(confidence),
                    "prediction_time_ms": round(prediction_time, 2)
                }
            except Exception as e:
                results["random_forest"] = {"error": str(e)}
        
        # Neural Network prediction
        if self.ml_models.nn_model is not None:
            try:
                start_time = time.time()
                prediction, confidence = self.ml_models.predict_nn(features)
                prediction_time = (time.time() - start_time) * 1000
                
                results["neural_network"] = {
                    "health_status": self.status_mapping.get(prediction, "Normal"),
                    "confidence_score": float(confidence),
                    "prediction_time_ms": round(prediction_time, 2)
                }
            except Exception as e:
                results["neural_network"] = {"error": str(e)}
        
        return results

