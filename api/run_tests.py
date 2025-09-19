#!/usr/bin/env python3
"""
Automated test runner for InstaBids API
Runs all test suites and generates comprehensive reports
"""

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def print_header(title):
    """Print formatted section header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def run_command(command, description):
    """Run a command and capture output"""
    print(f"\n[RUNNING] {description}")
    print(f"Command: {command}")
    print("-" * 40)

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print("[FAIL] Command timed out after 5 minutes")
        return False, "", "Timeout"
    except Exception as e:
        print(f"[FAIL] Error running command: {e}")
        return False, "", str(e)


def check_environment():
    """Check if test environment is properly configured"""
    print_header("Environment Check")

    # Check Python version
    python_version = sys.version
    print(f"Python Version: {python_version}")

    # Check required environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY"]
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"[OK] {var}: {value[:20]}...")
        else:
            print(f"[FAIL] {var}: Not set")

    # Check if pytest is installed
    try:
        import pytest

        print(f"[OK] pytest version: {pytest.__version__}")
    except ImportError:
        print("[FAIL] pytest not installed")
        return False

    # Check if required packages are available
    required_packages = ["fastapi", "supabase", "pydantic", "httpx"]
    for package in required_packages:
        try:
            __import__(package)
            print(f"[OK] {package}: Available")
        except ImportError:
            print(f"[FAIL] {package}: Not available")

    return True


def run_unit_tests():
    """Run unit tests"""
    print_header("Unit Tests")

    success, stdout, stderr = run_command(
        "python -m pytest tests/ -v --tb=short --durations=10", "Running unit tests"
    )

    return success


def run_integration_tests():
    """Run integration tests"""
    print_header("Integration Tests")

    success, stdout, stderr = run_command(
        "python -m pytest tests/test_integration_auth_flow.py -v --tb=short -m integration",
        "Running integration tests",
    )

    return success


def run_security_tests():
    """Run security tests"""
    print_header("Security Tests")

    success, stdout, stderr = run_command(
        "python -m pytest tests/ -v --tb=short -m security", "Running security tests"
    )

    return success


def run_performance_tests():
    """Run performance tests"""
    print_header("Performance Tests")

    success, stdout, stderr = run_command(
        "python -m pytest tests/ -v --tb=short -m slow", "Running performance tests"
    )

    return success


def run_coverage_report():
    """Generate coverage report"""
    print_header("Coverage Report")

    success, stdout, stderr = run_command(
        "python -m pytest tests/ --cov=. --cov-report=html --cov-report=term",
        "Generating coverage report",
    )

    if success:
        print("\n[INFO] Coverage report generated in htmlcov/index.html")

    return success


def run_comprehensive_test():
    """Run the comprehensive system test"""
    print_header("Comprehensive System Test")

    success, stdout, stderr = run_command(
        "python comprehensive_test.py", "Running comprehensive system verification"
    )

    return success


def generate_test_report(results):
    """Generate a comprehensive test report"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""
# InstaBids API Test Report
Generated: {timestamp}

## Test Results Summary
"""

    total_tests = len(results)
    passed_tests = sum(1 for success, _ in results.values() if success)

    report += f"""
- Total Test Suites: {total_tests}
- Passed: {passed_tests}
- Failed: {total_tests - passed_tests}
- Success Rate: {(passed_tests/total_tests)*100:.1f}%

## Individual Test Results
"""

    for test_name, (success, details) in results.items():
        status = "PASSED" if success else "FAILED"
        report += f"- {test_name}: {status}\n"

    report += f"""
## Recommendations
"""

    if passed_tests == total_tests:
        report += "[SUCCESS] All tests passed! The API is ready for deployment.\n"
    else:
        report += f"[WARNING] {total_tests - passed_tests} test suite(s) failed. Review the output above and fix issues before deployment.\n"

    # Write report to file
    with open("test_report.md", "w") as f:
        f.write(report)

    print(report)


def main():
    """Main test runner"""
    start_time = time.time()

    print_header("InstaBids API Automated Test Runner")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check environment
    if not check_environment():
        print(
            "[FAIL] Environment check failed. Please fix issues before running tests."
        )
        sys.exit(1)

    # Run all test suites
    results = {}

    # 1. Unit Tests
    results["Unit Tests"] = (run_unit_tests(), "Core functionality tests")

    # 2. Integration Tests
    results["Integration Tests"] = (run_integration_tests(), "End-to-end flow tests")

    # 3. Security Tests
    results["Security Tests"] = (run_security_tests(), "Security validation tests")

    # 4. Performance Tests
    results["Performance Tests"] = (
        run_performance_tests(),
        "Performance and load tests",
    )

    # 5. Coverage Report
    results["Coverage Report"] = (run_coverage_report(), "Code coverage analysis")

    # 6. Comprehensive Test
    results["Comprehensive System Test"] = (
        run_comprehensive_test(),
        "Full system verification",
    )

    # Generate final report
    end_time = time.time()
    duration = end_time - start_time

    print_header("Test Run Complete")
    print(f"Total Duration: {duration:.2f} seconds")

    generate_test_report(results)

    # Exit with appropriate code
    all_passed = all(success for success, _ in results.values())
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
