# APE - AI Productivity Engine

> All-in-one AI-powered web platform for research, creation, automation, and development.

## Features

- 🤖 **AI Chat Engine** - Conversational AI with context management
- 🔍 **Deep Research** - Web scraping and content analysis with citations
- 📊 **Smart Data Extraction** - OCR + web scraping with user-defined schemas
- 💻 **Code Assistant** - Code generation, review, and explanation
- 🎨 **Media Generation** - AI images, TTS, video (coming soon)
- 🤝 **Chatbot Builder** - Custom AI assistants (coming soon)
- ⚡ **Workflow Automation** - Multi-step task orchestration (coming soon)

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, LangChain, LangGraph
- **Database**: PostgreSQL, Redis, ChromaDB
- **AI**: Groq (dev), AWS Bedrock (prod), Multi-provider fallback
- **Frontend**: Next.js, Tailwind CSS (separate repo)
- **Infrastructure**: Docker, AWS ECS Fargate

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- API Keys: Groq, AWS (optional), Firecrawl

### Installation

```bash
# Clone repository
git clone <repo-url>
cd apev5

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env

# Start with Docker Compose
docker-compose up --build

# Or run locally
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

### API Documentation

Once running, visit:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Project Structure

```
apev5/
├── src/
│   ├── api/          # API routes, middleware, schemas
│   ├── services/     # Business logic
│   ├── repositories/ # Data access
│   ├── models/       # Database models
│   ├── llm/          # LLM providers
│   ├── external/     # External service clients
│   ├── core/         # Utilities
│   └── db/           # Database setup
├── tests/            # Test suites
├── docs/             # Documentation
└── scripts/          # Utility scripts
```

## Development

```bash
# Run tests
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# Lint and format
ruff check .
ruff format .

# Type check
mypy src --ignore-missing-imports

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Documentation

- [Requirements](docs/requirements.json)
- [Architecture](docs/architecture.md)
- AGENTS.md - Development framework (kept locally, not in repository)

## License

MIT

## Support

For issues and feature requests, please open an issue on GitHub.
