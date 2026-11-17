# API Contracts — AI-Powered Placement Coach

**Base URL (development):** `http://localhost:8000/api/v1`  
**Content-Type:** `application/json` (except file uploads: `multipart/form-data`)  
**Auth scheme:** `Authorization: Bearer <access_token>`

---

## Table of Contents

1. [Auth](#1-auth)
2. [Profile](#2-profile)
3. [Assessments](#3-assessments)
4. [Recommendations](#4-recommendations)
5. [Chatbot](#5-chatbot)
6. [Resume](#6-resume)
7. [Interview](#7-interview)
8. [Dashboard](#8-dashboard)
9. [Common Error Responses](#9-common-error-responses)

---

## 1. Auth

### POST `/auth/register`

**Auth:** Public

**Request Body**

```json
{
  "full_name":  "Priya Sharma",
  "email":      "priya@example.com",
  "password":   "Str0ng#Pass!",
  "role":       "student"
}
```

| Field | Type | Rules |
|---|---|---|
| `full_name` | string | 2–100 chars, required |
| `email` | string | valid email format, unique, required |
| `password` | string | min 8 chars, ≥1 uppercase, ≥1 digit, ≥1 special char |
| `role` | enum | `"student"` \| `"admin"` — defaults to `"student"` |

**Success `201 Created`**

```json
{
  "user_id":    "usr_4f9a1b2c3d",
  "full_name":  "Priya Sharma",
  "email":      "priya@example.com",
  "role":       "student",
  "created_at": "2026-10-31T18:00:00Z"
}
```

**Errors**

| Status | Reason |
|---|---|
| `400` | Validation failure (weak password, malformed email) |
| `409` | Email already registered |

---

### POST `/auth/login`

**Auth:** Public

**Request Body**

```json
{
  "email":    "priya@example.com",
  "password": "Str0ng#Pass!"
}
```

| Field | Type | Rules |
|---|---|---|
| `email` | string | required |
| `password` | string | required |

**Success `200 OK`**

```json
{
  "access_token":  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4...",
  "token_type":    "bearer",
  "expires_in":    900,
  "user": {
    "user_id":   "usr_4f9a1b2c3d",
    "full_name": "Priya Sharma",
    "email":     "priya@example.com",
    "role":      "student"
  }
}
```

> `expires_in` is in seconds (15 minutes for access token).

**Errors**

| Status | Reason |
|---|---|
| `400` | Missing fields |
| `401` | Invalid credentials |
| `403` | Account disabled |

---

### POST `/auth/refresh`

**Auth:** Public (refresh token in body)

**Request Body**

```json
{
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
}
```

**Success `200 OK`**

```json
{
  "access_token":  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "bmV3UmVmcmVzaFRva2Vu...",
  "token_type":    "bearer",
  "expires_in":    900
}
```

> Both tokens are rotated on each refresh. The old refresh token is invalidated immediately.

**Errors**

| Status | Reason |
|---|---|
| `400` | `refresh_token` missing |
| `401` | Token invalid, expired, or already used |

---

### POST `/auth/logout`

**Auth:** Bearer token

**Request Body**

```json
{
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
}
```

**Success `200 OK`**

```json
{
  "message": "Logged out successfully."
}
```

**Errors**

| Status | Reason |
|---|---|
| `400` | `refresh_token` missing |
| `401` | Access token invalid or expired |

---

## 2. Profile

### GET `/profile/me`

**Auth:** Bearer token

**Request:** No body or query params.

**Success `200 OK`**

```json
{
  "user_id":         "usr_4f9a1b2c3d",
  "full_name":       "Priya Sharma",
  "email":           "priya@example.com",
  "phone":           "+91-9876543210",
  "college":         "IIT Bombay",
  "degree":          "B.Tech",
  "branch":          "Computer Science",
  "graduation_year": 2027,
  "skills":          ["Python", "SQL", "Data Structures"],
  "linkedin_url":    "https://linkedin.com/in/priyasharma",
  "github_url":      "https://github.com/priyasharma",
  "avatar_url":      "https://cdn.example.com/avatars/usr_4f9a1b2c3d.jpg",
  "created_at":      "2026-10-31T18:00:00Z",
  "updated_at":      "2026-10-31T18:00:00Z"
}
```

**Errors**

| Status | Reason |
|---|---|
| `401` | Missing or invalid token |

---

### PUT `/profile/me`

**Auth:** Bearer token

**Request Body** *(all fields optional; only provided fields are updated)*

```json
{
  "full_name":       "Priya R. Sharma",
  "phone":           "+91-9876543210",
  "college":         "IIT Bombay",
  "degree":          "B.Tech",
  "branch":          "Computer Science",
  "graduation_year": 2027,
  "skills":          ["Python", "SQL", "Data Structures", "Machine Learning"],
  "linkedin_url":    "https://linkedin.com/in/priyasharma",
  "github_url":      "https://github.com/priyasharma"
}
```

| Field | Type | Rules |
|---|---|---|
| `full_name` | string | 2–100 chars |
| `phone` | string | E.164 format |
| `college` | string | max 150 chars |
| `degree` | string | max 80 chars |
| `branch` | string | max 100 chars |
| `graduation_year` | integer | 2000–2035 |
| `skills` | array[string] | max 30 items, each ≤ 50 chars |
| `linkedin_url` | string | valid URL |
| `github_url` | string | valid URL |

**Success `200 OK`** — returns the full updated profile object (same shape as `GET /profile/me`).

**Errors**

| Status | Reason |
|---|---|
| `400` | Validation failure |
| `401` | Missing or invalid token |

---

### GET `/profile/goals`

**Auth:** Bearer token

**Request:** No body or query params.

**Success `200 OK`**

```json
{
  "user_id":          "usr_4f9a1b2c3d",
  "target_roles":     ["Software Engineer", "Data Analyst"],
  "target_companies": ["Google", "Microsoft", "Flipkart"],
  "placement_deadline": "2027-06-30",
  "preferred_locations": ["Bangalore", "Remote"],
  "expected_ctc_lpa": 20,
  "preparation_hours_per_week": 15,
  "updated_at": "2026-10-31T18:00:00Z"
}
```

**Errors**

| Status | Reason |
|---|---|
| `401` | Missing or invalid token |
| `404` | Goals not yet set |

---

### PUT `/profile/goals`

**Auth:** Bearer token

**Request Body** *(all fields optional)*

```json
{
  "target_roles":               ["Software Engineer", "Data Analyst"],
  "target_companies":           ["Google", "Microsoft", "Flipkart"],
  "placement_deadline":         "2027-06-30",
  "preferred_locations":        ["Bangalore", "Remote"],
  "expected_ctc_lpa":           20,
  "preparation_hours_per_week": 15
}
```

| Field | Type | Rules |
|---|---|---|
| `target_roles` | array[string] | max 10 items |
| `target_companies` | array[string] | max 20 items |
| `placement_deadline` | string | ISO 8601 date, must be in the future |
| `preferred_locations` | array[string] | max 10 items |
| `expected_ctc_lpa` | number | > 0 |
| `preparation_hours_per_week` | integer | 1–100 |

**Success `200 OK`** — returns the full updated goals object (same shape as `GET /profile/goals`).

**Errors**

| Status | Reason |
|---|---|
| `400` | Validation failure |
| `401` | Missing or invalid token |

---

## 3. Assessments

### GET `/assessments/categories`

**Auth:** Bearer token

**Request:** No body or query params.

**Success `200 OK`**

```json
{
  "categories": [
    {
      "category_id":   "cat_aptitude",
      "name":          "Aptitude",
      "description":   "Quantitative, logical reasoning, and verbal ability.",
      "subcategories": [
        { "subcategory_id": "sub_quant",   "name": "Quantitative Ability" },
        { "subcategory_id": "sub_logical", "name": "Logical Reasoning" },
        { "subcategory_id": "sub_verbal",  "name": "Verbal Ability" }
      ]
    },
    {
      "category_id":   "cat_technical",
      "name":          "Technical",
      "description":   "DSA, OS, DBMS, Networking, and more.",
      "subcategories": [
        { "subcategory_id": "sub_dsa",      "name": "Data Structures & Algorithms" },
        { "subcategory_id": "sub_os",       "name": "Operating Systems" },
        { "subcategory_id": "sub_dbms",     "name": "Database Management" },
        { "subcategory_id": "sub_networks", "name": "Computer Networks" },
        { "subcategory_id": "sub_oops",     "name": "OOP Concepts" }
      ]
    },
    {
      "category_id":   "cat_coding",
      "name":          "Coding",
      "description":   "Programming problem-solving in Python, Java, or C++.",
      "subcategories": [
        { "subcategory_id": "sub_easy",   "name": "Easy" },
        { "subcategory_id": "sub_medium", "name": "Medium" },
        { "subcategory_id": "sub_hard",   "name": "Hard" }
      ]
    }
  ]
}
```

**Errors**

| Status | Reason |
|---|---|
| `401` | Missing or invalid token |

---

### POST `/assessments/sessions/start`

**Auth:** Bearer token

**Request Body**

```json
{
  "category_id":        "cat_technical",
  "subcategory_id":     "sub_dsa",
  "num_questions":      20,
  "time_limit_minutes": 30
}
```

| Field | Type | Rules |
|---|---|---|
| `category_id` | string | required, must exist |
| `subcategory_id` | string | required, must belong to `category_id` |
| `num_questions` | integer | 5–50, required |
| `time_limit_minutes` | integer | 5–120, required |

**Success `201 Created`**

```json
{
  "session_id":         "ases_7d3b9e2f",
  "category":           "Technical",
  "subcategory":        "Data Structures & Algorithms",
  "num_questions":      20,
  "time_limit_minutes": 30,
  "status":             "in_progress",
  "started_at":         "2026-10-31T18:05:00Z",
  "expires_at":         "2026-10-31T18:35:00Z",
  "questions": [
    {
      "question_id": "q_001",
      "position":    1,
      "text":        "What is the time complexity of binary search?",
      "options": [
        { "option_id": "opt_a", "text": "O(n)" },
        { "option_id": "opt_b", "text": "O(log n)" },
        { "option_id": "opt_c", "text": "O(n log n)" },
        { "option_id": "opt_d", "text": "O(1)" }
      ]
    }
  ]
}
```

> Correct answers are **not** included in the response. They are revealed only in the result.

**Errors**

| Status | Reason |
|---|---|
| `400` | Invalid category/subcategory IDs or out-of-range values |
| `401` | Missing or invalid token |
| `409` | User already has an in-progress session for this subcategory |

---

### GET `/assessments/sessions/{session_id}`

**Auth:** Bearer token

**Path Params:** `session_id` — string

**Success `200 OK`**

```json
{
  "session_id":         "ases_7d3b9e2f",
  "category":           "Technical",
  "subcategory":        "Data Structures & Algorithms",
  "num_questions":      20,
  "time_limit_minutes": 30,
  "status":             "in_progress",
  "started_at":         "2026-10-31T18:05:00Z",
  "expires_at":         "2026-10-31T18:35:00Z",
  "questions_answered": 7,
  "questions": [
    {
      "question_id": "q_001",
      "position":    1,
      "text":        "What is the time complexity of binary search?",
      "options": [
        { "option_id": "opt_a", "text": "O(n)" },
        { "option_id": "opt_b", "text": "O(log n)" },
        { "option_id": "opt_c", "text": "O(n log n)" },
        { "option_id": "opt_d", "text": "O(1)" }
      ]
    }
  ]
}
```

**Errors**

| Status | Reason |
|---|---|
| `401` | Missing or invalid token |
| `403` | Session belongs to another user |
| `404` | Session not found |

---

### POST `/assessments/sessions/{session_id}/submit`

**Auth:** Bearer token

**Path Params:** `session_id` — string

**Request Body**

```json
{
  "answers": [
    { "question_id": "q_001", "selected_option_id": "opt_b" },
    { "question_id": "q_002", "selected_option_id": "opt_a" },
    { "question_id": "q_003", "selected_option_id": null }
  ]
}
```

| Field | Type | Rules |
|---|---|---|
| `answers` | array[object] | required, must include all question IDs of the session |
| `answers[].question_id` | string | required, must belong to session |
| `answers[].selected_option_id` | string \| null | null indicates unanswered |

**Success `200 OK`**

```json
{
  "session_id":   "ases_7d3b9e2f",
  "status":       "completed",
  "submitted_at": "2026-10-31T18:20:00Z",
  "message":      "Assessment submitted. Use GET /assessments/sessions/ases_7d3b9e2f/result to view your score."
}
```

**Errors**

| Status | Reason |
|---|---|
| `400` | Missing answers, unknown question IDs |
| `401` | Missing or invalid token |
| `403` | Session belongs to another user |
| `404` | Session not found |
| `409` | Session already submitted or expired |

---

### GET `/assessments/sessions/{session_id}/result`

**Auth:** Bearer token

**Path Params:** `session_id` — string

**Success `200 OK`**

```json
{
  "session_id":          "ases_7d3b9e2f",
  "category":            "Technical",
  "subcategory":         "Data Structures & Algorithms",
  "total_questions":     20,
  "attempted":           20,
  "correct":             14,
  "incorrect":           5,
  "unanswered":          1,
  "score_percentage":    70.0,
  "time_taken_seconds":  900,
  "submitted_at":        "2026-10-31T18:20:00Z",
  "question_results": [
    {
      "question_id":        "q_001",
      "text":               "What is the time complexity of binary search?",
      "selected_option_id": "opt_b",
      "correct_option_id":  "opt_b",
      "is_correct":         true,
      "explanation":        "Binary search halves the search space each step, yielding O(log n)."
    }
  ]
}
```

**Errors**

| Status | Reason |
|---|---|
| `401` | Missing or invalid token |
| `403` | Session belongs to another user |
| `404` | Session not found |
| `409` | Session not yet submitted |

---

### GET `/assessments/history`

**Auth:** Bearer token

**Query Params**

| Param | Type | Default | Description |
|---|---|---|---|
| `page` | integer | 1 | Page number |
| `limit` | integer | 10 | Items per page (max 50) |
| `category_id` | string | — | Filter by category |

**Success `200 OK`**

```json
{
  "total": 12,
  "page":  1,
  "limit": 10,
  "sessions": [
    {
      "session_id":       "ases_7d3b9e2f",
      "category":         "Technical",
      "subcategory":      "Data Structures & Algorithms",
      "score_percentage": 70.0,
      "correct":          14,
      "total_questions":  20,
      "status":           "completed",
      "submitted_at":     "2026-10-31T18:20:00Z"
    }
  ]
}
```

**Errors**

| Status | Reason |
|---|---|
| `400` | Invalid query params |
| `401` | Missing or invalid token |

---

## 4. Recommendations

### GET `/recommendations/latest`

**Auth:** Bearer token

**Request:** No body or query params.

**Success `200 OK`**

```json
{
  "generated_at": "2026-10-31T18:00:00Z",
  "based_on": {
    "assessment_sessions_analyzed": 8,
    "weak_areas":   ["Logical Reasoning", "Operating Systems"],
    "target_roles": ["Software Engineer", "Data Analyst"]
  },
  "recommendations": [
    {
      "recommendation_id": "rec_a1b2c3",
      "type":              "topic",
      "priority":          "high",
      "title":             "Strengthen OS Fundamentals",
      "description":       "Your last 3 OS assessments averaged 42%. Focus on process scheduling, memory management, and deadlocks.",
      "resources": [
        {
          "resource_id":     "res_os_01",
          "title":           "Operating Systems: Three Easy Pieces",
          "type":            "book",
          "url":             "https://pages.cs.wisc.edu/~remzi/OSTEP/",
          "estimated_hours": 10
        },
        {
          "resource_id":     "res_os_02",
          "title":           "OS Concepts – Gate Smashers",
          "type":            "video_playlist",
          "url":             "https://youtube.com/playlist?list=PLxCzCOWd3aiGz9donHRrE9I3Mwn6XdP8p",
          "estimated_hours": 5
        }
      ]
    },
    {
      "recommendation_id": "rec_d4e5f6",
      "type":              "practice",
      "priority":          "medium",
      "title":             "Daily DSA — Sliding Window Problems",
      "description":       "You scored well on arrays but struggled with window-based optimisation. Solve 10 medium-level problems.",
      "resources": [
        {
          "resource_id":     "res_dsa_01",
          "title":           "LeetCode – Sliding Window Tag",
          "type":            "practice_platform",
          "url":             "https://leetcode.com/tag/sliding-window/",
          "estimated_hours": 4
        }
      ]
    }
  ]
}
```

**Errors**

| Status | Reason |
|---|---|
| `401` | Missing or invalid token |
| `404` | No recommendations generated yet; call `POST /recommendations/generate` |

---

### POST `/recommendations/generate`

**Auth:** Bearer token

**Request Body:** Empty (`{}`) — triggers server-side AI generation using the user's latest assessment data and goals.

**Success `202 Accepted`**

```json
{
  "message":            "Recommendation generation started. Check GET /recommendations/latest in a few seconds.",
  "job_id":             "job_rec_9z8y7x",
  "estimated_seconds":  8
}
```

**Errors**

| Status | Reason |
|---|---|
| `401` | Missing or invalid token |
| `409` | A generation job is already running for this user |
| `422` | Insufficient data — user must complete at least one assessment first |

---

## 5. Chatbot

### GET `/chat/sessions`

**Auth:** Bearer token

**Query Params**

| Param | Type | Default | Description |
|---|---|---|---|
| `page` | integer | 1 | Page number |
| `limit` | integer | 10 | Items per page (max 50) |

**Success `200 OK`**

```json
{
  "total": 5,
  "page":  1,
  "limit": 10,
  "sessions": [
    {
      "session_id":      "chat_1a2b3c",
      "title":           "How to prepare for TCS NQT?",
      "message_count":   14,
      "created_at":      "2026-10-30T10:00:00Z",
      "last_message_at": "2026-10-30T10:22:00Z"
    }
  ]
}
```

**Errors**

| Status | Reason |
|---|---|
| `401` | Missing or invalid token |

---

### POST `/chat/sessions`

**Auth:** Bearer token

**Request Body**

```json
{
  "title": "How to prepare for TCS NQT?"
}
```

| Field | Type | Rules |
|---|---|---|
| `title` | string | optional, max 200 chars; auto-generated from first message if omitted |

**Success `201 Created`**

```json
{
  "session_id": "chat_1a2b3c",
  "title":      "How to prepare for TCS NQT?",
  "created_at": "2026-10-31T18:30:00Z"
}
```

**Errors**

| Status | Reason |
|---|---|
| `400` | Validation failure |
| `401` | Missing or invalid token |

---

### GET `/chat/sessions/{session_id}/messages`

**Auth:** Bearer token

**Path Params:** `session_id` — string

**Query Params**

| Param | Type | Default | Description |
|---|---|---|---|
| `page` | integer | 1 | Page number (oldest first) |
| `limit` | integer | 20 | Messages per page (max 100) |

**Success `200 OK`**

```json
{
  "session_id": "chat_1a2b3c",
  "total":      14,
  "page":       1,
  "limit":      20,
  "messages": [
    {
      "message_id": "msg_001",
      "role":       "user",
      "content":    "How should I prepare for TCS NQT?",
      "created_at": "2026-10-30T10:00:00Z"
    },
    {
      "message_id": "msg_002",
      "role":       "assistant",
      "content":    "TCS NQT has four sections: Numerical Ability, Verbal Ability, Reasoning Ability, and Programming Logic. Here is a structured 4-week plan...",
      "created_at": "2026-10-30T10:00:05Z"
    }
  ]
}
```

**Errors**

| Status | Reason |
|---|---|
| `401` | Missing or invalid token |
| `403` | Session belongs to another user |
| `404` | Session not found |

---

### POST `/chat/sessions/{session_id}/messages`

**Auth:** Bearer token

**Path Params:** `session_id` — string

**Request Body**

```json
{
  "content": "Which topics should I focus on for Logical Reasoning?"
}
```

| Field | Type | Rules |
|---|---|---|
| `content` | string | 1–4000 chars, required |

**Success `200 OK`**

```json
{
  "user_message": {
    "message_id": "msg_015",
    "role":       "user",
    "content":    "Which topics should I focus on for Logical Reasoning?",
    "created_at": "2026-10-31T18:31:00Z"
  },
  "assistant_message": {
    "message_id": "msg_016",
    "role":       "assistant",
    "content":    "For Logical Reasoning in placements, prioritise: 1) Blood Relations, 2) Seating Arrangements, 3) Syllogisms, 4) Coding-Decoding, and 5) Number Series. Based on your recent assessment, you scored lowest on Syllogisms — I recommend starting there.",
    "created_at": "2026-10-31T18:31:03Z"
  }
}
```

**Errors**

| Status | Reason |
|---|---|
| `400` | Content missing or exceeds length |
| `401` | Missing or invalid token |
| `403` | Session belongs to another user |
| `404` | Session not found |
| `503` | AI backend unavailable |

---

## 6. Resume

### POST `/resume/upload`

**Auth:** Bearer token  
**Content-Type:** `multipart/form-data`

**Form Fields**

| Field | Type | Rules |
|---|---|---|
| `file` | file | required; PDF or DOCX; max 5 MB |
| `target_role` | string | required; max 100 chars |

**Example (multipart fields)**

```
file:        <binary PDF content>
target_role: "Software Engineer"
```

**Success `202 Accepted`**

```json
{
  "resume_id":       "res_9k8j7h",
  "filename":        "priya_sharma_resume.pdf",
  "target_role":     "Software Engineer",
  "file_size_bytes": 184320,
  "status":          "processing",
  "uploaded_at":     "2026-10-31T18:40:00Z",
  "message":         "Resume uploaded. Analysis will be ready shortly. Poll GET /resume/res_9k8j7h/analysis."
}
```

**Errors**

| Status | Reason |
|---|---|
| `400` | Missing fields, unsupported file type |
| `401` | Missing or invalid token |
| `413` | File exceeds 5 MB |

---

### GET `/resume/list`

**Auth:** Bearer token

**Query Params**

| Param | Type | Default | Description |
|---|---|---|---|
| `page` | integer | 1 | Page number |
| `limit` | integer | 10 | Items per page (max 50) |

**Success `200 OK`**

```json
{
  "total": 3,
  "page":  1,
  "limit": 10,
  "resumes": [
    {
      "resume_id":       "res_9k8j7h",
      "filename":        "priya_sharma_resume.pdf",
      "target_role":     "Software Engineer",
      "analysis_status": "completed",
      "uploaded_at":     "2026-10-31T18:40:00Z"
    }
  ]
}
```

**Errors**

| Status | Reason |
|---|---|
| `401` | Missing or invalid token |

---

### GET `/resume/{resume_id}`

**Auth:** Bearer token

**Path Params:** `resume_id` — string

**Success `200 OK`**

```json
{
  "resume_id":       "res_9k8j7h",
  "filename":        "priya_sharma_resume.pdf",
  "target_role":     "Software Engineer",
  "file_size_bytes": 184320,
  "analysis_status": "completed",
  "uploaded_at":     "2026-10-31T18:40:00Z",
  "download_url":    "https://cdn.example.com/resumes/res_9k8j7h/priya_sharma_resume.pdf"
}
```

**Errors**

| Status | Reason |
|---|---|
| `401` | Missing or invalid token |
| `403` | Resume belongs to another user |
| `404` | Resume not found |

---

### GET `/resume/{resume_id}/analysis`

**Auth:** Bearer token

**Path Params:** `resume_id` — string

**Success `200 OK`**

```json
{
  "resume_id":     "res_9k8j7h",
  "target_role":   "Software Engineer",
  "status":        "completed",
  "analyzed_at":   "2026-10-31T18:41:30Z",
  "overall_score": 72,
  "sections": {
    "contact_info":   { "present": true,  "score": 100 },
    "summary":        { "present": true,  "score": 65,  "feedback": "Summary is generic. Tailor it to Software Engineering roles by highlighting specific tech stacks." },
    "skills":         { "present": true,  "score": 80,  "feedback": "Add proficiency levels. Missing keywords: Kubernetes, REST APIs, CI/CD." },
    "experience":     { "present": true,  "score": 70,  "feedback": "Use quantified achievements (e.g., 'Reduced API response time by 30%')." },
    "education":      { "present": true,  "score": 95 },
    "projects":       { "present": true,  "score": 75,  "feedback": "Link GitHub repos. Add tech stack tags to each project." },
    "certifications": { "present": false, "score": 0,   "feedback": "Add relevant certifications: AWS Cloud Practitioner, Google Associate Cloud Engineer." }
  },
  "missing_keywords": ["Kubernetes", "REST APIs", "CI/CD", "Microservices", "Docker"],
  "suggestions": [
    "Replace objective statement with a 3-line professional summary.",
    "Quantify all internship impact metrics.",
    "Add a dedicated 'Achievements' section for hackathon wins.",
    "Keep resume to 1 page for under 2 years of experience."
  ],
  "ats_compatibility_score": 68,
  "ats_notes": "ATS may reject due to table-based layout. Use single-column plain formatting."
}
```

> `status` may be `"processing"` if analysis is not yet complete. Retry after a few seconds.

**Errors**

| Status | Reason |
|---|---|
| `401` | Missing or invalid token |
| `403` | Resume belongs to another user |
| `404` | Resume not found |

---

### GET `/resume/{resume_id}/file`

**Auth:** Bearer token  
**Description:** Securely downloads the original uploaded resume file. Verified against student ownership; files are never exposed statically.

**Success `200 OK`**  
- **Headers:**  
  `Content-Type: application/pdf` (or `application/vnd.openxmlformats-officedocument.wordprocessingml.document`)  
  `Content-Disposition: attachment; filename="priya_sharma_resume.pdf"`  
- **Body:** Binary file stream (`FileResponse`).

**Errors**

| Status | Reason |
|---|---|
| `401` | Missing or invalid access token |
| `403` | Resume belongs to another student |
| `404` | Resume or file not found on disk |

---

## 7. Interview

### POST `/interview/sessions/start`

**Auth:** Bearer token

**Request Body**

```json
{
  "interview_type": "technical",
  "topic":          "Data Structures & Algorithms"
}
```

| Field | Type | Rules |
|---|---|---|
| `interview_type` | enum | `"technical"` \| `"hr"` — required |
| `topic` | string | required for `technical`; max 100 chars. Ignored for `hr`. |

**Success `201 Created`**

```json
{
  "session_id":     "int_5e6f7g8h",
  "interview_type": "technical",
  "topic":          "Data Structures & Algorithms",
  "status":         "in_progress",
  "started_at":     "2026-10-31T19:00:00Z",
  "first_question": {
    "question_id": "iq_001",
    "text":        "Can you explain the difference between a stack and a queue, and give a real-world use case for each?"
  }
}
```

**Errors**

| Status | Reason |
|---|---|
| `400` | Invalid `interview_type` or missing `topic` for technical |
| `401` | Missing or invalid token |
| `409` | User already has an in-progress interview session |

---

### GET `/interview/sessions/{session_id}`

**Auth:** Bearer token

**Path Params:** `session_id` — string

**Success `200 OK`**

```json
{
  "session_id":       "int_5e6f7g8h",
  "interview_type":   "technical",
  "topic":            "Data Structures & Algorithms",
  "status":           "in_progress",
  "started_at":       "2026-10-31T19:00:00Z",
  "questions_asked":  3,
  "current_question": {
    "question_id": "iq_004",
    "text":        "What is the difference between BFS and DFS? When would you prefer one over the other?"
  }
}
```

**Errors**

| Status | Reason |
|---|---|
| `401` | Missing or invalid token |
| `403` | Session belongs to another user |
| `404` | Session not found |

---

### POST `/interview/sessions/{session_id}/answer`

**Auth:** Bearer token

**Path Params:** `session_id` — string

**Request Body**

```json
{
  "question_id": "iq_004",
  "answer_text": "BFS uses a queue and explores level by level, while DFS uses a stack and goes deep first. I would use BFS for shortest path problems like finding the nearest metro station, and DFS for problems like detecting cycles in a graph."
}
```

| Field | Type | Rules |
|---|---|---|
| `question_id` | string | required, must match current question |
| `answer_text` | string | 10–5000 chars, required |

**Success `200 OK`**

```json
{
  "feedback": {
    "score":        8,
    "max_score":    10,
    "strengths":    ["Correct use of queue/stack distinction.", "Good real-world analogy for BFS."],
    "improvements": ["Mention time and space complexity of both algorithms.", "DFS cycle detection explanation could include directed vs undirected graphs."],
    "model_answer_hint": "Also consider: BFS guarantees shortest path in unweighted graphs; DFS is preferred for topological sorting and maze solving."
  },
  "next_question": {
    "question_id": "iq_005",
    "text":        "Explain how a hash table handles collisions. What are the trade-offs between chaining and open addressing?"
  },
  "session_status": "in_progress"
}
```

> When the session ends (after the configured number of questions), `next_question` is `null` and `session_status` is `"completed"`.

**Errors**

| Status | Reason |
|---|---|
| `400` | Answer too short, wrong `question_id` |
| `401` | Missing or invalid token |
| `403` | Session belongs to another user |
| `404` | Session not found |
| `409` | Session already ended |
| `503` | AI backend unavailable |

---

### POST `/interview/sessions/{session_id}/end`

**Auth:** Bearer token

**Path Params:** `session_id` — string

**Request Body:** Empty (`{}`)

**Success `200 OK`**

```json
{
  "session_id": "int_5e6f7g8h",
  "status":     "completed",
  "ended_at":   "2026-10-31T19:25:00Z",
  "message":    "Session ended. Report available at GET /interview/sessions/int_5e6f7g8h/report"
}
```

**Errors**

| Status | Reason |
|---|---|
| `401` | Missing or invalid token |
| `403` | Session belongs to another user |
| `404` | Session not found |
| `409` | Session already ended |

---

### GET `/interview/sessions/{session_id}/report`

**Auth:** Bearer token

**Path Params:** `session_id` — string

**Success `200 OK`**

```json
{
  "session_id":       "int_5e6f7g8h",
  "interview_type":   "technical",
  "topic":            "Data Structures & Algorithms",
  "started_at":       "2026-10-31T19:00:00Z",
  "ended_at":         "2026-10-31T19:25:00Z",
  "duration_minutes": 25,
  "total_questions":  5,
  "average_score":    7.4,
  "overall_rating":   "Good",
  "overall_feedback": "Strong conceptual understanding. Work on articulating time/space complexity trade-offs and edge cases in your answers.",
  "question_reports": [
    {
      "question_id":   "iq_001",
      "question_text": "Can you explain the difference between a stack and a queue...",
      "answer_text":   "A stack follows LIFO...",
      "score":         8,
      "max_score":     10,
      "strengths":     ["Clear LIFO/FIFO distinction."],
      "improvements":  ["Mention stack overflow conditions."]
    }
  ],
  "skill_breakdown": {
    "conceptual_clarity": 8.0,
    "communication":      7.0,
    "depth_of_knowledge": 6.5,
    "problem_solving":    8.0
  },
  "recommended_topics": ["Time Complexity Analysis", "Graph Algorithms", "Dynamic Programming"]
}
```

**Errors**

| Status | Reason |
|---|---|
| `401` | Missing or invalid token |
| `403` | Session belongs to another user |
| `404` | Session not found |
| `409` | Session still in progress |

---

### GET `/interview/history`

**Auth:** Bearer token

**Query Params**

| Param | Type | Default | Description |
|---|---|---|---|
| `page` | integer | 1 | Page number |
| `limit` | integer | 10 | Items per page (max 50) |
| `interview_type` | enum | — | Filter: `"technical"` \| `"hr"` |

**Success `200 OK`**

```json
{
  "total": 9,
  "page":  1,
  "limit": 10,
  "sessions": [
    {
      "session_id":      "int_5e6f7g8h",
      "interview_type":  "technical",
      "topic":           "Data Structures & Algorithms",
      "average_score":   7.4,
      "overall_rating":  "Good",
      "total_questions": 5,
      "ended_at":        "2026-10-31T19:25:00Z"
    }
  ]
}
```

**Errors**

| Status | Reason |
|---|---|
| `401` | Missing or invalid token |

---

## 8. Dashboard

### GET `/dashboard/summary`

**Auth:** Bearer token

**Request:** No body or query params.

**Success `200 OK`**

```json
{
  "user_id":         "usr_4f9a1b2c3d",
  "full_name":       "Priya Sharma",
  "readiness_score": 67,
  "assessments": {
    "total_completed":          12,
    "average_score_percentage": 65.3,
    "last_completed_at":        "2026-10-31T18:20:00Z"
  },
  "interviews": {
    "total_completed":   4,
    "average_score":     7.1,
    "last_completed_at": "2026-10-31T19:25:00Z"
  },
  "resumes": {
    "total_uploaded":       2,
    "latest_overall_score": 72,
    "latest_ats_score":     68
  },
  "chat": {
    "total_sessions": 5,
    "total_messages": 68
  },
  "recommendations": {
    "pending_high_priority": 2,
    "last_generated_at":     "2026-10-31T18:00:00Z"
  },
  "placement_deadline":  "2027-06-30",
  "days_until_deadline": 241
}
```

**Errors**

| Status | Reason |
|---|---|
| `401` | Missing or invalid token |

---

### GET `/dashboard/activity`

**Auth:** Bearer token

**Query Params**

| Param | Type | Default | Rules |
|---|---|---|---|
| `days` | integer | 30 | 1–365 |

**Success `200 OK`**

```json
{
  "period_days": 30,
  "from_date":   "2026-10-01",
  "to_date":     "2026-10-31",
  "daily_activity": [
    {
      "date":               "2026-10-31",
      "assessments_taken":  2,
      "interviews_done":    1,
      "chat_messages_sent": 8,
      "resumes_uploaded":   0,
      "active_minutes":     95
    },
    {
      "date":               "2026-10-30",
      "assessments_taken":  1,
      "interviews_done":    0,
      "chat_messages_sent": 6,
      "resumes_uploaded":   1,
      "active_minutes":     45
    }
  ],
  "totals": {
    "assessments_taken":    10,
    "interviews_done":      3,
    "chat_messages_sent":   52,
    "resumes_uploaded":     1,
    "total_active_minutes": 620
  }
}
```

**Errors**

| Status | Reason |
|---|---|
| `400` | `days` out of range |
| `401` | Missing or invalid token |

---

### GET `/dashboard/readiness-score`

**Auth:** Bearer token

**Request:** No body or query params.

**Success `200 OK`**

```json
{
  "overall_readiness_score": 67,
  "grade":       "B",
  "computed_at": "2026-10-31T19:30:00Z",
  "components": {
    "aptitude": {
      "score":                 70,
      "weight":                0.20,
      "weighted_contribution": 14.0,
      "sessions_counted":      4,
      "trend":                 "improving"
    },
    "technical_knowledge": {
      "score":                 62,
      "weight":                0.25,
      "weighted_contribution": 15.5,
      "sessions_counted":      6,
      "trend":                 "stable"
    },
    "coding": {
      "score":                 55,
      "weight":                0.20,
      "weighted_contribution": 11.0,
      "sessions_counted":      2,
      "trend":                 "declining"
    },
    "interview_performance": {
      "score":                 74,
      "weight":                0.25,
      "weighted_contribution": 18.5,
      "sessions_counted":      4,
      "trend":                 "improving"
    },
    "resume_quality": {
      "score":                 72,
      "weight":                0.10,
      "weighted_contribution": 7.2,
      "resumes_counted":       2,
      "trend":                 "stable"
    }
  },
  "improvement_tips": [
    "Complete at least 2 more coding assessments to improve the Coding component score.",
    "Address the 5 missing resume keywords flagged in your latest analysis."
  ]
}
```

> `trend` values: `"improving"` | `"stable"` | `"declining"`  
> `grade` scale: A (90–100), B (75–89), C (60–74), D (45–59), F (< 45)

**Errors**

| Status | Reason |
|---|---|
| `401` | Missing or invalid token |
| `422` | Insufficient activity data to compute score (minimum 1 assessment required) |

---

## 9. Common Error Responses

All error responses follow this envelope:

```json
{
  "error": {
    "code":    "VALIDATION_ERROR",
    "message": "Human-readable description of the error.",
    "details": [
      { "field": "email", "issue": "Invalid email format." }
    ]
  }
}
```

> `details` is present only for `400` validation errors.

### Standard HTTP Status Codes

| Code | Meaning |
|---|---|
| `200` | OK |
| `201` | Resource created |
| `202` | Accepted (async job started) |
| `400` | Bad request / validation error |
| `401` | Unauthenticated — missing, invalid, or expired token |
| `403` | Forbidden — authenticated but not authorised |
| `404` | Resource not found |
| `409` | Conflict — duplicate or invalid state transition |
| `413` | Payload too large |
| `415` | Unsupported media type (magic byte check failed) |
| `422` | Unprocessable — business rule violation |
| `429` | Too many requests (free-tier rate limit exceeded, retry later) |
| `503` | AI service temporarily unavailable |

### Error Codes Reference

| `error.code` | Applies to |
|---|---|
| `VALIDATION_ERROR` | 400 — field-level failures |
| `INVALID_CREDENTIALS` | 401 — login failure |
| `TOKEN_EXPIRED` | 401 — access or refresh token expired |
| `TOKEN_INVALID` | 401 — malformed or revoked token |
| `FORBIDDEN` | 403 — resource ownership mismatch |
| `NOT_FOUND` | 404 — resource does not exist |
| `DUPLICATE_EMAIL` | 409 — registration with existing email |
| `SESSION_CONFLICT` | 409 — active session already exists |
| `SESSION_ALREADY_ENDED` | 409 — submit/answer on a closed session |
| `FILE_TOO_LARGE` | 413 — upload exceeds size limit (max 5 MB) |
| `UNSUPPORTED_MEDIA_TYPE` | 415 — invalid MIME type or failed magic byte check |
| `INSUFFICIENT_DATA` | 422 — not enough activity to perform action |
| `RATE_LIMIT_EXCEEDED` | 429 — AI free-tier quota reached (includes `Retry-After` header) |
| `AI_UNAVAILABLE` | 503 — AI backend unreachable |
