"""Product search tool for discovering products, checking prices, and inventory."""

import logging
import re
import json
from typing import Dict, List, Any, Optional, Type
from langchain_core.tools import BaseTool, Tool
from pydantic import BaseModel, Field
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import PrivateAttr
from langchain_openai import ChatOpenAI
from app.tools.database_client import DatabaseClient
from app.tools.tool_config import PRODUCT_CATEGORIES
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize database client
try:        
    _DB_CLIENT = DatabaseClient()
except Exception as e:
    logger.error(f"Failed to initialize Database client at import: {e}")
    _DB_CLIENT = None

# Initialize LLM client
try:
    _LLM_CLIENT = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        temperature=0.1,  # Low temperature for consistent structured output
        api_key=settings.OPENAI_API_KEY
    )
except Exception as e:
    logger.error(f"Failed to initialize LLM client at import: {e}")
    _LLM_CLIENT = None

class ProductSearchInput(BaseModel):
    """Input schema for product search tool"""
    query: str = Field(..., description="The search query to find products from the database")
    max_results: int = Field(default=5, description="Maximum number of products results to return")

class ProductSearchTool(BaseTool):
    """Tool for searching and discovering products in the database using LLM-based query understanding."""
    
    name: str = "product_search"
    description: str = "Search for products, check prices, inventory, and product information from the product database using natural language understanding"
    args_schema: Type[BaseModel] = ProductSearchInput

    def _run(self, query: str, max_results: int = 5, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Execute product search based on query using LLM for understanding."""
        try:
            if _DB_CLIENT is None:
                return "Product Database is not available right now."
            
            if _LLM_CLIENT is None:
                return "LLM service is not available. Falling back to basic search."
            
            # Use LLM to extract filters and search text
            extracted_filters = self._extract_filters_with_llm(query)
            
            if not extracted_filters:
                # Fallback to basic search if LLM fails
                logger.warning("LLM extraction failed, using fallback method")
                extracted_filters = self._fallback_extract_filters(query)
            
            # Build MongoDB filters
            filters = self._build_mongodb_filters(extracted_filters)
            
            # Get clean search text
            search_text = extracted_filters.get('search_text', query)
            
            # Search products
            results = _DB_CLIENT.search_products(
                query_text=search_text if search_text else None,
                filters=filters if filters else None,
                limit=max_results
            )
            
            if not results:
                return "No products found matching your criteria."
            
            # Format results
            return _format_product_results(results)
            
        except Exception as e:
            logger.error(f"Error during product search: {e}")
            return f"Error searching products: {str(e)}"

    def _extract_filters_with_llm(self, query: str) -> Optional[Dict[str, Any]]:
        """Use LLM to extract filters from natural language query."""
        try:
            prompt = f"""
            You are a product search assistant. Extract search filters from this query: "{query}"
            
            Return ONLY a valid JSON object with these exact fields:
            {{
                "price_range": {{"min": float, "max": float}} or null,
                "category": string or null,
                "availability": "in_stock", "out_of_stock", "limited_stock", "pre_order", or null,
                "search_text": "clean text without filter terms",
                "brand": string or null,
                "features": [string] or null
            }}
            
            Rules:
            - price_range: Use null if no price filter, otherwise specify min/max
            - category: Map to closest product category from: {', '.join(PRODUCT_CATEGORIES)}
            - availability: Use exact status values or null
            - search_text: Remove filter words, keep product description
            - brand: Extract brand names if mentioned
            - features: Extract product features/attributes
            
            Examples:
            "affordable smartphones under $500" → {{"price_range": {{"max": 500}}, "category": "electronics", "availability": null, "search_text": "smartphones", "brand": null, "features": null}}
            "luxury watches in stock" → {{"price_range": null, "category": "jewelry", "availability": "in_stock", "search_text": "luxury watches", "brand": null, "features": null}}
            "Apple iPhone between $800 and $1200" → {{"price_range": {{"min": 800, "max": 1200}}, "category": "electronics", "availability": null, "search_text": "iPhone", "brand": "Apple", "features": null}}
            """
            
            # Call LLM
            response = _LLM_CLIENT.invoke(prompt)
            response_text = response.content.strip()
            
            # Parse JSON response
            try:
                # Clean response text (remove markdown if present)
                if response_text.startswith('```json'):
                    response_text = response_text.split('```json')[1].split('```')[0]
                elif response_text.startswith('```'):
                    response_text = response_text.split('```')[1].split('```')[0]
                
                filters = json.loads(response_text)
                
                # Validate required fields
                required_fields = ['price_range', 'category', 'availability', 'search_text', 'brand', 'features']
                for field in required_fields:
                    if field not in filters:
                        filters[field] = None
                
                logger.info(f"LLM extracted filters: {filters}")
                return filters
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                logger.error(f"Raw response: {response_text}")
                return None
                
        except Exception as e:
            logger.error(f"Error in LLM filter extraction: {e}")
            return None

    def _fallback_extract_filters(self, query: str) -> Dict[str, Any]:
        """Fallback method using original hardcoded patterns if LLM fails."""
        logger.info("Using fallback filter extraction")
        
        # Extract filters using original methods
        price_filter = _extract_price_filter(query)
        category_filter = _extract_category_filter(query)
        availability_filter = _extract_availability_filter(query)
        
        # Build fallback response
        filters = {
            "price_range": None,
            "category": category_filter,
            "availability": availability_filter,
            "search_text": _clean_search_text(query),
            "brand": None,
            "features": None
        }
        
        # Convert price filter to price_range format
        if price_filter and "price" in price_filter:
            price_conditions = price_filter["price"]
            if "$lt" in price_conditions:
                filters["price_range"] = {"max": price_conditions["$lt"]}
            elif "$gt" in price_conditions:
                filters["price_range"] = {"min": price_conditions["$gt"]}
            elif "$gte" in price_conditions and "$lte" in price_conditions:
                filters["price_range"] = {
                    "min": price_conditions["$gte"],
                    "max": price_conditions["$lte"]
                }
        
        return filters

    def _build_mongodb_filters(self, extracted_filters: Dict[str, Any]) -> Dict[str, Any]:
        """Convert extracted filters to MongoDB query format."""
        filters = {}
        
        # Price range filter
        if extracted_filters.get("price_range"):
            price_range = extracted_filters["price_range"]
            if price_range.get("min") is not None and price_range.get("max") is not None:
                filters["price"] = {"$gte": price_range["min"], "$lte": price_range["max"]}
            elif price_range.get("min") is not None:
                filters["price"] = {"$gte": price_range["min"]}
            elif price_range.get("max") is not None:
                filters["price"] = {"$lte": price_range["max"]}
        
        # Category filter
        if extracted_filters.get("category"):
            filters["category"] = {"$regex": extracted_filters["category"], "$options": "i"}
        
        # Availability filter
        if extracted_filters.get("availability"):
            filters["inventory.availability"] = extracted_filters["availability"]
        
        # Brand filter
        if extracted_filters.get("brand"):
            filters["brand"] = {"$regex": extracted_filters["brand"], "$options": "i"}
        
        # Features filter (search in specifications)
        if extracted_filters.get("features") and isinstance(extracted_filters["features"], list):
            feature_conditions = []
            for feature in extracted_filters["features"]:
                feature_conditions.append({"specifications": {"$regex": feature, "$options": "i"}})
            if feature_conditions:
                filters["$or"] = feature_conditions
        
        return filters

def _extract_price_filter(query: str) -> Optional[Dict[str, Any]]:
    """Extract price filters from natural language query (fallback method)."""
    # Pattern for "under $X", "below $X", "less than $X"
    under_match = re.search(r"(?:under|below|less than|<)\s*\$?(\d+(?:\.\d{2})?)", query, re.IGNORECASE)
    if under_match:
        return {"price": {"$lt": float(under_match.group(1))}}
    
    # Pattern for "over $X", "above $X", "more than $X"
    over_match = re.search(r"(?:over|above|more than|>)\s*\$?(\d+(?:\.\d{2})?)", query, re.IGNORECASE)
    if over_match:
        return {"price": {"$gt": float(over_match.group(1))}}
    
    # Pattern for "between $X and $Y"
    between_match = re.search(r"between\s*\$?(\d+(?:\.\d{2})?)\s*and\s*\$?(\d+(?:\.\d{2})?)", query, re.IGNORECASE)
    if between_match:
        min_price = float(between_match.group(1))
        max_price = float(between_match.group(2))
        return {"price": {"$gte": min_price, "$lte": max_price}}
    
    return None
    
def _extract_category_filter(query: str) -> Optional[str]:
    """Extract category from query (fallback method)."""
    query_lower = query.lower()
    
    for category in PRODUCT_CATEGORIES:
        if category in query_lower:
            return category
    return None

def _extract_availability_filter(query: str) -> Optional[str]:
    """Extract availability status from query (fallback method)."""
    query_lower = query.lower()
    if any(word in query_lower for word in ["in stock", "available", "inventory"]):
        return "in_stock"
    elif any(word in query_lower for word in ["out of stock", "unavailable"]):
        return "out_of_stock"
    return None

def _clean_search_text(query: str) -> str:
    """Remove filter keywords to get clean search text (fallback method)."""
    # Remove price-related words
    cleaned = re.sub(r"(?:under|below|over|above|less than|more than|between)\s*\$?\d+(?:\.\d{2})?(?:\s*and\s*\$?\d+(?:\.\d{2})?)?", "", query, flags=re.IGNORECASE)
    
    # Remove availability words
    cleaned = re.sub(r"\b(?:in stock|out of stock|available|unavailable|inventory)\b", "", cleaned, flags=re.IGNORECASE)
    
    # Remove category words (they're already captured in filters)
    for category in PRODUCT_CATEGORIES:
        cleaned = re.sub(rf"\b{category}\b", "", cleaned, flags=re.IGNORECASE)
    
    # Clean up extra spaces
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    
    return cleaned if cleaned else ""

def _format_product_results(results: List[Dict[str, Any]]) -> str:
    """Format product search results for display."""
    if not results:
        return "No products found."
    
    formatted_results = ["PRODUCT SEARCH RESULTS:"]
    
    for i, product in enumerate(results, 1):
        name = product.get('name', 'Unknown Product')
        price = product.get('price', 'N/A')
        category = product.get('category', 'N/A')
        description = product.get('description', 'No description available')
        inventory = product.get('inventory', {})
        availability = inventory.get('availability', 'N/A')
        quantity = inventory.get('quantity', 'N/A')
        
        # Format price
        price_str = f"${price}" if isinstance(price, (int, float)) else str(price)
        
        # Format availability with quantity
        availability_str = availability
        if availability == "in_stock" and isinstance(quantity, int):
            availability_str = f"In Stock ({quantity} available)"
        elif availability == "out_of_stock":
            availability_str = "Out of Stock"
        
        product_info = (
            f"{i}. {name}\n"
            f"   Price: {price_str}\n"
            f"   Category: {category}\n"
            f"   Availability: {availability_str}\n"
            f"   Description: {description[:100]}{'...' if len(description) > 100 else ''}"
        )
        
        # Add specifications if available
        if 'specifications' in product:
            specs = product['specifications']
            if isinstance(specs, dict) and specs:
                spec_items = []
                for key, value in list(specs.items())[:3]:  # Show max 3 specs
                    spec_items.append(f"{key}: {value}")
                if spec_items:
                    product_info += f"\n   Specifications: {', '.join(spec_items)}"
        
        formatted_results.append(product_info)
    
    return "\n\n".join(formatted_results)
