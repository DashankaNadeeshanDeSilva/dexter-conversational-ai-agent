
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime


# Request/response models
class ChatMessage(BaseModel):
    """Chat message model."""
    
    role: str = Field(..., description="Role of the message sender (user or assistant)")
    content: str = Field(..., description="Content of the message")
    timestamp: Optional[datetime] = Field(None, description="Timestamp of the message")

class ChatRequest(BaseModel):
    """Chat request model."""
    
    user_id: str = Field(..., description="User ID")
    message: str = Field(..., description="Message content")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    session_id: Optional[str] = Field(None, description="Session ID")

class ChatResponse(BaseModel):
    """Chat response model."""
    
    conversation_id: str = Field(..., description="Conversation ID")
    session_id: str = Field(..., description="Session ID")
    message: ChatMessage = Field(..., description="Assistant's response message")

class ConversationListResponse(BaseModel):
    """Conversation list response model."""
    
    conversations: List[Dict[str, Any]] = Field(..., description="List of conversations")

class MemoryQueryRequest(BaseModel):
    """Memory query request model."""
    
    user_id: str = Field(..., description="User ID")
    query: str = Field(..., description="Query text")
    memory_type: str = Field(..., description="Type of memory to query")
    limit: Optional[int] = Field(5, description="Maximum number of results")

class MemoryQueryResponse(BaseModel):
    """Memory query response model."""
    
    memories: List[Dict[str, Any]] = Field(..., description="List of memories")

class HealthResponse(BaseModel):
    """Health response model."""
    
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Current timestamp")