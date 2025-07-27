"""Integration tests for the entire system."""

import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import json

from app.api.main import app
from app.agent.agent import ReActAgent
from app.memory.memory_manager import MemoryManager


class TestEndToEndIntegration:
    """End-to-end integration tests."""
    
    @pytest.fixture
    def test_client(self):
        """Create test client."""
        return TestClient(app)

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_complete_conversation_flow(self, mock_agent, mock_memory_manager, test_client):
        """Test complete conversation flow from API to agent."""
        # Arrange
        conversation_id = "test_conversation_123"
        session_id = "test_session_456"
        
        # Mock memory manager responses
        mock_memory_manager.create_conversation.return_value = conversation_id
        mock_memory_manager.session_manager.create_session.return_value = session_id
        
        # Mock agent responses
        mock_agent.process_message = AsyncMock(side_effect=[
            "Hello! How can I help you today?",
            "I found some great coffee options for you!",
            "Your appointment has been scheduled successfully."
        ])
        
        # Act & Assert - Multiple conversation turns
        
        # First message
        response1 = test_client.post("/chat", json={
            "user_id": "test_user",
            "message": "Hello"
        })
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["conversation_id"] == conversation_id
        assert data1["session_id"] == session_id
        assert "Hello! How can I help you today?" in data1["message"]["content"]
        
        # Second message (using same conversation)
        response2 = test_client.post("/chat", json={
            "user_id": "test_user",
            "message": "I'm looking for coffee recommendations",
            "conversation_id": conversation_id,
            "session_id": session_id
        })
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["conversation_id"] == conversation_id
        assert "coffee options" in data2["message"]["content"]
        
        # Third message (appointment booking)
        response3 = test_client.post("/chat", json={
            "user_id": "test_user",
            "message": "Schedule an appointment with Dr. Smith tomorrow at 2 PM",
            "conversation_id": conversation_id,
            "session_id": session_id
        })
        assert response3.status_code == 200
        data3 = response3.json()
        assert "appointment has been scheduled" in data3["message"]["content"]
        
        # Verify agent was called correctly
        assert mock_agent.process_message.call_count == 3

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_memory_persistence_across_sessions(self, mock_agent, mock_memory_manager, test_client):
        """Test that memory persists across different sessions."""
        # Arrange
        user_id = "persistent_user"
        
        # First conversation
        mock_memory_manager.create_conversation.return_value = "conv_1"
        mock_memory_manager.session_manager.create_session.return_value = "session_1"
        mock_agent.process_message = AsyncMock(return_value="I'll remember your coffee preference.")
        
        # Act - First conversation
        response1 = test_client.post("/chat", json={
            "user_id": user_id,
            "message": "I love espresso in the morning"
        })
        
        # Arrange - Second conversation (new session)
        mock_memory_manager.create_conversation.return_value = "conv_2"
        mock_memory_manager.session_manager.create_session.return_value = "session_2"
        mock_agent.process_message = AsyncMock(return_value="I remember you like espresso! Here are some recommendations.")
        
        # Act - Second conversation
        response2 = test_client.post("/chat", json={
            "user_id": user_id,
            "message": "Can you recommend some coffee?"
        })
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify memory operations were called
        assert mock_memory_manager.create_conversation.call_count == 2
        assert mock_agent.process_message.call_count == 2

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_error_recovery_and_graceful_degradation(self, mock_agent, mock_memory_manager, test_client):
        """Test system behavior under error conditions."""
        # Arrange
        mock_memory_manager.create_conversation.return_value = "test_conv"
        mock_memory_manager.session_manager.create_session.return_value = "test_session"
        
        # Simulate agent error
        mock_agent.process_message = AsyncMock(side_effect=Exception("Agent processing error"))
        
        # Act
        response = test_client.post("/chat", json={
            "user_id": "test_user",
            "message": "This should cause an error"
        })
        
        # Assert
        assert response.status_code == 500
        assert "Error processing chat" in response.json()["detail"]

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_concurrent_user_sessions(self, mock_agent, mock_memory_manager, test_client):
        """Test handling multiple concurrent user sessions."""
        # Arrange
        users = ["user_1", "user_2", "user_3"]
        
        # Mock different responses for different users
        mock_memory_manager.create_conversation.side_effect = [f"conv_{i}" for i in range(1, 4)]
        mock_memory_manager.session_manager.create_session.side_effect = [f"session_{i}" for i in range(1, 4)]
        mock_agent.process_message = AsyncMock(side_effect=[
            f"Hello {user}!" for user in users
        ])
        
        # Act - Simulate concurrent requests
        responses = []
        for i, user in enumerate(users):
            response = test_client.post("/chat", json={
                "user_id": user,
                "message": f"Hello from {user}"
            })
            responses.append(response)
        
        # Assert
        for i, response in enumerate(responses):
            assert response.status_code == 200
            data = response.json()
            assert data["conversation_id"] == f"conv_{i+1}"
            assert data["session_id"] == f"session_{i+1}"

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_memory_query_and_retrieval(self, mock_agent, mock_memory_manager, test_client):
        """Test memory querying functionality."""
        # Arrange
        mock_episodic_memories = [
            {
                "_id": "memory_1",
                "content": {"event": "user_greeting", "message": "Hello"},
                "metadata": {"timestamp": datetime.utcnow()}
            }
        ]
        mock_semantic_memories = [
            (MagicMock(page_content="User likes coffee", metadata={}), 0.95)
        ]
        mock_procedural_memories = [
            {
                "_id": "procedure_1",
                "content": {"tool": "search", "success": True},
                "metadata": {"timestamp": datetime.utcnow()}
            }
        ]
        
        mock_memory_manager.retrieve_episodic_memories.return_value = mock_episodic_memories
        mock_memory_manager.retrieve_semantic_memories.return_value = mock_semantic_memories
        mock_memory_manager.retrieve_procedural_memories.return_value = mock_procedural_memories
        
        # Act & Assert - Test episodic memory query
        response1 = test_client.post("/memory/query", json={
            "user_id": "test_user",
            "query": "greeting",
            "memory_type": "episodic"
        })
        assert response1.status_code == 200
        assert len(response1.json()["memories"]) == 1
        
        # Act & Assert - Test semantic memory query
        response2 = test_client.post("/memory/query", json={
            "user_id": "test_user",
            "query": "coffee",
            "memory_type": "semantic"
        })
        assert response2.status_code == 200
        assert len(response2.json()["memories"]) == 1
        
        # Act & Assert - Test procedural memory query
        response3 = test_client.post("/memory/query", json={
            "user_id": "test_user",
            "query": "search",
            "memory_type": "procedural"
        })
        assert response3.status_code == 200
        assert len(response3.json()["memories"]) == 1

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_session_management_lifecycle(self, mock_agent, mock_memory_manager, test_client):
        """Test complete session lifecycle management."""
        # Arrange
        user_id = "lifecycle_user"
        conversation_id = "lifecycle_conv"
        session_id = "lifecycle_session"
        
        mock_memory_manager.create_conversation.return_value = conversation_id
        mock_memory_manager.session_manager.create_session.return_value = session_id
        mock_agent.process_message = AsyncMock(return_value="Session started!")
        
        # Act & Assert - Start session with chat
        response1 = test_client.post("/chat", json={
            "user_id": user_id,
            "message": "Start new session"
        })
        assert response1.status_code == 200
        assert response1.json()["session_id"] == session_id
        
        # Act & Assert - Continue session
        mock_agent.process_message = AsyncMock(return_value="Session continuing...")
        response2 = test_client.post("/chat", json={
            "user_id": user_id,
            "message": "Continue session",
            "conversation_id": conversation_id,
            "session_id": session_id
        })
        assert response2.status_code == 200
        assert response2.json()["session_id"] == session_id
        
        # Act & Assert - Reset session
        response3 = test_client.post(f"/session/{session_id}/reset")
        assert response3.status_code == 200
        assert response3.json()["success"] is True
        mock_agent.reset_session.assert_called_once_with(session_id)

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_conversation_history_retrieval(self, mock_agent, mock_memory_manager, test_client):
        """Test conversation history retrieval."""
        # Arrange
        user_id = "history_user"
        mock_conversations = [
            {
                "_id": "conv_1",
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there!"}
                ]
            },
            {
                "_id": "conv_2",
                "user_id": user_id,
                "created_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                "messages": [
                    {"role": "user", "content": "How are you?"},
                    {"role": "assistant", "content": "I'm doing well!"}
                ]
            }
        ]
        mock_conversation_detail = {
            "_id": "conv_1",
            "user_id": user_id,
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
        }
        
        mock_memory_manager.get_user_conversations.return_value = mock_conversations
        mock_memory_manager.get_conversation.return_value = mock_conversation_detail
        
        # Act & Assert - Get all conversations
        response1 = test_client.get(f"/conversations/{user_id}")
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1["conversations"]) == 2
        assert data1["conversations"][0]["_id"] == "conv_1"
        
        # Act & Assert - Get specific conversation
        response2 = test_client.get(f"/conversations/{user_id}/conv_1")
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["_id"] == "conv_1"
        assert len(data2["messages"]) == 2

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_agent_status_monitoring(self, mock_agent, mock_memory_manager, test_client):
        """Test agent status and health monitoring."""
        # Act
        response = test_client.get("/agent/status")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "online"
        assert "capabilities" in data["data"]
        assert "memory_systems" in data["data"]
        assert "performance_metrics" in data["data"]
        
        # Verify expected capabilities
        capabilities = data["data"]["capabilities"]
        expected_capabilities = ["product_search", "appointment_booking", "semantic_retrieval", "web_search"]
        for capability in expected_capabilities:
            assert capability in capabilities


class TestStressAndPerformance:
    """Stress and performance tests."""
    
    @pytest.fixture
    def test_client(self):
        """Create test client."""
        return TestClient(app)

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_high_frequency_requests(self, mock_agent, mock_memory_manager, test_client):
        """Test system behavior under high frequency requests."""
        # Arrange
        mock_memory_manager.create_conversation.return_value = "stress_conv"
        mock_memory_manager.session_manager.create_session.return_value = "stress_session"
        mock_agent.process_message = AsyncMock(return_value="Stress test response")
        
        # Act - Send multiple rapid requests
        responses = []
        for i in range(10):
            response = test_client.post("/chat", json={
                "user_id": f"stress_user_{i}",
                "message": f"Stress test message {i}"
            })
            responses.append(response)
        
        # Assert
        for i, response in enumerate(responses):
            assert response.status_code == 200
            assert f"stress_user_{i}" in str(mock_agent.process_message.call_args_list[i])

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_large_conversation_context(self, mock_agent, mock_memory_manager, test_client):
        """Test handling of large conversation contexts."""
        # Arrange
        conversation_id = "large_conv"
        session_id = "large_session"
        
        mock_memory_manager.create_conversation.return_value = conversation_id
        mock_memory_manager.session_manager.create_session.return_value = session_id
        mock_agent.process_message = AsyncMock(return_value="Handling large context")
        
        # Create a very long message
        long_message = "This is a very long message. " * 1000  # ~30KB message
        
        # Act
        response = test_client.post("/chat", json={
            "user_id": "large_context_user",
            "message": long_message
        })
        
        # Assert
        assert response.status_code == 200
        # Verify the agent was called with the long message
        mock_agent.process_message.assert_called_once()
        call_args = mock_agent.process_message.call_args
        assert call_args[1]["message"] == long_message

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_memory_query_performance(self, mock_agent, mock_memory_manager, test_client):
        """Test performance of memory query operations."""
        # Arrange
        # Simulate large memory result sets
        large_episodic_memories = [
            {
                "_id": f"memory_{i}",
                "content": {"event": f"event_{i}"},
                "metadata": {"timestamp": datetime.utcnow()}
            }
            for i in range(100)
        ]
        mock_memory_manager.retrieve_episodic_memories.return_value = large_episodic_memories
        
        # Act
        response = test_client.post("/memory/query", json={
            "user_id": "performance_user",
            "query": "large query",
            "memory_type": "episodic",
            "limit": 100
        })
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["memories"]) == 100

    def test_health_check_performance(self, test_client):
        """Test health check endpoint performance."""
        # Act - Multiple health checks
        responses = []
        for _ in range(5):
            response = test_client.get("/health")
            responses.append(response)
        
        # Assert
        for response in responses:
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"
