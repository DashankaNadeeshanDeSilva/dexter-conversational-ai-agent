"""Internet search tool for the agent using DuckDuckGo."""

from typing import Optional, Type
from pydantic import Field
import logging
from langchain_core.tools import Tool, BaseTool
from ddgs import DDGS
from pydantic import BaseModel, Field
from langchain_core.callbacks import CallbackManagerForToolRun

logger = logging.getLogger(__name__)

class WebSearchInput(BaseModel):
    """Input schema for the multiplication tool."""
    query: str = Field(..., description="The search query to perform on the internet.")

class WebSearchTool(BaseTool):
    """Tool for internet search using DuckDuckGo."""

    name: str ="internet_search"
    description: str ="Search on the internet for a query and returns search results."     
    args_schema: Type[BaseModel] = WebSearchInput

    def _run(self, query: str, max_results: int = 5, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Run internet search for the query and return formatted results."""
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


if __name__ == "__main__":
    # Create the tool instance
    tool = WebSearchTool(max_results=3)

    # Run a test query
    query = "latest AI news 2025"
    result = tool.run(query)

    # Print the results
    print("\n===== DuckDuckGo Search Results =====\n")
    print(result)