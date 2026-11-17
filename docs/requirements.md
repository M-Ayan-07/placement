# Requirements Specification — AI-Powered Placement Coach

**Version:** 1.0.0
**Status:** Approved
**Last Updated:** 2026-10-31

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Functional Requirements](#2-functional-requirements)
   - [FR-AUTH — Authentication & Authorization](#fr-auth--authentication--authorization)
   - [FR-PROFILE — Student Profile & Placement Goals](#fr-profile--student-profile--placement-goals)
   - [FR-ASSESSMENT — Aptitude & Technical Assessments](#fr-assessment--aptitude--technical-assessments)
   - [FR-RECOMMENDATIONS — Personalized Recommendations](#fr-recommendations--personalized-recommendations)
   - [FR-CHATBOT — AI Placement Chatbot](#fr-chatbot--ai-placement-chatbot)
   - [FR-RESUME — Resume Scanner](#fr-resume--resume-scanner)
   - [FR-INTERVIEW — Interview Practice](#fr-interview--interview-practice)
   - [FR-DASHBOARD — Progress Tracking Dashboard](#fr-dashboard--progress-tracking-dashboard)
3. [Non-Functional Requirements](#3-non-functional-requirements)
4. [Constraints & Assumptions](#4-constraints--assumptions)

---

## 1. Project Overview

The **AI-Powered Placement Coach** is a web application that helps engineering and computer science students prepare for campus placement drives. It provides structured assessments, AI-generated study plans, resume analysis, mock interview practice, and a domain-specific AI chatbot — all personalised to each student's target companies, roles, and current skill level.

### Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14+ (App Router), Tailwind CSS, shadcn/ui |
| Backend | Python 3.11+, FastAPI |
| Database | PostgreSQL 16 (in Docker, zero cost) |
| AI Provider | Modular Adapter: Google AI Studio Free Tier (default), Groq Free Tier, or local Ollama |
| Authentication | JWT (HS256) — 15-min access token + 7-day refresh token in PostgreSQL (HttpOnly cookie) |
| Containerisation | Docker, Docker Compose |

---

## 2. Functional Requirements

> [!NOTE]
> All requirements use the format **"The system shall…"** Requirement IDs are stable and referenced in test cases and implementation tickets.

---

### FR-AUTH — Authentication & Authorization

| ID | Requirement |
|---|---|
| FR-AUTH-01 | The system shall allow a new user to register with a unique email address, full name, and a password of at least 8 characters containing at least one uppercase letter, one lowercase letter, one digit, and one special character. |
| FR-AUTH-02 | The system shall hash all passwords using bcrypt with a minimum cost factor of 12 before storing them in the database. |
| FR-AUTH-03 | The system shall send a verification email containing a time-limited (24-hour) email confirmation link upon successful registration. |
| FR-AUTH-04 | The system shall reject login attempts from unverified email accounts with an HTTP 403 response and a descriptive error message. |
| FR-AUTH-05 | The system shall authenticate registered users via email and password, issuing a signed JWT access token (expiry: 15 minutes) and a JWT refresh token (expiry: 7 days) on success. |
| FR-AUTH-06 | The system shall store refresh tokens in the `refresh_tokens` PostgreSQL table, associating each token with its user ID, issued-at timestamp, expiry timestamp, and a revoked flag. |
| FR-AUTH-07 | The system shall expose a `POST /auth/refresh` endpoint that accepts a valid, non-revoked refresh token and returns a new access token and a rotated refresh token; the previous refresh token shall be immediately marked as revoked. |
| FR-AUTH-08 | The system shall expose a `POST /auth/logout` endpoint that accepts the current refresh token and marks it as revoked, invalidating the session. |
| FR-AUTH-09 | The system shall reject any request to a protected endpoint that presents an expired, malformed, or missing JWT access token with an HTTP 401 response. |
| FR-AUTH-10 | The system shall lock an account for 15 minutes after 5 consecutive failed login attempts from the same email address and record the lockout event in an audit log. |
| FR-AUTH-11 | The system shall expose a `POST /auth/forgot-password` endpoint that sends a password-reset link (valid for 1 hour, single-use) to the registered email address without confirming or denying whether the email exists. |
| FR-AUTH-12 | The system shall expose a `POST /auth/reset-password` endpoint that accepts a valid reset token and a new password, updates the credential, and revokes all existing refresh tokens for that user. |

---

### FR-PROFILE — Student Profile & Placement Goals

| ID | Requirement |
|---|---|
| FR-PROFILE-01 | The system shall allow an authenticated student to create and update a profile containing: full name, profile photo (JPEG/PNG, max 2 MB), institution name, degree programme, current year of study, CGPA, and a short bio (max 500 characters). |
| FR-PROFILE-02 | The system shall allow a student to specify placement goals including: target companies (multi-select, max 20), target roles (multi-select, e.g., SDE, Data Analyst, DevOps Engineer), target CTC range (in LPA), and expected graduation year. |
| FR-PROFILE-03 | The system shall allow a student to list technical skills with self-assessed proficiency levels (Beginner / Intermediate / Advanced) and years of experience for each skill. |
| FR-PROFILE-04 | The system shall allow a student to add education history entries, each containing institution name, degree, field of study, start year, end year (or "Present"), and percentage/CGPA. |
| FR-PROFILE-05 | The system shall allow a student to add project entries, each containing project title, tech stack used, description (max 1000 characters), and an optional GitHub/live URL. |
| FR-PROFILE-06 | The system shall allow a student to add internship and work experience entries, each containing company name, role, start date, end date (or "Present"), and a description (max 500 characters). |
| FR-PROFILE-07 | The system shall expose a `GET /profile/me` endpoint returning the complete profile of the authenticated student, including computed profile completeness percentage. |
| FR-PROFILE-08 | The system shall compute profile completeness as a percentage based on the presence of: profile photo, bio, skills (≥3), education, projects (≥1), work experience, and placement goals — displayed on the dashboard. |
| FR-PROFILE-09 | The system shall display a prompt on the dashboard when profile completeness is below 70%, listing the specific missing sections. |

---

### FR-ASSESSMENT — Aptitude & Technical Assessments

| ID | Requirement |
|---|---|
| FR-ASSESS-01 | The system shall provide aptitude assessments in three categories: **Quantitative Aptitude** (arithmetic, algebra, percentages, time-speed-distance), **Logical Reasoning** (series, analogies, syllogisms, puzzles), and **Verbal Ability** (reading comprehension, grammar, vocabulary, sentence correction). |
| FR-ASSESS-02 | The system shall provide technical assessments in two categories: **Data Structures & Algorithms** (arrays, linked lists, trees, graphs, sorting, dynamic programming) and **CS Fundamentals** (OS, DBMS, Computer Networks, OOP concepts). |
| FR-ASSESS-03 | The system shall present each assessment as a fixed-length timed test: Aptitude tests — 30 questions in 30 minutes; DSA tests — 20 questions in 40 minutes; CS Fundamentals tests — 25 questions in 25 minutes. |
| FR-ASSESS-04 | The system shall display a countdown timer during an active assessment and automatically submit the assessment when the timer reaches zero, saving all answers recorded up to that point. |
| FR-ASSESS-05 | The system shall support question types: single-correct MCQ, multiple-correct MCQ, and fill-in-the-blank (numeric answer). |
| FR-ASSESS-06 | The system shall auto-score completed assessments immediately upon submission, applying a marking scheme of +1 for correct and 0 for incorrect/unattempted (no negative marking in V1). |
| FR-ASSESS-07 | The system shall display a detailed result page after submission showing: total score, percentage, section-wise scores, time taken, per-question correctness, the student's answer, and the correct answer with an explanation. |
| FR-ASSESS-08 | The system shall tag each question with a topic, difficulty level (Easy / Medium / Hard), and the assessment category, and store these tags in the database for analytics. |
| FR-ASSESS-09 | The system shall prevent a student from retaking the same assessment within 24 hours of their last attempt and display the remaining cooldown period. |
| FR-ASSESS-10 | The system shall store every assessment attempt — including question IDs, selected answers, time spent per question, and final score — in the `assessment_attempts` table for historical tracking. |
| FR-ASSESS-11 | The system shall expose a `GET /assessments/history` endpoint returning a paginated list of a student's past assessment attempts, sorted by date descending. |

---

### FR-RECOMMENDATIONS — Personalized Recommendations

| ID | Requirement |
|---|---|
| FR-REC-01 | The system shall generate a personalised study plan for a student using the Gemini API, taking as input: assessment scores (section-wise), weak topic tags identified from incorrect answers, target companies, target roles, and available hours per week (entered by the student). |
| FR-REC-02 | The system shall structure the generated study plan as a week-by-week schedule, specifying topics to cover each week, recommended daily time allocation, and milestone goals. |
| FR-REC-03 | The system shall curate a list of learning resources for each weak topic, including: resource title, type (article / video / course / problem set), URL, estimated completion time, and difficulty level. |
| FR-REC-04 | The system shall refresh the study plan automatically whenever a student completes a new assessment attempt, incorporating the latest performance data. |
| FR-REC-05 | The system shall allow a student to manually trigger a study plan refresh at most once every 24 hours via a `POST /recommendations/refresh` endpoint. |
| FR-REC-06 | The system shall display a prioritised list of recommended topics sorted by: (1) relevance to target companies/roles, (2) student's current weakness score in that topic, and (3) topic importance weight defined in the system's topic metadata. |
| FR-REC-07 | The system shall persist the latest generated study plan in the `study_plans` table with a timestamp, allowing the student to view the history of previously generated plans. |
| FR-REC-08 | The system shall surface company-specific preparation notes (interview patterns, frequently tested topics) for each company in the student's target list, sourced from a curated internal knowledge base. |

---

### FR-CHATBOT — AI Placement Chatbot

| ID | Requirement |
|---|---|
| FR-CHAT-01 | The system shall provide an AI-powered chatbot on a dedicated page, powered by the Google Gemini API, scoped exclusively to placement preparation topics (technical interviews, aptitude, resume, HR questions, company-specific guidance). |
| FR-CHAT-02 | The system shall maintain a per-session conversation history (up to the last 20 message pairs) and include it in every Gemini API call to enable context-aware responses. |
| FR-CHAT-03 | The system shall inject a system prompt into every Gemini API call that constrains the model to the placement domain, instructs it to politely decline off-topic queries, and provides the student's profile summary (target roles, weak topics) as context. |
| FR-CHAT-04 | The system shall stream the chatbot's response token-by-token to the frontend using Server-Sent Events (SSE), displaying tokens as they arrive to minimise perceived latency. |
| FR-CHAT-05 | The system shall persist all chatbot conversations (user messages and AI responses) in the `chat_sessions` and `chat_messages` tables, linked to the authenticated student. |
| FR-CHAT-06 | The system shall allow a student to start a new conversation session, which resets the conversation history context, via a "New Chat" action. |
| FR-CHAT-07 | The system shall display a list of past conversation sessions on the chatbot page, allowing the student to review prior conversations (read-only). |
| FR-CHAT-08 | The system shall enforce a rate limit of 30 chatbot messages per student per hour, responding with an HTTP 429 and a retry-after timestamp when the limit is exceeded. |
| FR-CHAT-09 | The system shall display suggested starter prompts on an empty conversation screen (e.g., "Help me prepare for a TCS interview", "Explain dynamic programming with examples"). |

---

### FR-RESUME — Resume Scanner

| ID | Requirement |
|---|---|
| FR-RESUME-01 | The system shall allow an authenticated student to upload a resume file in PDF or DOCX format, with a maximum file size of 5 MB, via a `POST /resume/upload` endpoint. |
| FR-RESUME-02 | The system shall reject uploads of files with MIME types other than `application/pdf` and `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, returning an HTTP 415 error with a descriptive message. |
| FR-RESUME-03 | The system shall extract text content from the uploaded resume using a server-side parser (PyMuPDF for PDF, python-docx for DOCX) without relying on the Gemini API for extraction. |
| FR-RESUME-04 | The system shall send the extracted resume text and the student's target role(s) to the Gemini API and receive a structured JSON analysis containing: identified skills, experience summary, education details, detected projects, and an overall quality score (0–100). |
| FR-RESUME-05 | The system shall perform a gap analysis by comparing the AI-extracted resume skills against a role-specific required-skills checklist stored in the system, identifying missing skills for each target role. |
| FR-RESUME-06 | The system shall generate specific, actionable suggestions for each identified gap, including: the missing skill/keyword, why it matters for the target role, and how to address it (e.g., "Add a project demonstrating X" or "Include your experience with Y from internship Z"). |
| FR-RESUME-07 | The system shall evaluate resume quality on the following dimensions and display a score (0–10) for each: impact of bullet points, use of quantifiable achievements, ATS keyword coverage for target roles, formatting consistency, and section completeness. |
| FR-RESUME-08 | The system shall store each resume upload and its analysis result in the `resumes` table, retaining the last 5 resume versions per student and deleting older files from storage. |
| FR-RESUME-09 | The system shall display a diff-style comparison when a student uploads a new resume version, highlighting improvements and regressions versus the previous version's scores. |
| FR-RESUME-10 | The system shall store uploaded resume files in a server-side directory accessible only to the backend service, never exposing direct file URLs to the client. |

---

### FR-INTERVIEW — Interview Practice

| ID | Requirement |
|---|---|
| FR-INT-01 | The system shall provide a **Technical Mock Interview** mode where the student selects a topic (e.g., Arrays, System Design, DBMS) and a difficulty level (Easy / Medium / Hard), and the system presents a series of 5–10 interview-style questions generated by the Gemini API. |
| FR-INT-02 | The system shall provide an **HR Mock Interview** mode with behavioural questions (e.g., STAR-format questions on teamwork, leadership, conflict resolution, strengths/weaknesses) generated by the Gemini API based on the student's profile and target roles. |
| FR-INT-03 | The system shall accept the student's answer to each interview question as free-text input (max 2000 characters per answer). |
| FR-INT-04 | The system shall submit each student answer to the Gemini API and return structured AI feedback containing: a score (0–10), specific strengths in the answer, specific weaknesses, a model answer or key points that should have been covered, and a suggested improvement. |
| FR-INT-05 | The system shall display AI feedback immediately after the student submits each answer, before presenting the next question. |
| FR-INT-06 | The system shall generate a session summary at the end of each interview session, including: overall score, average score per question, strongest topics, weakest topics, and a recommended focus area for improvement. |
| FR-INT-07 | The system shall store each interview session — including all questions, student answers, AI feedback, and session summary — in the `interview_sessions` and `interview_answers` tables. |
| FR-INT-08 | The system shall allow a student to review any past interview session in full (questions, their answers, and the AI feedback received) from the dashboard. |
| FR-INT-09 | The system shall allow the student to flag an AI-generated question or piece of feedback as inappropriate or incorrect, recording the flag in the `content_flags` table for admin review. |
| FR-INT-10 | The system shall support a "Company-Specific Interview" mode where the student selects a target company and the system tailors question style and topics based on that company's known interview pattern from the internal knowledge base. |

---

### FR-DASHBOARD — Progress Tracking Dashboard

| ID | Requirement |
|---|---|
| FR-DASH-01 | The system shall display a **Placement Readiness Score** (0–100) computed as a weighted average of: profile completeness (15%), assessment performance (35%), interview session scores (30%), and resume quality score (20%). |
| FR-DASH-02 | The system shall display assessment score history as a line chart per assessment category (Quantitative, Logical, Verbal, DSA, CS Fundamentals), with each data point representing a completed attempt, ordered chronologically. |
| FR-DASH-03 | The system shall display a topic-wise performance heatmap showing the student's accuracy percentage for each topic tag across all assessment attempts. |
| FR-DASH-04 | The system shall display an activity log listing the last 30 events, including: assessments taken, resume uploads, chatbot sessions started, and interview sessions completed, each with a timestamp. |
| FR-DASH-05 | The system shall display interview performance trend as a bar chart showing average interview score per session, categorised by interview type (Technical / HR). |
| FR-DASH-06 | The system shall display current study plan progress, showing the percentage of recommended weekly topics marked as studied, allowing a student to mark individual topics as complete. |
| FR-DASH-07 | The system shall display upcoming assessment recommendations (next suggested assessment category and topic) based on the student's weakest areas and time since last attempt. |
| FR-DASH-08 | The system shall display a streak counter showing the number of consecutive days the student has performed at least one activity (assessment, interview session, or chatbot message). |
| FR-DASH-09 | The system shall expose a `GET /dashboard/summary` endpoint that returns all dashboard data in a single response to minimise round-trips on page load. |

---

## 3. Non-Functional Requirements

### NFR-PERF — Performance

| ID | Requirement |
|---|---|
| NFR-PERF-01 | All non-AI FastAPI endpoints (auth, profile, assessment, dashboard) shall respond within **300 ms** at the 95th percentile under a load of 100 concurrent users. |
| NFR-PERF-02 | Assessment auto-scoring shall complete and return results within **500 ms** of submission under normal load. |
| NFR-PERF-03 | Resume parsing and Gemini API analysis shall complete within **30 seconds** end-to-end; the frontend shall display a progress indicator for the duration. |
| NFR-PERF-04 | Chatbot SSE streaming shall deliver the first token to the client within **3 seconds** of the user submitting a message. |
| NFR-PERF-05 | The dashboard summary endpoint (`GET /dashboard/summary`) shall respond within **500 ms** at the 95th percentile by using PostgreSQL indexed queries and avoiding N+1 query patterns. |
| NFR-PERF-06 | The system shall support a minimum of **200 concurrent authenticated users** without degradation beyond the above thresholds, validated via load testing before production release. |

### NFR-SEC — Security

| ID | Requirement |
|---|---|
| NFR-SEC-01 | All HTTP traffic shall be served exclusively over **HTTPS/TLS 1.2+**; plain HTTP requests shall be redirected to HTTPS with a 301 response. |
| NFR-SEC-02 | JWT access tokens shall be signed using **HS256** with a secret of at least 64 characters stored in an environment variable, never committed to version control. |
| NFR-SEC-03 | All API endpoints that mutate state shall validate the `Content-Type` header and reject requests with unexpected content types. |
| NFR-SEC-04 | File uploads shall be scanned for MIME type spoofing by inspecting magic bytes server-side, independent of the client-supplied `Content-Type` header. |
| NFR-SEC-05 | Uploaded resume files shall be stored outside the web root and served only after verifying the requesting user owns the file; direct file URL enumeration shall not be possible. |
| NFR-SEC-06 | All PostgreSQL queries shall use parameterised statements or an ORM (SQLAlchemy) to prevent SQL injection; raw string interpolation into queries is prohibited. |
| NFR-SEC-07 | The application shall include the following HTTP security headers on all responses: `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Content-Security-Policy`, and `Referrer-Policy: no-referrer`. |
| NFR-SEC-08 | Sensitive configuration values (database credentials, Gemini API key, JWT secret) shall be injected via environment variables; a `.env.example` file with placeholder values shall be provided in the repository. |
| NFR-SEC-09 | The maximum accepted file upload size shall be enforced at the FastAPI layer (5 MB for resumes, 2 MB for profile photos); requests exceeding this limit shall be rejected with HTTP 413. |
| NFR-SEC-10 | All authentication events (login success, login failure, password reset, token refresh, account lockout) shall be written to an append-only `audit_log` table with timestamp, user ID, IP address, and event type. |

### NFR-SCALE — Scalability

| ID | Requirement |
|---|---|
| NFR-SCALE-01 | The FastAPI backend shall be **stateless** — no in-process session state — so that multiple backend container replicas can serve requests interchangeably behind a load balancer. |
| NFR-SCALE-02 | The application shall be fully containerised using Docker; the Docker Compose configuration shall define services for `api`, `frontend`, and `db` with defined health checks and restart policies. |
| NFR-SCALE-03 | Database schema migrations shall be managed exclusively via **Alembic** migration scripts; no ad-hoc schema changes shall be applied directly to the database. |
| NFR-SCALE-04 | The system shall use **connection pooling** (SQLAlchemy's `QueuePool`) configured with a pool size of 10 and maximum overflow of 20 to manage PostgreSQL connections efficiently. |

### NFR-AVAIL — Availability

| ID | Requirement |
|---|---|
| NFR-AVAIL-01 | The production environment shall target **99.5% monthly uptime**, excluding scheduled maintenance windows announced at least 24 hours in advance. |
| NFR-AVAIL-02 | The system shall implement graceful shutdown — completing in-flight requests within a 30-second timeout before the process exits — to support zero-downtime rolling deployments. |
| NFR-AVAIL-03 | The FastAPI application shall expose a `GET /health` endpoint returning HTTP 200 with database connectivity status; this endpoint shall be used by Docker Compose health checks and any future load balancer configuration. |

### NFR-USE — Usability

| ID | Requirement |
|---|---|
| NFR-USE-01 | The frontend shall be **fully responsive** and functional on screen widths from 375 px (mobile) to 1920 px (desktop), using Tailwind CSS responsive utilities. |
| NFR-USE-02 | The application shall achieve a **Lighthouse Accessibility score of ≥ 85** on all primary pages (Dashboard, Assessment, Chatbot, Resume, Interview). |
| NFR-USE-03 | All interactive UI elements shall provide visible focus indicators and meet WCAG 2.1 Level AA colour contrast requirements. |
| NFR-USE-04 | Assessment and interview session pages shall warn the student before any action that would result in loss of unsaved progress (e.g., navigating away during an active test). |
| NFR-USE-05 | All form validation errors shall be displayed inline, adjacent to the relevant field, within 300 ms of the triggering event, without a full page reload. |

### NFR-MAINT — Maintainability

| ID | Requirement |
|---|---|
| NFR-MAINT-01 | The FastAPI backend shall follow a layered architecture: `routers` (HTTP layer) → `services` (business logic) → `repositories` (data access). No database queries shall appear directly in router handlers. |
| NFR-MAINT-02 | All Python modules, classes, and public functions shall include docstrings following the Google docstring style. |
| NFR-MAINT-03 | The codebase shall enforce style consistency via pre-commit hooks: **Ruff** (Python linting + formatting) and **ESLint + Prettier** (TypeScript/TSX). |
| NFR-MAINT-04 | All FastAPI endpoint request/response schemas shall be defined as **Pydantic v2 models** with field-level validation and documentation strings used to auto-generate OpenAPI documentation. |
| NFR-MAINT-05 | The backend shall achieve a minimum **unit test coverage of 80%** for service-layer modules, measured by `pytest-cov` and enforced in CI. |
| NFR-MAINT-06 | Environment-specific configuration shall be managed via a Pydantic `BaseSettings` class loading from environment variables; no hardcoded configuration values shall exist in application code. |

---

## 4. Constraints & Assumptions

| # | Constraint / Assumption |
|---|---|
| C-01 | Redis is **not** used in V1; JWT refresh token management, session storage, and rate limiting are implemented using PostgreSQL. |
| C-02 | The system integrates via a **modular AI adapter (`BaseAIProvider`)**; it defaults to Google AI Studio Free Tier (no credit card required) and supports zero-code configuration switching to Groq Free Tier or local Ollama. Specific model names are never hardcoded. |
| C-03 | Assessment question content is pre-seeded into the database via Alembic seed scripts; no admin CMS for question management is in scope for V1. |
| C-04 | Email delivery uses an **SMTP relay** (configurable via environment variables); a specific email provider is not mandated. |
| C-05 | The application targets **students only** in V1; no admin portal, recruiter portal, or institutional dashboard is in scope. |
| C-06 | All monetary values (target CTC) are stored and displayed in **Indian Rupees (LPA)** only. |
| C-07 | Free-tier rate limits (~15 RPM, 1,500 RPD) are actively handled: requests exceeding limits trigger exponential backoff retries, graceful user messaging (HTTP 429), and optional fallback to local Ollama. Paid API subscriptions are strictly avoided. |
| C-08 | Resume file storage in V1 uses the **local filesystem** under `backend/uploads/` with UUID-randomized filenames, magic-byte validation, path-traversal prevention, and authenticated-only retrieval. Migration to free cloud object storage (e.g., Cloudflare R2 free tier) requires zero business logic changes. |
| C-09 | **Zero Cost Constraint**: All infrastructure, libraries, databases, and APIs must operate strictly on $0 / free tiers. No credit card or billing activation is required. |
