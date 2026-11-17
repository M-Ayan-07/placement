# Testing & Acceptance — AI-Powered Placement Coach

## Table of Contents

1. [Testing Strategy](#1-testing-strategy)
2. [Backend Test Plan (pytest)](#2-backend-test-plan-pytest)
3. [Frontend Test Plan (Jest + RTL)](#3-frontend-test-plan-jest--rtl)
4. [E2E Test Plan (Playwright)](#4-e2e-test-plan-playwright)
5. [Acceptance Criteria](#5-acceptance-criteria)
6. [CI/CD Testing Gates](#6-cicd-testing-gates)

---

## 1. Testing Strategy

### 1.1 Test Levels

| Level | Tooling | Scope | Owned By |
|---|---|---|---|
| Unit | pytest / Jest + RTL | Single function, component, or hook in isolation | Developer |
| Integration | pytest + httpx (async) | API endpoints, DB interactions, service composition | Developer |
| E2E | Playwright | Full user journeys through the browser | QA / Developer |

### 1.2 Coverage Targets

| Layer | Metric | Target |
|---|---|---|
| Backend (Python) | Line coverage | ≥ 80% |
| Backend (Python) | Branch coverage | ≥ 70% |
| Frontend (JS/TS) | Statement coverage | ≥ 75% |
| Frontend (JS/TS) | Branch coverage | ≥ 65% |
| E2E | Critical happy paths | 100% (all 7 features) |

Coverage is enforced by `pytest-cov` on the backend and `jest --coverage` on the frontend. Builds that fall below these thresholds **fail the CI gate**.

### 1.3 AI Feature Testing Approach

All AI operations are routed through a provider-agnostic internal service layer (`AIService` / `BaseAIProvider`). This boundary is mocked at every level of the test suite so tests execute completely offline with **zero external API calls and $0 cost**.

**Unit / integration tests:**

```python
# conftest.py — shared fixture
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_ai_service():
    """Replace AIService calls with deterministic offline stubs."""
    with patch(
        "app.services.ai_service.AIService.generate_text",
        new_callable=AsyncMock,
    ) as m_text, patch(
        "app.services.ai_service.AIService.generate_structured",
        new_callable=AsyncMock,
    ) as m_struct:
        m_text.return_value = "Mocked AI response text"
        m_struct.return_value = '{"overall_score": 85, "strengths": ["Clean structure"], "weaknesses": [], "suggestions": []}'
        yield {"text": m_text, "structured": m_struct}
```

- Fixtures parameterise the stub to return domain-specific payloads (recommendation lists, resume analysis JSONs, chatbot turns, interview feedback).
- Error paths (HTTP 429 rate limit, safety blocks, network timeouts) are tested by configuring the mock to raise `AIServiceRateLimitError` and `asyncio.TimeoutError`.
- Backoff and retry logic is verified to ensure smooth recovery under free-tier quota spikes.

### 1.4 Test Database Strategy

- A dedicated PostgreSQL database named `placement_test` is used for all backend tests. It is never shared with development or staging data.
- The connection string is read from the environment variable `TEST_DATABASE_URL`.
- Alembic migrations are applied once at the start of each test session via a session-scoped fixture.
- Each test that writes data runs inside a transaction that is **rolled back** after the test, ensuring zero state leakage:

```python
# conftest.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.db.base import Base

TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]
engine = create_async_engine(TEST_DATABASE_URL, echo=False)

@pytest.fixture(scope="session", autouse=True)
async def apply_migrations():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session():
    async with engine.connect() as conn:
        async with conn.begin() as tx:
            session = AsyncSession(bind=conn)
            yield session
            await tx.rollback()
            await session.close()
```

- Seed fixtures (`factories/`) use `factory_boy` to generate realistic, relational test data without hard-coded IDs.
- File-based assets (PDF uploads) use a temporary local directory; the `STORAGE_BACKEND` env var is set to `local` in test mode.

---

## 2. Backend Test Plan (pytest)

Directory structure:

```
backend/
└── tests/
    ├── conftest.py
    ├── factories/
    │   ├── user_factory.py
    │   ├── assessment_factory.py
    │   └── resume_factory.py
    ├── unit/
    │   ├── test_scoring.py
    │   ├── test_readiness.py
    │   └── test_resume_parser.py
    ├── integration/
    │   ├── test_auth.py
    │   ├── test_profile.py
    │   ├── test_assessment.py
    │   ├── test_recommendations.py
    │   ├── test_chatbot.py
    │   ├── test_resume.py
    │   ├── test_interview.py
    │   └── test_dashboard.py
    └── contract/
        └── test_gemini_schema.py
```

All integration tests use `httpx.AsyncClient` against the FastAPI `app` instance:

```python
@pytest.fixture
async def client(db_session):
    from app.main import app
    from app.deps import get_db
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

---

### 2.1 Authentication

File: `tests/integration/test_auth.py`

| # | Test Name | Method + Path | Preconditions | Expected Outcome |
|---|---|---|---|---|
| A-01 | `test_register_success` | `POST /api/v1/auth/register` | Email not in DB | `201`, user row created, `access_token` + `refresh_token` returned |
| A-02 | `test_register_duplicate_email` | `POST /api/v1/auth/register` | Email already exists | `409 CONFLICT`, body `{"detail": "email_already_registered"}` |
| A-03 | `test_register_invalid_email_format` | `POST /api/v1/auth/register` | Malformed email string | `422 UNPROCESSABLE_ENTITY` |
| A-04 | `test_register_weak_password` | `POST /api/v1/auth/register` | Password < 8 chars | `422 UNPROCESSABLE_ENTITY` |
| A-05 | `test_login_success` | `POST /api/v1/auth/login` | Valid credentials | `200`, `access_token` (JWT, exp 15 min), `refresh_token` (exp 7 days) |
| A-06 | `test_login_wrong_password` | `POST /api/v1/auth/login` | Wrong password | `401 UNAUTHORIZED`, body `{"detail": "invalid_credentials"}` |
| A-07 | `test_login_unknown_email` | `POST /api/v1/auth/login` | Email not in DB | `401 UNAUTHORIZED` (same message — no user enumeration) |
| A-08 | `test_token_refresh_valid` | `POST /api/v1/auth/refresh` | Valid, non-expired refresh token | `200`, new `access_token` issued |
| A-09 | `test_token_refresh_expired` | `POST /api/v1/auth/refresh` | Refresh token past expiry | `401`, body `{"detail": "token_expired"}` |
| A-10 | `test_token_refresh_revoked` | `POST /api/v1/auth/refresh` | Token in revocation list (Redis) | `401`, body `{"detail": "token_revoked"}` |
| A-11 | `test_logout` | `POST /api/v1/auth/logout` | Authenticated request with refresh token | `204`, refresh token added to revocation store, subsequent refresh returns `401` |

---

### 2.2 Student Profiles

File: `tests/integration/test_profile.py`

| # | Test Name | Method + Path | Preconditions | Expected Outcome |
|---|---|---|---|---|
| P-01 | `test_get_own_profile` | `GET /api/v1/profile/me` | Authenticated user with profile row | `200`, returns own profile fields (name, college, branch, graduation_year) |
| P-02 | `test_get_profile_unauthenticated` | `GET /api/v1/profile/me` | No `Authorization` header | `401` |
| P-03 | `test_update_profile_success` | `PATCH /api/v1/profile/me` | Authenticated, valid payload | `200`, DB row updated, response reflects new values |
| P-04 | `test_update_profile_invalid_year` | `PATCH /api/v1/profile/me` | `graduation_year` in the past | `422` |
| P-05 | `test_get_goals` | `GET /api/v1/profile/me/goals` | User has placement goals set | `200`, list of goal objects with `role`, `companies`, `target_date` |
| P-06 | `test_update_goals_success` | `PUT /api/v1/profile/me/goals` | Authenticated, valid goals payload | `200`, goals row upserted |
| P-07 | `test_update_goals_empty_companies` | `PUT /api/v1/profile/me/goals` | `companies` array is empty | `422` |

---

### 2.3 Assessments

File: `tests/integration/test_assessment.py`

| # | Test Name | Method + Path | Preconditions | Expected Outcome |
|---|---|---|---|---|
| AS-01 | `test_start_session_success` | `POST /api/v1/assessments/sessions` | Authenticated, payload `{type: "aptitude", difficulty: "medium"}` | `201`, session row with `status=in_progress`, `expires_at` = now + 30 min, questions array |
| AS-02 | `test_start_session_invalid_type` | `POST /api/v1/assessments/sessions` | `type` = `"unknown"` | `422` |
| AS-03 | `test_submit_answers_success` | `POST /api/v1/assessments/sessions/{id}/submit` | Active session, all answers provided | `200`, session `status=completed`, `score` field populated |
| AS-04 | `test_submit_answers_partial` | `POST /api/v1/assessments/sessions/{id}/submit` | Subset of questions answered | `200`, unanswered questions scored 0 |
| AS-05 | `test_score_calculation_correct` | Unit — `scoring.calculate_score()` | 10 questions, 7 correct (equal weights) | Returns `{"raw": 7, "percentage": 70.0, "percentile": None}` |
| AS-06 | `test_score_calculation_weighted` | Unit — `scoring.calculate_score()` | Questions with custom `weight` fields | Weighted sum correct to 2 d.p. |
| AS-07 | `test_submit_expired_session` | `POST /api/v1/assessments/sessions/{id}/submit` | Session `expires_at` < now | `409`, body `{"detail": "session_expired"}`, session marked `status=timed_out` |
| AS-08 | `test_cannot_resubmit_completed` | `POST /api/v1/assessments/sessions/{id}/submit` | Session `status=completed` | `409`, body `{"detail": "session_already_completed"}` |

---

### 2.4 Personalised Recommendations

File: `tests/integration/test_recommendations.py`

| # | Test Name | Method + Path | Preconditions | Expected Outcome |
|---|---|---|---|---|
| R-01 | `test_generate_triggers_ai` | `GET /api/v1/recommendations` | Authenticated, `mock_gemini` fixture | `200`, `mock_gemini.assert_called_once()`, response contains `resources` array with ≥ 1 item |
| R-02 | `test_generate_structured_response` | `GET /api/v1/recommendations` | Mock returns seeded JSON fixture | Each item has `title`, `type`, `url`, `priority` (1–5) |
| R-03 | `test_generate_cached` | `GET /api/v1/recommendations` (called twice) | Same user, no profile change between calls | Second call does **not** invoke Gemini (cache hit in Redis) |
| R-04 | `test_cache_invalidated_on_goal_update` | Goal update then `GET /api/v1/recommendations` | Cache previously populated | Gemini invoked again after goal change |
| R-05 | `test_generate_gemini_unavailable` | `GET /api/v1/recommendations` | Mock raises `GeminiRateLimitError` | `503`, body `{"detail": "ai_service_unavailable"}` |

---

### 2.5 AI Chatbot

File: `tests/integration/test_chatbot.py`

| # | Test Name | Method + Path | Preconditions | Expected Outcome |
|---|---|---|---|---|
| C-01 | `test_create_session` | `POST /api/v1/chatbot/sessions` | Authenticated | `201`, session row with `id`, `created_at`, `message_count=0` |
| C-02 | `test_send_message_success` | `POST /api/v1/chatbot/sessions/{id}/messages` | Active session, `mock_gemini` | `201`, message row persisted with `role=assistant`, response text non-empty |
| C-03 | `test_send_message_builds_history` | Send 3 messages | Seeded session | Gemini is called with a `messages` array of length 3 (user, assistant, user) |
| C-04 | `test_history_retrieval` | `GET /api/v1/chatbot/sessions/{id}/messages` | Session with 5 messages | `200`, array length 5, ordered by `created_at` ascending |
| C-05 | `test_history_pagination` | `GET /api/v1/chatbot/sessions/{id}/messages?limit=3&offset=0` | 5-message session | Returns exactly 3 items, `X-Total-Count: 5` header |
| C-06 | `test_send_message_to_foreign_session` | `POST /api/v1/chatbot/sessions/{other_user_id}/messages` | Authenticated as different user | `403` |

---

### 2.6 Resume Scanner

File: `tests/integration/test_resume.py`

| # | Test Name | Method + Path | Preconditions | Expected Outcome |
|---|---|---|---|---|
| RS-01 | `test_upload_valid_pdf` | `POST /api/v1/resume/upload` | Multipart PDF ≤ 5 MB | `202`, resume row with `status=queued`, `resume_id` returned |
| RS-02 | `test_upload_invalid_type` | `POST /api/v1/resume/upload` | `.docx` file | `415 UNSUPPORTED_MEDIA_TYPE` |
| RS-03 | `test_upload_oversized_file` | `POST /api/v1/resume/upload` | PDF > 5 MB | `413 REQUEST_ENTITY_TOO_LARGE` |
| RS-04 | `test_processing_status_queued_to_processing` | Worker picks up task | Status was `queued` | Status transitions to `processing` |
| RS-05 | `test_processing_status_processing_to_complete` | Worker finishes | Status was `processing` | Status transitions to `complete`, `analysis` field populated |
| RS-06 | `test_processing_status_on_ai_failure` | Mock raises exception mid-task | Status was `processing` | Status transitions to `failed`, `error_message` populated |
| RS-07 | `test_analysis_retrieval` | `GET /api/v1/resume/{id}/analysis` | Status = `complete` | `200`, structured JSON with `score`, `strengths`, `gaps`, `suggestions` arrays |
| RS-08 | `test_analysis_not_ready` | `GET /api/v1/resume/{id}/analysis` | Status = `processing` | `202`, body `{"detail": "analysis_pending"}` |

---

### 2.7 Interview Practice

File: `tests/integration/test_interview.py`

| # | Test Name | Method + Path | Preconditions | Expected Outcome |
|---|---|---|---|---|
| I-01 | `test_start_session_technical` | `POST /api/v1/interview/sessions` | Payload `{mode: "technical", role: "SDE-1"}` | `201`, session row, first question returned |
| I-02 | `test_start_session_hr` | `POST /api/v1/interview/sessions` | Payload `{mode: "hr"}` | `201`, HR question set loaded |
| I-03 | `test_answer_turn` | `POST /api/v1/interview/sessions/{id}/turns` | Active session, `mock_gemini`, user answer text | `201`, AI feedback stored in turn row, `next_question` in response |
| I-04 | `test_answer_evaluated_by_ai` | Same as I-03 | Mock configured with feedback payload | `feedback.score` is integer 1–10, `feedback.explanation` non-empty string |
| I-05 | `test_end_session` | `POST /api/v1/interview/sessions/{id}/end` | Active session with ≥ 1 turn | `200`, session `status=complete` |
| I-06 | `test_report_generation` | `GET /api/v1/interview/sessions/{id}/report` | Status = `complete`, `mock_gemini` | `200`, report contains `overall_score`, `strengths`, `improvement_areas`, `per_question_breakdown` |
| I-07 | `test_report_not_available_for_active_session` | `GET /api/v1/interview/sessions/{id}/report` | Status = `in_progress` | `409`, body `{"detail": "session_not_complete"}` |

---

### 2.8 Progress Dashboard

File: `tests/integration/test_dashboard.py`

| # | Test Name | Method + Path | Preconditions | Expected Outcome |
|---|---|---|---|---|
| D-01 | `test_summary_data_aggregation` | `GET /api/v1/dashboard/summary` | User with 3 assessments, 2 interview sessions, 1 resume | `200`, `assessment_count=3`, `interview_count=2`, `resume_uploaded=true` |
| D-02 | `test_readiness_score_no_activity` | `GET /api/v1/dashboard/readiness` | New user, no assessments | `200`, `readiness_score=0`, `level="not_started"` |
| D-03 | `test_readiness_score_calculation` | Unit — `readiness.compute()` | Seeded: aptitude 70%, technical 80%, 1 mock interview score 7/10 | Score = weighted average per spec, `level="on_track"` |
| D-04 | `test_readiness_score_updates_after_assessment` | Complete new assessment | Previous score cached | Score recalculated, new score ≠ old score |
| D-05 | `test_activity_timeline` | `GET /api/v1/dashboard/activity?days=30` | Mixed activity across features | `200`, array of activity events ordered by `timestamp` desc, each with `type` and `metadata` |

---

## 3. Frontend Test Plan (Jest + RTL)

Configuration:

```json
// jest.config.ts
{
  "testEnvironment": "jsdom",
  "setupFilesAfterFramework": ["@testing-library/jest-dom"],
  "moduleNameMapper": {
    "^@/(.*)$": "<rootDir>/src/$1"
  },
  "coverageThreshold": {
    "global": { "statements": 75, "branches": 65 }
  }
}
```

---

### 3.1 Component Tests

#### `AuthForm` (`src/components/auth/AuthForm.tsx`)

```typescript
// tests/components/AuthForm.test.tsx
describe("AuthForm", () => {
  it("renders email and password fields");
  it("shows validation error when email is malformed on submit");
  it("shows validation error when password is fewer than 8 characters");
  it("calls onSubmit with trimmed credentials when form is valid");
  it("disables the submit button and shows spinner while isLoading=true");
  it("renders the toggle link to switch between login and register modes");
  it("displays server error message when error prop is non-null");
});
```

#### `AssessmentTimer` (`src/components/assessment/AssessmentTimer.tsx`)

```typescript
describe("AssessmentTimer", () => {
  beforeEach(() => jest.useFakeTimers());
  afterEach(() => jest.useRealTimers());

  it("displays MM:SS formatted from expiresAt prop");
  it("ticks down by 1 second on each interval");
  it("applies urgent CSS class when remaining time < 60 seconds");
  it("calls onExpire callback exactly once when countdown reaches 0");
  it("stops ticking after onExpire is called");
});
```

#### `ChatWindow` (`src/components/chatbot/ChatWindow.tsx`)

```typescript
describe("ChatWindow", () => {
  it("renders a message bubble for each item in messages prop");
  it("aligns user messages right and assistant messages left");
  it("scrolls to bottom automatically when a new message is appended");
  it("renders a typing indicator when isStreaming=true");
  it("disables the send button when input is empty or isStreaming=true");
  it("calls onSendMessage with input text and clears the input on submit");
  it("renders markdown in assistant messages (bold, code blocks)");
});
```

#### `ResumeUpload` (`src/components/resume/ResumeUpload.tsx`)

```typescript
describe("ResumeUpload", () => {
  it("accepts PDF files via drag-and-drop");
  it("rejects non-PDF files and shows an error message");
  it("rejects files larger than 5 MB and shows an error message");
  it("calls onUpload with the selected File object");
  it("shows upload progress bar when uploadProgress prop is between 1 and 99");
  it("shows success state when uploadProgress is 100");
});
```

#### `ProgressChart` (`src/components/dashboard/ProgressChart.tsx`)

```typescript
describe("ProgressChart", () => {
  it("renders without crashing when dataPoints prop is empty");
  it("renders one SVG path element per data series");
  it("displays the correct readiness score label from readinessScore prop");
  it("shows a legend entry for each named series");
});
```

---

### 3.2 Hook Tests

#### `useAuth` (`src/hooks/useAuth.ts`)

```typescript
describe("useAuth", () => {
  it("returns isAuthenticated=false and user=null on initial load with no token");
  it("decodes stored JWT and populates user on initial load");
  it("calls POST /api/v1/auth/login and stores tokens on login()");
  it("removes tokens and resets state on logout()");
  it("proactively refreshes the access token 60 seconds before expiry");
  it("sets isAuthenticated=false when refresh returns 401");
});
```

#### `useAssessment` (`src/hooks/useAssessment.ts`)

```typescript
describe("useAssessment", () => {
  it("fetches and returns questions on mount given a valid sessionId");
  it("tracks the current question index correctly after next()");
  it("records answers keyed by question id via recordAnswer()");
  it("calls POST .../submit with all recorded answers on submit()");
  it("sets isExpired=true and does not allow further answers after expiry");
});
```

#### `useChat` (`src/hooks/useChat.ts`)

```typescript
describe("useChat", () => {
  it("loads existing message history for a sessionId on mount");
  it("appends optimistic user message immediately on sendMessage()");
  it("appends assistant response after API resolves");
  it("removes optimistic message and sets error on API failure");
  it("sets isStreaming=true during pending request and false after");
});
```

---

## 4. E2E Test Plan (Playwright)

Configuration:

```typescript
// playwright.config.ts
export default defineConfig({
  baseURL: process.env.E2E_BASE_URL ?? "http://localhost:3000",
  use: { screenshot: "only-on-failure", video: "retain-on-failure" },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile-safari", use: { ...devices["iPhone 13"] } },
  ],
});
```

Fixtures: `tests/e2e/fixtures/auth.ts` provides `authenticatedPage` that logs in and injects a valid session before each test.

---

### 4.1 Feature 1 — Student Profiles

| Path | Scenario | Steps | Assertion |
|---|---|---|---|
| Happy | Complete profile and set goals | Register → navigate to `/profile` → fill all fields → save → navigate to `/profile/goals` → set role and companies → save | Profile page shows updated name; goals page shows saved role |
| Sad | Submit profile with blank required field | Navigate to `/profile` → clear `Full Name` → click Save | Inline validation error "Full name is required" visible; no network request made |

### 4.2 Feature 2 — Assessments

| Path | Scenario | Steps | Assertion |
|---|---|---|---|
| Happy | Complete a full aptitude assessment | Navigate to `/assessments` → Start Aptitude → answer all questions → submit | Results page shows score percentage and "Assessment Complete" heading |
| Sad | Session times out | Start assessment → wait for timer to expire (mocked to 3 s) → attempt to submit | Error toast "Session expired. Your answers could not be submitted." visible |

### 4.3 Feature 3 — Recommendations

| Path | Scenario | Steps | Assertion |
|---|---|---|---|
| Happy | View personalised resources | Login as user with goals set → navigate to `/recommendations` | At least 3 resource cards visible with title and external link |
| Sad | No goals set — degraded state | Login as user with no goals → navigate to `/recommendations` | Banner "Set your placement goals to get personalised recommendations" with CTA link to `/profile/goals` |

### 4.4 Feature 4 — AI Chatbot

| Path | Scenario | Steps | Assertion |
|---|---|---|---|
| Happy | Send a question and receive a reply | Navigate to `/chatbot` → type "What is a binary search tree?" → press Enter | Assistant bubble appears with non-empty text; input clears |
| Sad | Network failure mid-conversation | Send message → intercept the messages API call to return 503 | Error message "Failed to send message. Try again." visible; previous messages intact |

### 4.5 Feature 5 — Resume Scanner

| Path | Scenario | Steps | Assertion |
|---|---|---|---|
| Happy | Upload resume and view analysis | Navigate to `/resume` → drag-drop valid PDF → wait for status badge "Analysis Ready" → click View Analysis | Analysis page shows score, at least one strength, at least one suggestion |
| Sad | Upload invalid file type | Navigate to `/resume` → attempt to drop a `.docx` file | Dropzone shows error "Only PDF files are accepted"; no upload begins |

### 4.6 Feature 6 — Interview Practice

| Path | Scenario | Steps | Assertion |
|---|---|---|---|
| Happy | Complete a technical mock interview | Navigate to `/interview` → choose Technical, SDE-1 → answer 3 questions → End Session → View Report | Report page shows overall score (numeric), strengths section, and improvement areas |
| Sad | Submit empty answer | Start interview session → click Submit without typing | Inline error "Please enter an answer before submitting" visible |

### 4.7 Feature 7 — Progress Dashboard

| Path | Scenario | Steps | Assertion |
|---|---|---|---|
| Happy | Dashboard reflects completed activities | Complete one assessment and one interview in prior steps → navigate to `/dashboard` | Readiness score > 0; activity timeline shows at least 2 entries |
| Sad | Dashboard for brand-new user | Register fresh account → navigate to `/dashboard` | Readiness score shows 0%; CTA cards prompt user to take first assessment and upload resume |

---

## 5. Acceptance Criteria

Acceptance criteria are written in **Given / When / Then** format. A feature is accepted only when all criteria pass in the staging environment with no mocked AI.

---

### Feature 1 — Student Profiles and Placement Goals

**AC-1.1 — Profile Creation**
> **Given** a newly registered user with no profile data,
> **When** the user submits the profile form with a valid name, college, branch, and graduation year,
> **Then** the API responds with `200`, the profile row is persisted, and the UI displays the submitted values on next load.

**AC-1.2 — Profile Update Persistence**
> **Given** a user with an existing profile,
> **When** the user changes their branch and saves,
> **Then** `GET /api/v1/profile/me` returns the updated branch within the same session and after a hard refresh.

**AC-1.3 — Goal Setting**
> **Given** an authenticated user on the goals page,
> **When** the user selects "Software Engineer" as the target role, adds two target companies, and sets a target date 90 days in the future,
> **Then** the goals are saved, the recommendations cache is invalidated, and the chatbot context in subsequent sessions reflects the stated role.

**AC-1.4 — Data Privacy**
> **Given** two distinct authenticated users A and B,
> **When** user A attempts to access `GET /api/v1/profile/{user_b_id}` where `user_b_id` is not their own,
> **Then** the API returns `403 Forbidden` and no profile data is returned.

**AC-1.5 — Graduation Year Validation**
> **Given** a user on the profile edit page,
> **When** the user enters a graduation year that is in the past (e.g., 2019),
> **Then** the form displays an inline validation error "Graduation year must be the current year or later" and the Save button remains disabled.

---

### Feature 2 — Aptitude and Technical Assessments

**AC-2.1 — Session Initiation**
> **Given** an authenticated user,
> **When** they start an "aptitude" assessment,
> **Then** a session is created with `status=in_progress`, a 30-minute expiry is set, and exactly 20 questions are returned in a randomised order.

**AC-2.2 — Score Accuracy**
> **Given** a completed assessment session,
> **When** the result is retrieved,
> **Then** the `percentage_score` equals `(correct_answers / total_questions) × 100` rounded to one decimal place, and the value is between 0.0 and 100.0 inclusive.

**AC-2.3 — Timeout Enforcement**
> **Given** an active session whose `expires_at` has passed,
> **When** the user submits answers,
> **Then** the API returns `409` with `{"detail": "session_expired"}`, the session status is set to `timed_out`, and no score is recorded.

**AC-2.4 — No Replay**
> **Given** a session with `status=completed`,
> **When** a submit request is made to the same session ID,
> **Then** the API returns `409` with `{"detail": "session_already_completed"}` and the stored score is unchanged.

**AC-2.5 — Result Visibility**
> **Given** a completed session,
> **When** the user navigates to the results page,
> **Then** the score percentage, number of correct answers, and a per-question breakdown (correct/incorrect) are all displayed.

---

### Feature 3 — Personalised Preparation Recommendations

**AC-3.1 — AI-Driven Content**
> **Given** a user with a defined placement goal,
> **When** they load the recommendations page,
> **Then** the system returns at least 5 resources, each with a title, type (article/video/practice), URL, and priority level, and the content is relevant to the stated target role.

**AC-3.2 — Cache Freshness**
> **Given** a user who has not changed their profile or goals,
> **When** they load the recommendations page a second time within 24 hours,
> **Then** the response is served from cache, the Gemini API is not called, and response latency is under 200 ms.

**AC-3.3 — Goal Change Triggers Refresh**
> **Given** a user with cached recommendations,
> **When** they update their target role and revisit the recommendations page,
> **Then** a new Gemini call is made and the returned resources reflect the updated role.

**AC-3.4 — Graceful Degradation**
> **Given** the Gemini API is unavailable,
> **When** a user requests recommendations,
> **Then** the system returns `503` with `{"detail": "ai_service_unavailable"}` and the UI displays "Recommendations are temporarily unavailable. Please try again later."

**AC-3.5 — No Goals State**
> **Given** a user with no goals set,
> **When** they navigate to `/recommendations`,
> **Then** the page displays a prompt "Set your placement goals to receive personalised recommendations" with a link to `/profile/goals`, and no AI call is made.

---

### Feature 4 — AI-Powered Placement Chatbot

**AC-4.1 — Session Continuity**
> **Given** a user who has sent 5 messages in a chat session,
> **When** they refresh the page and reopen the same session,
> **Then** all 5 prior message bubbles are displayed in chronological order.

**AC-4.2 — Context Awareness**
> **Given** a user whose profile specifies role "Data Analyst",
> **When** they ask "What skills should I focus on?",
> **Then** the assistant's response mentions data-analysis-relevant skills (SQL, Python, statistics) rather than generic programming advice.

**AC-4.3 — Response Latency**
> **Given** a normal network and Gemini availability,
> **When** the user sends a message,
> **Then** the first token of the assistant reply is rendered within 3 seconds of submission (measured at the 95th percentile in load testing).

**AC-4.4 — Message Persistence**
> **Given** an authenticated user,
> **When** they send a message,
> **Then** both the user message and the assistant reply are stored in the database and retrievable via `GET /api/v1/chatbot/sessions/{id}/messages`.

**AC-4.5 — Cross-User Isolation**
> **Given** user A's chat session,
> **When** user B attempts to read or post to that session,
> **Then** the API returns `403 Forbidden` for both `GET` and `POST` operations.

---

### Feature 5 — Resume Scanner

**AC-5.1 — Upload Acceptance**
> **Given** an authenticated user,
> **When** they upload a valid PDF file ≤ 5 MB,
> **Then** the API responds `202`, a resume record is created with `status=queued`, and a `resume_id` is returned within 2 seconds.

**AC-5.2 — File Validation**
> **Given** an authenticated user,
> **When** they attempt to upload a non-PDF file (e.g. `.docx`, `.png`) or a PDF exceeding 5 MB,
> **Then** the API returns `415` or `413` respectively, no record is created, and the UI displays a specific error message.

**AC-5.3 — Analysis Completeness**
> **Given** a resume with `status=complete`,
> **When** the analysis endpoint is called,
> **Then** the response includes: `score` (0–100 integer), `strengths` (≥ 1 item), `gaps` (≥ 0 items), `suggestions` (≥ 1 item), and each item has a non-empty `text` field.

**AC-5.4 — Role-Specific Suggestions**
> **Given** a user whose goal is "Backend Engineer" and who uploads a resume,
> **When** analysis is complete,
> **Then** the `suggestions` array contains at least one item referencing backend-relevant skills (e.g. API design, databases, system design).

**AC-5.5 — Processing Status Transparency**
> **Given** a resume in `processing` state,
> **When** the user polls `GET /api/v1/resume/{id}/status`,
> **Then** the API returns `202` with `{"status": "processing"}`, and within 60 seconds of upload the status transitions to either `complete` or `failed`.

---

### Feature 6 — Technical and HR Interview Practice

**AC-6.1 — Session Start**
> **Given** an authenticated user,
> **When** they start a technical interview for role "SDE-1",
> **Then** a session is created, the first question is domain-relevant (data structures / algorithms / system design), and the session is limited to a maximum of 10 questions.

**AC-6.2 — Turn-by-Turn Evaluation**
> **Given** an active interview session,
> **When** the user submits an answer to a question,
> **Then** AI feedback is returned in the same response, containing a `score` (integer 1–10) and an `explanation` (non-empty string ≥ 20 characters).

**AC-6.3 — Report Generation**
> **Given** a completed interview session with at least 3 answered questions,
> **When** the user requests the session report,
> **Then** the report contains `overall_score` (weighted average of turn scores), `strengths` (list ≥ 1), `improvement_areas` (list ≥ 1), and a per-question breakdown with individual scores and explanations.

**AC-6.4 — HR Mode**
> **Given** a user who starts an HR interview session,
> **When** questions are served,
> **Then** all questions belong to the HR category (behavioural, situational, or career-related) and no coding or algorithm questions are included.

**AC-6.5 — Report Access Control**
> **Given** a completed session owned by user A,
> **When** user B requests the report for that session,
> **Then** the API returns `403 Forbidden`.

---

### Feature 7 — Progress Tracking Dashboard

**AC-7.1 — Readiness Score Range**
> **Given** any authenticated user,
> **When** `GET /api/v1/dashboard/readiness` is called,
> **Then** `readiness_score` is an integer between 0 and 100 inclusive, and `level` is one of `["not_started", "early", "on_track", "ready"]`.

**AC-7.2 — Score Composition**
> **Given** a user who has completed one aptitude assessment (80%), one technical assessment (60%), and one mock interview (score 7/10),
> **When** the readiness score is computed,
> **Then** the score equals `round(0.3 × 80 + 0.4 × 60 + 0.3 × 70)` = **69** and `level` = `"on_track"`.

**AC-7.3 — Activity Timeline**
> **Given** a user who has performed activities across at least three different feature areas,
> **When** they load `GET /api/v1/dashboard/activity?days=30`,
> **Then** the response contains one event per completed action, each with `type`, `timestamp`, and `metadata`, ordered by `timestamp` descending.

**AC-7.4 — Real-Time Score Update**
> **Given** a user currently viewing the dashboard,
> **When** they complete a new assessment in another tab,
> **Then** the readiness score on the dashboard updates within 10 seconds without a full page reload (WebSocket or polling at ≤ 10 s interval).

**AC-7.5 — Empty State**
> **Given** a user with no completed assessments, interviews, or resume uploads,
> **When** they load the dashboard,
> **Then** the readiness score displays as 0, the activity timeline shows "No activity yet", and CTA cards are displayed for each incomplete feature area.

---

## 6. CI/CD Testing Gates

All checks run in GitHub Actions. A pull request **cannot be merged to `main`** unless every gate below is green.

### 6.1 Gate Definitions

```yaml
# .github/workflows/ci.yml (excerpt)
jobs:

  backend-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install ruff mypy
      - run: ruff check backend/
      - run: mypy backend/app --strict

  backend-test:
    needs: backend-lint
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: placement_test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        options: --health-cmd pg_isready
    env:
      TEST_DATABASE_URL: postgresql+asyncpg://test:test@localhost/placement_test
      STORAGE_BACKEND: local
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r backend/requirements-test.txt
      - run: pytest backend/tests/unit backend/tests/integration
               --cov=app --cov-report=xml
               --cov-fail-under=80
               -x -q

  frontend-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run lint
      - run: npm run type-check

  frontend-test:
    needs: frontend-lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm test -- --coverage --ci --coverageThreshold='{"global":{"statements":75,"branches":65}}'

  e2e-test:
    needs: [backend-test, frontend-test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npx playwright install --with-deps chromium
      - run: npx playwright test --project=chromium
    env:
      E2E_BASE_URL: http://localhost:3000
```

### 6.2 Gate Summary Table

| Gate | Tool | Failure Condition | Blocks Merge |
|---|---|---|---|
| Backend lint | `ruff` | Any lint error | ✅ |
| Backend type check | `mypy --strict` | Any type error | ✅ |
| Backend unit + integration tests | `pytest` | Any test failure | ✅ |
| Backend line coverage | `pytest-cov` | < 80% line coverage | ✅ |
| Frontend lint | ESLint | Any error (warnings allowed) | ✅ |
| Frontend type check | `tsc --noEmit` | Any type error | ✅ |
| Frontend component + hook tests | Jest | Any test failure | ✅ |
| Frontend statement coverage | Jest `--coverage` | < 75% statement coverage | ✅ |
| E2E happy paths (Chromium) | Playwright | Any happy-path failure | ✅ |
| Gemini contract test | pytest (separate job) | Schema mismatch | ⚠️ Opens issue, does not block |

### 6.3 Merge Rules

- All gates must pass on the **head commit** of the PR branch.
- At least **1 approved review** from a code owner is required.
- The PR branch must be **up-to-date with `main`** before merging.
- Direct pushes to `main` are disabled via branch protection rules.
- Failed E2E tests produce an artifact bundle (screenshots + videos) attached to the Actions run for debugging.
