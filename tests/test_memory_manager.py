"""Tests for memory manager."""

import pytest
from unittest.mock import MagicMock, patch, call
from datetime import datetime
from typing import List, Tuple

from app.memory.memory_manager import MemoryManager, MemoryType
from langchain_core.documents import Document


class TestMemoryManager:
    """Tests for the memory manager."""
    
    @patch('app.memory.memory_manager.SemanticExtractor')
    @patch('app.memory.memory_manager.EpisodicMemoryManager')
    @patch('app.memory.memory_manager.ProceduralMemoryManager')
    @patch('app.memory.memory_manager.SessionManager')
    @patch('app.memory.memory_manager.MongoDBClient')
    @patch('app.memory.memory_manager.PineconeClient')
    def test_init(self, mock_pinecone_cls, mock_mongodb_cls, mock_session_cls, 
                  mock_procedural_cls, mock_episodic_cls, mock_semantic_cls):
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
        assert manager.short_term_memories == {}
        mock_session_cls.assert_called_once_with(mock_mongodb)
        mock_semantic_cls.assert_called_once()
        mock_episodic_cls.assert_called_once_with(mock_mongodb)
        mock_procedural_cls.assert_called_once_with(mock_mongodb)

    @patch('app.memory.memory_manager.SemanticExtractor')
    @patch('app.memory.memory_manager.EpisodicMemoryManager')
    @patch('app.memory.memory_manager.ProceduralMemoryManager')
    @patch('app.memory.memory_manager.SessionManager')
    @patch('app.memory.memory_manager.ShortTermMemory')
    @patch('app.memory.memory_manager.MongoDBClient')
    @patch('app.memory.memory_manager.PineconeClient')
    def test_get_short_term_memory_new_session(self, mock_pinecone_cls, mock_mongodb_cls, 
                                               mock_short_term_cls, mock_session_cls,
                                               mock_procedural_cls, mock_episodic_cls, 
                                               mock_semantic_cls):
        """Test getting short-term memory for new session."""
        # Arrange
        mock_short_term = MagicMock()
        mock_short_term_cls.return_value = mock_short_term
        
        manager = MemoryManager()
        
        # Act
        result = manager.get_short_term_memory("new_session")
        
        # Assert
        assert result == mock_short_term
        assert manager.short_term_memories["new_session"] == mock_short_term
        mock_short_term_cls.assert_called_once_with("new_session")

    @patch('app.memory.memory_manager.SemanticExtractor')
    @patch('app.memory.memory_manager.EpisodicMemoryManager')
    @patch('app.memory.memory_manager.ProceduralMemoryManager')
    @patch('app.memory.memory_manager.SessionManager')
    @patch('app.memory.memory_manager.ShortTermMemory')
    @patch('app.memory.memory_manager.MongoDBClient')
    @patch('app.memory.memory_manager.PineconeClient')
    def test_get_short_term_memory_existing_session(self, mock_pinecone_cls, mock_mongodb_cls, 
                                                   mock_short_term_cls, mock_session_cls,
                                                   mock_procedural_cls, mock_episodic_cls, 
                                                   mock_semantic_cls):
        """Test getting short-term memory for existing session."""
        # Arrange
        mock_short_term = MagicMock()
        manager = MemoryManager()
        manager.short_term_memories["existing_session"] = mock_short_term
        
        # Act
        result = manager.get_short_term_memory("existing_session")
        
        # Assert
        assert result == mock_short_term
        mock_short_term_cls.assert_not_called()  # Should not create new instance

    @patch('app.memory.memory_manager.SemanticExtractor')
    @patch('app.memory.memory_manager.EpisodicMemoryManager')
    @patch('app.memory.memory_manager.ProceduralMemoryManager')
    @patch('app.memory.memory_manager.SessionManager')
    @patch('app.memory.memory_manager.MongoDBClient')
    @patch('app.memory.memory_manager.PineconeClient')
    def test_clear_short_term_memory(self, mock_pinecone_cls, mock_mongodb_cls, mock_session_cls,
                                    mock_procedural_cls, mock_episodic_cls, mock_semantic_cls):
        """Test clearing short-term memory."""
        # Arrange
        mock_short_term = MagicMock()
        manager = MemoryManager()
        manager.short_term_memories["test_session"] = mock_short_term
        
        # Act
        manager.clear_short_term_memory("test_session")
        
        # Assert
        mock_short_term.clear.assert_called_once()

    @patch('app.memory.memory_manager.SemanticExtractor')
    @patch('app.memory.memory_manager.EpisodicMemoryManager')
    @patch('app.memory.memory_manager.ProceduralMemoryManager')
    @patch('app.memory.memory_manager.SessionManager')
    @patch('app.memory.memory_manager.MongoDBClient')
    @patch('app.memory.memory_manager.PineconeClient')
    def test_create_conversation(self, mock_pinecone_cls, mock_mongodb_cls, mock_session_cls,
                                mock_procedural_cls, mock_episodic_cls, mock_semantic_cls):
        """Test creating a conversation."""
        # Arrange
        mock_mongodb = MagicMock()
        mock_mongodb.create_conversation.return_value = "test_conversation_id"
        mock_mongodb_cls.return_value = mock_mongodb
        
        manager = MemoryManager()
        
        # Act
        result = manager.create_conversation("test_user")
        
        # Assert
        assert result == "test_conversation_id"
        mock_mongodb.create_conversation.assert_called_once_with("test_user")

    @patch('app.memory.memory_manager.SemanticExtractor')
    @patch('app.memory.memory_manager.EpisodicMemoryManager')
    @patch('app.memory.memory_manager.ProceduralMemoryManager')
    @patch('app.memory.memory_manager.SessionManager')
    @patch('app.memory.memory_manager.MongoDBClient')
    @patch('app.memory.memory_manager.PineconeClient')
    def test_store_episodic_memory(self, mock_pinecone_cls, mock_mongodb_cls, mock_session_cls,
                                  mock_procedural_cls, mock_episodic_cls, mock_semantic_cls):
        """Test storing episodic memory."""
        # Arrange
        mock_episodic = MagicMock()
        mock_episodic.store_memory.return_value = "test_episodic_id"
        mock_episodic_cls.return_value = mock_episodic
        
        manager = MemoryManager()
        
        # Act
        result = manager.store_episodic_memory(
            user_id="test_user",
            content={"event": "test_event"},
            metadata={"source": "test"}
        )
        
        # Assert
        assert result == "test_episodic_id"
        mock_episodic.store_memory.assert_called_once_with(
            user_id="test_user",
            content={"event": "test_event"},
            metadata={"source": "test"}
        )

    @patch('app.memory.memory_manager.SemanticExtractor')
    @patch('app.memory.memory_manager.EpisodicMemoryManager')
    @patch('app.memory.memory_manager.ProceduralMemoryManager')
    @patch('app.memory.memory_manager.SessionManager')
    @patch('app.memory.memory_manager.MongoDBClient')
    @patch('app.memory.memory_manager.PineconeClient')
    def test_store_semantic_memory(self, mock_pinecone_cls, mock_mongodb_cls, mock_session_cls,
                                  mock_procedural_cls, mock_episodic_cls, mock_semantic_cls):
        """Test storing semantic memory."""
        # Arrange
        mock_pinecone = MagicMock()
        mock_pinecone.store_memory.return_value = "test_semantic_id"
        mock_pinecone_cls.return_value = mock_pinecone
        
        manager = MemoryManager()
        
        # Act
        result = manager.store_semantic_memory(
            user_id="test_user",
            text="User likes coffee",
            metadata={"category": "preferences"}
        )
        
        # Assert
        assert result == "test_semantic_id"
        mock_pinecone.store_memory.assert_called_once_with(
            user_id="test_user",
            text="User likes coffee",
            metadata={"category": "preferences"}
        )

    @patch('app.memory.memory_manager.SemanticExtractor')
    @patch('app.memory.memory_manager.EpisodicMemoryManager')
    @patch('app.memory.memory_manager.ProceduralMemoryManager')
    @patch('app.memory.memory_manager.SessionManager')
    @patch('app.memory.memory_manager.MongoDBClient')
    @patch('app.memory.memory_manager.PineconeClient')
    def test_store_procedural_memory(self, mock_pinecone_cls, mock_mongodb_cls, mock_session_cls,
                                    mock_procedural_cls, mock_episodic_cls, mock_semantic_cls):
        """Test storing procedural memory."""
        # Arrange
        mock_procedural = MagicMock()
        mock_procedural.store_memory.return_value = "test_procedural_id"
        mock_procedural_cls.return_value = mock_procedural
        
        manager = MemoryManager()
        
        # Act
        result = manager.store_procedural_memory(
            user_id="test_user",
            content={"tool": "search", "success": True},
            metadata={"pattern": "search_pattern"}
        )
        
        # Assert
        assert result == "test_procedural_id"
        mock_procedural.store_memory.assert_called_once_with(
            user_id="test_user",
            content={"tool": "search", "success": True},
            metadata={"pattern": "search_pattern"}
        )

    @patch('app.memory.memory_manager.SemanticExtractor')
    @patch('app.memory.memory_manager.EpisodicMemoryManager')
    @patch('app.memory.memory_manager.ProceduralMemoryManager')
    @patch('app.memory.memory_manager.SessionManager')
    @patch('app.memory.memory_manager.MongoDBClient')
    @patch('app.memory.memory_manager.PineconeClient')
    def test_retrieve_semantic_memories(self, mock_pinecone_cls, mock_mongodb_cls, mock_session_cls,
                                       mock_procedural_cls, mock_episodic_cls, mock_semantic_cls):
        """Test retrieving semantic memories."""
        # Arrange
        mock_pinecone = MagicMock()
        expected_results = [
            (Document(page_content="User likes coffee", metadata={"score": 0.95}), 0.95)
        ]
        mock_pinecone.search_similar.return_value = expected_results
        mock_pinecone_cls.return_value = mock_pinecone
        
        manager = MemoryManager()
        
        # Act
        result = manager.retrieve_semantic_memories(
            user_id="test_user",
            query="coffee preferences",
            k=3
        )
        
        # Assert
        assert result == expected_results
        mock_pinecone.search_similar.assert_called_once_with(
            user_id="test_user",
            query="coffee preferences",
            k=3
        )

    @patch('app.memory.memory_manager.SemanticExtractor')
    @patch('app.memory.memory_manager.EpisodicMemoryManager')
    @patch('app.memory.memory_manager.ProceduralMemoryManager')
    @patch('app.memory.memory_manager.SessionManager')
    @patch('app.memory.memory_manager.MongoDBClient')
    @patch('app.memory.memory_manager.PineconeClient')
    def test_retrieve_episodic_memories(self, mock_pinecone_cls, mock_mongodb_cls, mock_session_cls,
                                       mock_procedural_cls, mock_episodic_cls, mock_semantic_cls):
        """Test retrieving episodic memories."""
        # Arrange
        mock_episodic = MagicMock()
        expected_results = [
            {
                "_id": "episodic_1",
                "user_id": "test_user",
                "content": {"event": "greeting"},
                "metadata": {"timestamp": datetime.utcnow()}
            }
        ]
        mock_episodic.get_memories.return_value = expected_results
        mock_episodic_cls.return_value = mock_episodic
        
        manager = MemoryManager()
        
        # Act
        result = manager.retrieve_episodic_memories(
            user_id="test_user",
            filter_query={"content.event": "greeting"},
            limit=5
        )
        
        # Assert
        assert result == expected_results
        mock_episodic.get_memories.assert_called_once_with(
            user_id="test_user",
            filter_query={"content.event": "greeting"},
            limit=5
        )

    @patch('app.memory.memory_manager.SemanticExtractor')
    @patch('app.memory.memory_manager.EpisodicMemoryManager')
    @patch('app.memory.memory_manager.ProceduralMemoryManager')
    @patch('app.memory.memory_manager.SessionManager')
    @patch('app.memory.memory_manager.MongoDBClient')
    @patch('app.memory.memory_manager.PineconeClient')
    def test_extract_semantic_facts(self, mock_pinecone_cls, mock_mongodb_cls, mock_session_cls,
                                   mock_procedural_cls, mock_episodic_cls, mock_semantic_cls):
        """Test extracting semantic facts."""
        # Arrange
        mock_semantic_extractor = MagicMock()
        expected_facts = [
            {"fact": "User prefers morning meetings", "confidence": 0.9}
        ]
        mock_semantic_extractor.extract_facts.return_value = expected_facts
        mock_semantic_cls.return_value = mock_semantic_extractor
        
        manager = MemoryManager()
        
        # Act
        result = manager.extract_semantic_facts(
            user_message="I prefer meetings in the morning",
            agent_response="I'll schedule morning meetings for you",
            conversation_context=[],
            user_id="test_user"
        )
        
        # Assert
        assert result == expected_facts
        mock_semantic_extractor.extract_facts.assert_called_once()

    @patch('app.memory.memory_manager.SemanticExtractor')
    @patch('app.memory.memory_manager.EpisodicMemoryManager')
    @patch('app.memory.memory_manager.ProceduralMemoryManager')
    @patch('app.memory.memory_manager.SessionManager')
    @patch('app.memory.memory_manager.MongoDBClient')
    @patch('app.memory.memory_manager.PineconeClient')
    def test_store_extracted_semantic_facts(self, mock_pinecone_cls, mock_mongodb_cls, mock_session_cls,
                                           mock_procedural_cls, mock_episodic_cls, mock_semantic_cls):
        """Test storing extracted semantic facts."""
        # Arrange
        mock_pinecone = MagicMock()
        mock_pinecone_cls.return_value = mock_pinecone
        
        manager = MemoryManager()
        facts = [
            {"fact": "User likes Python", "confidence": 0.95},
            {"fact": "User works remotely", "confidence": 0.8}
        ]
        
        # Act
        manager.store_extracted_semantic_facts(
            user_id="test_user",
            facts=facts,
            conversation_metadata={"conversation_id": "test_conv"}
        )
        
        # Assert
        assert mock_pinecone.store_memory.call_count == 2
        calls = mock_pinecone.store_memory.call_args_list
        
        # Check first fact
        assert calls[0][1]["user_id"] == "test_user"
        assert "User likes Python" in calls[0][1]["text"]
        
        # Check second fact
        assert calls[1][1]["user_id"] == "test_user"
        assert "User works remotely" in calls[1][1]["text"]

    def test_memory_type_enum(self):
        """Test MemoryType enum values."""
        # Assert
        assert MemoryType.EPISODIC == "episodic"
        assert MemoryType.SEMANTIC == "semantic"
        assert MemoryType.PROCEDURAL == "procedural"
        assert MemoryType.SHORT_TERM == "short_term"
