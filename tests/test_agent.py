"""Tests for the ReAct Agent implementation."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool

from app.agent.agent import ReActAgent, AgentState, AgentAction, create_system_prompt
from app.memory.memory_manager import MemoryManager


class TestAgentState:
    """Test the AgentState class."""
    
    def test_agent_state_creation(self):
        """Test creating an AgentState instance."""
        messages = [HumanMessage(content="Hello")]
        state = AgentState(
            messages=messages,
            user_id="test_user",
            conversation_id="test_conv",
            session_id="test_session"
        )
        
        assert state.messages == messages
        assert state.user_id == "test_user"
        assert state.conversation_id == "test_conv"
        assert state.session_id == "test_session"
        assert state.tools is None
        assert state.tool_names == []
    
    def test_agent_state_with_tools(self):
        """Test creating an AgentState with tools."""
        tools = [MagicMock(spec=BaseTool)]
        state = AgentState(
            messages=[],
            user_id="test_user",
            conversation_id="test_conv",
            session_id="test_session",
            tools=tools,
            tool_names=["test_tool"]
        )
        
        assert state.tools == tools
        assert state.tool_names == ["test_tool"]


class TestSystemPrompt:
    """Test the system prompt creation."""
    
    @patch('builtins.open', create=True)
    def test_create_system_prompt(self, mock_open):
        """Test creating system prompt with tool descriptions."""
        mock_open.return_value.__enter__.return_value.read.return_value = "System prompt with {tool_descriptions}"
        
        tool_descriptions = "- Tool1: Description1\n- Tool2: Description2"
        result = create_system_prompt(tool_descriptions)
        
        expected = "System prompt with - Tool1: Description1\n- Tool2: Description2"
        assert result == expected


class TestReActAgent:
    """Test the ReActAgent class."""
    
    @pytest.fixture
    def mock_memory_manager(self):
        """Create a mock memory manager."""
        return MagicMock(spec=MemoryManager)
    
    @pytest.fixture
    def mock_tools(self):
        """Create mock tools."""
        tools = []
        for i in range(4):
            tool = MagicMock(spec=BaseTool)
            tool.name = f"tool_{i}"
            tool.description = f"Description for tool {i}"
            tools.append(tool)
        return tools
    
    @patch('app.agent.agent.ChatOpenAI')
    @patch('app.agent.agent.ToolNode')
    @patch('app.agent.agent.StateGraph')
    def test_agent_initialization(self, mock_graph, mock_tool_node, mock_llm, mock_memory_manager):
        """Test ReActAgent initialization."""
        # Mock the LLM
        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance
        
        # Mock the graph
        mock_graph_instance = MagicMock()
        mock_graph.return_value = mock_graph_instance
        mock_graph_instance.add_node.return_value = mock_graph_instance
        mock_graph_instance.set_entry_point.return_value = mock_graph_instance
        mock_graph_instance.compile.return_value = MagicMock()
        
        # Mock the tool node
        mock_tool_node_instance = MagicMock()
        mock_tool_node.return_value = mock_tool_node_instance
        
        agent = ReActAgent(memory_manager=mock_memory_manager)
        
        assert agent.memory_manager == mock_memory_manager
        assert len(agent.tools) == 4  # Should have 4 tools
        assert agent.tool_node == mock_tool_node_instance
        assert agent.workflow is not None
    
    @patch('app.agent.agent.ChatOpenAI')
    @patch('app.agent.agent.ToolNode')
    @patch('app.agent.agent.StateGraph')
    def test_setup_tools(self, mock_graph, mock_tool_node, mock_llm, mock_memory_manager):
        """Test tool setup."""
        # Mock the graph compilation
        mock_graph_instance = MagicMock()
        mock_graph.return_value = mock_graph_instance
        mock_graph_instance.add_node.return_value = mock_graph_instance
        mock_graph_instance.set_entry_point.return_value = mock_graph_instance
        mock_graph_instance.compile.return_value = MagicMock()
        
        agent = ReActAgent(memory_manager=mock_memory_manager)
        
        # Check that tools are properly set up
        tool_names = [tool.name for tool in agent.tools]
        expected_names = ["web_search", "knowledge_retrieval", "product_search", "appointment"]
        
        for expected_name in expected_names:
            assert any(tool.name == expected_name for tool in agent.tools)
    
    @patch('app.agent.agent.ChatOpenAI')
    @patch('app.agent.agent.ToolNode')
    @patch('app.agent.agent.StateGraph')
    def test_create_agent_graph(self, mock_graph, mock_tool_node, mock_llm, mock_memory_manager):
        """Test agent graph creation."""
        # Mock the graph compilation
        mock_graph_instance = MagicMock()
        mock_graph.return_value = mock_graph_instance
        mock_graph_instance.add_node.return_value = mock_graph_instance
        mock_graph_instance.set_entry_point.return_value = mock_graph_instance
        mock_graph_instance.compile.return_value = MagicMock()
        
        agent = ReActAgent(memory_manager=mock_memory_manager)
        
        # Verify graph was created with proper structure
        mock_graph_instance.add_node.assert_called()
        mock_graph_instance.set_entry_point.assert_called()
        mock_graph_instance.compile.assert_called()
    
    @patch('app.agent.agent.ChatOpenAI')
    @patch('app.agent.agent.ToolNode')
    @patch('app.agent.agent.StateGraph')
    @patch('app.agent.agent.create_system_prompt')
    @patch('app.agent.agent.AgentMemoryUtils')
    def test_think_function(self, mock_memory_utils, mock_create_prompt, mock_graph, mock_tool_node, mock_llm, mock_memory_manager):
        """Test the think function in the agent graph."""
        # Mock the graph compilation
        mock_graph_instance = MagicMock()
        mock_graph.return_value = mock_graph_instance
        mock_graph_instance.add_node.return_value = mock_graph_instance
        mock_graph_instance.set_entry_point.return_value = mock_graph_instance
        mock_graph_instance.compile.return_value = MagicMock()
        
        # Mock the LLM
        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance
        mock_llm_instance.bind_tools.return_value.invoke.return_value = AIMessage(content="Test response")
        
        # Mock the memory utils
        mock_memory_utils_instance = MagicMock()
        mock_memory_utils.return_value = mock_memory_utils_instance
        mock_memory_utils_instance.retrieve_memory_context.return_value = "Memory context"
        
        # Mock the system prompt
        mock_create_prompt.return_value = "System prompt with tools"
        
        agent = ReActAgent(memory_manager=mock_memory_manager)
        
        # Create a test state
        state = AgentState(
            messages=[HumanMessage(content="Hello")],
            user_id="test_user",
            conversation_id="test_conv",
            session_id="test_session",
            tools=agent.tools
        )
        
        # Get the think function from the workflow
        think_function = agent.workflow.nodes["think"]
        
        # Test the think function
        result_state = think_function(state)
        
        # Verify the state was updated
        assert len(result_state.messages) == 2
        assert isinstance(result_state.messages[-1], AIMessage)
        assert result_state.messages[-1].content == "Test response"
    
    @patch('app.agent.agent.ChatOpenAI')
    @patch('app.agent.agent.ToolNode')
    @patch('app.agent.agent.StateGraph')
    def test_use_tool_function(self, mock_graph, mock_tool_node, mock_llm, mock_memory_manager):
        """Test the use_tool function in the agent graph."""
        # Mock the graph compilation
        mock_graph_instance = MagicMock()
        mock_graph.return_value = mock_graph_instance
        mock_graph_instance.add_node.return_value = mock_graph_instance
        mock_graph_instance.set_entry_point.return_value = mock_graph_instance
        mock_graph_instance.compile.return_value = MagicMock()
        
        # Mock the tool node
        mock_tool_node_instance = MagicMock()
        mock_tool_node.return_value = mock_tool_node_instance
        mock_tool_node_instance.invoke.return_value = {
            "messages": [ToolMessage(content="Tool result", name="test_tool")]
        }
        
        agent = ReActAgent(memory_manager=mock_memory_manager)
        
        # Create a test state with tool calls
        ai_message = AIMessage(content="I need to use a tool")
        ai_message.tool_calls = [{"name": "test_tool", "args": {}}]
        
        state = AgentState(
            messages=[HumanMessage(content="Hello"), ai_message],
            user_id="test_user",
            conversation_id="test_conv",
            session_id="test_session",
            tools=agent.tools
        )
        
        # Get the use_tool function from the workflow
        use_tool_function = agent.workflow.nodes["use_tool"]
        
        # Test the use_tool function
        result_state = use_tool_function(state)
        
        # Verify the tool was executed
        mock_tool_node_instance.invoke.assert_called_once()
    
    @patch('app.agent.agent.ChatOpenAI')
    @patch('app.agent.agent.ToolNode')
    @patch('app.agent.agent.StateGraph')
    def test_should_use_tool_logic(self, mock_graph, mock_tool_node, mock_llm, mock_memory_manager):
        """Test the should_use_tool decision logic."""
        # Mock the graph compilation
        mock_graph_instance = MagicMock()
        mock_graph.return_value = mock_graph_instance
        mock_graph_instance.add_node.return_value = mock_graph_instance
        mock_graph_instance.set_entry_point.return_value = mock_graph_instance
        mock_graph_instance.compile.return_value = MagicMock()
        
        agent = ReActAgent(memory_manager=mock_memory_manager)
        
        # Get the should_use_tool function from the workflow
        should_use_tool_function = agent.workflow.conditional_edges["should_use_tool"]
        
        # Test with human message (should think)
        state_with_human = AgentState(
            messages=[HumanMessage(content="Hello")],
            user_id="test_user",
            conversation_id="test_conv",
            session_id="test_session"
        )
        result = should_use_tool_function(state_with_human)
        assert result == "think"
        
        # Test with AI message without tool calls (should respond)
        ai_message = AIMessage(content="Hello there")
        ai_message.tool_calls = []
        state_with_ai = AgentState(
            messages=[HumanMessage(content="Hello"), ai_message],
            user_id="test_user",
            conversation_id="test_conv",
            session_id="test_session"
        )
        result = should_use_tool_function(state_with_ai)
        assert result == "response"
        
        # Test with AI message with tool calls (should use tool)
        ai_message_with_tools = AIMessage(content="I need to search")
        ai_message_with_tools.tool_calls = [{"name": "web_search", "args": {}}]
        state_with_tools = AgentState(
            messages=[HumanMessage(content="Search for something"), ai_message_with_tools],
            user_id="test_user",
            conversation_id="test_conv",
            session_id="test_session"
        )
        result = should_use_tool_function(state_with_tools)
        assert result == "use_tool"
    
    @patch('app.agent.agent.ChatOpenAI')
    @patch('app.agent.agent.ToolNode')
    @patch('app.agent.agent.StateGraph')
    @patch('app.agent.agent.AgentMemoryUtils')
    def test_process_message(self, mock_memory_utils, mock_graph, mock_tool_node, mock_llm, mock_memory_manager):
        """Test the process_message method."""
        # Mock the graph compilation
        mock_graph_instance = MagicMock()
        mock_graph.return_value = mock_graph_instance
        mock_graph_instance.add_node.return_value = mock_graph_instance
        mock_graph_instance.add_node.return_value = mock_graph_instance
        mock_graph_instance.set_entry_point.return_value = mock_graph_instance
        mock_graph_instance.compile.return_value = MagicMock()
        
        # Mock the workflow execution
        mock_workflow = MagicMock()
        mock_workflow.invoke.return_value = AgentState(
            messages=[HumanMessage(content="Hello"), AIMessage(content="Response")],
            user_id="test_user",
            conversation_id="test_conv",
            session_id="test_session"
        )
        
        agent = ReActAgent(memory_manager=mock_memory_manager)
        agent.workflow = mock_workflow
        
        # Mock the memory utils
        mock_memory_utils_instance = MagicMock()
        mock_memory_utils.return_value = mock_memory_utils_instance
        mock_memory_utils_instance.retrieve_memory_context.return_value = "Memory context"
        
        # Test process_message
        result = await agent.process_message(
            user_id="test_user",
            session_id="test_session",
            conversation_id="test_conv",
            message="Hello"
        )
        
        # Verify the workflow was invoked
        mock_workflow.invoke.assert_called_once()
        
        # Verify memory operations
        mock_memory_manager.add_message_to_short_term_memory.assert_called()
        mock_memory_manager.store_episodic_memory.assert_called()


class TestAgentIntegration:
    """Integration tests for the agent."""
    
    @pytest.mark.asyncio
    @patch('app.agent.agent.ChatOpenAI')
    @patch('app.agent.agent.ToolNode')
    @patch('app.agent.agent.StateGraph')
    async def test_agent_with_memory_integration(self, mock_graph, mock_tool_node, mock_llm, mock_memory_manager):
        """Test agent integration with memory system."""
        # Mock the graph compilation
        mock_graph_instance = MagicMock()
        mock_graph.return_value = mock_graph_instance
        mock_graph_instance.add_node.return_value = mock_graph_instance
        mock_graph_instance.set_entry_point.return_value = mock_graph_instance
        mock_graph_instance.compile.return_value = MagicMock()
        
        # Mock the LLM
        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance
        mock_llm_instance.bind_tools.return_value.invoke.return_value = AIMessage(content="Test response")
        
        # Mock the workflow
        mock_workflow = MagicMock()
        mock_workflow.invoke.return_value = AgentState(
            messages=[HumanMessage(content="Hello"), AIMessage(content="Response")],
            user_id="test_user",
            conversation_id="test_conv",
            session_id="test_session"
        )
        
        agent = ReActAgent(memory_manager=mock_memory_manager)
        agent.workflow = mock_workflow
        
        # Test processing a message
        result = await agent.process_message(
            user_id="test_user",
            session_id="test_session",
            conversation_id="test_conv",
            message="Hello, how are you?"
        )
        
        # Verify memory operations were called
        mock_memory_manager.add_message_to_short_term_memory.assert_called()
        mock_memory_manager.store_episodic_memory.assert_called()
        
        # Verify the workflow was executed
        mock_workflow.invoke.assert_called_once()
