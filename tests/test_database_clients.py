"""Tests for database clients."""

import pytest
from unittest.mock import MagicMock, patch, call
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pymongo

from app.memory.mongodb_client import MongoDBClient
from app.db_clients.pinecone_client import PineconeClient


class TestMongoDBClient:
    """Tests for MongoDB client."""
    
    @patch('app.memory.mongodb_client.MongoClient')
    def test_init(self, mock_mongo_client_cls):
        """Test initialization of MongoDB client."""
        # Arrange
        mock_mongo_client = MagicMock()
        mock_mongo_client_cls.return_value = mock_mongo_client
        
        # Act
        client = MongoDBClient()
        
        # Assert
        assert client.client == mock_mongo_client
        mock_mongo_client_cls.assert_called_once()

    @patch('app.memory.mongodb_client.MongoClient')
    def test_get_database(self, mock_mongo_client_cls):
        """Test getting database."""
        # Arrange
        mock_mongo_client = MagicMock()
        mock_database = MagicMock()
        mock_mongo_client.__getitem__.return_value = mock_database
        mock_mongo_client_cls.return_value = mock_mongo_client
        
        client = MongoDBClient()
        
        # Act
        database = client.get_database()
        
        # Assert
        assert database == mock_database

    @patch('app.memory.mongodb_client.MongoClient')
    def test_store_memory(self, mock_mongo_client_cls):
        """Test storing memory in MongoDB."""
        # Arrange
        mock_mongo_client = MagicMock()
        mock_database = MagicMock()
        mock_collection = MagicMock()
        mock_result = MagicMock()
        mock_result.inserted_id = "test_memory_id"
        
        mock_mongo_client.__getitem__.return_value = mock_database
        mock_database.__getitem__.return_value = mock_collection
        mock_collection.insert_one.return_value = mock_result
        mock_mongo_client_cls.return_value = mock_mongo_client
        
        client = MongoDBClient()
        
        # Act
        memory_id = client.store_memory(
            user_id="test_user",
            memory_type="episodic",
            content={"event": "test_event"},
            metadata={"source": "test"}
        )
        
        # Assert
        assert memory_id == "test_memory_id"
        mock_collection.insert_one.assert_called_once()
        call_args = mock_collection.insert_one.call_args[0][0]
        assert call_args["user_id"] == "test_user"
        assert call_args["memory_type"] == "episodic"
        assert call_args["content"] == {"event": "test_event"}
        assert call_args["metadata"] == {"source": "test"}
        assert "timestamp" in call_args

    @patch('app.memory.mongodb_client.MongoClient')
    def test_get_memories(self, mock_mongo_client_cls):
        """Test retrieving memories from MongoDB."""
        # Arrange
        mock_mongo_client = MagicMock()
        mock_database = MagicMock()
        mock_collection = MagicMock()
        mock_cursor = MagicMock()
        
        expected_memories = [
            {
                "_id": "memory_1",
                "user_id": "test_user",
                "memory_type": "episodic",
                "content": {"event": "test_event_1"},
                "timestamp": datetime.utcnow()
            },
            {
                "_id": "memory_2",
                "user_id": "test_user",
                "memory_type": "episodic",
                "content": {"event": "test_event_2"},
                "timestamp": datetime.utcnow()
            }
        ]
        
        mock_cursor.limit.return_value.sort.return_value = expected_memories
        mock_collection.find.return_value = mock_cursor
        mock_mongo_client.__getitem__.return_value = mock_database
        mock_database.__getitem__.return_value = mock_collection
        mock_mongo_client_cls.return_value = mock_mongo_client
        
        client = MongoDBClient()
        
        # Act
        memories = client.get_memories(
            user_id="test_user",
            memory_type="episodic",
            filter_query={"content.event": {"$exists": True}},
            limit=10
        )
        
        # Assert
        assert memories == expected_memories
        expected_filter = {
            "user_id": "test_user",
            "memory_type": "episodic",
            "content.event": {"$exists": True}
        }
        mock_collection.find.assert_called_once_with(expected_filter)
        mock_cursor.limit.assert_called_once_with(10)

    @patch('app.memory.mongodb_client.MongoClient')
    def test_create_conversation(self, mock_mongo_client_cls):
        """Test creating a conversation."""
        # Arrange
        mock_mongo_client = MagicMock()
        mock_database = MagicMock()
        mock_collection = MagicMock()
        mock_result = MagicMock()
        mock_result.inserted_id = "test_conversation_id"
        
        mock_mongo_client.__getitem__.return_value = mock_database
        mock_database.__getitem__.return_value = mock_collection
        mock_collection.insert_one.return_value = mock_result
        mock_mongo_client_cls.return_value = mock_mongo_client
        
        client = MongoDBClient()
        
        # Act
        conversation_id = client.create_conversation("test_user")
        
        # Assert
        assert conversation_id == "test_conversation_id"
        mock_collection.insert_one.assert_called_once()
        call_args = mock_collection.insert_one.call_args[0][0]
        assert call_args["user_id"] == "test_user"
        assert call_args["messages"] == []
        assert "created_at" in call_args

    @patch('app.memory.mongodb_client.MongoClient')
    def test_get_conversation(self, mock_mongo_client_cls):
        """Test getting a conversation."""
        # Arrange
        mock_mongo_client = MagicMock()
        mock_database = MagicMock()
        mock_collection = MagicMock()
        
        expected_conversation = {
            "_id": "test_conversation_id",
            "user_id": "test_user",
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ],
            "created_at": datetime.utcnow()
        }
        
        mock_collection.find_one.return_value = expected_conversation
        mock_mongo_client.__getitem__.return_value = mock_database
        mock_database.__getitem__.return_value = mock_collection
        mock_mongo_client_cls.return_value = mock_mongo_client
        
        client = MongoDBClient()
        
        # Act
        conversation = client.get_conversation("test_conversation_id")
        
        # Assert
        assert conversation == expected_conversation
        mock_collection.find_one.assert_called_once_with({"_id": "test_conversation_id"})

    @patch('app.memory.mongodb_client.MongoClient')
    def test_add_message_to_conversation(self, mock_mongo_client_cls):
        """Test adding message to conversation."""
        # Arrange
        mock_mongo_client = MagicMock()
        mock_database = MagicMock()
        mock_collection = MagicMock()
        
        mock_mongo_client.__getitem__.return_value = mock_database
        mock_database.__getitem__.return_value = mock_collection
        mock_mongo_client_cls.return_value = mock_mongo_client
        
        client = MongoDBClient()
        
        # Act
        client.add_message_to_conversation(
            conversation_id="test_conversation_id",
            message={"role": "user", "content": "Hello"}
        )
        
        # Assert
        mock_collection.update_one.assert_called_once()
        call_args = mock_collection.update_one.call_args
        assert call_args[0][0] == {"_id": "test_conversation_id"}
        assert "$push" in call_args[0][1]
        assert call_args[0][1]["$push"]["messages"]["role"] == "user"
        assert call_args[0][1]["$push"]["messages"]["content"] == "Hello"

    @patch('app.memory.mongodb_client.MongoClient')
    def test_get_user_conversations(self, mock_mongo_client_cls):
        """Test getting user conversations."""
        # Arrange
        mock_mongo_client = MagicMock()
        mock_database = MagicMock()
        mock_collection = MagicMock()
        mock_cursor = MagicMock()
        
        expected_conversations = [
            {"_id": "conv_1", "user_id": "test_user"},
            {"_id": "conv_2", "user_id": "test_user"}
        ]
        
        mock_cursor.limit.return_value.sort.return_value = expected_conversations
        mock_collection.find.return_value = mock_cursor
        mock_mongo_client.__getitem__.return_value = mock_database
        mock_database.__getitem__.return_value = mock_collection
        mock_mongo_client_cls.return_value = mock_mongo_client
        
        client = MongoDBClient()
        
        # Act
        conversations = client.get_user_conversations("test_user", limit=5)
        
        # Assert
        assert conversations == expected_conversations
        mock_collection.find.assert_called_once_with({"user_id": "test_user"})
        mock_cursor.limit.assert_called_once_with(5)

    @patch('app.memory.mongodb_client.MongoClient')
    def test_connection_error_handling(self, mock_mongo_client_cls):
        """Test MongoDB connection error handling."""
        # Arrange
        mock_mongo_client_cls.side_effect = pymongo.errors.ConnectionFailure("Connection failed")
        
        # Act & Assert
        with pytest.raises(pymongo.errors.ConnectionFailure):
            MongoDBClient()


class TestPineconeClient:
    """Tests for Pinecone client."""
    
    @patch('app.memory.pinecone_client.Pinecone')
    @patch('app.memory.pinecone_client.OpenAIEmbeddings')
    def test_init(self, mock_embeddings_cls, mock_pinecone_cls):
        """Test initialization of Pinecone client."""
        # Arrange
        mock_pinecone = MagicMock()
        mock_embeddings = MagicMock()
        mock_pinecone_cls.return_value = mock_pinecone
        mock_embeddings_cls.return_value = mock_embeddings
        
        # Act
        client = PineconeClient()
        
        # Assert
        assert client.pc == mock_pinecone
        assert client.embeddings == mock_embeddings
        mock_pinecone_cls.assert_called_once()
        mock_embeddings_cls.assert_called_once()

    @patch('app.memory.pinecone_client.Pinecone')
    @patch('app.memory.pinecone_client.OpenAIEmbeddings')
    def test_get_index(self, mock_embeddings_cls, mock_pinecone_cls):
        """Test getting Pinecone index."""
        # Arrange
        mock_pinecone = MagicMock()
        mock_index = MagicMock()
        mock_pinecone.Index.return_value = mock_index
        mock_pinecone_cls.return_value = mock_pinecone
        
        client = PineconeClient()
        
        # Act
        index = client.get_index()
        
        # Assert
        assert index == mock_index
        mock_pinecone.Index.assert_called_once()

    @patch('app.memory.pinecone_client.Pinecone')
    @patch('app.memory.pinecone_client.OpenAIEmbeddings')
    def test_store_memory(self, mock_embeddings_cls, mock_pinecone_cls):
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
        mock_embeddings.embed_query.assert_called_once_with("User likes coffee")
        mock_index.upsert.assert_called_once()
        
        # Check upsert call arguments
        upsert_args = mock_index.upsert.call_args[0][0]
        assert len(upsert_args) == 1
        vector_data = upsert_args[0]
        assert vector_data["values"] == [0.1, 0.2, 0.3]
        assert vector_data["metadata"]["user_id"] == "test_user"
        assert vector_data["metadata"]["text"] == "User likes coffee"
        assert vector_data["metadata"]["category"] == "preferences"

    @patch('app.memory.pinecone_client.Pinecone')
    @patch('app.memory.pinecone_client.OpenAIEmbeddings')
    def test_search_similar(self, mock_embeddings_cls, mock_pinecone_cls):
        """Test searching similar memories in Pinecone."""
        # Arrange
        mock_pinecone = MagicMock()
        mock_index = MagicMock()
        mock_embeddings = MagicMock()
        
        mock_pinecone.Index.return_value = mock_index
        mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
        
        # Mock Pinecone search results
        mock_search_results = {
            "matches": [
                {
                    "id": "memory_1",
                    "score": 0.95,
                    "metadata": {
                        "user_id": "test_user",
                        "text": "User likes coffee in the morning",
                        "category": "preferences"
                    }
                },
                {
                    "id": "memory_2",
                    "score": 0.87,
                    "metadata": {
                        "user_id": "test_user",
                        "text": "User prefers espresso",
                        "category": "preferences"
                    }
                }
            ]
        }
        mock_index.query.return_value = mock_search_results
        
        mock_pinecone_cls.return_value = mock_pinecone
        mock_embeddings_cls.return_value = mock_embeddings
        
        client = PineconeClient()
        
        # Act
        results = client.search_similar(
            user_id="test_user",
            query="coffee preferences",
            k=3
        )
        
        # Assert
        assert len(results) == 2
        
        # Check first result
        doc1, score1 = results[0]
        assert score1 == 0.95
        assert doc1.page_content == "User likes coffee in the morning"
        assert doc1.metadata["category"] == "preferences"
        
        # Check second result
        doc2, score2 = results[1]
        assert score2 == 0.87
        assert doc2.page_content == "User prefers espresso"
        
        # Verify search was called correctly
        mock_embeddings.embed_query.assert_called_once_with("coffee preferences")
        mock_index.query.assert_called_once()
        query_args = mock_index.query.call_args[1]
        assert query_args["vector"] == [0.1, 0.2, 0.3]
        assert query_args["top_k"] == 3
        assert query_args["include_metadata"] is True
        assert query_args["filter"]["user_id"] == "test_user"

    @patch('app.memory.pinecone_client.Pinecone')
    @patch('app.memory.pinecone_client.OpenAIEmbeddings')
    def test_search_similar_no_results(self, mock_embeddings_cls, mock_pinecone_cls):
        """Test searching with no results."""
        # Arrange
        mock_pinecone = MagicMock()
        mock_index = MagicMock()
        mock_embeddings = MagicMock()
        
        mock_pinecone.Index.return_value = mock_index
        mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_index.query.return_value = {"matches": []}
        
        mock_pinecone_cls.return_value = mock_pinecone
        mock_embeddings_cls.return_value = mock_embeddings
        
        client = PineconeClient()
        
        # Act
        results = client.search_similar(
            user_id="test_user",
            query="nonexistent query",
            k=3
        )
        
        # Assert
        assert results == []

    @patch('app.memory.pinecone_client.Pinecone')
    @patch('app.memory.pinecone_client.OpenAIEmbeddings')
    def test_embedding_error_handling(self, mock_embeddings_cls, mock_pinecone_cls):
        """Test handling of embedding errors."""
        # Arrange
        mock_embeddings = MagicMock()
        mock_embeddings.embed_query.side_effect = Exception("Embedding error")
        mock_embeddings_cls.return_value = mock_embeddings
        
        client = PineconeClient()
        
        # Act & Assert
        with pytest.raises(Exception):
            client.store_memory(
                user_id="test_user",
                text="Test text",
                metadata={}
            )

    @patch('app.memory.pinecone_client.Pinecone')
    @patch('app.memory.pinecone_client.OpenAIEmbeddings')
    def test_pinecone_connection_error(self, mock_embeddings_cls, mock_pinecone_cls):
        """Test Pinecone connection error handling."""
        # Arrange
        mock_pinecone_cls.side_effect = Exception("Pinecone connection failed")
        
        # Act & Assert
        with pytest.raises(Exception):
            PineconeClient()

    @patch('app.memory.pinecone_client.Pinecone')
    @patch('app.memory.pinecone_client.OpenAIEmbeddings')
    def test_delete_memory(self, mock_embeddings_cls, mock_pinecone_cls):
        """Test deleting memory from Pinecone."""
        # Arrange
        mock_pinecone = MagicMock()
        mock_index = MagicMock()
        mock_pinecone.Index.return_value = mock_index
        mock_pinecone_cls.return_value = mock_pinecone
        
        client = PineconeClient()
        
        # Act
        client.delete_memory("test_memory_id")
        
        # Assert
        mock_index.delete.assert_called_once_with(ids=["test_memory_id"])

    @patch('app.memory.pinecone_client.Pinecone')
    @patch('app.memory.pinecone_client.OpenAIEmbeddings')
    def test_get_index_stats(self, mock_embeddings_cls, mock_pinecone_cls):
        """Test getting index statistics."""
        # Arrange
        mock_pinecone = MagicMock()
        mock_index = MagicMock()
        mock_stats = {
            "dimension": 1536,
            "index_fullness": 0.1,
            "namespaces": {"": {"vector_count": 1000}},
            "total_vector_count": 1000
        }
        mock_index.describe_index_stats.return_value = mock_stats
        mock_pinecone.Index.return_value = mock_index
        mock_pinecone_cls.return_value = mock_pinecone
        
        client = PineconeClient()
        
        # Act
        stats = client.get_index_stats()
        
        # Assert
        assert stats == mock_stats
        mock_index.describe_index_stats.assert_called_once()
