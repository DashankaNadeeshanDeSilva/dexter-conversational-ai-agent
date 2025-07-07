"""Memory manager combining all memory types."""

from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime
from enum import Enum

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage

from app.memory.mongodb_client import MongoDBClient
from app.memory.pinecone_client import PineconeClient
from app.memory.short_term_memory import ShortTermMemory

logger = logging.getLogger(__name__)

class MemoryType(str, Enum):
    """Types of memory in the system."""
    EPISODIC = "episodic"
    SEMANTIC = "semantic" 
    PROCEDURAL = "procedural"
    SHORT_TERM = "short_term"

class MemoryManager:
    """Memory manager for all memory types."""
    
    def __init__(self):
        """Initialize memory manager."""
        self.mongodb_client = MongoDBClient()
        self.pinecone_client = PineconeClient()
        self.short_term_memories = {}  # Map of session_id -> ShortTermMemory
        logger.info("Memory manager initialized")
    
    # Get or create a short-term memory for a session
    def get_short_term_memory(self, session_id: str) -> ShortTermMemory:
        """
        Get or create a short-term memory for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Short-term memory instance
        """
        if session_id not in self.short_term_memories:
            self.short_term_memories[session_id] = ShortTermMemory(session_id)
            logger.debug(f"Created new short-term memory for session {session_id}")
        
        return self.short_term_memories[session_id]
    
    def add_message_to_short_term_memory(self, session_id: str, message: BaseMessage) -> None:
        """
        Add a message to short-term memory.
        
        Args:
            session_id: Session ID
            message: Message to add
        """
        memory = self.get_short_term_memory(session_id)
        memory.add_message(message)
    
    def get_short_term_memory_messages(self, session_id: str) -> List[BaseMessage]:
        """
        Get messages from short-term memory.
        
        Args:
            session_id: Session ID
            
        Returns:
            List of messages
        """
        memory = self.get_short_term_memory(session_id)
        return memory.get_messages()
    
    def clear_short_term_memory(self, session_id: str) -> None:
        """
        Clear short-term memory for a session.
        
        Args:
            session_id: Session ID
        """
        if session_id in self.short_term_memories:
            self.short_term_memories[session_id].clear()
            logger.debug(f"Cleared short-term memory for session {session_id}")
    
    def store_episodic_memory(
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
    
    def store_procedural_memory(
        self, 
        user_id: str, 
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store procedural memory (how to perform tasks, use tools).
        
        Args:
            user_id: User ID
            content: Memory content
            metadata: Optional metadata
            
        Returns:
            Memory ID
        """
        return self.mongodb_client.store_memory(
            user_id=user_id,
            memory_type=MemoryType.PROCEDURAL.value,
            content=content,
            metadata=metadata
        )
    
    def store_semantic_memory(
        self,
        user_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store semantic memory (factual knowledge).
        
        Args:
            user_id: User ID
            text: Text content
            metadata: Optional metadata
            
        Returns:
            Memory ID
        """
        return self.pinecone_client.store_memory(
            user_id=user_id,
            text=text,
            metadata=metadata
        )
    
    def retrieve_episodic_memories(
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
    
    def retrieve_procedural_memories(
        self,
        user_id: str,
        filter_query: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve procedural memories.
        
        Args:
            user_id: User ID
            filter_query: Optional filter query
            limit: Maximum number of results
            
        Returns:
            List of procedural memories
        """
        return self.mongodb_client.retrieve_memories(
            user_id=user_id,
            memory_type=MemoryType.PROCEDURAL.value,
            filter_query=filter_query,
            limit=limit
        )
    
    def retrieve_semantic_memories(
        self,
        user_id: str,
        query: str,
        k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Document, float]]:
        """
        Retrieve semantic memories based on similarity.
        
        Args:
            user_id: User ID
            query: Query text
            k: Number of results
            filter_metadata: Additional metadata filter
            
        Returns:
            List of (document, score) tuples
        """
        # TODO: try to retrive highest similarity (above thresholds) memories from Pinecone DB
        return self.pinecone_client.retrieve_similar(
            user_id=user_id,
            query=query,
            k=k,
            filter_metadata=filter_metadata
        )
    
    def create_conversation(self, user_id: str) -> str:
        """Create a new conversation and return its ID."""
        return self.mongodb_client.create_conversation(user_id)
    
    def add_message_to_conversation(
        self, 
        conversation_id: str, 
        message: Dict[str, Any]
    ) -> bool:
        """Add a message to a conversation."""
        # Store the message as episodic memory as well
        user_id = self.get_conversation_user_id(conversation_id)
        if user_id:
            self.store_episodic_memory(
                user_id=user_id,
                content={
                    "conversation_id": conversation_id,
                    "message": message
                },
                metadata={
                    "timestamp": datetime.utcnow().isoformat(),
                    "message_type": message.get("role", "unknown")
                }
            )
        
        return self.mongodb_client.add_message(conversation_id, message)
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get a conversation by ID."""
        return self.mongodb_client.get_conversation(conversation_id)
    
    def get_conversation_user_id(self, conversation_id: str) -> Optional[str]:
        """Get the user ID for a conversation."""
        conversation = self.get_conversation(conversation_id)
        return conversation.get("user_id") if conversation else None
    
    def get_user_conversations(
        self, 
        user_id: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get conversations for a user."""
        return self.mongodb_client.get_user_conversations(user_id, limit)
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation."""
        return self.mongodb_client.delete_conversation(conversation_id)
    
    def delete_memory(self, memory_id: str, memory_type: MemoryType) -> bool:
        """
        Delete a memory by ID and type.
        
        Args:
            memory_id: Memory ID
            memory_type: Type of memory
            
        Returns:
            Success status
        """
        if memory_type == MemoryType.SEMANTIC:
            return self.pinecone_client.delete_memory(memory_id)
        else:
            return self.mongodb_client.delete_memory(memory_id)
            
    def close(self):
        """Close memory manager and its clients."""
        self.mongodb_client.close()
        logger.info("Memory manager closed")
