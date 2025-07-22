"""Semantic knowledge retrieval tool for RAG-like functionality using Pinecone."""

import logging
from typing import Optional
from langchain_core.tools import BaseTool
from app.memory.pinecone_client import PineconeClient
from app.config import settings

logger = logging.getLogger(__name__)

class SemanticRetrievalTool(BaseTool):
    """Tool for semantic knowledge retrieval using Pinecone vector database."""
    
    name = "semantic_knowledge_search"
    description = "Search semantic knowledge base for relevant information using vector similarity"
    
    def __init__(self, pinecone_client: Optional[PineconeClient] = None, **kwargs):
        """Initialize the semantic retrieval tool."""
        super().__init__(**kwargs)
        self.pinecone_client = PineconeClient(settings.PINECONE_KNOWLEDGE_INDEX)
        
    def _run(self, query: str, max_results: int = 5, similarity_threshold: float = 0.7) -> str:
        """
        Run the semantic retrieval tool.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            similarity_threshold: Minimum similarity score threshold
            
        Returns:
            Formatted string with relevant semantic knowledge
        """
        try:
            results = self.pinecone_client.query(
                query_text=query,
                top_k=max_results,
                filter_metadata={"content_type": "knowledge"}
            )
            
            if not results or not results.get('matches'):
                return "No relevant semantic knowledge found."
            
            # Filter results by similarity threshold
            filtered_results = [
                match for match in results['matches'] 
                if match.get('score', 0) >= similarity_threshold
            ]
            
            if not filtered_results:
                logger.info(f"No results above similarity threshold {similarity_threshold} for query: {query}")
                return f"No semantic knowledge found above similarity threshold ({similarity_threshold})."
            
            # Format results for readability
            formatted_results = []
            for i, match in enumerate(filtered_results, 1):
                metadata = match.get('metadata', {})
                content = metadata.get('text', 'No content available')
                source = metadata.get('source', 'Unknown source')
                score = match.get('score', 0)
                
                # Better formatted result with clear structure
                formatted_result = (
                    f"{i}. {content}\n"
                    f"   Source: {source}\n" 
                    f"   Relevance Score: {score:.3f}"
                )
                formatted_results.append(formatted_result)
            
            return f"Relevant semantic knowledge:\n\n" + "\n\n".join(formatted_results)
            
        except Exception as e:
            logger.error(f"Error during semantic knowledge retrieval: {e}")
            return f"Error retrieving semantic knowledge: {str(e)}"
