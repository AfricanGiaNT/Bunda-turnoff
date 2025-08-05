"""
Test runner entrypoint for the service station operations bot.

Runs all relevant tests and provides a unified interface for testing.
"""

import sys
import os
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

class TestRunner:
    """Manages test execution for the service station operations bot."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.tests_dir = self.project_root / "tests"
        self.unit_tests_dir = self.tests_dir / "unit"
        self.integration_tests_dir = self.tests_dir / "integration"
    
    def discover_tests(self) -> Dict[str, List[Path]]:
        """Discover all test files in the project."""
        tests = {
            'unit': [],
            'integration': []
        }
        
        # Find unit tests
        if self.unit_tests_dir.exists():
            tests['unit'] = list(self.unit_tests_dir.rglob("test_*.py"))
        
        # Find integration tests
        if self.integration_tests_dir.exists():
            tests['integration'] = list(self.integration_tests_dir.rglob("test_*.py"))
        
        return tests
    
    def run_unit_tests(self) -> bool:
        """Run all unit tests."""
        logger.info("Running unit tests...")
        
        unit_tests = self.discover_tests()['unit']
        if not unit_tests:
            logger.warning("No unit tests found")
            return True
        
        success = True
        for test_file in unit_tests:
            logger.info(f"Running unit test: {test_file}")
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", str(test_file), "-v"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    logger.info(f"✓ {test_file.name} passed")
                else:
                    logger.error(f"✗ {test_file.name} failed")
                    logger.error(result.stdout)
                    logger.error(result.stderr)
                    success = False
                    
            except Exception as e:
                logger.error(f"Error running {test_file}: {e}")
                success = False
        
        return success
    
    def run_integration_tests(self) -> bool:
        """Run all integration tests."""
        logger.info("Running integration tests...")
        
        integration_tests = self.discover_tests()['integration']
        if not integration_tests:
            logger.warning("No integration tests found")
            return True
        
        success = True
        for test_file in integration_tests:
            logger.info(f"Running integration test: {test_file}")
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", str(test_file), "-v"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    logger.info(f"✓ {test_file.name} passed")
                else:
                    logger.error(f"✗ {test_file.name} failed")
                    logger.error(result.stdout)
                    logger.error(result.stderr)
                    success = False
                    
            except Exception as e:
                logger.error(f"Error running {test_file}: {e}")
                success = False
        
        return success
    
    def run_all_tests(self) -> bool:
        """Run all tests (unit and integration)."""
        logger.info("Running all tests...")
        
        unit_success = self.run_unit_tests()
        integration_success = self.run_integration_tests()
        
        overall_success = unit_success and integration_success
        
        if overall_success:
            logger.info("✓ All tests passed")
        else:
            logger.error("✗ Some tests failed")
        
        return overall_success
    
    def run_specific_test(self, test_path: str) -> bool:
        """Run a specific test file or test function."""
        logger.info(f"Running specific test: {test_path}")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_path, "-v"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"✓ Test passed: {test_path}")
                return True
            else:
                logger.error(f"✗ Test failed: {test_path}")
                logger.error(result.stdout)
                logger.error(result.stderr)
                return False
                
        except Exception as e:
            logger.error(f"Error running test {test_path}: {e}")
            return False
    
    def run_tests_with_coverage(self) -> bool:
        """Run tests with coverage reporting."""
        logger.info("Running tests with coverage...")
        
        try:
            result = subprocess.run(
                [
                    sys.executable, "-m", "pytest",
                    "--cov=api",
                    "--cov=utils",
                    "--cov-report=term-missing",
                    "--cov-report=html:htmlcov"
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✓ Tests with coverage completed successfully")
                logger.info(result.stdout)
                return True
            else:
                logger.error("✗ Tests with coverage failed")
                logger.error(result.stdout)
                logger.error(result.stderr)
                return False
                
        except Exception as e:
            logger.error(f"Error running tests with coverage: {e}")
            return False
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get a summary of test status."""
        tests = self.discover_tests()
        
        return {
            'unit_test_count': len(tests['unit']),
            'integration_test_count': len(tests['integration']),
            'total_test_count': len(tests['unit']) + len(tests['integration']),
            'unit_tests': [str(t) for t in tests['unit']],
            'integration_tests': [str(t) for t in tests['integration']]
        }

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run tests for service station operations bot")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("--test", type=str, help="Run a specific test file or function")
    parser.add_argument("--summary", action="store_true", help="Show test summary")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.summary:
        summary = runner.get_test_summary()
        print(f"Test Summary:")
        print(f"  Unit tests: {summary['unit_test_count']}")
        print(f"  Integration tests: {summary['integration_test_count']}")
        print(f"  Total tests: {summary['total_test_count']}")
        
        if summary['unit_tests']:
            print(f"  Unit test files: {', '.join(summary['unit_tests'])}")
        if summary['integration_tests']:
            print(f"  Integration test files: {', '.join(summary['integration_tests'])}")
    
    elif args.test:
        success = runner.run_specific_test(args.test)
        sys.exit(0 if success else 1)
    
    elif args.coverage:
        success = runner.run_tests_with_coverage()
        sys.exit(0 if success else 1)
    
    elif args.unit:
        success = runner.run_unit_tests()
        sys.exit(0 if success else 1)
    
    elif args.integration:
        success = runner.run_integration_tests()
        sys.exit(0 if success else 1)
    
    else:
        # Run all tests by default
        success = runner.run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 