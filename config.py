import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    API_TITLE = "Health Monitoring System API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "AI-powered health monitoring system with real-time predictions"
    
    # Server Configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Model Configuration
    MODEL_PATH = "models/"
    RANDOM_FOREST_MODEL_FILE = "random_forest_model.pkl"
    NEURAL_NETWORK_MODEL_FILE = "neural_network_model.tflite"
    
    # Data Configuration
    DATA_PATH = "data/"
    SYNTHETIC_DATASET_FILE = "synthetic_dataset.csv"
    
    # Health Parameter Ranges
    HEALTH_RANGES = {
        "heart_rate": {
            "normal": (60, 100),
            "warning": [(40, 59), (101, 140)],
            "critical": [(0, 39), (141, 300)]
        },
        "temperature": {
            "normal": (36.1, 37.2),
            "warning": [(35.0, 36.0), (37.3, 38.0)],
            "critical": [(0, 34.9), (38.1, 50.0)]
        },
        "spo2": {
            "normal": (95, 100),
            "warning": (90, 94),
            "critical": (0, 89)
        },
        "age": {
            # Age doesn't have normal/warning/critical, but affects other parameters
            "ranges": {
                "child": (1, 12),
                "teen": (13, 19),
                "adult": (20, 59),
                "senior": (60, 120)
            }
        },
        "blood_pressure": {
            "normal": {"systolic": (90, 120), "diastolic": (60, 80)},
            "warning": {"systolic": (121, 139), "diastolic": (81, 89)},
            "critical": {"systolic": [(70, 89), (140, 250)], "diastolic": [(40, 59), (90, 150)]}
        },
        "cholesterol": {
            "normal": (0, 200),
            "warning": (201, 239),
            "critical": (240, 400)
        }
    }
    
    # Model Training Configuration
    TRAINING_CONFIG = {
        "test_size": 0.2,
        "random_state": 42,
        "random_forest": {
            "n_estimators": 100,
            "max_depth": 10,
            "random_state": 42
        },
        "neural_network": {
            "epochs": 50,
            "batch_size": 32,
            "validation_split": 0.2
        }
    }
    
    # API Response Configuration
    RESPONSE_TIMEOUT_MS = 500
    CACHE_TTL = 300  # 5 minutes
    
    # Redis Configuration
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    
    @classmethod
    def get_health_ranges(cls) -> Dict[str, Any]:
        return cls.HEALTH_RANGES
    
    @classmethod
    def get_training_config(cls) -> Dict[str, Any]:
        return cls.TRAINING_CONFIG

