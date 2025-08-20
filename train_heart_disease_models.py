#!/usr/bin/env python3
"""
Heart Disease Specific Model Training Script

This script trains models specifically optimized for heart disease risk prediction
using the enhanced heart disease datasets from multiple sources.
"""

import os
import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import cross_val_score
import joblib
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import warnings
warnings.filterwarnings('ignore')

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.heart_disease_data_loader import HeartDiseaseDataLoader
from app.utils.dataset_generator import SyntheticDatasetGenerator
from config import Config


class HeartDiseaseModelTrainer:
    """Train specialized models for heart disease prediction"""
    
    def __init__(self):
        self.model_path = Config.MODEL_PATH
        self.data_path = Config.DATA_PATH
        os.makedirs(self.model_path, exist_ok=True)
        os.makedirs(self.data_path, exist_ok=True)
        
    def prepare_features(self, df: pd.DataFrame) -> tuple:
        """Prepare features for training"""
        # Select features for training
        feature_columns = [
            'heart_rate', 'temperature', 'spo2', 'age',
            'bp_systolic', 'bp_diastolic', 'cholesterol'
        ]
        
        # Add advanced features if available
        if 'chest_pain_type' in df.columns:
            feature_columns.extend([
                'chest_pain_type', 'exercise_angina', 
                'st_depression', 'vessels_colored'
            ])
        
        # Add calculated features if available
        if 'pulse_pressure' in df.columns:
            feature_columns.extend([
                'pulse_pressure', 'mean_arterial_pressure', 
                'rate_pressure_product'
            ])
        
        X = df[feature_columns].values
        
        # Convert health status to numerical
        status_mapping = {'Normal': 0, 'Warning': 1, 'Critical': 2}
        y = df['health_status'].map(status_mapping).values
        
        return X, y, feature_columns
    
    def train_random_forest_heart_disease(self, X_train, y_train, X_val, y_val):
        """Train Random Forest optimized for heart disease"""
        print("\n   Training Random Forest for Heart Disease...")
        
        # Optimized parameters for heart disease prediction
        rf_model = RandomForestClassifier(
            n_estimators=200,  # More trees for better accuracy
            max_depth=15,      # Deeper trees for complex patterns
            min_samples_split=10,
            min_samples_leaf=5,
            max_features='sqrt',
            bootstrap=True,
            class_weight='balanced',  # Handle class imbalance
            random_state=42,
            n_jobs=-1
        )
        
        start_time = time.time()
        rf_model.fit(X_train, y_train)
        training_time = time.time() - start_time
        
        # Evaluate
        train_score = rf_model.score(X_train, y_train)
        val_score = rf_model.score(X_val, y_val)
        
        # Get predictions for detailed metrics
        y_pred = rf_model.predict(X_val)
        
        print(f"   ✓ Random Forest training completed")
        print(f"   - Training accuracy: {train_score:.4f}")
        print(f"   - Validation accuracy: {val_score:.4f}")
        print(f"   - Training time: {training_time:.2f}s")
        
        # Feature importance
        feature_importance = rf_model.feature_importances_
        
        return rf_model, val_score, feature_importance
    
    def train_gradient_boosting_heart_disease(self, X_train, y_train, X_val, y_val):
        """Train Gradient Boosting for heart disease"""
        print("\n   Training Gradient Boosting for Heart Disease...")
        
        gb_model = GradientBoostingClassifier(
            n_estimators=150,
            learning_rate=0.1,
            max_depth=5,
            min_samples_split=10,
            min_samples_leaf=5,
            subsample=0.8,
            random_state=42
        )
        
        start_time = time.time()
        gb_model.fit(X_train, y_train)
        training_time = time.time() - start_time
        
        # Evaluate
        val_score = gb_model.score(X_val, y_val)
        
        print(f"   ✓ Gradient Boosting training completed")
        print(f"   - Validation accuracy: {val_score:.4f}")
        print(f"   - Training time: {training_time:.2f}s")
        
        return gb_model, val_score
    
    def train_neural_network_heart_disease(self, X_train, y_train, X_val, y_val):
        """Train Neural Network optimized for heart disease"""
        print("\n   Training Neural Network for Heart Disease...")
        
        # Scale features for neural network
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        
        # Build model
        model = keras.Sequential([
            layers.Input(shape=(X_train.shape[1],)),
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(128, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(3, activation='softmax')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Early stopping
        early_stopping = keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        # Train
        start_time = time.time()
        history = model.fit(
            X_train_scaled, y_train,
            validation_data=(X_val_scaled, y_val),
            epochs=100,
            batch_size=32,
            callbacks=[early_stopping],
            verbose=0
        )
        training_time = time.time() - start_time
        
        # Evaluate
        val_loss, val_accuracy = model.evaluate(X_val_scaled, y_val, verbose=0)
        
        print(f"   ✓ Neural Network training completed")
        print(f"   - Validation accuracy: {val_accuracy:.4f}")
        print(f"   - Training time: {training_time:.2f}s")
        print(f"   - Best epoch: {len(history.history['loss']) - 10}")
        
        return model, scaler, val_accuracy
    
    def evaluate_models(self, models: dict, X_val, y_val, feature_names):
        """Comprehensive evaluation of all models"""
        print("\n" + "="*60)
        print("Model Evaluation Report")
        print("="*60)
        
        results = {}
        
        for name, model_info in models.items():
            print(f"\n{name.upper()} Model:")
            print("-"*40)
            
            if name == 'neural_network':
                model, scaler = model_info
                X_val_processed = scaler.transform(X_val)
                y_pred = model.predict(X_val_processed).argmax(axis=1)
            else:
                model = model_info
                X_val_processed = X_val
                y_pred = model.predict(X_val_processed)
            
            # Classification report
            report = classification_report(
                y_val, y_pred,
                target_names=['Normal', 'Warning', 'Critical'],
                output_dict=True
            )
            
            print("\nClassification Report:")
            print(f"{'Class':<15} {'Precision':<10} {'Recall':<10} {'F1-Score':<10}")
            print("-"*45)
            for class_name in ['Normal', 'Warning', 'Critical']:
                metrics = report[class_name]
                print(f"{class_name:<15} {metrics['precision']:<10.3f} "
                      f"{metrics['recall']:<10.3f} {metrics['f1-score']:<10.3f}")
            
            # Overall accuracy
            accuracy = report['accuracy']
            print(f"\nOverall Accuracy: {accuracy:.4f}")
            
            # Confusion matrix
            cm = confusion_matrix(y_val, y_pred)
            print("\nConfusion Matrix:")
            print(cm)
            
            results[name] = {
                'accuracy': accuracy,
                'report': report,
                'confusion_matrix': cm
            }
        
        return results
    
    def save_models(self, models: dict, feature_names: list):
        """Save trained models"""
        print("\n" + "="*60)
        print("Saving Models")
        print("="*60)
        
        # Save Random Forest
        if 'random_forest' in models:
            rf_path = os.path.join(self.model_path, 'heart_disease_rf_model.pkl')
            joblib.dump(models['random_forest'], rf_path)
            print(f"✓ Random Forest saved to: {rf_path}")
        
        # Save Gradient Boosting
        if 'gradient_boosting' in models:
            gb_path = os.path.join(self.model_path, 'heart_disease_gb_model.pkl')
            joblib.dump(models['gradient_boosting'], gb_path)
            print(f"✓ Gradient Boosting saved to: {gb_path}")
        
        # Save Neural Network
        if 'neural_network' in models:
            model, scaler = models['neural_network']
            
            # Save Keras model
            nn_path = os.path.join(self.model_path, 'heart_disease_nn_model.h5')
            model.save(nn_path)
            print(f"✓ Neural Network saved to: {nn_path}")
            
            # Save scaler
            scaler_path = os.path.join(self.model_path, 'heart_disease_scaler.pkl')
            joblib.dump(scaler, scaler_path)
            print(f"✓ Scaler saved to: {scaler_path}")
            
            # Convert to TensorFlow Lite
            converter = tf.lite.TFLiteConverter.from_keras_model(model)
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            tflite_model = converter.convert()
            
            tflite_path = os.path.join(self.model_path, 'heart_disease_nn_model.tflite')
            with open(tflite_path, 'wb') as f:
                f.write(tflite_model)
            print(f"✓ TensorFlow Lite model saved to: {tflite_path}")
        
        # Save feature names
        feature_path = os.path.join(self.model_path, 'heart_disease_features.pkl')
        joblib.dump(feature_names, feature_path)
        print(f"✓ Feature names saved to: {feature_path}")


def main():
    """Main training function"""
    print("="*60)
    print("Heart Disease Model Training")
    print("="*60)
    
    trainer = HeartDiseaseModelTrainer()
    
    # Step 1: Load heart disease datasets
    print("\n1. Loading Heart Disease Datasets...")
    loader = HeartDiseaseDataLoader()
    
    # Check if enhanced dataset exists
    enhanced_path = os.path.join(Config.DATA_PATH, 'enhanced_heart_disease_dataset.csv')
    if os.path.exists(enhanced_path):
        print("Loading existing enhanced dataset...")
        train_df = pd.read_csv(os.path.join(Config.DATA_PATH, 'heart_disease_train.csv'))
        val_df = pd.read_csv(os.path.join(Config.DATA_PATH, 'heart_disease_validation.csv'))
    else:
        print("Creating enhanced heart disease dataset...")
        enhanced_df = loader.load_all_heart_disease_datasets()
        if enhanced_df.empty:
            print("Failed to load heart disease datasets. Using synthetic data...")
            # Fallback to synthetic data
            generator = SyntheticDatasetGenerator()
            enhanced_df = generator.generate_synthetic_data(num_samples=10000)
            enhanced_df = generator.prepare_training_data(enhanced_df)
        
        train_df, val_df = loader.create_risk_stratified_dataset()
    
    # Step 2: Prepare features
    print("\n2. Preparing Features...")
    X_train, y_train, feature_names = trainer.prepare_features(train_df)
    X_val, y_val, _ = trainer.prepare_features(val_df)
    
    print(f"Training samples: {len(X_train)}")
    print(f"Validation samples: {len(X_val)}")
    print(f"Features: {feature_names}")
    print(f"Class distribution (train): {np.bincount(y_train)}")
    
    # Step 3: Train models
    print("\n3. Training Models...")
    models = {}
    
    # Random Forest
    rf_model, rf_score, feature_importance = trainer.train_random_forest_heart_disease(
        X_train, y_train, X_val, y_val
    )
    models['random_forest'] = rf_model
    
    # Display feature importance
    print("\n   Feature Importance (Random Forest):")
    for fname, importance in sorted(zip(feature_names, feature_importance), 
                                  key=lambda x: x[1], reverse=True):
        print(f"   - {fname}: {importance:.4f}")
    
    # Gradient Boosting
    gb_model, gb_score = trainer.train_gradient_boosting_heart_disease(
        X_train, y_train, X_val, y_val
    )
    models['gradient_boosting'] = gb_model
    
    # Neural Network
    nn_model, scaler, nn_score = trainer.train_neural_network_heart_disease(
        X_train, y_train, X_val, y_val
    )
    models['neural_network'] = (nn_model, scaler)
    
    # Step 4: Evaluate models
    evaluation_results = trainer.evaluate_models(models, X_val, y_val, feature_names)
    
    # Step 5: Save models
    trainer.save_models(models, feature_names)
    
    # Summary
    print("\n" + "="*60)
    print("Training Summary")
    print("="*60)
    print(f"Random Forest Accuracy: {rf_score:.4f}")
    print(f"Gradient Boosting Accuracy: {gb_score:.4f}")
    print(f"Neural Network Accuracy: {nn_score:.4f}")
    
    # Determine best model
    scores = {'Random Forest': rf_score, 'Gradient Boosting': gb_score, 'Neural Network': nn_score}
    best_model = max(scores, key=scores.get)
    print(f"\nBest Model: {best_model} ({scores[best_model]:.4f})")
    
    print("\n" + "="*60)
    print("Heart Disease Model Training Completed!")
    print("="*60)


if __name__ == "__main__":
    main()

