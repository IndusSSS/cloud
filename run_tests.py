#!/usr/bin/env python3
"""
Comprehensive Test Runner for SmartSecurity Cloud Platform

This script runs all tests and provides detailed reporting on the test results.
"""

import subprocess
import sys
import json
import time
from datetime import datetime
from pathlib import Path


def run_command(command, description):
    """Run a command and return the result."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print('='*60)
    
    start_time = time.time()
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        end_time = time.time()
        
        print(f"Exit Code: {result.returncode}")
        print(f"Duration: {end_time - start_time:.2f} seconds")
        
        if result.stdout:
            print("\nSTDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        return result
        
    except Exception as e:
        print(f"Error running command: {e}")
        return None


def run_tests():
    """Run all tests and generate reports."""
    print("🚀 SmartSecurity Cloud Platform - Comprehensive Test Suite")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python Version: {sys.version}")
    
    # Test 1: Basic test run
    print("\n" + "="*80)
    print("TEST 1: Basic Test Execution")
    print("="*80)
    
    result1 = run_command(
        "python -m pytest tests/ -v --tb=short",
        "Running all tests with verbose output"
    )
    
    # Test 2: Test with coverage
    print("\n" + "="*80)
    print("TEST 2: Test Coverage Analysis")
    print("="*80)
    
    result2 = run_command(
        "python -m pytest tests/ --cov=app --cov-report=term-missing --cov-report=html",
        "Running tests with coverage analysis"
    )
    
    # Test 3: Specific test categories
    print("\n" + "="*80)
    print("TEST 3: Individual Test Categories")
    print("="*80)
    
    test_categories = [
        ("Authentication Tests", "tests/test_auth_endpoints.py"),
        ("Device Management Tests", "tests/test_device_endpoints.py"),
        ("Data Ingestion Tests", "tests/test_data_ingestion.py"),
        ("MQTT Integration Tests", "tests/test_mqtt_ingest.py"),
        ("Integration Tests", "tests/test_integration.py"),
        ("Health Check Tests", "tests/test_health.py"),
        ("Customer API Tests", "tests/test_customer_api.py"),
    ]
    
    category_results = {}
    
    for category_name, test_file in test_categories:
        print(f"\n--- {category_name} ---")
        result = run_command(
            f"python -m pytest {test_file} -v --tb=short",
            f"Running {category_name}"
        )
        category_results[category_name] = result.returncode if result else -1
    
    # Test 4: Performance tests
    print("\n" + "="*80)
    print("TEST 4: Performance Tests")
    print("="*80)
    
    result4 = run_command(
        "python -m pytest tests/test_integration.py::test_performance_considerations -v",
        "Running performance tests"
    )
    
    # Test 5: Security tests
    print("\n" + "="*80)
    print("TEST 5: Security Tests")
    print("="*80)
    
    result5 = run_command(
        "python -m pytest tests/test_auth_endpoints.py::test_password_hashing tests/test_auth_endpoints.py::test_jwt_token_creation tests/test_integration.py::test_security_integration -v",
        "Running security tests"
    )
    
    # Generate summary report
    print("\n" + "="*80)
    print("📊 TEST SUMMARY REPORT")
    print("="*80)
    
    # Parse test results
    if result1 and result1.stdout:
        lines = result1.stdout.split('\n')
        for line in lines:
            if 'passed' in line and 'failed' in line:
                print(f"Overall Test Results: {line.strip()}")
                break
    
    print(f"\nCategory Results:")
    for category, exit_code in category_results.items():
        status = "✅ PASSED" if exit_code == 0 else "❌ FAILED"
        print(f"  {category}: {status}")
    
    print(f"\nPerformance Tests: {'✅ PASSED' if result4 and result4.returncode == 0 else '❌ FAILED'}")
    print(f"Security Tests: {'✅ PASSED' if result5 and result5.returncode == 0 else '❌ FAILED'}")
    
    # Generate recommendations
    print(f"\n🔧 RECOMMENDATIONS:")
    print("1. Fix failing tests (see detailed output above)")
    print("2. Review coverage report in htmlcov/index.html")
    print("3. Address any security warnings")
    print("4. Consider adding more edge case tests")
    
    print(f"\n📁 Generated Reports:")
    print("- Coverage report: htmlcov/index.html")
    print("- Test results: See console output above")
    print("- Comprehensive report: COMPREHENSIVE_TEST_REPORT.md")
    
    print(f"\n🎯 Next Steps:")
    print("1. Review failing tests and fix issues")
    print("2. Improve test coverage for uncovered areas")
    print("3. Add integration tests with real database")
    print("4. Set up continuous integration pipeline")
    
    return result1.returncode if result1 else 1


def run_specific_test(test_name):
    """Run a specific test or test category."""
    print(f"🎯 Running specific test: {test_name}")
    
    if test_name == "auth":
        test_file = "tests/test_auth_endpoints.py"
    elif test_name == "devices":
        test_file = "tests/test_device_endpoints.py"
    elif test_name == "ingestion":
        test_file = "tests/test_data_ingestion.py"
    elif test_name == "mqtt":
        test_file = "tests/test_mqtt_ingest.py"
    elif test_name == "integration":
        test_file = "tests/test_integration.py"
    elif test_name == "health":
        test_file = "tests/test_health.py"
    elif test_name == "customer":
        test_file = "tests/test_customer_api.py"
    else:
        print(f"❌ Unknown test category: {test_name}")
        print("Available categories: auth, devices, ingestion, mqtt, integration, health, customer")
        return 1
    
    result = run_command(
        f"python -m pytest {test_file} -v --tb=short",
        f"Running {test_name} tests"
    )
    
    return result.returncode if result else 1


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        test_category = sys.argv[1]
        return run_specific_test(test_category)
    else:
        return run_tests()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 