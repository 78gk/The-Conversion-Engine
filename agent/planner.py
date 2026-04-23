from pathlib import Path
from typing import Any

from core.project_adapter import ProjectAdapter


DEFAULT_ADAPTER = ProjectAdapter(Path(__file__).resolve().parents[1])
INSTRUCTIONS_FILE = "input/TRP1 Challenge Week 10_ Conversion Engine for Sales Automation.md"


def _validate_tasks(raw_tasks: Any) -> list[dict[str, str]]:
    if not isinstance(raw_tasks, list):
        raise ValueError("Task manifest must be a list")

    tasks: list[dict[str, str]] = []
    for index, item in enumerate(raw_tasks):
        if not isinstance(item, dict):
            raise ValueError(f"Task entry {index} must be an object")

        task = item.get("task")
        tool = item.get("tool", "copilot")

        if not isinstance(task, str) or not task.strip():
            raise ValueError(f"Task entry {index} must include a non-empty 'task' string")
        if not isinstance(tool, str) or not tool.strip():
            raise ValueError(f"Task entry {index} must include a non-empty 'tool' string")

        tasks.append({"task": task.strip(), "tool": tool.strip()})

    if not tasks:
        raise ValueError("Task manifest cannot be empty")

    return tasks


def _extract_interim_tasks_from_instructions(adapter: ProjectAdapter) -> list[dict[str, str]]:
    if not adapter.exists(INSTRUCTIONS_FILE):
        return []

    content = adapter.read_text(INSTRUCTIONS_FILE)
    start_marker = "Interim Submission:"
    end_marker = "Final Submission:"

    start = content.find(start_marker)
    if start == -1:
        return []

    end = content.find(end_marker, start)
    if end == -1:
        end = len(content)

    interim_block = content[start:end]
    bullet_tasks: list[str] = []
    for raw_line in interim_block.splitlines():
        line = raw_line.strip()
        if line.startswith("●"):
            bullet = line.lstrip("●").strip()
            if bullet:
                bullet_tasks.append(bullet)

    if not bullet_tasks:
        return []

    tasks: list[dict[str, str]] = [
        {
            "task": "summarize interim submission requirements from input instructions",
            "tool": "copilot",
        }
    ]
    for bullet in bullet_tasks[:12]:
        tasks.append({"task": f"deliver interim requirement: {bullet}", "tool": "copilot"})

    tasks.append(
        {
            "task": "write interim submission report and evidence mapping",
            "tool": "copilot",
        }
    )
    return tasks


def _load_tasks(adapter: ProjectAdapter) -> tuple[list[dict[str, str]], str]:
    instruction_tasks = _extract_interim_tasks_from_instructions(adapter)
    if instruction_tasks:
        return instruction_tasks, INSTRUCTIONS_FILE

    if adapter.exists("input/tasks.json"):
        raw_tasks = adapter.read_json("input/tasks.json")
        return _validate_tasks(raw_tasks), "input/tasks.json"

    if adapter.exists("memory/tasks.json"):
        raw_tasks = adapter.read_json("memory/tasks.json")
        return _validate_tasks(raw_tasks), "memory/tasks.json"

    raise FileNotFoundError(
        "No task manifest found. Create input/tasks.json with a list of task objects."
    )


def run(adapter: ProjectAdapter | None = None):
    adapter = adapter or DEFAULT_ADAPTER
    print("Generating plan...")

    tasks, source = _load_tasks(adapter)

    adapter.write_json("memory/tasks.json", tasks)

    return {"status": "success", "task_count": len(tasks), "source": source}
