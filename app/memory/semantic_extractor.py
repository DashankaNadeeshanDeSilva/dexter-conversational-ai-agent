"""Semantic memory extraction using cognitive principles."""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.config import settings

logger = logging.getLogger(__name__)

class SemanticExtractor:
    """Handles extraction of semantic facts from conversations."""
    
    def __init__(self):
        """Initialize the semantic extractor."""
        self.extraction_llm = ChatOpenAI(
            model="gpt-4",  # Use more capable model for extraction
            temperature=0.1,  # Low temperature for consistent extraction
            api_key=settings.OPENAI_API_KEY
        )
        
        # Create extraction prompt based on cognitive science principles
        self.extraction_prompt = ChatPromptTemplate.from_messages([
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
        
        # Set up JSON parser
        self.parser = JsonOutputParser()
        
        # Create the extraction chain
        self.extraction_chain = self.extraction_prompt | self.extraction_llm | self.parser
        
        logger.info("Semantic extractor initialized")
    
    def extract_facts(
        self,
        user_message: str,
        agent_response: str,
        conversation_context: Optional[List[Dict[str, Any]]] = None,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract factual knowledge from conversation using cognitive principles.
        
        Args:
            user_message: The user's input message
            agent_response: The agent's response
            conversation_context: Optional context from recent conversation
            user_id: User ID for personalized extraction
            
        Returns:
            List of extracted semantic facts with metadata
        """
        # Prepare context if available
        context_prompt = ""
        if conversation_context:
            recent_messages = conversation_context[-3:]  # Last 3 exchanges for context
            context_text = "\n".join([
                f"- {msg.get('role', 'unknown')}: {msg.get('content', '')}"
                for msg in recent_messages
            ])
            context_prompt = f"\nRECENT CONVERSATION CONTEXT:\n{context_text}\n"
        
        try:
            # Extract facts
            extracted_facts = self.extraction_chain.invoke({
                "user_message": user_message,
                "agent_response": agent_response,
                "context_prompt": context_prompt
            })
            
            # Validate and enhance extracted facts
            validated_facts = []
            for fact in extracted_facts:
                if self._validate_fact(fact):
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
    
    def _validate_fact(self, fact: Dict[str, Any]) -> bool:
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
