#!/usr/bin/env python3
"""
Comprehensive test runner for Dexter AI Agent.

This script provides multiple ways to run tests:
1. Run all tests
2. Run specific test categories
3. Run with coverage reporting
4. Run with performance profiling
5. Run with different output formats
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Optional


class TestRunner:
    """Test runner for the Dexter AI Agent project."""
    
    def __init__(self):
        """Initialize the test runner."""
        self.project_root = Path(__file__).parent.parent
        self.tests_dir = self.project_root / "tests"
        self.requirements_file = self.project_root / "requirements.txt"
        
        # Test categories and their corresponding files
        self.test_categories = {
            "unit": [
                "test_agent.py",
                "test_memory_manager.py",
                "test_tools.py",
                "test_utils.py"
            ],
            "api": [
                "test_api.py"
            ],
            "integration": [
                "test_integration.py"
            ],
            "performance": [
                "test_performance.py"
            ],
            "database": [
                "test_database_clients.py"
            ]
        }
    
    def check_dependencies(self) -> bool:
        """Check if required testing dependencies are installed."""
        required_packages = [
            "pytest",
            "pytest-asyncio",
            "pytest-cov",
            "pytest-mock"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing required packages: {', '.join(missing_packages)}")
            print("Install them with: pip install -r requirements.txt")
            return False
        
        print("✅ All required packages are installed")
        return True
    
    def run_command(self, command: List[str], capture_output: bool = False) -> subprocess.CompletedProcess:
        """Run a shell command."""
        print(f"Running: {' '.join(command)}")
        
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=capture_output,
                text=True,
                check=False
            )
            return result
        except Exception as e:
            print(f"❌ Error running command: {e}")
            sys.exit(1)
    
    def run_all_tests(self, verbose: bool = False, coverage: bool = False) -> bool:
        """Run all tests."""
        print("🚀 Running all tests...")
        
        command = ["python", "-m", "pytest"]
        
        if verbose:
            command.append("-v")
        
        if coverage:
            command.extend([
                "--cov=app",
                "--cov-report=html",
                "--cov-report=term-missing"
            ])
        
        # Add test discovery
        command.append("tests/")
        
        result = self.run_command(command)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            if coverage:
                print("📊 Coverage report generated in htmlcov/")
            return True
        else:
            print("❌ Some tests failed!")
            return False
    
    def run_category_tests(self, category: str, verbose: bool = False) -> bool:
        """Run tests for a specific category."""
        if category not in self.test_categories:
            print(f"❌ Unknown test category: {category}")
            print(f"Available categories: {', '.join(self.test_categories.keys())}")
            return False
        
        print(f"🧪 Running {category} tests...")
        
        command = ["python", "-m", "pytest"]
        
        if verbose:
            command.append("-v")
        
        # Add specific test files
        for test_file in self.test_categories[category]:
            test_path = self.tests_dir / test_file
            if test_path.exists():
                command.append(str(test_path))
        
        result = self.run_command(command)
        
        if result.returncode == 0:
            print(f"✅ {category} tests passed!")
            return True
        else:
            print(f"❌ {category} tests failed!")
            return False
    
    def run_specific_test(self, test_path: str, verbose: bool = False) -> bool:
        """Run a specific test file or test function."""
        print(f"🎯 Running specific test: {test_path}")
        
        command = ["python", "-m", "pytest"]
        
        if verbose:
            command.append("-v")
        
        command.append(test_path)
        
        result = self.run_command(command)
        
        if result.returncode == 0:
            print(f"✅ Test {test_path} passed!")
            return True
        else:
            print(f"❌ Test {test_path} failed!")
            return False
    
    def run_with_coverage(self, verbose: bool = False) -> bool:
        """Run tests with coverage reporting."""
        print("📊 Running tests with coverage...")
        
        command = [
            "python", "-m", "pytest",
            "--cov=app",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-report=xml",
            "--cov-fail-under=80"
        ]
        
        if verbose:
            command.append("-v")
        
        command.append("tests/")
        
        result = self.run_command(command)
        
        if result.returncode == 0:
            print("✅ Tests passed with coverage requirements!")
            print("📊 Coverage report generated in htmlcov/")
            print("📊 Coverage report generated in coverage.xml")
            return True
        else:
            print("❌ Tests failed or coverage requirements not met!")
            return False
    
    def run_performance_tests(self, verbose: bool = False) -> bool:
        """Run performance tests."""
        print("⚡ Running performance tests...")
        
        command = ["python", "-m", "pytest"]
        
        if verbose:
            command.append("-v")
        
        command.extend([
            "tests/test_performance.py",
            "-m", "performance"
        ])
        
        result = self.run_command(command)
        
        if result.returncode == 0:
            print("✅ Performance tests passed!")
            return True
        else:
            print("❌ Performance tests failed!")
            return False
    
    def run_parallel_tests(self, num_workers: int = 4, verbose: bool = False) -> bool:
        """Run tests in parallel."""
        print(f"🔄 Running tests in parallel with {num_workers} workers...")
        
        command = [
            "python", "-m", "pytest",
            "-n", str(num_workers),
            "--dist=loadfile"
        ]
        
        if verbose:
            command.append("-v")
        
        command.append("tests/")
        
        result = self.run_command(command)
        
        if result.returncode == 0:
            print("✅ Parallel tests passed!")
            return True
        else:
            print("❌ Parallel tests failed!")
            return False
    
    def generate_test_report(self, output_format: str = "html") -> bool:
        """Generate a test report."""
        print(f"📋 Generating test report in {output_format} format...")
        
        command = [
            "python", "-m", "pytest",
            "--cov=app",
            f"--cov-report={output_format}",
            "--junitxml=test-results.xml"
        ]
        
        command.append("tests/")
        
        result = self.run_command(command)
        
        if result.returncode == 0:
            print(f"✅ Test report generated in {output_format} format!")
            return True
        else:
            print(f"❌ Failed to generate test report!")
            return False
    
    def clean_test_artifacts(self) -> None:
        """Clean up test artifacts."""
        print("🧹 Cleaning up test artifacts...")
        
        artifacts = [
            ".pytest_cache",
            "htmlcov",
            "coverage.xml",
            "test-results.xml",
            "__pycache__"
        ]
        
        for artifact in artifacts:
            artifact_path = self.project_root / artifact
            if artifact_path.exists():
                if artifact_path.is_file():
                    artifact_path.unlink()
                else:
                    import shutil
                    shutil.rmtree(artifact_path)
                print(f"   Removed: {artifact}")
        
        print("✅ Test artifacts cleaned up!")
    
    def show_test_summary(self) -> None:
        """Show a summary of available tests."""
        print("\n📚 Test Summary")
        print("=" * 50)
        
        for category, files in self.test_categories.items():
            print(f"\n{category.upper()} Tests:")
            for file in files:
                file_path = self.tests_dir / file
                status = "✅" if file_path.exists() else "❌"
                print(f"  {status} {file}")
        
        print(f"\nTotal test files: {sum(len(files) for files in self.test_categories.values())}")
        print(f"Tests directory: {self.tests_dir}")


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="Dexter AI Agent Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python test_runner.py

  # Run specific category
  python test_runner.py --category unit

  # Run with coverage
  python test_runner.py --coverage

  # Run in parallel
  python test_runner.py --parallel --workers 8

  # Run specific test
  python test_runner.py --test tests/test_agent.py

  # Generate report
  python test_runner.py --report html
        """
    )
    
    parser.add_argument(
        "--category",
        choices=["unit", "api", "integration", "performance", "database"],
        help="Run tests for a specific category"
    )
    
    parser.add_argument(
        "--test",
        help="Run a specific test file or test function"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage reporting"
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers (default: 4)"
    )
    
    parser.add_argument(
        "--report",
        choices=["html", "xml", "term"],
        help="Generate test report in specified format"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean up test artifacts after running"
    )
    
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show test summary and exit"
    )
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = TestRunner()
    
    # Check dependencies
    if not runner.check_dependencies():
        sys.exit(1)
    
    # Show summary if requested
    if args.summary:
        runner.show_test_summary()
        return
    
    # Record start time
    start_time = time.time()
    
    try:
        success = False
        
        # Run tests based on arguments
        if args.test:
            success = runner.run_specific_test(args.test, args.verbose)
        elif args.category:
            success = runner.run_category_tests(args.category, args.verbose)
        elif args.coverage:
            success = runner.run_with_coverage(args.verbose)
        elif args.parallel:
            success = runner.run_parallel_tests(args.workers, args.verbose)
        elif args.report:
            success = runner.generate_test_report(args.report)
        else:
            # Default: run all tests
            success = runner.run_all_tests(args.verbose, args.coverage)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Show results
        print(f"\n⏱️  Total execution time: {execution_time:.2f} seconds")
        
        if success:
            print("🎉 All tests completed successfully!")
        else:
            print("💥 Some tests failed!")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⏹️  Test execution interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
    
    finally:
        # Clean up if requested
        if args.clean:
            runner.clean_test_artifacts()


if __name__ == "__main__":
    main()
