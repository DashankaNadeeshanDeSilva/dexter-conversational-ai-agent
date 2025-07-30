"""Semantic knowledge retrieval tool for RAG-like functionality using Pinecone."""

import logging
from langchain_core.tools import BaseTool
from app.memory.pinecone_client import PineconeClient
from app.config import settings
from pydantic import PrivateAttr

logger = logging.getLogger(__name__)

class SemanticRetrievalTool(BaseTool):
    """Tool for semantic knowledge retrieval using Pinecone vector database."""
    
    name: str = "semantic_knowledge_search"
    description: str = "Search semantic knowledge base for relevant information using vector similarity"
    _pinecone_client: PineconeClient = PrivateAttr() # Use PrivateAttr for Non-Pydantic Field PineconeClient
    
    def __init__(self, **kwargs):
        """Initialize the semantic retrieval tool."""
        super().__init__(**kwargs)
        self._pinecone_client = PineconeClient(settings.PINECONE_KNOWLEDGE_INDEX)
        
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
            results = self._pinecone_client.query_knowledge(
                query=query,
                top_k=max_results,
                filter_metadata={"content_type": "knowledge"}
            )

            if not results: # List[Tuple[Document, float]]
                return "No relevant semantic knowledge found."
            
            # Filter results by similarity threshold
            filtered_results = [
                (doc, score) for doc, score in results if score >= similarity_threshold
            ]
            
            if not filtered_results:
                logger.info(f"No results above similarity threshold {similarity_threshold} for query: {query}")
                return f"No semantic knowledge found above similarity threshold ({similarity_threshold})."
            
            # Format results for readability
            formatted_results = []
            for i, (doc, score) in enumerate(filtered_results, 1):
                content = doc.page_content.strip()
                source = doc.metadata.get('source', 'Unknown Source')
        
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
