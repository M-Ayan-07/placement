# AI-Powered Placement Coach

**Tagline:** From campus to career — personalized, AI-driven placement preparation for engineering students.

---

## Description

AI-Powered Placement Coach is a full-stack web application that guides engineering and computer science students through every stage of campus placement preparation. It combines structured assessments, adaptive learning recommendations, resume analysis, and AI-driven interview practice into a single, cohesive platform. By integrating Google Gemini as its AI backbone, the application delivers context-aware feedback and coaching that adapts to each student's skill gaps, target companies, and placement timeline.

---

## Problem Statement

Campus placement seasons expose a persistent gap: students are academically capable but procedurally underprepared. Preparation is fragmented across disconnected resources — YouTube playlists for DSA, separate mock-test portals for aptitude, PDF resume templates, and ad-hoc peer mock interviews. There is no single system that understands a student's current skill level, tracks progress over time, and provides role-specific guidance. Students burn time switching contexts, receive no personalized feedback, and have no reliable signal for when they are placement-ready. This project exists to close that gap.

---

## Target Users

| Persona | Description |
|---|---|
| **Primary: Engineering/CS Student** | Final- or pre-final-year undergraduate student actively preparing for on-campus or off-campus placements. Familiarity with basic programming; varied aptitude and interview readiness. |
| **Secondary: Placement Cell Coordinator** | College placement officer who may monitor aggregate student progress. (Read-only analytics — out of V1 scope for UI, but data model must support it.) |

---

## Core Features

> These features map directly to the approved project synopsis. No features outside this list are in scope for V1.

### 1. Student Profiles and Placement Goals
Students create an account and complete an onboarding profile that captures: degree programme, graduation year, target companies or sectors, preferred roles (SDE, Data Analyst, etc.), and current self-assessed skill level. Goals are stored and used to personalise all downstream recommendations and assessments.

### 2. Aptitude and Technical Assessments
Timed assessments covering quantitative aptitude, logical reasoning, verbal ability, data structures, algorithms, operating systems, DBMS, and system design fundamentals. Questions are drawn from a categorised question bank stored in PostgreSQL. Results are scored, stored per attempt, and used to compute a skill-gap profile.

### 3. Personalised Preparation Recommendations and Learning Resources
Based on assessment results and stated goals, the system generates a prioritised study plan. Recommendations include curated external learning resources (articles, problems, videos) tagged by topic and difficulty, surfaced through the Gemini API. The plan updates as the student progresses.

### 4. AI-Powered Placement Chatbot
A conversational assistant powered by Gemini that answers placement-related questions, explains concepts, helps debug code snippets, and advises on preparation strategy. Chat history is persisted per user session in PostgreSQL.

### 5. Resume Scanner with Role-Specific Suggestions
Students upload a PDF or paste resume text. The system uses Gemini to parse the resume and generate role-specific, actionable improvement suggestions — covering content gaps, keyword alignment with job descriptions, formatting issues, and strength highlights. Results are stored and the student can iterate on multiple resume versions.

### 6. Technical and HR Interview Practice
- **Technical Practice:** The student selects a topic and difficulty. The system presents a coding or conceptual problem. The student submits a solution or answer. Gemini evaluates the response and provides structured feedback (correctness, time/space complexity commentary, better approaches).
- **HR Practice:** Behavioural and situational questions (e.g., "Tell me about yourself", "Describe a conflict you resolved") with AI-generated feedback on answer structure, clarity, and content.
- Sessions are recorded with scores and feedback for review.

### 7. Progress Tracking Dashboard
A per-student dashboard visualising: assessment score trends over time, topics attempted vs. topics remaining, interview practice session history and scores, resume iteration count, and an overall "placement readiness" indicator derived from aggregated performance metrics.

---

## High-Level User Journey

```
Register / Log In
      │
      ▼
Complete Onboarding Profile
(name, college, graduation year, target roles, self-assessed skills)
      │
      ▼
Take Baseline Assessment
(aptitude + technical — approximately 45 minutes)
      │
      ▼
View Personalised Preparation Plan
(topic priority queue, curated resources, estimated timeline)
      │
      ├──► Practice Assessments (retake specific topic quizzes)
      │
      ├──► Interview Practice (technical problems / HR questions with AI feedback)
      │
      ├──► Resume Scanner (upload → receive role-specific suggestions → iterate)
      │
      ├──► Placement Chatbot (ask questions, clarify concepts, strategy advice)
      │
      └──► Progress Dashboard (track scores, readiness indicator, session history)
```

A student cycles through Practice → Dashboard → Chatbot/Resources until the readiness indicator reaches their personal threshold or the placement season begins.

---

## Project Goals (V1 Scope)

| # | Goal |
|---|---|
| G1 | Deliver all seven approved features as functional, integrated modules within a single deployable application. |
| G2 | Provide a sub-3-second response time for all non-AI endpoints under typical single-user load. |
| G3 | Integrate free-tier AI APIs (Google AI Studio Free Tier / Groq Free Tier / local Ollama) via a modular adapter with configurable model names, incurring $0 in API costs. |
| G4 | Implement JWT-based authentication (access token + refresh token) with refresh tokens persisted in PostgreSQL and delivered via secure HttpOnly cookies. |
| G5 | Package the entire stack (Next.js frontend, FastAPI backend, PostgreSQL) in Docker Compose for one-command local setup. |
| G6 | Store all student performance data in a schema that supports future analytics extensions (e.g., placement cell dashboards) without a migration overhaul. |
| G7 | Maintain a strict $0 budget for all dependencies, APIs, and infrastructure in development and testing. |

---

## Non-Goals (Explicitly Out of V1 Scope)

| # | Non-Goal | Rationale |
|---|---|---|
| NG1 | Placement cell coordinator UI / admin portal | Data model will support it; UI deferred to V2. |
| NG2 | Redis or any in-memory cache layer | Refresh tokens go to PostgreSQL in V1; Redis added only if latency profiling justifies it. |
| NG3 | Real-time collaborative features (peer mock interviews, live chat) | Requires WebSocket infrastructure beyond V1 complexity budget. |
| NG4 | Mobile native applications (iOS / Android) | Web-responsive only; native apps are a V2+ consideration. |
| NG5 | Paid API subscriptions or billing-enabled cloud services | The architecture operates exclusively on verified free-tier limits ($0 operating cost). |
| NG6 | Payment gateway or premium tier | V1 is single-tier; monetisation strategy is post-launch. |
| NG7 | Automated job application or ATS integration | Out of scope; the platform prepares students but does not apply on their behalf. |
| NG8 | Email/SMS notification system | Deferred; no transactional messaging in V1. |

---

## Glossary

| Term | Definition |
|---|---|
| **Placement Season** | The academic-calendar period (typically August–March in Indian engineering colleges) during which companies visit campus to recruit graduating students. |
| **Aptitude Assessment** | A timed test covering quantitative reasoning, logical reasoning, and verbal ability — a standard screening round in most campus recruitment drives. |
| **Skill-Gap Profile** | A structured summary of the topics where a student's assessment scores fall below a defined threshold relative to their target role requirements. |
| **Preparation Plan** | An ordered, personalised list of study topics and linked resources generated from the student's skill-gap profile and placement goals. |
| **Placement Readiness Indicator** | A composite score (0–100) derived from assessment performance, interview practice scores, and resume completeness, used to give students a single progress signal. |
| **Resume Scanner** | The feature that accepts a student's resume and uses Gemini to produce role-specific, actionable improvement suggestions. |
| **Interview Practice Session** | A recorded interaction in which the student answers a technical or HR question and receives structured AI feedback. |
| **Access Token** | A short-lived JWT (15-minute expiry) sent with every authenticated API request in the `Authorization: Bearer` header. |
| **Refresh Token** | A long-lived opaque token (7-day expiry) stored server-side in PostgreSQL and used to issue new access tokens without requiring re-login. |
| **App Router** | The Next.js 13+ routing paradigm based on the `app/` directory, React Server Components, and nested layouts — the routing model used in this project. |
| **shadcn/ui** | A collection of accessible, unstyled React components built on Radix UI primitives and styled with Tailwind CSS, used as the project's component library. |
| **Docker Compose** | The container orchestration tool used to define and run the multi-container local development environment (frontend, backend, database). |
