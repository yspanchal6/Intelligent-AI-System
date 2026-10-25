# Intelligent AI System Using Python

A modular, text-first Python assistant that combines supervised intent classification, explicit action routing, local utilities, optional Gemini-powered responses, web search, task persistence, and optional voice interaction.

> **Project status:** Educational prototype. Feature availability depends on configuration and optional dependencies. See [Limitations](#limitations) and the detailed [documentation](docs/README.md).

## Contents

- [Features](#features)
- [Architecture](#architecture)
- [Technology stack](#technology-stack)
- [Project structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Run the application](#run-the-application)
- [Example commands](#example-commands)
- [Testing and evaluation](#testing-and-evaluation)
- [Security notes](#security-notes)
- [Limitations](#limitations)
- [Documentation](#documentation)

## Features

- **Intent classification:** word- and character-level TF-IDF features with Logistic Regression.
- **Explicit decision routing:** maps supported intents to defined Python actions.
- **Gemini integration:** optional general-question responses when API configuration and service availability permit.
- **Web search:** retrieves search results through DDGS; optional summarization can use Gemini.
- **Calculator:** restricted arithmetic evaluation rather than arbitrary Python `eval`.
- **Task manager:** add, list, and complete tasks with local JSON persistence.
- **Offline knowledge:** answers a limited set of coded educational topics.
- **Optional voice mode:** speech input/output when optional packages, microphone access, and compatible system dependencies are available.
- **Constrained automation:** creates text notes only in the designated output directory after confirmation.
- **Messaging draft:** can open a prefilled WhatsApp Web draft after confirmation; it does not send automatically.
- **Tests and evaluation scripts:** module tests plus classifier evaluation/model-comparison scripts.

Feature availability must be checked against the current code, configuration, and local environment. A module being present does not by itself prove that its external service is working.

## Architecture

```text
User (terminal; optional voice input)
                 |
                 v
        main.py / orchestration
                 |
        special-command handling
                 |
       TF-IDF + Logistic Regression
                 |
                 v
        decision_engine.py
          /      |       \
         v       v        v
   Local tools  Web search  Gemini chat
   - calculator - DDGS     - API configured
   - tasks      - optional summary
   - knowledge
   - note creation (confirmation)
   - WhatsApp draft (confirmation)
                 |
                 v
           User response
```

The intent model is trained from labeled examples in `intents.py` when initialized. It does not automatically learn from user conversations. See [System Architecture](docs/architecture.md) for more details.

## Technology stack

- Python
- scikit-learn
- python-dotenv
- Google Gen AI Python SDK (`google-genai`)
- DDGS for web search
- JSON for local task persistence
- Optional voice dependencies listed in `requirements-voice.txt`

## Project structure

```text
Intelligent-AI-System/
├── main.py
├── intents.py
├── decision_engine.py
├── chatbot_engine.py
├── web_search.py
├── task_engine.py
├── task_manager.py
├── local_knowledge.py
├── automation_engine.py
├── messaging_engine.py
├── voice_assistant.py
├── evaluation.py
├── compare_models.py
├── test_*.py
├── requirements.txt
├── requirements-voice.txt
├── .env.example
├── README.md
├── PROJECT_REPORT_NOTES.md
└── docs/
    ├── README.md
    ├── architecture.md
    ├── project-structure.md
    ├── setup-and-usage.md
    ├── testing.md
    └── security.md
```

The list above describes the clean documentation/source package. Optional files may vary by project version. Do not add claims about a module unless that module exists in your checked-out copy.

## Requirements

- Python 3.10 or newer is recommended.
- Internet access is needed for Gemini and web-search features.
- A Gemini API key is optional for local features but required for Gemini-backed features.
- Voice mode may require microphone permissions and additional system libraries.

## Installation

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`.
2. Add your own Gemini API key if you intend to use Gemini features.
3. Set `GEMINI_MODEL` to a model that is available to your account and supported by the installed SDK.
4. Keep `.env` private. Never commit real credentials or include them in screenshots.

Example `.env` format:

```dotenv
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=your_available_model_name
```

The model name is deliberately a placeholder; verify current model access with your provider account rather than assuming a particular model ID is available.

## Run the application

```bash
python main.py
```

Enter `help` to view commands supported by the current version and `exit` to close the assistant.

## Example commands

Exact phrasing depends on the training examples and command parsing in the current code. Examples to try include:

```text
help
Calculate 12 + 8
Show my tasks
Complete task 2
Search the web for Python courses
Explain machine learning
```

Some actions require confirmation. For WhatsApp drafts, the user must review and send the message manually.

## Testing and evaluation

Run the unit tests available in the repository:

```bash
python -m unittest test_task_engine.py test_task_manager.py test_decision_engine.py test_automation_engine.py test_chatbot_engine.py -v
```

Run classifier evaluation and model comparison:

```bash
python evaluation.py
python compare_models.py
```

If a test file or script is not present in your copy, omit it from the command and update the report accordingly. Record actual output, skipped tests, and errors; do not invent accuracy or test results. See [Testing](docs/testing.md).

## Security notes

- Keep `.env` and API keys out of Git.
- Review `.gitignore` before publishing.
- Do not include `.venv`, caches, generated data, or personal task files in the repository.
- Local task data is stored as JSON and should not be treated as encrypted.
- User confirmation is required for certain external actions.
- See [Security notes](docs/security.md).

## Limitations

- Intent classification is constrained by the quality and coverage of labeled training examples.
- Confidence scores are not equivalent to real-world accuracy.
- The offline knowledge base only covers topics implemented in code.
- Gemini and web search require network access and depend on external service availability, credentials, and quotas.
- Voice functionality depends on optional packages and local hardware/system configuration.
- Task data is stored locally and is not encrypted.
- This project has not been established as production-grade software.

## Documentation

- [Documentation index](docs/README.md)
- [Architecture and request flow](docs/architecture.md)
- [Project structure](docs/project-structure.md)
- [Setup and usage](docs/setup-and-usage.md)
- [Testing and evaluation](docs/testing.md)
- [Security notes](docs/security.md)
- [College report notes](PROJECT_REPORT_NOTES.md)

## Educational use

This project is intended for learning and demonstration. Add an explicit license file before publishing if you want to grant others clear reuse permissions.
