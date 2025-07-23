"""Database retrieval tool for business data using MongoDB."""

import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from langchain_core.tools import BaseTool

from app.tools.database_client import DatabaseClient

logger = logging.getLogger(__name__)

class DatabaseRetrievalTool(BaseTool):
    """Tool for retrieving business data from MongoDB databases."""
    
    name = "database_search"
    description = "Search databases for products, appointments, inventory, and other business data"
    
    def __init__(self, **kwargs):
        """Initialize the database retrieval tool."""
        super().__init__(**kwargs)
        self.db_client = DatabaseClient()
    
    def _run(self, query: str, database_type: str = "auto", max_results: int = 5) -> str:
        """
        Execute database search based on query.
        
        Args:
            query: Natural language search query
            database_type: 'products', 'appointments', 'auto' (auto-detect)
            max_results: Maximum number of results to return
            
        Returns:
            Formatted string with search results
        """
        try:
            # Auto-detect database type if not specified
            if database_type == "auto":
                database_type = self._detect_database_type(query)
            
            # Route to appropriate search method
            if database_type == "products":
                results = self._search_products(query, max_results)
            elif database_type == "appointments":
                results = self._search_appointments(query, max_results)
            else:
                # Try both databases and combine results
                product_results = self._search_products(query, max_results // 2)
                appointment_results = self._search_appointments(query, max_results // 2)
                results = self._combine_results(product_results, appointment_results)
            
            if not results:
                return f"No {database_type} data found for your query."
            
            # Format results for readability
            return self._format_results(results, database_type)
            
        except Exception as e:
            logger.error(f"Error during database search: {e}")
            return f"Error searching database: {str(e)}"
    
    def _detect_database_type(self, query: str) -> str:
        """Auto-detect which database to search based on query content."""
        query_lower = query.lower()
        
        # Product-related keywords
        product_keywords = [
            "product", "item", "price", "cost", "buy", "purchase", "inventory", 
            "stock", "available", "category", "brand", "model", "specifications"
        ]
        
        # Appointment-related keywords
        appointment_keywords = [
            "appointment", "schedule", "booking", "available", "time", "date",
            "consultation", "meeting", "doctor", "provider", "service", "calendar"
        ]
        
        # Count keyword matches
        product_score = sum(1 for keyword in product_keywords if keyword in query_lower)
        appointment_score = sum(1 for keyword in appointment_keywords if keyword in query_lower)
        
        if product_score > appointment_score:
            return "products"
        elif appointment_score > product_score:
            return "appointments"
        else:
            return "general"  # Search both
    
    def _search_products(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search products database with intelligent query parsing."""
        try:
            # Extract price filters from query
            price_filter = self._extract_price_filter(query)
            
            # Extract category from query
            category_filter = self._extract_category_filter(query)
            
            # Extract availability filter
            availability_filter = self._extract_availability_filter(query)
            
            # Build filters
            filters = {}
            if price_filter:
                filters.update(price_filter)
            if category_filter:
                filters["category"] = {"$regex": category_filter, "$options": "i"}
            if availability_filter:
                filters["inventory.availability"] = availability_filter
            
            # Extract search text (remove price and other filter words)
            search_text = self._clean_search_text(query)
            
            # Search products
            results = self.db_client.search_products(
                query_text=search_text if search_text else None,
                filters=filters if filters else None,
                limit=limit
            )
            
            # Add result type for formatting
            for result in results:
                result['_result_type'] = 'product'
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
    
    def _search_appointments(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search appointments database with intelligent query parsing."""
        try:
            # Extract date range from query
            date_range = self._extract_date_range(query)
            
            # Extract status filter
            status_filter = self._extract_status_filter(query)
            
            # Extract service type
            service_filter = self._extract_service_filter(query)
            
            # Build filters
            filters = {}
            if status_filter:
                filters["status"] = status_filter
            if service_filter:
                filters["service_type"] = {"$regex": service_filter, "$options": "i"}
            
            # Search appointments
            results = self.db_client.search_appointments(
                date_range=date_range,
                filters=filters if filters else None,
                limit=limit
            )
            
            # Add result type for formatting
            for result in results:
                result['_result_type'] = 'appointment'
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching appointments: {e}")
            return []
    
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
        categories = ["electronics", "clothing", "books", "toys", "sports", "health", "beauty", "home"]
        query_lower = query.lower()
        
        for category in categories:
            if category in query_lower:
                return category
        return None
    
    def _extract_availability_filter(self, query: str) -> Optional[str]:
        """Extract availability status from query."""
        if any(word in query.lower() for word in ["in stock", "available", "inventory"]):
            return "in_stock"
        elif any(word in query.lower() for word in ["out of stock", "unavailable"]):
            return "out_of_stock"
        return None
    
    def _extract_date_range(self, query: str) -> Optional[Dict[str, str]]:
        """Extract date range from natural language query."""
        today = datetime.now()
        query_lower = query.lower()
        
        if "today" in query_lower:
            date_str = today.strftime("%Y-%m-%d")
            return {"start": date_str, "end": date_str}
        elif "tomorrow" in query_lower:
            tomorrow = today + timedelta(days=1)
            date_str = tomorrow.strftime("%Y-%m-%d")
            return {"start": date_str, "end": date_str}
        elif "next week" in query_lower:
            start_date = today + timedelta(days=1)
            end_date = start_date + timedelta(days=7)
            return {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            }
        elif "this week" in query_lower:
            # Start from today to end of week
            days_until_sunday = 6 - today.weekday()
            end_date = today + timedelta(days=days_until_sunday)
            return {
                "start": today.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            }
        
        return None
    
    def _extract_status_filter(self, query: str) -> Optional[str]:
        """Extract appointment status from query."""
        if "available" in query.lower():
            return "available"
        elif "booked" in query.lower():
            return "booked"
        elif any(word in query.lower() for word in ["cancelled", "canceled"]):
            return "cancelled"
        return None
    
    def _extract_service_filter(self, query: str) -> Optional[str]:
        """Extract service type from query."""
        services = ["consultation", "checkup", "meeting", "therapy", "treatment"]
        query_lower = query.lower()
        
        for service in services:
            if service in query_lower:
                return service
        return None
    
    def _clean_search_text(self, query: str) -> str:
        """Remove filter keywords to get clean search text."""
        # Remove price-related words
        cleaned = re.sub(r"(?:under|below|over|above|less than|more than|between)\s*\$?\d+(?:\.\d{2})?(?:\s*and\s*\$?\d+(?:\.\d{2})?)?", "", query, flags=re.IGNORECASE)
        
        # Remove availability words
        cleaned = re.sub(r"\b(?:in stock|out of stock|available|unavailable|inventory)\b", "", cleaned, flags=re.IGNORECASE)
        
        # Remove date words
        cleaned = re.sub(r"\b(?:today|tomorrow|next week|this week)\b", "", cleaned, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        
        return cleaned if cleaned else ""
    
    def _combine_results(self, product_results: List[Dict], appointment_results: List[Dict]) -> List[Dict]:
        """Combine results from multiple databases."""
        combined = []
        combined.extend(product_results)
        combined.extend(appointment_results)
        return combined
    
    def _format_results(self, results: List[Dict[str, Any]], database_type: str) -> str:
        """Format search results for display."""
        if not results:
            return "No results found."
        
        formatted_sections = []
        
        # Group results by type
        products = [r for r in results if r.get('_result_type') == 'product']
        appointments = [r for r in results if r.get('_result_type') == 'appointment']
        
        # Format products
        if products:
            product_section = ["PRODUCTS:"]
            for i, product in enumerate(products, 1):
                name = product.get('name', 'Unknown Product')
                price = product.get('price', 'N/A')
                category = product.get('category', 'N/A')
                availability = product.get('inventory', {}).get('availability', 'N/A')
                
                product_info = (
                    f"{i}. {name}\n"
                    f"   Price: ${price}\n"
                    f"   Category: {category}\n"
                    f"   Availability: {availability}"
                )
                product_section.append(product_info)
            formatted_sections.append("\n\n".join(product_section))
        
        # Format appointments
        if appointments:
            appointment_section = ["APPOINTMENTS:"]
            for i, appointment in enumerate(appointments, 1):
                date = appointment.get('date', 'N/A')
                time = appointment.get('time', 'N/A')
                status = appointment.get('status', 'N/A')
                service_type = appointment.get('service_type', 'N/A')
                provider = appointment.get('provider', 'N/A')
                
                appointment_info = (
                    f"{i}. {service_type}\n"
                    f"   Date: {date}\n"
                    f"   Time: {time}\n"
                    f"   Provider: {provider}\n"
                    f"   Status: {status}"
                )
                appointment_section.append(appointment_info)
            formatted_sections.append("\n\n".join(appointment_section))
        
        return "\n\n" + "="*50 + "\n\n".join(formatted_sections)
