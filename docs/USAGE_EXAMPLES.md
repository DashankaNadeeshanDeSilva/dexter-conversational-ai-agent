## Usage Examples

### Basic Conversation
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find me wireless headphones under $200",
    "user_id": "user123"
  }'
```

### Product Search with Memory
```bash
# First interaction
POST /api/v1/chat
{
  "message": "I'm looking for gaming laptops",
  "user_id": "gamer_user"
}

# Follow-up interaction (Dexter remembers context)
POST /api/v1/chat
{
  "message": "What about ones with RTX 4080?",
  "user_id": "gamer_user"
}
```

### Appointment Management
```bash
POST /api/v1/chat
{
  "message": "Schedule a meeting with Dr. Smith tomorrow at 2 PM",
  "user_id": "patient_user"
}
```

## Memory System Details

1. **Semantic Memory**
Extracts and stores factual information from conversations:
```python
# Example stored facts
{
  "user_id": "user123",
  "fact": "User prefers morning appointments",
  "confidence": 0.95,
  "source": "conversation_456",
  "timestamp": "2025-01-27T10:30:00Z"
}
```

2. **Episodic Memory**
Stores complete interaction events:
```python
# Example episodic event
{
  "user_id": "user123",
  "event_type": "product_search",
  "query": "wireless headphones under $200",
  "tools_used": ["product_search"],
  "outcome": "found 5 matching products",
  "timestamp": "2025-01-27T10:30:00Z"
}
```
3. **Procedural Memory**
Learns successful patterns and strategies:
```python
# Example learned pattern
{
  "pattern_type": "tool_sequence",
  "context": "product_search_with_price_filter",
  "success_rate": 0.89,
  "typical_flow": ["extract_price_range", "filter_products", "rank_by_reviews"]
}
```

## Adding Custom Tools

1. **Create your tool class**:
```python
from app.tools.base_tool import BaseTool

class WeatherTool(BaseTool):
    name = "weather_search"
    description = "Get weather information for locations"
    
    async def _run(self, query: str, **kwargs) -> str:
        # Your tool implementation
        pass
```

2. **Register with the agent**:
```python
# In app/agent/agent.py
self.tools["weather_search"] = WeatherTool()
```

3. **Add configuration**:
```python
# In app/config.py
WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY")
```

An open-source conversational AI agent backend with memory systems for enterprise applications.

Sentence 2 (Technical Architecture): "Implemented a four-layer memory architecture (short-term, episodic, semantic, procedural) using ReAct framework with LangGraph, allowing the agent to learn preferences, remember interactions, and improve decision-making over time."

Sentence 3 (Technology Stack): "Built with FastAPI, OpenAI GPT-4, MongoDB, and Pinecone, featuring Docker deployment, AWS ECS integration, and Prometheus monitoring for production-ready enterprise deployment."