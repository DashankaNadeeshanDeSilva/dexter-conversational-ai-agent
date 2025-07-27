"""
README for Test Suite

# Dexter AI Agent Test Suite

This comprehensive test suite provides thorough testing coverage for the Dexter conversational AI agent project.

## Test Structure

### Core Test Files

1. **conftest.py** - Test configuration and fixtures
   - Centralized test setup and teardown
   - Mock factories for all major components
   - Shared fixtures across test files

2. **test_agent.py** - Agent core functionality tests
   - ReAct agent initialization and tool setup
   - Message processing and response generation
   - Error handling and edge cases
   - Semantic extraction and memory integration

3. **test_api.py** - API endpoint tests
   - FastAPI endpoint testing with full coverage
   - Chat functionality and conversation management
   - Memory query endpoints
   - Session lifecycle management
   - Error handling and validation

4. **test_memory_manager.py** - Memory orchestration tests
   - Memory manager coordination
   - Cross-memory-type operations
   - Fact extraction and storage
   - Memory retrieval and filtering

5. **test_memory_components.py** - Individual memory system tests
   - Short-term memory management
   - Episodic memory storage and retrieval
   - Semantic memory operations
   - Procedural memory tracking
   - Session management

6. **test_tools.py** - Tool implementation tests
   - Web search tool functionality
   - Product search capabilities
   - Appointment management system
   - Semantic retrieval operations
   - Tool error handling

7. **test_integration.py** - End-to-end integration tests
   - Complete conversation flows
   - Multi-user scenarios
   - Memory persistence across sessions
   - Error recovery mechanisms
   - System integration validation

8. **test_database_clients.py** - Database layer tests
   - MongoDB client operations (CRUD, conversations)
   - Pinecone client operations (vectors, similarity search)
   - Connection handling and error scenarios
   - Data validation and edge cases

9. **test_performance.py** - Performance and load tests
   - API response time benchmarks
   - Concurrent request handling
   - Memory operation performance
   - Load testing scenarios
   - Scalability metrics

10. **test_utils.py** - Test utilities and helpers
    - Test data generators
    - Mock factories
    - Assertion helpers
    - Performance measurement utilities
    - Test configuration management

11. **test_runner.py** - Test execution management
    - Comprehensive test runner
    - Test suite organization
    - Coverage reporting
    - Dependency checking
    - Test discovery and reporting

## Running Tests

### Quick Start
```bash
# Run all tests
python tests/test_runner.py

# Run specific test types
python tests/test_runner.py --type unit
python tests/test_runner.py --type integration
python tests/test_runner.py --type performance

# Run with verbose output
python tests/test_runner.py --verbose

# Run specific test file
python tests/test_runner.py --test test_agent.py

# Check test dependencies
python tests/test_runner.py --check-deps

# Show test summary
python tests/test_runner.py --summary
```

### Using pytest directly
```bash
# Run all tests with coverage
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing -v

# Run specific test file
pytest tests/test_agent.py -v

# Run specific test function
pytest tests/test_agent.py::TestReActAgent::test_process_message -v

# Run tests with specific markers
pytest tests/ -m "not slow" -v
```

## Test Categories

### Unit Tests
- **test_agent.py**: Core agent functionality
- **test_memory_manager.py**: Memory coordination
- **test_memory_components.py**: Individual memory systems
- **test_tools.py**: Tool implementations
- **test_database_clients.py**: Database operations

### Integration Tests
- **test_integration.py**: End-to-end workflows
- **test_api.py**: API endpoint integration

### Performance Tests
- **test_performance.py**: Load testing and benchmarks

## Key Features

### Comprehensive Mocking
- All external dependencies are properly mocked
- Database operations are isolated from real systems
- API calls are intercepted with realistic responses
- Async operations are properly handled

### Async Testing Support
- Full async/await pattern support
- Proper timeout handling
- Background task testing
- Concurrent operation validation

### Error Scenario Coverage
- Network failures and timeouts
- Database connection issues
- Invalid input validation
- Resource exhaustion scenarios
- Recovery mechanisms

### Performance Validation
- Response time benchmarks
- Throughput measurements
- Memory usage patterns
- Scalability testing
- Load handling validation

## Configuration

### Environment Variables
Tests automatically set up isolated test environments:
- `TESTING=true`
- `MONGODB_URL=mongodb://localhost:27017`
- `MONGODB_DATABASE=test_dexter`
- `PINECONE_API_KEY=test_api_key`
- `PINECONE_ENVIRONMENT=test-env`

### Test Data
- Realistic test data generators
- Various complexity levels (simple, medium, complex)
- Randomized data for edge case testing
- Consistent data patterns for reproducible tests

## Dependencies

### Required Packages
```
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-mock>=3.10.0
pytest-cov>=4.0.0
httpx>=0.24.0
fastapi>=0.100.0
motor>=3.0.0
pinecone-client>=2.0.0
```

### Installation
```bash
pip install -r requirements.txt
# or install test dependencies separately
pip install pytest pytest-asyncio pytest-mock pytest-cov httpx
```

## Coverage Goals

The test suite aims for:
- **90%+ code coverage** across all modules
- **100% API endpoint coverage**
- **All error paths tested**
- **Performance benchmarks established**
- **Integration scenarios validated**

## Best Practices

### Test Organization
- Tests are organized by functional area
- Each test file focuses on specific components
- Integration tests validate cross-component behavior
- Performance tests ensure scalability

### Test Isolation
- Each test is independent and can run in isolation
- Mocks prevent external dependencies
- Test data is generated fresh for each test
- Cleanup ensures no test pollution

### Maintainability
- Clear test naming conventions
- Comprehensive docstrings
- Modular test utilities
- Consistent assertion patterns

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running tests from the project root
2. **Async Warnings**: Update pytest-asyncio to latest version
3. **Coverage Issues**: Check that all source files are in the app/ directory
4. **Performance Test Failures**: Adjust timeout thresholds for your environment

### Debug Mode
```bash
# Run with debug output
pytest tests/ -v -s --tb=long

# Run single test with debug
pytest tests/test_agent.py::TestReActAgent::test_process_message -v -s --pdb
```

## Contributing

### Adding New Tests
1. Follow the existing naming conventions
2. Add appropriate fixtures to conftest.py
3. Include error scenario testing
4. Update this README if adding new test categories

### Test Guidelines
- Write descriptive test names
- Include both positive and negative test cases
- Test edge cases and boundary conditions
- Ensure proper async/await usage
- Add performance considerations for new features

## Continuous Integration

The test suite is designed to work with CI/CD pipelines:
- Exit codes properly indicate success/failure
- Coverage reports are generated in standard formats
- Tests can be run in parallel
- Environment setup is automated
- Detailed reporting is available

For more information about the Dexter AI Agent project, see the main README.md in the project root.
"""
