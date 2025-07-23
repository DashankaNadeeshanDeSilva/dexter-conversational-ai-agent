"""Database client for business data operations (products, appointments, etc.)."""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pymongo import MongoClient, ASCENDING, TEXT
from pymongo.collection import Collection
from pymongo.database import Database

from app.config import settings

logger = logging.getLogger(__name__)

class DatabaseClient:
    """Dedicated client for business database operations."""
    
    def __init__(self):
        """Initialize the database client for business data."""
        try:
            # Create separate connection for business data
            self.client = MongoClient(settings.MONGODB_URI)
            self.db: Database = self.client[settings.MONGODB_DATABASE]
            
            # Initialize collections
            self.products: Collection = self.db['products']
            self.appointments: Collection = self.db['appointments']
            
            # Setup indexes for search optimization
            self._setup_database_indexes()
            
            logger.info("DatabaseClient initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize DatabaseClient: {e}")
            raise
    
    def _setup_database_indexes(self):
        """Set up search indexes for optimal query performance."""
        try:
            # Product search indexes
            self.products.create_index([
                ("name", TEXT),
                ("description", TEXT),
                ("category", TEXT),
                ("tags", TEXT)
            ], name="product_text_search")
            
            self.products.create_index("category")
            self.products.create_index("price")
            self.products.create_index("inventory.availability")
            
            # Appointment search indexes
            self.appointments.create_index([("date", ASCENDING), ("time", ASCENDING)])
            self.appointments.create_index("status")
            self.appointments.create_index("service_type")
            self.appointments.create_index("provider")
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error setting up database indexes: {e}")
    
    def search_products(
        self,
        query_text: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search products with text and field-based filters.
        
        Args:
            query_text: Text to search in product name, description, category
            filters: Additional filters (price, category, availability, etc.)
            limit: Maximum number of results
            
        Returns:
            List of matching products
        """
        try:
            # Build MongoDB query
            query = {}
            
            # Add text search if provided
            if query_text:
                query["$text"] = {"$search": query_text}
            
            # Add field-based filters
            if filters:
                query.update(filters)
            
            # Execute search
            cursor = self.products.find(query).limit(limit)
            
            # Convert to list and add text search scores if text search was used
            results = []
            for doc in cursor:
                # Convert ObjectId to string for serialization
                doc['_id'] = str(doc['_id'])
                results.append(doc)
            
            logger.info(f"Found {len(results)} products for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
    
    def search_appointments(
        self,
        date_range: Optional[Dict[str, str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search appointments with date/time and field-based filters.
        
        Args:
            date_range: Dict with 'start' and 'end' date strings (YYYY-MM-DD)
            filters: Additional filters (status, provider, service_type, etc.)
            limit: Maximum number of results
            
        Returns:
            List of matching appointments
        """
        try:
            # Build MongoDB query
            query = {}
            
            # Add date range filter
            if date_range:
                date_filter = {}
                if date_range.get('start'):
                    date_filter["$gte"] = date_range['start']
                if date_range.get('end'):
                    date_filter["$lte"] = date_range['end']
                if date_filter:
                    query["date"] = date_filter
            
            # Add field-based filters
            if filters:
                query.update(filters)
            
            # Execute search
            cursor = self.appointments.find(query).sort("date", ASCENDING).limit(limit)
            
            # Convert to list
            results = []
            for doc in cursor:
                # Convert ObjectId to string for serialization
                doc['_id'] = str(doc['_id'])
                results.append(doc)
            
            logger.info(f"Found {len(results)} appointments for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching appointments: {e}")
            return []
    
    def search_database(
        self,
        collection_name: str,
        search_query: Dict[str, Any],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generic database search method for custom queries.
        
        Args:
            collection_name: Name of the collection to search
            search_query: MongoDB query dict
            limit: Maximum number of results
            
        Returns:
            List of matching documents
        """
        try:
            collection = self.db[collection_name]
            cursor = collection.find(search_query).limit(limit)
            
            results = []
            for doc in cursor:
                doc['_id'] = str(doc['_id'])
                results.append(doc)
            
            logger.info(f"Found {len(results)} documents in {collection_name}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching collection {collection_name}: {e}")
            return []
    
    def close(self):
        """Close the database connection."""
        if hasattr(self, 'client'):
            self.client.close()
            logger.info("DatabaseClient connection closed")
