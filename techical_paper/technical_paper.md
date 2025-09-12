Title: Dexter: A Memory-Centric Conversational AI Agent for Customer Support

Authors: Dashanka De Silva et al.

Version: 1.1 (Product-Oriented Research Paper Draft)

Date: 2025-09-11

Abstract

We present Dexter, a production-ready conversational AI agent tailored for customer support. Dexter integrates a ReAct-style reasoning engine with a multi-store memory system—short-term, semantic, episodic, and procedural—to achieve continuity, personalization, and robust tool use. Unlike stateless chatbots, Dexter maintains context across sessions, extracts durable facts, and learns effective strategies from successful interactions. It exposes a FastAPI interface, supports domain tools (product search, appointment management, semantic knowledge retrieval, web search), and ships with monitoring, security, and comprehensive tests. We detail the system design, implementation, and evaluation framework, emphasizing product goals (resolution rate, CSAT proxy, latency, cost) and pragmatic engineering trade-offs. This is a living paper accompanying an evolving codebase.

Keywords: conversational AI, memory systems, ReAct, RAG, customer support, Pinecone, MongoDB, FastAPI, LangChain, LangGraph

1 Introduction

Customer support assistants must understand evolving context, remember preferences, and reliably execute tasks. Prior approaches often rely on stateless prompting or narrow flows, producing brittle behavior and impersonal experiences. Dexter addresses these limitations with: (i) a ReAct agent that plans and acts via tools; (ii) a unified memory manager spanning working, event, fact, and strategy memories; and (iii) a production surface with APIs, observability, and tests. Our goal is practical: elevate first-contact resolution and user satisfaction while controlling latency and cost.

Contributions:
- A modular, memory-centric architecture that operationalizes human-like memory types in production.
- A ReAct+LangGraph agent that integrates memory retrieval and tool execution.
- A product-oriented evaluation harness (tests, metrics scaffolding) for reliability and performance.

2 Related Work

ReAct combines step-by-step reasoning with tool calls to improve decision making and factuality [1]. Retrieval-Augmented Generation (RAG) enriches responses with external knowledge retrieved by similarity search [2]. Foundational cognitive theories describe complementary memory systems: episodic memory for events [3], working memory for transient context [4], and procedural memory for learned skills and strategies [5]. Recent work on memory-augmented language models further demonstrates the value of non-parametric memories to improve recall and adaptability [6]. Dexter synthesizes these strands into a cohesive, deployable system for customer support, with explicit multi-memory orchestration and production operability (APIs, monitoring, tests, deployment assets).

3 System Overview

Dexter is a Python 3.11+ service built on FastAPI. The agent uses OpenAI models via LangChain and LangGraph. Persistence spans MongoDB (conversations, episodic/procedural) and Pinecone (semantic facts and knowledge). Short-term memory is in-process per session. Prometheus/Grafana provide observability. Docker-based workflows and AWS artifacts support deployment.

Repository anchors: app/ (agent, api, memory, tools, utils), docs/, tests/, deployment/, monitoring/.

Figure 1: System Architecture Overview. The agent (FastAPI service) integrates a ReAct+LangGraph controller with multi-store memory (short-term, episodic/procedural via MongoDB, semantic via Pinecone) and a tool ecosystem. See: ![](docs/System_Architecture.png)

4 Methods: Architecture and Algorithms

4.1 Memory-Oriented Architecture

Short-term (working) memory serves as a session-scoped buffer that maintains immediate discourse context, consistent with the role of working memory in human cognition [4]. Semantic memory captures durable, context-independent facts extracted from interaction windows and stores them as embeddings in Pinecone to enable similarity-based retrieval [2]. Episodic memory records time-ordered conversation events and tool outcomes in MongoDB, mirroring Tulving’s conception of episodic recollection [3]. Procedural memory retains successful strategies and tool-usage patterns—an operational analogue of skill learning [5]—to guide future decisions.

4.2 Agent Graph (ReAct with LangGraph)

The agent maintains an AgentState (messages, ids, tools). Think composes a system prompt with tool descriptions and memory context; the model may emit tool_calls following the ReAct paradigm [1]. A conditional edge routes to use_tool when tool_calls exist; otherwise the response is emitted. ToolNode executes tools and returns ToolMessage entries; the loop continues until a final response is produced.

4.3 Memory Algorithms

For each user turn, the system assembles context by retrieving relevant semantic facts from Pinecone and, where appropriate, consulting episodic and procedural signals exposed via utility functions. Periodically—every N messages—the SemanticExtractor processes a rolling window of recent messages to surface candidate facts, enriching each with entities and confidence estimates before persisting them to Pinecone with descriptive metadata. Following successful responses, whether tool-assisted or not, the agent materializes a procedural pattern that records the pattern_type, succinct rationale, and query context, enabling future decisions to benefit from prior successes.

5 Implementation

5.1 API and Contracts

FastAPI endpoints: /chat (main interaction), /conversations (create/list/get), /memories/query (semantic/episodic/procedural), /session/{session_id}/reset (short-term reset), /health, and optionally /metrics. Pydantic models validate inputs/outputs and timestamp messages.

5.2 Tools

The Product Search tool interprets natural-language queries using an LLM to extract structured filters and gracefully falls back to regex heuristics when needed; it compiles MongoDB queries and returns clearly formatted product summaries. The Appointment Management tool enforces operation-specific requirements, checks availability, performs CRUD actions, and communicates outcomes in user-friendly language. The Semantic Retrieval tool queries Pinecone to surface relevant knowledge, returning grounded content with its source attribution and similarity scores. Finally, the Web Search tool complements internal knowledge by providing an external retrieval path for open-domain information when appropriate.

5.3 Storage

MongoDB stores conversations, episodic events, and procedural patterns with metadata. Pinecone stores semantic facts and knowledge documents with per-user scopes and rich metadata to enable filtered retrieval.

5.4 Configuration and Prompts

Configuration is environment-driven (OpenAI, Pinecone, MongoDB, metrics, prompt path). The system prompt lives in app/agent/system_prompts and is augmented at runtime with current tool descriptions and retrieved memory context.

6 Evaluation (Product-Oriented)

Objectives and proxies:
- Resolution rate: fraction of sessions where user intent is resolved (proxied by tests and tool success paths).
- CSAT proxy: heuristic scoring of responses (readability, task completion signals).
- Latency: p95 endpoint latency under nominal load (middleware metrics, performance tests).
- Cost: token usage and tool invocation counts (metric scaffolding provided).

Methodology:
- Unit and integration tests (tests/) cover agent flow, tools, memory CRUD, and API contracts.
- Performance tests evaluate latency trends and concurrency behavior.
- Observability: Prometheus counters/histograms for requests and latency; extensible business metrics suggested (e.g., CHAT_TOKENS_USED).

Reporting: The repository includes coverage tooling and dashboards; teams can plug CI to gate on reliability and coverage thresholds.

7 Case Studies and Usage Scenarios

- Product discovery: Price- and feature-aware search that recalls prior preferences from semantic memory.
- Appointment workflows: End-to-end booking with availability checks and rescheduling; procedural memory accumulates successful patterns.
- Knowledge questions: RAG-like responses grounded in internal knowledge, with web search as fallback when allowed.

8 Limitations

- Session consolidation is a placeholder; long-horizon summarization and spaced rehearsal are deferred.
- Tool outcome learning on failures is scaffolded but can be extended to adaptive retries and guarded parameter suggestions.
- Access control and multi-tenant isolation can be strengthened via middleware and DB scoping patterns.

9 Ethical and Privacy Considerations

We recommend explicit consent, data minimization, and retention policies. Provide export/deletion capabilities and auditability of tool use. Encrypt data at rest and in transit; segregate user data and enforce strict scoping in retrieval.

10 Deployment and Operations

Local development via docker-compose and Makefile; production via Docker and AWS assets. Uvicorn serves the FastAPI app; /metrics exposes Prometheus data. Scale horizontally; consider DB sharding and caching (e.g., Redis) for hot data and short-term memory.

11 Results Summary and Practical Impact

In practice, Dexter’s memory-centric approach is designed to improve continuity (reduced repetition), personalization (preference recall), and task success (tool guidance via procedural memory). The engineering assets (APIs, tests, monitoring) support safe iteration and measurable gains. Teams can track resolution rate, latency, and cost to tune prompts, tools, and memory thresholds.

12 Future Work

- Implement session-level knowledge consolidation and periodic rehearsal.
- Expand procedural learning for failure-aware strategies and parameter recommendations.
- Add fine-grained authN/Z and tenancy; introduce privacy filters into retrieval.
- Explore streaming responses and parallel tool execution when safe.

13 Conclusion

Dexter operationalizes multi-memory conversational AI in a production setting. By unifying ReAct planning, tool use, and memory orchestration under a clean API and observability stack, it provides a practical foundation for customer support automation. The design choices emphasize measurable product outcomes alongside research-informed memory structures.

Acknowledgments

Built with FastAPI, LangChain/LangGraph, OpenAI, MongoDB, and Pinecone. We thank the open-source community and contributors.

References

- [1] Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models," 2022.
- [2] Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP," NeurIPS, 2020.
- [3] Tulving, "Episodic and Semantic Memory," Organization of Memory, 1972.
- [4] Baddeley, "Working Memory," Science, 1992.
- [5] Anderson, "Acquisition of Cognitive Skill," Psychological Review, 1982.
- [6] Borgeaud et al., "Improving language models by retrieving from trillions of tokens," ICML, 2022.

Project documentation and assets:
- docs/ARCHITECTURE.md, docs/API.md, docs/DEVELOPMENT.md, docs/DEPLOYMENT.md, docs/USAGE_EXAMPLES.md
- System diagrams: docs/System_Architecture_overview.jpeg, docs/Detailed_system.png, docs/System_Architecture.png
- Core modules: app/agent/agent.py, app/memory/memory_manager.py, app/tools/*.py, app/api/main.py, app/api/models.py, app/config.py

Appendix A: API Summary

- GET /health → status
- POST /chat → {conversation_id, session_id, message}
- POST /conversations/create_new → {user_id, conversation_id}
- GET /conversations/{user_id}
- GET /conversations/{user_id}/{conversation_id}
- POST /memories/query → semantic | episodic | procedural
- POST /session/{session_id}/reset
- GET /metrics (optional)

Appendix B: Configuration Keys (selected)

- OPENAI_API_KEY, OPENAI_MODEL, EMBEDDING_MODEL
- MONGODB_URI, MONGODB_DATABASE, *_COLLECTION
- PINECONE_API_KEY, PINECONE_*_INDEX
- ENABLE_METRICS, SYSTEM_PROMPT_PATH


