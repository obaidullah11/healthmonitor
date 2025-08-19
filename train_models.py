#!/usr/bin/env python3
"""
Model Training Script for Health Monitoring System

This script:
1. Generates synthetic health data
2. Trains Random Forest and Neural Network models
3. Compares model performance
4. Saves the best performing model
"""

import os
import sys
import time
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.dataset_generator import SyntheticDatasetGenerator
from app.models.ml_models import HealthMLModels
from config import Config

def main():
    """Main training function"""
    print("=" * 60)
    print("Health Monitoring System - Model Training")
    print("=" * 60)
    
    # Create necessary directories
    os.makedirs(Config.DATA_PATH, exist_ok=True)
    os.makedirs(Config.MODEL_PATH, exist_ok=True)
    
    # Step 1: Generate synthetic dataset
    print("\n1. Generating synthetic health dataset...")
    dataset_generator = SyntheticDatasetGenerator()
    
    try:
        # Check if dataset already exists
        dataset_path = os.path.join(Config.DATA_PATH, Config.SYNTHETIC_DATASET_FILE)
        if os.path.exists(dataset_path):
            print(f"Loading existing dataset from: {dataset_path}")
            df = dataset_generator.load_dataset()
        else:
            print("Generating new synthetic dataset...")
            df = dataset_generator.generate_synthetic_data(num_samples=10000)
            dataset_path = dataset_generator.save_dataset(df)
            print(f"Dataset saved to: {dataset_path}")
        
        print(f"Dataset shape: {df.shape}")
        print(f"Health status distribution:\n{df['health_status'].value_counts()}")
        
    except Exception as e:
        print(f"Error generating dataset: {e}")
        return
    
    # Step 2: Prepare training data
    print("\n2. Preparing training data...")
    try:
        X, y = dataset_generator.prepare_training_data(df)
        print(f"Features shape: {X.shape}")
        print(f"Labels shape: {y.shape}")
        print(f"Label distribution: {dict(zip(*np.unique(y, return_counts=True)))}")
        
    except Exception as e:
        print(f"Error preparing training data: {e}")
        return
    
    # Step 3: Train models
    print("\n3. Training machine learning models...")
    ml_models = HealthMLModels()
    
    # Train Random Forest
    print("\n   Training Random Forest model...")
    try:
        rf_results = ml_models.train_random_forest(X, y)
        print(f"   ✓ Random Forest training completed")
        print(f"   - Accuracy: {rf_results['accuracy']:.4f}")
        print(f"   - Training time: {rf_results['training_time']:.2f}s")
        print(f"   - Inference time: {rf_results['inference_time_ms']:.2f}ms")
        
    except Exception as e:
        print(f"   ✗ Random Forest training failed: {e}")
        rf_results = None
    
    # Train Neural Network
    print("\n   Training Neural Network model...")
    try:
        nn_results = ml_models.train_neural_network(X, y)
        print(f"   ✓ Neural Network training completed")
        print(f"   - Accuracy: {nn_results['accuracy']:.4f}")
        print(f"   - Training time: {nn_results['training_time']:.2f}s")
        print(f"   - Inference time: {nn_results['inference_time_ms']:.2f}ms")
        
    except Exception as e:
        print(f"   ✗ Neural Network training failed: {e}")
        nn_results = None
    
    # Step 4: Compare models
    print("\n4. Comparing model performance...")
    if rf_results and nn_results:
        comparison = ml_models.compare_models(rf_results, nn_results)
        
        print("\n   Model Comparison:")
        print(f"   Random Forest:")
        print(f"     - Accuracy: {comparison['random_forest']['accuracy']:.4f}")
        print(f"     - Training time: {comparison['random_forest']['training_time']:.2f}s")
        print(f"     - Inference time: {comparison['random_forest']['inference_time_ms']:.2f}ms")
        
        print(f"   Neural Network:")
        print(f"     - Accuracy: {comparison['neural_network']['accuracy']:.4f}")
        print(f"     - Training time: {comparison['neural_network']['training_time']:.2f}s")
        print(f"     - Inference time: {comparison['neural_network']['inference_time_ms']:.2f}ms")
        
        print(f"\n   Recommendation: {comparison['recommendation'].replace('_', ' ').title()}")
        
    elif rf_results:
        print("   Only Random Forest model available")
        comparison = {"recommendation": "random_forest"}
        
    elif nn_results:
        print("   Only Neural Network model available")
        comparison = {"recommendation": "neural_network"}
        
    else:
        print("   No models trained successfully")
        return
    
    # Step 5: Save models
    print("\n5. Saving trained models...")
    try:
        ml_models.save_models()
        print("   ✓ Models saved successfully")
        
    except Exception as e:
        print(f"   ✗ Error saving models: {e}")
    
    # Step 6: Test predictions
    print("\n6. Testing model predictions...")
    try:
        # Test with sample data
        test_cases = [
            {"heart_rate": 75, "temperature": 36.8, "spo2": 98},  # Normal
            {"heart_rate": 110, "temperature": 37.8, "spo2": 93},  # Warning
            {"heart_rate": 150, "temperature": 39.0, "spo2": 88},  # Critical
        ]
        
        print("\n   Test Predictions:")
        for i, test_case in enumerate(test_cases, 1):
            # Generate random values for missing parameters in test cases
            age = np.random.randint(25, 65)
            bp_systolic = np.random.uniform(110, 140)
            bp_diastolic = np.random.uniform(70, 90)
            cholesterol = np.random.uniform(150, 250)
            
            features = np.array([
                test_case["heart_rate"], 
                test_case["temperature"], 
                test_case["spo2"],
                age,
                bp_systolic,
                bp_diastolic,
                cholesterol
            ])
            
            if ml_models.rf_model:
                pred, conf = ml_models.predict_rf(features)
                status = {0: "Normal", 1: "Warning", 2: "Critical"}[pred]
                print(f"   Test {i}: {status} (confidence: {conf:.3f})")
        
    except Exception as e:
        print(f"   ✗ Error testing predictions: {e}")
    
    print("\n" + "=" * 60)
    print("Training completed successfully!")
    print("=" * 60)
    print(f"Dataset: {dataset_path}")
    print(f"Models: {Config.MODEL_PATH}")
    print(f"API Documentation: http://{Config.HOST}:{Config.PORT}/docs")
    print("=" * 60)

if __name__ == "__main__":
    import numpy as np
    main()



