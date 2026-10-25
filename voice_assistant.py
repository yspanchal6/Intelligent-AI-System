
"""Optional speech input/output for the AI assistant.

Speech input: sounddevice + SpeechRecognition + Google's Web Speech service.
Speech output: pyttsx3.
Uses the system's default microphone unless a device is specified.
"""

import threading

_engine = None
_engine_lock = threading.Lock()
_MICROPHONE_DEVICE = 1  # None = system default microphone
_SAMPLE_RATE = 16000
_CHUNK_SECONDS = 0.1


def voice_input_available():
    """Check whether the required voice-input packages are installed."""
    try:
        import sounddevice  # noqa: F401
        import speech_recognition  # noqa: F401
        import numpy  # noqa: F401
        return True
    except ImportError:
        return False


def list_microphones():
    """Print available audio devices to help diagnose microphone issues."""
    try:
        import sounddevice as sd

        devices = sd.query_devices()
        for index, device in enumerate(devices):
            if device["max_input_channels"] > 0:
                print(
                    f"{index}: {device['name']} "
                    f"(input channels: {device['max_input_channels']})"
                )
    except Exception as exc:
        print(f"Could not list microphones: {type(exc).__name__}: {exc}")


def speak(text):
    """Speak text using pyttsx3. Return True on success."""
    global _engine

    try:
        import pyttsx3

        with _engine_lock:
            if _engine is None:
                _engine = pyttsx3.init()
                _engine.setProperty("rate", 175)
                _engine.setProperty("volume", 1.0)

            _engine.say(str(text))
            _engine.runAndWait()

        return True

    except Exception as exc:
        # Allow a later attempt to reinitialize the speech engine.
        _engine = None
        print(f"Speech output unavailable: {type(exc).__name__}: {exc}")
        return False


def listen_once(language="en-IN", timeout=6, phrase_time_limit=10):
    """Listen once and return recognized text, or None if unsuccessful."""
    try:
        import numpy as np
        import sounddevice as sd
        import speech_recognition as sr
    except ImportError as exc:
        print(f"Voice input package missing: {exc.name}")
        print(
            "Install with: "
            "python -m pip install sounddevice SpeechRecognition numpy"
        )
        return None

    try:
        device = _MICROPHONE_DEVICE
        if device is None:
            default_input = getattr(sd.default, "device")[0]
            if default_input is None or int(default_input) < 0:
                print("No default microphone is configured.")
                list_microphones()
                return None
            device = int(default_input)

        info = sd.query_devices(device, "input")
        if info["max_input_channels"] < 1:
            print(f"Audio device {device} does not support microphone input.")
            list_microphones()
            return None

        # Use a sample rate supported by the chosen device when possible.
        try:
            sd.check_input_settings(
                device=device,
                samplerate=_SAMPLE_RATE,
                channels=1,
                dtype="int16",
            )
            sample_rate = _SAMPLE_RATE
        except Exception:
            sample_rate = int(info["default_samplerate"])
            sd.check_input_settings(
                device=device,
                samplerate=sample_rate,
                channels=1,
                dtype="int16",
            )

        frames_per_chunk = max(1, int(sample_rate * _CHUNK_SECONDS))
        recognizer = sr.Recognizer()

        print(f"Listening... Speak now. (Microphone: {info['name']})")

        recorded = []
        elapsed = 0.0
        speech_elapsed = 0.0
        silence_elapsed = 0.0
        started = False
        noise_levels = []

        # Measure background noise briefly, then adapt the voice threshold.
        with sd.InputStream(
            samplerate=sample_rate,
            channels=1,
            dtype="int16",
            device=device,
            blocksize=frames_per_chunk,
        ) as stream:
            calibration_chunks = max(1, int(0.4 / _CHUNK_SECONDS))

            for _ in range(calibration_chunks):
                chunk, overflowed = stream.read(frames_per_chunk)
                if overflowed:
                    continue
                samples = chunk.astype(np.float32)
                rms = float(np.sqrt(np.mean(samples * samples)))
                noise_levels.append(rms)

            noise_rms = (
                float(np.median(noise_levels)) if noise_levels else 0.0
            )
            threshold = max(180.0, noise_rms * 2.5)

            while True:
                chunk, overflowed = stream.read(frames_per_chunk)
                if overflowed:
                    print("Warning: microphone buffer overflowed.")

                samples = chunk.copy()
                rms = float(
                    np.sqrt(
                        np.mean(samples.astype(np.float32) ** 2)
                    )
                )
                chunk_duration = frames_per_chunk / sample_rate

                if not started:
                    elapsed += chunk_duration

                    if rms >= threshold:
                        started = True
                        recorded.append(samples)
                        speech_elapsed = chunk_duration
                        silence_elapsed = 0.0
                    elif elapsed >= timeout:
                        print("No speech detected. Check your microphone or try again.")
                        return None
                else:
                    recorded.append(samples)
                    speech_elapsed += chunk_duration

                    if rms < threshold:
                        silence_elapsed += chunk_duration
                    else:
                        silence_elapsed = 0.0

                    # Stop after a short pause or the maximum phrase duration.
                    if silence_elapsed >= 0.8:
                        break
                    if speech_elapsed >= phrase_time_limit:
                        break

        if not recorded:
            print("No speech detected. Try again.")
            return None

        audio_samples = np.concatenate(recorded, axis=0).reshape(-1)
        audio = sr.AudioData(
            audio_samples.tobytes(),
            sample_rate,
            2,
        )

        try:
            text = recognizer.recognize_google(
                audio,
                language=language,
            ).strip()
        except sr.UnknownValueError:
            print("Speech was detected, but the words were unclear.")
            return None
        except sr.RequestError as exc:
            print(f"Speech recognition service unavailable: {exc}")
            print("Check your internet connection and try again.")
            return None

        if not text:
            print("No words were recognized. Please try again.")
            return None

        print(f"You (voice): {text}")
        return text

    except Exception as exc:
        print(f"Microphone/audio error: {type(exc).__name__}: {exc}")
        print("Use list_microphones() to inspect available input devices.")
        return None
