"""Internet search tool for the agent using DuckDuckGo."""

from typing import Dict, Any, Optional
import logging
from langchain_core.tools import BaseTool
from langchain_core.pydantic_v1 import Field
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

class WebSearchTool(BaseTool):
    """Tool for internet search using DuckDuckGo."""
    
    name = "internet_search"
    description = "Search the internet for information about a query using DuckDuckGo"
       
    def _run(self, query: str, max_results: int = 5) -> str:
        """Run the search tool."""
        try:          
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            
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
