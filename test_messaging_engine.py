import unittest
from unittest.mock import patch
from messaging_engine import parse_whatsapp_command, open_whatsapp_draft


class TestMessagingEngine(unittest.TestCase):
    def test_parse_whatsapp_command(self):
        self.assertEqual(
            parse_whatsapp_command("WhatsApp to +91 98765-43210: Hello there"),
            ("919876543210", "Hello there"),
        )

    def test_reject_invalid_command(self):
        self.assertIsNone(parse_whatsapp_command("WhatsApp to: hello"))

    @patch("messaging_engine.webbrowser.open", return_value=True)
    def test_opens_draft_not_sending(self, mock_open):
        result = open_whatsapp_draft("919876543210", "Hello there")
        self.assertIn("click Send yourself", result)
        self.assertIn("wa.me/919876543210", mock_open.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
