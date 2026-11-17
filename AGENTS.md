# AGENTS.md — AI-Powered Placement Coach

> **For AI coding agents**: This file is the single source of truth for conventions, architecture, and rules in this codebase. Read it fully before making any changes. All instructions here are mandatory.

---

## 1. Project Overview

AI-Powered Placement Coach is a full-stack web application that helps job seekers prepare for and succeed in the hiring process. It combines a FastAPI backend with a Next.js 14 frontend to deliver AI-driven features — including resume analysis, mock interview coaching, personalised career recommendations, and a conversational placement assistant — all powered by the Google Gemini API.

---

## 2. Architecture Overview

```
c:\AiPlacement\
├── backend\
│   ├── app\
│   │   ├── main.py                  # FastAPI app factory, middleware, router registration
│   │   ├── core\
│   │   │   ├── config.py            # Settings via pydantic-settings (reads .env)
│   │   │   ├── security.py          # JWT creation/validation, password hashing
│   │   │   └── dependencies.py      # Reusable FastAPI Depends (get_db, get_current_user)
│   │   ├── routers\
│   │   │   ├── auth.py
│   │   │   ├── profile.py
│   │   │   ├── assessments.py
│   │   │   ├── recommendations.py
│   │   │   ├── chat.py
│   │   │   ├── resume.py
│   │   │   ├── interview.py
│   │   │   └── dashboard.py
│   │   ├── services\
│   │   │   ├── prompts.py           # ALL Gemini prompt templates live here
│   │   │   ├── ai_service.py        # Gemini API wrapper
│   │   │   ├── auth_service.py
│   │   │   ├── resume_service.py
│   │   │   ├── interview_service.py
│   │   │   └── recommendation_service.py
│   │   ├── models\                  # SQLAlchemy ORM models (one file per domain)
│   │   ├── schemas\                 # Pydantic v2 request/response schemas
│   │   └── db\
│   │       ├── session.py           # Async engine + AsyncSessionLocal
│   │       └── base.py              # DeclarativeBase
│   ├── alembic\                     # Database migrations
│   ├── tests\                       # pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend\
│   ├── app\                         # Next.js App Router pages and layouts
│   ├── components\                  # Shared UI components (shadcn/ui wrappers + composites)
│   ├── lib\
│   │   ├── api.ts                   # Axios/fetch client — the only place base URL is configured
│   │   └── utils.ts                 # General utility functions
│   ├── hooks\                       # All TanStack Query hooks (useProfile, useRecommendations, …)
│   ├── types\                       # TypeScript interfaces and type aliases
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── docs\
```

### Request Flow

```
Browser → Next.js App Router → TanStack Query hook (hooks/)
       → lib/api.ts (HTTP) → FastAPI router (routers/)
       → Service layer (services/) → SQLAlchemy model / Gemini API
       → PostgreSQL / Google Gemini
```

---

## 3. Coding Conventions

### 3.1 Python (backend)

- **Python version**: 3.11+. Use `match` statements, `tomllib`, and 3.11+ typing features freely.
- **Async everywhere**: every function that touches the database or an external API **must** be `async def`. Never use synchronous SQLAlchemy calls (`Session`, `execute` without `await`).
- **Type hints**: required on every function signature — parameters and return type. Use `from __future__ import annotations` in all files.
- **Pydantic v2**: use `model_validate()` (not `parse_obj()`), `model_dump()` (not `dict()`), and `model_dump(mode="json")` when serialising for JSON responses.
- **Naming**: `snake_case` for variables, functions, modules, and DB columns. `PascalCase` for classes.
- **Docstrings**: every public function and class must have a Google-style docstring explaining what it does, its args, and its return value.
- **Imports**: use absolute imports from `app.*`. Never use relative imports that cross package boundaries.
- **Exception handling**: raise `HTTPException` only in routers. Services raise domain-specific Python exceptions; routers catch and convert them.

```python
# ✅ Correct
async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Fetch a user record by email address.

    Args:
        db: Active async database session.
        email: The email to look up.

    Returns:
        The User ORM instance, or None if not found.
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

# ❌ Wrong — sync, no type hints, no docstring
def get_user(db, email):
    return db.query(User).filter(User.email == email).first()
```

### 3.2 TypeScript (frontend)

- **Strict mode**: `"strict": true` in `tsconfig.json`. Never disable or suppress strict checks.
- **No `any`**: use `unknown` and narrow with type guards, or define a proper interface. `any` is banned.
- **Functional components only**: no class components. All components are arrow functions.
- **Named exports**: export components and hooks by name. Default exports are only used for Next.js page files (required by the framework).
- **Naming**: `camelCase` for variables, functions, and hooks; `PascalCase` for React components and TypeScript interfaces/types.
- **File naming**: component files use `PascalCase.tsx`; hook files use `camelCase.ts`; utility files use `camelCase.ts`.
- **No inline styles**: use Tailwind utility classes. Never use the `style` prop unless absolutely unavoidable (e.g., dynamic canvas dimensions).

```tsx
// ✅ Correct
export function ResumeCard({ resume }: ResumeCardProps) {
  return <Card className="rounded-2xl shadow-md p-4">{resume.title}</Card>;
}

// ❌ Wrong — default export, any type, class component
export default class ResumeCard extends React.Component<any> { … }
```

---

## 4. Backend Conventions

### 4.1 Router → Service → Model Pattern

Responsibility must stay in its layer:

| Layer | Responsibility | Must NOT |
|---|---|---|
| **Router** (`routers/`) | Parse request, call service, return response, raise `HTTPException` | Contain business logic or DB queries |
| **Service** (`services/`) | Business logic, AI calls, orchestration | Import from `routers/` or raise `HTTPException` |
| **Model** (`models/`) | ORM schema definition, relationships | Contain any logic beyond simple properties |
| **Schema** (`schemas/`) | Request/response validation | Reference ORM models directly |

### 4.2 Database Sessions

All database access uses an injected `AsyncSession` from `app.core.dependencies.get_db`:

```python
# routers/profile.py
from app.core.dependencies import get_db, get_current_user
from app.services.profile_service import update_profile

@router.patch("/me", response_model=ProfileResponse)
async def update_my_profile(
    payload: ProfileUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProfileResponse:
    updated = await update_profile(db, current_user.id, payload)
    return ProfileResponse.model_validate(updated)
```

- Never instantiate `AsyncSession` directly inside a service or router.
- Always `await db.commit()` and `await db.refresh(instance)` after writes.
- Use `await db.rollback()` in exception handlers when the session may be dirty.

### 4.3 Authentication & Token Lifecycle

- **Access tokens**: Short-lived JWT (15-minute expiry), signed with `SECRET_KEY` using `ALGORITHM` (HS256). Payload includes `sub` (user UUID) and `role`. Stored in client memory/TanStack Query cache (never localStorage). Transmitted via `Authorization: Bearer <token>`.
- **Refresh tokens**: Cryptographically secure random token (64-byte urlsafe string), hashed using SHA-256 before storage in the `refresh_tokens` table. 7-day expiry.
- **Cookie settings**: Refresh token is returned in an `HttpOnly` cookie:
  - `HttpOnly: True` (prevents JavaScript/XSS access)
  - `Secure: True` in production (set `SECURE_COOKIES=False` only during local HTTP development)
  - `SameSite: Strict` (CSRF defense)
  - `Path: /api/v1/auth/refresh` (cookie only sent to the refresh endpoint)
  - `Max-Age: 604800` (7 days)
- **Token rotation**: Every call to `/auth/refresh` revokes the old refresh token (`revoked = True`) and issues a new refresh token and new access token. If a revoked token is reused, all tokens in that family are revoked immediately.
- **Logout**: `POST /auth/logout` sets `revoked = True` for the current refresh token in the database and clears the refresh cookie (`Max-Age=0`).
- **Password hashing**: bcrypt with a minimum work factor of 12. Never store plain text passwords.
- **Protection**: The `get_current_user` dependency in `core/dependencies.py` validates the access token and returns the `User` ORM object. Use it on every protected endpoint. Never check `Authorization` headers manually.

### 4.4 File Upload & Resume Storage Security

- **Storage location**: Local filesystem under `UPLOAD_DIR` (`backend/uploads/`) for development.
- **Randomized filenames**: Never save uploaded files under their original names. Use a UUIDv4 filename (e.g., `<uuid4>.pdf`). Store the original filename only in the database `resumes.original_filename` column.
- **Validation**:
  - **Size limit**: Enforce max 5 MB (`MAX_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024`). Reject with HTTP 413 if exceeded.
  - **MIME type check**: Verify `Content-Type` header is either `application/pdf` or `application/vnd.openxmlformats-officedocument.wordprocessingml.document`.
  - **Magic byte verification**: Verify file signature bytes (PDF: `b"%PDF-"`, DOCX: `b"PK\x03\x04"`). Reject with HTTP 415 if bytes do not match expected signature.
- **Path traversal prevention**: Always resolve destination paths using `os.path.abspath` and verify `os.path.commonpath([target, UPLOAD_DIR]) == UPLOAD_DIR`. Disallow `..`, relative components, or leading slashes in filenames.
- **Authenticated access**: Uploaded files must **never** be served via static file mounts. Serve files strictly through `GET /api/v1/resume/{resume_id}/file` after verifying authentication and student ownership.
- **Cloud migration**: Keep storage operations behind a `BaseStorageService` interface so swapping to free cloud object storage (e.g. Cloudflare R2 free tier with zero egress fees, or Supabase Storage free tier) requires zero changes to routers or business logic.

---

## 5. Frontend Conventions

### 5.1 Data Fetching — TanStack Query

- All server state lives in TanStack Query. **No `fetch()` or `axios` calls inside components.**
- Every API interaction has a dedicated hook in `hooks/`. Name hooks `use<Resource><Action>` (e.g., `useResumeUpload`, `useRecommendations`).
- Mutations use `useMutation`; reads use `useQuery` or `useInfiniteQuery`.

```tsx
// hooks/useRecommendations.ts  ✅
export function useRecommendations() {
  return useQuery({
    queryKey: ["recommendations"],
    queryFn: () => api.get<Recommendation[]>("/recommendations"),
  });
}

// components/RecommendationsPage.tsx  ✅
const { data, isLoading } = useRecommendations();

// components/RecommendationsPage.tsx  ❌ — direct fetch in component
const data = await fetch("/api/recommendations");
```

### 5.2 API Client

All HTTP calls go through `lib/api.ts`. This file is the only place where the base URL (`NEXT_PUBLIC_API_URL`) and auth token injection (via an Axios interceptor or equivalent) are configured.

### 5.3 UI Components

- Use **shadcn/ui** components for all standard UI elements: buttons, inputs, dialogs, cards, tables, tabs, selects, toasts, etc.
- Do **not** build raw Tailwind-only replacements for anything shadcn covers.
- Composite or domain-specific components (e.g., `ResumeCard`, `InterviewTimer`) live in `components/` and are built by composing shadcn primitives.
- Icons come from **lucide-react** only. Do not add other icon libraries.

---

## 6. AI Integration Rules

### 6.1 Prompt Management

**All AI prompt templates must live in `backend/app/services/prompts.py`.** No prompt string may appear anywhere else in the codebase.

```python
# backend/app/services/prompts.py  ✅
RESUME_ANALYSIS_PROMPT = """
You are an expert career coach. Analyse the following resume and return a JSON object with:
- strengths: list[str]
- weaknesses: list[str]
- suggestions: list[str]
- ats_score: int (0–100)

Resume:
{resume_text}
"""

# backend/app/services/resume_service.py  ✅
from app.services.prompts import RESUME_ANALYSIS_PROMPT

prompt = RESUME_ANALYSIS_PROMPT.format(resume_text=text)

# backend/app/services/resume_service.py  ❌ — inline prompt
prompt = f"Analyse this resume: {text}"
```

### 6.2 Modular AI Provider & Free-Tier Rules

**Strict Rule: Never assume a paid AI plan. Free APIs or local open-source models only.**

1. **Configurable Model Names**: Never hardcode specific model names (like `"gemini-1.5-pro"` or `"gemini-1.5-flash"`). Always read model identifiers from application configuration (`settings.AI_MODEL_CHAT`, `settings.AI_MODEL_ANALYSIS`).
2. **Provider-Agnostic Interface**: AI operations are wrapped in `backend/app/services/ai_service.py` behind a common abstract client or protocol (`BaseAIProvider`). This allows swapping providers (Google Gemini Free Tier, Groq Free Tier, or local Ollama) by changing `AI_PROVIDER` in `.env` without modifying any business logic.
3. **Free Tier Quotas & Rate Limits**:
   - Google AI Studio Free Tier provides ~15 RPM and 1,500 RPD for fast/flash models without billing.
   - The wrapper must gracefully catch HTTP 429 (`RESOURCE_EXHAUSTED` / rate limits), log a warning, implement exponential backoff retry (up to 3 attempts), and raise a user-friendly `AIServiceRateLimitError` that the router converts to HTTP 429 with `Retry-After`.
4. **Local / Open-Source Alternative**:
   - If no external API key is available or rate limits are exceeded, the system can point to a local Ollama instance (`AI_PROVIDER=ollama`, `OLLAMA_BASE_URL=http://localhost:11434`, `AI_MODEL_CHAT=llama3.2`) with zero external network requests and $0 cost.

```python
# backend/app/services/ai_service.py
import logging
from abc import ABC, abstractmethod
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIServiceError(Exception):
    """Domain exception for AI provider failures."""

class AIServiceRateLimitError(AIServiceError):
    """Raised when free-tier rate limits (HTTP 429) are reached."""

class BaseAIProvider(ABC):
    @abstractmethod
    async def generate_text(self, prompt: str, model: str | None = None) -> str:
        """Generate text response from the configured model."""

    @abstractmethod
    async def generate_structured(self, prompt: str, schema_desc: str, model: str | None = None) -> str:
        """Generate JSON structured response."""
```

---

## 7. Environment Variables

Define all variables in a `.env` file at the project root (never commit it). The backend reads them via `app/core/config.py` using `pydantic-settings`. The frontend reads `NEXT_PUBLIC_*` variables at build time via Next.js.

### Backend (read by `app/core/config.py`)

| Variable | Description | Default / Example |
|---|---|---|
| `DATABASE_URL` | Async PostgreSQL DSN | `postgresql+asyncpg://postgres:postgres@db:5432/placement` |
| `SECRET_KEY` | JWT signing secret (min 32 chars, random) | `openssl rand -hex 32` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` |
| `SECURE_COOKIES` | Set False for local HTTP dev, True in prod | `False` |
| `AI_PROVIDER` | Active AI provider (`gemini`, `groq`, `ollama`) | `gemini` |
| `GEMINI_API_KEY` | Google AI Studio free API key | `AIza…` (optional if using Ollama) |
| `AI_MODEL_CHAT` | Model for chatbot & interactive features | `gemini-1.5-flash` |
| `AI_MODEL_ANALYSIS` | Model for resume & interview evaluations | `gemini-1.5-flash` |
| `OLLAMA_BASE_URL` | Base URL for local Ollama fallback | `http://localhost:11434` |
| `UPLOAD_DIR` | Absolute path for uploaded files | `/app/uploads` |
| `MAX_UPLOAD_SIZE_MB` | Maximum allowed file upload size | `5` |
| `BACKEND_CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:3000` |
| `LOG_LEVEL` | Python logging level | `INFO` |

### Frontend (read by Next.js)

| Variable | Description | Example |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000/api/v1` |

> [!CAUTION]
> Never put `GEMINI_API_KEY`, `SECRET_KEY`, `DATABASE_URL`, or any credential into source code, a Dockerfile `ENV` instruction, or a committed `.env` file. All core services operate under free-tier limits ($0 cost).

---

## 8. Testing Rules

### 8.1 Backend — pytest

- **Every new endpoint requires at least one pytest test** covering the happy path. Add negative-path tests for auth failures and invalid input.
- Test files mirror the source layout: `tests/routers/test_auth.py`, `tests/services/test_resume_service.py`, etc.
- Use `httpx.AsyncClient` with `app` mounted directly (no live server):

- **Every new endpoint requires at least one pytest test** covering the happy path. Add negative-path tests for auth failures and invalid input.
- Test files mirror the source layout: `tests/routers/test_auth.py`, `tests/services/test_resume_service.py`, etc.
- Use `httpx.AsyncClient` with `app` mounted directly (no live server):

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
```

- **Mock all Gemini API calls** using a `pytest` fixture — never hit the real API in tests:

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture(autouse=True)
def mock_gemini():
    with patch("app.services.ai_service.genai.GenerativeModel") as mock_model:
        instance = mock_model.return_value
        instance.generate_content_async = AsyncMock(
            return_value=type("Response", (), {
                "text": '{"strengths": [], "weaknesses": [], "suggestions": [], "ats_score": 75}',
                "usage_metadata": type("Meta", (), {
                    "prompt_token_count": 100,
                    "candidates_token_count": 50,
                })(),
            })()
        )
        yield instance
```

- Use a separate test database (set `DATABASE_URL` in `pytest.ini` or `conftest.py` to a dedicated test DB).
- Never mock the database — use real async DB calls against the test database.

### 8.2 Frontend — Jest + React Testing Library

- Test files live alongside the code they test: `components/ResumeCard.test.tsx`.
- Mock all TanStack Query hooks in component tests using `jest.mock("../hooks/useResumeUpload")`.
- Do not test implementation details (internal state, private functions). Test rendered output and user interactions.

### 8.3 E2E — Playwright

- E2E tests live in `frontend/tests/e2e/`.
- Run against a locally composed stack (all services up via `docker compose`).
- Never hit production or staging environments from automated tests.

---

## 9. Git Conventions

### Branch Naming

```
feature/<short-description>    # New features
fix/<short-description>        # Bug fixes
docs/<short-description>       # Documentation only
chore/<short-description>      # Build, CI, dependency updates
refactor/<short-description>   # Code changes with no behaviour change
test/<short-description>       # Adding or fixing tests
```

### Commit Messages — Conventional Commits

```
<type>(<scope>): <short imperative summary>

[optional body]

[optional footer: BREAKING CHANGE or issue refs]
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`  
**Scopes** (use one): `auth`, `profile`, `resume`, `interview`, `recommendations`, `chat`, `dashboard`, `ai`, `db`, `infra`, `frontend`

```
# ✅ Good
feat(resume): add ATS score calculation via Gemini
fix(auth): refresh token not invalidated on logout
docs(agents): update environment variable table

# ❌ Bad
updated stuff
WIP
fixed bug
```

---

## 10. Do-Not Rules

These are hard rules. Violations will be rejected in code review.

| # | Rule |
|---|---|
| 1 | **Do not store secrets in code.** No API keys, passwords, or tokens in any `.py`, `.ts`, `.tsx`, `.json`, or Dockerfile committed to the repository. |
| 2 | **Do not use synchronous SQLAlchemy.** `Session`, `db.query()`, and any blocking ORM call are banned. Use `AsyncSession` and `await` exclusively. |
| 3 | **Do not bypass auth middleware.** Every protected route must use `Depends(get_current_user)`. Do not re-implement token validation inside a router or service. |
| 4 | **Do not put prompts inline.** All Gemini prompt strings belong in `backend/app/services/prompts.py`. No exceptions. |
| 5 | **Do not call external APIs in tests.** Mock the Gemini client and any other third-party service. Tests must be runnable offline. |
| 6 | **Do not use `any` in TypeScript.** Use proper types, generics, or `unknown` with type guards. |
| 7 | **Do not put business logic in routers.** Routers parse input and delegate to services. |
| 8 | **Do not call `fetch()` directly in React components.** All data fetching goes through TanStack Query hooks defined in `hooks/`. |
| 9 | **Do not commit `.env` files.** Add `.env` to `.gitignore` immediately if not already there. |
| 10 | **Do not skip migrations.** Never alter the database schema by hand or via raw SQL scripts outside of Alembic. |
