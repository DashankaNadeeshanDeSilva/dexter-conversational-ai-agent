"""Procedural memory management for storing successful patterns and tool usage."""

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

class ProceduralMemoryManager:
    """Manages procedural memory - storing successful patterns and tool usage."""
    
    def __init__(self, mongodb_client: MongoDBClient):
        """
        Initialize procedural memory manager.
        
        Args:
            mongodb_client: MongoDB client for storage
        """
        self.mongodb_client = mongodb_client
        logger.info("Procedural memory manager initialized")
    
    def store_pattern(
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
    
    def store_successful_pattern(
        self,
        user_id: str,
        pattern_type: str,
        pattern_description: str,
        context: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store a successful interaction pattern for future reference.
        
        Args:
            user_id: User ID
            pattern_type: Type of pattern (e.g., "workflow", "problem_solving", "tool_sequence")
            pattern_description: Description of the successful pattern
            context: Context where this pattern was successful
            metadata: Optional metadata
            
        Returns:
            Memory ID
        """
        return self.store_pattern(
            user_id=user_id,
            content={
                "pattern_type": pattern_type,
                "successful_pattern": pattern_description,
                "context": context,
                "success": True
            },
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
        filter_query = {}
        
        if tool_name:
            filter_query["content.tool"] = tool_name
            
        if success_only:
            filter_query["content.success"] = True
            
        if query_context:
            filter_query["content.query_context"] = {"$regex": query_context, "$options": "i"}
        
        return self.mongodb_client.retrieve_memories(
            user_id=user_id,
            memory_type=MemoryType.PROCEDURAL.value,
            filter_query=filter_query,
            limit=10
        )
    
    def retrieve_patterns(
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
