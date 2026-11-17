from __future__ import annotations

from datetime import datetime, timezone
import random
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.activity import ActivityLog
from app.models.assessment import Assessment, TestResponse, TestSession
from app.schemas.assessment import (
    AnswerItem,
    CategoriesResponse,
    QuestionItemOut,
    QuestionResultDetail,
    SessionResultResponse,
    SessionStartResponse,
    SubcategoryInfo,
)

DEFAULT_QUESTIONS = [
    # --- APTITUDE: Quantitative (10 Questions) ---
    {
        "category": "aptitude",
        "subcategory": "quantitative",
        "question": "A train 240 m long passes a pole in 24 seconds. How long will it take to pass a platform 650 m long?",
        "options": ["65 seconds", "89 seconds", "100 seconds", "150 seconds"],
        "correct_option": 1,
        "difficulty": "medium",
        "explanation": "Speed of train = 240 / 24 = 10 m/s. Total distance to cross platform = 240 + 650 = 890 m. Time taken = 890 / 10 = 89 seconds.",
        "tags": ["Speed & Distance", "Arithmetic"],
    },
    {
        "category": "aptitude",
        "subcategory": "quantitative",
        "question": "A and B can do a work in 12 days, B and C in 15 days, and C and A in 20 days. If A, B, and C work together, they will complete the work in:",
        "options": ["5 days", "10 days", "15 days", "20 days"],
        "correct_option": 1,
        "difficulty": "medium",
        "explanation": "2(A + B + C)'s 1 day work = 1/12 + 1/15 + 1/20 = 12/60 = 1/5. Thus (A + B + C)'s 1 day work = 1/10. Work completed in 10 days.",
        "tags": ["Time & Work", "Arithmetic"],
    },
    {
        "category": "aptitude",
        "subcategory": "quantitative",
        "question": "A bag contains 6 black and 8 white balls. One ball is drawn at random. What is the probability that the ball drawn is white?",
        "options": ["3/7", "4/7", "1/8", "3/4"],
        "correct_option": 1,
        "difficulty": "easy",
        "explanation": "Total balls = 6 + 8 = 14. White balls = 8. Probability = 8/14 = 4/7.",
        "tags": ["Probability"],
    },
    {
        "category": "aptitude",
        "subcategory": "quantitative",
        "question": "In how many different ways can the letters of the word 'LEADING' be arranged in such a way that the vowels always come together?",
        "options": ["360", "480", "720", "5040"],
        "correct_option": 2,
        "difficulty": "hard",
        "explanation": "Vowels are E, A, I (3 vowels). Treat (E,A,I) as 1 unit + 4 consonants = 5 units. 5! * 3! = 120 * 6 = 720 ways.",
        "tags": ["Permutations & Combinations"],
    },
    {
        "category": "aptitude",
        "subcategory": "quantitative",
        "question": "The difference between simple and compound interest on a sum of money for 2 years at 10% per annum is Rs. 65. The sum is:",
        "options": ["Rs. 6000", "Rs. 6500", "Rs. 7000", "Rs. 7500"],
        "correct_option": 1,
        "difficulty": "medium",
        "explanation": "For 2 years, Difference = P * (R/100)^2. 65 = P * (10/100)^2 = P * 1/100. P = 65 * 100 = Rs. 6500.",
        "tags": ["Simple & Compound Interest", "Arithmetic"],
    },
    {
        "category": "aptitude",
        "subcategory": "quantitative",
        "question": "A merchant marks his goods 25% above cost price and allows a discount of 10% for cash payment. His profit percentage is:",
        "options": ["12.5%", "15%", "17.5%", "20%"],
        "correct_option": 0,
        "difficulty": "easy",
        "explanation": "Let CP = 100. MP = 125. SP after 10% discount = 125 - 12.5 = 112.5. Profit = 12.5%.",
        "tags": ["Profit & Loss", "Percentages"],
    },
    {
        "category": "aptitude",
        "subcategory": "quantitative",
        "question": "A mixture contains milk and water in the ratio 5:3. If 4 litres of water are added, the ratio becomes 5:4. The quantity of milk in the mixture is:",
        "options": ["15 litres", "20 litres", "25 litres", "30 litres"],
        "correct_option": 1,
        "difficulty": "medium",
        "explanation": "Let milk = 5x, water = 3x. 5x / (3x + 4) = 5/4 => 20x = 15x + 20 => 5x = 20. Quantity of milk is 20 litres.",
        "tags": ["Ratios & Mixtures"],
    },
    {
        "category": "aptitude",
        "subcategory": "quantitative",
        "question": "Two pipes A and B can fill a tank in 20 and 30 minutes respectively. If both pipes are opened together, the time taken to fill the tank is:",
        "options": ["10 minutes", "12 minutes", "15 minutes", "25 minutes"],
        "correct_option": 1,
        "difficulty": "easy",
        "explanation": "Combined 1-minute rate = 1/20 + 1/30 = 5/60 = 1/12. Time taken = 12 minutes.",
        "tags": ["Pipes & Cisterns", "Time & Work"],
    },
    {
        "category": "aptitude",
        "subcategory": "quantitative",
        "question": "The present ages of a father and his son are in the ratio 7:2. Five years ago, the ratio of their ages was 6:1. What is the father's present age?",
        "options": ["28 years", "35 years", "42 years", "49 years"],
        "correct_option": 1,
        "difficulty": "medium",
        "explanation": "(7x - 5)/(2x - 5) = 6/1 => 7x - 5 = 12x - 30 => 5x = 25 => x = 5. Father's age = 7 * 5 = 35 years.",
        "tags": ["Age Problems", "Ratios"],
    },
    {
        "category": "aptitude",
        "subcategory": "quantitative",
        "question": "A boat can travel with a speed of 13 km/hr in still water. If the speed of the stream is 4 km/hr, find the time taken by the boat to go 68 km downstream:",
        "options": ["3 hours", "4 hours", "5 hours", "6 hours"],
        "correct_option": 1,
        "difficulty": "easy",
        "explanation": "Downstream speed = 13 + 4 = 17 km/hr. Time = 68 / 17 = 4 hours.",
        "tags": ["Boats & Streams", "Speed & Distance"],
    },

    # --- APTITUDE: Logical Reasoning (10 Questions) ---
    {
        "category": "aptitude",
        "subcategory": "logical",
        "question": "Statements: All mangoes are golden in colour. No golden-coloured things are cheap. Conclusions: 1) All mangoes are cheap. 2) Golden-coloured mangoes are not cheap.",
        "options": ["Only conclusion 1 follows", "Only conclusion 2 follows", "Either 1 or 2 follows", "Neither follows"],
        "correct_option": 1,
        "difficulty": "medium",
        "explanation": "Mangoes are golden, and no golden things are cheap. Hence mangoes cannot be cheap, meaning golden-coloured mangoes are definitely not cheap.",
        "tags": ["Syllogisms", "Logical Deduction"],
    },
    {
        "category": "aptitude",
        "subcategory": "logical",
        "question": "Pointing to a photograph of a boy Suresh said, 'He is the son of the only son of my mother.' How is Suresh related to that boy?",
        "options": ["Brother", "Uncle", "Cousin", "Father"],
        "correct_option": 3,
        "difficulty": "easy",
        "explanation": "The only son of Suresh's mother is Suresh himself. The boy in the photo is Suresh's son, so Suresh is the father.",
        "tags": ["Blood Relations"],
    },
    {
        "category": "aptitude",
        "subcategory": "logical",
        "question": "Find the missing number in the series: 4, 18, ?, 100, 180, 294, 448",
        "options": ["32", "36", "48", "64"],
        "correct_option": 2,
        "difficulty": "hard",
        "explanation": "Pattern is n^3 - n^2: 2^3 - 2^2 = 4, 3^3 - 3^2 = 18, 4^3 - 4^2 = 48, 5^3 - 5^2 = 100.",
        "tags": ["Number Series"],
    },
    {
        "category": "aptitude",
        "subcategory": "logical",
        "question": "In a certain code, 'ROSE' is written as '6821' and 'CHAIR' is written as '73456'. How is 'SEARCH' written in that code?",
        "options": ["214673", "214763", "241673", "214573"],
        "correct_option": 0,
        "difficulty": "easy",
        "explanation": "Direct mapping: S=2, E=1, A=4, R=6, C=7, H=3. Hence SEARCH = 214673.",
        "tags": ["Coding-Decoding"],
    },
    {
        "category": "aptitude",
        "subcategory": "logical",
        "question": "A person walks 10 km towards North. From there he walks 6 km towards South. Then he walks 3 km towards East. How far and in which direction is he with reference to his starting point?",
        "options": ["5 km West", "5 km North-East", "7 km East", "7 km North"],
        "correct_option": 1,
        "difficulty": "medium",
        "explanation": "Net North = 10 - 6 = 4 km. Net East = 3 km. Distance = sqrt(4^2 + 3^2) = 5 km North-East.",
        "tags": ["Direction Sense"],
    },
    {
        "category": "aptitude",
        "subcategory": "logical",
        "question": "Six persons A, B, C, D, E, and F are sitting in a circle facing the center. B is between D and C. A is between E and C. F is to the right of D. Who is sitting opposite to A?",
        "options": ["B", "D", "E", "F"],
        "correct_option": 1,
        "difficulty": "hard",
        "explanation": "Arrangement in clockwise order: C, A, E, F, D, B. Opposite to A is D.",
        "tags": ["Seating Arrangement"],
    },
    {
        "category": "aptitude",
        "subcategory": "logical",
        "question": "Statement: 'Please switch off your mobile phones during the campus interview round.' Assumptions: I. Ringing mobile phones disrupt interview evaluations. II. Most candidates carry mobile phones.",
        "options": ["Only I is implicit", "Only II is implicit", "Both I and II are implicit", "Neither is implicit"],
        "correct_option": 2,
        "difficulty": "medium",
        "explanation": "Notice is given because phones cause disruption (I) and candidates possess them (II). Both are implicit.",
        "tags": ["Statement & Assumptions"],
    },
    {
        "category": "aptitude",
        "subcategory": "logical",
        "question": "Clock is related to Time in the same way as Thermometer is related to:",
        "options": ["Heat", "Radiation", "Temperature", "Energy"],
        "correct_option": 2,
        "difficulty": "easy",
        "explanation": "A clock measures time; a thermometer measures temperature.",
        "tags": ["Analogies"],
    },
    {
        "category": "aptitude",
        "subcategory": "logical",
        "question": "Choose the word which is least like the other words in the group:",
        "options": ["Copper", "Zinc", "Brass", "Iron"],
        "correct_option": 2,
        "difficulty": "easy",
        "explanation": "Brass is an alloy (copper + zinc), while Copper, Zinc, and Iron are pure metallic elements.",
        "tags": ["Classification"],
    },
    {
        "category": "aptitude",
        "subcategory": "logical",
        "question": "In a class of 45 students, Rohit's rank is 16th from the top. What is his rank from the bottom?",
        "options": ["29th", "30th", "31st", "32nd"],
        "correct_option": 1,
        "difficulty": "easy",
        "explanation": "Rank from bottom = Total - Rank from top + 1 = 45 - 16 + 1 = 30th.",
        "tags": ["Ranking & Order"],
    },

    # --- APTITUDE: Verbal Ability (10 Questions) ---
    {
        "category": "aptitude",
        "subcategory": "verbal",
        "question": "Choose the word most nearly opposite in meaning to CANDID:",
        "options": ["Blunt", "Devious", "Sincere", "Outspoken"],
        "correct_option": 1,
        "difficulty": "easy",
        "explanation": "Candid means truthful and straightforward. Devious means deceitful or secretive (antonym).",
        "tags": ["Antonyms", "Vocabulary"],
    },
    {
        "category": "aptitude",
        "subcategory": "verbal",
        "question": "Identify the grammatically correct sentence:",
        "options": [
            "Neither the manager nor the employees was present.",
            "Neither the manager nor the employees were present.",
            "Neither the manager or the employees was present.",
            "Neither the manager nor the employee were present."
        ],
        "correct_option": 1,
        "difficulty": "medium",
        "explanation": "With 'neither...nor', the verb agrees in number with the closer subject ('employees' is plural, so 'were' is correct).",
        "tags": ["Subject-Verb Agreement", "Grammar"],
    },
    {
        "category": "aptitude",
        "subcategory": "verbal",
        "question": "Choose the word closest in meaning to METICULOUS:",
        "options": ["Careless", "Thorough", "Hasty", "Indifferent"],
        "correct_option": 1,
        "difficulty": "easy",
        "explanation": "Meticulous means showing great attention to detail; very careful and thorough.",
        "tags": ["Synonyms", "Vocabulary"],
    },
    {
        "category": "aptitude",
        "subcategory": "verbal",
        "question": "What is the meaning of the idiom 'To bite the bullet'?",
        "options": ["To avoid a difficult situation", "To accept an unpleasant situation courageously", "To lose one's temper", "To win by unfair means"],
        "correct_option": 1,
        "difficulty": "medium",
        "explanation": "'To bite the bullet' means to face a grim or difficult situation with fortitude.",
        "tags": ["Idioms & Phrases"],
    },
    {
        "category": "aptitude",
        "subcategory": "verbal",
        "question": "Select the correct sentence with proper punctuation and tense:",
        "options": [
            "Although she was exhausted she continued working on the project.",
            "Although she was exhausted, she continued working on the project.",
            "Although she was exhausted; she continued working on the project.",
            "Although she was exhausted but she continued working on the project."
        ],
        "correct_option": 1,
        "difficulty": "easy",
        "explanation": "A subordinate clause starting with 'Although' requires a comma after it and does not take 'but'.",
        "tags": ["Punctuation", "Sentence Structure"],
    },
    {
        "category": "aptitude",
        "subcategory": "verbal",
        "question": "Identify the part of the sentence containing an error: 'He is one of those candidates (A) / who always does (B) / their duty diligently (C) / No error (D)'",
        "options": ["Part A", "Part B", "Part C", "Part D"],
        "correct_option": 1,
        "difficulty": "hard",
        "explanation": "In 'one of those candidates who...', the relative pronoun 'who' refers to plural 'candidates', so the verb must be plural: 'do', not 'does'.",
        "tags": ["Error Spotting", "Grammar"],
    },
    {
        "category": "aptitude",
        "subcategory": "verbal",
        "question": "One word substitution: 'A person who knows and speaks many languages fluently'",
        "options": ["Linguist", "Polyglot", "Orator", "Philologist"],
        "correct_option": 1,
        "difficulty": "medium",
        "explanation": "A polyglot is someone who speaks or writes several languages. A linguist studies language scientifically.",
        "tags": ["One Word Substitution"],
    },
    {
        "category": "aptitude",
        "subcategory": "verbal",
        "question": "Convert into passive voice: 'The recruiter reviewed all candidate submissions.'",
        "options": [
            "All candidate submissions are reviewed by the recruiter.",
            "All candidate submissions were reviewed by the recruiter.",
            "All candidate submissions had been reviewed by the recruiter.",
            "All candidate submissions was reviewed by the recruiter."
        ],
        "correct_option": 1,
        "difficulty": "easy",
        "explanation": "Past simple 'reviewed' converts to 'were reviewed' because 'submissions' is plural.",
        "tags": ["Active & Passive Voice"],
    },
    {
        "category": "aptitude",
        "subcategory": "verbal",
        "question": "Choose the correctly spelt word:",
        "options": ["Accomodation", "Accommodation", "Acommodation", "Accomadation"],
        "correct_option": 1,
        "difficulty": "easy",
        "explanation": "Accommodation has double 'c' and double 'm'.",
        "tags": ["Spelling & Vocabulary"],
    },
    {
        "category": "aptitude",
        "subcategory": "verbal",
        "question": "Fill in the blank with appropriate preposition: 'He is proficient _____ algorithmic problem solving.'",
        "options": ["at", "in", "with", "for"],
        "correct_option": 1,
        "difficulty": "medium",
        "explanation": "The adjective 'proficient' is followed by the preposition 'in' when referring to a skill or subject.",
        "tags": ["Prepositions"],
    },

    # --- TECHNICAL: Data Structures & Algorithms (10 Questions) ---
    {
        "category": "technical",
        "subcategory": "dsa",
        "question": "What is the worst-case time complexity of searching an element in a Red-Black Tree with N nodes?",
        "options": ["O(1)", "O(log N)", "O(N)", "O(N log N)"],
        "correct_option": 1,
        "difficulty": "medium",
        "explanation": "A Red-Black tree is a self-balancing binary search tree with height bounded by 2*log(N+1). Search is always O(log N) worst-case.",
        "tags": ["Trees", "Time Complexity"],
    },
    {
        "category": "technical",
        "subcategory": "dsa",
        "question": "Which algorithmic technique is most appropriate for finding the shortest path in a weighted graph with non-negative edge weights?",
        "options": ["Breadth-First Search (BFS)", "Dijkstra's Algorithm", "Bellman-Ford Algorithm", "Floyd-Warshall Algorithm"],
        "correct_option": 1,
        "difficulty": "easy",
        "explanation": "Dijkstra's algorithm with a min-priority queue computes single-source shortest paths in O((V + E) log V) on graphs with non-negative weights.",
        "tags": ["Graphs", "Shortest Path"],
    },
    {
        "category": "technical",
        "subcategory": "dsa",
        "question": "Given an array of integers, which data structure allows answering Range Minimum Queries (RMQ) in O(1) time after O(N log N) pre-processing?",
        "options": ["Fenwick Tree (Binary Indexed Tree)", "Sparse Table", "Segment Tree", "Trie"],
        "correct_option": 1,
        "difficulty": "hard",
        "explanation": "Sparse Table precomputes power-of-two intervals in O(N log N) and answers idempotent queries like min/max/gcd in O(1).",
        "tags": ["Advanced Data Structures", "Range Queries"],
    },
    {
        "category": "technical",
        "subcategory": "dsa",
        "question": "What is the auxiliary space complexity of standard in-order traversal of a balanced binary tree?",
        "options": ["O(1)", "O(log N)", "O(N)", "O(N^2)"],
        "correct_option": 1,
        "difficulty": "medium",
        "explanation": "The recursive call stack or explicit traversal stack corresponds to the tree height. For a balanced tree, height is O(log N).",
        "tags": ["Trees", "Space Complexity"],
    },
    {
        "category": "technical",
        "subcategory": "dsa",
        "question": "What is the worst-case time complexity of lookup in a Hash Table when using separate chaining?",
        "options": ["O(1)", "O(log N)", "O(N)", "O(N^2)"],
        "correct_option": 2,
        "difficulty": "easy",
        "explanation": "In the worst case where all N keys hash to the same bucket, the lookup traverses an entire linked list of length N, taking O(N) time.",
        "tags": ["Hash Tables", "Time Complexity"],
    },
    {
        "category": "technical",
        "subcategory": "dsa",
        "question": "Which algorithm is used to find the maximum contiguous subarray sum in O(N) time?",
        "options": ["Kadane's Algorithm", "Kruskal's Algorithm", "Tarjan's Algorithm", "KMP Algorithm"],
        "correct_option": 0,
        "difficulty": "easy",
        "explanation": "Kadane's algorithm maintains maximum sum ending at current index and global maximum in a single pass of O(N) time and O(1) space.",
        "tags": ["Arrays", "Dynamic Programming"],
    },
    {
        "category": "technical",
        "subcategory": "dsa",
        "question": "Which of the following sorting algorithms is stable and achieves O(N log N) worst-case time complexity?",
        "options": ["Quick Sort", "Heap Sort", "Merge Sort", "Selection Sort"],
        "correct_option": 2,
        "difficulty": "medium",
        "explanation": "Merge Sort is guaranteed O(N log N) in all cases (worst, average, best) and maintains the relative order of duplicate elements (stable).",
        "tags": ["Sorting Algorithms"],
    },
    {
        "category": "technical",
        "subcategory": "dsa",
        "question": "How can you detect a cycle in a singly linked list with O(1) auxiliary space?",
        "options": ["Hash Set of visited pointers", "Floyd's Cycle-Finding Algorithm (Tortoise & Hare)", "Reversing the linked list", "Counting total nodes"],
        "correct_option": 1,
        "difficulty": "medium",
        "explanation": "Floyd's algorithm uses slow and fast pointers. If a cycle exists, fast will catch up to slow inside the loop in O(N) time and O(1) space.",
        "tags": ["Linked Lists", "Two Pointers"],
    },
    {
        "category": "technical",
        "subcategory": "dsa",
        "question": "In the 0/1 Knapsack problem with N items and maximum weight capacity W, what is the standard dynamic programming table size?",
        "options": ["O(N)", "O(W)", "O(N * W)", "O(2^N)"],
        "correct_option": 2,
        "difficulty": "medium",
        "explanation": "The DP state dp[i][w] represents maximum value with first i items and weight w, requiring an (N+1) x (W+1) table of size O(N * W).",
        "tags": ["Dynamic Programming", "Knapsack"],
    },
    {
        "category": "technical",
        "subcategory": "dsa",
        "question": "Which data structure is primarily used to implement Prim's algorithm efficiently to find a Minimum Spanning Tree?",
        "options": ["Stack", "Binary Min-Heap / Priority Queue", "Trie", "Disjoint Set Union"],
        "correct_option": 1,
        "difficulty": "medium",
        "explanation": "Prim's algorithm extracts the minimum weight cut edge repeatedly using a binary min-heap (or Fibonacci heap). Kruskal's uses DSU.",
        "tags": ["Graphs", "Minimum Spanning Tree"],
    },

    # --- TECHNICAL: CS Fundamentals (OS / DBMS / Networks) (10 Questions) ---
    {
        "category": "technical",
        "subcategory": "cs_fundamentals",
        "question": "Which of the following conditions is NOT required for a deadlock to occur in an operating system?",
        "options": ["Mutual Exclusion", "Hold and Wait", "Preemption allowed", "Circular Wait"],
        "correct_option": 2,
        "difficulty": "easy",
        "explanation": "Coffman conditions require NO PREEMPTION. If preemption is allowed, deadlock cannot persist.",
        "tags": ["Operating Systems", "Deadlocks"],
    },
    {
        "category": "technical",
        "subcategory": "cs_fundamentals",
        "question": "In relational database design, which Normal Form guarantees that every non-prime attribute is fully functionally dependent on the primary key, eliminating partial dependencies?",
        "options": ["First Normal Form (1NF)", "Second Normal Form (2NF)", "Third Normal Form (3NF)", "Boyce-Codd Normal Form (BCNF)"],
        "correct_option": 1,
        "difficulty": "medium",
        "explanation": "2NF eliminates partial dependencies on candidate keys. 3NF eliminates transitive dependencies.",
        "tags": ["DBMS", "Normalization"],
    },
    {
        "category": "technical",
        "subcategory": "cs_fundamentals",
        "question": "During the TCP 3-way handshake, what flags are sent in the second packet from the server to the client?",
        "options": ["SYN", "ACK", "SYN-ACK", "FIN-ACK"],
        "correct_option": 2,
        "difficulty": "easy",
        "explanation": "Step 1: Client -> Server (SYN). Step 2: Server -> Client (SYN-ACK). Step 3: Client -> Server (ACK).",
        "tags": ["Computer Networks", "TCP/IP"],
    },
    {
        "category": "technical",
        "subcategory": "cs_fundamentals",
        "question": "Which page replacement algorithm suffers from Belady's Anomaly where increasing the number of page frames leads to more page faults?",
        "options": ["Least Recently Used (LRU)", "Optimal Page Replacement (OPT)", "First-In First-Out (FIFO)", "Least Frequently Used (LFU)"],
        "correct_option": 2,
        "difficulty": "medium",
        "explanation": "FIFO page replacement is not a stack algorithm and can exhibit Belady's Anomaly.",
        "tags": ["Operating Systems", "Memory Management"],
    },
    {
        "category": "technical",
        "subcategory": "cs_fundamentals",
        "question": "What is the key difference between a process and a thread in modern operating systems?",
        "options": [
            "Processes share memory space while threads do not.",
            "Threads within the same process share code, data, and heap, but have independent stacks.",
            "Processes are managed by user space while threads are always kernel space.",
            "Threads cannot execute concurrently on multi-core systems."
        ],
        "correct_option": 1,
        "difficulty": "easy",
        "explanation": "Threads of the same process share address space, heap, and open file descriptors, but maintain private program counters and registers/stacks.",
        "tags": ["Operating Systems", "Concurrency"],
    },
    {
        "category": "technical",
        "subcategory": "cs_fundamentals",
        "question": "Which ACID property in databases ensures that concurrent transactions execute without interfering with one another, as if executed serially?",
        "options": ["Atomicity", "Consistency", "Isolation", "Durability"],
        "correct_option": 2,
        "difficulty": "easy",
        "explanation": "Isolation prevents concurrency anomalies like dirty reads, non-repeatable reads, and phantom reads.",
        "tags": ["DBMS", "Transactions & ACID"],
    },
    {
        "category": "technical",
        "subcategory": "cs_fundamentals",
        "question": "What protocol and port are predominantly used for standard DNS hostname resolution queries by client stub resolvers?",
        "options": ["TCP port 80", "UDP port 53", "TCP port 443", "UDP port 67"],
        "correct_option": 1,
        "difficulty": "easy",
        "explanation": "Standard DNS queries use UDP port 53 for low latency. TCP port 53 is used for zone transfers and messages exceeding 512 bytes.",
        "tags": ["Computer Networks", "DNS"],
    },
    {
        "category": "technical",
        "subcategory": "cs_fundamentals",
        "question": "What is the primary role of the Translation Lookaside Buffer (TLB) in virtual memory management?",
        "options": [
            "To cache disk blocks in RAM",
            "To cache recent virtual-to-physical address translations to avoid multi-level page table lookups",
            "To prevent stack overflow attacks",
            "To schedule CPU threads across cores"
        ],
        "correct_option": 1,
        "difficulty": "medium",
        "explanation": "The TLB is a high-speed hardware associative cache that stores recent page table translations, avoiding expensive memory lookups.",
        "tags": ["Operating Systems", "Virtual Memory"],
    },
    {
        "category": "technical",
        "subcategory": "cs_fundamentals",
        "question": "What distinguishes a Clustered Index from a Non-Clustered Index in relational databases?",
        "options": [
            "A table can have multiple clustered indexes but only one non-clustered index.",
            "A clustered index determines the physical storage order of rows in the table; only one clustered index can exist per table.",
            "Clustered indexes are slower than non-clustered indexes for range queries.",
            "Non-clustered indexes alter the physical layout of disk data."
        ],
        "correct_option": 1,
        "difficulty": "medium",
        "explanation": "Because table rows can only be physically sorted in one order, there can be only one clustered index per table.",
        "tags": ["DBMS", "Indexing"],
    },
    {
        "category": "technical",
        "subcategory": "cs_fundamentals",
        "question": "What is the crucial operational distinction between a Mutex and a Binary Semaphore?",
        "options": [
            "A Mutex can be unlocked by any thread, while a Semaphore cannot.",
            "A Mutex has an ownership concept (only the thread that locked it may unlock it); a Semaphore can be signaled by any thread.",
            "A Semaphore has a maximum value of 1 always.",
            "A Mutex cannot prevent race conditions."
        ],
        "correct_option": 1,
        "difficulty": "medium",
        "explanation": "A Mutex enforces strict locking ownership (ownership semantics). A binary semaphore is a signaling mechanism without ownership.",
        "tags": ["Operating Systems", "Synchronization"],
    },
]


async def seed_questions_if_needed(db: AsyncSession) -> None:
    """Seed initial placement diagnostic questions if question table is empty."""
    count_res = await db.execute(select(func.count(Assessment.id)))
    count = count_res.scalar_one()

    if count < len(DEFAULT_QUESTIONS):
        for q in DEFAULT_QUESTIONS:
            # Check by question text
            existing = await db.execute(select(Assessment).where(Assessment.question == q["question"]))
            if not existing.scalar_one_or_none():
                db.add(Assessment(**q))
        await db.commit()


async def get_assessment_categories(db: AsyncSession) -> CategoriesResponse:
    """Return available assessment categories and subcategory summaries."""
    await seed_questions_if_needed(db)

    # Subcategory configurations
    metadata = {
        ("aptitude", "quantitative"): ("Quantitative Aptitude", 15, "Arithmetic, time & work, probability, algebra screening questions."),
        ("aptitude", "logical"): ("Logical Reasoning", 15, "Syllogisms, blood relations, deductive patterns, and series."),
        ("aptitude", "verbal"): ("Verbal Ability", 15, "Reading comprehension, sentence correction, and vocabulary."),
        ("technical", "dsa"): ("Data Structures & Algorithms", 20, "Arrays, trees, graphs, dynamic programming, and complexity."),
        ("technical", "cs_fundamentals"): ("CS Core Fundamentals", 20, "Operating Systems, DBMS ACID properties, and TCP/IP networks."),
    }

    result: dict[str, list[SubcategoryInfo]] = {"aptitude": [], "technical": []}

    for (cat, subcat), (name, duration, desc) in metadata.items():
        q_count_res = await db.execute(
            select(func.count(Assessment.id)).where(
                Assessment.category == cat, Assessment.subcategory == subcat
            )
        )
        count = q_count_res.scalar_one()

        info = SubcategoryInfo(
            name=name,
            category=cat,
            question_count=count,
            duration_minutes=duration,
            description=desc,
        )
        if cat in result:
            result[cat].append(info)

    return CategoriesResponse(categories=result)


async def start_assessment_session(
    db: AsyncSession, user_id: str, category: str, subcategory: str, num_questions: int = 5
) -> SessionStartResponse:
    """Initialize a test session and return a randomized set of diagnostic questions."""
    await seed_questions_if_needed(db)

    stmt = select(Assessment).where(
        Assessment.category == category, Assessment.subcategory == subcategory
    )
    res = await db.execute(stmt)
    all_qs = list(res.scalars().all())

    if not all_qs:
        # Fallback to category only if subcategory is empty
        stmt_cat = select(Assessment).where(Assessment.category == category)
        all_qs = list((await db.execute(stmt_cat)).scalars().all())

    sample_size = min(len(all_qs), num_questions)
    chosen_qs = random.sample(all_qs, sample_size) if all_qs else []

    session = TestSession(
        user_id=user_id,
        category=category,
        subcategory=subcategory,
        score=0,
        max_score=len(chosen_qs),
        time_taken_seconds=0,
        status="in_progress",
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    # Return questions without revealing correct_option
    out_questions = [
        QuestionItemOut(
            id=q.id,
            category=q.category,
            subcategory=q.subcategory,
            question=q.question,
            options=q.options,
            difficulty=q.difficulty,
        )
        for q in chosen_qs
    ]

    return SessionStartResponse(
        session_id=session.id,
        category=category,
        subcategory=subcategory,
        time_limit_minutes=15,
        questions=out_questions,
    )


async def submit_assessment_session(
    db: AsyncSession, user_id: str, session_id: str, answers: list[AnswerItem], time_taken_seconds: int
) -> SessionResultResponse:
    """Evaluate answers, score the test, identify weak areas, and log dashboard event."""
    session_res = await db.execute(
        select(TestSession).where(TestSession.id == session_id, TestSession.user_id == user_id)
    )
    session = session_res.scalar_one_or_none()
    if not session:
        raise ValueError("Assessment session not found.")

    score = 0
    max_score = len(answers)
    weak_topics_set = set()
    breakdown: list[QuestionResultDetail] = []

    for item in answers:
        q_res = await db.execute(select(Assessment).where(Assessment.id == item.question_id))
        q = q_res.scalar_one_or_none()
        if not q:
            continue

        is_correct = (item.selected_option == q.correct_option)
        if is_correct:
            score += 1
        else:
            # Tag as weak topic
            for tag in q.tags:
                weak_topics_set.add(tag)
            if not q.tags:
                weak_topics_set.add(q.subcategory.replace("_", " ").title())

        # Save response record
        test_resp = TestResponse(
            session_id=session.id,
            question_id=q.id,
            selected_option=item.selected_option,
            is_correct=is_correct,
            time_taken_seconds=0,
        )
        db.add(test_resp)

        breakdown.append(
            QuestionResultDetail(
                question_id=q.id,
                question=q.question,
                options=q.options,
                selected_option=item.selected_option,
                correct_option=q.correct_option,
                is_correct=is_correct,
                explanation=q.explanation,
                tags=q.tags,
            )
        )

    session.score = score
    session.max_score = max_score
    session.time_taken_seconds = time_taken_seconds
    session.status = "completed"
    session.completed_at = datetime.now(timezone.utc)

    # Record event in activity log for dashboard
    percentage = (score / max_score * 100) if max_score > 0 else 0.0
    activity = ActivityLog(
        user_id=user_id,
        activity_type="assessment_completed",
        metadata_json={
            "session_id": session.id,
            "category": session.category,
            "subcategory": session.subcategory,
            "score": score,
            "max_score": max_score,
            "percentage": percentage,
        },
    )
    db.add(activity)

    await db.commit()

    return SessionResultResponse(
        session_id=session.id,
        category=session.category,
        subcategory=session.subcategory,
        score=score,
        max_score=max_score,
        percentage=round(percentage, 1),
        time_taken_seconds=time_taken_seconds,
        completed_at=session.completed_at,
        weak_topics=list(weak_topics_set),
        breakdown=breakdown,
    )


async def get_session_result_details(
    db: AsyncSession, user_id: str, session_id: str
) -> SessionResultResponse:
    """Retrieve full result report for an existing session."""
    session_res = await db.execute(
        select(TestSession)
        .options(selectinload(TestSession.responses).selectinload(TestResponse.assessment))
        .where(TestSession.id == session_id, TestSession.user_id == user_id)
    )
    session = session_res.scalar_one_or_none()
    if not session:
        raise ValueError("Assessment session not found.")

    weak_topics_set = set()
    breakdown: list[QuestionResultDetail] = []

    for resp in session.responses:
        q = resp.assessment
        if not resp.is_correct:
            for tag in q.tags:
                weak_topics_set.add(tag)

        breakdown.append(
            QuestionResultDetail(
                question_id=q.id,
                question=q.question,
                options=q.options,
                selected_option=resp.selected_option,
                correct_option=q.correct_option,
                is_correct=resp.is_correct,
                explanation=q.explanation,
                tags=q.tags,
            )
        )

    percentage = (session.score / session.max_score * 100) if session.max_score > 0 else 0.0

    return SessionResultResponse(
        session_id=session.id,
        category=session.category,
        subcategory=session.subcategory,
        score=session.score,
        max_score=session.max_score,
        percentage=round(percentage, 1),
        time_taken_seconds=session.time_taken_seconds,
        completed_at=session.completed_at or session.started_at,
        weak_topics=list(weak_topics_set),
        breakdown=breakdown,
    )


async def get_user_history(db: AsyncSession, user_id: str) -> list[dict]:
    """Retrieve all past test attempts for the student."""
    stmt = (
        select(TestSession)
        .where(TestSession.user_id == user_id)
        .order_by(TestSession.started_at.desc())
    )
    res = await db.execute(stmt)
    sessions = res.scalars().all()

    items = []
    for s in sessions:
        pct = (s.score / s.max_score * 100) if s.max_score > 0 else 0.0
        items.append({
            "session_id": s.id,
            "category": s.category,
            "subcategory": s.subcategory,
            "score": s.score,
            "max_score": s.max_score,
            "percentage": round(pct, 1),
            "time_taken_seconds": s.time_taken_seconds,
            "completed_at": s.completed_at,
            "status": s.status,
        })
    return items

