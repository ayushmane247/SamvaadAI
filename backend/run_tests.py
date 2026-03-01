#!/usr/bin/env python
"""
Test runner script for SamvaadAI backend.
Runs all tests and provides summary.
"""

import sys
import subprocess

def run_tests():
    """Run all backend tests"""
    print("=" * 60)
    print("Running SamvaadAI Backend Tests")
    print("=" * 60)
    print()
    
    # Run pytest
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        cwd=".",
        capture_output=False
    )
    
    return result.returncode

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
