import pandas as pd
import numpy as np
import requests
from typing import Optional, Dict, Any
import os
from config import Config

class RealDataLoader:
    """Load and process real health datasets"""
    
    def __init__(self):
        self.data_path = Config.DATA_PATH
        
    def load_cleveland_dataset(self, augment_missing: bool = True) -> pd.DataFrame:
        """
        Load Cleveland Heart Disease dataset and augment with missing parameters
        
        Args:
            augment_missing: If True, add synthetic temperature and SpO2 data
            
        Returns:
            DataFrame with all 6 health parameters
        """
        # Cleveland dataset URL
        url = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"
        
        # Column names for Cleveland dataset
        columns = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 
                   'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'target']
        
        try:
            # Download and load data
            print("Downloading Cleveland Heart Disease dataset...")
            df = pd.read_csv(url, names=columns, na_values='?')
            
            # Remove rows with missing values
            df = df.dropna()
            
            # Create health dataset with required parameters
            health_df = pd.DataFrame()
            
            # Map existing parameters
            health_df['age'] = df['age'].astype(int)
            health_df['heart_rate'] = df['thalach']  # Maximum heart rate achieved
            health_df['cholesterol'] = df['chol']
            
            # Blood pressure (only systolic available in Cleveland)
            health_df['bp_systolic'] = df['trestbps']
            # Estimate diastolic (typically 60-65% of systolic)
            health_df['bp_diastolic'] = (df['trestbps'] * 0.65).round()
            
            if augment_missing:
                # Add synthetic temperature and SpO2
                n_samples = len(health_df)
                
                # Temperature: Normal distribution with slight variations for heart disease patients
                base_temp = np.random.normal(36.8, 0.4, n_samples)
                # Slightly elevated temperature for heart disease patients
                disease_mask = df['target'] > 0
                base_temp[disease_mask] += np.random.uniform(0.1, 0.3, disease_mask.sum())
                health_df['temperature'] = np.clip(base_temp, 35.0, 42.0)
                
                # SpO2: Normal distribution, slightly lower for heart disease patients
                base_spo2 = np.random.normal(97, 2, n_samples)
                base_spo2[disease_mask] -= np.random.uniform(1, 3, disease_mask.sum())
                health_df['spo2'] = np.clip(base_spo2, 70, 100)
            
            # Determine health status based on all parameters
            health_df['health_status'] = self._determine_health_status(health_df)
            
            # Reorder columns
            health_df = health_df[['heart_rate', 'temperature', 'spo2', 'age', 
                                   'bp_systolic', 'bp_diastolic', 'cholesterol', 'health_status']]
            
            print(f"Loaded {len(health_df)} samples from Cleveland dataset")
            return health_df
            
        except Exception as e:
            print(f"Error loading Cleveland dataset: {e}")
            return pd.DataFrame()
    
    def load_mimic_subset(self, sample_size: int = 1000) -> pd.DataFrame:
        """
        Load a subset of MIMIC-III data (requires prior download)
        This is a placeholder - actual implementation requires MIMIC-III access
        """
        print("MIMIC-III requires registration and download from PhysioNet")
        print("Visit: https://physionet.org/content/mimiciii/1.4/")
        return pd.DataFrame()
    
    def load_combined_dataset(self, save_to_csv: bool = True) -> pd.DataFrame:
        """
        Load and combine multiple real datasets
        
        Args:
            save_to_csv: If True, save the combined dataset to CSV
            
        Returns:
            Combined DataFrame with all health parameters
        """
        datasets = []
        
        # Load Cleveland dataset
        cleveland_df = self.load_cleveland_dataset(augment_missing=True)
        if not cleveland_df.empty:
            datasets.append(cleveland_df)
        
        # Add more datasets here as they become available
        # e.g., MIMIC-III, NHANES, etc.
        
        if datasets:
            # Combine all datasets
            combined_df = pd.concat(datasets, ignore_index=True)
            
            # Shuffle the data
            combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)
            
            if save_to_csv:
                filename = 'real_health_dataset.csv'
                filepath = os.path.join(self.data_path, filename)
                combined_df.to_csv(filepath, index=False)
                print(f"Combined dataset saved to: {filepath}")
            
            print(f"Total samples in combined dataset: {len(combined_df)}")
            print(f"Health status distribution:")
            print(combined_df['health_status'].value_counts())
            
            return combined_df
        else:
            print("No datasets could be loaded")
            return pd.DataFrame()
    
    def _determine_health_status(self, df: pd.DataFrame) -> pd.Series:
        """
        Determine health status based on all parameters
        """
        statuses = []
        
        for _, row in df.iterrows():
            critical_count = 0
            warning_count = 0
            
            # Age-adjusted heart rate
            age = row['age']
            hr = row['heart_rate']
            if age < 30:
                hr_normal = (60, 100)
            elif age > 65:
                hr_normal = (60, 90)
            else:
                hr_normal = (60, 95)
            
            if hr < 50 or hr > 140:
                critical_count += 1
            elif not (hr_normal[0] <= hr <= hr_normal[1]):
                warning_count += 1
            
            # Blood pressure
            if row['bp_systolic'] >= 140 or row['bp_diastolic'] >= 90:
                critical_count += 1
            elif row['bp_systolic'] >= 120 or row['bp_diastolic'] >= 80:
                warning_count += 1
            
            # Cholesterol
            if row['cholesterol'] >= 240:
                warning_count += 1
            
            # Temperature (if available)
            if 'temperature' in row:
                if row['temperature'] < 35.0 or row['temperature'] > 38.0:
                    critical_count += 1
                elif row['temperature'] < 36.1 or row['temperature'] > 37.2:
                    warning_count += 1
            
            # SpO2 (if available)
            if 'spo2' in row:
                if row['spo2'] < 90:
                    critical_count += 1
                elif row['spo2'] < 95:
                    warning_count += 1
            
            # Determine status
            if critical_count > 0:
                statuses.append('Critical')
            elif warning_count >= 2:
                statuses.append('Warning')
            else:
                statuses.append('Normal')
        
        return pd.Series(statuses)
    
    def validate_dataset(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate the dataset for completeness and quality
        """
        required_columns = ['heart_rate', 'temperature', 'spo2', 'age', 
                           'bp_systolic', 'bp_diastolic', 'cholesterol', 'health_status']
        
        validation_results = {
            'is_valid': True,
            'missing_columns': [],
            'data_quality': {}
        }
        
        # Check for missing columns
        missing = set(required_columns) - set(df.columns)
        if missing:
            validation_results['is_valid'] = False
            validation_results['missing_columns'] = list(missing)
        
        # Check data quality
        for col in df.columns:
            if col in required_columns[:-1]:  # Exclude health_status
                validation_results['data_quality'][col] = {
                    'min': df[col].min(),
                    'max': df[col].max(),
                    'mean': df[col].mean(),
                    'std': df[col].std(),
                    'missing': df[col].isna().sum()
                }
        
        # Check health status distribution
        if 'health_status' in df.columns:
            validation_results['health_status_distribution'] = df['health_status'].value_counts().to_dict()
        
        return validation_results


# Example usage
if __name__ == "__main__":
    loader = RealDataLoader()
    
    # Load Cleveland dataset with synthetic augmentation
    cleveland_df = loader.load_cleveland_dataset(augment_missing=True)
    print("\nCleveland dataset shape:", cleveland_df.shape)
    print("\nFirst 5 rows:")
    print(cleveland_df.head())
    
    # Load combined dataset
    combined_df = loader.load_combined_dataset(save_to_csv=True)
    
    # Validate dataset
    validation = loader.validate_dataset(combined_df)
    print("\nDataset validation:")
    print(f"Is valid: {validation['is_valid']}")
    print(f"Health status distribution: {validation.get('health_status_distribution', {})}")

