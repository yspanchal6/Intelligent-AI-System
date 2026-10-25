"""Intelligent AI System: Gemini chat, web search, and local tools."""

import os
import re
import webbrowser
from datetime import datetime
from urllib.parse import urlparse

from dotenv import load_dotenv
from google import genai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline, FeatureUnion

from automation_engine import create_text_file, parse_note_command
from messaging_engine import parse_whatsapp_command, open_whatsapp_draft
from voice_assistant import listen_once, voice_input_available
from tts_engine import speak
from chatbot_engine import GeminiChatbot
from local_fallback import local_fallback
from decision_engine import decide_action, normalize_text, SEARCH_PREFIXES
from intents import examples
from local_knowledge import get_local_answer
from task_engine import evaluate_expression
from task_manager import add_task, list_tasks, complete_task
from web_search import search_results, format_results



load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
API_KEY_2 = os.getenv("GEMINI_API_KEY_2", "").strip()

GEMINI_MODEL = (
    os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    or "gemini-2.5-flash"
)

try:
    client = genai.Client(api_key=API_KEY) if API_KEY else None
except Exception:
    client = None

try:
    backup_client = (
        genai.Client(api_key=API_KEY_2)
        if API_KEY_2 and API_KEY_2 != API_KEY
        else None
    )
except Exception:
    backup_client = None

chatbot = GeminiChatbot(
    client=client,
    backup_client=backup_client,
    model=GEMINI_MODEL,
    max_turns=8,
)


# Word + character TF-IDF helps handle small wording variations.
texts = [text for text, _ in examples]
labels = [label for _, label in examples]
model = make_pipeline(
    FeatureUnion([
        ("word", TfidfVectorizer(
            analyzer="word", ngram_range=(1, 2), sublinear_tf=True
        )),
        ("char", TfidfVectorizer(
            analyzer="char_wb", ngram_range=(2, 5), min_df=1,
            sublinear_tf=True
        )),
    ]),
    LogisticRegression(max_iter=1000, random_state=42),
)
model.fit(texts, labels)


def ask_gemini(question):
    """Use Gemini first, then fall back to local responses."""
    answer, error = chatbot.answer(question)
    if answer:
        return answer
    print(f"Using local fallback: {error}")
    return local_fallback(question)


def search_and_summarize(query):
    """Search the web, then summarize results when Gemini is available."""
    results = search_results(query, max_results=5)
    if not results:
        return format_results(query, results)

    formatted = format_results(query, results)
    answer, error = chatbot.answer(
        f"Answer this request using the retrieved search results: {query}",
        extra_context=formatted,
    )
    if answer:
        sources = "\n".join(
            f"- {item['title']}: {item['url']}"
            for item in results if item.get("url")
        )
        return f"{answer}\n\nSources:\n{sources}"

    return f"Gemini summary unavailable: {error}\n\n{formatted}"


def perform_calculation(user_text):
    """Handle simple two-operand arithmetic, including common speech wording."""
    text = user_text.lower().strip()
    for prefix in ("calculate", "compute", "what is", "what's", "solve"):
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
            break

    replacements = (
        ("multiplied by", "*"),
        ("multiply by", "*"),
        ("divided by", "/"),
        ("divide by", "/"),
        ("times", "*"),
        ("plus", "+"),
        ("minus", "-"),
        ("modulo", "%"),
        ("mod", "%"),
        (" x ", " * "),
        (" by ", " / "),
    )
    for phrase, symbol in replacements:
        text = text.replace(phrase, symbol)

    text = re.sub(r"\s+", " ", text).strip()
    match = re.fullmatch(
        r"(-?\d+(?:\.\d+)?)\s*([+\-*/%])\s*(-?\d+(?:\.\d+)?)",
        text,
    )
    if not match:
        return "I couldn't parse that calculation. Try: calculate 12 + 8"

    expression = "".join(match.groups())
    try:
        return f"The answer is {evaluate_expression(expression)}"
    except (ValueError, SyntaxError, ZeroDivisionError) as exc:
        return f"Calculation failed: {exc}"


def extract_task_description(text):
    """Extract task text from supported task commands."""
    patterns = (
        r"^\s*add\s+(?:a\s+)?task\s+(?:to\s+)?(.+?)\s*$",
        r"^\s*create\s+(?:a\s+)?task\s+(?:to\s+)?(.+?)\s*$",
        r"^\s*new\s+task\s*:\s*(.+?)\s*$",
        r"^\s*remind\s+me\s+to\s+(.+?)\s*$",
    )
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return match.group(1).strip()
    return None


def extract_task_id(text):
    match = re.search(r"\b(?:task|item)\s*#?\s*(\d+)\b", text.lower())
    return int(match.group(1)) if match else None


def show_help():
    print("""
Commands and examples:

  Ask anything:          Explain machine learning simply
  Web search + summary:  Search the web for free Python courses
  Calculator:            Calculate 12 + 8
  Add task:              Remind me to study Python
  List tasks:            Show my tasks
  Complete task:         Complete task 2
  Open a website:        Open Google / Open website example.com
  Open YouTube:          Open YouTube
  Create note file:      Save note: study.txt | Revise Python and DSA
  Voice mode:            voice mode / text mode
  WhatsApp draft:        WhatsApp to +919876543210: Hello there
  Current time/date:     What time is it / What is today's date
  Clear chat memory:     clear conversation
  Exit:                  exit / goodbye

Files created by the assistant are restricted to the project's output/ folder.
""")


def _confirmation_value(answer):
    """Return True/False for clear yes/no replies, or None if ambiguous."""
    if not answer:
        return None

    text = normalize_text(answer).lower()
    text = re.sub(r"[^\w\s'-]", " ", text)
    words = set(text.split())

    negative_phrases = {
        "no", "n", "nope", "nah", "cancel", "cancel it", "stop",
        "don't", "do not", "not now", "never mind", "nevermind",
    }
    positive_phrases = {
        "yes", "y", "yeah", "yep", "yup", "sure", "certainly",
        "absolutely", "obviously", "okay", "ok", "correct",
        "affirmative", "proceed",
    }

    # Negatives take priority, avoiding accidental confirmation of "no, don't".
    if text in negative_phrases or words.intersection(
        {"no", "nope", "nah", "cancel", "stop", "never", "don't"}
    ):
        return False

    if text in positive_phrases or words.intersection(
        {"yes", "yeah", "yep", "yup", "sure", "certainly",
         "absolutely", "obviously", "okay", "ok", "affirmative", "proceed"}
    ):
        return True

    # Handle common natural confirmations such as "yes, open YouTube".
    if words.intersection({"yes", "yeah", "yep", "yup"}) and not words.intersection(
        {"no", "cancel", "stop", "don't"}
    ):
        return True

    return None


def _parse_browser_command(command):
    """Return (url, requested_browser, search_query) for spoken browser requests."""
    text = normalize_text(command).lower().strip()
    text = re.sub(r"[,.!?]+$", "", text)

    # Explicit search requests should use a search engine rather than opening a guessed URL.
    search_match = re.match(
        r"^(?:please\s+)?(?:search(?:\s+the\s+web)?\s+for|google\s+search\s+for|look\s+up|find)\s+(.+)$",
        text,
    )
    if search_match:
        query = search_match.group(1).strip()
        query = re.sub(r"\s+in\s+(?:my\s+)?(?:google\s+)?(?:chrome|edge|firefox)\s+browser$", "", query)
        return None, None, query

    browser = None
    browser_match = re.search(r"\b(?:in|using|with)\s+(?:my\s+)?(chrome|google chrome|edge|microsoft edge|firefox)\s*(?:browser)?$", text)
    if browser_match:
        browser_text = browser_match.group(1)
        browser = "chrome" if "chrome" in browser_text else ("edge" if "edge" in browser_text else "firefox")
        text = text[:browser_match.start()].strip()

    text = re.sub(r"^(?:please\s+)?(?:open|opening|launch|launching|visit|visiting|go to|navigate to)\s+", "", text)
    text = re.sub(r"^(?:the\s+)?(?:website|site)\s+", "", text)
    text = re.sub(r"\s+(?:website|site)$", "", text).strip().rstrip("/")

    aliases = {
        "google": "https://www.google.com",
        "google.com": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "youtube.com": "https://www.youtube.com",
        "github": "https://github.com",
        "github.com": "https://github.com",
        "facebook": "https://www.facebook.com",
        "instagram": "https://www.instagram.com",
        "linkedin": "https://www.linkedin.com",
        "hack the box": "https://www.hackthebox.com",
        "chrome": "https://www.google.com",
        "chrome browser": "https://www.google.com",
    }
    if text in aliases:
        return aliases[text], browser, None

    if text.startswith(("https://", "http://")):
        url = text
    elif " " not in text and "." in text:
        url = "https://" + text
    else:
        return None, browser, None

    parsed = urlparse(url)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or "." not in parsed.hostname
        or parsed.username
        or parsed.password
        or any(ch.isspace() for ch in url)
    ):
        return None, browser, None
    return url, browser, None



def _open_url(url, browser=None):
    """Attempt to open a URL; return (success, detail)."""
    try:
        if browser:
            try:
                browser_controller = webbrowser.get(browser)
                opened = bool(browser_controller.open(url, new=2))
                return opened, browser if opened else f"{browser} could not open the URL"
            except webbrowser.Error:
                # Requested browser is unavailable; try the default browser.
                opened = bool(webbrowser.open(url, new=2))
                if opened:
                    return True, "default browser (requested browser unavailable)"
                return False, "Requested browser and default browser could not open the URL"

        opened = bool(webbrowser.open(url, new=2))
        return opened, "default browser" if opened else "Browser could not open the URL"

    except Exception as exc:
        return False, str(exc)


def _display_site_name(url):
    """Return a friendly website name for spoken status messages."""
    host = (urlparse(url).hostname or "").lower()
    host = host.removeprefix("www.")
    known_names = {
        "google.com": "Google",
        "youtube.com": "YouTube",
        "github.com": "GitHub",
        "facebook.com": "Facebook",
        "instagram.com": "Instagram",
        "linkedin.com": "LinkedIn",
        "hackthebox.com": "Hack The Box",
    }
    if host in known_names:
        return known_names[host]
    # For other domains, use the first domain label rather than "www".
    first_label = host.split(".")[0] if host else "website"
    return first_label.replace("-", " ").title()


def _website_url(command):
    """Backward-compatible URL parser for other handlers."""
    url, _, query = _parse_browser_command(command)
    return url if not query else None


def run_assistant():
    print("\n" + "=" * 52)
    print("       INTELLIGENT AI ASSISTANT USING PYTHON")
    print("=" * 52)
    print(
        f"Gemini: {'configured (' + GEMINI_MODEL + ')' if client else 'not configured; local tools still work'}"
    )
    print("Web search: DDGS | Type 'help' for examples | 'exit' to close")
    print("Optional voice: type 'voice mode' to enable speech input/output.")
    voice_mode = False

    def reply(message):
        """Print the assistant's text response and speak the same response in voice mode."""
        text = str(message).strip()
        if not text:
            return
        print(f"Assistant: {text}")
        if voice_mode:
            try:
                spoken = speak(text)
                if not spoken:
                    print("Voice output failed. The text response is still available above.")
            except Exception as exc:
                print(f"Voice output unavailable: {type(exc).__name__}: {exc}")

    def ask_user(prompt):
        if voice_mode:
            print(prompt)
            try:
                spoken = speak(prompt.replace("Assistant: ", ""))
                if not spoken:
                    print("Voice prompt failed; listen for the prompt in the terminal.")
            except Exception as exc:
                print(f"Voice output unavailable: {type(exc).__name__}: {exc}")
            try:
                answer = listen_once()
                return str(answer).strip() if answer is not None else ""
            except KeyboardInterrupt:
                print("\nAssistant: Confirmation interrupted.")
                return "cancel"
        return input(prompt).strip()

    def ask_confirmation(prompt, retries=3):
        """Retry unclear responses and accept natural spoken yes/no phrases."""
        for attempt in range(retries):
            if attempt == 0:
                question = prompt
            else:
                question = "Assistant: Please say yes to confirm or no to cancel: "

            answer = ask_user(question)
            decision = _confirmation_value(answer)
            if decision is not None:
                return decision

        reply("I couldn't understand the confirmation. The action was cancelled.")
        return False

    while True:
        try:
            if voice_mode:
                user_text = listen_once()
                if user_text is None:
                    continue
                user_text = str(user_text).strip()
                if user_text:
                    pass  # Proceed with the recognized text.
            else:
                user_text = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAssistant: Goodbye!")
            break

        if not user_text:
            continue

        normalized = normalize_text(user_text)

        if normalized == "voice mode":
            if not voice_input_available():
                reply(
                    "Voice input is not installed. Run: "
                    "python -m pip install -r requirements-voice.txt, "
                    "then restart the assistant."
                )
            else:
                voice_mode = True
                reply(
                    "Voice mode enabled. Speak your requests. "
                    "Say text mode to return to keyboard input."
                )
            continue

        if normalized == "text mode":
            voice_mode = False
            print("Assistant: Text mode enabled.")
            continue

        if normalized in {
            "exit", "quit", "bye", "goodbye", "good bye",
            "goodbye assistant", "good bye assistant", "bye assistant",
            "see you", "stop assistant", "close assistant",
        }:
            reply("Goodbye!")
            break

        if normalized == "clear conversation":
            chatbot.clear_history()
            reply("Conversation history cleared.")
            continue

        if normalized in {"help", "show help", "what can you do"}:
            show_help()
            continue

        # Basic assistant identity questions should not require Gemini/API quota.
        identity_text = re.sub(r"[?!.,]+$", "", normalized).strip()
        if identity_text in {
            "what is your name", "whats your name", "who are you",
            "tell me your name", "what are you called",
        }:
            reply("My name is Intelligent AI Assistant. I am a Python-based assistant.")
            continue

        # Follow-up choice for the local ML overview precedes classifier routing.
        if user_text.strip() in {"1", "2", "3"}:
            local_answer = get_local_answer(user_text.strip())
            if local_answer:
                reply(local_answer)
                continue

        # Deterministic handling for spoken website, browser, and search requests.
        browser_url, requested_browser, search_query = _parse_browser_command(user_text)
        normalized_for_open = re.sub(r"[,.!?]+$", "", normalized)
        open_prefix = re.match(
            r"^(?:please\s+)?(?:open|opening|launch|launching|visit|visiting|go to|navigate to)\b",
            normalized_for_open,
        )

        # Support multiple named sites in one command, e.g. "open Google and YouTube in Chrome".
        multi_match = re.match(
            r"^(?:please\s+)?(?:open|opening|launch|launching|visit|visiting|go to|navigate to)\s+(.+)$",
            normalized,
        )
        if multi_match and not search_query:
            multi_text = multi_match.group(1).strip()
            multi_browser = None
            browser_match = re.search(
                r"\s+(?:in|using|with)\s+(?:my\s+)?(chrome|google chrome|edge|microsoft edge|firefox)\s*(?:browser)?$",
                multi_text,
            )
            if browser_match:
                browser_name = browser_match.group(1)
                multi_browser = "chrome" if "chrome" in browser_name else ("edge" if "edge" in browser_name else "firefox")
                multi_text = multi_text[:browser_match.start()].strip()
            parts = [part.strip() for part in re.split(r"\s+and\s+", multi_text) if part.strip()]
            if len(parts) > 1:
                urls = [_website_url(part) for part in parts]
                if all(urls):
                    names = [_display_site_name(url) for url in urls]
                    site_summary = " and ".join(names)
                    if ask_confirmation(f"Assistant: Open {site_summary}? Please say yes or no: "):
                        failed = []
                        for url, name in zip(urls, names):
                            reply(f"Opening {name}.")
                            ok, browser_used = _open_url(url, multi_browser)
                            if ok:
                                reply(f"Opened {name}.")
                            else:
                                failed.append(name)
                                reply(f"Not opening {name}.")
                        if failed:
                            pass
                    else:
                        reply("Cancelled.")
                    continue

        if search_query:
            reply(f"Searching the web for {search_query}.")
            results = search_results(search_query)
            if results:
                formatted = format_results(results)
                reply(formatted)
            else:
                # If the search provider returns no results, open a search page.
                search_url = "https://www.google.com/search?q=" + __import__("urllib.parse", fromlist=["quote_plus"]).quote_plus(search_query)
                ok, browser_used = _open_url(search_url, requested_browser)
                reply(
                    f"No search results were returned. Search page opening request sent using {browser_used}."
                    if ok else "Search failed and the browser could not be launched."
                )
            continue

        # Handle both "open Google" and "opening Google in Chrome browser".
        if open_prefix and browser_url:
            site_name = _display_site_name(browser_url)
            reply(f"Opening {site_name}.")
            opened, browser_used = _open_url(browser_url, requested_browser)
            if opened:
                reply(f"Opened {site_name}.")
            else:
                reply(f"Not opening {site_name}.")
            continue

        probabilities = model.predict_proba([user_text])[0]
        best_index = probabilities.argmax()
        intent = model.classes_[best_index]
        confidence = float(probabilities[best_index])
        action = decide_action(intent, confidence, user_text)
        print(f"Detected intent: {intent} ({confidence:.1%}) | Action: {action}")

        if action == "search_web":
            query = user_text
            for prefix in SEARCH_PREFIXES:
                if normalized.startswith(prefix.strip()):
                    query = user_text[len(prefix):].strip()
                    break
            reply("Searching the web and preparing a summary...")
            reply(search_and_summarize(query))

        elif action == "calculate":
            reply(perform_calculation(user_text))

        elif action == "add_task":
            description = extract_task_description(user_text)
            if not description:
                description = ask_user("Task description: ")
            reply(
                add_task(description)
                if description else "Task description cannot be empty."
            )

        elif action == "list_tasks":
            reply(list_tasks())

        elif action == "complete_task":
            task_id = extract_task_id(user_text)
            if task_id is None:
                try:
                    task_id = int(ask_user("Task ID to complete: ") or "")
                except (ValueError, TypeError):
                    reply("Enter a numeric task ID.")
                    continue
            reply(complete_task(task_id))

        elif action == "open_website":
            url = _website_url(user_text)
            if not url:
                reply("Please specify a valid website, such as open example.com.")
                continue
            if ask_confirmation(f"Assistant: Open {url}? Please say yes or no: "):
                opened = webbrowser.open(url)
                reply(
                    "Browser request sent."
                    if opened else "I couldn't confirm the browser opened."
                )
            else:
                reply("Cancelled.")

        elif action == "open_youtube":
            if ask_confirmation("Assistant: Open YouTube? Please say yes or no: "):
                reply("Opening YouTube.")
                opened, browser_used = _open_url("https://www.youtube.com")
                reply("Opened YouTube." if opened else "Not opening YouTube.")
            else:
                reply("Cancelled.")

        elif action == "send_message":
            parsed = parse_whatsapp_command(user_text)
            if not parsed:
                reply(
                    "Use this format: WhatsApp to +919876543210: "
                    "Your message text"
                )
                continue
            phone, message = parsed
            if ask_confirmation(
                f"Assistant: Open WhatsApp Web draft for {phone}? "
                "Review it before sending. Please say yes or no: "
            ):
                reply(open_whatsapp_draft(phone, message))
            else:
                reply("Message draft cancelled.")

        elif action == "create_file":
            parsed = parse_note_command(user_text)
            if parsed:
                filename, content = parsed
                if ask_confirmation(
                    f"Assistant: Create output/{filename}? Please say yes or no: "
                ):
                    reply(create_text_file(filename, content))
                else:
                    reply("File creation cancelled.")
            else:
                reply("Use: Save note: notes.txt | Your note content")

        elif action == "show_time":
            reply("The current time is " + datetime.now().strftime("%I:%M %p"))

        elif action == "show_date":
            reply("Today's date is " + datetime.now().strftime("%d-%m-%Y"))

        elif action == "greeting":
            reply("Hello! What would you like to work on?")

        elif action == "show_help":
            show_help()

        else:
            local_answer = get_local_answer(user_text)
            if local_answer and not client:
                reply("(Local knowledge) " + local_answer)
            else:
                reply(ask_gemini(user_text))


if __name__ == "__main__":
    try:
        run_assistant()
    except KeyboardInterrupt:
        print("\nAssistant: Stopped safely. Goodbye!")
