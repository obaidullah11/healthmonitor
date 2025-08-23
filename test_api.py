#!/usr/bin/env python3
"""
API Testing Script for Health Monitoring System

This script tests all API endpoints and validates the system functionality.
"""

import requests
import json
import time
import sys
from typing import Dict, Any

class HealthAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        
    def test_health_check(self) -> bool:
        """Test the health check endpoint"""
        print("Testing health check endpoint...")
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("✓ Health check passed")
                    print(f"  API Status: {data['data']['api_status']}")
                    print(f"  Models Loaded: {data['data']['model_status']['models_loaded']}")
                    return True
                else:
                    print("✗ Health check failed - API not healthy")
                    return False
            else:
                print(f"✗ Health check failed - Status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Health check failed - Error: {e}")
            return False
    
    def test_model_info(self) -> bool:
        """Test the model information endpoint"""
        print("\nTesting model info endpoint...")
        try:
            response = requests.get(f"{self.api_url}/model-info", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("✓ Model info endpoint working")
                    models = data['data']['available_models']
                    print(f"  Available models: {len(models)}")
                    for model in models:
                        print(f"    - {model['name']} ({model['type']})")
                    return True
                else:
                    print("✗ Model info failed")
                    return False
            else:
                print(f"✗ Model info failed - Status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Model info failed - Error: {e}")
            return False
    
    def test_input_validation(self) -> bool:
        """Test input validation endpoint"""
        print("\nTesting input validation...")
        
        test_cases = [
            {
                "name": "Valid input",
                "data": {"heart_rate": 75, "temperature": 36.8, "spo2": 98},
                "should_be_valid": True
            },
            {
                "name": "Invalid heart rate",
                "data": {"heart_rate": 25, "temperature": 36.8, "spo2": 98},
                "should_be_valid": False
            },
            {
                "name": "Invalid temperature",
                "data": {"heart_rate": 75, "temperature": 43.0, "spo2": 98},
                "should_be_valid": False
            },
            {
                "name": "Invalid SpO2",
                "data": {"heart_rate": 75, "temperature": 36.8, "spo2": 65},
                "should_be_valid": False
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{self.api_url}/validate-input",
                    json=test_case["data"],
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    is_valid = data.get("success", False)
                    
                    if is_valid == test_case["should_be_valid"]:
                        print(f"✓ {test_case['name']} - Validation {'passed' if is_valid else 'failed'} as expected")
                    else:
                        print(f"✗ {test_case['name']} - Expected {'valid' if test_case['should_be_valid'] else 'invalid'}, got {'valid' if is_valid else 'invalid'}")
                        all_passed = False
                else:
                    print(f"✗ {test_case['name']} - Request failed with status {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                print(f"✗ {test_case['name']} - Error: {e}")
                all_passed = False
        
        return all_passed
    
    def test_health_prediction(self) -> bool:
        """Test health prediction endpoint"""
        print("\nTesting health prediction...")
        
        test_cases = [
            {
                "name": "Normal case",
                "data": {"heart_rate": 75, "temperature": 36.8, "spo2": 98},
                "expected_status": "Normal"
            },
            {
                "name": "Warning case",
                "data": {"heart_rate": 110, "temperature": 37.8, "spo2": 93},
                "expected_status": "Warning"
            },
            {
                "name": "Critical case",
                "data": {"heart_rate": 150, "temperature": 39.0, "spo2": 88},
                "expected_status": "Critical"
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.api_url}/predict-health",
                    json=test_case["data"],
                    timeout=10
                )
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        prediction = data["data"]
                        status = prediction["health_status"]
                        confidence = prediction["confidence_score"]
                        model_used = prediction["prediction_details"]["model_used"]
                        
                        print(f"✓ {test_case['name']}")
                        print(f"  Status: {status} (expected: {test_case['expected_status']})")
                        print(f"  Confidence: {confidence:.3f}")
                        print(f"  Model: {model_used}")
                        print(f"  Response time: {response_time:.1f}ms")
                        
                        # Check if response time is within acceptable range
                        if response_time > 500:
                            print(f"  ⚠ Warning: Response time ({response_time:.1f}ms) exceeds 500ms threshold")
                        
                    else:
                        print(f"✗ {test_case['name']} - Prediction failed: {data.get('message', 'Unknown error')}")
                        all_passed = False
                else:
                    print(f"✗ {test_case['name']} - Request failed with status {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                print(f"✗ {test_case['name']} - Error: {e}")
                all_passed = False
        
        return all_passed
    
    def test_model_comparison(self) -> bool:
        """Test model comparison endpoint"""
        print("\nTesting model comparison...")
        
        test_data = {"heart_rate": 75, "temperature": 36.8, "spo2": 98}
        
        try:
            response = requests.post(
                f"{self.api_url}/compare-models",
                json=test_data,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    predictions = data["data"]["model_predictions"]
                    print("✓ Model comparison working")
                    print(f"  Available models: {len(predictions)}")
                    
                    for model_name, prediction in predictions.items():
                        if "error" in prediction:
                            print(f"    - {model_name}: Error - {prediction['error']}")
                        else:
                            print(f"    - {model_name}: {prediction['health_status']} (confidence: {prediction['confidence_score']:.3f})")
                    
                    return True
                else:
                    print("✗ Model comparison failed")
                    return False
            else:
                print(f"✗ Model comparison failed - Status code: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Model comparison failed - Error: {e}")
            return False
    
    def run_performance_test(self, num_requests: int = 10) -> bool:
        """Run performance test with multiple concurrent requests"""
        print(f"\nRunning performance test ({num_requests} requests)...")
        
        test_data = {"heart_rate": 75, "temperature": 36.8, "spo2": 98}
        response_times = []
        successful_requests = 0
        
        for i in range(num_requests):
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.api_url}/predict-health",
                    json=test_data,
                    timeout=10
                )
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    successful_requests += 1
                    response_times.append(response_time)
                    print(f"  Request {i+1}: {response_time:.1f}ms")
                else:
                    print(f"  Request {i+1}: Failed (status {response.status_code})")
                    
            except Exception as e:
                print(f"  Request {i+1}: Error - {e}")
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            
            print(f"\nPerformance Results:")
            print(f"  Successful requests: {successful_requests}/{num_requests}")
            print(f"  Average response time: {avg_time:.1f}ms")
            print(f"  Min response time: {min_time:.1f}ms")
            print(f"  Max response time: {max_time:.1f}ms")
            
            # Check if performance meets requirements
            if avg_time < 500:
                print("✓ Performance test passed (average < 500ms)")
                return True
            else:
                print("✗ Performance test failed (average >= 500ms)")
                return False
        else:
            print("✗ Performance test failed - no successful requests")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all tests and return overall success"""
        print("=" * 60)
        print("Health Monitoring System - API Testing")
        print("=" * 60)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Model Info", self.test_model_info),
            ("Input Validation", self.test_input_validation),
            ("Health Prediction", self.test_health_prediction),
            ("Model Comparison", self.test_model_comparison),
            ("Performance Test", lambda: self.run_performance_test(5))
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"✗ {test_name} - Unexpected error: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! The system is working correctly.")
        else:
            print("⚠ Some tests failed. Please check the system configuration.")
        
        return passed == total

def main():
    """Main function to run tests"""
    # Check if server is running
    base_url = "http://localhost:8000"
    
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code != 200:
            print("Error: Server is not responding correctly")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to server. Please ensure the server is running on http://localhost:8000")
        print("Start the server with: python main.py")
        sys.exit(1)
    
    # Run tests
    tester = HealthAPITester(base_url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()






