"""Test configuration and fixtures for Dexter AI Agent."""

import pytest
import os
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import Dict, Any, List
import uuid

# Set test environment variables
os.environ["ENVIRONMENT"] = "test"
os.environ["MONGODB_URI"] = "mongodb://localhost:27017/dexter_test"
os.environ["PINECONE_API_KEY"] = "test_key"
os.environ["PINECONE_ENVIRONMENT"] = "test_env"
os.environ["OPENAI_API_KEY"] = "test_openai_key"
os.environ["DEBUG"] = "true"
os.environ["ENABLE_METRICS"] = "false"

# Import only the classes we need for testing, NOT the actual app
from app.memory.memory_manager import MemoryManager
from app.agent.agent import ReActAgent, AgentState
from app.memory.mongodb_client import MongoDBClient
from app.db_clients.pinecone_client import PineconeClient
from app.memory.short_term_memory import ShortTermMemory
from app.memory.episodic_memory import EpisodicMemoryManager
from app.memory.procedural_memory import ProceduralMemoryManager
from app.memory.semantic_extractor import SemanticExtractor
from app.tools.web_search_tool import WebSearchTool
from app.tools.semantic_retrieval_tool import KnowledgeRetrievalTool
from app.tools.product_search_tool import ProductSearchTool
from app.tools.appointment_tool import AppointmentTool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_mongodb_client():
    """Create a mock MongoDB client."""
    mock = MagicMock(spec=MongoDBClient)
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
    mock.get_collection = MagicMock()
    return mock


@pytest.fixture
def mock_pinecone_client():
    """Create a mock Pinecone client."""
    mock = MagicMock(spec=PineconeClient)
    mock.store_memory = MagicMock(return_value="test_vector_id")
    mock.search_similar = MagicMock(return_value=[])
    mock.get_index = MagicMock()
    mock.store_knowledge = MagicMock(return_value="test_knowledge_id")
    mock.search_knowledge = MagicMock(return_value=[])
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
def mock_short_term_memory():
    """Create a mock short-term memory."""
    mock = MagicMock(spec=ShortTermMemory)
    mock.add_message = MagicMock()
    mock.get_messages = MagicMock(return_value=[])
    mock.clear = MagicMock()
    mock.session_id = "test_session_id"
    return mock


@pytest.fixture
def mock_episodic_memory():
    """Create a mock episodic memory manager."""
    mock = MagicMock(spec=EpisodicMemoryManager)
    mock.store_memory = MagicMock(return_value="test_episodic_id")
    mock.retrieve_memories = MagicMock(return_value=[])
    mock.search_memories = MagicMock(return_value=[])
    return mock


@pytest.fixture
def mock_procedural_memory():
    """Create a mock procedural memory manager."""
    mock = MagicMock(spec=ProceduralMemoryManager)
    mock.store_memory = MagicMock(return_value="test_procedural_id")
    mock.retrieve_memories = MagicMock(return_value=[])
    mock.search_memories = MagicMock(return_value=[])
    return mock


@pytest.fixture
def mock_semantic_extractor():
    """Create a mock semantic extractor."""
    mock = MagicMock(spec=SemanticExtractor)
    mock.extract_entities = MagicMock(return_value=["entity1", "entity2"])
    mock.extract_keywords = MagicMock(return_value=["keyword1", "keyword2"])
    mock.extract_summary = MagicMock(return_value="Test summary")
    return mock


@pytest.fixture
def mock_memory_manager(mock_mongodb_client, mock_pinecone_client, mock_short_term_memory, mock_semantic_extractor, mock_episodic_memory, mock_procedural_memory):
    """Create a mock memory manager."""
    mock = MagicMock(spec=MemoryManager)
    
    # Mock components
    mock.mongodb_client = mock_mongodb_client
    mock.pinecone_client = mock_pinecone_client
    mock.short_term_memories = {}
    mock.semantic_extractor = mock_semantic_extractor
    mock.episodic_memory = mock_episodic_memory
    mock.procedural_memory = mock_procedural_memory
    
    # Mock methods
    mock.get_short_term_memory = MagicMock(return_value=mock_short_term_memory)
    mock.add_message_to_short_term_memory = MagicMock()
    mock.get_short_term_memory_messages = MagicMock(return_value=[])
    mock.clear_short_term_memory = MagicMock()
    mock.store_episodic_memory = MagicMock(return_value="test_episodic_id")
    mock.store_procedural_memory = MagicMock(return_value="test_procedural_id")
    mock.create_conversation = MagicMock(return_value="test_conversation_id")
    mock.create_session = MagicMock(return_value="test_session_id")
    mock.get_conversation = MagicMock(return_value={
        "_id": "test_conversation_id",
        "user_id": "test_user",
        "messages": []
    })
    mock.add_message_to_conversation = MagicMock()
    
    return mock


@pytest.fixture
def mock_tools():
    """Create mock tools for testing."""
    tools = [
        MagicMock(spec=WebSearchTool, name="web_search", description="Search the web"),
        MagicMock(spec=KnowledgeRetrievalTool, name="knowledge_retrieval", description="Retrieve knowledge"),
        MagicMock(spec=ProductSearchTool, name="product_search", description="Search products"),
        MagicMock(spec=AppointmentTool, name="appointment", description="Book appointments")
    ]
    
    for tool in tools:
        tool.invoke = MagicMock(return_value="Tool result")
        tool.name = tool.name
        tool.description = tool.description
    
    return tools


@pytest.fixture
def mock_agent_state():
    """Create a mock agent state."""
    return AgentState(
        messages=[
            HumanMessage(content="Hello, how can you help me?"),
            AIMessage(content="I can help you with various tasks. What would you like to do?")
        ],
        user_id="test_user",
        conversation_id="test_conversation_id",
        session_id="test_session_id",
        tools=mock_tools(),
        tool_names=["web_search", "knowledge_retrieval", "product_search", "appointment"]
    )


@pytest.fixture
def mock_react_agent():
    """Create a mock ReAct agent."""
    mock = MagicMock(spec=ReActAgent)
    mock.memory_manager = mock_memory_manager()
    mock.tools = mock_tools()
    mock.process_message = AsyncMock(return_value="Test response")
    mock.workflow = MagicMock()
    return mock


@pytest.fixture
def test_app():
    """Create a test FastAPI app instance with mocked dependencies."""
    # Import here to avoid MongoDB connection during test setup
    from app.api.main import app
    
    # Mock the memory manager and agent in the app
    with patch('app.api.main.memory_manager') as mock_mm, \
         patch('app.api.main.agent') as mock_agent:
        
        # Set up mock memory manager
        mock_mm.create_conversation = MagicMock(return_value="test_conv_id")
        mock_mm.create_session = MagicMock(return_value="test_session_id")
        mock_mm.add_message_to_short_term_memory = MagicMock()
        mock_mm.store_episodic_memory = MagicMock(return_value="test_episodic_id")
        
        # Set up mock agent
        mock_agent.process_message = AsyncMock(return_value="Test response")
        
        yield app


@pytest.fixture
def test_client(test_app):
    """Create a test client for the FastAPI app."""
    from fastapi.testclient import TestClient
    return TestClient(test_app)


@pytest.fixture
def sample_chat_request():
    """Create a sample chat request for testing."""
    return {
        "user_id": "test_user",
        "message": "Hello, how can you help me?",
        "conversation_id": "test_conversation_id",
        "session_id": "test_session_id"
    }


@pytest.fixture
def sample_memory_query():
    """Create a sample memory query for testing."""
    return {
        "user_id": "test_user",
        "query": "What did we discuss about AI?",
        "memory_type": "episodic"
    }


@pytest.fixture
def mock_langchain_components():
    """Mock LangChain components."""
    with patch('langchain_openai.ChatOpenAI') as mock_llm, \
         patch('langgraph.graph.StateGraph') as mock_graph, \
         patch('langgraph.prebuilt.ToolNode') as mock_tool_node:
        
        mock_llm.return_value.bind_tools.return_value.invoke.return_value = AIMessage(content="Test response")
        mock_graph.return_value.add_node.return_value = mock_graph.return_value
        mock_graph.return_value.set_entry_point.return_value = mock_graph.return_value
        mock_graph.return_value.compile.return_value = MagicMock()
        mock_tool_node.return_value.invoke.return_value = {"messages": [ToolMessage(content="Tool result", name="test_tool")]}
        
        yield {
            "llm": mock_llm,
            "graph": mock_graph,
            "tool_node": mock_tool_node
        }