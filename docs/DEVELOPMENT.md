# Development Guide

**Note that this documentation is created with partial help of GenAI tools.**

This comprehensive guide covers everything you need to know about developing with, extending, and contributing to Dexter.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Core Concepts](#core-concepts)
- [Adding Custom Tools](#adding-custom-tools)
- [Extending Memory Systems](#extending-memory-systems)
- [Testing](#testing)
- [Contributing](#contributing)
- [Best Practices](#best-practices)

## Development Setup

### Prerequisites

- **Python**: 3.11 or higher
- **Database**: MongoDB 5.0+ (local or hosted)
- **Vector Database**: Pinecone account
- **AI Service**: OpenAI API key
- **Development Tools**: Docker, Git

### Quick Start

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/dexter-conversational-ai-agent.git
   cd dexter-conversational-ai-agent
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Initialize Database**:
   ```bash
   python scripts/init_database.py
   ```

6. **Run Development Server**:
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```

### Development Environment Variables

```env
# Development Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Hot Reloading
RELOAD=true
WORKERS=1

# Development Databases
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=dexter_dev

# Testing
TEST_DATABASE=dexter_test
PYTEST_WORKERS=auto
```

## Project Structure

### Overview

```
dexter-conversational-ai-agent/
├── app/                          # Main application code
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── config.py                 # Configuration management
│   ├── agent/                    # Core agent logic
│   │   ├── __init__.py
│   │   └── agent.py              # ReAct agent implementation
│   ├── api/                      # REST API endpoints
│   │   ├── __init__.py
│   │   └── main.py               # API route definitions
│   ├── memory/                   # Memory system modules
│   │   ├── __init__.py
│   │   ├── memory_manager.py     # Central memory coordinator
│   │   ├── semantic_extractor.py # Fact extraction logic
│   │   ├── episodic_memory.py    # Event storage and retrieval
│   │   ├── procedural_memory.py  # Pattern learning system
│   │   ├── session_manager.py    # Session lifecycle management
│   │   ├── mongodb_client.py     # MongoDB connection handler
│   │   ├── pinecone_client.py    # Pinecone vector database client
│   │   └── short_term_memory.py  # Redis-based working memory
│   ├── tools/                    # Tool implementations
│   │   ├── __init__.py
│   │   ├── base_tool.py          # Base tool interface
│   │   ├── search_tool.py        # Product search functionality
│   │   ├── appointment_tool.py   # Appointment management
│   │   └── semantic_retrieval_tool.py # Memory querying
│   └── utils/                    # Utility modules
│       ├── __init__.py
│       ├── auth_utils.py         # Authentication helpers
│       └── logging_utils.py      # Logging configuration
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py              # pytest configuration
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── e2e/                     # End-to-end tests
├── docs/                        # Documentation
├── deployment/                  # Deployment configurations
├── scripts/                     # Utility scripts
└── monitoring/                  # Monitoring configurations
```

### Key Components Explained

#### `app/main.py`
The FastAPI application entry point that:
- Initializes the application
- Sets up middleware and error handlers
- Configures CORS and security
- Registers API routes

#### `app/config.py`
Centralized configuration management:
- Environment variable loading
- Database connection settings
- Memory system configuration
- Tool-specific settings

#### `app/agent/agent.py`
The core ReAct agent implementation:
- Intent analysis and reasoning
- Tool selection and execution
- Memory system coordination
- Response generation

#### Memory System Modules
Each memory type has its own module:
- **Session Manager**: User session lifecycle
- **Semantic Extractor**: Fact extraction from conversations
- **Episodic Memory**: Event storage and chronological retrieval
- **Procedural Memory**: Strategy pattern learning
- **Short-term Memory**: Real-time conversation context

## Core Concepts

### ReAct Agent Pattern

The ReAct (Reasoning + Acting) pattern is implemented through a structured flow:

```python
class ReActAgent:
    async def process_message(self, message: str, context: dict) -> str:
        # 1. Reasoning Phase
        intent = await self.analyze_intent(message)
        relevant_context = await self.gather_context(intent, context)
        plan = await self.create_action_plan(intent, relevant_context)
        
        # 2. Acting Phase
        results = []
        for action in plan.actions:
            tool = self.tool_router.get_tool(action.tool_name)
            result = await tool.execute(action.parameters)
            results.append(result)
            
            # Learn from action
            await self.memory_manager.learn_from_action(action, result)
        
        # 3. Response Generation
        response = await self.generate_response(results, context)
        await self.memory_manager.store_interaction(message, response)
        
        return response
```

### Memory Management

Memory systems work together to provide comprehensive context:

```python
class MemoryManager:
    def __init__(self):
        self.session_manager = SessionManager()
        self.semantic_memory = SemanticExtractor()
        self.episodic_memory = EpisodicMemory()
        self.procedural_memory = ProceduralMemory()
        self.short_term_memory = ShortTermMemory()
    
    async def get_full_context(self, user_id: str, query: str) -> Context:
        # Gather context from all memory systems
        session_context = await self.session_manager.get_context(user_id)
        semantic_facts = await self.semantic_memory.query(query, user_id)
        recent_events = await self.episodic_memory.get_recent_events(user_id)
        learned_patterns = await self.procedural_memory.get_patterns(query)
        working_memory = await self.short_term_memory.get_context(user_id)
        
        return Context.combine_all(
            session_context, semantic_facts, recent_events, 
            learned_patterns, working_memory
        )
```

### Tool Architecture

All tools inherit from a base class that provides consistent interfaces:

```python
from abc import ABC, abstractmethod

class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name for identification"""
        pass
    
    @property 
    @abstractmethod
    def description(self) -> str:
        """Tool description for selection"""
        pass
    
    @abstractmethod
    async def _run(self, query: str, **kwargs) -> str:
        """Tool execution logic"""
        pass
    
    async def execute(self, query: str, **kwargs) -> ToolResult:
        """Execute tool with error handling and logging"""
        try:
            start_time = time.time()
            result = await self._run(query, **kwargs)
            execution_time = time.time() - start_time
            
            return ToolResult(
                success=True,
                result=result,
                execution_time=execution_time,
                tool_name=self.name
            )
        except Exception as e:
            logger.error(f"Tool {self.name} failed: {str(e)}")
            return ToolResult(
                success=False,
                error=str(e),
                tool_name=self.name
            )
```

## Adding Custom Tools

### Step 1: Create Tool Class

Create a new file in `app/tools/`:

```python
# app/tools/weather_tool.py
from typing import Dict, Any
import aiohttp
from .base_tool import BaseTool

class WeatherTool(BaseTool):
    name = "weather_search"
    description = "Get current weather information for a location"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    async def _run(self, query: str, **kwargs) -> str:
        # Extract location from query
        location = self._extract_location(query)
        
        # Call weather API
        weather_data = await self._get_weather_data(location)
        
        # Format response
        return self._format_weather_response(weather_data)
    
    def _extract_location(self, query: str) -> str:
        """Extract location from natural language query"""
        # Implement location extraction logic
        # You could use spaCy NER or regex patterns
        pass
    
    async def _get_weather_data(self, location: str) -> Dict[str, Any]:
        """Fetch weather data from API"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/weather"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric"
            }
            async with session.get(url, params=params) as response:
                return await response.json()
    
    def _format_weather_response(self, data: Dict[str, Any]) -> str:
        """Format weather data into human-readable response"""
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]
        city = data["name"]
        
        return f"The weather in {city} is {description} with a temperature of {temp}°C."
```

### Step 2: Register Tool

Add your tool to the tool registry in `app/agent/agent.py`:

```python
# app/agent/agent.py
from app.tools.weather_tool import WeatherTool

class ReActAgent:
    def __init__(self):
        self.tools = {
            "product_search": ProductSearchTool(),
            "appointment_tool": AppointmentTool(),
            "semantic_retrieval": SemanticRetrievalTool(),
            "weather_search": WeatherTool(api_key=config.WEATHER_API_KEY),  # Add here
        }
```

### Step 3: Add Configuration

Update `app/config.py` to include tool-specific settings:

```python
# app/config.py
class Config:
    # Existing configuration...
    
    # Weather Tool Configuration
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    WEATHER_CACHE_TTL: int = int(os.getenv("WEATHER_CACHE_TTL", "1800"))  # 30 minutes
```

### Step 4: Add Tests

Create tests for your tool:

```python
# tests/unit/tools/test_weather_tool.py
import pytest
from unittest.mock import AsyncMock, patch
from app.tools.weather_tool import WeatherTool

@pytest.fixture
def weather_tool():
    return WeatherTool(api_key="test_key")

@pytest.mark.asyncio
async def test_weather_query_success(weather_tool):
    mock_response = {
        "main": {"temp": 22.5},
        "weather": [{"description": "sunny"}],
        "name": "San Francisco"
    }
    
    with patch.object(weather_tool, '_get_weather_data', return_value=mock_response):
        result = await weather_tool._run("What's the weather in San Francisco?")
        
    assert "San Francisco" in result
    assert "22.5°C" in result
    assert "sunny" in result

@pytest.mark.asyncio
async def test_location_extraction(weather_tool):
    location = weather_tool._extract_location("How's the weather in New York today?")
    assert location == "New York"
```

### Advanced Tool Features

#### Tool with Memory Integration

```python
class SmartWeatherTool(WeatherTool):
    def __init__(self, api_key: str, memory_manager):
        super().__init__(api_key)
        self.memory_manager = memory_manager
    
    async def _run(self, query: str, user_id: str = None, **kwargs) -> str:
        # Check user's location preferences from memory
        if user_id:
            location_facts = await self.memory_manager.semantic_memory.query(
                f"user location preferences", user_id
            )
            if location_facts and not self._has_explicit_location(query):
                # Use preferred location if none specified
                preferred_location = self._extract_preferred_location(location_facts)
                query = f"weather in {preferred_location}"
        
        result = await super()._run(query, **kwargs)
        
        # Store interaction for learning
        if user_id:
            await self.memory_manager.store_tool_usage(
                tool_name=self.name,
                query=query,
                result=result,
                user_id=user_id,
                success=True
            )
        
        return result
```

#### Tool with Procedural Learning

```python
class LearningTool(BaseTool):
    def __init__(self, procedural_memory):
        self.procedural_memory = procedural_memory
    
    async def execute(self, query: str, **kwargs) -> ToolResult:
        # Check for learned patterns
        patterns = await self.procedural_memory.get_patterns(
            tool_name=self.name,
            context=kwargs.get('context', {})
        )
        
        # Apply learned optimizations
        if patterns:
            optimized_params = self._apply_learned_patterns(patterns, kwargs)
            kwargs.update(optimized_params)
        
        # Execute tool
        result = await super().execute(query, **kwargs)
        
        # Learn from this execution
        if result.success:
            await self.procedural_memory.learn_pattern(
                tool_name=self.name,
                context=kwargs.get('context', {}),
                parameters=kwargs,
                success_metrics=result.execution_time
            )
        
        return result
```

## Extending Memory Systems

### Creating Custom Memory Modules

```python
# app/memory/custom_memory.py
from typing import List, Dict, Any
from .base_memory import BaseMemory

class CustomMemory(BaseMemory):
    """Custom memory implementation for specific use cases"""
    
    def __init__(self, storage_backend):
        self.storage = storage_backend
        self.cache = {}
    
    async def store(self, data: Dict[str, Any], user_id: str) -> str:
        """Store data in custom memory"""
        # Implement custom storage logic
        memory_id = await self.storage.insert(data)
        
        # Update cache
        cache_key = f"{user_id}:{memory_id}"
        self.cache[cache_key] = data
        
        return memory_id
    
    async def retrieve(self, query: str, user_id: str, **filters) -> List[Dict[str, Any]]:
        """Retrieve data from custom memory"""
        # Check cache first
        cached_results = self._check_cache(query, user_id)
        if cached_results:
            return cached_results
        
        # Query storage
        results = await self.storage.search(query, user_id, **filters)
        
        # Update cache
        self._update_cache(query, user_id, results)
        
        return results
    
    async def update(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing memory entry"""
        success = await self.storage.update(memory_id, updates)
        
        # Invalidate cache
        self._invalidate_cache(memory_id)
        
        return success
    
    def _check_cache(self, query: str, user_id: str) -> List[Dict[str, Any]]:
        """Check if query results are cached"""
        # Implement cache lookup logic
        pass
    
    def _update_cache(self, query: str, user_id: str, results: List[Dict[str, Any]]):
        """Update cache with query results"""
        # Implement cache update logic
        pass
    
    def _invalidate_cache(self, memory_id: str):
        """Invalidate cache entries related to memory_id"""
        # Implement cache invalidation logic
        pass
```

### Integrating Custom Memory

```python
# app/memory/memory_manager.py
from .custom_memory import CustomMemory

class MemoryManager:
    def __init__(self):
        # Existing memory systems...
        self.custom_memory = CustomMemory(storage_backend)
    
    async def store_custom_data(self, data: Dict[str, Any], user_id: str) -> str:
        """Store data in custom memory system"""
        return await self.custom_memory.store(data, user_id)
    
    async def query_custom_data(self, query: str, user_id: str, **filters) -> List[Dict[str, Any]]:
        """Query custom memory system"""
        return await self.custom_memory.retrieve(query, user_id, **filters)
```

## Testing

### Test Structure

```
tests/
├── conftest.py              # pytest configuration and fixtures
├── unit/                    # Unit tests
│   ├── test_agent.py
│   ├── memory/
│   │   ├── test_semantic_extractor.py
│   │   ├── test_episodic_memory.py
│   │   └── test_procedural_memory.py
│   └── tools/
│       ├── test_search_tool.py
│       └── test_appointment_tool.py
├── integration/             # Integration tests
│   ├── test_memory_integration.py
│   ├── test_agent_memory_flow.py
│   └── test_api_endpoints.py
└── e2e/                     # End-to-end tests
    ├── test_conversation_flow.py
    └── test_memory_persistence.py
```

### Test Fixtures

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock
from app.agent.agent import ReActAgent
from app.memory.memory_manager import MemoryManager

@pytest.fixture
def mock_memory_manager():
    """Mock memory manager for unit tests"""
    manager = AsyncMock(spec=MemoryManager)
    manager.store_interaction = AsyncMock(return_value="event_123")
    manager.get_context = AsyncMock(return_value={"facts": [], "events": []})
    return manager

@pytest.fixture
def test_agent(mock_memory_manager):
    """Test agent with mocked dependencies"""
    agent = ReActAgent()
    agent.memory_manager = mock_memory_manager
    return agent

@pytest.fixture
async def test_client():
    """Test client for API testing"""
    from fastapi.testclient import TestClient
    from app.main import app
    
    with TestClient(app) as client:
        yield client
```

### Writing Effective Tests

#### Unit Test Example

```python
# tests/unit/memory/test_semantic_extractor.py
import pytest
from app.memory.semantic_extractor import SemanticExtractor

@pytest.mark.asyncio
async def test_extract_facts_from_conversation():
    extractor = SemanticExtractor()
    
    conversation = "I prefer morning appointments. My doctor is Dr. Smith."
    facts = await extractor.extract_facts(conversation, user_id="user123")
    
    assert len(facts) == 2
    assert any("morning appointments" in fact.content for fact in facts)
    assert any("Dr. Smith" in fact.content for fact in facts)

@pytest.mark.asyncio
async def test_fact_confidence_scoring():
    extractor = SemanticExtractor()
    
    # Clear factual statement should have high confidence
    clear_fact = "My name is John"
    facts = await extractor.extract_facts(clear_fact, user_id="user123")
    assert facts[0].confidence > 0.9
    
    # Uncertain statement should have lower confidence
    uncertain_fact = "I think I might prefer morning appointments"
    facts = await extractor.extract_facts(uncertain_fact, user_id="user123")
    assert facts[0].confidence < 0.8
```

#### Integration Test Example

```python
# tests/integration/test_agent_memory_flow.py
import pytest
from app.agent.agent import ReActAgent
from app.memory.memory_manager import MemoryManager

@pytest.mark.asyncio
async def test_conversation_memory_integration():
    """Test that agent properly stores and retrieves conversation context"""
    memory_manager = MemoryManager()
    agent = ReActAgent(memory_manager=memory_manager)
    
    user_id = "test_user_123"
    
    # First interaction
    response1 = await agent.process_message(
        "I'm looking for a laptop for programming",
        {"user_id": user_id}
    )
    
    # Second interaction should remember the context
    response2 = await agent.process_message(
        "What about gaming laptops?",
        {"user_id": user_id}
    )
    
    # Verify memory was used
    context = await memory_manager.get_context(user_id, "laptop preferences")
    assert len(context["semantic_facts"]) > 0
    assert "programming" in str(context["semantic_facts"])
```

#### End-to-End Test Example

```python
# tests/e2e/test_conversation_flow.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_complete_conversation_flow():
    """Test a complete conversation from start to finish"""
    client = TestClient(app)
    
    # Start session
    session_response = client.post("/api/v1/sessions", json={
        "user_id": "e2e_test_user"
    })
    session_id = session_response.json()["data"]["session_id"]
    
    # First message
    chat_response1 = client.post("/api/v1/chat", json={
        "message": "Find me wireless headphones under $200",
        "user_id": "e2e_test_user",
        "session_id": session_id
    })
    
    assert chat_response1.status_code == 200
    response1_data = chat_response1.json()["data"]
    assert "headphones" in response1_data["response"].lower()
    assert "product_search" in response1_data["tools_used"]
    
    # Follow-up message
    chat_response2 = client.post("/api/v1/chat", json={
        "message": "What about noise-cancelling ones?",
        "user_id": "e2e_test_user", 
        "session_id": session_id
    })
    
    assert chat_response2.status_code == 200
    response2_data = chat_response2.json()["data"]
    assert "noise" in response2_data["response"].lower()
    
    # End session
    end_response = client.post(f"/api/v1/sessions/{session_id}/end")
    assert end_response.status_code == 200
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest tests/e2e/          # End-to-end tests only

# Run tests in parallel
pytest -n auto

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_agent.py

# Run specific test function
pytest tests/unit/test_agent.py::test_intent_analysis
```

## Contributing

### Development Workflow

1. **Fork the Repository**
2. **Create Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**:
   - Follow coding standards
   - Add tests for new functionality
   - Update documentation

4. **Test Your Changes**:
   ```bash
   pytest
   black app/ tests/          # Code formatting
   flake8 app/ tests/         # Linting
   mypy app/                  # Type checking
   ```

5. **Commit Changes**:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

6. **Push and Create PR**:
   ```bash
   git push origin feature/your-feature-name
   ```

### Code Standards

#### Python Style Guide

- Follow PEP 8
- Use Black for code formatting
- Use type hints for all functions
- Write comprehensive docstrings

```python
async def process_user_message(
    message: str, 
    user_id: str, 
    context: Optional[Dict[str, Any]] = None
) -> ProcessingResult:
    """Process a user message and generate intelligent response.
    
    Args:
        message: The user's input message
        user_id: Unique identifier for the user
        context: Optional additional context for processing
        
    Returns:
        ProcessingResult containing the response and metadata
        
    Raises:
        ProcessingError: If message processing fails
        ValidationError: If input parameters are invalid
    """
    # Implementation here
    pass
```

#### Commit Message Format

Use conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Maintenance tasks

Examples:
```
feat(tools): add weather search tool
fix(memory): resolve semantic extraction timeout
docs: update API documentation for new endpoints
test(agent): add comprehensive reasoning tests
```

## Best Practices

### Memory System Guidelines

1. **Semantic Facts**: Keep facts atomic and specific
2. **Episodic Events**: Include sufficient context for reconstruction
3. **Procedural Patterns**: Ensure patterns are generalizable
4. **Session Management**: Implement proper cleanup and TTL

### Tool Development

1. **Error Handling**: Always handle external API failures gracefully
2. **Parameter Validation**: Validate and sanitize all inputs
3. **Performance**: Implement caching for expensive operations
4. **Testing**: Write comprehensive tests including edge cases

### API Design

1. **Consistency**: Follow established patterns for all endpoints
2. **Validation**: Use Pydantic models for request/response validation
3. **Documentation**: Include comprehensive OpenAPI documentation
4. **Versioning**: Plan for API evolution and backward compatibility

### Performance Optimization

1. **Async Operations**: Use async/await for all I/O operations
2. **Connection Pooling**: Implement proper database connection management
3. **Caching**: Cache frequently accessed data appropriately
4. **Monitoring**: Add metrics for performance tracking

### Security Considerations

1. **Input Validation**: Sanitize all user inputs
2. **Authentication**: Implement proper API key management
3. **Rate Limiting**: Protect against abuse
4. **Data Privacy**: Handle user data according to privacy requirements

For more information, see:
- [Architecture Guide](ARCHITECTURE.md)
- [API Reference](API.md)
- [Deployment Guide](DEPLOYMENT.md)
