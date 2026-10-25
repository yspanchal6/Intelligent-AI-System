"""Optional live Gemini integration test; safe for offline test discovery."""

import os
import unittest

from dotenv import load_dotenv

load_dotenv()


class TestGeminiIntegration(unittest.TestCase):
    def test_generate_content(self):
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            self.skipTest("GEMINI_API_KEY is not configured.")

        try:
            from google import genai
        except ImportError:
            self.skipTest("google-genai package is not installed.")

        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        client = genai.Client(api_key=api_key)
        try:
            response = client.models.generate_content(
                model=model_name,
                contents="Explain machine learning in three simple sentences.",
            )
        except Exception as exc:
            self.skipTest(f"Gemini call unavailable right now: {type(exc).__name__}")

        self.assertTrue(response.text and response.text.strip())


if __name__ == "__main__":
    unittest.main()
