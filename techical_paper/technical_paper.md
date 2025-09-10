Title: Dexter – A Production-Ready Conversational AI Agent with Human-Like Memory

Authors: Dashanka De Silva et al.

Version: 1.0

Date: 2025-09-10

Abstract

Dexter is a production-ready conversational AI agent backend designed for customer support assistance. It combines a ReAct-style reasoning engine with a multi-store memory architecture—short-term, semantic, episodic, and procedural—to deliver contextual, adaptive, and personalized interactions across sessions. The system integrates tool-augmented actions (product search, appointment management, semantic knowledge retrieval, web search), provides a robust FastAPI surface, and includes monitoring, security, testing, and deployment assets. This paper presents Dexter’s architecture, design decisions, API, memory systems, tools, data flow, performance, observability, and security posture, with references to implementation artifacts in the repository.

Keywords: ReAct, conversational AI, memory systems, RAG, Pinecone, MongoDB, FastAPI, LangChain, LangGraph

1. Introduction

Customer support automation requires both strong reasoning and long-lived memory. Stateless chatbots struggle with continuity, personalization, and complex workflows. Dexter addresses these gaps by integrating:
- A ReAct agent that plans, reasons, and invokes tools
- A unified memory manager orchestrating four memory types
- A tool ecosystem for domain actions and retrieval
- A production-grade API, security, monitoring, tests, and deployment scaffolding

The result is an agent capable of human-like continuity—remembering preferences, recalling prior interactions, and reusing successful strategies—while safely integrating with operational data sources and company knowledge.

2. System Overview

Dexter is a Python 3.11+ backend service exposing REST endpoints via FastAPI. Core compute is powered by OpenAI models via LangChain/LangGraph. Persistent state is split across MongoDB (episodic/procedural, conversations), Pinecone (semantic vectors and knowledge), and an in-process short-term memory for working context. Monitoring integrates Prometheus/Grafana. Deployment targets local Docker or cloud (AWS ECS) with IaC artifacts.

Repository anchors:
- Application: app/
- API: app/api
- Agent: app/agent
- Memory system: app/memory
- Tools: app/tools
- Configuration: app/config.py
- Docs: docs/
- Tests: tests/

3. Architecture

3.1 High-Level Components

- ReAct Agent (app/agent/agent.py): Orchestrates reasoning, tool selection, and memory usage using LangGraph state machines. Binds tools and injects memory context into prompts.
- Memory Manager (app/memory/memory_manager.py): Facade over all memory types and storage clients. Provides CRUD for conversations and long-term memories, and utilities for semantic extraction.
- Tools (app/tools): Domain actions and retrieval capabilities: product search, appointment management, semantic knowledge retrieval, and web search.
- API (app/api/main.py, app/api/models.py): FastAPI endpoints for chat, conversations, and memory queries with Pydantic models for validation.
- Storage Clients: MongoDB client (episodic/procedural, conversations), Pinecone client (semantic memories and knowledge base).
- Configuration (app/config.py): Environment-driven configuration (OpenAI, Pinecone, MongoDB, metrics, system prompts).

3.2 Reasoning and Control Flow

The agent uses a LangGraph StateGraph with nodes for think and use_tool. The decision function checks the most recent LLM output: if tool_calls are present, the agent transitions to use_tool; otherwise it ends with a response. Memory is consulted before generation to enrich context.

3.3 Memory-Oriented Design

- Short-term (Working) Memory: Session-scoped conversational context, stored in-memory via ShortTermMemory. This supports immediate discourse continuity and semantic extraction windows.
- Semantic Memory: Factual knowledge extracted from conversations and stored as embeddings in Pinecone. Retrieval provides relevant facts to the prompt.
- Episodic Memory: Chronological event logging of conversation messages and significant interactions in MongoDB. Useful for audits, longitudinal analysis, and recall of specific events.
- Procedural Memory: Patterns of successful strategies and tool usage stored in MongoDB, informing future action selection and parameterization.

4. Memory Systems

4.1 Short-Term Memory

Purpose: Maintain working context (messages) for a session. The agent writes user and assistant messages into short-term memory; periodic extraction uses recent windows to derive semantic facts.

Key behaviors:
- get_short_term_memory(session_id) lazily initializes a ShortTermMemory per session
- add_user_message/add_ai_message append to the rolling context
- clear_short_term_memory(session_id) resets state (exposed via /session/{session_id}/reset)

4.2 Semantic Memory (Pinecone)

Purpose: Store durable, context-free facts extracted from interaction windows.

Pipeline:
1) Extract facts via SemanticExtractor (LLM-guided)
2) Store facts with metadata (entities, confidence, context requirements) using PineconeClient
3) Retrieve similar facts for queries to enrich prompting and responses

APIs:
- store_semantic_memory(user_id, text, metadata)
- retrieve_semantic_memories(user_id, query, k, filter_metadata)
- store_extracted_semantic_facts(user_id, facts, conversation_metadata)

4.3 Episodic Memory (MongoDB)

Purpose: Capture time-ordered events (messages, tool outcomes) per conversation.

APIs:
- store_event(user_id, content, metadata)
- store_conversation_message(user_id, conversation_id, message)
- retrieve_events(user_id, filter_query, limit)

Each message added to a conversation is also mirrored to episodic memory for complete lineage.

4.4 Procedural Memory (MongoDB)

Purpose: Learn and store successful patterns and tool usage to inform future actions.

APIs:
- store_pattern(user_id, content, metadata)
- store_successful_pattern(user_id, pattern_type, pattern_description, context, metadata)
- get_tool_usage_patterns(user_id, tool_name?, query_context?, success_only)
- retrieve_patterns(user_id, filter_query, limit)

Usage: After successful responses or tool calls, patterns are saved with context and tags (e.g., tool_category). Failures can also be recorded for error-aware learning (agent logic contains scaffolding).

5. Agent Design (ReAct + LangGraph)

5.1 State and Prompting

Agent state (AgentState) includes messages, user_id, session_id, conversation_id, tools, and tool_names. The system prompt is loaded from app/agent/system_prompts/system_prompt.md and augmented at runtime with tool descriptions and retrieved memory context.

5.2 Tool Binding and Decisioning

The LLM is bound with available tools using tool_choice="auto". After the think step produces an AIMessage, the graph routes either to use_tool (if tool_calls present) or ends with RESPONSE. ToolNode integrates tool execution results back into the state as ToolMessage entries, which are then used for follow-up reasoning.

5.3 Memory Interaction

- Pre-generation: Retrieve semantic/episodic/procedural context based on the latest human message via AgentMemoryUtils and MemoryManager
- Post-generation: Update episodic memory with both user and assistant messages; periodically extract and store semantic facts; store procedural patterns when a response succeeds; optionally log tool usage outcomes

6. Tool Ecosystem

6.1 Product Search Tool (app/tools/product_search_tool.py)

Function: Natural-language product queries with intelligent filter extraction.

Highlights:
- LLM-guided filter extraction to JSON (category, price_range, availability, brand, features) with robust fallback (regex and simple heuristics)
- MongoDB filter construction and query to a product collection via DatabaseClient
- User-friendly result formatting with price, availability, and specifications snippets

6.2 Appointment Management Tool (app/tools/appointment_tool.py)

Function: Manage bookings end-to-end (book, cancel, reschedule, view, search_availability).

Highlights:
- Centralized validation by operation (required fields vary by action)
- Availability checks and CRUD via DatabaseClient
- Clear, human-readable confirmations and lists of appointments/availability

6.3 Semantic Knowledge Retrieval Tool (app/tools/semantic_retrieval_tool.py)

Function: Retrieve company knowledge via Pinecone similarity search (RAG-like).

Highlights:
- Query top_k relevant documents and format results with source and scores
- Optional similarity thresholding (scaffolding present)

6.4 Web Search Tool

Function: External web search capability (implementation present in app/tools/web_search_tool.py). Used when internal knowledge is insufficient.

7. API Surface

Implemented with FastAPI (app/api/main.py) and Pydantic models (app/api/models.py). Key endpoints:

- GET /health → HealthResponse
- POST /chat → ChatResponse
  - Accepts user_id, message, optional conversation_id and session_id
  - Creates conversation/session if not supplied
  - Returns assistant message plus resolved ids
- POST /conversations/create_new → create conversation for a user
- GET /conversations/{user_id} → list conversations (paginated by limit)
- GET /conversations/{user_id}/{conversation_id} → retrieve a conversation
- POST /memories/query → MemoryQueryResponse (semantic | episodic | procedural)
- POST /session/{session_id}/reset → clear short-term memory
- Optional: /metrics (Prometheus) when ENABLE_METRICS is true

Request/Response Validation: app/api/models.py defines ChatRequest, ChatResponse, ConversationListResponse, MemoryQueryRequest, MemoryQueryResponse, HealthResponse.

8. Data Flow

8.1 Chat Processing Pipeline

1) Receive request → validate models
2) Ensure conversation_id and session_id exist via MemoryManager
3) Write user message to short-term and episodic memory
4) Build AgentState and run LangGraph workflow
5) Optionally execute tools (ToolNode)
6) Generate assistant response
7) Write assistant message to episodic memory
8) Periodically extract semantic facts and store in Pinecone
9) Store successful procedural patterns
10) Return response

8.2 Memory Query

- Semantic: vector similarity via Pinecone; return Document content + metadata + score
- Episodic/Procedural: MongoDB retrieval with optional filters and limits

9. Configuration and Secrets

Configuration is centralized in app/config.py using pydantic-settings and dotenv. Key variables:
- MongoDB: MONGODB_URI, MONGODB_DATABASE, collection names
- Pinecone: PINECONE_API_KEY, PINECONE_*_INDEX
- OpenAI: OPENAI_API_KEY, OPENAI_MODEL, EMBEDDING_MODEL
- LangChain: LANGCHAIN_TRACING, LANGCHAIN_PROJECT, LANGCHAIN_API_KEY
- Monitoring: ENABLE_METRICS
- System Prompt Path: SYSTEM_PROMPT_PATH

10. Monitoring and Observability

When ENABLE_METRICS is enabled, the app mounts /metrics (Prometheus). Built-in HTTP middleware records request counts and latencies; business counters (e.g., CHAT_TOKENS_USED) are scaffolded for extension. The repository includes Grafana dashboards under monitoring/grafana and Prometheus configuration in monitoring/prometheus.yml.

11. Security Considerations

- Input validation via Pydantic models
- Logging of errors with minimal sensitive data
- Token-based authentication and rate limiting are documented in README and can be enforced at the API gateway/reverse proxy (implementation hooks can be added to FastAPI dependencies)
- Data privacy: Conversations and memories are user-scoped; retrieval APIs accept user_id and always filter by it

12. Testing Strategy

The tests/ suite covers unit, API, integration, performance, and database behaviors. Fixtures mock external dependencies (OpenAI, Pinecone, MongoDB) to ensure deterministic runs. Coverage targets are ≥80% overall with higher thresholds on critical paths. The test runner supports parallelization and multiple report formats.

Representative categories:
- test_agent*.py: Agent initialization, reasoning, and tool selection
- test_memory_*.py: Memory manager and individual memory components
- test_tools.py: Tool behaviors and validation
- test_api.py: Endpoint contracts and error handling
- test_performance.py: Latency and throughput under load

13. Deployment

- Local: docker-compose.yml for dev; Makefile targets for build/run
- Production: Dockerfile and AWS assets (deployment/aws/cloudformation.yml); environment-driven configuration for portability
- Runtime: uvicorn app.main:app or via container entrypoint; optional metrics exposure

14. Performance and Scalability

Optimizations:
- Short-term memory kept in-process for low-latency iteration
- MongoDB and Pinecone clients reused; filtering and indexing recommended for production data volumes
- LangGraph enables multi-turn tool reasoning with minimal overhead
- Batch embeddings and adjustable k for retrieval trade-offs

Scalability:
- Stateless API layer permits horizontal scaling and load balancing
- Database sharding/partitioning by user or tenant is feasible
- Caching layers (Redis) can be introduced for short-term memory or hot data

15. Limitations and Future Work

- Session Manager: The docs outline a richer session manager (engagement metrics, preferences) that is partially deferred; hooks exist to add it cleanly.
- Consolidation: MemoryManager.consolidate_session_knowledge is a placeholder; future work can implement session-level consolidation and spaced rehearsal.
- Tool Outcome Learning: Failure case learning exists in agent scaffolding; can be expanded to adaptive retries and guarded tool param suggestions.
- Access Control: Fine-grained authz and multi-tenant isolation layers can be added depending on environment.

16. Ethical Use and Privacy

Dexter is designed to handle user data responsibly. Operators should:
- Obtain user consent for data retention and personalization
- Apply data minimization, retention policies, and encryption at rest/in transit
- Provide user-accessible memory export and deletion
- Audit tool usage and ensure transparency

17. Reproducibility and Setup

Prerequisites:
- Python 3.11+, MongoDB, Pinecone, OpenAI API key

Steps (abridged):
1) pip install -r requirements.txt
2) Configure .env (OpenAI, MongoDB, Pinecone)
3) docker-compose up -d (recommended) or run uvicorn
4) Call /health, then /chat

18. Conclusion

Dexter demonstrates how principled memory design dramatically improves conversational agents: continuity, personalization, and effectiveness. The modular architecture, clear APIs, and comprehensive tooling make it a practical foundation for real-world customer support and beyond. With session consolidation, richer procedural learning, and expanded governance, Dexter can evolve into a full-fledged cognitive assistant platform.

References

- Repository documentation: docs/ARCHITECTURE.md, docs/API.md, docs/DEVELOPMENT.md, docs/DEPLOYMENT.md, docs/USAGE_EXAMPLES.md
- System diagrams: docs/System_Architecture_overview.jpeg, docs/Detailed_system.png, docs/System_Architecture.png
- Core modules: app/agent/agent.py, app/memory/memory_manager.py, app/tools/*.py, app/api/main.py, app/api/models.py, app/config.py

Appendix A: API Summary

- GET /health → service status
- POST /chat → {conversation_id, session_id, message}
- POST /conversations/create_new → {user_id, conversation_id}
- GET /conversations/{user_id} → list conversations
- GET /conversations/{user_id}/{conversation_id} → conversation detail
- POST /memories/query → semantic | episodic | procedural results
- POST /session/{session_id}/reset → clears short-term memory
- GET /metrics (optional) → Prometheus exposition

Appendix B: Configuration Keys (selected)

- OPENAI_API_KEY, OPENAI_MODEL, EMBEDDING_MODEL
- MONGODB_URI, MONGODB_DATABASE, *_COLLECTION
- PINECONE_API_KEY, PINECONE_*_INDEX
- ENABLE_METRICS, SYSTEM_PROMPT_PATH


