import pandas as pd
import numpy as np
from typing import Tuple
import os
from config import Config

class SyntheticDatasetGenerator:
    """Generate synthetic health data for prototyping and testing"""
    
    def __init__(self):
        self.config = Config.get_health_ranges()
        self.data_path = Config.DATA_PATH
        self.dataset_file = Config.SYNTHETIC_DATASET_FILE
        
    def generate_health_status(self, heart_rate: float, temperature: float, spo2: float, 
                             age: int, bp_systolic: float, bp_diastolic: float, 
                             cholesterol: float) -> str:
        """Determine health status based on all parameters"""
        critical_count = 0
        warning_count = 0
        
        # Check heart rate (age-adjusted)
        if age < 18:
            hr_normal = (70, 110)
        elif age > 65:
            hr_normal = (60, 90)
        else:
            hr_normal = (60, 100)
            
        if not (hr_normal[0] <= heart_rate <= hr_normal[1]):
            if heart_rate < 50 or heart_rate > 140:
                critical_count += 1
            else:
                warning_count += 1
        
        # Check temperature
        if temperature < 35.0 or temperature > 38.0:
            critical_count += 1
        elif temperature < 36.1 or temperature > 37.2:
            warning_count += 1
        
        # Check SpO2
        if spo2 < 90:
            critical_count += 1
        elif spo2 < 95:
            warning_count += 1
        
        # Check blood pressure
        if bp_systolic >= 140 or bp_diastolic >= 90:
            critical_count += 1
        elif bp_systolic >= 120 or bp_diastolic >= 80:
            warning_count += 1
        
        # Check cholesterol
        if cholesterol >= 240:
            critical_count += 1
        elif cholesterol >= 200:
            warning_count += 1
        
        # Determine overall status
        if critical_count > 0:
            return 'Critical'
        elif warning_count >= 2:
            return 'Warning'
        else:
            return 'Normal'
    
    def generate_synthetic_data(self, num_samples: int = 10000) -> pd.DataFrame:
        """Generate synthetic health data with all parameters"""
        np.random.seed(42)
        data = []
        
        for _ in range(num_samples):
            # Generate age first (affects other parameters)
            age = np.random.choice(range(18, 80), p=self._get_age_distribution())
            
            # Generate parameters based on age
            if age < 30:
                heart_rate = np.random.normal(72, 10)
                bp_systolic = np.random.normal(115, 10)
                bp_diastolic = np.random.normal(75, 8)
                cholesterol = np.random.normal(180, 30)
            elif age < 50:
                heart_rate = np.random.normal(75, 12)
                bp_systolic = np.random.normal(120, 12)
                bp_diastolic = np.random.normal(78, 10)
                cholesterol = np.random.normal(200, 35)
            else:
                heart_rate = np.random.normal(78, 15)
                bp_systolic = np.random.normal(130, 15)
                bp_diastolic = np.random.normal(82, 12)
                cholesterol = np.random.normal(220, 40)
            
            # Other parameters (less age-dependent)
            temperature = np.random.normal(36.8, 0.4)
            spo2 = np.random.normal(97, 2)
            
            # Add some edge cases (10% of data)
            if np.random.random() < 0.1:
                param = np.random.choice(['hr', 'bp', 'temp', 'spo2', 'chol'])
                if param == 'hr':
                    heart_rate = np.random.choice([45, 150])
                elif param == 'bp':
                    bp_systolic = np.random.choice([85, 160])
                    bp_diastolic = np.random.choice([55, 95])
                elif param == 'temp':
                    temperature = np.random.choice([35.5, 38.5])
                elif param == 'spo2':
                    spo2 = np.random.choice([88, 100])
                elif param == 'chol':
                    cholesterol = np.random.choice([150, 280])
            
            # Ensure values are within valid ranges
            heart_rate = np.clip(heart_rate, 30, 200)
            temperature = np.clip(temperature, 35.0, 42.0)
            spo2 = np.clip(spo2, 70, 100)
            bp_systolic = np.clip(bp_systolic, 70, 250)
            bp_diastolic = np.clip(bp_diastolic, 40, 150)
            cholesterol = np.clip(cholesterol, 100, 400)
            
            # Generate health status
            status = self.generate_health_status(
                heart_rate, temperature, spo2, age,
                bp_systolic, bp_diastolic, cholesterol
            )
            
            data.append([
                heart_rate, temperature, spo2, age,
                bp_systolic, bp_diastolic, cholesterol, status
            ])
        
        columns = ['heart_rate', 'temperature', 'spo2', 'age', 
                  'bp_systolic', 'bp_diastolic', 'cholesterol', 'health_status']
        return pd.DataFrame(data, columns=columns)
    
    def _add_pathological_cases(self, df: pd.DataFrame, percentage: float = 0.05):
        """Add specific pathological cases for model training"""
        num_cases = int(len(df) * percentage)
        pathological_cases = []
        
        # Case 1: Cardiac emergency (high HR, low BP, low SpO2)
        for _ in range(num_cases // 4):
            case = {
                'age': np.random.randint(50, 80),
                'heart_rate': np.random.uniform(150, 180),
                'temperature': np.random.uniform(36.5, 37.5),
                'spo2': np.random.uniform(85, 90),
                'bp_systolic': np.random.uniform(80, 95),
                'bp_diastolic': np.random.uniform(50, 60),
                'cholesterol': np.random.uniform(200, 300),
                'health_status': 'Critical'
            }
            pathological_cases.append(case)
        
        # Case 2: Sepsis (high temp, high HR, low BP)
        for _ in range(num_cases // 4):
            case = {
                'age': np.random.randint(30, 70),
                'heart_rate': np.random.uniform(110, 140),
                'temperature': np.random.uniform(38.5, 40.0),
                'spo2': np.random.uniform(90, 95),
                'bp_systolic': np.random.uniform(85, 100),
                'bp_diastolic': np.random.uniform(50, 65),
                'cholesterol': np.random.uniform(150, 250),
                'health_status': 'Critical'
            }
            pathological_cases.append(case)
        
        # Case 3: Hypertensive crisis
        for _ in range(num_cases // 4):
            case = {
                'age': np.random.randint(45, 75),
                'heart_rate': np.random.uniform(90, 110),
                'temperature': np.random.uniform(36.5, 37.2),
                'spo2': np.random.uniform(95, 98),
                'bp_systolic': np.random.uniform(180, 220),
                'bp_diastolic': np.random.uniform(110, 130),
                'cholesterol': np.random.uniform(220, 350),
                'health_status': 'Critical'
            }
            pathological_cases.append(case)
        
        # Case 4: High cholesterol with warning signs
        for _ in range(num_cases // 4):
            case = {
                'age': np.random.randint(40, 70),
                'heart_rate': np.random.uniform(80, 100),
                'temperature': np.random.uniform(36.5, 37.2),
                'spo2': np.random.uniform(94, 97),
                'bp_systolic': np.random.uniform(130, 140),
                'bp_diastolic': np.random.uniform(85, 90),
                'cholesterol': np.random.uniform(240, 320),
                'health_status': 'Warning'
            }
            pathological_cases.append(case)
        
        return pathological_cases
    
    def save_dataset(self, df: pd.DataFrame, filename: str = None) -> str:
        """Save the generated dataset to CSV"""
        if filename is None:
            filename = self.dataset_file
        
        filepath = os.path.join(self.data_path, filename)
        df.to_csv(filepath, index=False)
        return filepath
    
    def load_dataset(self, filename: str = None) -> pd.DataFrame:
        """Load the dataset from CSV"""
        if filename is None:
            filename = self.dataset_file
        
        filepath = os.path.join(self.data_path, filename)
        if os.path.exists(filepath):
            return pd.read_csv(filepath)
        else:
            raise FileNotFoundError(f"Dataset file not found: {filepath}")
    
    def _get_age_distribution(self):
        """Get realistic age distribution"""
        ages = range(18, 80)
        # Higher probability for middle ages
        probs = np.array([0.5 if 30 <= age <= 60 else 0.3 for age in ages])
        return probs / probs.sum()
    
    def prepare_training_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for model training"""
        # Convert health status to numerical labels
        status_mapping = {"Normal": 0, "Warning": 1, "Critical": 2}
        y = df['health_status'].map(status_mapping).values
        
        # Prepare features (all 6 parameters)
        X = df[['heart_rate', 'temperature', 'spo2', 'age', 
                'bp_systolic', 'bp_diastolic', 'cholesterol']].values
        
        return X, y

