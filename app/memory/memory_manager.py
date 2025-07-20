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
        return self.store_procedural_memory(
            user_id=user_id,
            content={
                "pattern_type": pattern_type,
                "successful_pattern": pattern_description,
                "context": context,
                "success": True
            },
            metadata=metadata
        )
    
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
        
        return self.retrieve_procedural_memories(
            user_id=user_id,
            filter_query=filter_query,
            limit=10
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
        
        Based on cognitive science research, this method identifies:
        1. Declarative facts (explicit knowledge shared)
        2. Implicit preferences and traits revealed
        3. Domain knowledge and concepts discussed
        4. Relational knowledge (connections between entities)
        
        Args:
            user_message: The user's input message
            agent_response: The agent's response
            conversation_context: Optional context from recent conversation
            user_id: User ID for personalized extraction
            
        Returns:
            List of extracted semantic facts with metadata
        """
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import JsonOutputParser
        import json
        
        # Initialize LLM for fact extraction
        extraction_llm = ChatOpenAI(
            model="gpt-4",  # Use more capable model for extraction
            temperature=0.1,  # Low temperature for consistent extraction
            api_key=settings.OPENAI_API_KEY
        )
        
        # Create extraction prompt based on cognitive science principles
        extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert cognitive scientist specializing in semantic memory extraction. 
            Your task is to extract factual knowledge from conversations that should be stored in long-term semantic memory.

            COGNITIVE PRINCIPLES FOR SEMANTIC MEMORY:
            1. **Declarative Facts**: Explicit factual statements that can be recalled independently
            2. **Conceptual Knowledge**: Definitions, categories, and conceptual relationships
            3. **Personal Attributes**: Stable traits, preferences, and characteristics revealed
            4. **Domain Knowledge**: Subject-matter expertise and domain-specific information
            5. **Relational Knowledge**: Relationships between entities, people, concepts

            EXTRACTION CRITERIA:
            - Extract facts that are GENERALIZABLE beyond this specific conversation
            - Focus on STABLE information that won't change rapidly
            - Identify IMPLICIT knowledge revealed through conversation patterns
            - Avoid conversation-specific details (store those in episodic memory)
            - Extract knowledge that could inform FUTURE interactions

            OUTPUT FORMAT: Return a JSON array of fact objects, each with:
            {{
                "fact": "The factual statement in clear, declarative form",
                "category": "personal_attribute|domain_knowledge|conceptual_knowledge|relational_knowledge|preference",
                "confidence": 0.0-1.0,
                "source_type": "explicit|implicit|inferred",
                "entities": ["list", "of", "key", "entities"],
                "context_requirement": "none|domain_specific|personal_context"
            }}

            If no significant semantic facts are found, return an empty array []."""),
            
            ("human", """CONVERSATION TO ANALYZE:

User Message: {user_message}

Agent Response: {agent_response}

{context_prompt}

Extract semantic facts that should be stored in long-term memory according to cognitive principles.""")
        ])
        
        # Prepare context if available
        context_prompt = ""
        if conversation_context:
            recent_messages = conversation_context[-3:]  # Last 3 exchanges for context
            context_text = "\n".join([
                f"- {msg.get('role', 'unknown')}: {msg.get('content', '')}"
                for msg in recent_messages
            ])
            context_prompt = f"\nRECENT CONVERSATION CONTEXT:\n{context_text}\n"
        
        # Set up JSON parser
        parser = JsonOutputParser()
        
        # Create the extraction chain
        extraction_chain = extraction_prompt | extraction_llm | parser
        
        try:
            # Extract facts
            extracted_facts = extraction_chain.invoke({
                "user_message": user_message,
                "agent_response": agent_response,
                "context_prompt": context_prompt
            })
            
            # Validate and enhance extracted facts
            validated_facts = []
            for fact in extracted_facts:
                if self._validate_semantic_fact(fact):
                    # Add extraction metadata
                    fact.update({
                        "extraction_timestamp": datetime.utcnow().isoformat(),
                        "extraction_method": "llm_cognitive_principles",
                        "user_id": user_id
                    })
                    validated_facts.append(fact)
            
            logger.info(f"Extracted {len(validated_facts)} semantic facts from conversation")
            return validated_facts
            
        except Exception as e:
            logger.error(f"Error extracting semantic facts: {e}")
            return []
    
    def _validate_semantic_fact(self, fact: Dict[str, Any]) -> bool:
        """
        Validate extracted semantic facts for quality and relevance.
        
        Args:
            fact: Extracted fact dictionary
            
        Returns:
            True if fact is valid for semantic storage
        """
        required_fields = ["fact", "category", "confidence"]
        
        # Check required fields
        if not all(field in fact for field in required_fields):
            return False
        
        # Check confidence threshold
        if fact.get("confidence", 0) < 0.3:  # Minimum confidence threshold
            return False
        
        # Check fact content quality
        fact_text = fact.get("fact", "").strip()
        if len(fact_text) < 10:  # Too short to be meaningful
            return False
        
        # Check for conversation-specific content that shouldn't be in semantic memory
        conversation_indicators = [
            "in this conversation", "just now", "earlier today", 
            "you mentioned", "as we discussed", "right now"
        ]
        
        if any(indicator in fact_text.lower() for indicator in conversation_indicators):
            return False
        
        return True
    
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
    
    def consolidate_session_knowledge(
        self,
        user_id: str,
        session_id: str,
        conversation_id: str
    ) -> List[str]:
        """
        Consolidate knowledge from an entire session using cognitive principles.
        
        This method implements the "big picture" approach by analyzing
        patterns and themes across an entire conversation session.
        
        Args:
            user_id: User ID
            session_id: Session ID
            conversation_id: Conversation ID
            
        Returns:
            List of memory IDs for consolidated knowledge
        """
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import JsonOutputParser
        
        # Get the full conversation
        conversation = self.memory_manager.get_conversation(conversation_id)
        if not conversation or not conversation.get("messages"):
            logger.warning(f"No conversation found for consolidation: {conversation_id}")
            return []
        
        messages = conversation["messages"]
        if len(messages) < 4:  # Need at least 2 exchanges to consolidate
            logger.debug("Conversation too short for knowledge consolidation")
            return []
        
        # Initialize LLM for consolidation
        consolidation_llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            api_key=settings.OPENAI_API_KEY
        )
        
        # Create consolidation prompt
        consolidation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a cognitive scientist specializing in knowledge consolidation from conversations.

            Your task is to analyze an ENTIRE conversation session and extract HIGH-LEVEL semantic knowledge that emerges from the conversation as a whole, not just individual exchanges.

            CONSOLIDATION PRINCIPLES:
            1. **Thematic Knowledge**: Overarching themes and topics discussed
            2. **Progressive Understanding**: Knowledge that builds up over multiple exchanges  
            3. **Implicit Patterns**: User behaviors, preferences, and traits revealed across the session
            4. **Domain Expertise**: Subject matter knowledge demonstrated or discussed
            5. **Relationship Dynamics**: How the user interacts with AI/information

            LOOK FOR:
            - Recurring topics or interests
            - Evolution of understanding throughout the conversation
            - Persistent preferences or constraints
            - Domain knowledge areas the user is interested in
            - Problem-solving patterns and approaches
            - Learning objectives or goals that emerge

            OUTPUT FORMAT: JSON array of consolidated knowledge objects:
            {{
                "knowledge": "Consolidated knowledge statement",
                "type": "thematic|progressive|behavioral|domain|relational",
                "confidence": 0.0-1.0,
                "evidence_count": number_of_supporting_exchanges,
                "scope": "session|domain|personal_trait",
                "entities": ["key", "entities", "involved"]
            }}

            Focus on knowledge that is MORE VALUABLE than individual facts - knowledge that emerges from the conversation pattern."""),
            
            ("human", """FULL CONVERSATION SESSION TO CONSOLIDATE:

            {conversation_text}

            Extract consolidated knowledge that emerges from this complete conversation session.""")
        ])
        
        # Prepare conversation text
        conversation_text = ""
        for i, msg in enumerate(messages):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            conversation_text += f"{i+1}. {role.upper()}: {content}\n\n"
        
        # Set up parser
        parser = JsonOutputParser()
        
        # Create consolidation chain
        consolidation_chain = consolidation_prompt | consolidation_llm | parser
        
        try:
            # Extract consolidated knowledge
            consolidated_knowledge = consolidation_chain.invoke({
                "conversation_text": conversation_text
            })
            
            # Store consolidated knowledge
            stored_ids = []
            for knowledge in consolidated_knowledge:
                if knowledge.get("confidence", 0) >= 0.4:  # Higher threshold for consolidated knowledge
                    
                    memory_id = self.memory_manager.store_semantic_memory(
                        user_id=user_id,
                        text=knowledge["knowledge"],
                        metadata={
                            "knowledge_type": "consolidated",
                            "consolidation_type": knowledge.get("type"),
                            "confidence": knowledge.get("confidence"),
                            "evidence_count": knowledge.get("evidence_count"),
                            "scope": knowledge.get("scope"),
                            "entities": knowledge.get("entities", []),
                            "source_conversation": conversation_id,
                            "source_session": session_id,
                            "consolidation_timestamp": datetime.utcnow().isoformat()
                        }
                    )
                    stored_ids.append(memory_id)
            
            logger.info(f"Consolidated {len(stored_ids)} knowledge items from session {session_id}")
            return stored_ids
            
        except Exception as e:
            logger.error(f"Error consolidating session knowledge: {e}")
            return []
