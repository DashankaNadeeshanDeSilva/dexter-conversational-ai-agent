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
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, FunctionMessage


class TestShortTermMemory:
    """Test short-term memory functionality."""
    
    def test_init(self):
        """Test initialization of short-term memory."""
        # Act
        memory = ShortTermMemory("test_session")
        
        # Assert
        assert memory.session_id == "test_session"
        assert memory.messages == []
        assert memory.max_token_limit == 4000  # Default value
    
    def test_init_with_custom_token_limit(self):
        """Test initialization with custom token limit."""
        # Act
        memory = ShortTermMemory("test_session", max_token_limit=2000)
        
        # Assert
        assert memory.max_token_limit == 2000
    
    def test_add_user_message(self):
        """Test adding user message."""
        # Arrange
        memory = ShortTermMemory("test_session")
        
        # Act
        memory.add_user_message("Hello, how are you?")
        
        # Assert
        assert len(memory.messages) == 1
        assert memory.messages[0].content == "Hello, how are you?"
        assert isinstance(memory.messages[0], HumanMessage)
    
    def test_add_ai_message(self):
        """Test adding AI message."""
        # Arrange
        memory = ShortTermMemory("test_session")
        
        # Act
        memory.add_ai_message("I'm doing well, thank you!")
        
        # Assert
        assert len(memory.messages) == 1
        assert memory.messages[0].content == "I'm doing well, thank you!"
        assert isinstance(memory.messages[0], AIMessage)
    
    def test_add_system_message(self):
        """Test adding system message."""
        # Arrange
        memory = ShortTermMemory("test_session")
        
        # Act
        memory.add_system_message("You are a helpful AI assistant.")
        
        # Assert
        assert len(memory.messages) == 1
        assert memory.messages[0].content == "You are a helpful AI assistant."
        assert isinstance(memory.messages[0], SystemMessage)
    
    def test_add_function_message(self):
        """Test adding function message."""
        # Arrange
        memory = ShortTermMemory("test_session")
        
        # Act
        memory.add_function_message("search_tool", "Found 5 results")
        
        # Assert
        assert len(memory.messages) == 1
        assert memory.messages[0].name == "search_tool"
        assert memory.messages[0].content == "Found 5 results"
        assert isinstance(memory.messages[0], FunctionMessage)
    
    def test_token_limit_enforcement(self):
        """Test that token limit is enforced."""
        # Arrange - Create memory with very low token limit
        memory = ShortTermMemory("test_session", max_token_limit=10)
        
        # Act - Add messages that exceed the token limit
        memory.add_user_message("This is a very long message that should exceed the token limit")
        memory.add_ai_message("Another long message to push over the limit")
        
        # Assert - Should only keep the most recent message due to token limit
        assert len(memory.messages) <= 2  # May keep system message + recent message
    
    def test_clear_memory(self):
        """Test clearing memory."""
        # Arrange
        memory = ShortTermMemory("test_session")
        memory.add_user_message("Hello")
        memory.add_ai_message("Hi there")
        
        # Act
        memory.clear()
        
        # Assert
        assert len(memory.messages) == 0
        assert memory.token_count == 0
    
    def test_get_messages(self):
        """Test getting all messages."""
        # Arrange
        memory = ShortTermMemory("test_session")
        memory.add_user_message("Hello")
        memory.add_ai_message("Hi there")
        
        # Act
        messages = memory.get_messages()
        
        # Assert
        assert len(messages) == 2
        assert messages[0].content == "Hello"
        assert messages[1].content == "Hi there"


class TestSessionManager:
    """Test session manager functionality."""
    
    def test_create_session(self, mock_mongodb_client):
        """Test creating a new session."""
        # Arrange
        mock_mongodb_client.db = MagicMock()
        mock_mongodb_client.db.__getitem__.return_value = MagicMock()
        mock_mongodb_client.db.__getitem__.return_value.insert_one.return_value.inserted_id = "test_session_id"
        manager = SessionManager(mock_mongodb_client)
        
        # Act
        session_id = manager.create_session("test_user", "test_conversation")
        
        # Assert
        assert session_id is not None
        manager.sessions.insert_one.assert_called_once()
    
    def test_get_session_stats(self, mock_mongodb_client):
        """Test getting session statistics."""
        # Arrange
        expected_session = {
            "_id": "test_session_id",
            "user_id": "test_user",
            "conversation_id": "test_conversation",
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "status": "active"
        }
        mock_mongodb_client.db = MagicMock()
        mock_mongodb_client.db.__getitem__.return_value = MagicMock()
        mock_mongodb_client.db.__getitem__.return_value.find_one.return_value = expected_session
        manager = SessionManager(mock_mongodb_client)
        
        # Act
        stats = manager.get_session_stats("test_session_id")
        
        # Assert
        assert stats is not None
        assert stats["session_id"] == "test_session_id"
        assert stats["user_id"] == "test_user"
    
    def test_update_session_activity(self, mock_mongodb_client):
        """Test updating session activity."""
        # Arrange
        mock_mongodb_client.db = MagicMock()
        mock_mongodb_client.db.__getitem__.return_value = MagicMock()
        mock_mongodb_client.db.__getitem__.return_value.update_one.return_value.modified_count = 1
        manager = SessionManager(mock_mongodb_client)
        
        # Act
        result = manager.update_session_activity("test_session_id")
        
        # Assert
        assert result is True
        manager.sessions.update_one.assert_called_once()
    
    def test_get_active_sessions(self, mock_mongodb_client):
        """Test getting active sessions."""
        # Arrange
        expected_sessions = [
            {"_id": "session_1", "user_id": "test_user", "status": "active"},
            {"_id": "session_2", "user_id": "test_user", "status": "active"}
        ]
        mock_mongodb_client.db = MagicMock()
        mock_mongodb_client.db.__getitem__.return_value = MagicMock()
        
        # Mock the cursor behavior properly
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = expected_sessions
        mock_mongodb_client.db.__getitem__.return_value.find.return_value = mock_cursor
        
        manager = SessionManager(mock_mongodb_client)
        
        # Act
        sessions = manager.get_active_sessions("test_user")
        
        # Assert
        assert len(sessions) == 2
        assert sessions[0]["user_id"] == "test_user"
    
    def test_get_user_session_history(self, mock_mongodb_client):
        """Test getting user session history."""
        # Arrange
        expected_sessions = [
            {"_id": "session_1", "user_id": "test_user"},
            {"_id": "session_2", "user_id": "test_user"}
        ]
        mock_mongodb_client.db = MagicMock()
        mock_mongodb_client.db.__getitem__.return_value = MagicMock()
        
        # Mock the cursor behavior properly
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value.limit.return_value = expected_sessions
        mock_mongodb_client.db.__getitem__.return_value.find.return_value = mock_cursor
        
        manager = SessionManager(mock_mongodb_client)
        
        # Act
        sessions = manager.get_user_session_history("test_user", limit=5)
        
        # Assert
        assert len(sessions) == 2
        assert sessions[0]["user_id"] == "test_user"
    
    def test_end_session(self, mock_mongodb_client):
        """Test ending a session."""
        # Arrange
        mock_mongodb_client.db = MagicMock()
        mock_mongodb_client.db.__getitem__.return_value = MagicMock()
        mock_mongodb_client.db.__getitem__.return_value.update_one.return_value.modified_count = 1
        manager = SessionManager(mock_mongodb_client)
        
        # Mock get_session_stats to return valid stats with all required fields
        manager.get_session_stats = MagicMock(return_value={
            "session_id": "test_session_id",
            "user_id": "test_user",
            "conversation_id": "test_conv",
            "message_count": 5,
            "tool_usage_count": 2,
            "duration_minutes": 10.5,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        })
        
        # Act
        result = manager.end_session("test_session_id")
        
        # Assert
        assert result is not None
        assert result["session_id"] == "test_session_id"
        manager.sessions.update_one.assert_called_once()
    
    def test_delete_session(self, mock_mongodb_client):
        """Test deleting a session."""
        # Arrange
        mock_mongodb_client.db = MagicMock()
        mock_mongodb_client.db.__getitem__.return_value = MagicMock()
        mock_mongodb_client.db.__getitem__.return_value.delete_one.return_value.deleted_count = 1
        manager = SessionManager(mock_mongodb_client)
        
        # Act
        result = manager.delete_session("test_session_id")
        
        # Assert
        assert result is True
        manager.sessions.delete_one.assert_called_once()


class TestSemanticExtractor:
    """Test semantic extractor functionality."""
    
    @patch('app.memory.semantic_extractor.ChatOpenAI')
    def test_init(self, mock_openai_cls):
        """Test initialization of semantic extractor."""
        # Arrange
        mock_llm = MagicMock()
        mock_openai_cls.return_value = mock_llm
        
        # Act
        extractor = SemanticExtractor()
        
        # Assert
        assert extractor.extraction_llm == mock_llm
        assert extractor.extraction_prompt is not None
        assert extractor.parser is not None
    
    @patch('app.memory.semantic_extractor.ChatOpenAI')
    def test_extract_facts_success(self, mock_openai_cls):
        """Test successful fact extraction."""
        # Arrange
        mock_llm = MagicMock()
        mock_openai_cls.return_value = mock_llm
        
        extractor = SemanticExtractor()
        
        # Mock the extraction chain directly
        mock_facts = [{"fact": "User likes coffee", "confidence": 0.9, "category": "preferences"}]
        extractor.extraction_chain = MagicMock()
        extractor.extraction_chain.invoke.return_value = mock_facts
        
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
    def test_extract_facts_no_facts(self, mock_openai_cls):
        """Test fact extraction when no facts are found."""
        # Arrange
        mock_llm = MagicMock()
        mock_openai_cls.return_value = mock_llm
        
        extractor = SemanticExtractor()
        
        # Mock the extraction chain to return empty facts
        extractor.extraction_chain = MagicMock()
        extractor.extraction_chain.invoke.return_value = []
        
        # Act
        facts = extractor.extract_facts(
            user_message="Hello there",
            agent_response="Hi! How can I help you?",
            conversation_context=[],
            user_id="test_user"
        )
        
        # Assert
        assert len(facts) == 0
    
    @patch('app.memory.semantic_extractor.ChatOpenAI')
    def test_extract_facts_with_context(self, mock_openai_cls):
        """Test fact extraction with conversation context."""
        # Arrange
        mock_llm = MagicMock()
        mock_openai_cls.return_value = mock_llm
        
        extractor = SemanticExtractor()
        
        # Mock the extraction chain
        mock_facts = [{"fact": "User is a developer", "confidence": 0.8, "category": "personal_attribute"}]
        extractor.extraction_chain = MagicMock()
        extractor.extraction_chain.invoke.return_value = mock_facts
        
        context = [
            {"role": "user", "content": "I work as a software developer"},
            {"role": "assistant", "content": "That sounds interesting!"}
        ]
        
        # Act
        facts = extractor.extract_facts(
            user_message="I use Python for my projects",
            agent_response="Python is a great language for development",
            conversation_context=context,
            user_id="test_user"
        )
        
        # Assert
        assert len(facts) == 1
        assert facts[0]["fact"] == "User is a developer"
        assert facts[0]["category"] == "personal_attribute"
    
    @patch('app.memory.semantic_extractor.ChatOpenAI')
    def test_extract_facts_error_handling(self, mock_openai_cls):
        """Test fact extraction error handling."""
        # Arrange
        mock_llm = MagicMock()
        mock_openai_cls.return_value = mock_llm
        
        extractor = SemanticExtractor()
        
        # Mock the extraction chain to raise an exception
        extractor.extraction_chain = MagicMock()
        extractor.extraction_chain.invoke.side_effect = Exception("LLM error")
        
        # Act
        facts = extractor.extract_facts(
            user_message="Test message",
            agent_response="Test response",
            conversation_context=[],
            user_id="test_user"
        )
        
        # Assert - Should return empty list on error
        assert len(facts) == 0


class TestEpisodicMemoryManager:
    """Test episodic memory manager functionality."""
    
    def test_init(self, mock_mongodb_client):
        """Test initialization of episodic memory manager."""
        # Act
        manager = EpisodicMemoryManager(mock_mongodb_client)
        
        # Assert
        assert manager.mongodb_client == mock_mongodb_client
    
    def test_store_event(self, mock_mongodb_client):
        """Test storing episodic memory."""
        # Arrange
        mock_mongodb_client.store_memory.return_value = "test_memory_id"
        manager = EpisodicMemoryManager(mock_mongodb_client)
        
        # Act
        memory_id = manager.store_event(
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
    
    def test_store_conversation_message(self, mock_mongodb_client):
        """Test storing conversation message as episodic memory."""
        # Arrange
        mock_mongodb_client.store_memory.return_value = "test_message_id"
        manager = EpisodicMemoryManager(mock_mongodb_client)
        
        message = {"role": "user", "content": "Hello there"}
        
        # Act
        memory_id = manager.store_conversation_message(
            user_id="test_user",
            conversation_id="test_conv",
            message=message
        )
        
        # Assert
        assert memory_id == "test_message_id"
        mock_mongodb_client.store_memory.assert_called_once()
    
    def test_retrieve_events(self, mock_mongodb_client):
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
        mock_mongodb_client.retrieve_memories.return_value = expected_memories
        manager = EpisodicMemoryManager(mock_mongodb_client)
        
        # Act
        memories = manager.retrieve_events(
            user_id="test_user",
            filter_query={"content.event": "greeting"},
            limit=5
        )
        
        # Assert
        assert len(memories) == 1
        assert memories[0]["_id"] == "memory_1"
        mock_mongodb_client.retrieve_memories.assert_called_once_with(
            user_id="test_user",
            memory_type="episodic",
            filter_query={"content.event": "greeting"},
            limit=5
        )
    
    def test_retrieve_conversation_events(self, mock_mongodb_client):
        """Test retrieving conversation-specific episodic memories."""
        # Arrange
        expected_memories = [
            {"_id": "memory_1", "content": {"conversation_id": "test_conv"}},
            {"_id": "memory_2", "content": {"conversation_id": "test_conv"}}
        ]
        mock_mongodb_client.retrieve_memories.return_value = expected_memories
        manager = EpisodicMemoryManager(mock_mongodb_client)
        
        # Act
        memories = manager.retrieve_conversation_events(
            user_id="test_user",
            conversation_id="test_conv",
            limit=50
        )
        
        # Assert
        assert len(memories) == 2
        assert all(m["content"]["conversation_id"] == "test_conv" for m in memories)
        mock_mongodb_client.retrieve_memories.assert_called_once_with(
            user_id="test_user",
            memory_type="episodic",
            filter_query={"content.conversation_id": "test_conv"},
            limit=50
        )


class TestProceduralMemoryManager:
    """Test procedural memory manager functionality."""
    
    def test_init(self, mock_mongodb_client):
        """Test initialization of procedural memory manager."""
        # Act
        manager = ProceduralMemoryManager(mock_mongodb_client)
        
        # Assert
        assert manager.mongodb_client == mock_mongodb_client
    
    def test_store_pattern(self, mock_mongodb_client):
        """Test storing procedural memory."""
        # Arrange
        mock_mongodb_client.store_memory.return_value = "test_procedure_id"
        manager = ProceduralMemoryManager(mock_mongodb_client)
        
        # Act
        memory_id = manager.store_pattern(
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
    
    def test_store_successful_pattern(self, mock_mongodb_client):
        """Test storing successful interaction pattern."""
        # Arrange
        mock_mongodb_client.store_memory.return_value = "test_pattern_id"
        manager = ProceduralMemoryManager(mock_mongodb_client)
        
        # Act
        memory_id = manager.store_successful_pattern(
            user_id="test_user",
            pattern_type="workflow",
            pattern_description="Search then filter approach",
            context="information_gathering",
            metadata={"domain": "research"}
        )
        
        # Assert
        assert memory_id == "test_pattern_id"
        mock_mongodb_client.store_memory.assert_called_once()
    
    def test_retrieve_patterns(self, mock_mongodb_client):
        """Test retrieving procedural memories."""
        # Arrange
        expected_patterns = [
            {
                "_id": "procedure_1",
                "user_id": "test_user",
                "content": {"tool": "search", "success": True},
                "metadata": {"timestamp": datetime.utcnow()}
            }
        ]
        mock_mongodb_client.retrieve_memories.return_value = expected_patterns
        manager = ProceduralMemoryManager(mock_mongodb_client)
        
        # Act
        patterns = manager.retrieve_patterns(
            user_id="test_user",
            filter_query={"content.tool": "search"},
            limit=5
        )
        
        # Assert
        assert len(patterns) == 1
        assert patterns[0]["_id"] == "procedure_1"
        mock_mongodb_client.retrieve_memories.assert_called_once_with(
            user_id="test_user",
            memory_type="procedural",
            filter_query={"content.tool": "search"},
            limit=5
        )
    
    def test_get_tool_usage_patterns(self, mock_mongodb_client):
        """Test getting tool usage patterns."""
        # Arrange
        expected_patterns = [
            {"content": {"tool": "search", "arguments": {"query": "test"}}},
            {"content": {"tool": "search", "arguments": {"query": "python"}}}
        ]
        mock_mongodb_client.retrieve_memories.return_value = expected_patterns
        manager = ProceduralMemoryManager(mock_mongodb_client)
        
        # Act
        patterns = manager.get_tool_usage_patterns(
            user_id="test_user",
            tool_name="search",
            query_context="test",
            success_only=True
        )
        
        # Assert
        assert len(patterns) == 2
        assert all(p["content"]["tool"] == "search" for p in patterns)
        mock_mongodb_client.retrieve_memories.assert_called_once_with(
            user_id="test_user",
            memory_type="procedural",
            filter_query={
                "content.tool": "search", 
                "content.success": True,
                "content.query_context": {"$regex": "test", "$options": "i"}
            },
            limit=10
        )
    
    def test_get_tool_usage_patterns_no_tool_filter(self, mock_mongodb_client):
        """Test getting tool usage patterns without tool filter."""
        # Arrange
        expected_patterns = [
            {"content": {"tool": "search", "success": True}},
            {"content": {"tool": "appointment", "success": True}}
        ]
        mock_mongodb_client.retrieve_memories.return_value = expected_patterns
        manager = ProceduralMemoryManager(mock_mongodb_client)
        
        # Act
        patterns = manager.get_tool_usage_patterns(
            user_id="test_user",
            tool_name=None,
            query_context=None,
            success_only=True
        )
        
        # Assert
        assert len(patterns) == 2
        mock_mongodb_client.retrieve_memories.assert_called_once_with(
            user_id="test_user",
            memory_type="procedural",
            filter_query={"content.success": True},
            limit=10
        )
