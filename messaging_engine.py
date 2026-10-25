"""Create a WhatsApp Web message draft; the user must review and send it."""

import re
import webbrowser
from urllib.parse import quote


def parse_whatsapp_command(text):
    """Parse: whatsapp to +919876543210: Hello there"""
    match = re.match(
        r"^\s*(?:send\s+)?(?:a\s+)?whatsapp(?:\s+message)?\s+to\s+([+\d()\s-]{7,25})\s*:\s*(.+?)\s*$",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return None
    phone = re.sub(r"\D", "", match.group(1))
    message = match.group(2).strip()
    if len(phone) < 8 or len(phone) > 15 or not message:
        return None
    return phone, message


def open_whatsapp_draft(phone, message):
    """Open a prefilled WhatsApp Web draft; does not send it automatically."""
    url = f"https://wa.me/{phone}?text={quote(message)}"
    try:
        opened = webbrowser.open(url)
    except Exception:
        opened = False
    if opened:
        return "WhatsApp Web opened with your message drafted. Review the recipient and click Send yourself."
    return f"Could not confirm browser launch. You can open this draft URL manually: {url}"
