#!/usr/bin/env python3
"""
Test script for the Integrated Health + Heart Disease API

This script tests the enhanced /predict-health endpoint that now includes
heart disease risk assessment in the response.
"""

import requests
import json
import time
from typing import Dict, Any


def test_integrated_endpoint(base_url: str = "http://localhost:8000"):
    """Test the integrated health prediction endpoint"""
    
    api_url = f"{base_url}/api/v1"
    
    print("="*60)
    print("Testing Integrated Health + Heart Disease Prediction")
    print("="*60)
    
    # Test cases
    test_cases = [
        {
            "name": "Young Healthy Person",
            "data": {
                "heart_rate": 70,
                "temperature": 36.8,
                "spo2": 98,
                "age": 25,
                "blood_pressure_systolic": 115,
                "blood_pressure_diastolic": 75,
                "cholesterol": 160
            }
        },
        {
            "name": "Middle-aged with Some Risk Factors",
            "data": {
                "heart_rate": 85,
                "temperature": 36.9,
                "spo2": 96,
                "age": 50,
                "blood_pressure_systolic": 135,
                "blood_pressure_diastolic": 85,
                "cholesterol": 220
            }
        },
        {
            "name": "Older Person with High Risk",
            "data": {
                "heart_rate": 95,
                "temperature": 37.0,
                "spo2": 94,
                "age": 65,
                "blood_pressure_systolic": 150,
                "blood_pressure_diastolic": 95,
                "cholesterol": 260
            }
        }
    ]
    
    for test in test_cases:
        print(f"\nTest Case: {test['name']}")
        print("-" * 50)
        
        # Display input
        print("Input Parameters:")
        for key, value in test['data'].items():
            print(f"  - {key}: {value}")
        
        try:
            # Make request
            start_time = time.time()
            response = requests.post(
                f"{api_url}/predict-health",
                json=test['data'],
                headers={"Content-Type": "application/json"}
            )
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    result = data['data']
                    
                    print(f"\n✓ Request successful (Response time: {response_time:.2f}ms)")
                    
                    # General Health Status
                    print("\n📊 General Health Assessment:")
                    print(f"  - Status: {result['health_status']}")
                    print(f"  - Confidence: {result['confidence_score']*100:.1f}%")
                    print(f"  - Action: {result['suggested_action']}")
                    
                    # Heart Disease Risk
                    if 'heart_disease_assessment' in result:
                        cvd = result['heart_disease_assessment']
                        print("\n❤️  Cardiovascular Risk Assessment:")
                        print(f"  - Risk Level: {cvd['risk_level']}")
                        print(f"  - 10-Year Risk: {cvd['risk_percentage']}%")
                        
                        if cvd['major_risk_factors']:
                            print(f"  - Major Risk Factors: {', '.join(cvd['major_risk_factors'])}")
                        else:
                            print("  - Major Risk Factors: None identified")
                        
                        if cvd['primary_recommendation']:
                            print(f"  - Recommendation: {cvd['primary_recommendation']}")
                    else:
                        print("\n⚠️  No heart disease assessment included in response")
                else:
                    print(f"✗ Request failed: {data['message']}")
            else:
                print(f"✗ HTTP Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60)
    
    # Summary
    print("\nSummary:")
    print("The /predict-health endpoint now provides:")
    print("1. General health status (Normal/Warning/Critical)")
    print("2. Heart disease risk assessment (Low/Moderate/High/Very High)")
    print("3. Major risk factors identification")
    print("4. Primary recommendation for cardiovascular health")
    print("\nAll in a single API call!")


def main():
    """Main function"""
    # Check if API is running
    try:
        response = requests.get("http://localhost:8000/api/v1/health")
        if response.status_code == 200:
            print("✓ API is running")
            test_integrated_endpoint()
        else:
            print("✗ API health check failed")
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API. Please ensure the server is running:")
        print("  python main.py")


if __name__ == "__main__":
    main()


