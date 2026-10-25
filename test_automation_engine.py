import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import automation_engine


class TestAutomationEngine(unittest.TestCase):
    def test_create_text_file_in_output_folder(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out = Path(temp_dir) / "output"
            with patch.object(automation_engine, "OUTPUT_DIR", out):
                result = automation_engine.create_text_file("notes.txt", "hello")
                self.assertEqual(result, "Created file: output/notes.txt")
                self.assertEqual((out / "notes.txt").read_text(encoding="utf-8"), "hello")

    def test_reject_non_txt(self):
        self.assertIn(".txt filename", automation_engine.create_text_file("notes.py", "hello"))

    def test_parse_note_command(self):
        self.assertEqual(automation_engine.parse_note_command("Save note: a.txt | hello"), ("a.txt", "hello"))


if __name__ == "__main__":
    unittest.main()
