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
from app.memory.session_manager import SessionManager
from app.memory.semantic_extractor import SemanticExtractor
from app.memory.episodic_memory import EpisodicMemoryManager
from app.memory.procedural_memory import ProceduralMemoryManager

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
        #self.session_manager = SessionManager(self.mongodb_client)
        self.semantic_extractor = SemanticExtractor()
        self.episodic_memory = EpisodicMemoryManager(self.mongodb_client)
        self.procedural_memory = ProceduralMemoryManager(self.mongodb_client)
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
    
    ### redundant method to add a message to short-term memory 
    def add_message_to_short_term_memory(self, session_id: str, message: BaseMessage) -> None:
        """
        Add a message to short-term memory.
        
        Args:
            session_id: Session ID
            message: Message to add
        """
        memory = self.get_short_term_memory(session_id)
        memory.add_message(message)
    
    ### redundant method
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
    
    # used in test cases
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
        return self.episodic_memory.store_event(
            user_id=user_id,
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
        return self.procedural_memory.store_pattern(
            user_id=user_id,
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
        return self.episodic_memory.retrieve_events(
            user_id=user_id,
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
        return self.procedural_memory.retrieve_patterns(
            user_id=user_id,
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
            self.episodic_memory.store_conversation_message(
                user_id=user_id,
                conversation_id=conversation_id,
                message=message
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
    
    def store_successful_pattern(
        self,
        user_id: str,
        pattern_type: str,
        pattern_description: str,
        context: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store a successful interaction pattern for future reference in Procedural memory.
        
        Args:
            user_id: User ID
            pattern_type: Type of pattern (e.g., "workflow", "problem_solving", "tool_sequence")
            pattern_description: Description of the successful pattern
            context: Context where this pattern was successful
            metadata: Optional metadata
            
        Returns:
            Memory ID
        """
        return self.procedural_memory.store_successful_pattern(
            user_id=user_id,
            pattern_type=pattern_type,
            pattern_description=pattern_description,
            context=context,
            metadata=metadata
        )
    
    # redundant method to retrieve tool usage patterns
    def get_tool_usage_patterns(
        self,
        user_id: str,
        tool_name: Optional[str] = None,
        query_context: Optional[str] = None,
        success_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve tool usage patterns for guidance.
        
        Args:
            user_id: User ID
            tool_name: Specific tool to get patterns for
            query_context: Context to match against
            success_only: Whether to only return successful patterns
            
        Returns:
            List of tool usage patterns
        """
        return self.procedural_memory.get_tool_usage_patterns(
            user_id=user_id,
            tool_name=tool_name,
            query_context=query_context,
            success_only=success_only
        )
    
    def close(self):
        """Close memory manager and its clients."""
        self.mongodb_client.close()
        logger.info("Memory manager closed")
    
    def extract_semantic_facts(
        self,
        user_message: str,
        agent_response: str,
        conversation_context: Optional[List[Dict[str, Any]]] = None,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract factual knowledge from conversation using cognitive principles.
        
        This method delegates to the SemanticExtractor module for modular processing.
        
        Args:
            user_message: The user's input message
            agent_response: The agent's response
            conversation_context: Optional context from recent conversation
            user_id: User ID for personalized extraction
            
        Returns:
            List of extracted semantic facts with metadata
        """
        return self.semantic_extractor.extract_facts(
            user_message=user_message,
            agent_response=agent_response,
            conversation_context=conversation_context,
            user_id=user_id
        )
    
    def store_extracted_semantic_facts(
        self,
        user_id: str,
        facts: List[Dict[str, Any]],
        conversation_metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Store extracted facts in semantic memory with proper categorization.
        
        Args:
            user_id: User ID
            facts: List of extracted semantic facts
            conversation_metadata: Optional metadata about the source conversation
            
        Returns:
            List of memory IDs for stored facts
        """
        stored_memory_ids = []
        
        for fact in facts:
            # Prepare metadata for storage
            storage_metadata = {
                "fact_category": fact.get("category"),
                "confidence": fact.get("confidence"),
                "source_type": fact.get("source_type"),
                "entities": fact.get("entities", []),
                "context_requirement": fact.get("context_requirement"),
                "extraction_timestamp": fact.get("extraction_timestamp"),
                "extraction_method": fact.get("extraction_method"),
                **(conversation_metadata or {})
            }
            
            # Store in semantic memory
            memory_id = self.store_semantic_memory(
                user_id=user_id,
                text=fact["fact"],
                metadata=storage_metadata
            )
            
            stored_memory_ids.append(memory_id)
            logger.debug(f"Stored semantic fact: {fact['fact'][:50]}... (ID: {memory_id})")
        
        return stored_memory_ids
    
    # TODO: Consolidation orchestration and management - deferred for future implementation
    # This method will be fully implemented in the next phase after thorough discussion
    def consolidate_session_knowledge(
        self,
        user_id: str,
        session_id: str,
        conversation_id: str
    ) -> List[str]:
        """
        Consolidate knowledge from an entire session using cognitive principles.
        
        DEFERRED: This functionality is temporarily deferred pending 
        consolidation orchestration design and implementation.
        
        Args:
            user_id: User ID
            session_id: Session ID
            conversation_id: Conversation ID
            
        Returns:
            List of memory IDs for consolidated knowledge (empty for now)
        """
        logger.info(f"Session knowledge consolidation deferred for session {session_id}")
        return []  # Return empty list until consolidation is properly implemented
