
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import task_manager


class TestTaskManager(unittest.TestCase):
    def test_add_list_and_complete_task(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            task_file = Path(temp_dir) / "tasks.json"

            with patch.object(task_manager, "TASK_FILE", task_file):
                self.assertEqual(
                    task_manager.add_task("Study for exam"),
                    "Task added: Study for exam",
                )
                self.assertEqual(
                    task_manager.add_task("Prepare for viva"),
                    "Task added: Prepare for viva",
                )

                tasks = task_manager.load_tasks()
                self.assertEqual(len(tasks), 2)
                self.assertEqual(tasks[0]["description"], "Study for exam")

                task_list = task_manager.list_tasks()
                self.assertIn("Your tasks:", task_list)
                self.assertIn("1. [Pending] Study for exam", task_list)
                self.assertIn("2. [Pending] Prepare for viva", task_list)

                self.assertEqual(
                    task_manager.complete_task(1),
                    "Task 1 marked as completed.",
                )
                self.assertTrue(task_manager.load_tasks()[0]["completed"])


if __name__ == "__main__":
    unittest.main()

