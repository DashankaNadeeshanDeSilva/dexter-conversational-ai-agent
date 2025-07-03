"""Tests for memory manager."""

import pytest
from unittest.mock import MagicMock, patch
from app.memory.memory_manager import MemoryManager, MemoryType

@pytest.fixture
def mock_mongodb_client():
    """Create a mock MongoDB client."""
    mock = MagicMock()
    return mock

@pytest.fixture
def mock_pinecone_client():
    """Create a mock Pinecone client."""
    mock = MagicMock()
    return mock

class TestMemoryManager:
    """Tests for the memory manager."""
    
    @patch('app.memory.memory_manager.MongoDBClient')
    @patch('app.memory.memory_manager.PineconeClient')
    def test_init(self, mock_pinecone_cls, mock_mongodb_cls):
        """Test initialization of memory manager."""
        # Arrange
        mock_mongodb = MagicMock()
        mock_pinecone = MagicMock()
        mock_mongodb_cls.return_value = mock_mongodb
        mock_pinecone_cls.return_value = mock_pinecone
        
        # Act
        manager = MemoryManager()
        
        # Assert
        assert manager.mongodb_client == mock_mongodb
        assert manager.pinecone_client == mock_pinecone
    
    @patch('app.memory.memory_manager.MongoDBClient')
    @patch('app.memory.memory_manager.PineconeClient')
    def test_store_episodic_memory(self, mock_pinecone_cls, mock_mongodb_cls):
        """Test storing episodic memory."""
        # Arrange
        mock_mongodb = MagicMock()
        mock_mongodb.store_memory.return_value = "test-memory-id"
        mock_mongodb_cls.return_value = mock_mongodb
        
        manager = MemoryManager()
        
        # Act
        result = manager.store_episodic_memory(
            user_id="test-user",
            content={"test": "content"},
            metadata={"meta": "data"}
        )
        
        # Assert
        assert result == "test-memory-id"
        mock_mongodb.store_memory.assert_called_once_with(
            user_id="test-user",
            memory_type=MemoryType.EPISODIC.value,
            content={"test": "content"},
            metadata={"meta": "data"}
        )
    
    @patch('app.memory.memory_manager.MongoDBClient')
    @patch('app.memory.memory_manager.PineconeClient')
    def test_store_semantic_memory(self, mock_pinecone_cls, mock_mongodb_cls):
        """Test storing semantic memory."""
        # Arrange
        mock_pinecone = MagicMock()
        mock_pinecone.store_memory.return_value = "test-memory-id"
        mock_pinecone_cls.return_value = mock_pinecone
        
        manager = MemoryManager()
        
        # Act
        result = manager.store_semantic_memory(
            user_id="test-user",
            text="test content",
            metadata={"meta": "data"}
        )
        
        # Assert
        assert result == "test-memory-id"
        mock_pinecone.store_memory.assert_called_once_with(
            user_id="test-user",
            text="test content",
            metadata={"meta": "data"}
        )
    
    @patch('app.memory.memory_manager.MongoDBClient')
    @patch('app.memory.memory_manager.PineconeClient')
    def test_create_conversation(self, mock_pinecone_cls, mock_mongodb_cls):
        """Test creating a conversation."""
        # Arrange
        mock_mongodb = MagicMock()
        mock_mongodb.create_conversation.return_value = "test-conversation-id"
        mock_mongodb_cls.return_value = mock_mongodb
        
        manager = MemoryManager()
        
        # Act
        result = manager.create_conversation(user_id="test-user")
        
        # Assert
        assert result == "test-conversation-id"
        mock_mongodb.create_conversation.assert_called_once_with("test-user")
    
    @patch('app.memory.memory_manager.ShortTermMemory')
    @patch('app.memory.memory_manager.MongoDBClient')
    @patch('app.memory.memory_manager.PineconeClient')
    def test_get_short_term_memory(self, mock_pinecone_cls, mock_mongodb_cls, mock_short_term_cls):
        """Test getting short-term memory."""
        # Arrange
        mock_short_term = MagicMock()
        mock_short_term_cls.return_value = mock_short_term
        
        manager = MemoryManager()
        
        # Act
        result = manager.get_short_term_memory("test-session")
        
        # Assert
        assert result == mock_short_term
        mock_short_term_cls.assert_called_once_with("test-session")
        
        # Act again to test retrieval of existing memory
        result2 = manager.get_short_term_memory("test-session")
        
        # Assert only one instance was created
        assert mock_short_term_cls.call_count == 1
        assert result2 == mock_short_term
