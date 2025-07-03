"""Tests for API endpoints."""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from datetime import datetime

from app.api.main import app

@pytest.fixture
def test_client():
    """Create a test client for the API."""
    return TestClient(app)

@pytest.fixture
def mock_memory_manager():
    """Create a mock memory manager."""
    mock = MagicMock()
    return mock

@pytest.fixture
def mock_agent():
    """Create a mock agent."""
    mock = MagicMock()
    return mock

class TestApiEndpoints:
    """Tests for the API endpoints."""
    
    def test_health_check(self, test_client):
        """Test health check endpoint."""
        # Act
        response = test_client.get("/health")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    @patch('app.api.main.agent')
    def test_chat(self, mock_agent, test_client):
        """Test chat endpoint."""
        # Arrange
        mock_agent.process_message.return_value = "Test response"
        
        # Act
        response = test_client.post(
            "/chat",
            json={
                "user_id": "test-user",
                "message": "Hello"
            }
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "session_id" in data
        assert data["message"]["content"] == "Test response"
        assert data["message"]["role"] == "assistant"
        
    @patch('app.api.main.memory_manager')
    def test_get_conversations(self, mock_memory_manager, test_client):
        """Test get conversations endpoint."""
        # Arrange
        mock_memory_manager.get_user_conversations.return_value = [
            {
                "_id": "test-conversation-id",
                "user_id": "test-user",
                "created_at": datetime.utcnow().isoformat(),
                "messages": []
            }
        ]
        
        # Act
        response = test_client.get("/conversations/test-user")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["conversations"]) == 1
        assert data["conversations"][0]["_id"] == "test-conversation-id"
        
    @patch('app.api.main.agent')
    def test_reset_session(self, mock_agent, test_client):
        """Test reset session endpoint."""
        # Act
        response = test_client.post("/session/test-session/reset")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        mock_agent.reset_session.assert_called_once_with("test-session")
