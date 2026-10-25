# Setup and Usage

## Prerequisites

- Python 3.10 or newer is recommended.
- A terminal such as PowerShell, Command Prompt, or a Unix shell.
- Internet access for Gemini and web search.
- A Gemini API key only if Gemini-backed features are required.
- Microphone and compatible optional dependencies for voice mode.

## Windows PowerShell setup

Run these commands from the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation due to local policy, use Command Prompt activation or follow your institution's approved Python setup guidance. Do not weaken system policy unnecessarily.

## macOS / Linux setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Environment configuration

1. Copy `.env.example` to `.env`.
2. Add a provider-issued API key only if you need Gemini.
3. Set the model variable to a model ID currently available to your account.
4. Never commit `.env`, paste a key into source code, or include a secret in screenshots.

Example format:

```dotenv
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=your_available_model_name
```

## Run

```bash
python main.py
```

Use the application's built-in `help` command to see the exact commands supported by the current version. Use the documented exit command to close the program.

## Optional voice support

If `requirements-voice.txt` exists in your checkout, install it only when voice mode is needed:

```bash
python -m pip install -r requirements-voice.txt
```

Speech recognition may need internet access and microphone permissions. Package installation alone does not guarantee that voice mode will work on every operating system.

## Troubleshooting

- **Missing module:** activate the project's virtual environment and install the requirements.
- **Gemini authentication error:** verify `.env` key spelling, key validity, and that `.env` is in the project root.
- **Quota or rate-limit error:** check the provider's current quota and retry policy; local features may remain usable.
- **Model not found:** choose a model ID available to your account and supported by the installed SDK.
- **Search unavailable:** check network connectivity and the installed DDGS version.
- **Voice dependency error:** verify the optional dependency installation and operating-system requirements.
- **Task data issue:** back up local `tasks.json` before making manual edits.
