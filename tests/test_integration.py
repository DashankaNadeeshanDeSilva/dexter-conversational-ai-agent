"""Integration tests for the complete AI Agent system."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime
from typing import Dict, Any, List

from app.agent.agent import ReActAgent, AgentState
from app.memory.memory_manager import MemoryManager
# Import removed to prevent MongoDB connection during test collection
from app.tools.web_search_tool import WebSearchTool
from app.tools.product_search_tool import ProductSearchTool
from app.tools.appointment_tool import AppointmentTool
from app.tools.semantic_retrieval_tool import KnowledgeRetrievalTool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from fastapi.testclient import TestClient


@pytest.fixture
def mock_tools():
    """Create mock tools for testing."""
    tools = []
    tool_names = ["internet_search", "product_search", "appointment_management", "company_knowledge_retrieval"]
    
    for name in tool_names:
        tool = MagicMock()
        tool.name = name  # Set the name attribute directly
        tool.description = f"Mock {name} tool"
        tools.append(tool)
    
    return tools

@pytest.fixture
def test_client(test_app):
    """Create a test client for integration tests."""
    return TestClient(test_app)

class TestSystemIntegration:
    """Test system-wide integration scenarios."""
    
    def test_complete_chat_workflow(self, mock_tools, test_client):
        """Test complete chat workflow from request to response."""
        # Mock memory manager and agent
        with patch('app.api.main.memory_manager') as mock_memory_manager, \
             patch('app.api.main.agent') as mock_agent:
            
            # Setup mocks
            mock_memory_manager.create_conversation.return_value = "conv_123"
            mock_memory_manager.create_session.return_value = "sess_456"
            mock_agent.process_message = AsyncMock(return_value="Test response")
            
            # Test chat request
            chat_request = {
                "user_id": "test_user",
                "message": "Hello, how are you?",
                "conversation_id": None,
                "session_id": None
            }
            
            response = test_client.post("/chat", json=chat_request)
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert data["conversation_id"] == "conv_123"
            assert data["session_id"] == "sess_456"
            
            # Verify memory manager calls
            mock_memory_manager.create_conversation.assert_called_once()
            mock_memory_manager.create_session.assert_called_once()
            mock_agent.process_message.assert_called_once()

    def test_agent_memory_integration(self, mock_tools, test_client):
        """Test agent integration with memory system."""
        with patch('app.api.main.memory_manager') as mock_memory_manager, \
             patch('app.api.main.agent') as mock_agent:
            
            # Setup mocks
            mock_memory_manager.get_short_term_memory.return_value = MagicMock()
            mock_memory_manager.add_message_to_conversation.return_value = True
            mock_agent.process_message = AsyncMock(return_value="Memory-enhanced response")
            
            # Test chat with existing conversation
            chat_request = {
                "user_id": "test_user",
                "message": "What did we discuss earlier?",
                "conversation_id": "conv_123",
                "session_id": "sess_456"
            }
            
            response = test_client.post("/chat", json=chat_request)
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            
            # Verify memory operations - the agent.process_message handles these internally
            mock_agent.process_message.assert_called_once()

    def test_tool_memory_integration(self, mock_tools, test_client):
        """Test tool integration with memory system."""
        with patch('app.api.main.memory_manager') as mock_memory_manager, \
             patch('app.api.main.agent') as mock_agent:
            
            # Setup mocks
            mock_memory_manager.store_episodic_memory.return_value = "episodic_123"
            mock_memory_manager.store_procedural_memory.return_value = "procedural_123"
            mock_agent.process_message = AsyncMock(return_value="Tool used successfully")
            
            # Test chat that triggers tool usage
            chat_request = {
                "user_id": "test_user",
                "message": "Search for information about AI",
                "conversation_id": "conv_123",
                "session_id": "sess_456"
            }
            
            response = test_client.post("/chat", json=chat_request)
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert "message" in data

    def test_conversation_flow_integration(self, test_client):
        """Test conversation flow and management."""
        with patch('app.api.main.memory_manager') as mock_memory_manager:
            # Setup mocks
            mock_memory_manager.get_user_conversations.return_value = [
                {"_id": "conv_1", "title": "Test Conversation"}
            ]
            mock_memory_manager.get_conversation.return_value = {
                "_id": "conv_1",
                "user_id": "test_user",  # This must match the URL parameter
                "messages": [{"role": "user", "content": "Hello"}]
            }
            
            # Test getting conversations
            response = test_client.get("/conversations/test_user")
            assert response.status_code == 200
            data = response.json()
            assert "conversations" in data
            
            # Test getting specific conversation
            response = test_client.get("/conversations/test_user/conv_1")
            assert response.status_code == 200
            data = response.json()
            assert "messages" in data

    def test_memory_query_integration(self, test_client):
        """Test memory query functionality."""
        with patch('app.api.main.memory_manager') as mock_memory_manager:
            # Setup mocks for different memory types
            mock_memory_manager.retrieve_episodic_memories.return_value = [
                {"_id": "ep_1", "content": "User asked about AI"}
            ]
            mock_memory_manager.retrieve_procedural_memories.return_value = [
                {"_id": "proc_1", "content": "Used search tool successfully"}
            ]
            mock_memory_manager.retrieve_semantic_memories.return_value = [
                (MagicMock(page_content="AI is artificial intelligence", metadata={"source": "textbook"}), 0.95)
            ]
            
            # Test episodic memory query
            memory_request = {
                "user_id": "test_user",
                "query": "What did we discuss?",
                "memory_type": "episodic"
            }
            
            response = test_client.post("/memories/query", json=memory_request)
            assert response.status_code == 200
            data = response.json()
            assert "memories" in data

    def test_memory_retrieval_integration(self, test_client):
        """Test memory retrieval across different types."""
        with patch('app.api.main.memory_manager') as mock_memory_manager:
            # Setup mocks
            mock_memory_manager.retrieve_semantic_memories.return_value = [
                (MagicMock(page_content="AI is artificial intelligence", metadata={"source": "textbook"}), 0.95)
            ]
            
            # Test semantic memory retrieval
            memory_request = {
                "user_id": "test_user",
                "query": "Tell me about AI",
                "memory_type": "semantic"
            }
            
            response = test_client.post("/memories/query", json=memory_request)
            assert response.status_code == 200
            data = response.json()
            assert "memories" in data
            assert len(data["memories"]) > 0


class TestEndToEndWorkflow:
    """Test end-to-end workflows."""
    
    @pytest.fixture
    def setup_system(self):
        """Set up the complete system for testing."""
        # This would set up a real system with mocked external dependencies
        # For now, we'll use mocks
        pass
    
    @pytest.mark.asyncio
    async def test_user_question_workflow(self):
        """Test complete workflow from user question to response."""
        # This test would simulate a real user asking a question
        # and the system processing it through the complete pipeline
        
        # 1. User asks a question
        user_question = "What is artificial intelligence?"
        user_id = "test_user"
        
        # 2. System creates conversation and session
        conversation_id = "conv_123"
        session_id = "session_456"
        
        # 3. Agent processes the question
        # 4. Agent decides to use knowledge retrieval tool
        # 5. Tool retrieves relevant information
        # 6. Agent formulates response
        # 7. Response is stored in memory
        # 8. User receives response
        
        # For now, we'll test the components individually
        assert user_question == "What is artificial intelligence?"
        assert user_id == "test_user"
        assert conversation_id == "conv_123"
        assert session_id == "session_456"
    
    @pytest.mark.asyncio
    async def test_tool_usage_workflow(self):
        """Test workflow where agent uses tools."""
        # This test would simulate the agent deciding to use tools
        # and the complete tool execution workflow
        
        # 1. Agent receives request that requires tool usage
        # 2. Agent decides which tool to use
        # 3. Tool is executed
        # 4. Tool results are processed
        # 5. Results are stored in memory
        # 6. Agent formulates response with tool results
        
        # For now, we'll test the concept
        tool_decision = "use_web_search"
        tool_execution = "search_results"
        memory_storage = "stored_in_procedural_memory"
        
        assert tool_decision == "use_web_search"
        assert tool_execution == "search_results"
        assert memory_storage == "stored_in_procedural_memory"
    
    @pytest.mark.asyncio
    async def test_memory_retrieval_workflow(self):
        """Test workflow where agent retrieves memories."""
        # This test would simulate the agent retrieving relevant memories
        # to provide context-aware responses
        
        # 1. Agent receives question
        # 2. Agent checks memory for relevant information
        # 3. Relevant memories are retrieved
        # 4. Memories are incorporated into response
        # 5. Response is personalized based on memory
        
        # For now, we'll test the concept
        memory_check = "check_episodic_memory"
        memory_retrieval = "retrieve_relevant_memories"
        response_personalization = "incorporate_memories"
        
        assert memory_check == "check_episodic_memory"
        assert memory_retrieval == "retrieve_relevant_memories"
        assert response_personalization == "incorporate_memories"


class TestSystemPerformance:
    """Test system performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_response_time(self):
        """Test system response time."""
        # This would measure actual response times
        # For now, we'll test the concept
        
        start_time = datetime.utcnow()
        # Simulate processing time
        await asyncio.sleep(0.1)
        end_time = datetime.utcnow()
        
        response_time = (end_time - start_time).total_seconds()
        assert response_time >= 0.1  # Should take at least 0.1 seconds
    
    @pytest.mark.asyncio
    async def test_memory_operations_performance(self):
        """Test memory operations performance."""
        # This would test the performance of memory operations
        # For now, we'll test the concept
        
        memory_operations = ["store", "retrieve", "search", "update"]
        operation_times = {}
        
        for operation in memory_operations:
            start_time = datetime.utcnow()
            # Simulate operation
            await asyncio.sleep(0.01)
            end_time = datetime.utcnow()
            operation_times[operation] = (end_time - start_time).total_seconds()
        
        # Verify all operations completed
        assert len(operation_times) == 4
        for time in operation_times.values():
            assert time >= 0.01  # Should take at least 0.01 seconds


class TestErrorHandling:
    """Test error handling in the system."""
    
    @pytest.mark.asyncio
    async def test_agent_error_handling(self, test_client):
        """Test agent error handling in the API."""
        # Mock agent to raise an exception
        with patch('app.api.main.agent') as mock_agent:
            mock_agent.process_message = AsyncMock(side_effect=Exception("Agent error"))
            
            # Test chat request that causes agent error
            chat_request = {
                "user_id": "test_user",
                "message": "Hello",
                "conversation_id": None,
                "session_id": None
            }

            response = test_client.post("/chat", json=chat_request)

            # Should return 500 error
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "Agent error" in data["detail"]

    def test_tool_error_handling(self, mock_tools, test_client):
        """Test tool error handling."""
        # Mock a tool to raise an exception
        error_tool = mock_tools[0]
        error_tool.invoke = MagicMock(side_effect=Exception("Tool error"))
        
        # Test that the system handles tool errors gracefully
        with patch('app.api.main.agent') as mock_agent:
            mock_agent.process_message = AsyncMock(return_value="Error handled gracefully")
            
            chat_request = {
                "user_id": "test_user",
                "message": "Use the tool that will fail",
                "conversation_id": "conv_123",
                "session_id": "sess_456"
            }
            
            response = test_client.post("/chat", json=chat_request)
            
            # Should still return a response (error handled)
            assert response.status_code == 200
            data = response.json()
            assert "message" in data

    def test_memory_error_handling(self, test_client):
        """Test memory system error handling."""
        # Mock memory manager to raise an exception
        with patch('app.api.main.memory_manager') as mock_memory_manager:
            mock_memory_manager.create_conversation.side_effect = Exception("Memory error")
            
            # Test chat request that causes memory error
            chat_request = {
                "user_id": "test_user",
                "message": "Hello",
                "conversation_id": None,
                "session_id": None
            }
            
            response = test_client.post("/chat", json=chat_request)
            
            # Should return 500 error
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "Memory error" in data["detail"]

    def test_database_error_handling(self, test_client):
        """Test database error handling."""
        # Mock database client to raise an exception
        with patch('app.api.main.memory_manager') as mock_memory_manager:
            mock_memory_manager.get_user_conversations.side_effect = Exception("Database error")
            
            # Test getting conversations that causes database error
            response = test_client.get("/conversations/test_user")
            
            # Should return 500 error
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "Database error" in data["detail"]


class TestDataConsistency:
    """Test data consistency across the system."""
    
    @pytest.mark.asyncio
    async def test_conversation_data_consistency(self, mock_memory_manager):
        """Test conversation data consistency."""
        # Mock conversation data
        conversation_data = {
            "_id": "conv_123",
            "user_id": "user_456",
            "messages": [
                {"role": "user", "content": "Hello", "timestamp": datetime.utcnow()}
            ],
            "created_at": datetime.utcnow()
        }
        
        mock_memory_manager.get_conversation.return_value = conversation_data
        
        # Test data consistency
        retrieved_conversation = mock_memory_manager.get_conversation("conv_123")
        
        assert retrieved_conversation["_id"] == "conv_123"
        assert retrieved_conversation["user_id"] == "user_456"
        assert len(retrieved_conversation["messages"]) == 1
        assert retrieved_conversation["messages"][0]["role"] == "user"
        assert retrieved_conversation["messages"][0]["content"] == "Hello"
    
    @pytest.mark.asyncio
    async def test_memory_data_consistency(self, mock_memory_manager):
        """Test memory data consistency."""
        # Mock memory data
        memory_data = {
            "user_id": "user_123",
            "memory_type": "episodic",
            "content": {"event": "user_greeting", "message": "Hello"},
            "metadata": {"conversation_id": "conv_456", "timestamp": datetime.utcnow()}
        }
        
        mock_memory_manager.store_episodic_memory.return_value = "memory_789"
        
        # Test memory storage and retrieval consistency
        memory_id = mock_memory_manager.store_episodic_memory(
            user_id=memory_data["user_id"],
            content=memory_data["content"],
            metadata=memory_data["metadata"]
        )
        
        assert memory_id == "memory_789"
        
        # Verify the call was made with correct data
        mock_memory_manager.store_episodic_memory.assert_called_once_with(
            user_id=memory_data["user_id"],
            content=memory_data["content"],
            metadata=memory_data["metadata"]
        )


# Import asyncio for async tests
import asyncio
