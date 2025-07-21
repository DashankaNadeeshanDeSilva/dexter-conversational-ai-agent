"""Episodic memory management for storing conversation events and interactions."""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
from enum import Enum

from app.memory.mongodb_client import MongoDBClient

logger = logging.getLogger(__name__)

class MemoryType(str, Enum):
    """Types of memory in the system."""
    EPISODIC = "episodic"
    SEMANTIC = "semantic" 
    PROCEDURAL = "procedural"
    SHORT_TERM = "short_term"

class EpisodicMemoryManager:
    """Manages episodic memory - storing specific events, conversations, and interactions."""
    
    def __init__(self, mongodb_client: MongoDBClient):
        """
        Initialize episodic memory manager.
        
        Args:
            mongodb_client: MongoDB client for storage
        """
        self.mongodb_client = mongodb_client
        logger.info("Episodic memory manager initialized")
    
    def store_event(
        self, 
        user_id: str, 
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store episodic memory (specific events, conversations, interactions).
        
        Args:
            user_id: User ID
            content: Memory content
            metadata: Optional metadata
            
        Returns:
            Memory ID
        """
        return self.mongodb_client.store_memory(
            user_id=user_id,
            memory_type=MemoryType.EPISODIC.value,
            content=content,
            metadata=metadata
        )
    
    def store_conversation_message(
        self,
        user_id: str,
        conversation_id: str,
        message: Dict[str, Any]
    ) -> str:
        """
        Store a conversation message as episodic memory.
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID
            message: Message content
            
        Returns:
            Memory ID
        """
        return self.store_event(
            user_id=user_id,
            content={
                "conversation_id": conversation_id,
                "message": message
            },
            metadata={
                "timestamp": datetime.utcnow().isoformat(),
                "message_type": message.get("role", "unknown"),
                "event_type": "conversation_message"
            }
        )
    
    def retrieve_events(
        self,
        user_id: str,
        filter_query: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve episodic memories.
        
        Args:
            user_id: User ID
            filter_query: Optional filter query
            limit: Maximum number of results
            
        Returns:
            List of episodic memories
        """
        return self.mongodb_client.retrieve_memories(
            user_id=user_id,
            memory_type=MemoryType.EPISODIC.value,
            filter_query=filter_query,
            limit=limit
        )
    
    # redundant method to retrieve conversation events
    def retrieve_conversation_events(
        self,
        user_id: str,
        conversation_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieve episodic memories for a specific conversation.
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID
            limit: Maximum number of results
            
        Returns:
            List of conversation episodic memories
        """
        filter_query = {"content.conversation_id": conversation_id}
        
        return self.retrieve_events(
            user_id=user_id,
            filter_query=filter_query,
            limit=limit
        )
