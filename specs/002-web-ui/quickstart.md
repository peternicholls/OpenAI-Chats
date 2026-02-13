# Quickstart Guide: ChatGPT Archive Web UI

**Feature**: 002-web-ui  
**Date**: 2026-02-12  
**Audience**: Developers setting up local development or production deployment

---

## Overview

This guide covers:
1. **Prerequisites** - Required tools and dependencies
2. **Local Development Setup** - Running frontend and backend separately
3. **Docker Deployment** - Production containerized deployment
4. **Testing** - Running tests
5. **Common Tasks** - Frequently used commands

---

## Prerequisites

### Required Software

| Tool | Version | Purpose |
|------|---------|---------|
| **Python** | 3.11+ | Backend API |
| **Node.js** | 20+ | Frontend build |
| **npm** | 10+ | Package manager |
| **Docker** | 24+ | Container runtime (for production) |
| **Docker Compose** | 2.20+ | Multi-container orchestration |
| **Git** | 2.40+ | Version control |

### Optional
- **OpenAI API Key** (for semantic search / embeddings)

---

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/peternicholls/OpenAI-Chats.git
cd OpenAI-Chats
git checkout 002-web-ui
```

---

### 2. Backend Setup (FastAPI)

#### Install Python dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install chatgpt_archive package with API dependencies
pip install -e ".[api]"  # Installs FastAPI, Uvicorn, etc.
```

#### Configure environment

```bash
# Set database path (optional, defaults to ~/.chatgpt-archive/chats.db)
export CHATGPT_ARCHIVE_DB=/path/to/your/chats.db

# Optional: OpenAI API key for embeddings
export OPENAI_API_KEY=sk-...
```

#### Initialize database (if needed)

```bash
# Import an archive first (creates database)
chatgpt-archive import /path/to/chatgpt-export/
```

#### Run backend server

```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend now running at: http://localhost:8000  
API docs available at: http://localhost:8000/docs (Swagger UI)

---

### 3. Frontend Setup (Next.js)

#### Install dependencies

```bash
cd web
npm install
```

#### Configure environment

Create `web/.env.local`:

```env
# API endpoint
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Analytics, etc.
```

#### Run development server

```bash
npm run dev
```

Frontend now running at: http://localhost:3000

---

### 4. Verify Setup

1. **Check backend health**: http://localhost:8000/api/health
2. **Open frontend**: http://localhost:3000
3. **Check API docs**: http://localhost:8000/docs

---

## Docker Deployment (Production)

### 1. Build and Run

From repository root:

```bash
# Build containers
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

Services:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000 (internal only, proxied via frontend)

---

### 2. Import Archive (Docker)

Option A: Mount archive directory as volume

```bash
# Edit docker-compose.yml, add volume:
services:
  api:
    volumes:
      - ./my-chatgpt-export:/import:ro

# Import via API container
docker-compose exec api chatgpt-archive import /import
```

Option B: Upload via web UI

1. Open http://localhost:3000
2. Navigate to "Import" page
3. Upload archive ZIP file

---

### 3. Manage Deployment

```bash
# Stop services
docker-compose down

# Stop and remove volumes (deletes database!)
docker-compose down -v

# View service status
docker-compose ps

# Rebuild after code changes
docker-compose build --no-cache
docker-compose up -d
```

---

## Testing

### Test Setup

#### Install Python Test Dependencies

```bash
source venv/bin/activate

# Install dev dependencies (pytest, httpx, etc.)
pip install -e ".[dev]"
cd api && pip install -e ".[dev]"
```

#### Install Frontend Test Dependencies

```bash
cd web

# Install Vitest, React Testing Library, MSW
npm install --save-dev \
  vitest @vitejs/plugin-react \
  @testing-library/react @testing-library/jest-dom @testing-library/user-event \
  jsdom msw
```

---

### Backend Tests (pytest)

```bash
# Activate venv
source venv/bin/activate

# Run all tests
pytest

# Run unit tests only
pytest tests/unit -v

# Run integration tests
pytest tests/integration -v

# Run with coverage
pytest --cov=chatgpt_archive --cov=api --cov-report=html

# Run specific test file
pytest tests/integration/test_api_conversations.py -v

# Run tests matching pattern
pytest -k "test_export" -v
```

#### Test Structure
```
tests/
├── conftest.py              # Shared fixtures (db, client)
├── fixtures/                # Sample data
├── unit/                    # Fast, isolated tests
│   ├── test_exporters.py
│   ├── test_search.py
│   └── test_embeddings.py
└── integration/             # API endpoint tests
    ├── test_api_conversations.py
    ├── test_api_search.py
    └── test_api_export.py
```

---

### Frontend Tests

#### Unit Tests (Vitest + React Testing Library)

```bash
cd web

# Run tests
npm test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run specific file
npm test -- api.test.ts
```

#### Test Structure
```
web/
├── __tests__/
│   ├── mocks/handlers.ts    # MSW request handlers
│   ├── services/api.test.ts
│   ├── hooks/               # Hook tests
│   └── components/          # Component tests
├── vitest.config.ts
└── vitest.setup.ts
```

#### E2E Tests (Playwright)

```bash
cd web

# Install Playwright browsers (first time only)
npx playwright install

# Run E2E tests
npm run test:e2e

# Run in UI mode (interactive)
npm run test:e2e:ui

# Run specific test
npx playwright test search.spec.ts
```

---

### CI/CD Test Pipeline

```yaml
# .github/workflows/test.yml
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - uses: actions/setup-node@v4
      with:
        node-version: '20'
    
    - name: Install Python deps
      run: |
        pip install -e ".[dev]"
        cd api && pip install -e ".[dev]"
    
    - name: Run Python tests
      run: pytest --cov --cov-fail-under=70
    
    - name: Install Node deps
      run: cd web && npm ci
    
    - name: Run frontend tests
      run: cd web && npm test
```

---

## Common Development Tasks

### Add a New API Endpoint

1. **Define route** in `api/routers/`:
   ```python
   # api/routers/conversations.py
   @router.get("/api/conversations/{id}")
   async def get_conversation(id: str):
       # Implementation
   ```

2. **Add to OpenAPI spec**: Update `specs/002-web-ui/contracts/api.yaml`

3. **Update frontend types**: `web/src/types/index.ts`

4. **Create API client method**: `web/src/services/api.ts`

5. **Test**: Write test in `api/tests/` and `web/src/__tests__/`

---

### Add a New UI Component

1. **Create component**: `web/src/components/[category]/ComponentName.tsx`
   ```tsx
   export default function ComponentName({ prop }: ComponentNameProps) {
     return <div>...</div>;
   }
   ```

2. **Add types**: Define `ComponentNameProps` interface

3. **Import in page**: Use in Next.js page or parent component

4. **Style with Tailwind**: Use utility classes

5. **Test**: Write test in `web/src/__tests__/components/`

---

### Add a shadcn/ui Component

```bash
cd web

# Add a component (e.g., dropdown menu)
npx shadcn-ui@latest add dropdown-menu

# Component installed to web/src/components/ui/
```

Now import and use:
```tsx
import { DropdownMenu } from '@/components/ui/dropdown-menu';
```

---

### Database Migrations

SQLite schema is managed by the `chatgpt_archive` package. If schema changes are needed:

1. Update `chatgpt_archive/db.py`
2. Run migration script (if implemented) or manually:
   ```bash
   sqlite3 ~/.chatgpt-archive/chats.db < migration.sql
   ```

---

### Generate API Client from OpenAPI Spec

```bash
# Install openapi-generator-cli
npm install -g @openapitools/openapi-generator-cli

# Generate TypeScript client
openapi-generator-cli generate \
  -i specs/002-web-ui/contracts/api.yaml \
  -g typescript-fetch \
  -o web/src/generated/api

# Use generated client in frontend
```

---

## Environment Variables

### Backend (`api/`)

| Variable | Default | Description |
|----------|---------|-------------|
| `CHATGPT_ARCHIVE_DB` | `~/.chatgpt-archive/chats.db` | SQLite database path |
| `OPENAI_API_KEY` | None | OpenAI API key (for embeddings) |
| `API_HOST` | `0.0.0.0` | API bind host |
| `API_PORT` | `8000` | API port |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed CORS origins |

### Frontend (`web/`)

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API URL |
| `NEXT_PUBLIC_APP_NAME` | `ChatGPT Archive` | App display name |

---

## Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`  
**Fix**: Install dependencies: `pip install -e ".[api]"`

**Error**: `Database not found`  
**Fix**: Import an archive first: `chatgpt-archive import /path/to/export/`

---

### Frontend won't build

**Error**: `Module not found: Can't resolve '@/components/ui/button'`  
**Fix**: Install shadcn component: `npx shadcn-ui@latest add button`

**Error**: `TypeError: Cannot read property 'map' of undefined`  
**Fix**: Add null checks for API responses

---

### Docker containers won't start

**Error**: `port is already allocated`  
**Fix**: Stop conflicting service or change port in `docker-compose.yml`

**Error**: `no space left on device`  
**Fix**: Clean up Docker: `docker system prune -a`

---

### CORS errors in browser

**Error**: `Access to fetch at 'http://localhost:8000' ... has been blocked by CORS`  
**Fix**: Add frontend URL to `CORS_ORIGINS` in backend config:
```python
# api/middleware/cors.py
origins = [
    "http://localhost:3000",
    "http://localhost:3001",  # Add additional origins
]
```

---

## Next Steps

After setup:

1. **Import an archive**: Use CLI or web UI to import your ChatGPT export
2. **Explore features**: Try search, view conversations, export
3. **Generate embeddings** (optional): For semantic search
4. **Customize**: Modify UI components, add features

---

## Development Workflow

### Recommended workflow:

1. **Create feature branch**: `git checkout -b feature/my-feature`
2. **Backend first**: Add API endpoint, test with Swagger UI
3. **Frontend integration**: Create components, connect to API
4. **Test**: Write and run unit/E2E tests
5. **Commit**: `git commit -m "Add feature X"`
6. **Deploy**: `docker-compose build && docker-compose up -d`

---

## Additional Resources

- **Next.js Docs**: https://nextjs.org/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **shadcn/ui**: https://ui.shadcn.com
- **Tailwind CSS**: https://tailwindcss.com/docs
- **React Query**: https://tanstack.com/query/latest
- **Playwright**: https://playwright.dev

---

## Getting Help

- **Issues**: File bug reports at GitHub Issues
- **Docs**: See `/docs` directory for additional documentation
- **API Reference**: http://localhost:8000/docs (when running)
- **Spec**: See `/specs/002-web-ui/` for architecture details

---

**Happy coding!** 🚀
