## Question: 

Ok i was able to run the app. when I ran chat endpoint i got this outcome from the agent

{
"conversation_id": "688a8a939687546434794c57",
"session_id": "e62df255-0b78-448e-a88d-ca01feb4014a",
"message": {
"role": "assistant",
"content": "I'm sorry, I encountered an error: 'WebSearchTool' object has no attribute 'to_pydantic_tool'",
"timestamp": "2025-07-31T08:57:39.289576"
}
}

## Answer:
**Seems like there is an error with running the WebSearchTool class.**

The error 'WebSearchTool' object has no attribute 'to_pydantic_tool' means that your WebSearchTool is being passed to LangGraph/LangChain as a tool, but it does not implement the expected interface for tools in the latest LangChain/LangGraph versions.

### Why This Happens
LangChain v0.1+ and LangGraph expect tools to be created using the @tool decorator or by subclassing Tool from langchain_core.tools, not just BaseTool.
The to_pydantic_tool method is part of the new tool interface, and your custom class does not provide it.
How to Fix
Option 1: Use the @tool Decorator (Recommended for Simplicity)
If your tool is just a function, use the decorator:

```bash
from langchain_core.tools import tool

@tool
def web_search(query: str, max_results: int = 5) -> str:
    # ... your search logic ...
```

Option 2: Subclass Tool and Implement Proper Interface
If you want a class-based tool, subclass Tool and implement the required methods:

```bash
from langchain_core.tools import Tool

def web_search_fn(query: str, max_results: int = 5) -> str:
    # ... your search logic ...
    return "results..."

web_search_tool = Tool(
    name="internet_search",
    description="Search the internet for information about a query using DuckDuckGo",
    func=web_search_fn
)
```

Option 3: If You Want to Keep a Class, Use the New Tool API
If you want to keep your class, you must ensure it matches the new interface.
But the simplest fix is to switch to the function-based or Tool-object approach above.

What To Do Now
Replace your WebSearchTool class with a function-based tool using the @tool decorator, or wrap your function with Tool.
Update your agent/tool registration to use the new tool object/function.
Example: Function-Based Tool:
```bash
from langchain_core.tools import tool
from duckduckgo_search import DDGS
import logging

logger = logging.getLogger(__name__)

@tool
def web_search(query: str, max_results: int = 5) -> str:
    """Search the internet for information about a query using DuckDuckGo."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            logger.warning(f"No search results found for: {query}")
            return "No search results found."
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
```

Then, register web_search as your tool in your agent/tool setup.


```bash
"""Internet search tool for the agent using DuckDuckGo."""

from typing import Dict, Any, Optional
import logging
from langchain_core.tools import Tool
from pydantic import Field
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

class WebSearchTool(Tool):
    """Tool for internet search using DuckDuckGo."""
    
    name: str = "internet_search"
    description: str = "Search on the internet for a query and returns search results."

    def __init__(self, max_results: int = 5):

        def search_fn(query: str) -> str:
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

        super().__init__(
            name=self.name,
            description=self.description,
            func=search_fn, 
        )
    
    # Optional convenience method
    def run(self, query: str) -> str:
        """Web search manual testing."""
        return self.func(query)
       


```


```bash

"""Semantic knowledge retrieval tool for RAG-like functionality using Pinecone."""

import logging
from langchain_core.tools import BaseTool, Tool
from app.memory.pinecone_client import PineconeClient
from app.config import settings
from pydantic import PrivateAttr, Field

logger = logging.getLogger(__name__)

class SemanticRetrievalTool(Tool):
    """Tool for semantic knowledge retrieval using Pinecone vector database."""
    
    name: str = "semantic_knowledge_search"
    description: str = "Search semantic knowledge base for relevant information using vector similarity"
    _pinecone_client: PineconeClient = PrivateAttr() # Use PrivateAttr for Non-Pydantic Field PineconeClient
    max_results: int = Field(default=5, description="Maximum number of search results")
    similarity_threshold: float = 0.7
    
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


```


```bash
# Alternative approach using @tool decorator (often more compatible)
from langchain_core.tools import tool

@tool
def internet_search_tool(query: str, max_results: int = 5) -> str:
    """Search on the internet for a query and returns search results.
    
    Args:
        query: The search query to look up on the internet
        max_results: Maximum number of search results to return
    """
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
```