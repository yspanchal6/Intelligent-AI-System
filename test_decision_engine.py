import unittest
from decision_engine import decide_action


class TestDecisionEngine(unittest.TestCase):
    def test_search_overrides_wrong_ml_intent(self):
        self.assertEqual(decide_action("add_task", 0.34, "Search the internet for Python tutorials"), "search_web")
        self.assertEqual(decide_action("calculator", 0.55, "Find the latest cybersecurity news"), "search_web")

    def test_math_and_question_routing(self):
        self.assertEqual(decide_action("calculator", 0.82, "calculate 12 + 8"), "calculate")
        self.assertEqual(decide_action("calculator", 0.55, "what is google"), "ask_gemini")

    def test_task_commands(self):
        self.assertEqual(decide_action("add_task", 0.80, "remind me to study"), "add_task")
        self.assertEqual(decide_action("list_tasks", 0.80, "show my tasks"), "list_tasks")
        self.assertEqual(decide_action("complete_task", 0.80, "complete task 2"), "complete_task")

    def test_whatsapp_message_command(self):
        self.assertEqual(
            decide_action("add_task", 0.2, "WhatsApp to +919876543210: Hello"),
            "send_message",
        )

    def test_note_command(self):
        self.assertEqual(decide_action("add_task", 0.2, "save note: notes.txt | hello"), "create_file")


if __name__ == "__main__":
    unittest.main()
