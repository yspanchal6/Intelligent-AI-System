
"""Deterministic routing for supported assistant actions."""

import re

CONFIDENCE_THRESHOLD = 0.35

SEARCH_PREFIXES = (
    "search the internet for ",
    "search the web for ",
    "search web for ",
    "search online for ",
    "web search for ",
    "search for ",
    "find the latest ",
    "find current ",
    "look up ",
    "google ",
)


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower().strip()).rstrip("!?., ")


def decide_action(intent, confidence, user_text):
    """Return a supported action name for a user request."""
    text = normalize_text(user_text)

    # Remove optional category prefixes.
    prefixes = (
        "calculator:",
        "task management:",
        "ai fallback:",
        "recursion fallback:",
    )
    for prefix in prefixes:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
            break

    # Greetings.
    greetings = {
        "hi", "hello", "hey", "hii", "greeting",
        "hello there", "hey there",
        "good morning", "good afternoon", "good evening",
        "how are you", "how are you doing",
    }
    if text in greetings:
        return "greeting"

    # Date and time.
    if text in {
        "time", "date/time", "time and date", "current time",
        "what time is it", "tell me the time", "show time",
        "what is the time now", "tell me the current time",
    }:
        return "show_time"

    if text in {
        "date", "today", "current date", "show date",
        "what is today's date", "what's today's date",
        "what is the date", "what is the date today",
    }:
        return "show_date"

    if text in {"help", "help me", "show help", "what can you do",
                "your abilities", "what commands are available",
                "what features do you have"}:
        return "show_help"

    # Web search.
    if text in {"web search", "search the web", "search online"}:
        return "search_web"

    if any(text.startswith(prefix) for prefix in SEARCH_PREFIXES):
        return "search_web"

    # Website opening. These actions require handlers in main.py.

    # Keep YouTube on its existing dedicated handler.
    if text in {
        "open youtube", "open up youtube",
        "launch youtube", "go to youtube", "please open youtube",
    }:
        return "open_youtube"

    # Open common websites and arbitrary domains.
    website_match = re.match(
        r"^(?:open|visit|launch)\s+(?:website\s+|site\s+)?(.+)$",
        text,
    )

    if website_match:
        target = website_match.group(1).strip()

        if target in {"google", "google.com"}:
            return "open_website"

        # Treat domain-like targets as websites, not general questions.
        if "." in target and " " not in target:
            return "open_website"
   

    if text in {
        "open youtube", "open up youtube",
        "launch youtube", "go to youtube", "please open youtube",
    }:
        return "open_youtube"

    # WhatsApp message.
    if text.startswith((
        "whatsapp to ", "whatsapp message to ",
        "send whatsapp to ", "send whatsapp message to ",
    )):
        return "send_message"

    # Create a text file.
    if text.startswith((
        "create a text file", "create text file",
        "save note:", "write note:",
    )):
        return "create_file"

    # Task management.
    if text in {
        "show tasks", "show my tasks", "list tasks",
        "list my tasks", "view tasks", "my tasks",
        "show all my tasks", "display my task list",
    }:
        return "list_tasks"

    if (
        re.match(r"^(complete|finish)\s+(the\s+)?(task|item)\b", text)
        or re.match(r"^mark\s+(the\s+)?(task|item)\b", text)
    ):
        return "complete_task"

    if (
        text in {"add task", "add a task", "create task",
                 "create a task", "new task"}
        or re.match(r"^(add|create)\s+(a\s+)?task\s+", text)
        or text.startswith("remind me to ")
    ):
        return "add_task"

    # Calculator: normalize natural-language operators.
    normalized = text
    replacements = {
        "multiplied by": "*",
        "multiply by": "*",
        "divided by": "/",
        "divide by": "/",
        "times": "*",
        "plus": "+",
        "minus": "-",
        "modulo": "%",
    }

    for phrase, symbol in replacements.items():
        normalized = normalized.replace(phrase, symbol)

    for prefix in ("calculate", "compute", "what is", "solve"):
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):].strip()
            break

    arithmetic = (
        r"-?\d+(?:\.\d+)?\s*[+\-*/%]\s*-?\d+(?:\.\d+)?"
    )

    if re.fullmatch(arithmetic, normalized):
        return "calculate"

    if text.startswith(("calculate ", "compute ", "solve ")):
        return "calculate"

    # Use ML predictions for supported simple actions.
    action_map = {
        "greeting": "greeting",
        "time": "show_time",
        "date": "show_date",
        "youtube": "open_youtube",
        "help": "show_help",
    }

    if confidence >= CONFIDENCE_THRESHOLD and intent in action_map:
        return action_map[intent]

    # General questions use the conversational assistant.
    return "ask_gemini"
