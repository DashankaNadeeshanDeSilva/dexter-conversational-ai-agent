"""ReAct agent implementation using LangGraph."""

from typing import Dict, List, Any, Optional, Tuple, Type, Annotated, Sequence, Union, Literal
import logging
import json
from enum import Enum
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, FunctionMessage, BaseMessage
from langchain_core.tools import BaseTool
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableConfig
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor, ToolInvocation
import pydantic

from app.config import settings
from app.memory.memory_manager import MemoryManager, MemoryType
from app.tools.web_search_tool import WebSearchTool
from app.tools.semantic_retrieval_tool import SemanticRetrievalTool
from app.tools.product_search_tool import ProductSearchTool
from app.tools.appointment_tool import AppointmentTool
from app.agent.memory_utils import AgentMemoryUtils

logger = logging.getLogger(__name__)

# Define the agent state
class AgentState(pydantic.BaseModel):
    """State for the agent.
    Structured data container to maintain rich state information across multiple interactions 
    while ensuring data integrity through Pydantic's validation features."""
    
    messages: list[BaseMessage] # stores the conversation history as a list of BaseMessage objects
    user_id: str
    conversation_id: str
    session_id: str
    tools: Optional[List[BaseTool]] = None # list that hold BaseTool objects representing tool capabilities
    tool_names: List[str] = []
    
    class Config:
        arbitrary_types_allowed = True

class AgentAction(str, Enum):
    """Possible agent actions."""
    
    THINK = "think"
    USE_TOOL = "use_tool"
    RESPONSE = "response"

def create_system_prompt(tool_descriptions: str) -> str:
    """Create the system prompt for the agent."""
    with open("system_prompt.md", "r") as file:
        system_prompt = file.read()
    return system_prompt.format(tool_descriptions=tool_descriptions)

class ReActAgent:
    """ReAct agent implementation using LangGraph."""
    
    def __init__(self, memory_manager: MemoryManager):
        """Initialize the ReAct agent."""
        self.memory_manager = memory_manager
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY
        )
        
        # Set up tools
        self.tools = self._setup_tools()
        self.tool_executor = ToolExecutor(self.tools)
        
        # Set up the agent graph
        self.workflow = self._create_agent_graph()
        
        logger.info("ReAct agent initialized")
    
    def _setup_tools(self) -> List[BaseTool]:
        """Set up tools for the agent."""
        tools = [
            SearchTool(),
            SemanticRetrievalTool(),
            ProductSearchTool(),
            AppointmentTool()
        ]
        return tools
    
    def _create_agent_graph(self) -> StateGraph:
        """Create the agent workflow graph."""
        
        def should_use_tool(state: AgentState) -> Union[Literal["use_tool"], Literal["response"]]:
            """Determine if the agent should use a tool or respond."""
            last_message = state.messages[-1]
            
            if not isinstance(last_message, AIMessage):
                return "think"
                
            if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
                return "response"
                
            return "use_tool"
        
        def think(state: AgentState) -> AgentState:
            """Generate agent thoughts/response."""
            # Prepare tool descriptions and system prompt
            tool_descriptions = "\n".join([
                f"- {tool.name}: {tool.description}" for tool in state.tools or []
            ]) 
            system_prompt = create_system_prompt(tool_descriptions=tool_descriptions)
            
            # Create prompt with messages
            messages = [SystemMessage(content=system_prompt)] + state.messages
            
            # Check if there are memories relevant to the last human message
            if state.messages and isinstance(state.messages[-1], HumanMessage):
                query = state.messages[-1].content

                # Get memories relevant to the last human message
                agent_memory_utils = AgentMemoryUtils(self.memory_manager)

                # Check and retrieve relevant memories from semantic, episodic, and procedural memories
                memory_context = agent_memory_utils.retrieve_memory_context(state.user_id, query)

                # Insert combined memories into context (just after system message/prompt)
                if memory_context != "No relevant information found in memory.":
                    messages.insert(1, SystemMessage(content=memory_context))
 
            # Get response from LLM
            response = self.llm.invoke(
                messages,
                tool_choice="auto",
                tools=[tool.to_pydantic_tool() for tool in state.tools] if state.tools else None
            )
            
            # Update the messages
            state.messages.append(response)
            return state
        
        def use_tool(state: AgentState) -> AgentState:
            """Use a tool based on the agent's decision."""
            last_message = state.messages[-1]
            
            if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
                return state
            
            for tool_call in last_message.tool_calls:
                action = tool_call.name
                args = json.loads(tool_call.args)
                
                # Execute the tool
                try:
                    tool_result = self.tool_executor.execute(
                        ToolInvocation(
                            name=action,
                            arguments=args
                        )
                    )
                    
                    # Add the tool (function) message to the state
                    state.messages.append(
                        FunctionMessage(
                            name=action,
                            content=str(tool_result)
                        )
                    )
                    
                    # Store procedural memory about tool usage
                    query_context = ""
                    if state.messages:
                        # Get the original user query for context
                        human_messages = [msg for msg in state.messages if isinstance(msg, HumanMessage)]
                        if human_messages:
                            query_context = human_messages[-1].content
                    
                    self.memory_manager.store_procedural_memory(
                        user_id=state.user_id,
                        content={
                            "tool": action,
                            "arguments": args,
                            "result_summary": str(tool_result)[:100] + "...",
                            "query_context": query_context,
                            "success": True,  # We'll track success vs failure
                            "tool_selection_reason": f"Used {action} for query about: {query_context[:50]}..."
                        },
                        metadata={
                            "conversation_id": state.conversation_id,
                            "timestamp": str(datetime.utcnow()),
                            "tool_category": "successful_usage"
                        }
                    )
                    
                except Exception as e:
                    logger.error(f"Error executing tool {action}: {e}")

                    # Add tool error message to the state
                    state.messages.append(
                        FunctionMessage(
                            name=action,
                            content=f"Error executing tool: {str(e)}"
                        )
                    )
                    
                    # Store procedural memory about failed tool usage
                    query_context = ""
                    if state.messages:
                        human_messages = [msg for msg in state.messages if isinstance(msg, HumanMessage)]
                        if human_messages:
                            query_context = human_messages[-1].content
                    
                    self.memory_manager.store_procedural_memory(
                        user_id=state.user_id,
                        content={
                            "tool": action,
                            "arguments": args,
                            "error": str(e),
                            "query_context": query_context,
                            "success": False,
                            "failure_reason": f"Tool {action} failed with error: {str(e)}"
                        },
                        metadata={
                            "conversation_id": state.conversation_id,
                            "timestamp": str(datetime.utcnow()),
                            "tool_category": "failed_usage"
                        }
                    )
            
            return state
        
        # Create the ReAct agent graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("think", think)
        workflow.add_node("use_tool", use_tool)
        
        # Set entry point
        workflow.set_entry_point("think")
        
        # Add edges
        workflow.add_conditional_edges(
            "think",
            should_use_tool,
            {
                "use_tool": "use_tool",
                "response": END
            }
        )
        
        workflow.add_edge("use_tool", "think")
        
        # Compile the graph
        return workflow.compile()
    
    async def process_message(
        self,
        user_id: str,
        session_id: str,
        conversation_id: str,
        message: str
    ) -> str:
        """
        Process a user message and return the agent's response.
        
        Args:
            user_id: User ID
            session_id: Session ID
            conversation_id: Conversation ID
            message: User message
            
        Returns:
            Agent response
        """
        # Update session activity for user message
        #self.memory_manager.session_manager.update_session_activity(session_id, "message")
        
        # Get short-term memory or initialize it
        short_term_memory = self.memory_manager.get_short_term_memory(session_id)
        
        # Add user message (HumanMessage) to Short-term memory
        short_term_memory.add_user_message(message)
        
        ## Episodic Memory Storage
        # Add user message to the database as Episodic memory
        self.memory_manager.add_message_to_conversation(
            conversation_id=conversation_id,
            message={
                "role": "user",
                "content": message
            }
        )
        
        # Create initial state with existing messages
        state = AgentState(
            messages=short_term_memory.get_messages(),
            user_id=user_id,
            session_id=session_id,
            conversation_id=conversation_id,
            tools=self.tools,
            tool_names=[tool.name for tool in self.tools]
        )
        
        # Run the agent
        try:
            result = self.workflow.invoke(state)
            
            # Extract AI message
            ai_messages = [msg for msg in result.messages if isinstance(msg, AIMessage)]
            
            if not ai_messages:
                response = "I'm sorry, I wasn't able to generate a proper response."
            else:
                response = ai_messages[-1].content
            
            ## Episodic Memory Storage
            # Store agent response in coversation database as Episodic memory
            self.memory_manager.add_message_to_conversation(
                conversation_id=conversation_id,
                message={
                    "role": "assistant",
                    "content": response
                }
            )

            # Add ai response (AIMessage) to Short-term memory
            short_term_memory.add_ai_message(response)
            
            ## Semantic Memory Extraction and Storage 
            # Extract semantic facts after every N messages from the last N messages
            # This is to ensure we have enough context for meaningful fact extraction
            EXTRACTION_INTERVAL = 10   # Extract every 10 messages, use last 10 as context
            num_messages = len(short_term_memory.get_messages())
            if num_messages > EXTRACTION_INTERVAL and num_messages % EXTRACTION_INTERVAL == 0:
                conversation_context = short_term_memory.get_messages()[-EXTRACTION_INTERVAL:]
   
                # Extract semantic facts from the conversation (using LLM)
                extracted_facts = self.memory_manager.extract_semantic_facts(
                    user_message=message,
                    agent_response=response,
                    conversation_context=conversation_context,
                    user_id=user_id
                )
                
                # Store extracted facts in Semantic memory
                if extracted_facts:
                    self.memory_manager.store_extracted_semantic_facts(
                        user_id=user_id,
                        facts=extracted_facts,
                        conversation_metadata={
                            "conversation_id": conversation_id,
                            "session_id": session_id,
                            "source_type": "conversation_extraction"
                        }
                    )
                    logger.info(f"Stored {len(extracted_facts)} semantic facts for user {user_id}")
            
            ## Procedural Memory Storage
            # Store successful interaction pattern in procedural memory if response was generated successfully
            if response and response != "I'm sorry, I wasn't able to generate a proper response.":
                # Determine the pattern type based on tools used
                tool_calls_made = []
                for msg in result.messages:
                    if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            tool_calls_made.append(tool_call.name)
                
                pattern_type = "direct_response" if not tool_calls_made else f"tool_assisted_{'+'.join(tool_calls_made)}"
                
                self.memory_manager.store_successful_pattern(
                    user_id=user_id,
                    pattern_type=pattern_type,
                    pattern_description=f"Successfully handled query '{message[:50]}...' with: {pattern_type}",
                    context=message,
                    metadata={
                        "conversation_id": conversation_id,
                        "timestamp": str(datetime.utcnow()),
                        "tool_category": "successful_pattern"
                    }
                )
            
            logger.info(f"Processed message for user {user_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"I'm sorry, I encountered an error: {str(e)}"
    
    def reset_session(self, session_id: str) -> None:
        """Reset the short-term memory for a session."""
        self.memory_manager.clear_short_term_memory(session_id)
        logger.info(f"Reset session {session_id}")
