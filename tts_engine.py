"""Reliable synchronous Windows Text-to-Speech wrapper using SAPI5.

The engine is created and disposed for each utterance to avoid reusing a
stale pyttsx3 engine after microphone/audio operations.
"""
from __future__ import annotations

import threading

_TTS_LOCK = threading.RLock()


def speak(text: str) -> bool:
    """Speak text aloud with Windows SAPI5; return True if runAndWait completes."""
    message = str(text).strip()
    if not message:
        return True

    try:
        import pyttsx3

        with _TTS_LOCK:
            engine = pyttsx3.init(driverName="sapi5")
            engine.setProperty("rate", 175)
            engine.setProperty("volume", 1.0)

            # Prefer an English Windows voice when available; otherwise use default.
            try:
                voices = engine.getProperty("voices") or []
                for voice in voices:
                    descriptor = f"{getattr(voice, 'id', '')} {getattr(voice, 'name', '')}".lower()
                    if "english" in descriptor or "zira" in descriptor or "david" in descriptor:
                        engine.setProperty("voice", voice.id)
                        break
            except Exception:
                pass

            engine.say(message)
            engine.runAndWait()
            try:
                engine.stop()
            except Exception:
                pass
            del engine
        return True

    except Exception as exc:
        print(f"Speech output unavailable: {type(exc).__name__}: {exc}")
        return False
