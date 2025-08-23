"""
Enhanced Heart Disease Dataset Loader

This module provides functionality to load and process multiple heart disease datasets
including Cleveland, Hungarian, Switzerland, and VA Long Beach datasets from UCI.
"""

import pandas as pd
import numpy as np
import requests
from typing import Dict, List, Optional, Tuple
import os
from config import Config


class HeartDiseaseDataLoader:
    """Load and process multiple heart disease datasets for enhanced training"""
    
    def __init__(self):
        self.data_path = Config.DATA_PATH
        self.dataset_urls = {
            'cleveland': 'https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data',
            'hungarian': 'https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.hungarian.data',
            'switzerland': 'https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.switzerland.data',
            'va': 'https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.va.data'
        }
        
        # Common column names for all heart disease datasets
        self.columns = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 
                       'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'target']
    
    def load_all_heart_disease_datasets(self) -> pd.DataFrame:
        """Load and combine all available heart disease datasets"""
        all_datasets = []
        
        for dataset_name, url in self.dataset_urls.items():
            print(f"\nLoading {dataset_name} dataset...")
            df = self._load_single_dataset(dataset_name, url)
            if not df.empty:
                all_datasets.append(df)
                print(f"✓ Loaded {len(df)} samples from {dataset_name}")
            else:
                print(f"✗ Failed to load {dataset_name} dataset")
        
        if all_datasets:
            # Combine all datasets
            combined_df = pd.concat(all_datasets, ignore_index=True)
            print(f"\nTotal samples across all datasets: {len(combined_df)}")
            
            # Process and augment the combined dataset
            processed_df = self._process_combined_dataset(combined_df)
            
            # Save the enhanced dataset
            self._save_enhanced_dataset(processed_df)
            
            return processed_df
        else:
            print("No datasets could be loaded")
            return pd.DataFrame()
    
    def _load_single_dataset(self, name: str, url: str) -> pd.DataFrame:
        """Load a single heart disease dataset from UCI"""
        try:
            # Download data
            df = pd.read_csv(url, names=self.columns, na_values='?')
            
            # Add dataset source
            df['dataset_source'] = name
            
            # Remove rows with too many missing values
            df = df.dropna(thresh=len(df.columns) - 3)  # Allow up to 3 missing values
            
            return df
        except Exception as e:
            print(f"Error loading {name} dataset: {e}")
            return pd.DataFrame()
    
    def _process_combined_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize the combined dataset"""
        # Create our standard health monitoring format
        processed_df = pd.DataFrame()
        
        # Map existing parameters
        processed_df['age'] = df['age'].astype(int)
        processed_df['heart_rate'] = df['thalach']  # Maximum heart rate achieved
        processed_df['cholesterol'] = df['chol'].fillna(df['chol'].median())
        
        # Blood pressure
        processed_df['bp_systolic'] = df['trestbps'].fillna(df['trestbps'].median())
        # Estimate diastolic (using medical ratio)
        processed_df['bp_diastolic'] = (processed_df['bp_systolic'] * 0.65).round()
        
        # Add synthetic temperature and SpO2 based on heart disease severity
        n_samples = len(processed_df)
        
        # Temperature: Normal with variations based on condition
        base_temp = np.random.normal(36.8, 0.3, n_samples)
        # Patients with heart disease might have slightly different temperatures
        disease_severity = df['target'].fillna(0)
        temp_adjustment = disease_severity * 0.1 * np.random.randn(n_samples)
        processed_df['temperature'] = np.clip(base_temp + temp_adjustment, 35.0, 42.0)
        
        # SpO2: Lower for heart disease patients
        base_spo2 = np.random.normal(97, 1.5, n_samples)
        spo2_adjustment = disease_severity * np.random.uniform(-2, -0.5, n_samples)
        processed_df['spo2'] = np.clip(base_spo2 + spo2_adjustment, 70, 100).round()
        
        # Additional heart disease specific features
        processed_df['chest_pain_type'] = df['cp'].fillna(0)  # 0-3 scale
        processed_df['exercise_angina'] = df['exang'].fillna(0)  # 0 or 1
        processed_df['st_depression'] = df['oldpeak'].fillna(0)  # ST depression
        processed_df['vessels_colored'] = df['ca'].fillna(0)  # Number of vessels colored
        
        # Target: Convert to risk levels
        processed_df['heart_disease_severity'] = disease_severity
        processed_df['health_status'] = self._determine_health_status(processed_df)
        
        # Add dataset source
        processed_df['dataset_source'] = df['dataset_source']
        
        # Remove any remaining NaN values
        processed_df = processed_df.dropna()
        
        return processed_df
    
    def _determine_health_status(self, df: pd.DataFrame) -> pd.Series:
        """Determine health status based on heart disease severity and vitals"""
        statuses = []
        
        for _, row in df.iterrows():
            severity = row['heart_disease_severity']
            
            # Check additional risk factors
            risk_count = 0
            
            # Blood pressure check
            if row['bp_systolic'] >= 140 or row['bp_diastolic'] >= 90:
                risk_count += 2
            elif row['bp_systolic'] >= 130 or row['bp_diastolic'] >= 85:
                risk_count += 1
            
            # Cholesterol check
            if row['cholesterol'] >= 240:
                risk_count += 2
            elif row['cholesterol'] >= 200:
                risk_count += 1
            
            # Heart rate check
            if row['heart_rate'] > 100 or row['heart_rate'] < 60:
                risk_count += 1
            
            # SpO2 check
            if row['spo2'] < 95:
                risk_count += 1
            
            # Determine status based on disease severity and risk factors
            if severity >= 3 or risk_count >= 4:
                statuses.append('Critical')
            elif severity >= 1 or risk_count >= 2:
                statuses.append('Warning')
            else:
                statuses.append('Normal')
        
        return pd.Series(statuses)
    
    def _save_enhanced_dataset(self, df: pd.DataFrame) -> str:
        """Save the enhanced heart disease dataset"""
        filename = 'enhanced_heart_disease_dataset.csv'
        filepath = os.path.join(self.data_path, filename)
        
        # Save with proper column order
        columns_order = [
            'heart_rate', 'temperature', 'spo2', 'age', 
            'bp_systolic', 'bp_diastolic', 'cholesterol',
            'chest_pain_type', 'exercise_angina', 'st_depression',
            'vessels_colored', 'heart_disease_severity',
            'health_status', 'dataset_source'
        ]
        
        df[columns_order].to_csv(filepath, index=False)
        print(f"\nEnhanced dataset saved to: {filepath}")
        
        # Print summary statistics
        print("\nDataset Summary:")
        print(f"Total samples: {len(df)}")
        print(f"Health status distribution:\n{df['health_status'].value_counts()}")
        print(f"Dataset sources:\n{df['dataset_source'].value_counts()}")
        print(f"Heart disease severity distribution:\n{df['heart_disease_severity'].value_counts()}")
        
        return filepath
    
    def load_framingham_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Framingham study inspired features"""
        # Add calculated features commonly used in Framingham risk score
        df['pulse_pressure'] = df['bp_systolic'] - df['bp_diastolic']
        df['mean_arterial_pressure'] = df['bp_diastolic'] + (df['pulse_pressure'] / 3)
        df['rate_pressure_product'] = df['heart_rate'] * df['bp_systolic'] / 100
        
        # Age groups for risk stratification
        df['age_group'] = pd.cut(df['age'], 
                                 bins=[0, 40, 50, 60, 70, 100], 
                                 labels=['<40', '40-49', '50-59', '60-69', '70+'])
        
        # Cholesterol risk categories
        df['cholesterol_category'] = pd.cut(df['cholesterol'], 
                                           bins=[0, 200, 240, 400], 
                                           labels=['Normal', 'Borderline', 'High'])
        
        # Blood pressure categories
        df['bp_category'] = df.apply(self._categorize_blood_pressure, axis=1)
        
        return df
    
    def _categorize_blood_pressure(self, row) -> str:
        """Categorize blood pressure according to AHA guidelines"""
        systolic = row['bp_systolic']
        diastolic = row['bp_diastolic']
        
        if systolic < 120 and diastolic < 80:
            return 'Normal'
        elif systolic < 130 and diastolic < 80:
            return 'Elevated'
        elif systolic < 140 or diastolic < 90:
            return 'Stage 1 Hypertension'
        else:
            return 'Stage 2 Hypertension'
    
    def create_risk_stratified_dataset(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Create training and validation sets stratified by risk levels"""
        # Load the enhanced dataset
        filepath = os.path.join(self.data_path, 'enhanced_heart_disease_dataset.csv')
        
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
        else:
            # Create it if it doesn't exist
            df = self.load_all_heart_disease_datasets()
        
        # Add Framingham features
        df = self.load_framingham_features(df)
        
        # Stratified split by health status
        from sklearn.model_selection import train_test_split
        
        X = df.drop(['health_status', 'dataset_source'], axis=1)
        y = df['health_status']
        
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=42
        )
        
        # Combine back for saving
        train_df = pd.concat([X_train, y_train], axis=1)
        val_df = pd.concat([X_val, y_val], axis=1)
        
        # Save stratified datasets
        train_df.to_csv(os.path.join(self.data_path, 'heart_disease_train.csv'), index=False)
        val_df.to_csv(os.path.join(self.data_path, 'heart_disease_validation.csv'), index=False)
        
        print(f"\nTraining set: {len(train_df)} samples")
        print(f"Validation set: {len(val_df)} samples")
        
        return train_df, val_df


# Example usage
if __name__ == "__main__":
    loader = HeartDiseaseDataLoader()
    
    # Load all heart disease datasets
    enhanced_df = loader.load_all_heart_disease_datasets()
    
    # Create stratified train/validation sets
    if not enhanced_df.empty:
        train_df, val_df = loader.create_risk_stratified_dataset()
        print("\nDatasets created successfully!")


