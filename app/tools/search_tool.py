"""Internet search tool for the agent using DuckDuckGo."""

from typing import Dict, Any, Optional
import logging
from langchain_core.tools import BaseTool
from langchain_core.pydantic_v1 import Field
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

class SearchTool(BaseTool):
    """Tool for internet search using DuckDuckGo."""
    
    name = "internet_search"
    description = "Search the internet for information about a query using DuckDuckGo"
    
    max_results: int = Field(default=5, description="Maximum number of search results to return")
    
    def _run(self, query: str, **kwargs) -> str:
        """Run the search tool."""
        try:
            logger.info(f"Performing internet search: {query}")
            
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=self.max_results))
            
            if not results:
                logger.warning(f"No search results found for: {query}")
                return "No search results found."
                
            # Format results
            formatted_results = []
            for i, result in enumerate(results, 1):
                title = result.get("title", "No title")
                body = result.get("body", "No content")
                url = result.get("href", "No URL")
                
                formatted_result = f"{i}. {title}\n{body}\nSource: {url}\n"
                formatted_results.append(formatted_result)
                
            return "\n".join(formatted_results)
            
        except Exception as e:
            logger.error(f"Error during internet search: {e}")
            return f"Error performing search: {str(e)}"
    
    async def _arun(self, query: str, **kwargs) -> str:
        """Run the search tool asynchronously."""
        # DuckDuckGo doesn't have an async API, so just call the sync version
        return self._run(query, **kwargs)
