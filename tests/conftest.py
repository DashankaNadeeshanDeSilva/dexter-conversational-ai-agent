"""Test configuration and fixtures."""

import pytest
import os
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import Dict, Any, List
import uuid

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["MONGODB_URI"] = "mongodb://localhost:27017/dexter_test"
os.environ["PINECONE_API_KEY"] = "test_key"
os.environ["PINECONE_ENVIRONMENT"] = "test_env"
os.environ["OPENAI_API_KEY"] = "test_openai_key"

from app.memory.memory_manager import MemoryManager
from app.agent.agent import ReActAgent
from app.api.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_mongodb_client():
    """Create a mock MongoDB client."""
    mock = MagicMock()
    mock.store_memory = MagicMock(return_value="test_memory_id")
    mock.get_memories = MagicMock(return_value=[])
    mock.create_conversation = MagicMock(return_value="test_conversation_id")
    mock.get_conversation = MagicMock(return_value={
        "_id": "test_conversation_id",
        "user_id": "test_user",
        "messages": [],
        "created_at": datetime.utcnow()
    })
    mock.add_message_to_conversation = MagicMock()
    mock.get_user_conversations = MagicMock(return_value=[])
    mock.get_database = MagicMock()
    return mock


@pytest.fixture
def mock_pinecone_client():
    """Create a mock Pinecone client."""
    mock = MagicMock()
    mock.store_memory = MagicMock(return_value="test_vector_id")
    mock.search_similar = MagicMock(return_value=[])
    mock.get_index = MagicMock()
    return mock


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client."""
    mock = MagicMock()
    mock.chat.completions.create = MagicMock(return_value=MagicMock(
        choices=[MagicMock(message=MagicMock(content="Test response"))]
    ))
    return mock


@pytest.fixture
def mock_memory_manager():
    """Create a mock memory manager."""
    mock = MagicMock(spec=MemoryManager)
    
    # Mock session manager
    mock.session_manager = MagicMock()
    mock.session_manager.create_session = MagicMock(return_value="test_session_id")
    mock.session_manager.get_session = MagicMock(return_value={
        "session_id": "test_session_id",
        "user_id": "test_user",
        "conversation_id": "test_conversation_id",
        "created_at": datetime.utcnow()
    })
    
    # Mock short-term memory
    mock_short_term = MagicMock()
    mock_short_term.add_user_message = MagicMock()
    mock_short_term.add_ai_message = MagicMock()
    mock_short_term.get_messages = MagicMock(return_value=[])
    mock_short_term.clear = MagicMock()
    mock.get_short_term_memory = MagicMock(return_value=mock_short_term)
    
    # Mock memory operations
    mock.create_conversation = MagicMock(return_value="test_conversation_id")
    mock.get_conversation = MagicMock(return_value={
        "_id": "test_conversation_id",
        "user_id": "test_user",
        "messages": []
    })
    mock.add_message_to_conversation = MagicMock()
    mock.get_user_conversations = MagicMock(return_value=[])
    
    # Mock memory storage and retrieval
    mock.store_episodic_memory = MagicMock(return_value="test_episodic_id")
    mock.store_semantic_memory = MagicMock(return_value="test_semantic_id")
    mock.store_procedural_memory = MagicMock(return_value="test_procedural_id")
    
    mock.retrieve_episodic_memories = MagicMock(return_value=[])
    mock.retrieve_semantic_memories = MagicMock(return_value=[])
    mock.retrieve_procedural_memories = MagicMock(return_value=[])
    
    # Mock semantic extraction
    mock.extract_semantic_facts = MagicMock(return_value=[
        {
            "fact": "Test fact",
            "confidence": 0.9,
            "category": "general"
        }
    ])
    mock.store_extracted_semantic_facts = MagicMock()
    mock.store_successful_pattern = MagicMock()
    
    # Mock memory clearing
    mock.clear_short_term_memory = MagicMock()
    
    return mock


@pytest.fixture
def mock_tools():
    """Create mock tools."""
    tools = []
    
    # Web search tool mock
    web_search_tool = MagicMock()
    web_search_tool.name = "internet_search"
    web_search_tool.description = "Search the internet for information"
    web_search_tool._run = MagicMock(return_value="Test search results")
    tools.append(web_search_tool)
    
    # Product search tool mock
    product_search_tool = MagicMock()
    product_search_tool.name = "product_search"
    product_search_tool.description = "Search for products"
    product_search_tool._run = MagicMock(return_value="Test product results")
    tools.append(product_search_tool)
    
    # Appointment tool mock
    appointment_tool = MagicMock()
    appointment_tool.name = "appointment_tool"
    appointment_tool.description = "Manage appointments"
    appointment_tool._run = MagicMock(return_value="Appointment booked")
    tools.append(appointment_tool)
    
    # Semantic retrieval tool mock
    semantic_tool = MagicMock()
    semantic_tool.name = "semantic_retrieval"
    semantic_tool.description = "Retrieve semantic information"
    semantic_tool._run = MagicMock(return_value="Semantic results")
    tools.append(semantic_tool)
    
    return tools


@pytest.fixture
def mock_react_agent():
    """Create a mock ReAct agent."""
    mock = MagicMock(spec=ReActAgent)
    mock.process_message = AsyncMock(return_value="Test agent response")
    mock.reset_session = MagicMock()
    mock.tools = []
    mock.workflow = MagicMock()
    return mock


@pytest.fixture
def sample_conversation_data():
    """Sample conversation data for testing."""
    return {
        "conversation_id": "test_conversation_id",
        "user_id": "test_user",
        "session_id": "test_session_id",
        "messages": [
            {
                "role": "user",
                "content": "Hello, how are you?",
                "timestamp": datetime.utcnow()
            },
            {
                "role": "assistant", 
                "content": "I'm doing well, thank you for asking!",
                "timestamp": datetime.utcnow()
            }
        ],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


@pytest.fixture
def sample_memory_data():
    """Sample memory data for testing."""
    return {
        "episodic": [
            {
                "_id": "episodic_1",
                "user_id": "test_user",
                "memory_type": "episodic",
                "content": {
                    "event": "user_greeting",
                    "message": "Hello",
                    "response": "Hi there!"
                },
                "metadata": {
                    "conversation_id": "test_conversation_id",
                    "timestamp": datetime.utcnow()
                }
            }
        ],
        "semantic": [
            {
                "fact": "User likes coffee",
                "confidence": 0.95,
                "category": "preferences",
                "source": "conversation"
            }
        ],
        "procedural": [
            {
                "_id": "procedural_1",
                "user_id": "test_user",
                "memory_type": "procedural",
                "content": {
                    "tool": "product_search",
                    "arguments": {"query": "coffee"},
                    "success": True,
                    "pattern": "search_for_preferences"
                },
                "metadata": {
                    "conversation_id": "test_conversation_id",
                    "timestamp": datetime.utcnow()
                }
            }
        ]
    }


@pytest.fixture
def test_user_data():
    """Test user data."""
    return {
        "user_id": "test_user_123",
        "session_id": "test_session_456",
        "conversation_id": "test_conversation_789"
    }


@pytest.fixture
def mock_llm_response():
    """Mock LLM response."""
    mock_response = MagicMock()
    mock_response.content = "This is a test response from the LLM."
    mock_response.tool_calls = []
    return mock_response


@pytest.fixture
def mock_tool_executor():
    """Mock tool executor."""
    mock = MagicMock()
    mock.execute = MagicMock(return_value="Tool execution result")
    return mock


class TestHelpers:
    """Test helper functions."""
    
    @staticmethod
    def create_test_message(role: str = "user", content: str = "test message"):
        """Create a test message."""
        return {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow()
        }
    
    @staticmethod
    def create_test_memory(memory_type: str, user_id: str = "test_user"):
        """Create test memory data."""
        return {
            "_id": f"test_{memory_type}_id",
            "user_id": user_id,
            "memory_type": memory_type,
            "content": {"test": "data"},
            "metadata": {
                "timestamp": datetime.utcnow(),
                "source": "test"
            }
        }
    
    @staticmethod
    def assert_memory_stored(mock_storage, memory_type: str, user_id: str):
        """Assert that memory was stored correctly."""
        mock_storage.store_memory.assert_called()
        call_args = mock_storage.store_memory.call_args
        assert call_args[1]["memory_type"] == memory_type
        assert call_args[1]["user_id"] == user_id
    
    @staticmethod
    def create_mock_ai_message(content: str = "test response", tool_calls: List = None):
        """Create a mock AI message."""
        from langchain_core.messages import AIMessage
        message = MagicMock(spec=AIMessage)
        message.content = content
        message.tool_calls = tool_calls or []
        return message
    
    @staticmethod
    def create_mock_human_message(content: str = "test message"):
        """Create a mock human message."""
        from langchain_core.messages import HumanMessage
        message = MagicMock(spec=HumanMessage)
        message.content = content
        return message


# Patch decorators for commonly mocked modules
mongodb_patch = patch('app.memory.memory_manager.MongoDBClient')
pinecone_patch = patch('app.memory.memory_manager.PineconeClient')
openai_patch = patch('app.agent.agent.ChatOpenAI')
tools_patch = patch('app.agent.agent.SearchTool')
