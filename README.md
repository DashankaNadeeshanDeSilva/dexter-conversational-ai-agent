# 🤖 Dexter v1.0 - Advanced Conversational AI Agent Backend

A sophisticated, production-ready open-source AI agent backend featuring cognitive science-inspired memory systems, intelligent tool usage, and comprehensive session management. Built for enterprise applications requiring persistent memory, natural language understanding, and seamless tool integration.

![](docs/System_Architecture_overview.jpg)

## 🌟 Highlights

🧠 **Revolutionary Memory Architecture**: Four-layer cognitive memory system (short-term, semantic, episodic, procedural) based on cognitive science principles  
⚡ **Lightning Fast**: High-performance FastAPI backend with optimized database queries  
🔧 **Extensible Tools**: Intelligent appointment booking, product search, semantic retrieval, and web search capabilities  
🎯 **Session Intelligence**: Advanced session lifecycle management with activity tracking and conversation continuity  
🚀 **Enterprise Ready**: Docker containerization, monitoring, testing, and AWS deployment automation  
📈 **Observable**: Complete monitoring with Prometheus/Grafana dashboards and LangSmith tracing  

## ✨ Core Features

### 🧠 Cognitive Memory Systems
- **Session Manager**: Complete lifecycle management with activity tracking and intelligent session persistence
- **Semantic Extractor**: LLM-powered fact extraction using cognitive science principles for knowledge consolidation
- **Episodic Memory**: Detailed conversation event tracking and temporal relationship modeling
- **Procedural Memory**: Tool usage pattern learning and successful strategy retention
- **Short-term Memory**: Real-time conversation context maintenance with automatic cleanup

### 🛠️ Intelligent Tool Suite
- **�️ Product Search**: Advanced filtering by price, category, availability with natural language queries
- **📅 Appointment Management**: Full CRUD operations with conflict detection and NER-based provider extraction
- **🔍 Semantic Retrieval**: Vector-based knowledge search using Pinecone with similarity thresholds
- **🌐 Web Search**: Real-time information retrieval for current events and external knowledge

### � ReAct Agent Framework
- **Reasoning Engine**: Multi-step problem decomposition and solution planning
- **Action Execution**: Intelligent tool selection and parameter extraction
- **Memory Integration**: Continuous learning from interactions and tool usage patterns
- **Error Recovery**: Robust error handling with fallback strategies

### 🏗️ Production Architecture
- **FastAPI Backend**: High-performance REST API with automatic documentation
- **Modular Design**: Clean separation of concerns with pluggable components
- **Session Management**: Comprehensive endpoint suite for session control and analytics
- **Memory Analytics**: Query endpoints for memory system introspection
- **Health Monitoring**: Complete observability with metrics and health checks

## 🔧 Tech Stack

**Core Framework**  
- LangChain/LangGraph for agent orchestration and tool management
- FastAPI for high-performance API endpoints with automatic OpenAPI documentation

**Memory & Storage**  
- MongoDB for episodic memory, procedural patterns, and session persistence
- Pinecone for semantic vector storage and similarity search
- Redis for short-term memory and caching (optional)

**AI & Intelligence**  
- OpenAI GPT-4 for reasoning, semantic extraction, and natural language understanding
- spaCy for named entity recognition and linguistic processing
- Custom embedding models for semantic memory consolidation

**Infrastructure & Deployment**  
- Docker & Docker Compose for containerization and development
- AWS ECS with CloudFormation for production deployment
- Prometheus & Grafana for monitoring and observability
- GitHub Actions for CI/CD automation

**Development & Testing**  
- Pytest for comprehensive unit and integration testing
- LangSmith for agent tracing and debugging
- Pre-commit hooks for code quality
- Type hints and Pydantic models for robust data validation

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- MongoDB (local or hosted)
- Pinecone Account
- OpenAI API Key

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/dexter-conversational-ai-agent.git
   cd dexter-conversational-ai-agent
   ```

2. **Environment Configuration**:
   ```bash
   cp .env.example .env
   ```
   Configure your `.env` file with the following required variables:
   ```env
   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key
   
   # MongoDB Configuration
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DATABASE=dexter_agent
   
   # Pinecone Configuration
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX=dexter-semantic-memory
   PINECONE_ENVIRONMENT=us-west1-gcp
   
   # LangSmith (Optional)
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your_langsmith_api_key
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run with Docker** (Recommended):
   ```bash
   docker-compose up -d
   ```

5. **Or run locally**:
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```

### 🎯 API Usage Examples

**Start a conversation session**:
```bash
curl -X POST "http://localhost:8000/api/v1/sessions" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "user123"}'
```

**Chat with the agent**:
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Find me wireless headphones under $100",
       "session_id": "session_id_from_previous_call",
       "user_id": "user123"
     }'
```

**Book an appointment**:
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Schedule a consultation with Dr. Smith tomorrow at 2 PM",
       "session_id": "session_id",
       "user_id": "user123"
     }'
```

**End a session**:
```bash
curl -X POST "http://localhost:8000/api/v1/sessions/{session_id}/end" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "user123"}'
```

**Get session statistics**:
```bash
curl -X GET "http://localhost:8000/api/v1/sessions/{session_id}/stats?user_id=user123"
```

## 🔧 Advanced Configuration

### Memory System Configuration

Configure memory behavior in `app/config.py`:

```python
# Memory retention settings
SHORT_TERM_MEMORY_TTL = 3600  # 1 hour
SEMANTIC_SIMILARITY_THRESHOLD = 0.75
MAX_EPISODIC_EVENTS_PER_SESSION = 1000

# Session management
SESSION_TIMEOUT = 1800  # 30 minutes
AUTO_SESSION_CLEANUP = True
```

### Tool Configuration

Add custom tools by extending the base tool class:

```python
from app.tools.base_tool import BaseTool

class CustomTool(BaseTool):
    name = "custom_tool"
    description = "Your custom tool description"
    
    def _run(self, query: str) -> str:
        # Your tool implementation
        return "Tool result"
```

### Docker Deployment

Full production deployment with monitoring:

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f dexter-agent

# Scale the application
docker-compose up --scale dexter-agent=3
```

## 🏗️ Architecture Overview

```
dexter-conversational-ai-agent/
├── app/
│   ├── agent/              # Core ReAct agent implementation
│   │   └── agent.py       # Main agent logic with tool integration
│   ├── api/               # FastAPI application and endpoints
│   │   └── main.py        # REST API with session and memory endpoints
│   ├── memory/            # Modular memory systems
│   │   ├── memory_manager.py      # Central memory coordinator
│   │   ├── session_manager.py     # Session lifecycle management
│   │   ├── semantic_extractor.py  # LLM-based fact extraction
│   │   ├── episodic_memory.py     # Event-based memory storage
│   │   ├── procedural_memory.py   # Pattern and skill learning
│   │   ├── short_term_memory.py   # Real-time context management
│   │   ├── mongodb_client.py      # MongoDB persistence layer
│   │   └── pinecone_client.py     # Vector storage interface
│   ├── tools/             # Intelligent tool suite
│   │   ├── appointment_tool.py    # Advanced appointment management
│   │   ├── product_search_tool.py # E-commerce search capabilities
│   │   ├── semantic_retrieval_tool.py # Vector-based knowledge search
│   │   └── search_tool.py         # Web search integration
│   └── utils/             # Shared utilities
│       ├── logging_utils.py       # Structured logging
│       └── auth_utils.py          # Authentication helpers
├── deployment/            # Production deployment
│   └── aws/              # AWS CloudFormation templates
├── monitoring/           # Observability stack
│   ├── grafana/          # Custom dashboards
│   └── prometheus.yml    # Metrics collection
├── tests/                # Comprehensive test suite
├── docs/                 # Documentation and diagrams
└── docker-compose.yml    # Multi-service orchestration
```

## 🧠 Memory Systems Deep Dive

### Session Manager
- **Lifecycle Management**: Complete session creation, activity tracking, and explicit termination
- **Statistics**: Conversation metrics, tool usage analytics, and session duration tracking
- **Persistence**: MongoDB-backed session storage with user association

### Semantic Extractor  
- **Cognitive Approach**: Uses cognitive science principles for fact extraction
- **LLM Integration**: GPT-4 powered semantic analysis with structured outputs
- **Knowledge Consolidation**: Transforms conversations into persistent factual knowledge

### Episodic Memory
- **Event Storage**: Detailed conversation event tracking with temporal relationships
- **Context Preservation**: Maintains conversation flow and interaction history
- **Query Interface**: Rich querying capabilities for conversation analysis

### Procedural Memory
- **Pattern Learning**: Captures successful tool usage patterns and strategies
- **Skill Retention**: Maintains knowledge about effective problem-solving approaches
- **Adaptation**: Continuously improves based on interaction outcomes

## 🛠️ Tool Ecosystem

### Product Search Tool
- **Natural Language Processing**: "Find wireless headphones under $100 in electronics"
- **Advanced Filtering**: Price ranges, categories, availability status
- **Inventory Integration**: Real-time stock checking and specification matching

### Appointment Tool
- **CRUD Operations**: Complete appointment lifecycle management
- **NLP Understanding**: Natural language date/time parsing and provider extraction
- **Conflict Detection**: Automatic scheduling conflict resolution
- **Provider Recognition**: Named entity recognition for healthcare providers

### Semantic Retrieval Tool
- **Vector Search**: Pinecone-powered similarity search with configurable thresholds
- **Knowledge Base**: Persistent storage of extracted facts and learned information
- **Context Awareness**: Integrates with episodic memory for enhanced relevance

## 📊 API Reference

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/chat` | POST | Send message to agent |
| `/api/v1/sessions` | POST | Create new session |
| `/api/v1/sessions/{id}/end` | POST | End active session |
| `/api/v1/sessions/{id}/stats` | GET | Session analytics |
| `/api/v1/memory/semantic` | GET | Query semantic memory |
| `/api/v1/memory/episodic` | GET | Retrieve conversation events |
| `/health` | GET | Health check |

### Session Management
```python
# Session creation response
{
  "session_id": "uuid-string",
  "user_id": "user123",
  "created_at": "2024-01-01T00:00:00Z",
  "status": "active"
}

# Session statistics response
{
  "session_id": "uuid-string", 
  "message_count": 15,
  "tool_usage": {"product_search": 3, "appointment": 2},
  "duration_seconds": 1847,
  "total_tokens": 12450
}
```

## 🚀 Production Deployment

### AWS Deployment

Deploy to AWS ECS using CloudFormation:

```bash
# Deploy infrastructure
aws cloudformation deploy \
  --template-file deployment/aws/cloudformation.yml \
  --stack-name dexter-agent-stack \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    Environment=production \
    ImageTag=latest

# Update service
aws ecs update-service \
  --cluster dexter-agent-cluster \
  --service dexter-agent-service \
  --force-new-deployment
```

### Monitoring & Observability

Access monitoring dashboards:
- **Grafana**: `http://localhost:3000` (admin/admin)
- **Prometheus**: `http://localhost:9090`
- **Agent API Docs**: `http://localhost:8000/docs`

Key metrics monitored:
- Request latency and throughput
- Memory system performance
- Tool usage patterns
- Session analytics
- Error rates and system health

### Testing

Run the comprehensive test suite:

```bash
# Unit tests
pytest tests/unit/

# Integration tests  
pytest tests/integration/

# Memory system tests
pytest tests/test_memory_manager.py -v

# API endpoint tests
pytest tests/test_api.py -v

# Coverage report
pytest --cov=app tests/
```

## 🤝 Contributing

We welcome contributions! This project is designed to be:

- **Modular**: Easy to extend with new tools and memory components
- **Well-Tested**: Comprehensive test coverage for reliability
- **Documented**: Clear documentation for all components
- **Production-Ready**: Enterprise-grade architecture and monitoring

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Install development dependencies: `pip install -r requirements-dev.txt`
4. Run tests: `pytest`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Adding New Tools

Extend the agent's capabilities by creating new tools:

```python
# app/tools/my_custom_tool.py
from app.tools.base_tool import BaseTool

class MyCustomTool(BaseTool):
    name = "my_custom_tool"
    description = "Description of what your tool does"
    
    def _run(self, query: str) -> str:
        # Your tool implementation
        return "Tool output"
```

Register in `app/agent/agent.py`:
```python
from app.tools.my_custom_tool import MyCustomTool

# Add to tools list
tools = [
    # ... existing tools
    MyCustomTool()
]
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Support

If you find this project helpful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs and issues
- 💡 Suggesting new features
- 🤝 Contributing code improvements

---

Built with ❤️ for the open-source AI community. Dexter represents the future of conversational AI with human-like memory and reasoning capabilities.
