"""Session management for tracking conversation sessions."""
### Inactive - this file is not used in the current implementation
from typing import Dict, List, Any, Optional
import logging
import uuid
from datetime import datetime
from pymongo.collection import Collection

from app.memory.mongodb_client import MongoDBClient

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages session lifecycle and metadata."""
    
    def __init__(self, mongodb_client: MongoDBClient):
        """
        Initialize session manager.
        
        Args:
            mongodb_client: MongoDB client for session persistence
        """
        self.mongodb_client = mongodb_client
        self.db = mongodb_client.db
        self.sessions = self.db["sessions"]  # Session collection
        
        # Create indexes for efficient retrieval
        self._setup_indexes()
        
        logger.info("Session manager initialized")
    
    def _setup_indexes(self):
        """Set up database indexes for session management."""
        # Index for session lookup by session_id
        self.sessions.create_index("session_id", unique=True)
        
        # Index for user sessions
        self.sessions.create_index("user_id")
        
        # Index for conversation sessions
        self.sessions.create_index("conversation_id")
        
        # Index for session status and timestamps
        self.sessions.create_index([("status", 1), ("created_at", -1)])
        self.sessions.create_index("last_activity")
    
    def create_session(self, user_id: str, conversation_id: str) -> str:
        """
        Create and track a new session.
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID this session belongs to
            
        Returns:
            New session ID
        """
        session_id = str(uuid.uuid4())
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "status": "active",
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "message_count": 0,
            "tool_usage_count": 0,
            "metadata": {
                "session_type": "chat",
                "version": "1.0"
            }
        }
        
        try:
            self.sessions.insert_one(session_data)
            logger.info(f"Created new session {session_id} for user {user_id}")
            return session_id
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise
    
    def update_session_activity(self, session_id: str, activity_type: str = "message") -> bool:
        """
        Update session activity and statistics.
        
        Args:
            session_id: Session ID
            activity_type: Type of activity ('message', 'tool_usage', etc.)
            
        Returns:
            True if update was successful
        """
        update_data = {
            "last_activity": datetime.utcnow()
        }
        
        # Increment appropriate counters
        if activity_type == "message":
            update_data["$inc"] = {"message_count": 1}
        elif activity_type == "tool_usage":
            update_data["$inc"] = {"tool_usage_count": 1}
        
        try:
            result = self.sessions.update_one(
                {"session_id": session_id},
                {"$set": update_data} if "$inc" not in update_data else {
                    "$set": {k: v for k, v in update_data.items() if k != "$inc"},
                    "$inc": update_data["$inc"]
                }
            )
            
            if result.modified_count > 0:
                logger.debug(f"Updated activity for session {session_id}: {activity_type}")
                return True
            else:
                logger.warning(f"Session {session_id} not found for activity update")
                return False
                
        except Exception as e:
            logger.error(f"Error updating session activity: {e}")
            return False
    
    def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session statistics for decision making.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session statistics dictionary or None if not found
        """
        try:
            session = self.sessions.find_one({"session_id": session_id})
            
            if not session:
                logger.warning(f"Session {session_id} not found")
                return None
            
            # Calculate session duration
            duration = datetime.utcnow() - session["created_at"]
            
            stats = {
                "session_id": session_id,
                "user_id": session["user_id"],
                "conversation_id": session["conversation_id"],
                "status": session["status"],
                "created_at": session["created_at"],
                "last_activity": session["last_activity"],
                "duration_minutes": duration.total_seconds() / 60,
                "message_count": session.get("message_count", 0),
                "tool_usage_count": session.get("tool_usage_count", 0),
                "metadata": session.get("metadata", {})
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting session stats: {e}")
            return None
    
    def end_session(self, session_id: str, end_reason: str = "explicit") -> Optional[Dict[str, Any]]:
        """
        Explicitly end a session and return consolidation data.
        
        Args:
            session_id: Session ID to end
            end_reason: Reason for ending ('explicit', 'timeout', 'error')
            
        Returns:
            Session end data for consolidation or None if not found
        """
        try:
            # Get final session stats before ending
            session_stats = self.get_session_stats(session_id)
            
            if not session_stats:
                return None
            
            # Update session status to ended
            end_data = {
                "status": "ended",
                "ended_at": datetime.utcnow(),
                "end_reason": end_reason,
                "final_message_count": session_stats["message_count"],
                "final_tool_usage_count": session_stats["tool_usage_count"],
                "total_duration_minutes": session_stats["duration_minutes"]
            }
            
            result = self.sessions.update_one(
                {"session_id": session_id},
                {"$set": end_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"Ended session {session_id} (reason: {end_reason})")
                
                # Return data needed for consolidation
                return {
                    "session_id": session_id,
                    "user_id": session_stats["user_id"],
                    "conversation_id": session_stats["conversation_id"],
                    "session_stats": session_stats,
                    "end_data": end_data,
                    "should_consolidate": session_stats["message_count"] >= 4  # Minimum threshold
                }
            else:
                logger.warning(f"Failed to end session {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            return None
    
    def get_active_sessions(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get active sessions, optionally filtered by user.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            List of active session data
        """
        try:
            query = {"status": "active"}
            if user_id:
                query["user_id"] = user_id
            
            cursor = self.sessions.find(query).sort("last_activity", -1)
            
            sessions = []
            for session in cursor:
                # Convert ObjectId to string for JSON serialization
                session["_id"] = str(session["_id"])
                sessions.append(session)
            
            logger.debug(f"Found {len(sessions)} active sessions" + (f" for user {user_id}" if user_id else ""))
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting active sessions: {e}")
            return []
    
    def get_user_session_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get session history for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of sessions to return
            
        Returns:
            List of user's session history
        """
        try:
            cursor = (
                self.sessions.find({"user_id": user_id})
                .sort("created_at", -1)
                .limit(limit)
            )
            
            sessions = []
            for session in cursor:
                # Convert ObjectId to string for JSON serialization
                session["_id"] = str(session["_id"])
                sessions.append(session)
            
            logger.debug(f"Retrieved {len(sessions)} sessions for user {user_id}")
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting user session history: {e}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session (use with caution).
        
        Args:
            session_id: Session ID to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            result = self.sessions.delete_one({"session_id": session_id})
            
            if result.deleted_count > 0:
                logger.info(f"Deleted session {session_id}")
                return True
            else:
                logger.warning(f"Session {session_id} not found for deletion")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False
