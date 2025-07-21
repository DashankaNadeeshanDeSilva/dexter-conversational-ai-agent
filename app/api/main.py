"""Main FastAPI application."""

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.config import settings
from app.agent.agent import ReActAgent
from app.memory.memory_manager import MemoryManager

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Agent with Memory",
    description="An AI agent with short-term, semantic, episodic, and procedural memory",
    version="1.0.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize memory manager
memory_manager = MemoryManager()

# Initialize agent
agent = ReActAgent(memory_manager=memory_manager)

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

# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow()
    }

# Chat endpoint
@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Process a chat message and get a response from the agent.
    
    Args:
        request: Chat request
        
    Returns:
        Chat response
    """
    try:
        user_id = request.user_id
        message = request.message
        
        # Get or create conversation_id
        # conversation_id: represents a unique conversation thread (across multiple sessions) for given user
        conversation_id = request.conversation_id
        if not conversation_id:
            conversation_id = memory_manager.create_conversation(user_id)
            logger.info(f"Created new conversation {conversation_id} for user {user_id}")
        
        # Get or create session_id
        # session_id: represents a unique interaction/context (within a conversation) for given user (supports short-term memory)
        session_id = request.session_id
        if not session_id:
            session_id = memory_manager.session_manager.create_session(user_id, conversation_id)
            logger.info(f"Created new session {session_id} for user {user_id}")
        
        # Process message with agent
        response_text = await agent.process_message(
            user_id=user_id,
            session_id=session_id,
            conversation_id=conversation_id,
            message=message
        )
        
        logger.info(f"Processed message for user {user_id}")
        
        return {
            "conversation_id": conversation_id,
            "session_id": session_id,
            "message": {
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.utcnow()
            }
        }
    
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat: {str(e)}"
        )

# Get conversations (all) for user
@app.get(
    "/conversations/{user_id}", 
    response_model=ConversationListResponse, 
    tags=["Conversations"]
)
async def get_conversations(user_id: str, limit: int = 10):
    """
    Get conversations for a user.
    
    Args:
        user_id: User ID
        limit: Maximum number of conversations
        
    Returns:
        List of conversations
    """
    try:
        conversations = memory_manager.get_user_conversations(user_id, limit)
        
        return {
            "conversations": conversations
        }
    
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting conversations: {str(e)}"
        )

# Get a specific conversation
@app.get(
    "/conversations/{user_id}/{conversation_id}", 
    response_model=Dict[str, Any], 
    tags=["Conversations"]
)
async def get_conversation(user_id: str, conversation_id: str):
    """
    Get a specific conversation.
    
    Args:
        user_id: User ID
        conversation_id: Conversation ID
        
    Returns:
        Conversation
    """
    try:
        conversation = memory_manager.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        if conversation.get("user_id") != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation"
            )
        
        return conversation
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting conversation: {str(e)}"
        )

# Query memories
@app.post(
    "/memories/query", 
    response_model=MemoryQueryResponse, 
    tags=["Memories"]
)
async def query_memories(request: MemoryQueryRequest):
    """
    Query memories of a specific type.
    
    Args:
        request: Memory query request
        
    Returns:
        List of memories
    """
    try:
        user_id = request.user_id
        memory_type = request.memory_type
        query = request.query
        limit = request.limit
        
        memories = []
        
        if memory_type == "semantic":
            # Query semantic memories
            results = memory_manager.retrieve_semantic_memories(
                user_id=user_id,
                query=query,
                k=limit
            )
            
            for doc, score in results:
                memories.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": score
                })
        
        elif memory_type in ["episodic", "procedural"]:
            # Query MongoDB memories
            memories = memory_manager.mongodb_client.retrieve_memories(
                user_id=user_id,
                memory_type=memory_type,
                limit=limit
            )
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid memory type: {memory_type}"
            )
        
        return {
            "memories": memories
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error querying memories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying memories: {str(e)}"
        )

# Reset session endpoint
@app.post(
    "/session/{session_id}/reset", 
    tags=["Session"]
)
async def reset_session(session_id: str):
    """
    Reset a session's short-term memory.
    
    Args:
        session_id: Session ID
    """
    try:
        agent.reset_session(session_id)
        
        return {
            "success": True,
            "message": f"Session {session_id} reset successfully"
        }
    
    except Exception as e:
        logger.error(f"Error resetting session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting session: {str(e)}"
        )

if settings.ENABLE_METRICS:
    # Configure Prometheus metrics
    from prometheus_client import Counter, Histogram, Summary
    import time
    from prometheus_client import make_asgi_app
    
    # Create metrics
    REQUEST_COUNT = Counter(
        "request_count", 
        "App Request Count", 
        ["app_name", "method", "endpoint", "status_code"]
    )
    
    REQUEST_LATENCY = Histogram(
        "request_latency_seconds", 
        "Request latency in seconds", 
        ["app_name", "method", "endpoint"]
    )
    
    CHAT_TOKENS_USED = Counter(
        "chat_tokens_used", 
        "Number of tokens used in chat", 
        ["user_id", "model"]
    )
    
    # Create metrics endpoint
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    
    @app.middleware("http")
    async def monitor_requests(request: Request, call_next):
        """Middleware to monitor HTTP requests."""
        method = request.method
        path = request.url.path
        
        # Skip metrics endpoint itself
        if path == "/metrics":
            return await call_next(request)
        
        start_time = time.time()
        
        response = await call_next(request)
        
        # Record metrics
        status_code = response.status_code
        REQUEST_COUNT.labels(
            app_name="ai_agent",
            method=method,
            endpoint=path,
            status_code=status_code
        ).inc()
        
        REQUEST_LATENCY.labels(
            app_name="ai_agent",
            method=method,
            endpoint=path
        ).observe(time.time() - start_time)
        
        return response
