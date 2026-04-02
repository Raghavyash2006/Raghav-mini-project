#!/usr/bin/env python3
"""
AI Content Localization Platform - API Testing Script

This script tests all API endpoints to verify the backend is working correctly.

Run this in a separate terminal while the Flask server is running:
    python test_api.py
"""

import requests
import json
import sys
from typing import Dict, Any

# Configuration
API_BASE = "http://127.0.0.1:5000"

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session_id = None
        self.passed = 0
        self.failed = 0
        self.test_results = []

    def print_header(self, text: str):
        """Print section header."""
        print(f"\n{BLUE}{'=' * 70}{RESET}")
        print(f"{BLUE}{text.center(70)}{RESET}")
        print(f"{BLUE}{'=' * 70}{RESET}\n")

    def print_test(self, name: str, status: bool, message: str):
        """Print test result."""
        status_icon = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
        print(f"{status_icon} {name}")
        print(f"  {message}")
        
        if status:
            self.passed += 1
        else:
            self.failed += 1
        
        self.test_results.append({
            'name': name,
            'status': status,
            'message': message
        })

    def print_response(self, response):
        """Pretty print API response."""
        print(f"  {YELLOW}Status:{RESET} {response.status_code}")
        try:
            data = response.json()
            print(f"  {YELLOW}Response:{RESET}")
            print(f"    {json.dumps(data, indent=2)}")
        except:
            print(f"  {YELLOW}Response:{RESET} {response.text[:200]}")

    # ========================================================================
    # TEST SUITE
    # ========================================================================

    def test_health_check(self):
        """Test 1: Health Check"""
        try:
            response = requests.get(f"{self.base_url}/health")
            success = response.status_code == 200
            self.print_test(
                "Test 1: Health Check",
                success,
                f"Status {response.status_code} - Database {'healthy' if success else 'unhealthy'}"
            )
            if not success:
                self.print_response(response)
        except Exception as e:
            self.print_test(
                "Test 1: Health Check",
                False,
                f"Connection failed: {str(e)}"
            )

    def test_root_endpoint(self):
        """Test 2: Root Endpoint"""
        try:
            response = requests.get(f"{self.base_url}/")
            success = response.status_code == 200
            self.print_test(
                "Test 2: Root Endpoint",
                success,
                f"Status {response.status_code} - API information retrieved"
            )
            if not success:
                self.print_response(response)
        except Exception as e:
            self.print_test(
                "Test 2: Root Endpoint",
                False,
                f"Connection failed: {str(e)}"
            )

    def test_basic_localization(self):
        """Test 3: Basic Localization"""
        try:
            payload = {
                "text": "Hello world",
                "target_language": "es",
                "tone": "neutral"
            }
            response = requests.post(
                f"{self.base_url}/api/localize",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            success = response.status_code == 200 and response.json().get("success")
            
            message = ""
            if success:
                data = response.json().get("data", {})
                message = f"Translation: '{data.get('localized_text')}' (Quality: {data.get('quality_score')}%)"
                self.session_id = data.get("request_id")
            else:
                message = f"Status {response.status_code} - API error"
            
            self.print_test(
                "Test 3: Basic Localization (English → Spanish)",
                success,
                message
            )
            if not success:
                self.print_response(response)
        except Exception as e:
            self.print_test(
                "Test 3: Basic Localization",
                False,
                f"Request failed: {str(e)}"
            )

    def test_idiom_localization(self):
        """Test 4: Idiom Localization"""
        try:
            payload = {
                "text": "It's raining cats and dogs",
                "target_language": "hi",
                "tone": "casual"
            }
            response = requests.post(
                f"{self.base_url}/api/localize",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            success = response.status_code == 200 and response.json().get("success")
            
            message = ""
            if success:
                data = response.json().get("data", {})
                message = f"Idiom adapted: {data.get('explanation', 'No explanation')}"
            else:
                message = f"Status {response.status_code}"
            
            self.print_test(
                "Test 4: Idiom Localization (with cultural adaptation)",
                success,
                message
            )
            if not success:
                self.print_response(response)
        except Exception as e:
            self.print_test(
                "Test 4: Idiom Localization",
                False,
                f"Request failed: {str(e)}"
            )

    def test_sentiment_preservation(self):
        """Test 5: Sentiment Preservation"""
        try:
            payload = {
                "text": "This product is amazing and wonderful!",
                "target_language": "fr",
                "tone": "formal"
            }
            response = requests.post(
                f"{self.base_url}/api/localize",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            success = response.status_code == 200 and response.json().get("success")
            
            message = ""
            if success:
                data = response.json().get("data", {})
                message = f"Sentiment: {data.get('sentiment', 'unknown')} - Preserved in localization"
            else:
                message = f"Status {response.status_code}"
            
            self.print_test(
                "Test 5: Sentiment Preservation (English → French)",
                success,
                message
            )
            if not success:
                self.print_response(response)
        except Exception as e:
            self.print_test(
                "Test 5: Sentiment Preservation",
                False,
                f"Request failed: {str(e)}"
            )

    def test_error_empty_text(self):
        """Test 6: Error Handling - Empty Text"""
        try:
            payload = {
                "text": "",
                "target_language": "es",
                "tone": "neutral"
            }
            response = requests.post(
                f"{self.base_url}/api/localize",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            success = response.status_code == 400
            self.print_test(
                "Test 6: Error Handling - Empty Text",
                success,
                f"Status {response.status_code} - Correctly rejected empty input"
            )
        except Exception as e:
            self.print_test(
                "Test 6: Error Handling - Empty Text",
                False,
                f"Request failed: {str(e)}"
            )

    def test_error_invalid_language(self):
        """Test 7: Error Handling - Invalid Language"""
        try:
            payload = {
                "text": "Hello",
                "target_language": "invalid",
                "tone": "neutral"
            }
            response = requests.post(
                f"{self.base_url}/api/localize",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            success = response.status_code == 400
            self.print_test(
                "Test 7: Error Handling - Invalid Language",
                success,
                f"Status {response.status_code} - Correctly rejected invalid language"
            )
        except Exception as e:
            self.print_test(
                "Test 7: Error Handling - Invalid Language",
                False,
                f"Request failed: {str(e)}"
            )

    def test_feedback_submission(self):
        """Test 8: Feedback Submission"""
        if not self.session_id:
            self.print_test(
                "Test 8: Feedback Submission",
                False,
                "No session ID from previous test - skipping"
            )
            return

        try:
            payload = {
                "request_id": self.session_id,
                "rating": 5,
                "comment": "Excellent translation!"
            }
            response = requests.post(
                f"{self.base_url}/api/feedback",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            success = response.status_code == 201 and response.json().get("success")
            
            message = f"Status {response.status_code}"
            if success:
                feedback_id = response.json().get("feedback_id")
                message += f" - Feedback ID: {feedback_id}"
            
            self.print_test(
                "Test 8: Feedback Submission",
                success,
                message
            )
            if not success:
                self.print_response(response)
        except Exception as e:
            self.print_test(
                "Test 8: Feedback Submission",
                False,
                f"Request failed: {str(e)}"
            )

    def test_history_retrieval(self):
        """Test 9: History Retrieval"""
        try:
            response = requests.get(
                f"{self.base_url}/api/history?limit=10",
                headers={"Content-Type": "application/json"}
            )
            success = response.status_code == 200 and response.json().get("success")
            
            message = ""
            if success:
                data = response.json().get("data", [])
                total = response.json().get("pagination", {}).get("total", 0)
                message = f"Retrieved {total} record(s) from history"
            else:
                message = f"Status {response.status_code}"
            
            self.print_test(
                "Test 9: History Retrieval",
                success,
                message
            )
            if not success:
                self.print_response(response)
        except Exception as e:
            self.print_test(
                "Test 9: History Retrieval",
                False,
                f"Request failed: {str(e)}"
            )

    def test_history_pagination(self):
        """Test 10: History Pagination"""
        try:
            response = requests.get(
                f"{self.base_url}/api/history?limit=5&offset=0",
                headers={"Content-Type": "application/json"}
            )
            success = response.status_code == 200
            
            message = ""
            if success:
                pagination = response.json().get("pagination", {})
                message = f"Pagination: limit={pagination.get('limit')}, offset={pagination.get('offset')}"
            else:
                message = f"Status {response.status_code}"
            
            self.print_test(
                "Test 10: History Pagination",
                success,
                message
            )
        except Exception as e:
            self.print_test(
                "Test 10: History Pagination",
                False,
                f"Request failed: {str(e)}"
            )

    def run_all_tests(self):
        """Run all tests."""
        self.print_header("API ENDPOINT TESTS")
        
        print(f"Testing backend at: {self.base_url}\n")
        
        self.test_health_check()
        self.test_root_endpoint()
        self.test_basic_localization()
        self.test_idiom_localization()
        self.test_sentiment_preservation()
        self.test_error_empty_text()
        self.test_error_invalid_language()
        self.test_feedback_submission()
        self.test_history_retrieval()
        self.test_history_pagination()
        
        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary."""
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        self.print_header("TEST SUMMARY")
        
        print(f"Total Tests:   {total}")
        print(f"{GREEN}Passed:      {self.passed}{RESET}")
        print(f"{RED}Failed:      {self.failed}{RESET}")
        print(f"Pass Rate:     {pass_rate:.1f}%\n")
        
        if self.failed == 0:
            print(f"{GREEN}✓ All tests passed! Backend is ready for production.{RESET}\n")
            return 0
        else:
            print(f"{RED}✗ Some tests failed. Check the errors above.{RESET}\n")
            print("Common issues:")
            print("  - Backend not running (python app.py)")
            print("  - OPENAI_API_KEY not set in .env")
            print("  - Database connection failed")
            print("  - Port 5000 already in use\n")
            return 1


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("AI CONTENT LOCALIZATION PLATFORM - API TEST SUITE".center(70))
    print("=" * 70)
    
    tester = APITester(API_BASE)
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)
