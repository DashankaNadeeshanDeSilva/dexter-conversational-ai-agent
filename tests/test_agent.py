"""Tests for ReAct agent."""

import pytest
from unittest.mock import MagicMock, patch
import json

from app.core.agent import ReActAgent, AgentState, AgentAction

@pytest.fixture
def mock_memory_manager():
    """Create a mock memory manager."""
    mock = MagicMock()
    return mock

@pytest.fixture
def mock_tool_executor():
    """Create a mock tool executor."""
    mock = MagicMock()
    return mock

@pytest.fixture
def mock_llm():
    """Create a mock LLM."""
    mock = MagicMock()
    return mock

class TestReActAgent:
    """Tests for the ReAct agent."""
    
    @patch('app.core.agent.ChatOpenAI')
    def test_init(self, mock_llm_cls, mock_memory_manager):
        """Test initialization of ReAct agent."""
        # Arrange
        mock_llm = MagicMock()
        mock_llm_cls.return_value = mock_llm
        
        # Act
        agent = ReActAgent(memory_manager=mock_memory_manager)
        
        # Assert
        assert agent.memory_manager == mock_memory_manager
        assert agent.llm == mock_llm
        assert len(agent.tools) > 0
        
    @patch('app.core.agent.SearchTool')
    @patch('app.core.agent.ChatOpenAI')
    def test_setup_tools(self, mock_llm_cls, mock_search_tool_cls, mock_memory_manager):
        """Test tool setup."""
        # Arrange
        mock_search_tool = MagicMock()
        mock_search_tool_cls.return_value = mock_search_tool
        
        # Act
        agent = ReActAgent(memory_manager=mock_memory_manager)
        tools = agent._setup_tools()
        
        # Assert
        assert mock_search_tool in tools
        
    @patch('app.core.agent.ChatOpenAI')
    def test_reset_session(self, mock_llm_cls, mock_memory_manager):
        """Test resetting session."""
        # Arrange
        agent = ReActAgent(memory_manager=mock_memory_manager)
        
        # Act
        agent.reset_session("test-session")
        
        # Assert
        mock_memory_manager.clear_short_term_memory.assert_called_once_with("test-session")
