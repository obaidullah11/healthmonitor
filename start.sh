#!/bin/bash

echo "Starting Health Monitoring System..."

# Check if models exist, if not, train them
if [ ! -f "models/random_forest_model.pkl" ] || [ ! -f "models/neural_network_model.h5" ]; then
    echo "Models not found. Training models..."
    python train_models.py
    
    # Check if training was successful
    if [ $? -eq 0 ]; then
        echo "Model training completed successfully!"
    else
        echo "Error: Model training failed!"
        exit 1
    fi
else
    echo "Models found. Skipping training..."
fi

# Create necessary directories if they don't exist
mkdir -p data/processed
mkdir -p data/raw
mkdir -p models

# Start the FastAPI application
echo "Starting FastAPI server on port $PORT..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
