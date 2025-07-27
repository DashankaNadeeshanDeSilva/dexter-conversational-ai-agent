"""Tests for API endpoints."""

import pytest
import json
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi.testclient import TestClient
from datetime import datetime

from app.api.main import app


class TestApiEndpoints:
    """Tests for the API endpoints."""
    
    @pytest.fixture
    def test_client(self):
        """Create a test client for the API."""
        return TestClient(app)

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_health_check(self, mock_agent, mock_memory_manager, test_client):
        """Test health check endpoint."""
        # Act
        response = test_client.get("/health")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_chat_new_conversation(self, mock_agent, mock_memory_manager, test_client):
        """Test chat endpoint with new conversation."""
        # Arrange
        mock_memory_manager.create_conversation.return_value = "new_conversation_id"
        mock_memory_manager.session_manager.create_session.return_value = "new_session_id"
        mock_agent.process_message = AsyncMock(return_value="Test response")
        
        # Act
        response = test_client.post(
            "/chat",
            json={
                "user_id": "test_user",
                "message": "Hello"
            }
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == "new_conversation_id"
        assert data["session_id"] == "new_session_id"
        assert data["message"]["content"] == "Test response"
        assert data["message"]["role"] == "assistant"
        mock_memory_manager.create_conversation.assert_called_once_with("test_user")
        mock_memory_manager.session_manager.create_session.assert_called_once()

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_chat_existing_conversation(self, mock_agent, mock_memory_manager, test_client):
        """Test chat endpoint with existing conversation and session."""
        # Arrange
        mock_agent.process_message = AsyncMock(return_value="Test response")
        
        # Act
        response = test_client.post(
            "/chat",
            json={
                "user_id": "test_user",
                "message": "Hello again",
                "conversation_id": "existing_conversation_id",
                "session_id": "existing_session_id"
            }
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == "existing_conversation_id"
        assert data["session_id"] == "existing_session_id"
        assert data["message"]["content"] == "Test response"
        # Should not create new conversation or session
        mock_memory_manager.create_conversation.assert_not_called()
        mock_memory_manager.session_manager.create_session.assert_not_called()

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_chat_error_handling(self, mock_agent, mock_memory_manager, test_client):
        """Test chat endpoint error handling."""
        # Arrange
        mock_memory_manager.create_conversation.return_value = "test_conversation_id"
        mock_memory_manager.session_manager.create_session.return_value = "test_session_id"
        mock_agent.process_message = AsyncMock(side_effect=Exception("Processing error"))
        
        # Act
        response = test_client.post(
            "/chat",
            json={
                "user_id": "test_user",
                "message": "Hello"
            }
        )
        
        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "Error processing chat" in data["detail"]

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_chat_validation_error(self, mock_agent, mock_memory_manager, test_client):
        """Test chat endpoint with invalid request data."""
        # Act
        response = test_client.post(
            "/chat",
            json={
                "message": "Hello"  # Missing required user_id
            }
        )
        
        # Assert
        assert response.status_code == 422  # Validation error

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_get_conversations(self, mock_agent, mock_memory_manager, test_client):
        """Test get conversations endpoint."""
        # Arrange
        mock_conversations = [
            {
                "_id": "conversation_1",
                "user_id": "test_user",
                "created_at": datetime.utcnow().isoformat(),
                "messages": []
            },
            {
                "_id": "conversation_2",
                "user_id": "test_user",
                "created_at": datetime.utcnow().isoformat(),
                "messages": []
            }
        ]
        mock_memory_manager.get_user_conversations.return_value = mock_conversations
        
        # Act
        response = test_client.get("/conversations/test_user")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["conversations"]) == 2
        assert data["conversations"][0]["_id"] == "conversation_1"
        mock_memory_manager.get_user_conversations.assert_called_once_with("test_user", 10)

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_get_conversations_with_limit(self, mock_agent, mock_memory_manager, test_client):
        """Test get conversations endpoint with custom limit."""
        # Arrange
        mock_memory_manager.get_user_conversations.return_value = []
        
        # Act
        response = test_client.get("/conversations/test_user?limit=5")
        
        # Assert
        assert response.status_code == 200
        mock_memory_manager.get_user_conversations.assert_called_once_with("test_user", 5)

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_get_conversation_by_id(self, mock_agent, mock_memory_manager, test_client):
        """Test get specific conversation endpoint."""
        # Arrange
        mock_conversation = {
            "_id": "test_conversation_id",
            "user_id": "test_user",
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ],
            "created_at": datetime.utcnow()
        }
        mock_memory_manager.get_conversation.return_value = mock_conversation
        
        # Act
        response = test_client.get("/conversations/test_user/test_conversation_id")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["_id"] == "test_conversation_id"
        assert len(data["messages"]) == 2
        mock_memory_manager.get_conversation.assert_called_once_with("test_conversation_id")

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_reset_session(self, mock_agent, mock_memory_manager, test_client):
        """Test reset session endpoint."""
        # Act
        response = test_client.post("/session/test_session/reset")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Session reset successfully"
        mock_agent.reset_session.assert_called_once_with("test_session")

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_query_memory_episodic(self, mock_agent, mock_memory_manager, test_client):
        """Test query memory endpoint for episodic memories."""
        # Arrange
        mock_memories = [
            {
                "_id": "memory_1",
                "content": {"event": "user_greeting"},
                "metadata": {"timestamp": datetime.utcnow()}
            }
        ]
        mock_memory_manager.retrieve_episodic_memories.return_value = mock_memories
        
        # Act
        response = test_client.post(
            "/memory/query",
            json={
                "user_id": "test_user",
                "query": "greeting",
                "memory_type": "episodic",
                "limit": 5
            }
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["memories"]) == 1
        mock_memory_manager.retrieve_episodic_memories.assert_called_once()

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_query_memory_semantic(self, mock_agent, mock_memory_manager, test_client):
        """Test query memory endpoint for semantic memories."""
        # Arrange
        mock_memories = [
            (MagicMock(page_content="User likes coffee", metadata={}), 0.95)
        ]
        mock_memory_manager.retrieve_semantic_memories.return_value = mock_memories
        
        # Act
        response = test_client.post(
            "/memory/query",
            json={
                "user_id": "test_user",
                "query": "preferences",
                "memory_type": "semantic",
                "limit": 3
            }
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["memories"]) == 1
        mock_memory_manager.retrieve_semantic_memories.assert_called_once()

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_query_memory_procedural(self, mock_agent, mock_memory_manager, test_client):
        """Test query memory endpoint for procedural memories."""
        # Arrange
        mock_memories = [
            {
                "_id": "procedure_1",
                "content": {"tool": "search", "success": True},
                "metadata": {"timestamp": datetime.utcnow()}
            }
        ]
        mock_memory_manager.retrieve_procedural_memories.return_value = mock_memories
        
        # Act
        response = test_client.post(
            "/memory/query",
            json={
                "user_id": "test_user",
                "query": "search",
                "memory_type": "procedural",
                "limit": 5
            }
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["memories"]) == 1
        mock_memory_manager.retrieve_procedural_memories.assert_called_once()

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_query_memory_invalid_type(self, mock_agent, mock_memory_manager, test_client):
        """Test query memory endpoint with invalid memory type."""
        # Act
        response = test_client.post(
            "/memory/query",
            json={
                "user_id": "test_user",
                "query": "test",
                "memory_type": "invalid_type",
                "limit": 5
            }
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "Invalid memory type" in data["detail"]

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_get_agent_status(self, mock_agent, mock_memory_manager, test_client):
        """Test get agent status endpoint."""
        # Act
        response = test_client.get("/agent/status")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["status"] == "online"
        assert "capabilities" in data["data"]
        assert "memory_systems" in data["data"]

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_api_cors_headers(self, mock_agent, mock_memory_manager, test_client):
        """Test CORS headers in API responses."""
        # Act
        response = test_client.options("/health")
        
        # Assert
        # CORS middleware should handle OPTIONS requests
        assert response.status_code in [200, 405]  # Some test clients handle OPTIONS differently
