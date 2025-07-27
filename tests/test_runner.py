"""Test runner and test suite management utilities."""

import os
import sys
import subprocess
import pytest
from pathlib import Path
from typing import List, Optional, Dict, Any
import json


class TestRunner:
    """Comprehensive test runner for the Dexter AI Agent project."""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize test runner."""
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.tests_dir = self.project_root / "tests"
        
    def run_unit_tests(self, verbose: bool = True, coverage: bool = True) -> int:
        """Run unit tests."""
        cmd = ["python", "-m", "pytest"]
        
        # Add test files for unit testing
        unit_test_files = [
            "test_agent.py",
            "test_memory_manager.py",
            "test_memory_components.py",
            "test_tools.py",
            "test_database_clients.py"
        ]
        
        for test_file in unit_test_files:
            test_path = self.tests_dir / test_file
            if test_path.exists():
                cmd.append(str(test_path))
        
        # Add options
        if verbose:
            cmd.extend(["-v", "-s"])
        
        if coverage:
            cmd.extend([
                "--cov=app",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov"
            ])
        
        cmd.extend([
            "--tb=short",
            "--disable-warnings"
        ])
        
        print(f"Running unit tests: {' '.join(cmd)}")
        return subprocess.run(cmd, cwd=self.project_root).returncode
    
    def run_integration_tests(self, verbose: bool = True) -> int:
        """Run integration tests."""
        cmd = ["python", "-m", "pytest"]
        
        integration_test_files = [
            "test_integration.py",
            "test_api.py"
        ]
        
        for test_file in integration_test_files:
            test_path = self.tests_dir / test_file
            if test_path.exists():
                cmd.append(str(test_path))
        
        if verbose:
            cmd.extend(["-v", "-s"])
        
        cmd.extend([
            "--tb=short",
            "--disable-warnings"
        ])
        
        print(f"Running integration tests: {' '.join(cmd)}")
        return subprocess.run(cmd, cwd=self.project_root).returncode
    
    def run_performance_tests(self, verbose: bool = True) -> int:
        """Run performance tests."""
        cmd = ["python", "-m", "pytest"]
        
        performance_test_file = self.tests_dir / "test_performance.py"
        if performance_test_file.exists():
            cmd.append(str(performance_test_file))
        else:
            print("Performance test file not found")
            return 1
        
        if verbose:
            cmd.extend(["-v", "-s"])
        
        cmd.extend([
            "--tb=short",
            "--disable-warnings",
            "-m", "not slow"  # Skip slow tests unless explicitly requested
        ])
        
        print(f"Running performance tests: {' '.join(cmd)}")
        return subprocess.run(cmd, cwd=self.project_root).returncode
    
    def run_all_tests(self, verbose: bool = True, coverage: bool = True) -> Dict[str, int]:
        """Run all test suites."""
        results = {}
        
        print("=" * 60)
        print("RUNNING COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        
        # Run unit tests
        print("\n" + "=" * 40)
        print("UNIT TESTS")
        print("=" * 40)
        results['unit'] = self.run_unit_tests(verbose=verbose, coverage=coverage)
        
        # Run integration tests
        print("\n" + "=" * 40)
        print("INTEGRATION TESTS")
        print("=" * 40)
        results['integration'] = self.run_integration_tests(verbose=verbose)
        
        # Run performance tests
        print("\n" + "=" * 40)
        print("PERFORMANCE TESTS")
        print("=" * 40)
        results['performance'] = self.run_performance_tests(verbose=verbose)
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUITE SUMMARY")
        print("=" * 60)
        
        total_failures = 0
        for suite_name, return_code in results.items():
            status = "PASSED" if return_code == 0 else "FAILED"
            print(f"{suite_name.upper()} TESTS: {status}")
            if return_code != 0:
                total_failures += 1
        
        overall_status = "PASSED" if total_failures == 0 else "FAILED"
        print(f"\nOVERALL: {overall_status}")
        
        if coverage and results.get('unit', 1) == 0:
            print(f"\nCoverage report generated in: {self.project_root / 'htmlcov' / 'index.html'}")
        
        return results
    
    def run_specific_test(self, test_path: str, verbose: bool = True) -> int:
        """Run a specific test file or test function."""
        cmd = ["python", "-m", "pytest", test_path]
        
        if verbose:
            cmd.extend(["-v", "-s"])
        
        cmd.extend([
            "--tb=short",
            "--disable-warnings"
        ])
        
        print(f"Running specific test: {' '.join(cmd)}")
        return subprocess.run(cmd, cwd=self.project_root).returncode
    
    def check_test_dependencies(self) -> bool:
        """Check if all test dependencies are installed."""
        required_packages = [
            "pytest",
            "pytest-asyncio", 
            "pytest-mock",
            "pytest-cov",
            "httpx",
            "fastapi",
            "motor",
            "pinecone-client"
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print("Missing test dependencies:")
            for package in missing_packages:
                print(f"  - {package}")
            print("\nInstall missing dependencies with:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
        
        print("All test dependencies are installed.")
        return True
    
    def discover_tests(self) -> Dict[str, List[str]]:
        """Discover all available tests."""
        test_files = {}
        
        if not self.tests_dir.exists():
            return test_files
        
        for test_file in self.tests_dir.glob("test_*.py"):
            if test_file.name == "__init__.py":
                continue
                
            # Parse test file to find test functions
            try:
                with open(test_file, 'r') as f:
                    content = f.read()
                    
                test_functions = []
                for line in content.split('\n'):
                    stripped = line.strip()
                    if stripped.startswith('def test_') or stripped.startswith('async def test_'):
                        func_name = stripped.split('(')[0].replace('def ', '').replace('async ', '')
                        test_functions.append(func_name)
                
                test_files[test_file.name] = test_functions
                
            except Exception as e:
                print(f"Warning: Could not parse {test_file}: {e}")
                test_files[test_file.name] = []
        
        return test_files
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate a comprehensive test report."""
        discovered_tests = self.discover_tests()
        
        report = {
            "project_root": str(self.project_root),
            "tests_directory": str(self.tests_dir),
            "total_test_files": len(discovered_tests),
            "test_files": discovered_tests,
            "dependencies_ok": self.check_test_dependencies()
        }
        
        # Count total test functions
        total_functions = sum(len(functions) for functions in discovered_tests.values())
        report["total_test_functions"] = total_functions
        
        return report
    
    def print_test_summary(self):
        """Print a summary of available tests."""
        report = self.generate_test_report()
        
        print("=" * 60)
        print("DEXTER AI AGENT - TEST SUITE SUMMARY")
        print("=" * 60)
        print(f"Project Root: {report['project_root']}")
        print(f"Tests Directory: {report['tests_directory']}")
        print(f"Total Test Files: {report['total_test_files']}")
        print(f"Total Test Functions: {report['total_test_functions']}")
        print(f"Dependencies OK: {report['dependencies_ok']}")
        
        print("\nAvailable Test Files:")
        print("-" * 40)
        
        for test_file, functions in report['test_files'].items():
            print(f"\n{test_file} ({len(functions)} tests)")
            for func in functions[:5]:  # Show first 5 functions
                print(f"  - {func}")
            if len(functions) > 5:
                print(f"  ... and {len(functions) - 5} more")
        
        print("\n" + "=" * 60)


def main():
    """Main CLI entry point for test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dexter AI Agent Test Runner")
    parser.add_argument("--type", choices=["unit", "integration", "performance", "all"], 
                       default="all", help="Type of tests to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--no-coverage", action="store_true", help="Disable coverage reporting")
    parser.add_argument("--test", "-t", help="Run specific test file or function")
    parser.add_argument("--summary", "-s", action="store_true", help="Show test summary")
    parser.add_argument("--check-deps", action="store_true", help="Check test dependencies")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.summary:
        runner.print_test_summary()
        return 0
    
    if args.check_deps:
        return 0 if runner.check_test_dependencies() else 1
    
    if args.test:
        return runner.run_specific_test(args.test, verbose=args.verbose)
    
    coverage = not args.no_coverage
    
    if args.type == "unit":
        return runner.run_unit_tests(verbose=args.verbose, coverage=coverage)
    elif args.type == "integration":
        return runner.run_integration_tests(verbose=args.verbose)
    elif args.type == "performance":
        return runner.run_performance_tests(verbose=args.verbose)
    elif args.type == "all":
        results = runner.run_all_tests(verbose=args.verbose, coverage=coverage)
        return max(results.values())  # Return highest error code
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
