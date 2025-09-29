"""Tests for database clients."""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pymongo

from app.memory.mongodb_client import MongoDBClient
from app.db_clients.pinecone_client import PineconeClient


class TestMongoDBClient:
    """Test MongoDBClient functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_client(self):
        """Setup MongoDB client for testing."""
        with patch('app.memory.mongodb_client.MongoClient') as mock_mongo_client_cls:
            mock_mongo_client = MagicMock()
            mock_database = MagicMock()
            mock_mongo_client.__getitem__.return_value = mock_database
            mock_mongo_client_cls.return_value = mock_mongo_client
            
            # Create client instance
            self.client = MongoDBClient()
            
            # Mock the collections with correct names
            self.client.memory = MagicMock()
            self.client.conversations = MagicMock()
            self.client.sessions = MagicMock()
            
            yield

    def test_get_database(self):
        """Test getting database instance."""
        # Test that the client has access to the database
        assert hasattr(self.client, 'db')
        assert self.client.db is not None

    def test_store_memory(self):
        """Test storing memory in MongoDB."""
        # Test data
        user_id = "test_user"
        memory_type = "episodic"
        content = {"event": "test_event"}
        metadata = {
            "timestamp": datetime.utcnow(),
            "source": "test"
        }
        
        # Mock the collection
        mock_collection = MagicMock()
        mock_result = MagicMock()
        mock_result.inserted_id = "test_id"
        mock_collection.insert_one.return_value = mock_result
        
        # Set up the mock chain properly
        self.client.memory = mock_collection
        
        # Store memory
        result = self.client.store_memory(user_id, memory_type, content, metadata)
        
        # Verify
        assert result == "test_id"
        mock_collection.insert_one.assert_called_once()
        
        # Check that the call arguments include the expected fields
        call_args = mock_collection.insert_one.call_args[0][0]
        assert "user_id" in call_args
        assert "memory_type" in call_args
        assert "content" in call_args
        assert "created_at" in call_args
        assert "updated_at" in call_args

    def test_get_memories(self):
        """Test retrieving memories from MongoDB."""
        # Test data
        user_id = "test_user"
        memory_type = "episodic"
        filter_query = {"content.event": {"$exists": True}}
        
        # Mock the collection
        mock_collection = MagicMock()
        
        # Mock the find operation chain
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.sort.return_value = mock_cursor
        
        # Mock cursor iteration
        mock_cursor.__iter__.return_value = [
            {
                "_id": "mem_1",
                "user_id": user_id,
                "memory_type": memory_type,
                "content": {"event": "event_1"},
                "metadata": {
                    "timestamp": datetime.utcnow(),
                    "source": "test"
                }
            },
            {
                "_id": "mem_2",
                "user_id": user_id,
                "memory_type": memory_type,
                "content": {"event": "event_2"},
                "metadata": {
                    "timestamp": datetime.utcnow(),
                    "source": "test"
                }
            }
        ]
        
        # Set up the mock chain
        mock_collection.find.return_value = mock_cursor
        self.client.memory = mock_collection
        
        # Get memories
        memories = self.client.retrieve_memories(
            user_id=user_id,
            memory_type=memory_type,
            filter_query=filter_query,
            limit=10
        )
        
        # Verify
        assert len(memories) == 2
        mock_collection.find.assert_called_once()
        mock_cursor.limit.assert_called_once_with(10)

    def test_create_conversation(self):
        """Test creating a conversation."""
        # Arrange
        mock_collection = MagicMock()
        mock_result = MagicMock()
        mock_result.inserted_id = "test_conversation_id"
        mock_collection.insert_one.return_value = mock_result
        self.client.conversations = mock_collection
        
        # Act
        conversation_id = self.client.create_conversation("test_user")
        
        # Assert
        assert conversation_id == "test_conversation_id"
        mock_collection.insert_one.assert_called_once()
        
        # Check that the call arguments include the expected fields
        call_args = mock_collection.insert_one.call_args[0][0]
        assert call_args["user_id"] == "test_user"
        assert "created_at" in call_args

    def test_get_conversation(self):
        """Test getting conversation by ID."""
        # Use a valid ObjectId string
        conversation_id = "507f1f77bcf86cd799439011"  # 24-character hex string
        
        # Mock the collection
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {
            "_id": conversation_id,
            "user_id": "test_user",
            "messages": [],
            "created_at": datetime.utcnow()
        }
        self.client.conversations = mock_collection
        
        # Get conversation
        conversation = self.client.get_conversation(conversation_id)
        
        # Verify
        assert conversation is not None
        assert conversation["_id"] == conversation_id
        mock_collection.find_one.assert_called_once()

    def test_add_message_to_conversation(self):
        """Test adding message to conversation."""
        # Use a valid ObjectId string
        conversation_id = "507f1f77bcf86cd799439011"
        message = {
            "role": "user",
            "content": "Hello",
            "timestamp": datetime.utcnow()
        }
        
        # Mock the collection
        mock_collection = MagicMock()
        mock_collection.update_one.return_value.modified_count = 1
        self.client.conversations = mock_collection
        
        # Add message
        result = self.client.add_message(conversation_id, message)
        
        # Verify
        assert result is True
        mock_collection.update_one.assert_called_once()

    def test_get_user_conversations(self):
        """Test getting user conversations."""
        user_id = "test_user"
        expected_conversations = [
            {"_id": "conv_1", "user_id": user_id},
            {"_id": "conv_2", "user_id": user_id}
        ]
        
        # Mock the collection
        mock_collection = MagicMock()
        
        # Mock the find operation chain
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        
        # Mock cursor iteration
        mock_cursor.__iter__.return_value = expected_conversations
        
        # Set up the mock chain
        mock_collection.find.return_value = mock_cursor
        self.client.conversations = mock_collection
        
        # Get conversations
        conversations = self.client.get_user_conversations(user_id, limit=10)
        
        # Verify
        assert conversations == expected_conversations
        mock_collection.find.assert_called_once()
        mock_cursor.sort.assert_called_once()
        mock_cursor.limit.assert_called_once_with(10)

    @patch('app.memory.mongodb_client.MongoClient')
    def test_connection_error_handling(self, mock_mongo_client_cls):
        """Test MongoDB connection error handling."""
        # Arrange
        mock_mongo_client_cls.side_effect = pymongo.errors.ConnectionFailure("Connection failed")
        
        # Act & Assert
        with pytest.raises(pymongo.errors.ConnectionFailure):
            MongoDBClient()


class TestPineconeClient:
    """Test PineconeClient functionality."""
    
    @patch('app.db_clients.pinecone_client.PineconeClient._initialize_index')
    @patch('app.db_clients.pinecone_client.Pinecone')
    def test_init(self, mock_pinecone_cls, mock_init_index):
        """Test PineconeClient initialization."""
        # Arrange
        mock_pinecone = MagicMock()
        mock_pinecone_cls.return_value = mock_pinecone
        
        # Act
        client = PineconeClient()
        
        # Assert
        mock_pinecone_cls.assert_called_once()
        assert client.pc == mock_pinecone
        mock_init_index.assert_called_once()

    @patch('app.db_clients.pinecone_client.PineconeClient._initialize_index')
    @patch('app.db_clients.pinecone_client.Pinecone')
    def test_get_index(self, mock_pinecone_cls, mock_init_index):
        """Test getting Pinecone index."""
        # Arrange
        mock_pinecone = MagicMock()
        mock_index = MagicMock()
        mock_pinecone.Index.return_value = mock_index
        mock_pinecone_cls.return_value = mock_pinecone
        
        client = PineconeClient()
        
        # Act
        index = client.pc.Index(client.index_name)
        
        # Assert
        assert index == mock_index
        # The Index method is called multiple times during initialization, so we check it was called
        mock_pinecone.Index.assert_called()

    @patch('app.db_clients.pinecone_client.PineconeClient._initialize_index')
    @patch('app.db_clients.pinecone_client.Pinecone')
    @patch('app.db_clients.pinecone_client.OpenAIEmbeddings')
    def test_store_memory(self, mock_embeddings_cls, mock_pinecone_cls, mock_init_index):
        """Test storing memory in Pinecone."""
        # Arrange
        mock_pinecone = MagicMock()
        mock_index = MagicMock()
        mock_embeddings = MagicMock()
        
        mock_pinecone.Index.return_value = mock_index
        mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_pinecone_cls.return_value = mock_pinecone
        mock_embeddings_cls.return_value = mock_embeddings
        
        client = PineconeClient()
        
        # Act
        memory_id = client.store_memory(
            user_id="test_user",
            text="User likes coffee",
            metadata={"category": "preferences"}
        )
        
        # Assert
        assert memory_id is not None

    @patch('app.db_clients.pinecone_client.PineconeClient._initialize_index')
    @patch('app.db_clients.pinecone_client.Pinecone')
    @patch('app.db_clients.pinecone_client.OpenAIEmbeddings')
    def test_retrieve_similar(self, mock_embeddings_cls, mock_pinecone_cls, mock_init_index):
        """Test retrieving similar memories in Pinecone."""
        # Arrange
        mock_pinecone = MagicMock()
        mock_index = MagicMock()
        mock_embeddings = MagicMock()
        
        mock_pinecone.Index.return_value = mock_index
        mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
        
        # Mock vector store search results
        mock_doc1 = MagicMock()
        mock_doc1.page_content = "User likes coffee in the morning"
        mock_doc1.metadata = {"user_id": "test_user", "category": "preferences"}
        
        mock_doc2 = MagicMock()
        mock_doc2.page_content = "User prefers espresso"
        mock_doc2.metadata = {"user_id": "test_user", "category": "preferences"}
        
        mock_results = [(mock_doc1, 0.95), (mock_doc2, 0.87)]
        
        # Mock the vector store
        client = PineconeClient()
        client.vector_store = MagicMock()
        client.vector_store.similarity_search_with_score.return_value = mock_results
        
        # Act
        results = client.retrieve_similar(
            user_id="test_user",
            query="coffee preferences",
            k=3
        )
        
        # Assert
        assert len(results) == 2

    @patch('app.db_clients.pinecone_client.PineconeClient._initialize_index')
    @patch('app.db_clients.pinecone_client.Pinecone')
    @patch('app.db_clients.pinecone_client.OpenAIEmbeddings')
    def test_retrieve_similar_no_results(self, mock_embeddings_cls, mock_pinecone_cls, mock_init_index):
        """Test retrieving with no results."""
        # Arrange
        mock_pinecone = MagicMock()
        mock_index = MagicMock()
        mock_embeddings = MagicMock()
        
        mock_pinecone.Index.return_value = mock_index
        mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
        
        # Mock the vector store
        client = PineconeClient()
        client.vector_store = MagicMock()
        client.vector_store.similarity_search_with_score.return_value = []
        
        # Act
        results = client.retrieve_similar(
            user_id="test_user",
            query="nonexistent query",
            k=3
        )
        
        # Assert
        assert results == []

    @patch('app.db_clients.pinecone_client.PineconeClient._initialize_index')
    @patch('app.db_clients.pinecone_client.Pinecone')
    @patch('app.db_clients.pinecone_client.OpenAIEmbeddings')
    def test_embedding_error_handling(self, mock_embeddings_cls, mock_pinecone_cls, mock_init_index):
        """Test handling of embedding errors."""
        # Arrange
        mock_embeddings = MagicMock()
        mock_embeddings.embed_query.side_effect = Exception("Embedding error")
        mock_embeddings_cls.return_value = mock_embeddings
        
        client = PineconeClient()
        
        # Mock the vector store directly
        client.vector_store = MagicMock()
        client.vector_store.add_documents.side_effect = Exception("Vector store error")
        
        # Act & Assert
        with pytest.raises(Exception):
            client.store_memory(
                user_id="test_user",
                text="Test text",
                metadata={}
            )

    @patch('app.db_clients.pinecone_client.PineconeClient._initialize_index')
    @patch('app.db_clients.pinecone_client.Pinecone')
    def test_pinecone_connection_error(self, mock_pinecone_cls, mock_init_index):
        """Test Pinecone connection error handling."""
        # Arrange
        mock_pinecone_cls.side_effect = Exception("Pinecone connection failed")
        
        # Act & Assert
        with pytest.raises(Exception):
            PineconeClient()

    @patch('app.db_clients.pinecone_client.PineconeClient._initialize_index')
    @patch('app.db_clients.pinecone_client.Pinecone')
    @patch('app.db_clients.pinecone_client.OpenAIEmbeddings')
    def test_delete_memory(self, mock_embeddings_cls, mock_pinecone_cls, mock_init_index):
        """Test deleting memory from Pinecone."""
        # Arrange
        mock_pinecone = MagicMock()
        mock_index = MagicMock()
        mock_pinecone.Index.return_value = mock_index
        mock_pinecone_cls.return_value = mock_pinecone
        
        client = PineconeClient()
        
        # Mock the vector store
        client.vector_store = MagicMock()
        
        # Act
        result = client.delete_memory("test_memory_id")
        
        # Assert
        assert result is True
        client.vector_store.delete.assert_called_once_with(ids=["test_memory_id"])

    @patch('app.db_clients.pinecone_client.PineconeClient._initialize_index')
    @patch('app.db_clients.pinecone_client.Pinecone')
    @patch('app.db_clients.pinecone_client.OpenAIEmbeddings')
    def test_query_knowledge(self, mock_embeddings_cls, mock_pinecone_cls, mock_init_index):
        """Test querying knowledge from Pinecone."""
        # Arrange
        mock_pinecone = MagicMock()
        mock_index = MagicMock()
        mock_embeddings = MagicMock()
        
        mock_pinecone.Index.return_value = mock_index
        mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
        
        # Mock the vector store
        client = PineconeClient()
        client.vector_store = MagicMock()
        
        mock_doc = MagicMock()
        mock_doc.page_content = "AI is artificial intelligence"
        mock_doc.metadata = {"source": "textbook"}
        
        mock_results = [(mock_doc, 0.95)]
        client.vector_store.similarity_search_with_score.return_value = mock_results
        
        # Act
        results = client.query_knowledge(
            query="What is AI?",
            top_k=5
        )
        
        # Assert
        assert len(results) == 1
        assert results[0][0].page_content == "AI is artificial intelligence"
