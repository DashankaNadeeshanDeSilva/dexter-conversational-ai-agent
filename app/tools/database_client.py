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
    
    # ============================================================================
    # APPOINTMENT CRUD OPERATIONS
    # ============================================================================
    
    def create_appointment(
        self,
        user_name: str,
        user_email: str,
        date: str,
        time: str,
        service_type: str,
        provider: Optional[str] = None,
        duration: int = 60,
        notes: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a new appointment.
        
        Args:
            user_name: User's full name
            user_email: User's email address
            date: Appointment date (YYYY-MM-DD)
            time: Appointment time (HH:MM)
            service_type: Type of service/consultation
            provider: Service provider name
            duration: Duration in minutes
            notes: Optional notes
            
        Returns:
            Appointment ID if successful, None otherwise
        """
        try:
            appointment = {
                "date": date,
                "time": time,
                "duration": duration,
                "status": "booked",
                "service_type": service_type,
                "provider": provider or "TBD",
                "client_info": {
                    "name": user_name,
                    "email": user_email
                },
                "metadata": {
                    "notes": notes or "",
                    "location": "TBD"  # Can be updated later
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = self.appointments.insert_one(appointment)
            appointment_id = str(result.inserted_id)
            
            logger.info(f"Created appointment {appointment_id} for {user_name}")
            return appointment_id
            
        except Exception as e:
            logger.error(f"Error creating appointment: {e}")
            return None
    
    def update_appointment(
        self,
        appointment_id: str,
        user_email: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update an existing appointment.
        
        Args:
            appointment_id: Appointment ID
            user_email: User's email for verification
            updates: Fields to update
            
        Returns:
            Success status
        """
        try:
            # Verify appointment belongs to user
            existing = self.appointments.find_one({
                "_id": appointment_id,
                "client_info.email": user_email
            })
            
            if not existing:
                logger.warning(f"Appointment {appointment_id} not found for user {user_email}")
                return False
            
            # Prepare update with timestamp
            update_data = {
                **updates,
                "updated_at": datetime.utcnow()
            }
            
            result = self.appointments.update_one(
                {"_id": appointment_id},
                {"$set": update_data}
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Updated appointment {appointment_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating appointment: {e}")
            return False
    
    def cancel_appointment(
        self,
        appointment_id: str,
        user_email: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Cancel an appointment.
        
        Args:
            appointment_id: Appointment ID
            user_email: User's email for verification
            reason: Optional cancellation reason
            
        Returns:
            Success status
        """
        try:
            update_data = {
                "status": "cancelled",
                "metadata.cancellation_reason": reason or "User cancelled",
                "metadata.cancelled_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = self.appointments.update_one(
                {
                    "_id": appointment_id,
                    "client_info.email": user_email,
                    "status": {"$ne": "cancelled"}  # Prevent double cancellation
                },
                {"$set": update_data}
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Cancelled appointment {appointment_id}")
            else:
                logger.warning(f"Could not cancel appointment {appointment_id} for {user_email}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error cancelling appointment: {e}")
            return False
    
    def get_user_appointments(
        self,
        user_email: str,
        status_filter: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get appointments for a specific user.
        
        Args:
            user_email: User's email address
            status_filter: Optional status filter ('booked', 'cancelled', etc.)
            limit: Maximum number of results
            
        Returns:
            List of user's appointments
        """
        try:
            query = {"client_info.email": user_email}
            
            if status_filter:
                query["status"] = status_filter
            
            cursor = self.appointments.find(query).sort("date", ASCENDING).limit(limit)
            
            results = []
            for doc in cursor:
                doc['_id'] = str(doc['_id'])
                results.append(doc)
            
            logger.info(f"Found {len(results)} appointments for {user_email}")
            return results
            
        except Exception as e:
            logger.error(f"Error getting user appointments: {e}")
            return []
    
    def check_availability(
        self,
        date: str,
        time: str,
        provider: Optional[str] = None,
        duration: int = 60
    ) -> bool:
        """
        Check if a time slot is available.
        
        Args:
            date: Date to check (YYYY-MM-DD)
            time: Time to check (HH:MM)
            provider: Optional provider filter
            duration: Duration in minutes
            
        Returns:
            True if available, False otherwise
        """
        try:
            query = {
                "date": date,
                "time": time,
                "status": "booked"
            }
            
            if provider:
                query["provider"] = provider
            
            existing = self.appointments.find_one(query)
            is_available = existing is None
            
            logger.debug(f"Availability check for {date} {time}: {'Available' if is_available else 'Booked'}")
            return is_available
            
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return False
    
    def close(self):
        """Close the database connection."""
        if hasattr(self, 'client'):
            self.client.close()
            logger.info("DatabaseClient connection closed")
