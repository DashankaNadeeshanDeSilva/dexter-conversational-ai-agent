"""MongoDB client for episodic and procedural memory storage."""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from pymongo import MongoClient
from pymongo.collection import Collection
from bson.objectid import ObjectId
import uuid

from app.config import settings

logger = logging.getLogger(__name__)

class MongoDBClient:
    """MongoDB client for long-term memory storage."""
    
    def __init__(self):
        """Initialize MongoDB client."""
        try:
            # Create MongoDB client
            self.client = MongoClient(settings.MONGODB_URI)
            self.db = self.client[settings.MONGODB_DATABASE]
            
            # Initialize collections
            self.conversations: Collection = self.db[settings.MONGODB_CONVERSATION_COLLECTION]
            self.sessions: Collection = self.db[settings.MONGODB_SESSION_COLLECTION]
            self.memory: Collection = self.db[settings.MONGODB_MEMORY_COLLECTION]
            
            # Create indexes for faster retrieval
            self._setup_indexes()
            
            logger.info("MongoDB client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB client: {e}")
            raise
    
    def _setup_indexes(self):
        """Set up indexes for conversation and memory managment."""
        # Create index for conversations by user_id for quick user history retrieval
        self.conversations.create_index(["user_id", "created_at", "updated_at", "messages"])

        # Create index for sessions by user_id for quick user history retrieval
        self.sessions.create_index(["session_id", "user_id", "conversation_id", "created_at"])

        # Index for memory by user_id and memory_type for quick memory retrieval
        self.memory.create_index([("user_id", 1), ("memory_type", 1)])
        self.memory.create_index("created_at")
    
    def create_conversation(self, user_id: str) -> str:
        """Create a new conversation and return its ID."""
        conversation = {
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "messages": []
        }
        result = self.conversations.insert_one(conversation)
        conversation_id = str(result.inserted_id)
        logger.info(f"Created conversation {conversation_id} for user {user_id}")
        return conversation_id

    def create_session(self, user_id: str, conversation_id: str) -> str:
        """Create a new session for a conversation."""
        session_id = str(uuid.uuid4())
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "created_at": datetime.utcnow()
        }
        
        try:
            self.sessions.insert_one(session_data)
            logger.info(f"Created new session {session_id} for conversation {conversation_id}")
            return session_id
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise
    
    def add_message(self, conversation_id: str, message: Dict[str, Any]) -> bool:
        """Add a message to a conversation."""
        message["timestamp"] = datetime.utcnow()
        
        # Convert ObjectId to string if conversation_id is a string
        if isinstance(conversation_id, str):
            conversation_id = ObjectId(conversation_id)
            
        result = self.conversations.update_one(
            {"_id": conversation_id},
            {
                "$push": {"messages": message},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        success = result.modified_count > 0
        
        if success:
            logger.debug(f"Added message to conversation {conversation_id}")
        else:
            logger.warning(f"Failed to add message to conversation {conversation_id}")
            
        return success
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get a conversation by ID."""
        if isinstance(conversation_id, str):
            conversation_id = ObjectId(conversation_id)
            
        conversation = self.conversations.find_one({"_id": conversation_id})
        
        if conversation:
            # Convert ObjectId to string for JSON serialization
            conversation["_id"] = str(conversation["_id"])
            logger.debug(f"Retrieved conversation {conversation_id}")
        else:
            logger.warning(f"Conversation {conversation_id} not found")
            
        return conversation
    
    def get_user_conversations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversations for a user."""
        cursor = (
            self.conversations.find({"user_id": user_id})
            .sort("updated_at", -1)
            .limit(limit)
        )
        
        conversations = []
        for conversation in cursor:
            # Convert ObjectId to string for JSON serialization
            conversation["_id"] = str(conversation["_id"])
            conversations.append(conversation)
            
        logger.debug(f"Retrieved {len(conversations)} conversations for user {user_id}")
        return conversations
    
    def store_memory(
        self, 
        user_id: str, 
        memory_type: str, 
        content: Dict[str, Any], 
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store a memory for a user."""
        if metadata is None:
            metadata = {}
            
        memory = {
            "user_id": user_id,
            "memory_type": memory_type,
            "content": content,
            "metadata": metadata,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "access_count": 0
        }
        
        result = self.memory.insert_one(memory)
        memory_id = str(result.inserted_id)
        logger.debug(f"Stored {memory_type} memory {memory_id} for user {user_id}")
        return memory_id
    
    def retrieve_memories(
        self, 
        user_id: str, 
        memory_type: str,
        filter_query: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve memories for a user by type and optional filter."""
        query = {"user_id": user_id, "memory_type": memory_type}
        
        if filter_query:
            query.update(filter_query)
            
        cursor = (
            self.memory.find(query)
            .sort("created_at", -1)
            .limit(limit)
        )
        
        # Update access count for retrieved memories
        memory_ids = []
        memories = []
        
        for memory in cursor:
            memory_id = memory["_id"]
            memory_ids.append(memory_id)
            
            # Convert ObjectId to string for JSON serialization
            memory["_id"] = str(memory["_id"])
            memories.append(memory)
        
        if memory_ids:
            # Increase access count for all retrieved memories
            self.memory.update_many(
                {"_id": {"$in": memory_ids}},
                {"$inc": {"access_count": 1}}
            )
            
        logger.debug(f"Retrieved {len(memories)} {memory_type} memories for user {user_id}")
        return memories
    
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update a memory."""
        if isinstance(memory_id, str):
            memory_id = ObjectId(memory_id)
            
        updates["updated_at"] = datetime.utcnow()
        
        result = self.memory.update_one(
            {"_id": memory_id},
            {"$set": updates}
        )
        
        success = result.modified_count > 0
        
        if success:
            logger.debug(f"Updated memory {memory_id}")
        else:
            logger.warning(f"Failed to update memory {memory_id}")
            
        return success
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation."""
        if isinstance(conversation_id, str):
            conversation_id = ObjectId(conversation_id)
            
        result = self.conversations.delete_one({"_id": conversation_id})
        success = result.deleted_count > 0
        
        if success:
            logger.debug(f"Deleted conversation {conversation_id}")
        else:
            logger.warning(f"Failed to delete conversation {conversation_id}")
            
        return success
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory."""
        if isinstance(memory_id, str):
            memory_id = ObjectId(memory_id)
            
        result = self.memory.delete_one({"_id": memory_id})
        success = result.deleted_count > 0
        
        if success:
            logger.debug(f"Deleted memory {memory_id}")
        else:
            logger.warning(f"Failed to delete memory {memory_id}")
            
        return success
    
    def close(self):
        """Close the MongoDB client connection."""
        self.client.close()
        logger.info("MongoDB client connection closed")
