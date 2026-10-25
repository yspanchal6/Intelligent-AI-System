"""Small offline knowledge base and numbered machine-learning follow-ups."""

last_topic = None


def get_local_answer(question):
    global last_topic
    text = question.lower().strip().rstrip("?!., ")

    if last_topic == "machine_learning":
        ml_types = {
            "1": "Supervised learning uses labeled examples. A model learns from input-output pairs, such as emails labeled spam or not spam.",
            "2": "Unsupervised learning finds patterns in data without supplied labels. Examples include customer clustering and grouping similar documents.",
            "3": "Reinforcement learning trains an agent to choose actions using rewards and penalties. It is used in robotics, games, and control systems.",
        }
        if text in ml_types:
            last_topic = None
            return ml_types[text]

    knowledge = {
        "machine_learning": (["machine learning", "what is ml", "explain ml"], "Machine learning is a branch of AI that learns patterns from data to make predictions or decisions.\n1. Supervised learning\n2. Unsupervised learning\n3. Reinforcement learning\nEnter 1, 2, or 3 to learn about each type."),
        "artificial_intelligence": (["artificial intelligence", "what is ai", "define ai"], "Artificial intelligence (AI) is the field of building computer systems that perform tasks associated with human intelligence, such as reasoning, language understanding, and problem-solving."),
        "python": (["what is python", "python programming", "python language"], "Python is a readable, general-purpose programming language used in automation, web development, data analysis, and AI."),
        "cybersecurity": (["cybersecurity", "cyber security"], "Cybersecurity is the practice of protecting systems, networks, applications, and data from unauthorized access, attacks, and damage."),
        "quantum_computing": (["quantum computing"], "Quantum computing uses quantum-mechanical states to process information. Practical advantages depend on the problem and the available hardware."),
    }
    for topic, (keywords, answer) in knowledge.items():
        if any(keyword in text for keyword in keywords):
            last_topic = topic if topic == "machine_learning" else None
            return answer
    return None
