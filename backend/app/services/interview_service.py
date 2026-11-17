from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.interview import InterviewSession, InterviewExchange
from app.models.activity import ActivityLog
from app.services.ai_service import get_ai_service, AIServiceError
from app.services.prompts import INTERVIEW_QUESTION_PROMPT, INTERVIEW_FEEDBACK_PROMPT

logger = logging.getLogger(__name__)

CURATED_QUESTION_BANK = {
    "technical": {
        "Data Structures & Algorithms": [
            "Explain how a Hash Map handles collisions. Compare Separate Chaining vs Open Addressing in terms of cache performance and time complexity.",
            "Given an unsorted array of integers, how would you find the longest consecutive elements sequence in O(n) time complexity? Explain your data structure choice.",
            "What is the difference between BFS and DFS graph traversals? When would you strictly choose BFS over DFS for solving a shortest path problem?",
            "Explain the difference between a Binary Search Tree (BST) and a self-balancing AVL Tree. What triggers single or double rotations?",
            "How would you find the median of a continuous data stream of integers with incoming numbers in real time? Describe the two-heap approach.",
            "Explain how Dynamic Programming differs from Divide and Conquer. What two key properties must a problem have to be solved with DP?",
            "Describe how to implement an LRU (Least Recently Used) cache with O(1) get and put operations using a doubly linked list and hash map.",
            "Given a directed graph, how do you detect whether a cycle exists using Kahn's Algorithm (Topological Sort)?",
            "What is a Trie (Prefix Tree), and why is it preferred over a Hash Table for autocomplete and dictionary prefix search queries?",
            "Explain the QuickSelect algorithm for finding the k-th smallest or largest element in an unsorted array in O(n) average time complexity.",
        ],
        "System Design": [
            "How would you design a URL shortening service like Bitly? What database schema and hashing strategy would you use to prevent duplicate shortened URLs?",
            "Explain the difference between horizontal and vertical scaling. How does a database read-replica setup help scale read-heavy applications?",
            "What is caching, and how do you handle cache invalidation? Compare Write-Through vs Write-Back cache strategies.",
            "How would you design a rate limiter to protect public API endpoints against denial-of-service abuse? Explain the Token Bucket algorithm.",
            "Explain the CAP theorem with concrete distributed database examples (e.g. Cassandra vs PostgreSQL).",
            "What is Database Sharding? How does consistent hashing prevent massive key remapping when adding or removing database nodes?",
            "How would you design a real-time Notification System that delivers push, email, and SMS notifications reliably with message queues?",
            "Compare monolithic architecture vs microservices architecture. What problems do API Gateways and service meshes solve?",
            "Explain the difference between synchronous REST APIs, asynchronous WebSockets, and Message Brokers (like Kafka/RabbitMQ).",
            "How would you design an idempotent payment processing system that guarantees no customer is double-charged during network drops?",
        ],
        "Database Management": [
            "Explain ACID properties in relational databases with a real-world banking transaction example.",
            "What is indexing, and how does a B-Tree index speed up SELECT queries? When can an index negatively affect performance?",
            "What is the difference between INNER JOIN, LEFT JOIN, and FULL OUTER JOIN? Give an example scenario for LEFT JOIN.",
            "Explain database normalization from 1NF to BCNF. What are the trade-offs of denormalization in high-read analytical databases?",
            "What are database transactions and savepoints? How do database write-ahead logging (WAL) and checkpointing ensure durability?",
            "Explain the difference between Optimistic Concurrency Control and Pessimistic Concurrency Control in relational databases.",
            "Compare SQL relational databases (PostgreSQL/MySQL) with NoSQL Document stores (MongoDB) and Key-Value stores (Redis). When would you choose each?",
            "What is a Deadlock in database systems, and how does the database engine detect and resolve deadlocks automatically?",
            "Explain the concept of query execution plans and EXPLAIN ANALYZE. How do you identify sequential table scans?",
            "What is Database Partitioning (horizontal vs vertical), and how does it improve query performance on tables with tens of millions of rows?",
        ],
        "Computer Networks & OS": [
            "Explain what happens under the hood from the moment you type 'https://www.google.com' into a browser until the webpage renders.",
            "What is the difference between a process and a thread? How does inter-process communication (IPC) work?",
            "Compare TCP and UDP protocols. Why does DNS or live video streaming typically prefer UDP over TCP?",
            "Explain Virtual Memory, Paging, and Page Faults. How does the Operating System handle a page fault?",
            "What is the role of CPU scheduling algorithms? Compare Round Robin, Shortest Job First (SJF), and Multi-Level Feedback Queue.",
            "Explain the TLS/SSL Handshake mechanism. How do asymmetric encryption and symmetric session keys work together to secure HTTPS?",
            "What are sockets in network programming, and how do non-blocking I/O event loops (like epoll or Node.js) handle thousands of concurrent connections?",
            "What is the difference between a mutex, a semaphore, and a spinlock? In what scenario would a spinlock be chosen?",
            "Explain the subnetting concept in IPv4. What is a subnet mask, and what is the difference between private and public IP addresses?",
            "What is the difference between symmetric and asymmetric multiprocessing, and how does CPU cache affinity impact multi-threaded performance?",
        ],
    },
    "hr": {
        "Behavioral": [
            "Tell me about a challenging technical project you worked on where you encountered an unexpected roadblock. How did you resolve it?",
            "Describe a situation where you had a disagreement with a team member or peer on a technical decision. How did you handle the situation?",
            "Where do you see yourself in the next 3 to 5 years, and how does joining our company align with your career trajectory?",
            "Can you describe a time when you received constructive criticism on your code or academic work? How did you respond and incorporate that feedback?",
            "Tell me about a time you had to learn a completely new programming language or tool under a tight deadline.",
            "Describe a situation where a project failed or didn't meet initial expectations. What were your key takeaways and what would you do differently?",
            "How do you manage stress and prioritize tasks when balancing academic coursework, semester exams, and campus placement preparation?",
            "Tell me about a time you took initiative to solve a problem or build a tool without being asked by a professor or team lead.",
            "Describe an experience where you had to explain a complex technical concept to a non-technical peer or client.",
            "Why do you want to work as a software engineer at our company specifically, rather than at other tech companies?",
        ],
        "Situational": [
            "If you are assigned a project using a tech stack you have never worked with before, and the deadline is in two weeks, how would you approach it?",
            "How do you prioritize multiple urgent tasks when facing tight academic or project deadlines?",
            "Why should we hire you over other candidates who have identical technical qualifications?",
            "If you notice a major security vulnerability or data loss bug in a peer's pull request right before a production release, what action would you take?",
            "If your team lead assigns you a task with vague requirements and is unavailable for questions, how do you proceed?",
            "Suppose you and your teammate both have completely different architectural approaches for the final year capstone project. How do you reach consensus?",
            "If a production database query runs slowly and causes service timeouts during peak campus recruitment traffic, how would you systematically diagnose it?",
            "How would you react if an interviewer points out an obvious mistake in your live coding solution on the whiteboard?",
            "If you realize halfway through an interview coding challenge that your initial approach has an O(n^2) complexity and won't pass constraints, what do you do?",
            "What questions do you have for us about our engineering culture, tech stack, and onboarding mentorship for campus hires?",
        ],
    },
}


def _get_curated_question(interview_type: str, topic: str, turn_order: int) -> str:
    """Retrieve fallback question from curated bank."""
    cat = CURATED_QUESTION_BANK.get(interview_type, CURATED_QUESTION_BANK["technical"])
    questions = cat.get(topic)
    if not questions:
        # Default fallback to first category in interview type
        first_key = next(iter(cat))
        questions = cat[first_key]

    index = (turn_order - 1) % len(questions)
    return questions[index]


def _heuristic_evaluate_answer(
    question: str,
    answer: str,
    interview_type: str,
    topic: str,
) -> dict[str, Any]:
    """Provide realistic, rigorous evaluation of answers when offline or AI call fails."""
    ans_clean = answer.strip()
    words = ans_clean.split()
    word_count = len(words)
    ans_lower = ans_clean.lower()

    # Evasive, empty, or non-answers
    evasive_phrases = [
        "don't know", "dont know", "no idea", "not sure", "have no clue",
        "skip", "pass", "cannot answer", "can't answer", "na", "no answer",
        "idk", "nothing", "what is this", "i forgot", "have not learned",
    ]
    is_evasive = any(p in ans_lower for p in evasive_phrases) or word_count < 4

    if is_evasive:
        return {
            "score": 2,
            "feedback": (
                f"The response was evasive or incomplete regarding {topic}. "
                "In technical campus recruitment rounds, evasive or non-answers severely hurt your rating. "
                "Even when unsure, explain the fundamental concepts or state your reasoning steps."
            ),
            "strengths": ["None observed - response was evasive or incomplete"],
            "improvements": [
                f"Master core concepts and definitions of {topic}",
                "Practice thinking aloud and attempting partial solutions rather than giving up",
            ],
            "model_answer": f"A comprehensive answer for this {topic} question should define the key mechanism, explain internal data structures or trade-offs, and cite concrete placement-relevant examples.",
        }

    # Extract non-stopword tokens from question to verify relevance
    stop_words = {
        "what", "how", "why", "when", "where", "which", "who", "whom", "whose",
        "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
        "do", "does", "did", "can", "could", "should", "would", "may", "might",
        "must", "the", "a", "an", "and", "or", "but", "if", "because", "as",
        "until", "while", "of", "at", "by", "for", "with", "about", "against",
        "between", "into", "through", "during", "before", "after", "above", "below",
        "to", "from", "up", "down", "in", "out", "on", "off", "over", "under",
        "again", "further", "then", "once", "here", "there", "all", "any", "both",
        "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not",
        "only", "own", "same", "so", "than", "too", "very", "explain", "describe",
        "compare", "difference", "give", "example", "given", "using", "your",
    }
    q_words = re.findall(r"\b[a-zA-Z]{3,}\b", question.lower())
    key_q_terms = [w for w in q_words if w not in stop_words]

    matched_terms = [t for t in key_q_terms if t in ans_lower]

    # If completely irrelevant (no matching keywords from question or topic)
    topic_words = re.findall(r"\b[a-zA-Z]{3,}\b", topic.lower())
    matched_topic = [t for t in topic_words if t in ans_lower]

    if not matched_terms and not matched_topic:
        return {
            "score": 3,
            "feedback": (
                f"The response does not address the core subject matter of the question ({topic}). "
                f"Expected to hear about technical aspects such as {', '.join(key_q_terms[:3]) if key_q_terms else topic}, "
                "but the answer lacked relevant technical concepts."
            ),
            "strengths": ["None observed - response did not address the question"],
            "improvements": [
                f"Directly target the technical terms asked in the prompt: {', '.join(key_q_terms[:3]) if key_q_terms else topic}",
                "Avoid off-topic filler text and structure your answer with clear points",
            ],
            "model_answer": f"An exemplary answer should directly focus on {', '.join(key_q_terms[:3]) if key_q_terms else topic}, detail technical mechanisms, and contrast alternative trade-offs.",
        }

    # Answer is relevant - score based on depth
    if word_count < 20:
        score = 5
        feedback = (
            "The answer touches on the correct subject but is too brief for an interview. "
            "Interviewers expect you to elaborate on the mechanism, complexities, and real-world considerations."
        )
        strengths = ["Identified the correct topic context"]
        improvements = [
            "Elaborate with concrete technical mechanisms and examples",
            "State time and space complexities or trade-offs explicitly",
        ]
    elif word_count < 45:
        score = 7
        feedback = (
            "Good concise answer covering fundamental concepts. To elevate to top-tier, "
            "mention architectural trade-offs, edge cases, and quantitative impact."
        )
        strengths = ["Accurate conceptual coverage", "Clear communication"]
        improvements = [
            "Discuss potential edge cases or failure modes",
            "Structure behavioral responses using STAR format",
        ]
    else:
        score = 8
        feedback = (
            "Thorough and well-reasoned response. Demonstrates solid technical foundation, "
            "structured explanation, and clear communication."
        )
        strengths = ["Detailed technical explanation", "Directly addressed the question with good depth"]
        improvements = [
            "Summarize the final outcome or metric impact in a crisp closing sentence",
        ]

    return {
        "score": score,
        "feedback": feedback,
        "strengths": strengths,
        "improvements": improvements,
        "model_answer": f"An exemplary response clearly defines {key_q_terms[0] if key_q_terms else topic}, outlines the operational workflow, and provides time/space complexity or quantitative results.",
    }


async def start_interview(
    db: AsyncSession,
    user_id: str,
    interview_type: str,
    topic: str,
) -> InterviewSession:
    """Initialize a mock interview session and generate the first question."""
    session = InterviewSession(
        user_id=user_id,
        interview_type=interview_type.lower(),
        topic=topic.strip(),
        status="in_progress",
    )
    db.add(session)
    await db.flush()

    # Generate Question 1
    ai_service = get_ai_service()
    question_text = ""
    prompt = INTERVIEW_QUESTION_PROMPT.format(
        interview_type=session.interview_type,
        topic=session.topic,
        difficulty="medium",
    )
    try:
        data = await ai_service.generate_structured(prompt)
        question_text = data.get("question", "")
    except (AIServiceError, Exception) as e:
        logger.warning("AI generation failed for interview question: %s. Using curated question.", str(e))

    if not question_text:
        question_text = _get_curated_question(session.interview_type, session.topic, turn_order=1)

    first_turn = InterviewExchange(
        session_id=session.id,
        turn_order=1,
        question=question_text,
    )
    db.add(first_turn)
    await db.commit()

    return await get_interview_session(db, user_id, session.id) or session


async def get_interview_session(
    db: AsyncSession,
    user_id: str,
    session_id: str,
) -> InterviewSession | None:
    """Fetch session with all exchanges."""
    result = await db.execute(
        select(InterviewSession)
        .where(InterviewSession.id == session_id, InterviewSession.user_id == user_id)
        .options(selectinload(InterviewSession.exchanges))
    )
    return result.scalar_one_or_none()


async def get_interview_history(db: AsyncSession, user_id: str) -> list[InterviewSession]:
    """Retrieve user's past interviews."""
    result = await db.execute(
        select(InterviewSession)
        .where(InterviewSession.user_id == user_id)
        .order_by(InterviewSession.started_at.desc())
    )
    return list(result.scalars().all())


async def submit_answer(
    db: AsyncSession,
    user_id: str,
    session_id: str,
    answer: str,
) -> dict[str, Any]:
    """Evaluate candidate answer, persist feedback, and issue next question or complete interview."""
    session = await get_interview_session(db, user_id, session_id)
    if not session:
        raise ValueError("Interview session not found")
    if session.status == "completed":
        raise ValueError("Interview session has already concluded")

    # Find active exchange
    active_turn: InterviewExchange | None = None
    for ex in session.exchanges:
        if ex.student_answer is None:
            active_turn = ex
            break

    if not active_turn:
        raise ValueError("No pending question to answer in this session")

    active_turn.student_answer = answer.strip()

    # AI Evaluation
    ai_service = get_ai_service()
    feedback_data: dict[str, Any] = {}
    prompt = INTERVIEW_FEEDBACK_PROMPT.format(
        question=active_turn.question,
        answer=answer,
        expected_points=f"Technical accuracy regarding {session.topic}, direct relevance to the question, explanation of mechanisms and trade-offs",
    )
    try:
        feedback_data = await ai_service.generate_structured(prompt)
    except (AIServiceError, Exception) as e:
        logger.warning("AI evaluation failed: %s. Using heuristic evaluation.", str(e))

    raw_score = feedback_data.get("score")
    if isinstance(raw_score, int) and 1 <= raw_score <= 10 and feedback_data.get("feedback"):
        score = raw_score
        feedback = str(feedback_data["feedback"])
        strengths = list(feedback_data.get("strengths") or ["Clear response formulation"])
        improvements = list(feedback_data.get("improvements") or ["Deepen coverage of edge cases and trade-offs"])
        model_answer = str(feedback_data.get("model_answer") or "An exemplary answer should state the definition clearly and explain core mechanisms.")
    else:
        # Fallback to realistic heuristic evaluation
        heuristic = _heuristic_evaluate_answer(
            question=active_turn.question,
            answer=answer,
            interview_type=session.interview_type,
            topic=session.topic,
        )
        score = heuristic["score"]
        feedback = heuristic["feedback"]
        strengths = heuristic["strengths"]
        improvements = heuristic["improvements"]
        model_answer = heuristic["model_answer"]

    active_turn.score = score
    active_turn.ai_feedback = feedback

    # Total questions per session: 10
    is_complete = active_turn.turn_order >= 10
    next_question: str | None = None
    overall_score: int | None = None
    overall_feedback: str | None = None

    if not is_complete:
        next_turn_order = active_turn.turn_order + 1
        # Generate next question
        next_q_prompt = INTERVIEW_QUESTION_PROMPT.format(
            interview_type=session.interview_type,
            topic=session.topic,
            difficulty="medium",
        )
        try:
            next_q_data = await ai_service.generate_structured(next_q_prompt)
            next_question = next_q_data.get("question")
        except Exception:
            next_question = None

        if not next_question:
            next_question = _get_curated_question(session.interview_type, session.topic, turn_order=next_turn_order)

        next_exchange = InterviewExchange(
            session_id=session.id,
            turn_order=next_turn_order,
            question=next_question,
        )
        db.add(next_exchange)
    else:
        # Mark session complete
        session.status = "completed"
        session.completed_at = datetime.now(timezone.utc)
        all_scores = [ex.score for ex in session.exchanges if ex.score is not None]
        all_scores.append(score)
        # Scale 1-10 to 0-100
        avg_10 = sum(all_scores) / len(all_scores)
        overall_score = int(round(avg_10 * 10))
        session.score = overall_score

        if overall_score >= 80:
            overall_feedback = "Outstanding performance! You showed strong technical depth, communication, and structured thinking."
        elif overall_score >= 60:
            overall_feedback = "Good foundation. Deepen your explanation of edge cases, time/space complexity, and concise delivery."
        else:
            overall_feedback = "Needs practice. Focus on revising fundamental concepts and practicing mock responses with structured points."
        session.overall_feedback = overall_feedback

        # Log activity
        activity = ActivityLog(
            user_id=user_id,
            activity_type="interview_completed",
            description=f"Completed {session.interview_type.upper()} mock interview on {session.topic} with score {overall_score}%",
            metadata_json={"session_id": session.id, "score": overall_score},
        )
        db.add(activity)

    await db.commit()

    return {
        "turn_order": active_turn.turn_order,
        "score": score,
        "feedback": feedback,
        "strengths": strengths,
        "improvements": improvements,
        "model_answer": model_answer,
        "next_question": next_question,
        "is_complete": is_complete,
        "overall_score": overall_score,
        "overall_feedback": overall_feedback,
    }
