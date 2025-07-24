# Detailed Project Structure

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