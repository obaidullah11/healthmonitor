import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import joblib
import os
import time
from typing import Tuple, Dict, Any
from config import Config

class HealthMLModels:
    """Machine learning models for health status prediction"""
    
    def __init__(self):
        self.config = Config.get_training_config()
        self.model_path = Config.MODEL_PATH
        self.rf_model = None
        self.nn_model = None
        self.rf_model_file = Config.RANDOM_FOREST_MODEL_FILE
        self.nn_model_file = Config.NEURAL_NETWORK_MODEL_FILE
        
    def train_random_forest(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Train Random Forest model"""
        print("Training Random Forest model...")
        start_time = time.time()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.config["test_size"], 
            random_state=self.config["random_state"], stratify=y
        )
        
        # Train model
        self.rf_model = RandomForestClassifier(
            n_estimators=self.config["random_forest"]["n_estimators"],
            max_depth=self.config["random_forest"]["max_depth"],
            random_state=self.config["random_forest"]["random_state"]
        )
        
        self.rf_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.rf_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        training_time = time.time() - start_time
        
        # Test inference time
        inference_start = time.time()
        _ = self.rf_model.predict(X_test[:100])
        inference_time = (time.time() - inference_start) / 100  # Average per prediction
        
        results = {
            "model_type": "Random Forest",
            "accuracy": accuracy,
            "training_time": training_time,
            "inference_time_ms": inference_time * 1000,
            "classification_report": classification_report(y_test, y_pred),
            "feature_importance": dict(zip(
                ['heart_rate', 'temperature', 'spo2', 'age', 'bp_systolic', 'bp_diastolic', 'cholesterol'], 
                self.rf_model.feature_importances_
            ))
        }
        
        print(f"Random Forest - Accuracy: {accuracy:.4f}, Training Time: {training_time:.2f}s")
        return results
    
    def build_neural_network(self, input_shape: Tuple[int, ...]) -> keras.Model:
        """Build neural network for 6 input features"""
        model = keras.Sequential([
            layers.Dense(128, activation='relu', input_shape=input_shape),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(64, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.1),
            
            layers.Dense(16, activation='relu'),
            layers.Dense(3, activation='softmax')  # 3 classes: Normal, Warning, Critical
        ])
        
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def train_neural_network(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Train Neural Network model"""
        print("Training Neural Network model...")
        start_time = time.time()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.config["test_size"], 
            random_state=self.config["random_state"], stratify=y
        )
        
        # Build and train model
        self.nn_model = self.build_neural_network((X.shape[1],))
        
        history = self.nn_model.fit(
            X_train, y_train,
            epochs=self.config["neural_network"]["epochs"],
            batch_size=self.config["neural_network"]["batch_size"],
            validation_split=self.config["neural_network"]["validation_split"],
            verbose=1
        )
        
        # Evaluate
        y_pred = np.argmax(self.nn_model.predict(X_test), axis=1)
        accuracy = accuracy_score(y_test, y_pred)
        
        training_time = time.time() - start_time
        
        # Test inference time
        inference_start = time.time()
        _ = self.nn_model.predict(X_test[:100])
        inference_time = (time.time() - inference_start) / 100
        
        results = {
            "model_type": "Neural Network",
            "accuracy": accuracy,
            "training_time": training_time,
            "inference_time_ms": inference_time * 1000,
            "classification_report": classification_report(y_test, y_pred),
            "training_history": history.history
        }
        
        print(f"Neural Network - Accuracy: {accuracy:.4f}, Training Time: {training_time:.2f}s")
        return results
    
    def compare_models(self, rf_results: Dict[str, Any], nn_results: Dict[str, Any]) -> Dict[str, Any]:
        """Compare the performance of both models"""
        comparison = {
            "random_forest": {
                "accuracy": rf_results["accuracy"],
                "training_time": rf_results["training_time"],
                "inference_time_ms": rf_results["inference_time_ms"]
            },
            "neural_network": {
                "accuracy": nn_results["accuracy"],
                "training_time": nn_results["training_time"],
                "inference_time_ms": nn_results["inference_time_ms"]
            },
            "recommendation": None
        }
        
        # Determine recommendation based on accuracy and speed
        if rf_results["accuracy"] > nn_results["accuracy"]:
            if rf_results["inference_time_ms"] < 100:  # Sub-100ms threshold
                comparison["recommendation"] = "random_forest"
            else:
                comparison["recommendation"] = "neural_network"
        else:
            comparison["recommendation"] = "neural_network"
        
        return comparison
    
    def save_models(self):
        """Save trained models to disk"""
        os.makedirs(self.model_path, exist_ok=True)
        
        # Save Random Forest
        if self.rf_model:
            rf_path = os.path.join(self.model_path, self.rf_model_file)
            joblib.dump(self.rf_model, rf_path)
            print(f"Random Forest model saved to: {rf_path}")
        
        # Save Neural Network
        if self.nn_model:
            nn_path = os.path.join(self.model_path, self.nn_model_file.replace('.tflite', '.h5'))
            self.nn_model.save(nn_path)
            print(f"Neural Network model saved to: {nn_path}")
            
            # Convert to TensorFlow Lite
            self.convert_to_tflite(nn_path)
    
    def convert_to_tflite(self, model_path: str):
        """Convert Keras model to TensorFlow Lite format"""
        try:
            # Load the saved model
            model = keras.models.load_model(model_path)
            
            # Convert to TensorFlow Lite
            converter = tf.lite.TFLiteConverter.from_keras_model(model)
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            tflite_model = converter.convert()
            
            # Save the TFLite model
            tflite_path = os.path.join(self.model_path, self.nn_model_file)
            with open(tflite_path, 'wb') as f:
                f.write(tflite_model)
            
            print(f"TensorFlow Lite model saved to: {tflite_path}")
            
        except Exception as e:
            print(f"Error converting to TensorFlow Lite: {e}")
    
    def load_models(self):
        """Load trained models from disk"""
        # Load Random Forest
        rf_path = os.path.join(self.model_path, self.rf_model_file)
        if os.path.exists(rf_path):
            self.rf_model = joblib.load(rf_path)
            print(f"Random Forest model loaded from: {rf_path}")
        
        # Load Neural Network (TFLite)
        nn_path = os.path.join(self.model_path, self.nn_model_file)
        if os.path.exists(nn_path):
            self.nn_model = nn_path  # Store path for TFLite interpreter
            print(f"Neural Network model loaded from: {nn_path}")
    
    def predict_rf(self, features: np.ndarray) -> Tuple[int, float]:
        """Make prediction using Random Forest model"""
        if self.rf_model is None:
            raise ValueError("Random Forest model not loaded")
        
        # Get prediction and probability
        prediction = self.rf_model.predict(features.reshape(1, -1))[0]
        probabilities = self.rf_model.predict_proba(features.reshape(1, -1))[0]
        confidence = np.max(probabilities)
        
        return prediction, confidence
    
    def predict_nn(self, features: np.ndarray) -> Tuple[int, float]:
        """Make prediction using Neural Network model (TFLite)"""
        if self.nn_model is None:
            raise ValueError("Neural Network model not loaded")
        
        try:
            # Load TFLite interpreter
            interpreter = tf.lite.Interpreter(model_path=self.nn_model)
            interpreter.allocate_tensors()
            
            # Get input and output tensors
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            
            # Set input tensor
            interpreter.set_tensor(input_details[0]['index'], features.reshape(1, -1).astype(np.float32))
            
            # Run inference
            interpreter.invoke()
            
            # Get output
            output = interpreter.get_tensor(output_details[0]['index'])
            prediction = np.argmax(output[0])
            confidence = np.max(output[0])
            
            return prediction, confidence
            
        except Exception as e:
            print(f"Error in Neural Network prediction: {e}")
            # Fallback to Random Forest if available
            if self.rf_model:
                return self.predict_rf(features)
            else:
                raise ValueError("No models available for prediction")

