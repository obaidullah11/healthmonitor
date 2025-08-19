from typing import Dict, List, Any
from app.models.health_model import HealthDataInput
from config import Config

def validate_health_data(health_data: HealthDataInput) -> Dict[str, Any]:
    """
    Comprehensive validation of health data input.
    
    Returns a dictionary with validation results including:
    - valid: Boolean indicating if data is valid
    - errors: List of validation errors
    - warnings: List of validation warnings
    """
    errors = []
    warnings = []
    
    # Get health ranges from config
    health_ranges = Config.get_health_ranges()
    
    # Validate heart rate
    if health_data.heart_rate < 30 or health_data.heart_rate > 200:
        errors.append(f"Heart rate ({health_data.heart_rate} BPM) is outside valid range (30-200 BPM)")
    elif health_data.heart_rate < 40 or health_data.heart_rate > 140:
        warnings.append(f"Heart rate ({health_data.heart_rate} BPM) is outside normal range (40-140 BPM)")
    
    # Validate temperature
    if health_data.temperature < 35.0 or health_data.temperature > 42.0:
        errors.append(f"Temperature ({health_data.temperature}°C) is outside valid range (35.0-42.0°C)")
    elif health_data.temperature < 36.0 or health_data.temperature > 37.5:
        warnings.append(f"Temperature ({health_data.temperature}°C) is outside normal range (36.0-37.5°C)")
    
    # Validate SpO2
    if health_data.spo2 < 70 or health_data.spo2 > 100:
        errors.append(f"SpO2 ({health_data.spo2}%) is outside valid range (70-100%)")
    elif health_data.spo2 < 90:
        warnings.append(f"SpO2 ({health_data.spo2}%) is below normal range (90-100%)")
    
    # Check for critical combinations
    critical_conditions = check_critical_conditions(health_data)
    if critical_conditions:
        warnings.extend(critical_conditions)
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

def check_critical_conditions(health_data: HealthDataInput) -> List[str]:
    """
    Check for potentially critical combinations of vital signs.
    
    Returns a list of warning messages for concerning combinations.
    """
    warnings = []
    
    # High heart rate with low SpO2
    if health_data.heart_rate > 120 and health_data.spo2 < 95:
        warnings.append("High heart rate combined with low SpO2 may indicate respiratory distress")
    
    # High temperature with high heart rate
    if health_data.temperature > 38.0 and health_data.heart_rate > 100:
        warnings.append("High temperature combined with elevated heart rate may indicate fever or infection")
    
    # Low SpO2 with normal heart rate (could indicate chronic condition)
    if health_data.spo2 < 92 and 60 <= health_data.heart_rate <= 100:
        warnings.append("Low SpO2 with normal heart rate may indicate chronic respiratory condition")
    
    # Very low temperature with low heart rate
    if health_data.temperature < 36.0 and health_data.heart_rate < 60:
        warnings.append("Low temperature combined with low heart rate may indicate hypothermia")
    
    return warnings

def validate_input_ranges(heart_rate: float, temperature: float, spo2: float) -> Dict[str, Any]:
    """
    Validate individual input ranges before creating HealthDataInput object.
    
    This can be used for preliminary validation in forms or other interfaces.
    """
    errors = []
    
    # Heart rate validation
    if not isinstance(heart_rate, (int, float)):
        errors.append("Heart rate must be a number")
    elif heart_rate < 30 or heart_rate > 200:
        errors.append("Heart rate must be between 30 and 200 BPM")
    
    # Temperature validation
    if not isinstance(temperature, (int, float)):
        errors.append("Temperature must be a number")
    elif temperature < 35.0 or temperature > 42.0:
        errors.append("Temperature must be between 35.0 and 42.0°C")
    
    # SpO2 validation
    if not isinstance(spo2, (int, float)):
        errors.append("SpO2 must be a number")
    elif spo2 < 70 or spo2 > 100:
        errors.append("SpO2 must be between 70 and 100%")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

def get_normal_ranges() -> Dict[str, Dict[str, Any]]:
    """
    Get normal ranges for health parameters.
    
    Returns a dictionary with normal, warning, and critical ranges for each parameter.
    """
    health_ranges = Config.get_health_ranges()
    
    return {
        "heart_rate": {
            "normal": f"{health_ranges['heart_rate']['normal'][0]}-{health_ranges['heart_rate']['normal'][1]} BPM",
            "warning": "40-59 or 101-140 BPM",
            "critical": "Below 40 or above 140 BPM"
        },
        "temperature": {
            "normal": f"{health_ranges['temperature']['normal'][0]}-{health_ranges['temperature']['normal'][1]}°C",
            "warning": "35.0-36.0 or 37.3-38.0°C",
            "critical": "Below 35.0 or above 38.0°C"
        },
        "spo2": {
            "normal": f"{health_ranges['spo2']['normal'][0]}-{health_ranges['spo2']['normal'][1]}%",
            "warning": f"{health_ranges['spo2']['warning'][0]}-{health_ranges['spo2']['warning'][1]}%",
            "critical": f"Below {health_ranges['spo2']['critical'][0]}%"
        }
    }

