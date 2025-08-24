# Dexter AI Agent - Test Suite

This directory contains the comprehensive test suite for the Dexter AI Agent project. The test suite covers unit tests, integration tests, API tests, and performance tests to ensure the reliability and quality of the AI agent system.

## 🏗️ Test Architecture

The test suite is organized into the following categories:

### Unit Tests
- **`test_agent.py`** - Tests for the ReAct agent implementation
- **`test_memory_manager.py`** - Tests for the memory management system
- **`test_tools.py`** - Tests for all AI agent tools
- **`test_utils.py`** - Tests for utility functions

### API Tests
- **`test_api.py`** - Tests for the FastAPI endpoints and models

### Integration Tests
- **`test_integration.py`** - End-to-end system integration tests

### Performance Tests
- **`test_performance.py`** - Performance and stress testing

### Database Tests
- **`test_database_clients.py`** - Tests for database clients and operations

## 🚀 Quick Start

### Prerequisites

Ensure you have the required testing dependencies installed:

```bash
pip install -r requirements.txt
```

The following packages are required for testing:
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking support
- `httpx` - HTTP client for testing
- `fastapi` - FastAPI testing support

### Running Tests

#### 1. Run All Tests
```bash
# From the project root
python -m pytest tests/

# Or use the test runner
python tests/test_runner.py
```

#### 2. Run Specific Test Categories
```bash
# Unit tests only
python tests/test_runner.py --category unit

# API tests only
python tests/test_runner.py --category api

# Integration tests only
python tests/test_runner.py --category integration
```

#### 3. Run with Coverage
```bash
# Run all tests with coverage reporting
python tests/test_runner.py --coverage

# Coverage will be generated in htmlcov/ directory
```

#### 4. Run Specific Tests
```bash
# Run a specific test file
python tests/test_runner.py --test tests/test_agent.py

# Run a specific test function
python tests/test_runner.py --test tests/test_agent.py::TestReActAgent::test_agent_initialization
```

#### 5. Run in Parallel
```bash
# Run tests in parallel with 8 workers
python tests/test_runner.py --parallel --workers 8
```

## 🧪 Test Configuration

### Test Fixtures (`conftest.py`)

The `conftest.py` file contains shared test fixtures and configuration:

- **Mock Dependencies** - MongoDB, Pinecone, OpenAI clients
- **Memory Components** - Short-term, episodic, procedural memory
- **Tools** - Web search, product search, appointment, knowledge retrieval
- **Agent Components** - ReAct agent, memory manager
- **API Components** - FastAPI app, test client

### Environment Variables

Tests use the following environment variables (automatically set in `conftest.py`):

```bash
ENVIRONMENT=test
MONGODB_URI=mongodb://localhost:27017/dexter_test
PINECONE_API_KEY=test_key
PINECONE_ENVIRONMENT=test_env
OPENAI_API_KEY=test_openai_key
DEBUG=true
ENABLE_METRICS=false
```

## 📊 Test Coverage

The test suite aims for comprehensive coverage of:

- **Agent Logic** - ReAct reasoning, tool selection, workflow execution
- **Memory System** - Episodic, semantic, procedural, and short-term memory
- **Tools** - Web search, product search, appointment booking, knowledge retrieval
- **API Endpoints** - Chat, conversations, memory queries, health checks
- **Database Operations** - MongoDB and Pinecone interactions
- **Error Handling** - Graceful degradation and error recovery

### Coverage Requirements

- **Minimum Coverage**: 80%
- **Critical Paths**: 95%+
- **Error Handling**: 90%+

## 🔧 Test Runner Features

The `test_runner.py` script provides advanced testing capabilities:

### Command Line Options

```bash
python tests/test_runner.py [OPTIONS]

Options:
  --category {unit,api,integration,performance,database}
                        Run tests for a specific category
  --test PATH           Run a specific test file or test function
  --coverage            Run tests with coverage reporting
  --parallel            Run tests in parallel
  --workers INTEGER     Number of parallel workers (default: 4)
  --report {html,xml,term}
                        Generate test report in specified format
  --verbose, -v         Verbose output
  --clean               Clean up test artifacts after running
  --summary             Show test summary and exit
```

### Examples

```bash
# Show test summary
python tests/test_runner.py --summary

# Run unit tests with verbose output
python tests/test_runner.py --category unit --verbose

# Run with coverage and generate HTML report
python tests/test_runner.py --coverage --report html

# Run in parallel and clean up artifacts
python tests/test_runner.py --parallel --workers 8 --clean
```

## 🧩 Test Structure

### Unit Tests

Unit tests focus on testing individual components in isolation:

```python
class TestReActAgent:
    """Test the ReActAgent class."""
    
    def test_agent_initialization(self):
        """Test ReActAgent initialization."""
        # Test setup
        # Test execution
        # Test assertions
```

### Integration Tests

Integration tests verify that components work together:

```python
class TestSystemIntegration:
    """Test the complete system integration."""
    
    async def test_complete_chat_workflow(self):
        """Test complete chat workflow from API to agent to memory."""
        # Test complete system workflow
        # Verify component interactions
        # Check end-to-end functionality
```

### API Tests

API tests verify HTTP endpoints and request/response handling:

```python
class TestAPIEndpoints:
    """Test the API endpoints."""
    
    def test_chat_endpoint_success(self):
        """Test successful chat endpoint."""
        # Test API request
        # Verify response format
        # Check business logic
```

## 🚨 Error Handling

Tests include comprehensive error handling scenarios:

- **Network Failures** - Database connection issues, API timeouts
- **Invalid Input** - Malformed requests, missing required fields
- **System Errors** - Memory allocation failures, tool execution errors
- **Graceful Degradation** - System behavior under error conditions

## 📈 Performance Testing

Performance tests measure:

- **Response Times** - API endpoint latency
- **Memory Usage** - Memory consumption patterns
- **Concurrent Users** - System behavior under load
- **Scalability** - Performance with increasing data volumes

## 🔍 Debugging Tests

### Verbose Output

```bash
# Enable verbose output
python tests/test_runner.py --verbose

# Or use pytest directly
python -m pytest tests/ -v -s
```

### Test Discovery

```bash
# List all available tests
python -m pytest tests/ --collect-only

# Show test collection with details
python -m pytest tests/ --collect-only -v
```

### Running Failed Tests

```bash
# Run only failed tests from last run
python -m pytest tests/ --lf

# Run failed tests with verbose output
python -m pytest tests/ --lf -v
```

## 🧹 Test Maintenance

### Adding New Tests

1. **Create Test File** - Follow naming convention `test_*.py`
2. **Import Dependencies** - Import modules and fixtures
3. **Write Test Classes** - Organize tests by functionality
4. **Add Test Methods** - Use descriptive method names
5. **Update Test Runner** - Add to appropriate category in `test_runner.py`

### Test Naming Conventions

- **Test Files**: `test_<module_name>.py`
- **Test Classes**: `Test<ClassName>`
- **Test Methods**: `test_<functionality_description>`

### Example Test Structure

```python
"""Tests for the <ModuleName> module."""

import pytest
from unittest.mock import MagicMock, patch

from app.module.module_name import ClassName


class TestClassName:
    """Test the ClassName class."""
    
    @pytest.fixture
    def mock_dependency(self):
        """Create a mock dependency."""
        return MagicMock()
    
    def test_method_name(self, mock_dependency):
        """Test the method_name method."""
        # Arrange
        instance = ClassName(mock_dependency)
        
        # Act
        result = instance.method_name("test_input")
        
        # Assert
        assert result == "expected_output"
        mock_dependency.some_method.assert_called_once_with("test_input")
```

## 📋 Test Reports

### Coverage Reports

Coverage reports are generated in multiple formats:

- **HTML**: `htmlcov/index.html` - Interactive web report
- **XML**: `coverage.xml` - CI/CD integration
- **Terminal**: Console output with missing lines

### JUnit Reports

JUnit XML reports for CI/CD integration:

```bash
python tests/test_runner.py --report xml
```

### Custom Reports

Generate custom reports using pytest plugins:

```bash
# Generate HTML report
python -m pytest tests/ --html=report.html

# Generate JSON report
python -m pytest tests/ --json-report
```

## 🔄 Continuous Integration

The test suite is designed for CI/CD integration:

### GitHub Actions

```yaml
- name: Run Tests
  run: |
    python -m pytest tests/ --cov=app --cov-report=xml --junitxml=test-results.xml
```

### GitLab CI

```yaml
test:
  script:
    - python -m pytest tests/ --cov=app --cov-report=xml
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors** - Ensure PYTHONPATH includes project root
2. **Missing Dependencies** - Install required packages from requirements.txt
3. **Database Connection** - Check MongoDB and Pinecone connection strings
4. **Async Test Issues** - Use `@pytest.mark.asyncio` for async tests

### Debug Mode

Enable debug mode for detailed error information:

```bash
# Set debug environment variable
export DEBUG=true

# Run tests with debug output
python tests/test_runner.py --verbose
```

### Test Isolation

Ensure tests don't interfere with each other:

```bash
# Run tests in isolation
python -m pytest tests/ --dist=no

# Clean up between tests
python tests/test_runner.py --clean
```

## 📚 Additional Resources

- **Pytest Documentation**: https://docs.pytest.org/
- **Pytest-asyncio**: https://pytest-asyncio.readthedocs.io/
- **Pytest-cov**: https://pytest-cov.readthedocs.io/
- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/

## 🤝 Contributing

When adding new tests:

1. **Follow Existing Patterns** - Use established test structure
2. **Add Comprehensive Coverage** - Test happy path and edge cases
3. **Update Documentation** - Document new test functionality
4. **Maintain Test Quality** - Ensure tests are reliable and fast

## 📞 Support

For test-related issues:

1. **Check Documentation** - Review this README and test files
2. **Review Error Messages** - Look for specific failure details
3. **Check Dependencies** - Ensure all required packages are installed
4. **Verify Configuration** - Check environment variables and test setup

---

**Happy Testing! 🧪✨**
