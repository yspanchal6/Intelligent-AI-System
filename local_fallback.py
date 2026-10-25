
"""Rule-based offline responses for when Gemini is unavailable."""

import re


RESPONSES = {
    "ai": (
        "Artificial intelligence (AI) is a field of computer science that "
        "develops systems capable of learning, reasoning, language processing, "
        "and pattern recognition."
    ),
    "machine_learning": (
        "Machine learning is a branch of AI in which computers learn patterns "
        "from data to make predictions or decisions without being explicitly "
        "programmed for every case."
    ),
    "python": (
        "Python is a high-level, general-purpose programming language known "
        "for readable syntax. It is used in automation, web development, "
        "data analysis, and AI."
    ),
    "cybersecurity": (
        "Cybersecurity protects computers, networks, applications, and data "
        "from unauthorized access, attacks, damage, and theft."
    ),
    "dsa": (
        "Data Structures and Algorithms (DSA) focuses on organizing data "
        "efficiently and solving problems through step-by-step procedures. "
        "Common structures include arrays, linked lists, stacks, queues, "
        "trees, and graphs."
    ),
    "computer_networks": (
        "Computer networks connect devices so they can exchange data and "
        "share resources. Important topics include the OSI model, TCP/IP, "
        "IP addressing, routing, and network protocols."
    ),
    "operating_system": (
        "An operating system manages computer hardware and software resources. "
        "Its responsibilities include process management, memory management, "
        "file management, and device management."
    ),
    "java": (
        "Java is a high-level, class-based programming language. It compiles "
        "to bytecode that runs on the Java Virtual Machine (JVM)."
    ),
    "html": (
        "HTML (HyperText Markup Language) structures web-page content using "
        "elements such as headings, paragraphs, links, images, and forms."
    ),
    "javascript": (
        "JavaScript is a programming language commonly used to make web pages "
        "interactive and to build applications on both browsers and servers."
    ),
    "recursion": (
        "Recursion occurs when a function calls itself to solve a smaller "
        "version of a problem. A base case is required to stop the calls."
    ),
    "stack": (
        "A stack is a linear data structure that follows LIFO: Last In, "
        "First Out. Common operations are push, pop, and peek."
    ),
    "queue": (
        "A queue is a linear data structure that generally follows FIFO: "
        "First In, First Out. Common operations are enqueue and dequeue."
    ),
    "osi": (
        "The OSI model has seven layers: Physical, Data Link, Network, "
        "Transport, Session, Presentation, and Application."
    ),
    "sql": (
        "SQL (Structured Query Language) is used to define, retrieve, "
        "insert, update, and delete data in relational databases."
    ),
}


def local_fallback(question):
    """Answer supported questions using offline keyword rules."""
    if not isinstance(question, str) or not question.strip():
        return "Please enter a question."

    text = re.sub(r"\s+", " ", question.lower().strip())
    text = re.sub(r"[?.!,]+$", "", text)
    text = re.sub(
        r"\b(please|simply|briefly|in simple words|explain|describe|tell me about)\b",
        " ",
        text,
    )
    text = re.sub(r"\s+", " ", text).strip()

    if text in {"hi", "hello", "hey", "hii", "hello there"}:
        return (
            "Hello! Gemini is unavailable right now, but I can answer "
            "some common questions offline."
        )

    # Check specific concepts before broader topic names.
    rules = [
        (r"\b(osi model|seven layers of osi|osi layers)\b", "osi"),
        (r"\b(recursion|recursive function)\b", "recursion"),
        (r"\b(stack|lifo)\b", "stack"),
        (r"\b(queue|fifo)\b", "queue"),
        (r"\b(machine learning|ml)\b", "machine_learning"),
        (r"\b(artificial intelligence|what is ai|about ai|explain ai|ai)\b", "ai"),
        (r"\b(computer network|computer networking|tcp/ip|ip addressing)\b",
         "computer_networks"),
        (r"\b(operating system|process management|memory management)\b",
         "operating_system"),
        (r"\b(data structures|algorithms|dsa)\b", "dsa"),
        (r"\b(cybersecurity|cyber security|ethical hacking)\b", "cybersecurity"),
        (r"\b(python|python programming)\b", "python"),
        (r"\b(java|jvm|java programming)\b", "java"),
        (r"\b(html|html5)\b", "html"),
        (r"\b(javascript|js programming)\b", "javascript"),
        (r"\b(sql|structured query language|database query)\b", "sql"),
    ]

    for pattern, response_key in rules:
        if re.search(pattern, text):
            return RESPONSES[response_key]

    return (
        "I couldn't answer that question using my offline knowledge. "
        "Gemini may be unavailable because of an API quota or connection "
        "issue. Try a supported topic or try again when Gemini is available."
    )
