from pydantic import BaseModel, Field, validator
from typing import Optional, Literal, Tuple
from datetime import datetime

class HealthDataInput(BaseModel):
    """Input model for health data from the form"""
    heart_rate: float = Field(..., ge=30, le=200, description="Heart rate in BPM")
    temperature: float = Field(..., ge=35.0, le=42.0, description="Body temperature in Celsius")
    spo2: float = Field(..., ge=70, le=100, description="Blood oxygen level in percentage")
    age: int = Field(..., ge=1, le=120, description="Age in years")
    blood_pressure_systolic: float = Field(..., ge=70, le=250, description="Systolic blood pressure in mmHg")
    blood_pressure_diastolic: float = Field(..., ge=40, le=150, description="Diastolic blood pressure in mmHg")
    cholesterol: float = Field(..., ge=100, le=400, description="Total cholesterol in mg/dL")
    
    @validator('heart_rate')
    def validate_heart_rate(cls, v):
        if v < 30 or v > 200:
            raise ValueError('Heart rate must be between 30 and 200 BPM')
        return v
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if v < 35.0 or v > 42.0:
            raise ValueError('Temperature must be between 35.0 and 42.0°C')
        return v
    
    @validator('spo2')
    def validate_spo2(cls, v):
        if v < 70 or v > 100:
            raise ValueError('SpO2 must be between 70 and 100%')
        return v
    
    @validator('age')
    def validate_age(cls, v):
        if v < 1 or v > 120:
            raise ValueError('Age must be between 1 and 120 years')
        return v
    
    @validator('blood_pressure_systolic')
    def validate_bp_systolic(cls, v):
        if v < 70 or v > 250:
            raise ValueError('Systolic BP must be between 70 and 250 mmHg')
        return v
    
    @validator('blood_pressure_diastolic')
    def validate_bp_diastolic(cls, v):
        if v < 40 or v > 150:
            raise ValueError('Diastolic BP must be between 40 and 150 mmHg')
        return v
    
    @validator('cholesterol')
    def validate_cholesterol(cls, v):
        if v < 100 or v > 400:
            raise ValueError('Cholesterol must be between 100 and 400 mg/dL')
        return v
    
    @property
    def blood_pressure(self) -> Tuple[float, float]:
        """Return blood pressure as tuple (systolic, diastolic)"""
        return (self.blood_pressure_systolic, self.blood_pressure_diastolic)

class HealthPrediction(BaseModel):
    """Model for health prediction results"""
    health_status: Literal["Normal", "Warning", "Critical"]
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    suggested_action: str
    prediction_details: dict

class HealthDataRecord(BaseModel):
    """Model for storing health data records"""
    id: Optional[str] = None
    heart_rate: float
    temperature: float
    spo2: float
    health_status: Optional[str] = None
    confidence_score: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None

class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    message: str
    data: Optional[dict] = None
    error_code: Optional[str] = None

