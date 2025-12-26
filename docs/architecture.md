# APE - AI Productivity Engine: Architecture Design

**Version**: 1.0.0  
**Date**: 2024-12-25  
**Phase**: 1 - Architecture Design  
**Status**: Draft (Pending Approval)

---

## 1. System Overview

### 1.1 Architecture Pattern

**Chosen Pattern**: Modular Monolith with Clean Architecture

**Rationale**:
- Solo developer - microservices would add unnecessary complexity
- Faster development and deployment
- Easy to split into microservices later if needed
- Clear module boundaries enforce separation of concerns

**Trade-offs**:
- Pros: Simple deployment, shared database, easier debugging
- Cons: Must be careful about module coupling, single point of failure

### 1.2 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENTS                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Web App   │  │  Mobile App │  │   CLI Tool  │  │  API Users  │        │
│  │  (Next.js)  │  │   (Future)  │  │   (Future)  │  │  (Direct)   │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼────────────────┼────────────────┼────────────────┼────────────────┘
          │                │                │                │
          └────────────────┴────────────────┴────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            API GATEWAY                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         FastAPI Application                          │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │   Auth   │ │   CORS   │ │   Rate   │ │  Logging │ │  Error   │  │   │
│  │  │Middleware│ │Middleware│ │ Limiter  │ │Middleware│ │ Handler  │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API ROUTERS                                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │  /auth   │ │  /chat   │ │/research │ │  /data   │ │  /code   │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SERVICE LAYER                                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │    Auth     │ │    Chat     │ │  Research   │ │    Data     │           │
│  │   Service   │ │   Service   │ │   Service   │ │  Extraction │           │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                           │
│  │    Code     │ │    LLM      │ │   Export    │                           │
│  │   Service   │ │   Service   │ │   Service   │                           │
│  └─────────────┘ └─────────────┘ └─────────────┘                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES                                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │    Groq     │ │   AWS       │ │  Firecrawl  │ │    AWS      │           │
│  │    LLM      │ │  Bedrock    │ │   (Scrape)  │ │  Textract   │           │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ PostgreSQL  │ │    Redis    │ │  ChromaDB   │ │     S3      │           │
│  │  (Primary)  │ │   (Cache)   │ │  (Vectors)  │ │   (Files)   │           │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Design

### 2.1 Core Modules

| Module | Responsibility | Key Dependencies |
|--------|----------------|------------------|
| `auth` | User authentication, JWT tokens, sessions | PostgreSQL, Redis |
| `chat` | AI conversations, context management | LLM Service, ChromaDB |
| `research` | Web research, content analysis, citations | Firecrawl, LLM Service |
| `data_extraction` | OCR, web scraping, schema-based extraction | Textract, Firecrawl, LLM |
| `code` | Code generation, review, explanation | LLM Service |
| `llm` | Multi-provider LLM abstraction with fallback | Groq, Bedrock, OpenAI |
| `export` | Output formatting (JSON, CSV, Excel) | None |

### 2.2 Module Dependency Rules

```
┌─────────────────────────────────────────────────┐
│                   ROUTERS                        │
│            (Depends on Services)                 │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│                  SERVICES                        │
│      (Depends on Repositories + External)        │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│               REPOSITORIES                       │
│           (Depends on Models)                    │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│                   MODELS                         │
│              (No dependencies)                   │
└─────────────────────────────────────────────────┘

RULES:
- Lower layers NEVER import from higher layers
- Services can call other services (horizontal)
- All external calls go through dedicated service classes
```

---

## 3. Database Design

### 3.1 PostgreSQL Schema

```sql
-- Users & Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat & Conversations
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    model VARCHAR(50) DEFAULT 'auto',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    tokens_used INTEGER,
    model_used VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Research Sessions
CREATE TABLE research_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
    summary TEXT,
    sources JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Data Extraction Jobs
CREATE TABLE extraction_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    source_type VARCHAR(20) NOT NULL, -- 'document', 'web_single', 'web_crawl'
    source_url TEXT,
    source_file_path TEXT,
    schema_definition JSONB NOT NULL,
    validation_rules JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    result_data JSONB,
    error_message TEXT,
    rows_extracted INTEGER DEFAULT 0,
    rows_valid INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Audit Log (for compliance)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    details JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Usage Tracking
CREATE TABLE usage_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    service VARCHAR(50) NOT NULL, -- 'chat', 'research', 'extraction', 'code'
    tokens_input INTEGER DEFAULT 0,
    tokens_output INTEGER DEFAULT 0,
    cost_usd DECIMAL(10, 6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_extraction_jobs_user ON extraction_jobs(user_id);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_usage_records_user_date ON usage_records(user_id, created_at);
```

### 3.2 Redis Keys Structure

```
# Session Management
session:{session_id} -> JSON user data (TTL: 24h)

# Rate Limiting
ratelimit:{user_id}:{endpoint} -> count (TTL: 1min)

# Caching
cache:llm:{hash(prompt)} -> response (TTL: 1h)
cache:research:{hash(query)} -> results (TTL: 24h)
cache:extraction:{job_id} -> status (TTL: 1h)

# Job Queues (if needed)
queue:extraction -> list of job_ids
queue:research -> list of job_ids
```

### 3.3 ChromaDB Collections

```
# Document embeddings for RAG
collection: user_{user_id}_documents
  - id: document chunk ID
  - embedding: vector
  - metadata: {source, page, user_id}

# Research source embeddings
collection: research_{session_id}
  - id: source chunk ID
  - embedding: vector
  - metadata: {url, title, date}
```

---

## 4. API Design

### 4.1 API Structure

```
/api/v1
├── /auth
│   ├── POST /register          # Create account
│   ├── POST /login             # Get JWT tokens
│   ├── POST /refresh           # Refresh access token
│   ├── POST /logout            # Invalidate session
│   ├── POST /forgot-password   # Request reset
│   └── POST /reset-password    # Complete reset
│
├── /users
│   ├── GET  /me                # Get current user
│   ├── PUT  /me                # Update profile
│   └── GET  /me/usage          # Get usage stats
│
├── /chat
│   ├── GET    /conversations              # List conversations
│   ├── POST   /conversations              # Start new conversation
│   ├── GET    /conversations/{id}         # Get conversation
│   ├── DELETE /conversations/{id}         # Delete conversation
│   ├── POST   /conversations/{id}/messages # Send message
│   └── GET    /conversations/{id}/messages # Get messages
│
├── /research
│   ├── POST /sessions              # Start research
│   ├── GET  /sessions/{id}         # Get results
│   ├── GET  /sessions/{id}/export  # Export results
│   └── GET  /sessions              # List sessions
│
├── /extraction
│   ├── POST /jobs                  # Create extraction job
│   ├── GET  /jobs/{id}             # Get job status/results
│   ├── GET  /jobs/{id}/export      # Export as CSV/JSON/Excel
│   ├── POST /schema/detect         # AI schema detection
│   └── POST /validate              # Validate data against rules
│
├── /code
│   ├── POST /generate              # Generate code
│   ├── POST /review                # Review code
│   ├── POST /explain               # Explain code
│   └── POST /convert               # Convert between languages
│
└── /health
    └── GET /                       # Health check
```

### 4.2 Request/Response Examples

#### Chat Message
```json
// POST /api/v1/chat/conversations/{id}/messages
// Request
{
  "content": "Explain how async/await works in Python",
  "model": "auto"  // or "groq", "bedrock", "openai"
}

// Response
{
  "id": "msg_abc123",
  "role": "assistant",
  "content": "Async/await in Python is a way to write...",
  "model_used": "groq/llama-3.1-8b-instant",
  "tokens_used": 450,
  "created_at": "2024-12-25T10:30:00Z"
}
```

#### Data Extraction
```json
// POST /api/v1/extraction/jobs
// Request
{
  "source_type": "web_single",
  "source_url": "https://example.com/jobs",
  "schema": {
    "columns": [
      {"name": "Job Title", "type": "string", "required": true},
      {"name": "Company", "type": "string", "required": true},
      {"name": "Salary", "type": "string"},
      {"name": "Location", "type": "string"},
      {"name": "Posted Date", "type": "date"}
    ]
  },
  "validation_rules": {
    "Salary": {"pattern": "^\\$?[\\d,]+"}
  },
  "output_format": "csv"
}

// Response
{
  "job_id": "ext_xyz789",
  "status": "processing",
  "estimated_completion": "2024-12-25T10:31:00Z"
}
```

#### Schema Auto-Detection
```json
// POST /api/v1/extraction/schema/detect
// Request
{
  "url": "https://example.com/products"
}

// Response
{
  "detected_content_type": "product_listing",
  "confidence": 0.92,
  "suggested_schema": {
    "columns": [
      {"name": "Product Name", "type": "string", "required": true},
      {"name": "Price", "type": "number", "required": true},
      {"name": "Rating", "type": "number"},
      {"name": "Reviews Count", "type": "integer"},
      {"name": "URL", "type": "url"}
    ]
  },
  "sample_data": [
    {"Product Name": "Widget A", "Price": 29.99, "Rating": 4.5}
  ]
}
```

---

## 5. LLM Service Architecture

### 5.1 Multi-Provider Abstraction

```python
# Pseudocode for LLM Service
class LLMService:
    providers = [
        GroqProvider(priority=1),      # Fast, free tier
        BedrockProvider(priority=2),   # Production
        OpenAIProvider(priority=3)     # Fallback
    ]
    
    async def generate(self, prompt, model="auto"):
        if model != "auto":
            return await self.call_specific(model, prompt)
        
        for provider in sorted(self.providers, key=lambda p: p.priority):
            try:
                return await provider.generate(prompt)
            except ProviderError as e:
                log.warning(f"{provider.name} failed: {e}")
                continue
        
        raise AllProvidersFailedError()
```

### 5.2 Provider Configuration

| Provider | Model | Use Case | Cost |
|----------|-------|----------|------|
| Groq | llama-3.1-8b-instant | Local dev, fast responses | Free tier |
| Groq | llama-3.1-70b-versatile | Complex reasoning | Free tier |
| Bedrock | claude-3-5-sonnet | Production, high quality | $3/$15 per 1M |
| Bedrock | claude-3-haiku | Fast, cheap tasks | $0.25/$1.25 per 1M |
| OpenAI | gpt-4o | Fallback only | $5/$15 per 1M |

---

## 6. Project Structure

```
apev5/
├── AGENTS.md                    # Development framework
├── README.md                    # Project documentation
├── pyproject.toml               # Python project config
├── docker-compose.yml           # Local development
├── Dockerfile                   # Production image
├── .env.example                 # Environment template
├── .gitignore
│
├── docs/
│   ├── requirements.json        # Requirements document
│   ├── architecture.md          # This document
│   └── api/                     # API documentation
│
├── src/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry
│   ├── config.py                # Configuration management
│   ├── dependencies.py          # Dependency injection
│   │
│   ├── api/                     # API Layer
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── chat.py
│   │   │   ├── research.py
│   │   │   ├── extraction.py
│   │   │   ├── code.py
│   │   │   └── health.py
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── rate_limit.py
│   │   │   └── logging.py
│   │   └── schemas/             # Pydantic models for API
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── chat.py
│   │       ├── research.py
│   │       ├── extraction.py
│   │       └── code.py
│   │
│   ├── services/                # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── chat_service.py
│   │   ├── research_service.py
│   │   ├── extraction_service.py
│   │   ├── code_service.py
│   │   ├── llm_service.py
│   │   └── export_service.py
│   │
│   ├── repositories/            # Data Access Layer
│   │   ├── __init__.py
│   │   ├── user_repository.py
│   │   ├── conversation_repository.py
│   │   ├── extraction_repository.py
│   │   └── base.py
│   │
│   ├── models/                  # Database Models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   ├── extraction_job.py
│   │   └── base.py
│   │
│   ├── llm/                     # LLM Providers
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── groq_provider.py
│   │   ├── bedrock_provider.py
│   │   └── openai_provider.py
│   │
│   ├── external/                # External Service Clients
│   │   ├── __init__.py
│   │   ├── firecrawl_client.py
│   │   ├── textract_client.py
│   │   └── s3_client.py
│   │
│   ├── core/                    # Core Utilities
│   │   ├── __init__.py
│   │   ├── security.py          # JWT, hashing
│   │   ├── exceptions.py        # Custom exceptions
│   │   └── logging.py           # Logging config
│   │
│   └── db/                      # Database
│       ├── __init__.py
│       ├── session.py           # SQLAlchemy session
│       ├── redis.py             # Redis client
│       └── migrations/          # Alembic migrations
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── unit/
│   │   ├── test_auth_service.py
│   │   ├── test_chat_service.py
│   │   ├── test_extraction_service.py
│   │   └── ...
│   ├── integration/
│   │   ├── test_auth_api.py
│   │   ├── test_chat_api.py
│   │   └── ...
│   └── e2e/
│       └── test_user_journeys.py
│
├── frontend/                    # Next.js Frontend (separate)
│   ├── package.json
│   ├── next.config.js
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   └── stores/
│   └── ...
│
└── scripts/
    ├── setup.sh                 # Development setup
    ├── seed_db.py               # Database seeding
    └── test_providers.py        # Test LLM providers
```

---

## 7. Security Architecture

### 7.1 Authentication Flow

```
┌─────────┐         ┌─────────┐         ┌─────────┐
│  Client │         │   API   │         │   DB    │
└────┬────┘         └────┬────┘         └────┬────┘
     │                   │                   │
     │  POST /login      │                   │
     │  {email, pass}    │                   │
     │──────────────────▶│                   │
     │                   │  Verify password  │
     │                   │──────────────────▶│
     │                   │◀──────────────────│
     │                   │                   │
     │                   │  Generate JWT     │
     │  {access_token,   │  Store session    │
     │   refresh_token}  │──────────────────▶│ Redis
     │◀──────────────────│                   │
     │                   │                   │
     │  GET /api/...     │                   │
     │  Auth: Bearer ... │                   │
     │──────────────────▶│                   │
     │                   │  Validate JWT     │
     │                   │  Check session    │
     │  Response         │──────────────────▶│ Redis
     │◀──────────────────│                   │
```

### 7.2 Security Measures

| Layer | Measure | Implementation |
|-------|---------|----------------|
| Transport | TLS 1.3 | HTTPS everywhere |
| Auth | JWT | Short-lived (15min), refresh tokens |
| Password | bcrypt | Cost factor 12 |
| Rate Limit | Per-user | Redis sliding window |
| Input | Validation | Pydantic schemas |
| Output | Sanitization | No sensitive data in responses |
| AI | Guardrails | AWS Bedrock Guardrails |
| Audit | Logging | All actions logged |

---

## 8. Deployment Architecture

### 8.1 Local Development

```yaml
# docker-compose.yml
services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://redis:6379
    depends_on: [postgres, redis, chroma]
    
  postgres:
    image: postgres:16
    volumes: [postgres_data:/var/lib/postgresql/data]
    
  redis:
    image: redis:7-alpine
    
  chroma:
    image: chromadb/chroma
    volumes: [chroma_data:/chroma/chroma]
    
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
```

### 8.2 Production (AWS)

```
┌─────────────────────────────────────────────────────────────┐
│                        AWS Cloud                             │
│                                                              │
│  ┌──────────────┐     ┌──────────────┐                      │
│  │ CloudFront   │────▶│   S3 Static  │  (Frontend)          │
│  │    (CDN)     │     │    Hosting   │                      │
│  └──────┬───────┘     └──────────────┘                      │
│         │                                                    │
│         │ /api/*                                             │
│         ▼                                                    │
│  ┌──────────────┐     ┌──────────────┐                      │
│  │     ALB      │────▶│  ECS Fargate │  (API)               │
│  │ (Load Bal.)  │     │   Cluster    │                      │
│  └──────────────┘     └──────┬───────┘                      │
│                              │                               │
│         ┌────────────────────┼────────────────────┐         │
│         ▼                    ▼                    ▼         │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐ │
│  │     RDS      │     │ ElastiCache  │     │  OpenSearch  │ │
│  │ (PostgreSQL) │     │   (Redis)    │     │  (Vectors)   │ │
│  └──────────────┘     └──────────────┘     └──────────────┘ │
│                                                              │
│  ┌──────────────┐     ┌──────────────┐                      │
│  │   Bedrock    │     │   Textract   │                      │
│  │    (LLM)     │     │    (OCR)     │                      │
│  └──────────────┘     └──────────────┘                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Technology Decisions

### 9.1 Decision Log

| Decision | Choice | Alternatives | Rationale |
|----------|--------|--------------|-----------|
| API Framework | FastAPI | Flask, Django | Async support, auto docs, Pydantic |
| Database | PostgreSQL | MySQL, MongoDB | JSONB support, reliability, pgvector option |
| Cache | Redis | Memcached | Richer data structures, persistence |
| Vector DB | ChromaDB | Pinecone, Weaviate | Simple, local-first, good for MVP |
| LLM Framework | LangChain | Raw API calls | Abstractions, tool support, community |
| Web Scraping | Firecrawl | Scrapy, Playwright | AI-friendly markdown output, handles JS |
| Frontend | Next.js | React SPA, Vue | SSR option, file routing, good DX |

### 9.2 Scaling Strategy

**Phase 1 (MVP)**: Single container, vertical scaling
- 1 API instance on ECS Fargate (2 vCPU, 4GB)
- RDS db.t3.small
- ElastiCache t3.micro

**Phase 2 (Growth)**: Horizontal scaling
- Multiple API instances behind ALB
- Read replicas for PostgreSQL
- Redis cluster mode

**Phase 3 (Scale)**: Decomposition
- Extract heavy services (extraction, research) into separate services
- Add job queue (SQS/Celery) for async processing
- Consider dedicated vector database

---

## 10. Next Steps

After architecture approval:

1. **Setup Project Structure** - Create all directories and initial files
2. **Docker Environment** - docker-compose.yml for local development
3. **Database Setup** - SQLAlchemy models, Alembic migrations
4. **Core Infrastructure** - Config, logging, exceptions, security utilities
5. **Auth Module** - First feature to implement
6. **LLM Service** - Multi-provider abstraction

---

## Approval Checklist

- [ ] High-level architecture makes sense
- [ ] Database schema covers all features
- [ ] API structure is clear
- [ ] Project structure is organized
- [ ] Security measures are adequate
- [ ] Deployment strategy is feasible
- [ ] Technology choices are justified

**Ready to proceed to Phase 2 (Implementation)?**
