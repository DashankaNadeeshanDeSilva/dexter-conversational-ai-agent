# API Reference

**Note that this documentation is created with partial help of GenAI tools.**

This document provides comprehensive documentation for all Dexter API endpoints, including request/response formats, authentication, and usage examples.

## Table of Contents

- [Getting Started](#getting-started)
- [Authentication](#authentication)
- [Core Endpoints](#core-endpoints)
- [Memory Management](#memory-management)
- [Session Control](#session-control)
- [Health & Monitoring](#health--monitoring)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)

## Getting Started

### Base URL

```
Production: https://api.dexter-ai.com/api/v1
Development: http://localhost:8000/api/v1
```

### Content Type

All API requests should use `Content-Type: application/json` unless otherwise specified.

### Response Format

All responses follow a consistent format:

```json
{
  "success": true,
  "data": { /* response data */ },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_abc123"
}
```

Error responses:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": { /* specific error details */ }
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_abc123"
}
```

## Authentication

Dexter uses API key authentication for production environments.

### API Key Authentication

Include your API key in the request headers:

```http
Authorization: Bearer your-api-key-here
```

### Example Request

```bash
curl -X POST https://api.dexter-ai.com/api/v1/chat \
  -H "Authorization: Bearer your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how can you help me today?",
    "user_id": "user123",
    "session_id": "session456"
  }'
```

## Core Endpoints

### Chat Endpoint

The primary endpoint for conversational interactions with Dexter.

#### `POST /chat`

**Description**: Send a message to Dexter and receive an intelligent response.

**Request Body**:
```json
{
  "message": "string (required) - User's message",
  "user_id": "string (required) - Unique user identifier", 
  "session_id": "string (optional) - Session ID for conversation continuity",
  "context": {
    "metadata": "object (optional) - Additional context information"
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "response": "Dexter's response message",
    "session_id": "session_abc123",
    "tools_used": ["product_search", "semantic_retrieval"],
    "memory_updates": {
      "semantic_facts_added": 2,
      "episodic_events_recorded": 1,
      "procedural_patterns_learned": 0
    },
    "response_metadata": {
      "processing_time_ms": 1250,
      "confidence_score": 0.95,
      "sources_consulted": ["semantic_memory", "episodic_memory"]
    }
  }
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find me a wireless gaming headset under $150",
    "user_id": "user123"
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "response": "I found several excellent wireless gaming headsets under $150. Here are my top recommendations:\n\n1. **SteelSeries Arctis 7P** - $149.99\n   - Excellent audio quality with DTS Headphone:X 2.0\n   - 24-hour battery life\n   - Compatible with PS5, PS4, PC, and mobile\n\n2. **HyperX Cloud Flight** - $129.99\n   - 30-hour battery life\n   - Detachable noise-cancelling microphone\n   - Comfortable for long gaming sessions\n\nWould you like more details about any of these options or see additional choices?",
    "session_id": "sess_789xyz",
    "tools_used": ["product_search"],
    "memory_updates": {
      "semantic_facts_added": 1,
      "episodic_events_recorded": 1,
      "procedural_patterns_learned": 0
    }
  }
}
```

### Agent Status

#### `GET /agent/status`

**Description**: Get current agent status and capabilities.

**Response**:
```json
{
  "success": true,
  "data": {
    "status": "online",
    "version": "1.0.0",
    "capabilities": [
      "product_search",
      "appointment_booking", 
      "semantic_retrieval",
      "web_search"
    ],
    "memory_systems": {
      "semantic_memory": "operational",
      "episodic_memory": "operational", 
      "procedural_memory": "operational",
      "session_manager": "operational"
    },
    "performance_metrics": {
      "average_response_time_ms": 875,
      "success_rate": 0.98,
      "active_sessions": 42
    }
  }
}
```

## Memory Management

### Semantic Memory

#### `POST /memory/semantic/query`

**Description**: Query the semantic memory for relevant facts and knowledge.

**Request Body**:
```json
{
  "query": "string (required) - Search query",
  "user_id": "string (required) - User identifier",
  "max_results": "integer (optional, default: 10) - Maximum results to return",
  "similarity_threshold": "float (optional, default: 0.75) - Minimum similarity score"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "fact_id": "fact_123",
        "content": "User prefers morning appointments",
        "similarity_score": 0.89,
        "source_session": "session_456",
        "created_at": "2024-01-10T09:15:00Z"
      }
    ],
    "total_results": 1,
    "query_embedding_time_ms": 45
  }
}
```

#### `POST /memory/semantic/facts`

**Description**: Manually add semantic facts to memory.

**Request Body**:
```json
{
  "facts": [
    {
      "content": "string (required) - Fact content",
      "user_id": "string (required) - User identifier", 
      "confidence": "float (optional, default: 0.9) - Confidence score",
      "source": "string (optional) - Source of the fact"
    }
  ]
}
```

### Episodic Memory

#### `GET /memory/episodic/events`

**Description**: Retrieve episodic events for a user or session.

**Query Parameters**:
- `user_id` (string, required): User identifier
- `session_id` (string, optional): Specific session ID
- `event_type` (string, optional): Filter by event type
- `start_date` (string, optional): Start date (ISO format)
- `end_date` (string, optional): End date (ISO format)
- `limit` (integer, optional, default: 50): Maximum results

**Response**:
```json
{
  "success": true,
  "data": {
    "events": [
      {
        "event_id": "event_789",
        "session_id": "session_456",
        "timestamp": "2024-01-15T10:30:00Z",
        "event_type": "message",
        "content": "User asked about product recommendations",
        "context": {
          "emotional_tone": "positive",
          "user_satisfaction": 0.85
        }
      }
    ],
    "total_events": 1,
    "query_time_ms": 12
  }
}
```

### Procedural Memory

#### `GET /memory/procedural/patterns`

**Description**: Retrieve learned procedural patterns.

**Query Parameters**:
- `pattern_type` (string, optional): Filter by pattern type
- `min_success_rate` (float, optional): Minimum success rate threshold
- `limit` (integer, optional, default: 20): Maximum results

**Response**:
```json
{
  "success": true,
  "data": {
    "patterns": [
      {
        "pattern_id": "pattern_123",
        "pattern_type": "appointment_booking",
        "success_rate": 0.92,
        "usage_count": 45,
        "strategy": {
          "steps": ["extract_provider", "check_availability", "suggest_times"],
          "tools": ["appointment_tool"]
        },
        "last_used": "2024-01-15T09:45:00Z"
      }
    ],
    "total_patterns": 1
  }
}
```

## Session Control

### Session Management

#### `POST /sessions`

**Description**: Create a new conversation session.

**Request Body**:
```json
{
  "user_id": "string (required) - User identifier",
  "metadata": "object (optional) - Session metadata"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "session_id": "sess_new123",
    "user_id": "user456",
    "created_at": "2024-01-15T10:30:00Z",
    "status": "active"
  }
}
```

#### `GET /sessions/{session_id}`

**Description**: Get session details and statistics.

**Response**:
```json
{
  "success": true,
  "data": {
    "session_id": "sess_123",
    "user_id": "user456",
    "created_at": "2024-01-15T10:30:00Z",
    "last_activity": "2024-01-15T10:45:00Z",
    "status": "active",
    "message_count": 12,
    "tools_used": ["product_search", "appointment_tool"],
    "engagement_metrics": {
      "average_response_time": 2.3,
      "user_satisfaction": 0.88,
      "conversation_depth": 6
    }
  }
}
```

#### `POST /sessions/{session_id}/end`

**Description**: Explicitly end a session.

**Response**:
```json
{
  "success": true,
  "data": {
    "session_id": "sess_123",
    "ended_at": "2024-01-15T10:50:00Z",
    "final_stats": {
      "total_messages": 12,
      "duration_minutes": 20,
      "tools_used": 3,
      "user_satisfaction": 0.88
    }
  }
}
```

#### `GET /sessions`

**Description**: List sessions for a user.

**Query Parameters**:
- `user_id` (string, required): User identifier
- `status` (string, optional): Filter by status (active/ended)
- `limit` (integer, optional, default: 50): Maximum results
- `offset` (integer, optional, default: 0): Results offset

## Health & Monitoring

### Health Check

#### `GET /health`

**Description**: System health status.

**Response**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "services": {
      "database": "operational",
      "pinecone": "operational",
      "memory_systems": "operational",
      "tools": "operational"
    },
    "performance": {
      "average_response_time_ms": 875,
      "success_rate": 0.98,
      "active_sessions": 42,
      "requests_per_minute": 120
    },
    "version": "1.0.0"
  }
}
```

### Memory Health

#### `GET /health/memory`

**Description**: Detailed memory system health.

**Response**:
```json
{
  "success": true,
  "data": {
    "semantic_memory": {
      "status": "operational",
      "total_facts": 15420,
      "average_query_time_ms": 45,
      "index_utilization": 0.78
    },
    "episodic_memory": {
      "status": "operational", 
      "total_events": 89650,
      "average_query_time_ms": 12,
      "storage_utilization": 0.65
    },
    "procedural_memory": {
      "status": "operational",
      "total_patterns": 342,
      "average_success_rate": 0.87,
      "learning_efficiency": 0.92
    },
    "session_manager": {
      "status": "operational",
      "active_sessions": 42,
      "total_sessions_today": 156,
      "average_session_duration_min": 18
    }
  }
}
```

### Metrics

#### `GET /metrics`

**Description**: Prometheus-compatible metrics endpoint.

**Response**: Prometheus metrics format

```
# HELP dexter_requests_total Total requests processed
# TYPE dexter_requests_total counter
dexter_requests_total{method="POST",endpoint="/chat"} 1234

# HELP dexter_response_time_seconds Response time in seconds
# TYPE dexter_response_time_seconds histogram
dexter_response_time_seconds_bucket{le="0.5"} 890
dexter_response_time_seconds_bucket{le="1.0"} 1180
dexter_response_time_seconds_bucket{le="2.0"} 1220
dexter_response_time_seconds_bucket{le="+Inf"} 1234
```

## Error Handling

### Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `VALIDATION_ERROR` | Invalid request parameters | 400 |
| `AUTHENTICATION_ERROR` | Invalid or missing API key | 401 |
| `AUTHORIZATION_ERROR` | Insufficient permissions | 403 |
| `NOT_FOUND` | Resource not found | 404 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `INTERNAL_ERROR` | Server error | 500 |
| `SERVICE_UNAVAILABLE` | Service temporarily unavailable | 503 |

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "user_id",
      "issue": "Required field missing"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_abc123"
}
```

### Common Error Scenarios

#### Missing Required Fields

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Missing required field: user_id",
    "details": {
      "required_fields": ["user_id", "message"],
      "provided_fields": ["message"]
    }
  }
}
```

#### Session Not Found

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Session not found",
    "details": {
      "session_id": "sess_invalid123",
      "suggestion": "Create a new session or verify the session ID"
    }
  }
}
```

## Rate Limiting

Dexter implements rate limiting to ensure fair usage and system stability.

### Default Limits

- **Authenticated requests**: 1000 requests per hour per API key
- **Chat endpoint**: 60 requests per minute per user
- **Memory queries**: 300 requests per hour per user

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999  
X-RateLimit-Reset: 1642252800
X-RateLimit-Window: 3600
```

### Rate Limit Exceeded Response

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded",
    "details": {
      "limit": 60,
      "window_seconds": 60,
      "retry_after_seconds": 45
    }
  }
}
```

## Examples

### Complete Chat Flow

```javascript
// 1. Start a new session
const sessionResponse = await fetch('/api/v1/sessions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-api-key'
  },
  body: JSON.stringify({
    user_id: 'user123'
  })
});

const { session_id } = (await sessionResponse.json()).data;

// 2. Send a message
const chatResponse = await fetch('/api/v1/chat', {
  method: 'POST', 
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-api-key'
  },
  body: JSON.stringify({
    message: 'Find me a good laptop for programming',
    user_id: 'user123',
    session_id: session_id
  })
});

const chatResult = await chatResponse.json();
console.log(chatResult.data.response);

// 3. Continue conversation
const followUpResponse = await fetch('/api/v1/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json', 
    'Authorization': 'Bearer your-api-key'
  },
  body: JSON.stringify({
    message: 'What about gaming laptops under $2000?',
    user_id: 'user123',
    session_id: session_id
  })
});

// 4. End session when done
await fetch(`/api/v1/sessions/${session_id}/end`, {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your-api-key'
  }
});
```

### Memory Query Example

```python
import requests

# Query semantic memory for user preferences
response = requests.post(
    'http://localhost:8000/api/v1/memory/semantic/query',
    json={
        'query': 'appointment preferences',
        'user_id': 'user123',
        'max_results': 5,
        'similarity_threshold': 0.75
    },
    headers={'Authorization': 'Bearer your-api-key'}
)

facts = response.json()['data']['results']
for fact in facts:
    print(f"Fact: {fact['content']} (Score: {fact['similarity_score']})")
```

### Webhook Integration

```javascript
// Example webhook handler for chat completions
app.post('/webhook/chat-complete', (req, res) => {
  const { session_id, user_id, response_data } = req.body;
  
  // Process completion event
  console.log(`Chat completed for session: ${session_id}`);
  console.log(`User satisfaction: ${response_data.user_satisfaction}`);
  
  // Acknowledge receipt
  res.json({ success: true, processed: true });
});

// Register webhook with Dexter (if webhooks are configured)
const webhookResponse = await fetch('/api/v1/webhooks', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-api-key'
  },
  body: JSON.stringify({
    url: 'https://your-app.com/webhook/chat-complete',
    events: ['chat.completed', 'session.ended'],
    secret: 'your-webhook-secret'
  })
});
```

For more information, see:
- [Architecture Guide](ARCHITECTURE.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Development Guide](DEVELOPMENT.md)
