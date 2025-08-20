#!/usr/bin/env python3
"""
Test script for Heart Disease Risk Assessment API

This script tests the heart disease prediction endpoints with various test cases
representing different risk levels.
"""

import requests
import json
import time
from typing import Dict, Any


class HeartDiseaseAPITester:
    """Test the heart disease prediction API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        
    def test_health_check(self) -> bool:
        """Test if the API is running"""
        try:
            response = requests.get(f"{self.api_url}/health")
            if response.status_code == 200:
                data = response.json()
                print("✓ API Health Check: Success")
                print(f"  - Status: {data['data']['api_status']}")
                print(f"  - Models loaded: {data['data']['model_status']['models_loaded']}")
                return True
            else:
                print("✗ API Health Check: Failed")
                return False
        except Exception as e:
            print(f"✗ API Health Check: Error - {e}")
            return False
    
    def test_heart_disease_prediction(self, test_case: Dict[str, Any], case_name: str):
        """Test heart disease prediction endpoint"""
        print(f"\n{case_name}:")
        print("-" * 50)
        
        # Display input data
        print("Input Parameters:")
        for key, value in test_case.items():
            print(f"  - {key}: {value}")
        
        try:
            # Make prediction request
            start_time = time.time()
            response = requests.post(
                f"{self.api_url}/predict-heart-disease",
                json=test_case,
                headers={"Content-Type": "application/json"}
            )
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    result = data['data']
                    
                    print(f"\n✓ Prediction Success (Response time: {response_time:.2f}ms)")
                    print(f"\nRisk Assessment:")
                    print(f"  - Risk Level: {result['risk_level']}")
                    print(f"  - 10-Year Risk: {result['risk_percentage']}%")
                    print(f"  - Confidence: {result['confidence_score']*100:.1f}%")
                    
                    print(f"\nRisk Factors Identified:")
                    if result['risk_factors']:
                        for factor in result['risk_factors']:
                            modifiable = "✓ Modifiable" if factor['modifiable'] else "✗ Non-modifiable"
                            print(f"  - {factor['factor']} ({factor['severity']}): {factor['value']} → Target: {factor['target']} [{modifiable}]")
                    else:
                        print("  - No significant risk factors identified")
                    
                    print(f"\nRisk Scores Breakdown:")
                    scores = result['risk_scores']
                    print(f"  - Traditional: {scores['traditional']['level']} ({len(scores['traditional']['factors'])} factors)")
                    print(f"  - Framingham: {scores['framingham']['percentage']}% ({scores['framingham']['level']})")
                    print(f"  - AI-Based: {scores['ai_based']['percentage']}% ({scores['ai_based']['level']})")
                    
                    print(f"\nRecommendations:")
                    for i, rec in enumerate(result['recommendations'], 1):
                        print(f"  {i}. {rec}")
                else:
                    print(f"✗ Prediction Failed: {data['message']}")
            else:
                print(f"✗ Request Failed: Status {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def run_all_tests(self):
        """Run all test cases"""
        print("="*60)
        print("Heart Disease Risk Assessment API Tests")
        print("="*60)
        
        # Check API health first
        if not self.test_health_check():
            print("\nAPI is not running. Please start the server first.")
            return
        
        # Test cases representing different risk levels
        test_cases = [
            # Low Risk Case
            {
                "name": "Test Case 1: Low Risk Patient",
                "data": {
                    "heart_rate": 70,
                    "temperature": 36.8,
                    "spo2": 98,
                    "age": 30,
                    "blood_pressure_systolic": 115,
                    "blood_pressure_diastolic": 75,
                    "cholesterol": 180
                }
            },
            
            # Moderate Risk Case
            {
                "name": "Test Case 2: Moderate Risk Patient",
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
            
            # High Risk Case
            {
                "name": "Test Case 3: High Risk Patient",
                "data": {
                    "heart_rate": 95,
                    "temperature": 37.0,
                    "spo2": 94,
                    "age": 65,
                    "blood_pressure_systolic": 145,
                    "blood_pressure_diastolic": 92,
                    "cholesterol": 250
                }
            },
            
            # Very High Risk Case
            {
                "name": "Test Case 4: Very High Risk Patient",
                "data": {
                    "heart_rate": 110,
                    "temperature": 37.2,
                    "spo2": 92,
                    "age": 70,
                    "blood_pressure_systolic": 160,
                    "blood_pressure_diastolic": 95,
                    "cholesterol": 280
                }
            },
            
            # Young Patient with Risk Factors
            {
                "name": "Test Case 5: Young Patient with Risk Factors",
                "data": {
                    "heart_rate": 90,
                    "temperature": 36.7,
                    "spo2": 97,
                    "age": 35,
                    "blood_pressure_systolic": 140,
                    "blood_pressure_diastolic": 90,
                    "cholesterol": 260
                }
            }
        ]
        
        # Run tests
        for test in test_cases:
            self.test_heart_disease_prediction(test["data"], test["name"])
            print()
        
        # Test regular health prediction for comparison
        print("\n" + "="*60)
        print("Regular Health Status Prediction (for comparison)")
        print("="*60)
        
        test_case = test_cases[2]["data"]  # Use high risk case
        try:
            response = requests.post(
                f"{self.api_url}/predict-health",
                json=test_case,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    result = data['data']
                    print(f"Health Status: {result['health_status']}")
                    print(f"Confidence: {result['confidence_score']*100:.1f}%")
                    print(f"Action: {result['suggested_action']}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n" + "="*60)
        print("Testing Complete!")
        print("="*60)


def main():
    """Main test function"""
    tester = HeartDiseaseAPITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()

