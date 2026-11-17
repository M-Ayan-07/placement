from __future__ import annotations

import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat import ChatMessage, ChatSession
from app.models.activity import ActivityLog
from app.services.ai_service import get_ai_service, AIServiceError
from app.services.prompts import CHATBOT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

def _get_dynamic_coaching_response(message: str, history: list[ChatMessage] | None = None) -> str:
    """Generate dynamic, context-aware coaching response tailored to student's exact query and history."""
    lower = message.lower().strip()

    # Determine conversational context from recent history if available
    recent_context = ""
    if history:
        for past_msg in reversed(history[-4:]):
            if past_msg.role == "user":
                recent_context += f" {past_msg.content.lower()}"

    combined_context = f"{recent_context} {lower}"

    # 1. Company-specific strategies
    if any(c in lower for c in ["google", "meta", "microsoft", "amazon", "apple", "faang", "tier-1", "tier 1"]):
        return (
            "### Strategy for Tier-1 Product Companies (FAANG / Big Tech)\n\n"
            "For top product companies, the hiring bar centers on algorithmic problem solving, clean code, and deep fundamentals:\n\n"
            "1. **Online Assessment (OA)**: 2-3 medium/hard problems (frequently LeetCode Medium/Hard). Focus heavily on Graphs (BFS/DFS, Dijkstra), Dynamic Programming, and Heap/PriorityQueue.\n"
            "2. **Technical Rounds (2-3 rounds)**:\n"
            "   - **Think Aloud**: Communicate your thought process before writing a single line of code.\n"
            "   - **Clarify Constraints**: Ask about input sizes, duplicate values, and negative numbers.\n"
            "   - **State Complexity**: Always state Big-O Time and Space complexities upfront, and explore trade-offs.\n"
            "3. **Projects & Deep Dives**: Be prepared to explain architectural choices, scaling bottlenecks, and testing strategies for your top project.\n\n"
            "**Recommended Next Step**: Solve 3-4 graph and DP problems under a 30-minute timed constraint, and practice dry-running edge cases on paper."
        )

    if any(c in lower for c in ["tcs", "infosys", "wipro", "cognizant", "accenture", "capgemini", "service based", "mass recruiter"]):
        return (
            "### Strategy for Service-Based IT Companies (TCS, Infosys, Wipro, Accenture)\n\n"
            "Recruitment for these companies typically follows a high-volume structured funnel:\n\n"
            "1. **Round 1 — Cognitive & Aptitude Test**:\n"
            "   - Quantitative Aptitude (Percentages, Profit/Loss, Time & Work, Speed & Distance).\n"
            "   - Logical Reasoning (Blood Relations, Coding-Decoding, Seating Arrangements).\n"
            "   - Verbal Ability (Reading Comprehension, Error Spotting).\n"
            "2. **Round 2 — Technical Assessment**:\n"
            "   - Basic to intermediate programming (Strings, Arrays, Matrix operations, Palindromes, Sorting).\n"
            "   - Core CS MCQs (DBMS SQL queries, OOP concepts in Java/C++/Python, basic OS).\n"
            "3. **Round 3 — Technical & HR Interview**:\n"
            "   - Fundamental OOP principles (Polymorphism, Inheritance, Encapsulation, Abstraction).\n"
            "   - Final year project explanation in simple, confident terms.\n"
            "   - Willingness to relocate and work in shifts (always answer affirmatively).\n\n"
            "**Recommended Action**: Dedicate 45 minutes daily to quantitative aptitude on IndiaBIX or our Assessments section, and revise SQL queries and OOP definitions."
        )

    # 2. DSA & Coding patterns
    if any(k in lower for k in ["dp", "dynamic programming", "knapsack", "memoization", "tabulation"]):
        return (
            "### Mastering Dynamic Programming (DP) for Placements\n\n"
            "Dynamic Programming problems often intimidate students, but 90% of interview DP problems fall into standard patterns:\n\n"
            "1. **0/1 Knapsack & Unbounded Knapsack** (Subset Sum, Equal Partition, Coin Change).\n"
            "2. **Longest Common Subsequence (LCS)** (Edit Distance, Longest Palindromic Subsequence).\n"
            "3. **Longest Increasing Subsequence (LIS)** (O(n log n) with binary search).\n"
            "4. **Matrix / Grid DP** (Unique Paths, Minimum Path Sum).\n\n"
            "**The 4-Step DP Framework**:\n"
            "- Step 1: Write the brute force recursive solution.\n"
            "- Step 2: Identify overlapping subproblems and memoize with a hash map or 2D array (Top-Down).\n"
            "- Step 3: Convert to iterative table filling (Bottom-Up) if required for O(1) space optimization.\n"
            "- Step 4: Trace the recurrence relation explicitly when explaining to the interviewer.\n\n"
            "Would you like to walk through an example recurrence relation like Coin Change or Longest Common Subsequence?"
        )

    if any(k in lower for k in ["graph", "bfs", "dfs", "dijkstra", "topological", "cycle"]):
        return (
            "### Graph Traversal & Algorithm Patterns\n\n"
            "Graphs are a favorite topic in technical rounds. Focus on these core implementations:\n\n"
            "1. **BFS (Breadth-First Search)**: Ideal for unweighted shortest path problems and level-order processing. Always use a `Queue` and a `visited` set.\n"
            "2. **DFS (Depth-First Search)**: Ideal for path exploration, connected components, and flood fill. Implemented using recursion or an explicit stack.\n"
            "3. **Cycle Detection**:\n"
            "   - Undirected graph: BFS/DFS with parent tracking, or Disjoint Set Union (DSU).\n"
            "   - Directed graph: DFS with 3-color states (visiting, visited), or Kahn's Algorithm (in-degree count).\n"
            "4. **Topological Sort**: Crucial for dependency resolution and course scheduling problems.\n"
            "5. **Dijkstra's Algorithm**: For shortest paths in weighted non-negative graphs using `PriorityQueue` (O((V + E) log V)).\n\n"
            "**Interview Tip**: When an interview question mentions 'relationships', 'dependencies', or 'networks', immediately consider modeling it as a graph."
        )

    if any(k in lower for k in ["tree", "bst", "binary tree", "binary search tree", "inorder", "level order"]):
        return (
            "### Tree & BST Patterns for Interviews\n\n"
            "Tree questions test recursion and hierarchical thinking. Master these core techniques:\n\n"
            "1. **DFS Traversals**: Inorder (Left-Root-Right), Preorder (Root-Left-Right), Postorder (Left-Right-Root). Remember: Inorder traversal of a valid BST always yields sorted elements!\n"
            "2. **BFS / Level Order**: Use a queue; process nodes level by level (size = queue.length).\n"
            "3. **Common Interview Problems**:\n"
            "   - Maximum Depth / Diameter of Binary Tree\n"
            "   - Lowest Common Ancestor (LCA) in BT and BST\n"
            "   - Validate Binary Search Tree (use min/max bounds, not just local node comparisons)\n"
            "   - Invert / Flip Binary Tree\n\n"
            "What specific tree problem or concept would you like to practice?"
        )

    if any(k in lower for k in ["dsa", "leetcode", "algorithm", "data structure", "coding"]):
        return (
            "### High-Yield DSA Placement Roadmap\n\n"
            "To maximize interview conversion, focus on pattern-based learning rather than memorizing individual problems:\n\n"
            "1. **Array & Two Pointers**: Sliding Window, Two Sum variation, Dutch National Flag.\n"
            "2. **Linked Lists**: Fast & Slow Pointers (cycle detection, middle node), reversal in groups.\n"
            "3. **Stacks & Queues**: Monotonic Stack (Next Greater Element), valid parentheses.\n"
            "4. **Binary Search**: Search in Rotated Sorted Array, finding boundaries (lower/upper bound).\n"
            "5. **Trees & Graphs**: BFS/DFS, LCA, cycle detection, Topological Sort.\n"
            "6. **Dynamic Programming**: 0/1 Knapsack, LCS, LIS.\n\n"
            "**Daily Routine**: Aim for 2 LeetCode Mediums daily. Spend max 25 minutes trying to solve on your own before reading editorial hints."
        )

    # 3. Resume & ATS Analysis
    if any(k in lower for k in ["resume", "cv", "ats", "score", "format", "bullet"]):
        return (
            "### High-Impact Resume & ATS Optimization\n\n"
            "To ensure your resume passes automated ATS filters and impresses hiring managers:\n\n"
            "1. **The Google XYZ Formula**: Frame every bullet point as: *'Accomplished [X], as measured by [Y], by doing [Z]'*.\n"
            "   - *Weak*: 'Built an e-commerce website using React and Node.js.'\n"
            "   - *Strong*: 'Engineered a full-stack e-commerce portal with React and Node.js, reducing API latency by 35% through Redis caching.'\n"
            "2. **Format & Length**: Keep strictly to 1 page for students/fresher roles. Use clean single-column layouts with standard font sizes (10-11pt).\n"
            "3. **Technical Skills Taxonomy**: Group clearly under *Languages*, *Frameworks & Libraries*, *Databases*, and *Developer Tools*.\n"
            "4. **Links**: Include clickable hyperlinks to your GitHub profile, LinkedIn, and live project demos.\n\n"
            "You can upload your CV directly to our **Resume Scanner** page to get an immediate ATS score and role-specific keyword analysis!"
        )

    # 4. HR, Behavioral & Interview Strategy
    if any(k in lower for k in ["tell me about yourself", "introduce", "self intro"]):
        return (
            "### Perfecting 'Tell Me About Yourself' (90-Second Pitch)\n\n"
            "This question sets the tone for your entire interview. Structure it into 3 clear acts:\n\n"
            "1. **Act 1: Present (30s)**: Your current education, branch, college, and primary technical passion (e.g. *'I am a final year Computer Science student at XYZ, specializing in full-stack web systems and distributed services.'*)\n"
            "2. **Act 2: Past (30s)**: Your key hands-on experience, proudest project, or internship (e.g. *'Recently, I built a high-throughput placement portal that helped 300+ students track mock interviews.'*)\n"
            "3. **Act 3: Future (30s)**: Why you are excited about this company and specific role (e.g. *'I have been following your engineering team's work on cloud infrastructure and am eager to contribute as an SDE-1.'*)\n\n"
            "**Key Tip**: Never repeat your entire resume line-by-line. Highlight your strengths and guide the interviewer toward topics you excel in!"
        )

    if any(k in lower for k in ["star", "behavioral", "hr round", "conflict", "weakness"]):
        return (
            "### Behavioral Interview Mastery with the STAR Framework\n\n"
            "In HR and managerial rounds, answering with the STAR method ensures concrete, credible answers:\n\n"
            "- **Situation (20%)**: Set the context briefly (project name, team size, deadline).\n"
            "- **Task (10%)**: Explain the specific challenge or objective you were responsible for.\n"
            "- **Action (50%)**: Detail the technical and collaborative steps **you** personally took. Use 'I' instead of 'we'.\n"
            "- **Result (20%)**: Quantify the positive outcome (e.g., 'reduced load time by 40%', 'delivered 2 days ahead of schedule').\n\n"
            "**Common Behavioral Questions to Prepare**:\n"
            "1. Tell me about a time you faced a difficult bug under a tight deadline.\n"
            "2. Describe a technical disagreement with a peer and how you reached consensus.\n"
            "3. What is your biggest weakness? (Choose a real operational trait and explain how you are proactively mitigating it)."
        )

    # 5. Core CS Subjects (DBMS, OS, Networks, System Design)
    if any(k in lower for k in ["dbms", "sql", "database", "acid", "index", "normalization"]):
        return (
            "### Core DBMS & SQL Placement Essentials\n\n"
            "Recruiters heavily test relational databases during technical screening:\n\n"
            "1. **ACID Properties**: Atomicity (all-or-nothing), Consistency (integrity constraints), Isolation (concurrency levels), Durability (write-ahead log).\n"
            "2. **Indexing & B-Trees**: How B-Tree indexes convert O(N) table scans into O(log N) lookups. When NOT to index (small tables, high-write frequency).\n"
            "3. **SQL Queries to Practice**:\n"
            "   - Finding Nth highest salary (`DENSE_RANK()` or `LIMIT / OFFSET`).\n"
            "   - Joins: INNER, LEFT, RIGHT, and FULL OUTER joins with NULL handling.\n"
            "   - Group By with `HAVING` vs `WHERE`.\n"
            "4. **Normalization**: 1NF (atomic values), 2NF (no partial dependency), 3NF (no transitive dependency), and BCNF.\n\n"
            "Practice writing actual SQL queries on our Assessments module to test your query speed!"
        )

    if any(k in lower for k in ["os", "operating system", "process", "thread", "deadlock", "paging"]):
        return (
            "### Operating Systems Key Concepts for Placements\n\n"
            "Master these 4 recurring OS topics:\n\n"
            "1. **Processes vs Threads**: A process has its own address space, PCB, and open files; threads share address space and heap but have independent stacks and registers.\n"
            "2. **Deadlocks**: The 4 Coffman conditions (Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait). Explain Banker's algorithm and prevention techniques.\n"
            "3. **CPU Scheduling**: Round Robin (time quantum trade-offs), SJF, Priority scheduling.\n"
            "4. **Virtual Memory**: Paging, Page Fault handling, Thrashing, and LRU page replacement algorithm.\n\n"
            "Be prepared to code an LRU Cache or explain inter-process communication (IPC) mechanisms like pipes and shared memory."
        )

    if any(k in lower for k in ["system design", "microservice", "cache", "load balancer", "scalability"]):
        return (
            "### System Design Primer for Entry-Level Interviews\n\n"
            "For campus roles, interviewers look for foundational architectural understanding rather than multi-datacenter complexity:\n\n"
            "1. **Vertical vs Horizontal Scaling**: Adding CPU/RAM to a single box vs adding multiple server nodes behind a Load Balancer.\n"
            "2. **Caching**: In-memory caches (Redis/Memcached). Cache invalidation strategies (Write-Through, Write-Back, Cache-Aside).\n"
            "3. **Database Scaling**: Read replicas for read-heavy workloads, and Sharding (horizontal partitioning) for massive datasets.\n"
            "4. **CAP Theorem**: In a distributed system with Network Partitions (P), you must choose between Consistency (C) and Availability (A).\n\n"
            "**Classic Problems**: Design a URL Shortener (Bitly), a Rate Limiter (Token Bucket), or a Notification System."
        )

    # 6. Context-Aware Follow-up or General Coaching
    if any(f in lower for f in ["more", "continue", "example", "explain", "detail", "how to start", "roadmap"]):
        if "dsa" in combined_context or "code" in combined_context:
            return (
                "### Detailed Action Plan for Coding & Problem Solving\n\n"
                "Here is an actionable 3-week sprint to boost your problem-solving speed:\n\n"
                "- **Week 1 (Arrays & Pointers)**: 15 problems on Two Pointers, Sliding Window, and Prefix Sums.\n"
                "- **Week 2 (Trees & Graphs)**: 15 problems on DFS, BFS, Binary Tree level order, and Lowest Common Ancestor.\n"
                "- **Week 3 (DP & Greedy)**: 10 problems on 0/1 Knapsack, Coin Change, and Interval Scheduling.\n\n"
                "Always write clean code with meaningful variable names and handle edge cases (empty array, null pointers, single elements) before submitting."
            )
        elif "interview" in combined_context or "hr" in combined_context:
            return (
                "### Next Step in Interview Preparation\n\n"
                "To build fluency, start a session in our **Mock Interview** tab:\n"
                "1. Select a Technical or HR topic.\n"
                "2. Use the voice speech-to-text feature to speak your answer under realistic timed pressure.\n"
                "3. Review the AI's objective score and compare against the provided benchmark model answer."
            )

    # Default dynamic response
    return (
        f"### Placement Guidance on '{message.strip()}'\n\n"
        "To excel in campus recruitment, approach this with structured preparation:\n\n"
        "1. **Core Concept Mastery**: Ensure you understand the underlying mechanisms, terminology, and edge cases.\n"
        "2. **Practical Application**: Implement solutions or practice articulating this concept out loud in 60-90 seconds.\n"
        "3. **Mock Evaluation**: Test yourself under realistic interview conditions to gauge clarity, structure, and timing.\n\n"
        "Would you like to explore specific coding questions, deep-dive into interview practice, or review your resume for a target job role?"
    )


async def create_session(
    db: AsyncSession,
    user_id: str,
    title: str = "Placement Guidance Session",
) -> ChatSession:
    """Create a new chat conversation session with an initial welcome message."""
    session = ChatSession(user_id=user_id, title=title)
    db.add(session)
    await db.flush()

    welcome_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=(
            "Hello! I am your AI Placement Coach. Whether you need guidance on coding patterns, "
            "technical concepts, resume reviews, or HR interview rounds, feel free to ask me anything!"
        ),
    )
    db.add(welcome_msg)
    await db.commit()
    return await get_session_by_id(db, user_id, session.id) or session


async def get_user_sessions(db: AsyncSession, user_id: str) -> list[ChatSession]:
    """Retrieve all chat sessions belonging to a student."""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user_id)
        .options(selectinload(ChatSession.messages))
        .order_by(ChatSession.started_at.desc())
    )
    return list(result.scalars().all())


async def get_session_by_id(db: AsyncSession, user_id: str, session_id: str) -> ChatSession | None:
    """Get a chat session with its messages, ensuring ownership."""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .options(selectinload(ChatSession.messages))
    )
    return result.scalar_one_or_none()


async def send_message(
    db: AsyncSession,
    user_id: str,
    session_id: str,
    content: str,
) -> tuple[ChatMessage, ChatMessage]:
    """Post a user message, query the AI coach, and save both turns."""
    session = await get_session_by_id(db, user_id, session_id)
    if not session:
        raise ValueError("Chat session not found")

    # Save user message
    user_msg = ChatMessage(
        session_id=session_id,
        role="user",
        content=content.strip(),
    )
    db.add(user_msg)
    await db.flush()

    # Build context from recent messages
    recent_history = [m for m in session.messages if m.id != user_msg.id][-8:]
    conversation_context = "\n".join(
        f"{m.role.capitalize()}: {m.content}" for m in recent_history
    )
    prompt = (
        f"You are conversing with a student preparing for campus placements.\n\n"
        f"Conversation History:\n{conversation_context}\n\n"
        f"Student's Current Query:\n{content.strip()}\n\n"
        f"Provide a helpful, direct, context-aware, and actionable response addressing the student's question."
    )

    ai_service = get_ai_service()
    try:
        reply_text = await ai_service.generate_text(
            prompt=prompt,
            system_instruction=CHATBOT_SYSTEM_PROMPT,
        )
    except AIServiceError as e:
        logger.warning("AI Service error in chat: %s. Using dynamic placement guidance fallback.", str(e))
        reply_text = _get_dynamic_coaching_response(content, recent_history)

    assistant_msg = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=reply_text.strip(),
    )
    db.add(assistant_msg)

    # Log student activity
    activity = ActivityLog(
        user_id=user_id,
        activity_type="chat_message_sent",
        description="Engaged with AI Placement Assistant",
        metadata_json={"session_id": session_id},
    )
    db.add(activity)

    await db.commit()
    await db.refresh(user_msg)
    await db.refresh(assistant_msg)
    return user_msg, assistant_msg
