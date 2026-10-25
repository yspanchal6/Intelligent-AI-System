
import json
from pathlib import Path

TASK_FILE = Path(__file__).parent / "tasks.json"


def load_tasks():
    """Load saved tasks from the JSON file."""
    if not TASK_FILE.exists():
        return []

    try:
        with TASK_FILE.open("r", encoding="utf-8") as file:
            tasks = json.load(file)

        return tasks if isinstance(tasks, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_tasks(tasks):
    """Save tasks so they remain available after restarting."""
    with TASK_FILE.open("w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=4)


def add_task(description):
    description = description.strip()

    if not description:
        return "Task description cannot be empty."

    tasks = load_tasks()
    tasks.append({
        "id": max((task.get("id", 0) for task in tasks), default=0) + 1,
        "description": description,
        "completed": False
    })
    save_tasks(tasks)

    return f"Task added: {description}"


def list_tasks():
    tasks = load_tasks()

    if not tasks:
        return "No tasks saved yet."

    lines = ["Your tasks:"]

    for task in tasks:
        status = "Done" if task.get("completed") else "Pending"
        lines.append(
            f"{task['id']}. [{status}] {task['description']}"
        )

    return "\n".join(lines)


def complete_task(task_id):
    tasks = load_tasks()

    for task in tasks:
        if task.get("id") == task_id:
            if task.get("completed"):
                return f"Task {task_id} is already completed."

            task["completed"] = True
            save_tasks(tasks)
            return f"Task {task_id} marked as completed."

    return f"Task {task_id} was not found."
