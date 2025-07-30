"""Product search tool for discovering products, checking prices, and inventory."""

import logging
import re
from typing import Dict, List, Any, Optional
from langchain_core.tools import BaseTool
from pydantic import PrivateAttr
from app.tools.database_client import DatabaseClient
from app.tools.tool_config import PRODUCT_CATEGORIES

logger = logging.getLogger(__name__)

class ProductSearchTool(BaseTool):
    """Tool for searching and discovering products in the database."""
    
    name: str = "product_search"
    description: str = "Search for products, check prices, inventory, and product information"
    _db_client: DatabaseClient = PrivateAttr() # Use PrivateAttr for Non-Pydantic Field
    
    def __init__(self, **kwargs):
        """Initialize the product search tool."""
        super().__init__(**kwargs)
        self._db_client = DatabaseClient()
    
    def _run(self, query: str, max_results: int = 5) -> str:
        """
        Execute product search based on query.
        
        Args:
            query: Natural language search query for products
            max_results: Maximum number of results to return
            
        Returns:
            Formatted string with product search results
        """
        try:
            # Extract filters from query
            price_filter = self._extract_price_filter(query)
            category_filter = self._extract_category_filter(query)
            availability_filter = self._extract_availability_filter(query)
            
            # Build filters
            filters = {}
            if price_filter:
                filters.update(price_filter)
            if category_filter:
                filters["category"] = {"$regex": category_filter, "$options": "i"}
            if availability_filter:
                filters["inventory.availability"] = availability_filter
            
            # Extract clean search text
            search_text = self._clean_search_text(query)
            
            # Search products
            results = self._db_client.search_products(
                query_text=search_text if search_text else None,
                filters=filters if filters else None,
                limit=max_results
            )
            
            if not results:
                return "No products found matching your criteria."
            
            # Format results
            return self._format_product_results(results)
            
        except Exception as e:
            logger.error(f"Error during product search: {e}")
            return f"Error searching products: {str(e)}"
    
    def _extract_price_filter(self, query: str) -> Optional[Dict[str, Any]]:
        """Extract price filters from natural language query."""
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
    
    def _extract_category_filter(self, query: str) -> Optional[str]:
        """Extract category from query."""
        query_lower = query.lower()
        
        for category in PRODUCT_CATEGORIES:
            if category in query_lower:
                return category
        return None
    
    def _extract_availability_filter(self, query: str) -> Optional[str]:
        """Extract availability status from query."""
        query_lower = query.lower()
        if any(word in query_lower for word in ["in stock", "available", "inventory"]):
            return "in_stock"
        elif any(word in query_lower for word in ["out of stock", "unavailable"]):
            return "out_of_stock"
        return None
    
    def _clean_search_text(self, query: str) -> str:
        """Remove filter keywords to get clean search text."""
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
    
    def _format_product_results(self, results: List[Dict[str, Any]]) -> str:
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
