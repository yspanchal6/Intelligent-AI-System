"""Small, constrained automation helpers for the assistant."""

import re
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output"


def create_text_file(filename, content, overwrite=False):
    """Create a text file only inside the project's output directory."""
    name = Path(filename).name
    if not name or name in {".", ".."} or not name.lower().endswith(".txt"):
        return "Please provide a simple .txt filename, such as notes.txt."
    if re.search(r'[<>:"/\\|?*]', name):
        return "The filename contains unsupported characters."
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    target = (OUTPUT_DIR / name).resolve()
    if target.parent != OUTPUT_DIR.resolve():
        return "That file path is not allowed."
    if target.exists() and not overwrite:
        return f"A file named {name} already exists in output. Nothing was changed."
    try:
        target.write_text(content, encoding="utf-8")
        return f"Created file: output/{name}"
    except OSError as exc:
        return f"Could not create the file ({type(exc).__name__})."


def parse_note_command(text):
    """Parse: save note: filename.txt | content"""
    match = re.match(r"^(?:save note|write note):\s*([^|]+)\|\s*(.*)$", text.strip(), re.I | re.S)
    if match:
        return match.group(1).strip(), match.group(2).strip()

    match = re.match(
        r"^create (?:a )?text file(?: named)? ([^ ]+\.txt) with content[: ]+(.+)$",
        text.strip(), re.I | re.S,
    )
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return None
