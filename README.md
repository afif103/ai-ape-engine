# APE - AI Productivity Engine

> All-in-one AI-powered web platform for research, creation, automation, and development.

## Features

- 🤖 **AI Chat Engine** - Conversational AI with context management
- 🔍 **Deep Research** - Web scraping and content analysis with citations
- 📊 **Smart Data Extraction** - **FULLY IMPLEMENTED** - Upload files, AI processing, edit data, multi-format export
- 💻 **Code Assistant** - Code generation, review, and explanation
- 🎨 **Media Generation** - AI images, TTS, video (coming soon)
- 🤝 **Chatbot Builder** - Custom AI assistants (coming soon)
- ⚡ **Workflow Automation** - Multi-step task orchestration (coming soon)

## 🚀 Data Extraction System (Production Ready)

**Fully functional file upload, processing, and export system:**

- **File Support**: CSV, TXT, PDF, DOCX, Images (PNG/JPG)
- **AI Processing**: Table detection, OCR, structure recognition
- **Data Editing**: Inline table editing with real-time updates
- **Export Formats**: CSV, JSON, Excel (.xlsx), XML, HTML
- **Security**: JWT authentication, file validation, size limits
- **Performance**: Docker deployment, async processing, caching

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
- Frontend: http://localhost:3001

### Data Extraction Workflow

1. **Register/Login**: Create account and authenticate
2. **Upload Files**: Drag-and-drop CSV, TXT, PDF, DOCX, or images
3. **AI Processing**: Automatic table detection and data extraction
4. **Edit Data**: Modify extracted data inline
5. **Export**: Download in CSV, JSON, Excel, XML, or HTML formats

**Current Status**: ✅ **FULLY FUNCTIONAL** - Complete data extraction and export system working

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


## License

MIT

## Support

For issues and feature requests, please open an issue on GitHub.
