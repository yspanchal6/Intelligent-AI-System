# System Architecture

## Overview

The application is a command-line assistant organized around input handling, an intent-classification pipeline, explicit action routing, local tools, and optional external services.

```text
Terminal input / optional voice input
                |
                v
       main.py (orchestration)
                |
       command and follow-up checks
                |
                v
   TF-IDF feature extraction + classifier
                |
                v
       decision_engine.py
         /       |        \
        v        v         v
    Local tools  Web search  Gemini chat
        |        |         |
        +--------+---------+
                 |
           Response to user
```

Optional voice input/output is a separate capability and may require packages and operating-system support not needed for text mode.

## Component responsibilities

| Component | Responsibility |
|---|---|
| `main.py` | Initializes configuration and model components, handles the interaction loop, and coordinates actions. |
| `intents.py` | Supplies labeled example phrases used by the intent classifier. |
| `decision_engine.py` | Routes predicted intents to a defined set of supported actions. |
| `task_engine.py` | Evaluates supported arithmetic expressions using a restricted approach. |
| `task_manager.py` | Manages tasks in local JSON storage. |
| `local_knowledge.py` | Provides selected offline educational answers. |
| `chatbot_engine.py` | Integrates with the configured Gemini client for general responses. |
| `web_search.py` | Retrieves search results and may use Gemini to summarize them. |
| `automation_engine.py` | Handles constrained note creation with confirmation and a designated output directory. |
| `messaging_engine.py` | Opens a prefilled messaging draft after confirmation; it does not automatically send it. |
| `voice_assistant.py` | Provides optional speech input/output. |
| `evaluation.py` | Measures classifier performance on the evaluation split. |
| `compare_models.py` | Compares classifier configurations. |

Confirm each file exists in the current checkout before relying on a row above; project versions may differ.

## Request flow

1. The user enters a text command, or speech is transcribed when voice mode is enabled.
2. The application handles explicit control commands and applicable follow-up choices.
3. Text is converted to numerical features using TF-IDF vectorization.
4. A Logistic Regression classifier predicts an intent and a class score.
5. The decision engine selects a supported local action or configured fallback.
6. The selected component returns a result or a controlled error.
7. The application displays the response and may speak it in voice mode.

## Machine-learning pipeline

The project uses labeled example phrases rather than a large external dataset. The model is trained from the examples available in `intents.py`. If the current implementation uses word and character TF-IDF features, these representations help match phrases with different surface forms. Logistic Regression provides a lightweight classification baseline.

The model does not automatically learn from conversations. Changes to training phrases should be followed by evaluation on a held-out dataset. A small evaluation set cannot establish general-purpose accuracy.

## External services and persistence

- Gemini features require a valid API key, network access, provider/model access, and available quota.
- Web search depends on DDGS and network/service availability.
- Tasks are persisted in local JSON. Treat this data as private local data, not encrypted storage.
- Conversation history, where implemented, should be treated according to the actual runtime behavior of the source code.
