import numpy as np
import time
from typing import Dict, Any, Tuple, List
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
    
    def predict_heart_disease_risk(self, health_data: HealthDataInput) -> Dict[str, Any]:
        """Comprehensive heart disease risk assessment"""
        start_time = time.time()
        
        # Calculate multiple risk scores
        traditional_risk = self._calculate_traditional_cvd_risk(health_data)
        framingham_risk = self._calculate_framingham_score(health_data)
        ai_risk = self._calculate_ai_cvd_risk(health_data)
        
        # Combine assessments
        combined_risk = self._combine_risk_scores(traditional_risk, framingham_risk, ai_risk)
        
        # Identify specific risk factors
        risk_factors = self._identify_cvd_risk_factors(health_data)
        
        # Generate recommendations
        recommendations = self._generate_cvd_recommendations(combined_risk, risk_factors)
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "risk_level": combined_risk["level"],
            "risk_percentage": combined_risk["percentage"],
            "confidence_score": combined_risk["confidence"],
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "risk_scores": {
                "traditional": traditional_risk,
                "framingham": framingham_risk,
                "ai_based": ai_risk
            },
            "processing_time_ms": round(processing_time, 2)
        }
    
    def _calculate_traditional_cvd_risk(self, health_data: HealthDataInput) -> Dict[str, Any]:
        """Calculate traditional cardiovascular risk factors"""
        risk_score = 0
        factors = []
        
        # Age risk
        if health_data.age >= 65:
            risk_score += 3
            factors.append("Age ≥65 years")
        elif health_data.age >= 55:
            risk_score += 2
            factors.append("Age 55-64 years")
        elif health_data.age >= 45:
            risk_score += 1
            factors.append("Age 45-54 years")
        
        # Hypertension
        if health_data.blood_pressure_systolic >= 140 or health_data.blood_pressure_diastolic >= 90:
            risk_score += 3
            factors.append("Hypertension (≥140/90 mmHg)")
        elif health_data.blood_pressure_systolic >= 130 or health_data.blood_pressure_diastolic >= 85:
            risk_score += 2
            factors.append("Prehypertension")
        
        # Cholesterol
        if health_data.cholesterol >= 240:
            risk_score += 3
            factors.append("High cholesterol (≥240 mg/dL)")
        elif health_data.cholesterol >= 200:
            risk_score += 2
            factors.append("Borderline high cholesterol")
        
        # Heart rate
        if health_data.heart_rate > 100:
            risk_score += 2
            factors.append("Elevated resting heart rate")
        
        # Low SpO2 as cardiovascular risk indicator
        if health_data.spo2 < 95:
            risk_score += 2
            factors.append("Low oxygen saturation (<95%)")
        
        # Determine risk level
        if risk_score >= 10:
            level = "very_high"
        elif risk_score >= 7:
            level = "high"
        elif risk_score >= 4:
            level = "moderate"
        else:
            level = "low"
        
        return {"score": risk_score, "level": level, "factors": factors}
    
    def _calculate_framingham_score(self, health_data: HealthDataInput) -> Dict[str, Any]:
        """Simplified Framingham Risk Score calculation"""
        # Using coefficients for 10-year CVD risk (male coefficients)
        # Note: This is simplified without HDL, smoking status
        
        age_factor = health_data.age * 0.0483
        chol_factor = np.log(health_data.cholesterol) * 0.6545
        bp_factor = np.log(health_data.blood_pressure_systolic) * 0.0221
        
        # Assume average HDL of 50
        hdl_factor = np.log(50) * -0.8396
        
        sum_factors = age_factor + chol_factor + bp_factor + hdl_factor
        
        # Calculate 10-year risk percentage
        risk_percentage = 100 * (1 - 0.88936 ** np.exp(sum_factors - 3.0618))
        risk_percentage = max(1, min(30, risk_percentage))
        
        if risk_percentage >= 20:
            level = "high"
        elif risk_percentage >= 10:
            level = "moderate"
        else:
            level = "low"
        
        return {
            "percentage": round(risk_percentage, 1),
            "level": level,
            "note": "Simplified calculation without HDL/smoking data"
        }
    
    def _calculate_ai_cvd_risk(self, health_data: HealthDataInput) -> Dict[str, Any]:
        """AI-based cardiovascular risk using ML patterns"""
        if self.models_loaded and self.ml_models.rf_model is not None:
            # Use the ML model specifically for CVD risk
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
                prediction, confidence = self.ml_models.predict_rf(features)
                
                # Map prediction to CVD risk
                if prediction == 2:  # Critical
                    risk_percentage = 25.0
                    level = "high"
                elif prediction == 1:  # Warning
                    risk_percentage = 15.0
                    level = "moderate"
                else:  # Normal
                    risk_percentage = 5.0
                    level = "low"
                
                return {
                    "percentage": risk_percentage,
                    "level": level,
                    "confidence": float(confidence),
                    "ml_based": True
                }
            except:
                pass
        
        # Fallback: Pattern-based assessment
        risk_score = 0
        
        # High BP + High Cholesterol pattern
        if (health_data.blood_pressure_systolic >= 130 and 
            health_data.cholesterol >= 200):
            risk_score += 4
        
        # Age + multiple factors pattern
        if health_data.age >= 50:
            risk_count = sum([
                health_data.blood_pressure_systolic >= 130,
                health_data.cholesterol >= 200,
                health_data.heart_rate > 80,
                health_data.spo2 < 96
            ])
            risk_score += risk_count * 1.5
        
        # Abnormal vitals combination
        if (health_data.heart_rate > 90 and health_data.spo2 < 95):
            risk_score += 3
        
        risk_percentage = min(30, risk_score * 3.5)
        
        if risk_percentage >= 20:
            level = "high"
        elif risk_percentage >= 10:
            level = "moderate"
        else:
            level = "low"
        
        return {
            "percentage": round(risk_percentage, 1),
            "level": level,
            "confidence": 0.75,
            "ml_based": False
        }
    
    def _combine_risk_scores(self, traditional: Dict, framingham: Dict, ai: Dict) -> Dict[str, Any]:
        """Combine multiple risk assessment methods"""
        weights = {"traditional": 0.3, "framingham": 0.4, "ai": 0.3}
        level_scores = {"low": 1, "moderate": 2, "high": 3, "very_high": 4}
        
        weighted_score = (
            level_scores.get(traditional["level"], 1) * weights["traditional"] +
            level_scores.get(framingham["level"], 1) * weights["framingham"] +
            level_scores.get(ai["level"], 1) * weights["ai"]
        )
        
        if weighted_score >= 3.5:
            final_level = "Very High"
        elif weighted_score >= 2.5:
            final_level = "High"
        elif weighted_score >= 1.5:
            final_level = "Moderate"
        else:
            final_level = "Low"
        
        # Average percentage from methods that provide it
        percentages = []
        if "percentage" in framingham:
            percentages.append(framingham["percentage"])
        if "percentage" in ai:
            percentages.append(ai["percentage"])
        
        avg_percentage = np.mean(percentages) if percentages else 10.0
        
        # Calculate confidence
        confidence = ai.get("confidence", 0) if ai.get("confidence", 0) > 0 else 0.8
        
        return {
            "level": final_level,
            "percentage": round(avg_percentage, 1),
            "confidence": confidence,
            "description": f"{final_level} Risk ({avg_percentage:.1f}% 10-year risk)"
        }
    
    def _identify_cvd_risk_factors(self, health_data: HealthDataInput) -> List[Dict[str, Any]]:
        """Identify specific cardiovascular risk factors"""
        risk_factors = []
        
        # Major modifiable risk factors
        if health_data.blood_pressure_systolic >= 140 or health_data.blood_pressure_diastolic >= 90:
            risk_factors.append({
                "factor": "Hypertension",
                "severity": "Major",
                "value": f"{health_data.blood_pressure_systolic}/{health_data.blood_pressure_diastolic} mmHg",
                "target": "<120/80 mmHg",
                "modifiable": True
            })
        
        if health_data.cholesterol >= 240:
            risk_factors.append({
                "factor": "High Cholesterol",
                "severity": "Major",
                "value": f"{health_data.cholesterol} mg/dL",
                "target": "<200 mg/dL",
                "modifiable": True
            })
        
        # Non-modifiable risk factors
        if health_data.age >= 65:
            risk_factors.append({
                "factor": "Advanced Age",
                "severity": "Major",
                "value": f"{health_data.age} years",
                "target": "N/A",
                "modifiable": False
            })
        
        # Additional risk indicators
        if health_data.heart_rate > 80:
            risk_factors.append({
                "factor": "Elevated Resting Heart Rate",
                "severity": "Minor",
                "value": f"{health_data.heart_rate} BPM",
                "target": "60-80 BPM",
                "modifiable": True
            })
        
        if health_data.spo2 < 95:
            risk_factors.append({
                "factor": "Low Oxygen Saturation",
                "severity": "Minor",
                "value": f"{health_data.spo2}%",
                "target": ">95%",
                "modifiable": True
            })
        
        # Sort by severity
        risk_factors.sort(key=lambda x: 0 if x["severity"] == "Major" else 1)
        
        return risk_factors
    
    def _generate_cvd_recommendations(self, risk_assessment: Dict, risk_factors: List[Dict]) -> List[str]:
        """Generate personalized cardiovascular health recommendations"""
        recommendations = []
        
        # Risk level based recommendations
        if risk_assessment["level"] in ["High", "Very High"]:
            recommendations.append("🚨 Schedule an appointment with a cardiologist within 2 weeks")
            recommendations.append("📊 Request complete cardiac workup including ECG and stress test")
        elif risk_assessment["level"] == "Moderate":
            recommendations.append("👨‍⚕️ Discuss cardiovascular risk with your primary care physician")
            recommendations.append("📋 Consider preventive cardiology consultation")
        
        # Factor-specific recommendations
        has_hypertension = any(f["factor"] == "Hypertension" for f in risk_factors)
        has_high_chol = any(f["factor"] == "High Cholesterol" for f in risk_factors)
        has_high_hr = any(f["factor"] == "Elevated Resting Heart Rate" for f in risk_factors)
        
        if has_hypertension:
            recommendations.append("🩺 Monitor blood pressure daily and maintain a log")
            recommendations.append("🧂 Reduce sodium intake to <2,300mg per day")
            recommendations.append("💊 Discuss blood pressure medications with your doctor")
        
        if has_high_chol:
            recommendations.append("🥗 Adopt a heart-healthy diet (Mediterranean or DASH)")
            recommendations.append("🏃‍♂️ Engage in 150 minutes of moderate exercise weekly")
            recommendations.append("💊 Consider statin therapy if lifestyle changes insufficient")
        
        if has_high_hr:
            recommendations.append("🧘‍♂️ Practice stress reduction techniques (meditation, yoga)")
            recommendations.append("☕ Limit caffeine and stimulant intake")
        
        # General recommendations for everyone
        if risk_assessment["level"] != "Low":
            recommendations.append("🚭 If you smoke, seek help to quit immediately")
            recommendations.append("⚖️ Maintain a healthy weight (BMI 18.5-24.9)")
            recommendations.append("😴 Ensure 7-9 hours of quality sleep nightly")
        
        return recommendations[:6]  # Return top 6 recommendations

