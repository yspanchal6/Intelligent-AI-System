
import unittest
from unittest.mock import Mock
from chatbot_engine import GeminiChatbot


class TestGeminiChatbot(unittest.TestCase):
    def test_no_client_has_safe_message(self):
        bot = GeminiChatbot(client=None)
        answer, error = bot.answer("hello")
        self.assertIsNone(answer)
        self.assertIn("not configured", error)

    def test_history_is_bounded(self):
        bot = GeminiChatbot(client=Mock(), max_turns=2)
        bot.history.extend([
            ("User", "1"),
            ("Assistant", "1"),
            ("User", "2"),
            ("Assistant", "2"),
        ])
        bot.history.append(("User", "3"))
        self.assertLessEqual(len(bot.history), 4)

    def test_quota_error_prevents_repeated_api_calls(self):
        client = Mock()
        client.models.generate_content.side_effect = Exception(
            "429 RESOURCE_EXHAUSTED: quota exceeded"
        )

        bot = GeminiChatbot(client=client)

        answer1, error1 = bot.answer("Explain AI")
        self.assertIsNone(answer1)
        self.assertIn("quota", error1.lower())
        self.assertTrue(bot.quota_exhausted)

        answer2, error2 = bot.answer("Explain recursion")
        self.assertIsNone(answer2)
        self.assertIn("quota", error2.lower())

        # The mocked Gemini endpoint must be called only once.
        self.assertEqual(
            client.models.generate_content.call_count,
            1,
        )


if __name__ == "__main__":
    unittest.main()
