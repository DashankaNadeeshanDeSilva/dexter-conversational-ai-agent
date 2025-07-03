"""Short-term memory implementation for the agent."""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, FunctionMessage, BaseMessage
from langchain_core.chat_history import BaseChatMessageHistory

logger = logging.getLogger(__name__)

class ShortTermMemory(BaseChatMessageHistory):
    """Short-term memory for the agent using message histories."""
    
    def __init__(self, session_id: str, max_token_limit: int = 4000):
        """
        Initialize the short-term memory.
        
        Args:
            session_id: Session identifier
            max_token_limit: Maximum token limit for the memory
        """
        self.session_id = session_id
        self.max_token_limit = max_token_limit
        self.messages: List[BaseMessage] = []
        self.token_count = 0
        logger.debug(f"Initialized short-term memory for session {session_id}")
    
    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the memory."""
        self.messages.append(message)
        # A simple estimation of token count - this should be replaced with a proper tokenizer
        self.token_count += len(message.content) // 4
        self._enforce_token_limit()
        logger.debug(f"Added message to short-term memory for session {self.session_id}")
    
    def add_user_message(self, message: str) -> None:
        """Add a user message to the memory."""
        self.add_message(HumanMessage(content=message))
    
    def add_ai_message(self, message: str) -> None:
        """Add an AI message to the memory."""
        self.add_message(AIMessage(content=message))
        
    def add_system_message(self, message: str) -> None:
        """Add a system message to the memory."""
        self.add_message(SystemMessage(content=message))
    
    def add_function_message(self, name: str, content: str) -> None:
        """Add a function call result message to the memory."""
        self.add_message(FunctionMessage(name=name, content=content))
    
    def clear(self) -> None:
        """Clear all messages from memory."""
        self.messages.clear()
        self.token_count = 0
        logger.debug(f"Cleared short-term memory for session {self.session_id}")
    
    def _enforce_token_limit(self) -> None:
        """Enforce the token limit by removing oldest messages."""
        while self.token_count > self.max_token_limit and len(self.messages) > 1:
            # Always keep the system message if it exists
            if isinstance(self.messages[0], SystemMessage) and len(self.messages) > 1:
                removed_message = self.messages.pop(1)
            else:
                removed_message = self.messages.pop(0)
            
            # Subtract tokens
            self.token_count -= len(removed_message.content) // 4
            logger.debug(f"Removed message from short-term memory due to token limit")
    
    def get_messages(self) -> List[BaseMessage]:
        """Get all messages."""
        return self.messages
    
    @property
    def messages(self) -> List[BaseMessage]:
        """Get all messages."""
        return self._messages
    
    @messages.setter
    def messages(self, messages: List[BaseMessage]) -> None:
        """Set messages."""
        self._messages = messages
