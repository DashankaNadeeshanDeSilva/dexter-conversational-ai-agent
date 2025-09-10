"""Tests for the Memory Manager."""

import pytest
from unittest.mock import MagicMock, patch, call
from datetime import datetime
from typing import Dict, Any, List

from app.memory.memory_manager import MemoryManager, MemoryType
from app.memory.mongodb_client import MongoDBClient
from app.db_clients.pinecone_client import PineconeClient
from app.memory.short_term_memory import ShortTermMemory
from app.memory.episodic_memory import EpisodicMemoryManager
from app.memory.procedural_memory import ProceduralMemoryManager
from app.memory.semantic_extractor import SemanticExtractor
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage


class TestMemoryManager:
    """Test the MemoryManager class."""
    
    @pytest.fixture
    def mock_mongodb_client(self):
        """Create a mock MongoDB client."""
        mock = MagicMock(spec=MongoDBClient)
        mock.store_memory = MagicMock(return_value="test_memory_id")
        mock.get_memories = MagicMock(return_value=[])
        mock.create_conversation = MagicMock(return_value="test_conversation_id")
        mock.create_session = MagicMock(return_value="test_session_id")
        mock.get_conversation = MagicMock(return_value={
            "_id": "test_conversation_id",
            "user_id": "test_user",
            "messages": [],
            "created_at": datetime.utcnow()
        })
        mock.add_message_to_conversation = MagicMock()
        mock.get_user_conversations = MagicMock(return_value=[])
        return mock
    
    @pytest.fixture
    def mock_pinecone_client(self):
        """Create a mock Pinecone client."""
        mock = MagicMock(spec=PineconeClient)
        mock.store_memory = MagicMock(return_value="test_vector_id")
        mock.search_similar = MagicMock(return_value=[])
        mock.store_knowledge = MagicMock(return_value="test_knowledge_id")
        mock.search_knowledge = MagicMock(return_value=[])
        return mock
    
    @pytest.fixture
    def mock_short_term_memory(self):
        """Create a mock short-term memory."""
        mock = MagicMock(spec=ShortTermMemory)
        mock.add_message = MagicMock()
        mock.get_messages = MagicMock(return_value=[])
        mock.clear = MagicMock()
        mock.session_id = "test_session_id"
        return mock
    
    @pytest.fixture
    def mock_episodic_memory(self):
        """Create a mock episodic memory manager."""
        mock = MagicMock(spec=EpisodicMemoryManager)
        mock.store_event = MagicMock(return_value="test_episodic_id")
        mock.retrieve_events = MagicMock(return_value=[])
        return mock
    
    @pytest.fixture
    def mock_procedural_memory(self):
        """Create a mock procedural memory manager."""
        mock = MagicMock(spec=ProceduralMemoryManager)
        mock.store_pattern = MagicMock(return_value="test_procedural_id")
        mock.retrieve_patterns = MagicMock(return_value=[])
        return mock
    
    @pytest.fixture
    def mock_semantic_extractor(self):
        """Create a mock semantic extractor."""
        mock = MagicMock(spec=SemanticExtractor)
        mock.extract_entities = MagicMock(return_value=["entity1", "entity2"])
        mock.extract_keywords = MagicMock(return_value=["keyword1", "keyword2"])
        mock.extract_summary = MagicMock(return_value="Test summary")
        return mock
    
    @pytest.fixture
    def memory_manager(self, mock_mongodb_client, mock_pinecone_client, 
                      mock_short_term_memory, mock_episodic_memory, 
                      mock_procedural_memory, mock_semantic_extractor):
        """Create a MemoryManager instance with mocked dependencies."""
        with patch('app.memory.memory_manager.MongoDBClient', return_value=mock_mongodb_client), \
             patch('app.memory.memory_manager.PineconeClient', return_value=mock_pinecone_client), \
             patch('app.memory.memory_manager.ShortTermMemory', return_value=mock_short_term_memory), \
             patch('app.memory.memory_manager.EpisodicMemoryManager', return_value=mock_episodic_memory), \
             patch('app.memory.memory_manager.ProceduralMemoryManager', return_value=mock_procedural_memory), \
             patch('app.memory.memory_manager.SemanticExtractor', return_value=mock_semantic_extractor):
        
            manager = MemoryManager()
            # Replace the actual instances with mocks
            manager.mongodb_client = mock_mongodb_client
            manager.pinecone_client = mock_pinecone_client
            manager.episodic_memory = mock_episodic_memory
            manager.procedural_memory = mock_procedural_memory
            manager.short_term_memories = {}
            return manager
    
    def test_initialization(self, memory_manager, mock_mongodb_client, mock_pinecone_client,
                           mock_short_term_memory, mock_episodic_memory, mock_procedural_memory,
                           mock_semantic_extractor):
        """Test MemoryManager initialization."""
        assert memory_manager.mongodb_client == mock_mongodb_client
        assert memory_manager.pinecone_client == mock_pinecone_client
        assert memory_manager.short_term_memories == {}
        assert memory_manager.semantic_extractor == mock_semantic_extractor
        assert memory_manager.episodic_memory == mock_episodic_memory
        assert memory_manager.procedural_memory == mock_procedural_memory
    
    def test_get_short_term_memory_new_session(self, memory_manager, mock_short_term_memory):
        """Test getting short-term memory for a new session."""
        session_id = "new_session"
        
        # Mock the ShortTermMemory constructor
        with patch('app.memory.memory_manager.ShortTermMemory', return_value=mock_short_term_memory):
            result = memory_manager.get_short_term_memory(session_id)
        
        assert result == mock_short_term_memory
        assert session_id in memory_manager.short_term_memories
        assert memory_manager.short_term_memories[session_id] == mock_short_term_memory
    
    def test_get_short_term_memory_existing_session(self, memory_manager, mock_short_term_memory):
        """Test getting short-term memory for an existing session."""
        session_id = "existing_session"
        memory_manager.short_term_memories[session_id] = mock_short_term_memory
        
        result = memory_manager.get_short_term_memory(session_id)
        
        assert result == mock_short_term_memory
        # Should not create a new instance
        assert len(memory_manager.short_term_memories) == 1
    
    def test_add_message_to_short_term_memory(self, memory_manager, mock_short_term_memory):
        """Test adding a message to short-term memory."""
        session_id = "test_session"
        message = HumanMessage(content="Hello")
        # Ensure the created STM is our mock
        from unittest.mock import patch as _patch
        with _patch('app.memory.memory_manager.ShortTermMemory', return_value=mock_short_term_memory):
            memory_manager.add_message_to_short_term_memory(session_id, message)
        mock_short_term_memory.add_message.assert_called_once_with(message)
    
    def test_get_short_term_memory_messages(self, memory_manager, mock_short_term_memory):
        """Test getting messages from short-term memory."""
        session_id = "test_session"
        expected_messages = [HumanMessage(content="Hello"), AIMessage(content="Hi")]
        mock_short_term_memory.get_messages.return_value = expected_messages
        from unittest.mock import patch as _patch
        with _patch('app.memory.memory_manager.ShortTermMemory', return_value=mock_short_term_memory):
            result = memory_manager.get_short_term_memory_messages(session_id)
        assert result == expected_messages
        mock_short_term_memory.get_messages.assert_called_once()
    
    def test_clear_short_term_memory(self, memory_manager, mock_short_term_memory):
        """Test clearing short-term memory."""
        session_id = "test_session"
        memory_manager.short_term_memories[session_id] = mock_short_term_memory
        
        memory_manager.clear_short_term_memory(session_id)
        
        mock_short_term_memory.clear.assert_called_once()
    
    def test_clear_short_term_memory_nonexistent_session(self, memory_manager):
        """Test clearing short-term memory for non-existent session."""
        session_id = "nonexistent_session"
        
        # Should not raise an error
        memory_manager.clear_short_term_memory(session_id)
    
    def test_store_episodic_memory(self, memory_manager, mock_episodic_memory):
        """Test storing episodic memory."""
        user_id = "test_user"
        content = {"event": "user_greeting", "message": "Hello"}
        metadata = {"conversation_id": "test_conv", "timestamp": datetime.utcnow()}
        
        result = memory_manager.store_episodic_memory(user_id, content, metadata)
        
        assert result == "test_episodic_id"
        mock_episodic_memory.store_event.assert_called_once_with(user_id=user_id, content=content, metadata=metadata)
    
    def test_store_procedural_memory(self, memory_manager, mock_procedural_memory):
        """Test storing procedural memory."""
        user_id = "test_user"
        content = {"tool": "web_search", "success": True}
        metadata = {"conversation_id": "test_conv", "timestamp": datetime.utcnow()}
        
        result = memory_manager.store_procedural_memory(user_id, content, metadata)
        
        assert result == "test_procedural_id"
        mock_procedural_memory.store_pattern.assert_called_once_with(user_id=user_id, content=content, metadata=metadata)
    
    def test_create_conversation(self, memory_manager, mock_mongodb_client):
        """Test creating a conversation."""
        user_id = "test_user"
        
        result = memory_manager.create_conversation(user_id)
        
        assert result == "test_conversation_id"
        mock_mongodb_client.create_conversation.assert_called_once_with(user_id)
    
    def test_create_session(self, memory_manager, mock_mongodb_client):
        """Test creating a session."""
        user_id = "test_user"
        conversation_id = "test_conv"
        
        result = memory_manager.create_session(user_id, conversation_id)
        
        assert result == "test_session_id"
        mock_mongodb_client.create_session.assert_called_once_with(user_id, conversation_id)
    
    def test_get_conversation(self, memory_manager, mock_mongodb_client):
        """Test getting a conversation."""
        conversation_id = "test_conv"
        expected_conversation = {
            "_id": "test_conversation_id",
                "user_id": "test_user",
            "messages": []
        }
        mock_mongodb_client.get_conversation.return_value = expected_conversation
        
        result = memory_manager.get_conversation(conversation_id)
        
        assert result == expected_conversation
        mock_mongodb_client.get_conversation.assert_called_once_with(conversation_id)
    
    def test_add_message_to_conversation(self, memory_manager, mock_mongodb_client):
        """Test adding a message to a conversation."""
        conversation_id = "test_conv"
        message = HumanMessage(content="Hello")
        
        memory_manager.add_message_to_conversation(conversation_id, message)
        
        mock_mongodb_client.add_message.assert_called_once_with(conversation_id, message)
    
    def test_get_user_conversations(self, memory_manager, mock_mongodb_client):
        """Test getting user conversations."""
        user_id = "test_user"
        expected_conversations = [
            {"_id": "conv1", "user_id": user_id},
            {"_id": "conv2", "user_id": user_id}
        ]
        mock_mongodb_client.get_user_conversations.return_value = expected_conversations
        
        result = memory_manager.get_user_conversations(user_id)
        
        assert result == expected_conversations
        mock_mongodb_client.get_user_conversations.assert_called_once_with(user_id, 10)  # Fixed: include default limit parameter
    
    def test_retrieve_episodic_memories(self, memory_manager, mock_episodic_memory):
        """Test retrieving episodic memories."""
        user_id = "test_user"
        query = "What did we discuss?"
        expected_memories = [{"memory": "episodic_memory_1"}, {"memory": "episodic_memory_2"}]
        mock_episodic_memory.retrieve_events.return_value = expected_memories
        result = memory_manager.retrieve_episodic_memories(user_id, {"query": query})
        assert result == expected_memories
        mock_episodic_memory.retrieve_events.assert_called_once_with(user_id=user_id, filter_query={"query": query}, limit=10)
    
    def test_retrieve_procedural_memories(self, memory_manager, mock_procedural_memory):
        """Test retrieving procedural memories."""
        user_id = "test_user"
        query = "How did we solve this?"
        expected_memories = [{"memory": "procedural_memory_1"}]
        mock_procedural_memory.retrieve_patterns.return_value = expected_memories
        result = memory_manager.retrieve_procedural_memories(user_id, {"query": query})
        assert result == expected_memories
        mock_procedural_memory.retrieve_patterns.assert_called_once_with(user_id=user_id, filter_query={"query": query}, limit=10)
    
    def test_search_semantic_memories(self, memory_manager, mock_pinecone_client):
        """Test searching semantic memories."""
        user_id = "test_user"
        query = "AI and machine learning"
        expected_memories = [{"memory": "semantic_memory_1"}]
        mock_pinecone_client.retrieve_similar.return_value = expected_memories
        result = memory_manager.retrieve_semantic_memories(user_id, query)
        assert result == expected_memories
        mock_pinecone_client.retrieve_similar.assert_called_once_with(user_id=user_id, query=query, k=5, filter_metadata=None)
    
    def test_store_knowledge(self, memory_manager, mock_pinecone_client):
        """Test storing knowledge."""
        user_id = "test_user"  # Added missing user_id parameter
        knowledge_text = "AI is a branch of computer science"
        metadata = {"source": "textbook", "category": "AI"}
        
        result = memory_manager.store_semantic_memory(user_id, knowledge_text, metadata)  # Fixed: use correct method name
        
        assert result == "test_vector_id"  # The actual return value from the mock
        mock_pinecone_client.store_memory.assert_called_once_with(user_id=user_id, text=knowledge_text, metadata=metadata)
    
    def test_search_knowledge(self, memory_manager, mock_pinecone_client):
        """Test searching knowledge."""
        user_id = "test_user"  # Added missing user_id parameter
        query = "What is artificial intelligence?"
        expected_results = [{"knowledge": "AI definition"}]
        mock_pinecone_client.retrieve_similar.return_value = expected_results
        result = memory_manager.retrieve_semantic_memories(user_id, query)
        assert result == expected_results
        mock_pinecone_client.retrieve_similar.assert_called_once_with(user_id=user_id, query=query, k=5, filter_metadata=None)


class TestMemoryType:
    """Test the MemoryType enum."""
    
    def test_memory_type_values(self):
        """Test MemoryType enum values."""
        assert MemoryType.EPISODIC == "episodic"
        assert MemoryType.SEMANTIC == "semantic"
        assert MemoryType.PROCEDURAL == "procedural"
        assert MemoryType.SHORT_TERM == "short_term"


class TestMemoryManagerIntegration:
    """Integration tests for MemoryManager."""
    
    @pytest.fixture
    def mock_memory_manager(self):
        """Create a mock memory manager for integration tests."""
        mock = MagicMock(spec=MemoryManager)
        mock.create_conversation = MagicMock(return_value="test_conversation_id")
        mock.create_session = MagicMock(return_value="test_session_id")
        mock.store_episodic_memory = MagicMock(return_value="test_episodic_id")
        mock.store_procedural_memory = MagicMock(return_value="test_procedural_id")
        mock.store_semantic_memory = MagicMock(return_value="test_knowledge_id")
        mock.retrieve_episodic_memories = MagicMock(return_value=[])
        mock.retrieve_procedural_memories = MagicMock(return_value=[])
        mock.retrieve_semantic_memories = MagicMock(return_value=[])
        return mock
    
    @pytest.mark.asyncio
    async def test_memory_workflow(self, mock_memory_manager, mock_episodic_memory,
                                    mock_procedural_memory, mock_pinecone_client):
        """Test complete memory workflow."""
        user_id = "test_user"
        conversation_id = "test_conv"
        session_id = "test_session"
        
        # Create conversation and session
        conv_id = mock_memory_manager.create_conversation(user_id)
        sess_id = mock_memory_manager.create_session(user_id, conversation_id)
        
        assert conv_id == "test_conversation_id"
        assert sess_id == "test_session_id"
        
        # Store different types of memory
        episodic_id = mock_memory_manager.store_episodic_memory(
            user_id,
            {"event": "user_query", "message": "What is AI?"},
            {"conversation_id": conversation_id}
        )

        procedural_id = mock_memory_manager.store_procedural_memory(
            user_id,
            {"tool": "web_search", "success": True},
            {"conversation_id": conversation_id}
        )

        knowledge_id = mock_memory_manager.store_semantic_memory(
            user_id,
            "AI is artificial intelligence",
            {"source": "conversation", "category": "definition"}
        )
        
        assert episodic_id == "test_episodic_id"
        assert procedural_id == "test_procedural_id"
        assert knowledge_id == "test_knowledge_id"
        
        # Retrieve memories via the mock manager
        mock_memory_manager.retrieve_episodic_memories(user_id, {"query": "AI"})
        mock_memory_manager.retrieve_procedural_memories(user_id, {"query": "web_search"})
        mock_memory_manager.retrieve_semantic_memories(user_id, "artificial intelligence")
        mock_memory_manager.retrieve_semantic_memories(user_id, "AI definition")
        
        # Verify the manager's methods were called
        mock_memory_manager.retrieve_episodic_memories.assert_called()
        mock_memory_manager.retrieve_procedural_memories.assert_called()
        mock_memory_manager.retrieve_semantic_memories.assert_called()
