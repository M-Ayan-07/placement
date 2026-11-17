from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_chat_lifecycle(client: AsyncClient):
    # Register and login user
    await client.post(
        "/api/v1/auth/register",
        json={"email": "chatuser@example.com", "password": "Password123!", "full_name": "Chat Candidate"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "chatuser@example.com", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create chat session
    res = await client.post(
        "/api/v1/chat/sessions",
        headers=headers,
        json={"title": "Placement Doubts on System Design"},
    )
    assert res.status_code == 201
    session_data = res.json()
    session_id = session_data["id"]
    assert session_data["title"] == "Placement Doubts on System Design"
    assert len(session_data["messages"]) >= 1
    assert session_data["messages"][0]["role"] == "assistant"

    # 2. List sessions
    list_res = await client.get("/api/v1/chat/sessions", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 3. Send message
    msg_res = await client.post(
        f"/api/v1/chat/sessions/{session_id}/messages",
        headers=headers,
        json={"content": "What are the key DSA topics I must master for Amazon?"},
    )
    assert msg_res.status_code == 200
    reply = msg_res.json()
    assert reply["user_message"]["role"] == "user"
    assert reply["assistant_message"]["role"] == "assistant"
    assert len(reply["assistant_message"]["content"]) > 10

    # 4. Fetch full session details
    detail_res = await client.get(f"/api/v1/chat/sessions/{session_id}", headers=headers)
    assert detail_res.status_code == 200
    assert len(detail_res.json()["messages"]) >= 3


@pytest.mark.asyncio
async def test_interview_turn_progression(client: AsyncClient):
    # Register and login user
    await client.post(
        "/api/v1/auth/register",
        json={"email": "mockuser@example.com", "password": "Password123!", "full_name": "Mock Candidate"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "mockuser@example.com", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Start interview
    start_res = await client.post(
        "/api/v1/interview/start",
        headers=headers,
        json={"interview_type": "technical", "topic": "Data Structures & Algorithms"},
    )
    assert start_res.status_code == 201
    data = start_res.json()
    session_id = data["id"]
    assert data["status"] == "in_progress"
    assert len(data["exchanges"]) == 1
    assert data["exchanges"][0]["turn_order"] == 1
    assert len(data["exchanges"][0]["question"]) > 5

    # 2. Submit Turn 1 answer
    ans1_res = await client.post(
        f"/api/v1/interview/{session_id}/answer",
        headers=headers,
        json={
            "answer": "A hash map uses a hashing function to map keys to array buckets. Collisions can be resolved via separate chaining with linked lists or open addressing with linear probing."
        },
    )
    assert ans1_res.status_code == 200
    ans1 = ans1_res.json()
    assert ans1["is_complete"] is False
    assert ans1["turn_order"] == 1
    assert ans1["score"] >= 1
    assert ans1["next_question"] is not None

    # 3. Submit Turn 2 through 9
    for turn in range(2, 10):
        ans_turn_res = await client.post(
            f"/api/v1/interview/{session_id}/answer",
            headers=headers,
            json={
                "answer": f"For turn {turn}, we evaluate the problem constraints, use appropriate data structures, and state optimal time and space complexity."
            },
        )
        assert ans_turn_res.status_code == 200
        ans_turn = ans_turn_res.json()
        assert ans_turn["is_complete"] is False
        assert ans_turn["turn_order"] == turn

    # 4. Submit Turn 10 answer (concluding the interview)
    ans10_res = await client.post(
        f"/api/v1/interview/{session_id}/answer",
        headers=headers,
        json={
            "answer": "BFS traverses level by level using a FIFO queue, guaranteeing the shortest path in unweighted graphs. DFS explores deep paths first using recursion or stack."
        },
    )
    assert ans10_res.status_code == 200
    ans10 = ans10_res.json()
    assert ans10["is_complete"] is True
    assert ans10["overall_score"] is not None
    assert ans10["overall_feedback"] is not None

    # 5. Verify session status is completed with 10 turns
    session_res = await client.get(f"/api/v1/interview/{session_id}", headers=headers)
    assert session_res.status_code == 200
    session_final = session_res.json()
    assert session_final["status"] == "completed"
    assert session_final["score"] == ans10["overall_score"]
    assert len(session_final["exchanges"]) == 10


@pytest.mark.asyncio
async def test_interview_cross_user_isolation(client: AsyncClient):
    # Register Candidate A
    await client.post(
        "/api/v1/auth/register",
        json={"email": "canda@example.com", "password": "Password123!", "full_name": "Candidate A"},
    )
    l1 = await client.post(
        "/api/v1/auth/login",
        json={"email": "canda@example.com", "password": "Password123!"},
    )
    t1 = l1.json()["access_token"]
    h1 = {"Authorization": f"Bearer {t1}"}

    # Register Candidate B
    await client.post(
        "/api/v1/auth/register",
        json={"email": "candb@example.com", "password": "Password123!", "full_name": "Candidate B"},
    )
    l2 = await client.post(
        "/api/v1/auth/login",
        json={"email": "candb@example.com", "password": "Password123!"},
    )
    t2 = l2.json()["access_token"]
    h2 = {"Authorization": f"Bearer {t2}"}

    # Start interview as Candidate A
    res = await client.post(
        "/api/v1/interview/start",
        headers=h1,
        json={"interview_type": "hr", "topic": "Behavioral"},
    )
    session_id = res.json()["id"]

    # Candidate B tries to access Candidate A's interview -> 404
    cross_res = await client.get(f"/api/v1/interview/{session_id}", headers=h2)
    assert cross_res.status_code == 404


@pytest.mark.asyncio
async def test_interview_low_score_for_irrelevant_or_evasive_answer(client: AsyncClient):
    """Verify that wrong, off-topic, or evasive answers receive low scores (<= 3) and constructive feedback."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "evaltest@example.com", "password": "Password123!", "full_name": "Evaluation Candidate"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "evaltest@example.com", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Start technical interview on DBMS
    start_res = await client.post(
        "/api/v1/interview/start",
        headers=headers,
        json={"interview_type": "technical", "topic": "Database Management"},
    )
    session_id = start_res.json()["id"]

    # Submit an evasive answer
    evasive_res = await client.post(
        f"/api/v1/interview/{session_id}/answer",
        headers=headers,
        json={"answer": "I don't know, skip this question please."},
    )
    assert evasive_res.status_code == 200
    evasive_data = evasive_res.json()
    assert evasive_data["score"] <= 3
    assert "evasive" in evasive_data["feedback"].lower() or "unable" in evasive_data["feedback"].lower()

