"""Tests for ReAct agent."""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch, call
from datetime import datetime
from typing import List

from app.agent.agent import ReActAgent, AgentState, AgentAction
from app.memory.memory_manager import MemoryManager
from langchain_core.messages import AIMessage, HumanMessage, FunctionMessage


class TestReActAgent:
    """Tests for the ReAct agent."""
    
    @patch('app.agent.agent.ChatOpenAI')
    @patch('app.agent.agent.WebSearchTool')
    @patch('app.agent.agent.ProductSearchTool')
    @patch('app.agent.agent.AppointmentTool')
    @patch('app.agent.agent.SemanticRetrievalTool')
    def test_init(self, mock_semantic_tool, mock_appointment_tool, mock_product_tool, 
                  mock_web_tool, mock_llm_cls, mock_memory_manager):
        """Test initialization of ReAct agent."""
        # Arrange
        mock_llm = MagicMock()
        mock_llm_cls.return_value = mock_llm
        
        # Act
        agent = ReActAgent(memory_manager=mock_memory_manager)
        
        # Assert
        assert agent.memory_manager == mock_memory_manager
        assert agent.llm == mock_llm
        assert len(agent.tools) == 4  # 4 tools: web, product, appointment, semantic
        assert agent.workflow is not None
        
    @patch('app.agent.agent.ChatOpenAI')
    @patch('app.agent.agent.WebSearchTool')
    @patch('app.agent.agent.ProductSearchTool')
    @patch('app.agent.agent.AppointmentTool')
    @patch('app.agent.agent.SemanticRetrievalTool')
    def test_setup_tools(self, mock_semantic_tool, mock_appointment_tool, mock_product_tool,
                        mock_web_tool, mock_llm_cls, mock_memory_manager):
        """Test tool setup."""
        # Arrange
        mock_web_instance = MagicMock()
        mock_web_tool.return_value = mock_web_instance
        
        # Act
        agent = ReActAgent(memory_manager=mock_memory_manager)
        tools = agent._setup_tools()
        
        # Assert
        assert len(tools) == 4
        mock_web_tool.assert_called_once()
        mock_product_tool.assert_called_once()
        mock_appointment_tool.assert_called_once()
        mock_semantic_tool.assert_called_once()
        
    @patch('app.agent.agent.ChatOpenAI')
    @patch('app.agent.agent.WebSearchTool')
    @patch('app.agent.agent.ProductSearchTool')
    @patch('app.agent.agent.AppointmentTool')
    @patch('app.agent.agent.SemanticRetrievalTool')
    def test_reset_session(self, mock_semantic_tool, mock_appointment_tool, mock_product_tool,
                          mock_web_tool, mock_llm_cls, mock_memory_manager):
        """Test resetting session."""
        # Arrange
        agent = ReActAgent(memory_manager=mock_memory_manager)
        
        # Act
        agent.reset_session("test-session")
        
        # Assert
        mock_memory_manager.clear_short_term_memory.assert_called_once_with("test-session")

    @patch('app.agent.agent.ChatOpenAI')
    @patch('app.agent.agent.WebSearchTool')
    @patch('app.agent.agent.ProductSearchTool')
    @patch('app.agent.agent.AppointmentTool')
    @patch('app.agent.agent.SemanticRetrievalTool')
    @pytest.mark.asyncio
    async def test_process_message_simple_response(self, mock_semantic_tool, mock_appointment_tool, 
                                                  mock_product_tool, mock_web_tool, mock_llm_cls, 
                                                  mock_memory_manager):
        """Test processing a simple message without tool usage."""
        # Arrange
        agent = ReActAgent(memory_manager=mock_memory_manager)
        
        # Mock short-term memory
        mock_short_term = MagicMock()
        mock_short_term.get_messages.return_value = []
        mock_short_term.add_user_message = MagicMock()
        mock_short_term.add_ai_message = MagicMock()
        mock_memory_manager.get_short_term_memory.return_value = mock_short_term
        
        # Mock workflow result
        mock_result = MagicMock()
        mock_ai_message = MagicMock(spec=AIMessage)
        mock_ai_message.content = "Hello! How can I help you today?"
        mock_result.messages = [mock_ai_message]
        agent.workflow.invoke = MagicMock(return_value=mock_result)
        
        # Act
        response = await agent.process_message(
            user_id="test_user",
            session_id="test_session",
            conversation_id="test_conversation",
            message="Hello"
        )
        
        # Assert
        assert response == "Hello! How can I help you today?"
        mock_short_term.add_user_message.assert_called_once()
        mock_short_term.add_ai_message.assert_called_once()
        mock_memory_manager.add_message_to_conversation.assert_called()

    @patch('app.agent.agent.ChatOpenAI')
    @patch('app.agent.agent.WebSearchTool')
    @patch('app.agent.agent.ProductSearchTool')
    @patch('app.agent.agent.AppointmentTool')
    @patch('app.agent.agent.SemanticRetrievalTool')
    @pytest.mark.asyncio
    async def test_process_message_with_tool_usage(self, mock_semantic_tool, mock_appointment_tool, 
                                                  mock_product_tool, mock_web_tool, mock_llm_cls, 
                                                  mock_memory_manager):
        """Test processing a message that requires tool usage."""
        # Arrange
        agent = ReActAgent(memory_manager=mock_memory_manager)
        
        # Mock short-term memory
        mock_short_term = MagicMock()
        mock_short_term.get_messages.return_value = []
        mock_memory_manager.get_short_term_memory.return_value = mock_short_term
        
        # Mock workflow result with tool usage
        mock_result = MagicMock()
        mock_tool_call = MagicMock()
        mock_tool_call.name = "internet_search"
        mock_ai_message = MagicMock(spec=AIMessage)
        mock_ai_message.content = "I found some search results for you."
        mock_ai_message.tool_calls = [mock_tool_call]
        mock_result.messages = [mock_ai_message]
        agent.workflow.invoke = MagicMock(return_value=mock_result)
        
        # Act
        response = await agent.process_message(
            user_id="test_user",
            session_id="test_session", 
            conversation_id="test_conversation",
            message="Search for Python tutorials"
        )
        
        # Assert
        assert response == "I found some search results for you."
        mock_memory_manager.store_procedural_memory.assert_called()

    @patch('app.agent.agent.ChatOpenAI')
    @patch('app.agent.agent.WebSearchTool')
    @patch('app.agent.agent.ProductSearchTool')
    @patch('app.agent.agent.AppointmentTool')
    @patch('app.agent.agent.SemanticRetrievalTool')
    @pytest.mark.asyncio
    async def test_process_message_semantic_extraction(self, mock_semantic_tool, mock_appointment_tool, 
                                                      mock_product_tool, mock_web_tool, mock_llm_cls, 
                                                      mock_memory_manager):
        """Test semantic fact extraction during message processing."""
        # Arrange
        agent = ReActAgent(memory_manager=mock_memory_manager)
        
        # Mock short-term memory with enough messages to trigger extraction
        mock_short_term = MagicMock()
        mock_messages = [MagicMock() for _ in range(11)]  # 11 messages to trigger extraction
        mock_short_term.get_messages.return_value = mock_messages
        mock_memory_manager.get_short_term_memory.return_value = mock_short_term
        
        # Mock semantic extraction
        mock_memory_manager.extract_semantic_facts.return_value = [
            {"fact": "User likes Python", "confidence": 0.9}
        ]
        
        # Mock workflow result
        mock_result = MagicMock()
        mock_ai_message = MagicMock(spec=AIMessage)
        mock_ai_message.content = "I understand you're interested in Python!"
        mock_result.messages = [mock_ai_message]
        agent.workflow.invoke = MagicMock(return_value=mock_result)
        
        # Act
        response = await agent.process_message(
            user_id="test_user",
            session_id="test_session",
            conversation_id="test_conversation", 
            message="I love programming in Python"
        )
        
        # Assert
        mock_memory_manager.extract_semantic_facts.assert_called_once()
        mock_memory_manager.store_extracted_semantic_facts.assert_called_once()

    @patch('app.agent.agent.ChatOpenAI')
    @patch('app.agent.agent.WebSearchTool')
    @patch('app.agent.agent.ProductSearchTool')
    @patch('app.agent.agent.AppointmentTool')
    @patch('app.agent.agent.SemanticRetrievalTool')
    @pytest.mark.asyncio
    async def test_process_message_error_handling(self, mock_semantic_tool, mock_appointment_tool, 
                                                 mock_product_tool, mock_web_tool, mock_llm_cls, 
                                                 mock_memory_manager):
        """Test error handling during message processing."""
        # Arrange
        agent = ReActAgent(memory_manager=mock_memory_manager)
        
        # Mock short-term memory
        mock_short_term = MagicMock()
        mock_short_term.get_messages.return_value = []
        mock_memory_manager.get_short_term_memory.return_value = mock_short_term
        
        # Mock workflow to raise an exception
        agent.workflow.invoke = MagicMock(side_effect=Exception("Test error"))
        
        # Act
        response = await agent.process_message(
            user_id="test_user",
            session_id="test_session",
            conversation_id="test_conversation",
            message="Test message"
        )
        
        # Assert
        assert "I'm sorry, I wasn't able to generate a proper response." in response

    def test_agent_state_creation(self):
        """Test AgentState creation and validation."""
        # Arrange
        test_messages = [
            HumanMessage(content="Test message"),
            AIMessage(content="Test response")
        ]
        
        # Act
        state = AgentState(
            messages=test_messages,
            user_id="test_user",
            session_id="test_session",
            conversation_id="test_conversation",
            tools=[],
            tool_names=[]
        )
        
        # Assert
        assert state.user_id == "test_user"
        assert state.session_id == "test_session"
        assert state.conversation_id == "test_conversation"
        assert len(state.messages) == 2
        assert state.tools == []
        assert state.tool_names == []

    def test_agent_action_enum(self):
        """Test AgentAction enum values."""
        # Assert
        assert AgentAction.CALL_TOOL == "call_tool"
        assert AgentAction.RESPOND == "respond"

    @patch('app.agent.agent.ChatOpenAI')
    @patch('app.agent.agent.WebSearchTool')
    @patch('app.agent.agent.ProductSearchTool')
    @patch('app.agent.agent.AppointmentTool')
    @patch('app.agent.agent.SemanticRetrievalTool')
    def test_create_system_prompt(self, mock_semantic_tool, mock_appointment_tool, 
                                 mock_product_tool, mock_web_tool, mock_llm_cls, 
                                 mock_memory_manager):
        """Test system prompt creation."""
        # Arrange
        from app.agent.agent import create_system_prompt
        tool_descriptions = "Tool 1: Description 1\nTool 2: Description 2"
        
        # Act
        prompt = create_system_prompt(tool_descriptions)
        
        # Assert
        assert "AI assistant with advanced memory capabilities" in prompt
        assert tool_descriptions in prompt
        assert "short-term memory" in prompt
        assert "episodic memory" in prompt
        assert "semantic memory" in prompt
        assert "procedural memory" in prompt
