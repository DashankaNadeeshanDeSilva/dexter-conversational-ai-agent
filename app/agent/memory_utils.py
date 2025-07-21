import logging
from typing import List, Dict, Any, Optional, Tuple
from langchain_core.documents import Document

class AgentMemoryUtils:
    """Utility class for agent memory operations."""

    def __init__(self, memory_manager):
        """Initialize the memory utilities with the memory manager."""
        self.memory_manager = memory_manager

    def retrive_memory_context(self, user_id: str, query: str) -> str:
        """Retireve and format memory context based on user query"""

        # retrive semantic memories
        semantic_memories = self.get_semantic_context(user_id, query, k=3)
        # retrive episodic memories
        episodic_memories = self.get_episodic_context(user_id, query, limit=3)
        # retrive procedural memories
        procedural_memories = self.get_procedural_context(user_id, query, limit=5)

        # combine all memory contexts
        if semantic_memories or episodic_memories or procedural_memories:
            return memory_context = self.combine_memory_contexts(
                semantic_memories=semantic_memories,
                episodic_memories=episodic_memories,
                procedural_memories=procedural_memories
            )
        else:
            return "No relevant information found in memory."
            
    def get_semantic_context(self, user_id: str, query: str, k: int = 3) -> List[Tuple[Document, float]]:
        """Retrieve and format semantic memories."""
        # Get semantic memories (existing)
        semantic_memories = self.memory_manager.retrieve_semantic_memories(
            user_id=user_id,
            query=query,
            k=k
        )
        return semantic_memories

    def get_episodic_context(self, user_id: str, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Retrieve and format episodic memories."""            
        episodic_memories = self.memory_manager.retrieve_episodic_memories(
            user_id=user_id,
            filter_query={
                "content.message.content": {"$regex": query, "$options": "i"}
            },
            limit=limit
        )
        return episodic_memories

    def get_procedural_context(self, user_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve and format procedural memories."""            
        procedural_memories = self.memory_manager.retrieve_procedural_memories(
            user_id=user_id,
            filter_query={
                "$or": [
                    {"content.query_context": {"$regex": query[:50], "$options": "i"}},
                    {"content.tool": {"$exists": True}},
                    {"content.successful_pattern": {"$exists": True}}
                ]
            },
            limit=limit
        )
        return procedural_memories

    def combine_memory_contexts(
        self,
        semantic_memories: List[Tuple[Document, float]],
        episodic_memories: List[Dict[str, Any]],
        procedural_memories: List[Dict[str, Any]]
    ) -> str:
        """Combine memory contexts into a single string."""
        if semantic_memories or episodic_memories or procedural_memories:
            memory_context = "Relevant information from memory:\n"
        
            # Add semantic context
            for doc, score in semantic_memories:
                memory_context += f"- Fact: {doc.page_content} (relevance: {score:.2f})\n"
        
            # Add episodic context
            for episode in episodic_memories:
                memory_context += f"- Past interaction: {episode['content']['message']['content']}\n"
                    
            # Add procedural guidance
            if procedural_memories:
                memory_context += "\nLearned patterns and tool usage:\n"
                for procedure in procedural_memories:
                    if "tool" in procedure["content"]:
                        tool_name = procedure["content"]["tool"]
                        args = procedure["content"].get("arguments", {})
                        memory_context += f"- For similar queries, successfully used {tool_name} with args: {args}\n"
                    elif "successful_pattern" in procedure["content"]:
                        pattern = procedure["content"]["successful_pattern"]
                        memory_context += f"- Successful approach: {pattern}\n"
        
            return memory_context.strip()
        
        else:
            return "No relevant information found in memory."

