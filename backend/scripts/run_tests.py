#!/usr/bin/env python3
"""Script to run tests with various options."""

import subprocess
import sys
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n🔄 {description}")
    print(f"Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} - PASSED")
        if result.stdout:
            print(result.stdout)
        return True
    else:
        print(f"❌ {description} - FAILED")
        if result.stderr:
            print("STDERR:", result.stderr)
        if result.stdout:
            print("STDOUT:", result.stdout)
        return False


def main():
    parser = argparse.ArgumentParser(description="Run tests for Aura Journal backend")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests") 
    parser.add_argument("--service", choices=["entry-ingestor", "nlp-agent"], help="Run tests for specific service")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Change to backend directory
    backend_dir = Path(__file__).parent.parent
    
    # Base pytest command
    pytest_cmd = ["python", "-m", "pytest"]
    
    if args.verbose:
        pytest_cmd.append("-v")
    
    if args.coverage:
        pytest_cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
    
    # Determine test paths
    test_paths = []
    
    if args.service:
        if args.service == "entry-ingestor":
            test_paths.append("services/entry_ingestor/tests")
        elif args.service == "nlp-agent":
            test_paths.append("services/nlp_agent/tests")
    else:
        # Run all tests
        test_paths.extend([
            "tests",  # Shared tests
            "services/entry_ingestor/tests",
            "services/nlp_agent/tests"
        ])
    
    # Add marker filters
    if args.unit:
        pytest_cmd.extend(["-m", "unit"])
    elif args.integration:
        pytest_cmd.extend(["-m", "integration"])
    
    # Add test paths
    pytest_cmd.extend(test_paths)
    
    success = True
    
    # Run linting first
    print("🧹 Running code quality checks...")
    ruff_check = run_command(["python", "-m", "ruff", "check", "."], "Ruff linting")
    ruff_format = run_command(["python", "-m", "ruff", "format", "--check", "."], "Ruff formatting")
    
    if not (ruff_check and ruff_format):
        print("\n⚠️  Code quality issues found. Fix them with:")
        print("   python -m ruff check --fix .")
        print("   python -m ruff format .")
        success = False
    
    # Run tests
    test_success = run_command(pytest_cmd, "Running tests")
    
    if not test_success:
        success = False
    
    # Summary
    print("\n" + "="*50)
    if success:
        print("🎉 All checks passed!")
        sys.exit(0)
    else:
        print("💥 Some checks failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
