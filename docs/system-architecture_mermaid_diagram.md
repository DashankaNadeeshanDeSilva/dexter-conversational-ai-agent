# Dexter AI Agent - System Architecture Diagram

This document contains the Mermaid diagram code for visualizing the complete system architecture of the Dexter conversational AI agent.

## Complete System Architecture

```mermaid
graph TB
    %% User Interaction Layer
    subgraph "Client Layer"
        UI[Web Interface]
        API_CLIENT[API Clients]
        MOBILE[Mobile Apps]
    end

    %% API Gateway Layer
    subgraph "API Layer"
        FASTAPI[FastAPI Backend<br/>Port 8000]
        DOCS[OpenAPI Docs<br/>/docs]
        HEALTH[Health Check<br/>/health]
    end

    %% Core Agent System
    subgraph "Agent Core"
        AGENT[ReAct Agent<br/>LangGraph]
        REASONING[Reasoning Engine]
        ACTION[Action Executor]
        TOOL_ROUTER[Tool Router]
    end

    %% Memory Management System
    subgraph "Memory Systems"
        MEMORY_MGR[Memory Manager<br/>Central Coordinator]
        
        subgraph "Session Layer"
            SESSION_MGR[Session Manager<br/>Lifecycle Control]
            SHORT_TERM[Short-term Memory<br/>Real-time Context]
        end
        
        subgraph "Long-term Memory"
            SEMANTIC_EXT[Semantic Extractor<br/>LLM-based Facts]
            EPISODIC[Episodic Memory<br/>Event Tracking]
            PROCEDURAL[Procedural Memory<br/>Pattern Learning]
            SEMANTIC_MEM[Semantic Memory<br/>Vector Knowledge]
        end
    end

    %% Tool Ecosystem
    subgraph "Intelligent Tools"
        PRODUCT_TOOL[Product Search Tool<br/>E-commerce Integration]
        APPOINTMENT_TOOL[Appointment Tool<br/>CRUD + NER]
        SEMANTIC_TOOL[Semantic Retrieval<br/>Vector Search]
        WEB_TOOL[Web Search Tool<br/>Real-time Info]
        CUSTOM_TOOLS[Custom Tools<br/>Extensible]
    end

    %% Storage Layer
    subgraph "Data Storage"
        MONGODB[(MongoDB<br/>Document Store)]
        PINECONE[(Pinecone<br/>Vector DB)]
        REDIS[(Redis<br/>Cache - Optional)]
    end

    %% External Services
    subgraph "AI Services"
        OPENAI[OpenAI GPT-4<br/>LLM Reasoning]
        EMBEDDINGS[Embedding Models<br/>Vector Generation]
        SPACY[spaCy NLP<br/>Entity Recognition]
    end

    %% Monitoring & Observability
    subgraph "Monitoring Stack"
        PROMETHEUS[Prometheus<br/>Metrics Collection]
        GRAFANA[Grafana<br/>Dashboards]
        LANGSMITH[LangSmith<br/>Agent Tracing]
        LOGS[Structured Logging]
    end

    %% Infrastructure
    subgraph "Infrastructure"
        DOCKER[Docker<br/>Containerization]
        AWS_ECS[AWS ECS<br/>Production Deploy]
        CLOUDFORMATION[CloudFormation<br/>Infrastructure as Code]
        GITHUB_ACTIONS[GitHub Actions<br/>CI/CD Pipeline]
    end

    %% Data Flow Connections
    UI --> FASTAPI
    API_CLIENT --> FASTAPI
    MOBILE --> FASTAPI
    
    FASTAPI --> AGENT
    FASTAPI --> SESSION_MGR
    FASTAPI --> MEMORY_MGR
    
    AGENT --> REASONING
    AGENT --> ACTION
    AGENT --> TOOL_ROUTER
    AGENT --> MEMORY_MGR
    
    REASONING --> OPENAI
    ACTION --> TOOL_ROUTER
    
    TOOL_ROUTER --> PRODUCT_TOOL
    TOOL_ROUTER --> APPOINTMENT_TOOL
    TOOL_ROUTER --> SEMANTIC_TOOL
    TOOL_ROUTER --> WEB_TOOL
    TOOL_ROUTER --> CUSTOM_TOOLS
    
    MEMORY_MGR --> SESSION_MGR
    MEMORY_MGR --> SHORT_TERM
    MEMORY_MGR --> SEMANTIC_EXT
    MEMORY_MGR --> EPISODIC
    MEMORY_MGR --> PROCEDURAL
    MEMORY_MGR --> SEMANTIC_MEM
    
    SESSION_MGR --> MONGODB
    EPISODIC --> MONGODB
    PROCEDURAL --> MONGODB
    SHORT_TERM --> REDIS
    
    SEMANTIC_EXT --> OPENAI
    SEMANTIC_MEM --> PINECONE
    SEMANTIC_TOOL --> PINECONE
    
    APPOINTMENT_TOOL --> SPACY
    PRODUCT_TOOL --> MONGODB
    
    %% Monitoring Connections
    FASTAPI -.-> PROMETHEUS
    AGENT -.-> LANGSMITH
    MONGODB -.-> PROMETHEUS
    PINECONE -.-> PROMETHEUS
    
    PROMETHEUS --> GRAFANA
    
    %% Styling
    classDef userLayer fill:#e1f5fe
    classDef apiLayer fill:#f3e5f5
    classDef agentLayer fill:#e8f5e8
    classDef memoryLayer fill:#fff3e0
    classDef toolLayer fill:#fce4ec
    classDef storageLayer fill:#e0f2f1
    classDef aiLayer fill:#f1f8e9
    classDef monitorLayer fill:#e8eaf6
    classDef infraLayer fill:#fafafa
    
    class UI,API_CLIENT,MOBILE userLayer
    class FASTAPI,DOCS,HEALTH apiLayer
    class AGENT,REASONING,ACTION,TOOL_ROUTER agentLayer
    class MEMORY_MGR,SESSION_MGR,SHORT_TERM,SEMANTIC_EXT,EPISODIC,PROCEDURAL,SEMANTIC_MEM memoryLayer
    class PRODUCT_TOOL,APPOINTMENT_TOOL,SEMANTIC_TOOL,WEB_TOOL,CUSTOM_TOOLS toolLayer
    class MONGODB,PINECONE,REDIS storageLayer
    class OPENAI,EMBEDDINGS,SPACY aiLayer
    class PROMETHEUS,GRAFANA,LANGSMITH,LOGS monitorLayer
    class DOCKER,AWS_ECS,CLOUDFORMATION,GITHUB_ACTIONS infraLayer
```

## Memory System Detail View

```mermaid
graph TB
    subgraph "Memory Architecture Deep Dive"
        USER_INPUT[User Message Input]
        
        subgraph "Session Management"
            SESSION_CREATE[Create/Resume Session]
            SESSION_TRACK[Activity Tracking]
            SESSION_STATS[Statistics Collection]
            SESSION_END[Session Termination]
        end
        
        subgraph "Memory Processing Pipeline"
            CONTEXT[Context Analysis]
            EXTRACT[Fact Extraction]
            CATEGORIZE[Memory Categorization]
            STORE[Storage Routing]
        end
        
        subgraph "Memory Types"
            STM[Short-term Memory<br/>• Conversation Context<br/>• Immediate State<br/>• Session Variables]
            
            SEM[Semantic Memory<br/>• Factual Knowledge<br/>• Conceptual Relations<br/>• Vector Embeddings]
            
            EPI[Episodic Memory<br/>• Conversation Events<br/>• Temporal Sequences<br/>• User Interactions]
            
            PRO[Procedural Memory<br/>• Tool Usage Patterns<br/>• Successful Strategies<br/>• Learned Behaviors]
        end
        
        subgraph "Retrieval System"
            QUERY[Memory Query]
            SIMILARITY[Similarity Search]
            CONTEXT_MERGE[Context Merging]
            RESPONSE[Enhanced Response]
        end
        
        USER_INPUT --> SESSION_CREATE
        SESSION_CREATE --> CONTEXT
        CONTEXT --> EXTRACT
        EXTRACT --> CATEGORIZE
        CATEGORIZE --> STORE
        
        STORE --> STM
        STORE --> SEM
        STORE --> EPI
        STORE --> PRO
        
        QUERY --> STM
        QUERY --> SEM
        QUERY --> EPI
        QUERY --> PRO
        
        STM --> SIMILARITY
        SEM --> SIMILARITY
        EPI --> SIMILARITY
        PRO --> SIMILARITY
        
        SIMILARITY --> CONTEXT_MERGE
        CONTEXT_MERGE --> RESPONSE
    end
    
    classDef sessionLayer fill:#e3f2fd
    classDef processLayer fill:#f1f8e9
    classDef memoryLayer fill:#fff3e0
    classDef retrievalLayer fill:#fce4ec
    
    class SESSION_CREATE,SESSION_TRACK,SESSION_STATS,SESSION_END sessionLayer
    class CONTEXT,EXTRACT,CATEGORIZE,STORE processLayer
    class STM,SEM,EPI,PRO memoryLayer
    class QUERY,SIMILARITY,CONTEXT_MERGE,RESPONSE retrievalLayer
```

## Tool Integration Flow

```mermaid
sequenceDiagram
    participant User
    participant API as FastAPI
    participant Agent as ReAct Agent
    participant Memory as Memory Manager
    participant Tools as Tool Router
    participant Storage as Data Stores
    
    User->>API: Send Message
    API->>Memory: Create/Resume Session
    Memory->>Storage: Load Context
    API->>Agent: Process Message
    
    Agent->>Memory: Retrieve Relevant Context
    Memory->>Storage: Query Memory Systems
    Storage-->>Memory: Return Context
    Memory-->>Agent: Contextual Information
    
    Agent->>Agent: Reasoning Phase
    Agent->>Tools: Determine Tool Usage
    
    alt Product Search
        Tools->>Tools: Product Search Tool
        Tools->>Storage: Query Product DB
    else Appointment Booking
        Tools->>Tools: Appointment Tool
        Tools->>Storage: Check Availability
    else Semantic Search
        Tools->>Tools: Semantic Retrieval
        Tools->>Storage: Vector Search
    end
    
    Tools-->>Agent: Tool Results
    Agent->>Memory: Store Interaction
    Memory->>Storage: Persist Memory
    
    Agent-->>API: Generate Response
    API-->>User: Return Response
    
    Note over Memory,Storage: Continuous Learning<br/>from Interactions
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DEV_LOCAL[Local Development<br/>Docker Compose]
        DEV_TEST[Testing Suite<br/>Pytest + Coverage]
        DEV_LINT[Code Quality<br/>Pre-commit Hooks]
    end
    
    subgraph "CI/CD Pipeline"
        GIT[GitHub Repository]
        ACTIONS[GitHub Actions]
        BUILD[Docker Build]
        TEST_CI[Automated Testing]
        SECURITY[Security Scanning]
    end
    
    subgraph "AWS Production"
        ECR[AWS ECR<br/>Container Registry]
        ECS[AWS ECS<br/>Container Service]
        ALB[Application Load Balancer]
        
        subgraph "ECS Cluster"
            TASK1[Dexter Agent Task 1]
            TASK2[Dexter Agent Task 2]
            TASK3[Dexter Agent Task N]
        end
        
        subgraph "Data Layer"
            RDS[MongoDB Atlas<br/>or AWS DocumentDB]
            PINE[Pinecone Cloud<br/>Vector Database]
            ELASTICACHE[AWS ElastiCache<br/>Redis]
        end
        
        subgraph "Monitoring"
            CLOUDWATCH[CloudWatch Logs]
            PROM_AWS[Prometheus on ECS]
            GRAF_AWS[Grafana on ECS]
        end
    end
    
    DEV_LOCAL --> GIT
    GIT --> ACTIONS
    ACTIONS --> BUILD
    BUILD --> TEST_CI
    TEST_CI --> SECURITY
    SECURITY --> ECR
    
    ECR --> ECS
    ECS --> ALB
    ALB --> TASK1
    ALB --> TASK2
    ALB --> TASK3
    
    TASK1 --> RDS
    TASK2 --> RDS
    TASK3 --> RDS
    
    TASK1 --> PINE
    TASK2 --> PINE
    TASK3 --> PINE
    
    TASK1 --> ELASTICACHE
    TASK2 --> ELASTICACHE
    TASK3 --> ELASTICACHE
    
    ECS --> CLOUDWATCH
    ECS --> PROM_AWS
    PROM_AWS --> GRAF_AWS
    
    classDef devEnv fill:#e8f5e8
    classDef cicd fill:#e3f2fd
    classDef aws fill:#fff3e0
    classDef data fill:#f3e5f5
    classDef monitor fill:#fce4ec
    
    class DEV_LOCAL,DEV_TEST,DEV_LINT devEnv
    class GIT,ACTIONS,BUILD,TEST_CI,SECURITY cicd
    class ECR,ECS,ALB,TASK1,TASK2,TASK3 aws
    class RDS,PINE,ELASTICACHE data
    class CLOUDWATCH,PROM_AWS,GRAF_AWS monitor
```
