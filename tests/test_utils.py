"""Test utilities and helper functions for the test suite."""

import asyncio
import json
import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from unittest.mock import MagicMock, AsyncMock
import pytest

# Test data generators
class TestDataGenerator:
    """Generate test data for various test scenarios."""
    
    @staticmethod
    def generate_user_id(prefix: str = "test_user") -> str:
        """Generate a random user ID."""
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{prefix}_{suffix}"
    
    @staticmethod
    def generate_conversation_id(prefix: str = "conv") -> str:
        """Generate a random conversation ID."""
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        return f"{prefix}_{suffix}"
    
    @staticmethod
    def generate_session_id(prefix: str = "session") -> str:
        """Generate a random session ID."""
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        return f"{prefix}_{suffix}"
    
    @staticmethod
    def generate_message(complexity: str = "simple") -> str:
        """Generate test messages of varying complexity."""
        messages = {
            "simple": [
                "Hello",
                "How are you?",
                "What's the weather like?",
                "Tell me a joke",
                "What time is it?"
            ],
            "medium": [
                "Can you help me find information about machine learning?",
                "I need to schedule an appointment for next week",
                "What are the latest trends in artificial intelligence?",
                "Can you search for the best restaurants in New York?",
                "Explain quantum computing in simple terms"
            ],
            "complex": [
                "I'm working on a machine learning project that involves natural language processing and I need to understand the differences between transformer models and recurrent neural networks, specifically how attention mechanisms work and their computational complexity",
                "Can you help me plan a comprehensive marketing strategy for a tech startup that includes market research, competitor analysis, customer segmentation, and a detailed timeline with budget considerations?",
                "I need to understand the implications of quantum computing on current cryptographic systems and how organizations should prepare for the transition to quantum-resistant encryption methods",
                "Analyze the environmental impact of different renewable energy sources including solar, wind, hydro, and geothermal power, considering their lifecycle carbon footprint and scalability potential"
            ]
        }
        return random.choice(messages.get(complexity, messages["simple"]))
    
    @staticmethod
    def generate_memory_data(memory_type: str) -> Dict[str, Any]:
        """Generate test memory data."""
        base_data = {
            "user_id": TestDataGenerator.generate_user_id(),
            "conversation_id": TestDataGenerator.generate_conversation_id(),
            "timestamp": datetime.now().isoformat(),
            "content": {}
        }
        
        if memory_type == "episodic":
            base_data["content"] = {
                "user_input": TestDataGenerator.generate_message("medium"),
                "agent_response": "Test agent response",
                "context": {"session_id": TestDataGenerator.generate_session_id()},
                "emotions": {"sentiment": "neutral", "confidence": 0.8}
            }
        elif memory_type == "semantic":
            base_data["content"] = {
                "facts": [
                    "The user is interested in machine learning",
                    "The user prefers detailed explanations",
                    "The user is working on a tech project"
                ],
                "topics": ["machine learning", "technology", "programming"],
                "entities": ["Python", "TensorFlow", "AI"]
            }
        elif memory_type == "procedural":
            base_data["content"] = {
                "tool_name": "web_search",
                "parameters": {"query": "machine learning tutorials"},
                "outcome": "success",
                "performance_metrics": {"response_time": 1.2, "accuracy": 0.95}
            }
        
        return base_data
    
    @staticmethod
    def generate_search_results(count: int = 5) -> List[Dict[str, Any]]:
        """Generate mock search results."""
        results = []
        for i in range(count):
            results.append({
                "title": f"Test Result {i + 1}",
                "url": f"https://example.com/result_{i + 1}",
                "snippet": f"This is a test snippet for result {i + 1} containing relevant information.",
                "score": random.uniform(0.7, 0.95)
            })
        return results
    
    @staticmethod
    def generate_product_data(count: int = 3) -> List[Dict[str, Any]]:
        """Generate mock product data."""
        products = []
        categories = ["Electronics", "Books", "Clothing", "Home & Garden", "Sports"]
        
        for i in range(count):
            products.append({
                "id": f"prod_{i + 1}",
                "name": f"Test Product {i + 1}",
                "category": random.choice(categories),
                "price": round(random.uniform(10.99, 299.99), 2),
                "rating": round(random.uniform(3.5, 5.0), 1),
                "description": f"High-quality test product {i + 1} with excellent features.",
                "availability": random.choice(["in_stock", "limited", "out_of_stock"])
            })
        return products
    
    @staticmethod
    def generate_appointment_slots(days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Generate available appointment slots."""
        slots = []
        base_date = datetime.now().date()
        
        for day in range(1, days_ahead + 1):
            slot_date = base_date + timedelta(days=day)
            for hour in [9, 11, 14, 16]:
                slots.append({
                    "date": slot_date.isoformat(),
                    "time": f"{hour:02d}:00",
                    "duration": 60,
                    "available": random.choice([True, True, True, False])  # 75% available
                })
        return slots


class AsyncTestHelper:
    """Helper utilities for async testing."""
    
    @staticmethod
    async def run_with_timeout(coro, timeout: float = 5.0):
        """Run an async function with timeout."""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            pytest.fail(f"Operation timed out after {timeout} seconds")
    
    @staticmethod
    def create_async_mock(return_value=None, side_effect=None):
        """Create an async mock with proper configuration."""
        mock = AsyncMock()
        if return_value is not None:
            mock.return_value = return_value
        if side_effect is not None:
            mock.side_effect = side_effect
        return mock


class MockFactory:
    """Factory for creating various mocks used in tests."""
    
    @staticmethod
    def create_memory_manager_mock():
        """Create a comprehensive memory manager mock."""
        mock = MagicMock()
        
        # Short-term memory methods
        mock.store_short_term_memory = MagicMock()
        mock.get_short_term_memory = MagicMock(return_value=[])
        mock.clear_short_term_memory = MagicMock()
        
        # Session management
        mock.session_manager = MagicMock()
        mock.session_manager.create_session = MagicMock(return_value="test_session")
        mock.session_manager.get_session = MagicMock(return_value={"id": "test_session"})
        mock.session_manager.update_session = MagicMock()
        mock.session_manager.end_session = MagicMock()
        
        # Conversation management
        mock.create_conversation = MagicMock(return_value="test_conversation")
        mock.get_conversation = MagicMock(return_value={"id": "test_conversation"})
        mock.update_conversation = MagicMock()
        
        # Memory retrieval
        mock.retrieve_episodic_memories = MagicMock(return_value=[])
        mock.retrieve_semantic_memories = MagicMock(return_value=[])
        mock.retrieve_procedural_memories = MagicMock(return_value=[])
        
        # Memory storage
        mock.store_episodic_memory = MagicMock()
        mock.store_semantic_memory = MagicMock()
        mock.store_procedural_memory = MagicMock()
        
        # Fact extraction
        mock.extract_and_store_facts = MagicMock()
        
        return mock
    
    @staticmethod
    def create_agent_mock():
        """Create a comprehensive agent mock."""
        mock = MagicMock()
        
        # Basic agent methods
        mock.process_message = AsyncMock(return_value="Test response from agent")
        mock.initialize_tools = MagicMock()
        mock.get_available_tools = MagicMock(return_value=["web_search", "product_search"])
        
        # Memory integration
        mock.memory_manager = MockFactory.create_memory_manager_mock()
        
        # Tool execution
        mock.execute_tool = AsyncMock(return_value={"result": "Tool execution successful"})
        
        return mock
    
    @staticmethod
    def create_database_client_mock(client_type: str):
        """Create database client mocks."""
        mock = MagicMock()
        
        if client_type == "mongodb":
            mock.connect = AsyncMock()
            mock.disconnect = AsyncMock()
            mock.insert_document = AsyncMock(return_value="doc_id")
            mock.find_documents = AsyncMock(return_value=[])
            mock.update_document = AsyncMock(return_value=True)
            mock.delete_document = AsyncMock(return_value=True)
            mock.create_conversation = AsyncMock(return_value="conv_id")
            mock.get_conversation = AsyncMock(return_value=None)
            mock.update_conversation = AsyncMock(return_value=True)
            
        elif client_type == "pinecone":
            mock.connect = AsyncMock()
            mock.disconnect = AsyncMock()
            mock.upsert_vectors = AsyncMock()
            mock.query_similar = AsyncMock(return_value=[])
            mock.delete_vectors = AsyncMock()
            mock.get_index_stats = AsyncMock(return_value={"total_vectors": 0})
            
        return mock
    
    @staticmethod
    def create_tool_mock(tool_name: str):
        """Create tool-specific mocks."""
        mock = MagicMock()
        mock.name = tool_name
        
        if tool_name == "web_search":
            mock.search = AsyncMock(return_value=TestDataGenerator.generate_search_results())
            
        elif tool_name == "product_search":
            mock.search_products = AsyncMock(return_value=TestDataGenerator.generate_product_data())
            
        elif tool_name == "appointment_tool":
            mock.get_available_slots = AsyncMock(return_value=TestDataGenerator.generate_appointment_slots())
            mock.book_appointment = AsyncMock(return_value={"id": "appt_123", "status": "confirmed"})
            
        elif tool_name == "semantic_retrieval":
            mock.retrieve_similar = AsyncMock(return_value=[])
            
        return mock


class AssertionHelper:
    """Helper methods for common test assertions."""
    
    @staticmethod
    def assert_response_structure(response_data: Dict[str, Any], expected_keys: List[str]):
        """Assert that response has expected structure."""
        for key in expected_keys:
            assert key in response_data, f"Expected key '{key}' not found in response"
    
    @staticmethod
    def assert_memory_data_valid(memory_data: Dict[str, Any], memory_type: str):
        """Assert that memory data has valid structure."""
        required_keys = ["user_id", "conversation_id", "timestamp", "content"]
        AssertionHelper.assert_response_structure(memory_data, required_keys)
        
        # Type-specific validations
        if memory_type == "episodic":
            assert "user_input" in memory_data["content"]
            assert "agent_response" in memory_data["content"]
        elif memory_type == "semantic":
            assert "facts" in memory_data["content"] or "topics" in memory_data["content"]
        elif memory_type == "procedural":
            assert "tool_name" in memory_data["content"]
    
    @staticmethod
    def assert_api_error_response(response_data: Dict[str, Any]):
        """Assert that error response has proper structure."""
        required_keys = ["detail"]
        AssertionHelper.assert_response_structure(response_data, required_keys)
    
    @staticmethod
    def assert_chat_response_valid(response_data: Dict[str, Any]):
        """Assert that chat response has valid structure."""
        required_keys = ["response", "conversation_id", "session_id"]
        AssertionHelper.assert_response_structure(response_data, required_keys)
        
        assert isinstance(response_data["response"], str)
        assert len(response_data["response"]) > 0


class PerformanceTestHelper:
    """Helper utilities for performance testing."""
    
    @staticmethod
    def measure_execution_time(func, *args, **kwargs):
        """Measure execution time of a function."""
        import time
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        return result, execution_time
    
    @staticmethod
    async def measure_async_execution_time(coro):
        """Measure execution time of an async function."""
        import time
        start_time = time.time()
        result = await coro
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        return result, execution_time
    
    @staticmethod
    def calculate_performance_metrics(execution_times: List[float]) -> Dict[str, float]:
        """Calculate performance metrics from execution times."""
        import statistics
        
        if not execution_times:
            return {}
        
        return {
            "average": statistics.mean(execution_times),
            "median": statistics.median(execution_times),
            "min": min(execution_times),
            "max": max(execution_times),
            "std_dev": statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
            "p95": statistics.quantiles(execution_times, n=20)[18] if len(execution_times) >= 20 else max(execution_times)
        }


class TestConfigHelper:
    """Helper for test configuration and setup."""
    
    @staticmethod
    def get_test_config() -> Dict[str, Any]:
        """Get test configuration."""
        return {
            "mongodb": {
                "host": "localhost",
                "port": 27017,
                "database": "test_dexter",
                "collection": "test_conversations"
            },
            "pinecone": {
                "api_key": "test_api_key",
                "environment": "test-env",
                "index_name": "test-index"
            },
            "api": {
                "base_url": "http://localhost:8000",
                "timeout": 30
            },
            "performance": {
                "max_response_time": 5000,  # milliseconds
                "max_concurrent_requests": 50,
                "load_test_duration": 60  # seconds
            }
        }
    
    @staticmethod
    def setup_test_environment():
        """Setup test environment variables."""
        import os
        config = TestConfigHelper.get_test_config()
        
        # Set environment variables for testing
        os.environ["MONGODB_URL"] = f"mongodb://{config['mongodb']['host']}:{config['mongodb']['port']}"
        os.environ["MONGODB_DATABASE"] = config["mongodb"]["database"]
        os.environ["PINECONE_API_KEY"] = config["pinecone"]["api_key"]
        os.environ["PINECONE_ENVIRONMENT"] = config["pinecone"]["environment"]
        os.environ["PINECONE_INDEX_NAME"] = config["pinecone"]["index_name"]
        os.environ["TESTING"] = "true"
    
    @staticmethod
    def cleanup_test_environment():
        """Cleanup test environment."""
        import os
        test_env_vars = [
            "MONGODB_URL", "MONGODB_DATABASE", "PINECONE_API_KEY", 
            "PINECONE_ENVIRONMENT", "PINECONE_INDEX_NAME", "TESTING"
        ]
        
        for var in test_env_vars:
            if var in os.environ:
                del os.environ[var]


# Pytest fixtures that can be imported by other test files
@pytest.fixture
def test_data_generator():
    """Fixture providing test data generator."""
    return TestDataGenerator()


@pytest.fixture
def mock_factory():
    """Fixture providing mock factory."""
    return MockFactory()


@pytest.fixture
def assertion_helper():
    """Fixture providing assertion helper."""
    return AssertionHelper()


@pytest.fixture
def performance_helper():
    """Fixture providing performance test helper."""
    return PerformanceTestHelper()


@pytest.fixture(scope="session", autouse=True)
def setup_test_config():
    """Session-scoped fixture to setup test configuration."""
    TestConfigHelper.setup_test_environment()
    yield
    TestConfigHelper.cleanup_test_environment()


# Export all utilities for easy importing
__all__ = [
    'TestDataGenerator',
    'AsyncTestHelper', 
    'MockFactory',
    'AssertionHelper',
    'PerformanceTestHelper',
    'TestConfigHelper'
]
