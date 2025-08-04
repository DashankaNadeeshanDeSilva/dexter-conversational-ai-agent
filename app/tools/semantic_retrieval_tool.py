"""Semantic knowledge retrieval tool for RAG-like functionality using Pinecone."""

import logging
from typing import Optional, Type
from langchain_core.tools import BaseTool, Tool
from langchain_core.callbacks import CallbackManagerForToolRun
from app.db_clients.pinecone_client import PineconeClient
from app.config import settings
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

NAME: str = "semantic_knowledge_search"
DESCRIPTION: str = "Search semantic knowledge base for relevant information using vector similarity"

#pinecone_client = PineconeClient(settings.PINECONE_KNOWLEDGE_INDEX)

class SemanticRetrievalInput(BaseModel):
    """Input schema for semantic retrival tool)"""
    query: str = Field(..., description="The search query to find relevent semantic knowledge")
    max_results: int = Field(default=5, description="Maximum number of semantic seaech results to return")
    similarity_threshold: float = Field(default=0.7, description="Minumum similarity score threshold")

class SemanticRetrievalTool(BaseTool):
    """Tool for semantic knowledge retrieval using Pinecone vector database."""
    
    name: str = "semantic_knowledge_search"
    description: str = "Search semantic knowledge base for relevant information using vector similarity"
    args_schema: Type[BaseModel] = SemanticRetrievalInput
    
    def _run(self, query: str, max_results: int = 5, similarity_threshold: float = 0.7, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Run the semantic retrieval tool.
        Args:
            query: The search query
            max_results: Maximum number of results to return
            similarity_threshold: Minimum similarity score threshold
            
        Returns:
            Formatted string with relevant semantic knowledge
        """ 
        try:
            # Initialize Pinecone client
            pinecone_client = PineconeClient(settings.PINECONE_KNOWLEDGE_INDEX)

            # Query the knowledge base
            results = pinecone_client.query_knowledge(
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

if __name__ == "__main__":
    semantic_retrieval_tool = SemanticRetrievalTool()

    query = "What are your establishment/office openning hours ?"
    result = semantic_retrieval_tool._run(query)

    logger.info("Retrieved context: ", result)