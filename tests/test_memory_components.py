"""Tests for memory system components."""

import pytest
from unittest.mock import MagicMock, patch, call
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.memory.short_term_memory import ShortTermMemory
from app.memory.session_manager import SessionManager
from app.memory.semantic_extractor import SemanticExtractor
from app.memory.episodic_memory import EpisodicMemoryManager
from app.memory.procedural_memory import ProceduralMemoryManager
from langchain_core.messages import HumanMessage, AIMessage


class TestShortTermMemory:
    """Tests for short-term memory."""
    
    def test_init(self):
        """Test initialization of short-term memory."""
        # Act
        memory = ShortTermMemory("test_session")
        
        # Assert
        assert memory.session_id == "test_session"
        assert memory.messages == []
        assert memory.max_messages == 50

    def test_add_user_message(self):
        """Test adding user message."""
        # Arrange
        memory = ShortTermMemory("test_session")
        
        # Act
        memory.add_user_message("Hello, how are you?")
        
        # Assert
        assert len(memory.messages) == 1
        assert isinstance(memory.messages[0], HumanMessage)
        assert memory.messages[0].content == "Hello, how are you?"

    def test_add_ai_message(self):
        """Test adding AI message."""
        # Arrange
        memory = ShortTermMemory("test_session")
        
        # Act
        memory.add_ai_message("I'm doing well, thank you!")
        
        # Assert
        assert len(memory.messages) == 1
        assert isinstance(memory.messages[0], AIMessage)
        assert memory.messages[0].content == "I'm doing well, thank you!"

    def test_get_messages(self):
        """Test getting all messages."""
        # Arrange
        memory = ShortTermMemory("test_session")
        memory.add_user_message("Hello")
        memory.add_ai_message("Hi there!")
        
        # Act
        messages = memory.get_messages()
        
        # Assert
        assert len(messages) == 2
        assert isinstance(messages[0], HumanMessage)
        assert isinstance(messages[1], AIMessage)

    def test_clear_messages(self):
        """Test clearing messages."""
        # Arrange
        memory = ShortTermMemory("test_session")
        memory.add_user_message("Hello")
        memory.add_ai_message("Hi there!")
        
        # Act
        memory.clear()
        
        # Assert
        assert len(memory.messages) == 0

    def test_max_messages_limit(self):
        """Test that messages are limited to max_messages."""
        # Arrange
        memory = ShortTermMemory("test_session", max_messages=3)
        
        # Act
        for i in range(5):
            memory.add_user_message(f"Message {i}")
        
        # Assert
        assert len(memory.messages) == 3
        assert memory.messages[0].content == "Message 2"  # Oldest messages removed
        assert memory.messages[-1].content == "Message 4"  # Newest message preserved

    def test_get_recent_messages(self):
        """Test getting recent messages."""
        # Arrange
        memory = ShortTermMemory("test_session")
        for i in range(10):
            memory.add_user_message(f"Message {i}")
        
        # Act
        recent = memory.get_recent_messages(3)
        
        # Assert
        assert len(recent) == 3
        assert recent[0].content == "Message 7"
        assert recent[-1].content == "Message 9"


class TestSessionManager:
    """Tests for session manager."""
    
    @pytest.fixture
    def mock_mongodb_client(self):
        """Mock MongoDB client."""
        mock = MagicMock()
        return mock

    def test_init(self, mock_mongodb_client):
        """Test initialization of session manager."""
        # Act
        manager = SessionManager(mock_mongodb_client)
        
        # Assert
        assert manager.mongodb_client == mock_mongodb_client

    def test_create_session(self, mock_mongodb_client):
        """Test creating a new session."""
        # Arrange
        mock_mongodb_client.get_database.return_value.sessions.insert_one.return_value.inserted_id = "test_session_id"
        manager = SessionManager(mock_mongodb_client)
        
        # Act
        session_id = manager.create_session("test_user", "test_conversation")
        
        # Assert
        assert session_id is not None
        mock_mongodb_client.get_database.return_value.sessions.insert_one.assert_called_once()

    def test_get_session(self, mock_mongodb_client):
        """Test getting an existing session."""
        # Arrange
        expected_session = {
            "_id": "test_session_id",
            "user_id": "test_user",
            "conversation_id": "test_conversation",
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        mock_mongodb_client.get_database.return_value.sessions.find_one.return_value = expected_session
        manager = SessionManager(mock_mongodb_client)
        
        # Act
        session = manager.get_session("test_session_id")
        
        # Assert
        assert session == expected_session
        mock_mongodb_client.get_database.return_value.sessions.find_one.assert_called_once_with(
            {"_id": "test_session_id"}
        )

    def test_update_session_activity(self, mock_mongodb_client):
        """Test updating session activity."""
        # Arrange
        manager = SessionManager(mock_mongodb_client)
        
        # Act
        manager.update_session_activity("test_session_id")
        
        # Assert
        mock_mongodb_client.get_database.return_value.sessions.update_one.assert_called_once()

    def test_get_user_sessions(self, mock_mongodb_client):
        """Test getting user sessions."""
        # Arrange
        expected_sessions = [
            {"_id": "session_1", "user_id": "test_user"},
            {"_id": "session_2", "user_id": "test_user"}
        ]
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value.sort.return_value = expected_sessions
        mock_mongodb_client.get_database.return_value.sessions.find.return_value = mock_cursor
        manager = SessionManager(mock_mongodb_client)
        
        # Act
        sessions = manager.get_user_sessions("test_user", limit=10)
        
        # Assert
        assert sessions == expected_sessions
        mock_mongodb_client.get_database.return_value.sessions.find.assert_called_once_with(
            {"user_id": "test_user"}
        )


class TestSemanticExtractor:
    """Tests for semantic extractor."""
    
    @patch('app.memory.semantic_extractor.ChatOpenAI')
    def test_init(self, mock_openai_cls):
        """Test initialization of semantic extractor."""
        # Arrange
        mock_llm = MagicMock()
        mock_openai_cls.return_value = mock_llm
        
        # Act
        extractor = SemanticExtractor()
        
        # Assert
        assert extractor.llm == mock_llm

    @patch('app.memory.semantic_extractor.ChatOpenAI')
    def test_extract_facts_success(self, mock_openai_cls):
        """Test successful fact extraction."""
        # Arrange
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = '{"facts": [{"fact": "User likes coffee", "confidence": 0.9, "category": "preferences"}]}'
        mock_llm.invoke.return_value = mock_response
        mock_openai_cls.return_value = mock_llm
        
        extractor = SemanticExtractor()
        
        # Act
        facts = extractor.extract_facts(
            user_message="I love drinking coffee in the morning",
            agent_response="I'll remember that you enjoy coffee",
            conversation_context=[],
            user_id="test_user"
        )
        
        # Assert
        assert len(facts) == 1
        assert facts[0]["fact"] == "User likes coffee"
        assert facts[0]["confidence"] == 0.9
        assert facts[0]["category"] == "preferences"

    @patch('app.memory.semantic_extractor.ChatOpenAI')
    def test_extract_facts_invalid_json(self, mock_openai_cls):
        """Test fact extraction with invalid JSON response."""
        # Arrange
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Invalid JSON response"
        mock_llm.invoke.return_value = mock_response
        mock_openai_cls.return_value = mock_llm
        
        extractor = SemanticExtractor()
        
        # Act
        facts = extractor.extract_facts(
            user_message="Test message",
            agent_response="Test response",
            conversation_context=[],
            user_id="test_user"
        )
        
        # Assert
        assert facts == []

    @patch('app.memory.semantic_extractor.ChatOpenAI')
    def test_extract_facts_llm_error(self, mock_openai_cls):
        """Test fact extraction with LLM error."""
        # Arrange
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("LLM error")
        mock_openai_cls.return_value = mock_llm
        
        extractor = SemanticExtractor()
        
        # Act
        facts = extractor.extract_facts(
            user_message="Test message",
            agent_response="Test response",
            conversation_context=[],
            user_id="test_user"
        )
        
        # Assert
        assert facts == []


class TestEpisodicMemoryManager:
    """Tests for episodic memory manager."""
    
    @pytest.fixture
    def mock_mongodb_client(self):
        """Mock MongoDB client."""
        mock = MagicMock()
        return mock

    def test_init(self, mock_mongodb_client):
        """Test initialization of episodic memory manager."""
        # Act
        manager = EpisodicMemoryManager(mock_mongodb_client)
        
        # Assert
        assert manager.mongodb_client == mock_mongodb_client

    def test_store_memory(self, mock_mongodb_client):
        """Test storing episodic memory."""
        # Arrange
        mock_mongodb_client.store_memory.return_value = "test_memory_id"
        manager = EpisodicMemoryManager(mock_mongodb_client)
        
        # Act
        memory_id = manager.store_memory(
            user_id="test_user",
            content={"event": "user_greeting", "message": "Hello"},
            metadata={"conversation_id": "test_conv"}
        )
        
        # Assert
        assert memory_id == "test_memory_id"
        mock_mongodb_client.store_memory.assert_called_once_with(
            user_id="test_user",
            memory_type="episodic",
            content={"event": "user_greeting", "message": "Hello"},
            metadata={"conversation_id": "test_conv"}
        )

    def test_get_memories(self, mock_mongodb_client):
        """Test retrieving episodic memories."""
        # Arrange
        expected_memories = [
            {
                "_id": "memory_1",
                "user_id": "test_user",
                "content": {"event": "greeting"},
                "metadata": {"timestamp": datetime.utcnow()}
            }
        ]
        mock_mongodb_client.get_memories.return_value = expected_memories
        manager = EpisodicMemoryManager(mock_mongodb_client)
        
        # Act
        memories = manager.get_memories(
            user_id="test_user",
            filter_query={"content.event": "greeting"},
            limit=5
        )
        
        # Assert
        assert memories == expected_memories
        mock_mongodb_client.get_memories.assert_called_once_with(
            user_id="test_user",
            memory_type="episodic",
            filter_query={"content.event": "greeting"},
            limit=5
        )

    def test_get_recent_memories(self, mock_mongodb_client):
        """Test getting recent episodic memories."""
        # Arrange
        expected_memories = [
            {"_id": "memory_1", "timestamp": datetime.utcnow()},
            {"_id": "memory_2", "timestamp": datetime.utcnow() - timedelta(hours=1)}
        ]
        mock_mongodb_client.get_memories.return_value = expected_memories
        manager = EpisodicMemoryManager(mock_mongodb_client)
        
        # Act
        memories = manager.get_recent_memories("test_user", hours=24, limit=10)
        
        # Assert
        assert memories == expected_memories
        mock_mongodb_client.get_memories.assert_called_once()


class TestProceduralMemoryManager:
    """Tests for procedural memory manager."""
    
    @pytest.fixture
    def mock_mongodb_client(self):
        """Mock MongoDB client."""
        mock = MagicMock()
        return mock

    def test_init(self, mock_mongodb_client):
        """Test initialization of procedural memory manager."""
        # Act
        manager = ProceduralMemoryManager(mock_mongodb_client)
        
        # Assert
        assert manager.mongodb_client == mock_mongodb_client

    def test_store_memory(self, mock_mongodb_client):
        """Test storing procedural memory."""
        # Arrange
        mock_mongodb_client.store_memory.return_value = "test_procedure_id"
        manager = ProceduralMemoryManager(mock_mongodb_client)
        
        # Act
        memory_id = manager.store_memory(
            user_id="test_user",
            content={"tool": "search", "pattern": "web_search", "success": True},
            metadata={"context": "user_query"}
        )
        
        # Assert
        assert memory_id == "test_procedure_id"
        mock_mongodb_client.store_memory.assert_called_once_with(
            user_id="test_user",
            memory_type="procedural",
            content={"tool": "search", "pattern": "web_search", "success": True},
            metadata={"context": "user_query"}
        )

    def test_get_memories(self, mock_mongodb_client):
        """Test retrieving procedural memories."""
        # Arrange
        expected_memories = [
            {
                "_id": "procedure_1",
                "user_id": "test_user",
                "content": {"tool": "search", "success": True},
                "metadata": {"timestamp": datetime.utcnow()}
            }
        ]
        mock_mongodb_client.get_memories.return_value = expected_memories
        manager = ProceduralMemoryManager(mock_mongodb_client)
        
        # Act
        memories = manager.get_memories(
            user_id="test_user",
            filter_query={"content.tool": "search"},
            limit=5
        )
        
        # Assert
        assert memories == expected_memories
        mock_mongodb_client.get_memories.assert_called_once_with(
            user_id="test_user",
            memory_type="procedural",
            filter_query={"content.tool": "search"},
            limit=5
        )

    def test_get_successful_patterns(self, mock_mongodb_client):
        """Test getting successful patterns."""
        # Arrange
        expected_patterns = [
            {"content": {"tool": "search", "success": True, "pattern": "web_search"}},
            {"content": {"tool": "appointment", "success": True, "pattern": "booking"}}
        ]
        mock_mongodb_client.get_memories.return_value = expected_patterns
        manager = ProceduralMemoryManager(mock_mongodb_client)
        
        # Act
        patterns = manager.get_successful_patterns("test_user", limit=10)
        
        # Assert
        assert patterns == expected_patterns
        mock_mongodb_client.get_memories.assert_called_once()
        # Verify the filter query includes success=True
        call_args = mock_mongodb_client.get_memories.call_args
        assert call_args[1]["filter_query"]["content.success"] is True

    def test_get_tool_usage_patterns(self, mock_mongodb_client):
        """Test getting tool usage patterns."""
        # Arrange
        expected_patterns = [
            {"content": {"tool": "search", "arguments": {"query": "test"}}},
            {"content": {"tool": "search", "arguments": {"query": "python"}}}
        ]
        mock_mongodb_client.get_memories.return_value = expected_patterns
        manager = ProceduralMemoryManager(mock_mongodb_client)
        
        # Act
        patterns = manager.get_tool_usage_patterns("test_user", "search", limit=5)
        
        # Assert
        assert patterns == expected_patterns
        mock_mongodb_client.get_memories.assert_called_once()
        # Verify the filter query includes the tool name
        call_args = mock_mongodb_client.get_memories.call_args
        assert call_args[1]["filter_query"]["content.tool"] == "search"
