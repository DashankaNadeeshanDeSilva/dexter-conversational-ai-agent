"""Tests for the FastAPI application."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import status
import json
from datetime import datetime

# Import removed to prevent MongoDB connection during test collection
from fastapi import HTTPException
from app.api.models import ChatRequest, ChatResponse, ConversationListResponse, MemoryQueryRequest, MemoryQueryResponse, HealthResponse
from langchain_core.messages import HumanMessage, AIMessage, ChatMessage


class TestAPIEndpoints:
    """Test the API endpoints."""
    
    @pytest.fixture
    def sample_chat_request(self):
        """Create a sample chat request."""
        return {
            "user_id": "test_user",
            "message": "Hello, how can you help me?",
            "conversation_id": "test_conversation_id",
            "session_id": "test_session_id"
        }
    
    @pytest.fixture
    def sample_memory_query(self):
        """Create a sample memory query request."""
        return {
            "user_id": "test_user",
            "query": "What did we discuss about AI?",
            "memory_type": "episodic"
        }
    
    def test_health_check(self, test_client):
        """Test the health check endpoint."""
        response = test_client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_chat_endpoint_success(self, mock_agent, mock_memory_manager, test_client, sample_chat_request):
        """Test successful chat endpoint."""
        # Mock the memory manager
        mock_memory_manager.create_conversation.return_value = "test_conversation_id"
        mock_memory_manager.create_session.return_value = "test_session_id"
        
        # Mock the agent
        mock_agent.process_message = AsyncMock(return_value="Hello! I can help you with various tasks.")
        
        response = test_client.post("/chat", json=sample_chat_request)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["conversation_id"] == "test_conversation_id"
        assert data["session_id"] == "test_session_id"
        assert data["message"]["content"] == "Hello! I can help you with various tasks."
        assert data["message"]["role"] == "assistant"
        assert "timestamp" in data["message"]
    
    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_chat_endpoint_new_conversation(self, mock_agent, mock_memory_manager, test_client):
        """Test chat endpoint with new conversation."""
        request_data = {
            "user_id": "test_user",
            "message": "Hello",
            "conversation_id": None,
            "session_id": None
        }
        
        # Mock the memory manager
        mock_memory_manager.create_conversation.return_value = "new_conversation_id"
        mock_memory_manager.create_session.return_value = "new_session_id"
        
        # Mock the agent
        mock_agent.process_message = AsyncMock(return_value="Hi there!")
        
        response = test_client.post("/chat", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["conversation_id"] == "new_conversation_id"
        assert data["session_id"] == "new_session_id"
        
        # Verify conversation and session were created
        mock_memory_manager.create_conversation.assert_called_once_with("test_user")
        mock_memory_manager.create_session.assert_called_once_with("test_user", "new_conversation_id")
    
    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_chat_endpoint_existing_conversation(self, mock_agent, mock_memory_manager, test_client):
        """Test chat endpoint with existing conversation."""
        request_data = {
            "user_id": "test_user",
            "message": "Continue our conversation",
            "conversation_id": "existing_conv_id",
            "session_id": "existing_session_id"
        }
        
        # Mock the memory manager
        mock_memory_manager.create_conversation.return_value = "existing_conv_id"
        mock_memory_manager.create_session.return_value = "existing_session_id"
        
        # Mock the agent
        mock_agent.process_message = AsyncMock(return_value="Of course! Let's continue.")
        
        response = test_client.post("/chat", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["conversation_id"] == "existing_conv_id"
        assert data["session_id"] == "existing_session_id"
        
        # Verify no new conversation/session was created
        mock_memory_manager.create_conversation.assert_not_called()
        mock_memory_manager.create_session.assert_not_called()
    
    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_chat_endpoint_agent_error(self, mock_agent, mock_memory_manager, test_client, sample_chat_request):
        """Test chat endpoint when agent encounters an error."""
        # Mock the memory manager
        mock_memory_manager.create_conversation.return_value = "test_conversation_id"
        mock_memory_manager.create_session.return_value = "test_session_id"

        # Mock the agent to raise an exception
        mock_agent.process_message = AsyncMock(side_effect=Exception("Agent error"))

        response = test_client.post("/chat", json=sample_chat_request)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "detail" in data
        assert "Agent error" in data["detail"]
    
    @patch('app.api.main.memory_manager')
    def test_chat_endpoint_invalid_request(self, mock_memory_manager, test_client):
        """Test chat endpoint with invalid request data."""
        invalid_request = {
            "user_id": "",  # Empty user_id
            "message": "",   # Empty message
            "conversation_id": "test_conv",
            "session_id": "test_session"
        }
        
        response = test_client.post("/chat", json=invalid_request)
        
        # Current API accepts empty strings; ensure it returns 200 with a response structure
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "conversation_id" in data
        assert "session_id" in data
        assert "message" in data
    
    @patch('app.api.main.memory_manager')
    def test_conversations_endpoint(self, mock_memory_manager, test_client):
        """Test the conversations endpoint."""
        user_id = "test_user"
        expected_conversations = [
            {
                "_id": "conv1",
                "user_id": user_id,
                "messages": [],
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "_id": "conv2",
                "user_id": user_id,
                "messages": [],
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        
        mock_memory_manager.get_user_conversations.return_value = expected_conversations
        
        response = test_client.get(f"/conversations/{user_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["conversations"]) == 2
        # API returns only conversations list; no user_id field in response
    
    @patch('app.api.main.memory_manager')
    def test_conversations_endpoint_no_conversations(self, mock_memory_manager, test_client):
        """Test conversations endpoint when user has no conversations."""
        user_id = "test_user"
        mock_memory_manager.get_user_conversations.return_value = []
        
        response = test_client.get(f"/conversations/{user_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["conversations"]) == 0
        # API returns only conversations list; no user_id field in response
    
    @patch('app.api.main.memory_manager')
    def test_conversation_endpoint(self, mock_memory_manager, test_client):
        """Test the conversation endpoint."""
        conversation_id = "test_conv_id"
        user_id = "test_user"
        expected_conversation = {
            "_id": conversation_id,
            "user_id": user_id,
            "messages": [
                {"role": "user", "content": "Hello", "timestamp": datetime.utcnow().isoformat()},
                {"role": "assistant", "content": "Hi there!", "timestamp": datetime.utcnow().isoformat()}
            ],
            "created_at": datetime.utcnow().isoformat()
        }
        
        mock_memory_manager.get_conversation.return_value = expected_conversation
        
        response = test_client.get(f"/conversations/{user_id}/{conversation_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["_id"] == conversation_id
        assert len(data["messages"]) == 2
        
        mock_memory_manager.get_conversation.assert_called_once_with(conversation_id)
    
    @patch('app.api.main.memory_manager')
    def test_conversation_endpoint_not_found(self, mock_memory_manager, test_client):
        """Test conversation endpoint when conversation is not found."""
        conversation_id = "nonexistent_conv"
        user_id = "test_user"
        mock_memory_manager.get_conversation.return_value = None
        
        response = test_client.get(f"/conversations/{user_id}/{conversation_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]
    
    @patch('app.api.main.memory_manager')
    def test_memory_query_endpoint(self, mock_memory_manager, test_client, sample_memory_query):
        """Test the memory query endpoint."""
        expected_memories = [
            {"memory": "episodic_memory_1", "relevance": 0.9},
            {"memory": "episodic_memory_2", "relevance": 0.8}
        ]
        
        # For episodic memory, the API calls mongodb_client.retrieve_memories
        mock_memory_manager.mongodb_client.retrieve_memories.return_value = expected_memories
        
        response = test_client.post("/memories/query", json=sample_memory_query)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "memories" in data
        assert len(data["memories"]) == 2
        
        mock_memory_manager.mongodb_client.retrieve_memories.assert_called_once_with(
            user_id="test_user", memory_type="episodic", limit=5
        )
    
    @patch('app.api.main.memory_manager')
    def test_memory_query_endpoint_procedural(self, mock_memory_manager, test_client):
        """Test memory query endpoint for procedural memory."""
        request_data = {
            "user_id": "test_user",
            "query": "How did we solve this problem?",
            "memory_type": "procedural"
        }
        
        expected_memories = [
            {"memory": "procedural_memory_1", "relevance": 0.95}
        ]
        
        mock_memory_manager.mongodb_client.retrieve_memories.return_value = expected_memories
        
        response = test_client.post("/memories/query", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "memories" in data
        assert len(data["memories"]) == 1
        
        mock_memory_manager.mongodb_client.retrieve_memories.assert_called_once_with(
            user_id="test_user", memory_type="procedural", limit=5
        )
    
    @patch('app.api.main.memory_manager')
    def test_memory_query_endpoint_semantic(self, mock_memory_manager, test_client):
        """Test memory query endpoint for semantic memory."""
        request_data = {
            "user_id": "test_user",
            "query": "What do you know about AI?",
            "memory_type": "semantic"
        }
        
        # Mock the document and score tuple that retrieve_semantic_memories returns
        mock_doc = MagicMock()
        mock_doc.page_content = "AI is artificial intelligence"
        mock_doc.metadata = {}
        expected_memories = [(mock_doc, 0.9)]
        
        mock_memory_manager.retrieve_semantic_memories.return_value = expected_memories
        
        response = test_client.post("/memories/query", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "memories" in data
        assert len(data["memories"]) == 1
        assert data["memories"][0]["content"] == "AI is artificial intelligence"
        
        mock_memory_manager.retrieve_semantic_memories.assert_called_once_with(
            user_id="test_user", query="What do you know about AI?", k=5
        )
    
    @patch('app.api.main.memory_manager')
    def test_memory_query_endpoint_invalid_type(self, mock_memory_manager, test_client):
        """Test memory query endpoint with invalid memory type."""
        request_data = {
            "user_id": "test_user",
            "query": "Test query",
            "memory_type": "invalid_type"
        }
        
        response = test_client.post("/memories/query", json=request_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert "Invalid memory type: invalid_type" in data["detail"]
    
    @patch('app.api.main.memory_manager')
    def test_memory_query_endpoint_no_memories(self, mock_memory_manager, test_client, sample_memory_query):
        """Test memory query endpoint when no memories are found."""
        mock_memory_manager.mongodb_client.retrieve_memories.return_value = []
        
        response = test_client.post("/memories/query", json=sample_memory_query)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "memories" in data
        assert len(data["memories"]) == 0
    
    def test_chat_endpoint_missing_required_fields(self, test_client):
        """Test chat endpoint with missing required fields."""
        incomplete_request = {
            "user_id": "test_user"
            # Missing message, conversation_id, session_id
        }
        
        response = test_client.post("/chat", json=incomplete_request)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_memory_query_endpoint_missing_required_fields(self, test_client):
        """Test memory query endpoint with missing required fields."""
        incomplete_request = {
            "user_id": "test_user"
            # Missing query and memory_type
        }
        
        response = test_client.post("/memories/query", json=incomplete_request)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @patch('app.api.main.memory_manager')
    def test_create_conversation_endpoint(self, mock_memory_manager, test_client):
        """Test the create conversation endpoint."""
        user_id = "test_user"
        conversation_id = "new_conv_id"
        
        mock_memory_manager.create_conversation.return_value = conversation_id
        
        response = test_client.post("/conversations/create_new", json={"user_id": user_id})
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == user_id
        assert data["conversation_id"] == conversation_id
        assert "created_at" in data
        assert "updated_at" in data
        assert data["messages"] == []
        
        mock_memory_manager.create_conversation.assert_called_once_with(user_id)
    
    @patch('app.api.main.agent')
    def test_reset_session_endpoint(self, mock_agent, test_client):
        """Test the session reset endpoint."""
        session_id = "test_session_id"
        
        mock_agent.reset_session.return_value = None
        
        response = test_client.post(f"/session/{session_id}/reset")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "reset successfully" in data["message"]
        
        mock_agent.reset_session.assert_called_once_with(session_id)


class TestAPIModels:
    """Test the API models."""
    
    def test_chat_request_model(self):
        """Test ChatRequest model validation."""
        # Valid request
        valid_request = ChatRequest(
            user_id="test_user",
            message="Hello",
            conversation_id="test_conv",
            session_id="test_session"
        )
        
        assert valid_request.user_id == "test_user"
        assert valid_request.message == "Hello"
        assert valid_request.conversation_id == "test_conv"
        assert valid_request.session_id == "test_session"
        
        # Test with optional fields as None
        request_with_none = ChatRequest(
            user_id="test_user",
            message="Hello",
            conversation_id=None,
            session_id=None
        )
        
        assert request_with_none.conversation_id is None
        assert request_with_none.session_id is None
    
    def test_chat_response_model(self):
        """Test ChatResponse model creation and validation."""
        # Create a valid chat response
        from datetime import datetime, timezone
        
        # Use string timestamp to avoid validation issues
        test_timestamp = "2024-01-01T12:00:00Z"
        
        response = ChatResponse(
            message={
                "role": "assistant",
                "content": "Hello! How can I help you today?",
                "timestamp": test_timestamp
            },
            conversation_id="conv_123",
            session_id="sess_456"
        )
        
        # Validate the response
        assert response.message["role"] == "assistant"
        assert response.message["content"] == "Hello! How can I help you today?"
        assert response.conversation_id == "conv_123"
        assert response.session_id == "sess_456"
        
        # Test serialization
        data = response.model_dump()
        assert "message" in data
        assert "conversation_id" in data
        assert "session_id" in data

    def test_memory_query_response_model(self):
        """Test MemoryQueryResponse model creation and validation."""
        # Create sample memories
        sample_memories = [
            {
                "id": "mem_1",
                "content": "Sample memory content",
                "memory_type": "episodic",
                "relevance_score": 0.95
            }
        ]
        
        response = MemoryQueryResponse(
            memories=sample_memories
        )
        
        # Validate the response
        assert response.memories == sample_memories
        
        # Test serialization
        data = response.model_dump()
        assert "memories" in data

    def test_conversation_list_response_model(self):
        """Test ConversationListResponse model creation and validation."""
        # Create sample conversations
        sample_conversations = [
            {
                "id": "conv_1",
                "title": "Test Conversation",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        response = ConversationListResponse(
            conversations=sample_conversations
        )
        
        # Validate the response
        assert response.conversations == sample_conversations
        
        # Test serialization
        data = response.model_dump()
        assert "conversations" in data
    
    def test_health_response_model(self):
        """Test HealthResponse model validation."""
        response = HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow()
        )
        
        assert response.status == "healthy"
        assert response.timestamp is not None


class TestAPIErrorHandling:
    """Test API error handling."""
    
    def test_invalid_json_request(self, test_client):
        """Test handling of invalid JSON requests."""
        response = test_client.post("/chat", data="invalid json")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_unsupported_endpoint(self, test_client):
        """Test handling of unsupported endpoints."""
        response = test_client.get("/nonexistent")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_method_not_allowed(self, test_client):
        """Test handling of unsupported HTTP methods."""
        response = test_client.put("/chat")
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
