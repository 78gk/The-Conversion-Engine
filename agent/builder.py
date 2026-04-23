from pathlib import Path

from agent.prompt_utils import (
    load_previous_metrics,
    render_previous_metrics_section,
    render_requirements_block,
)
from core.project_adapter import ProjectAdapter


DEFAULT_ADAPTER = ProjectAdapter(Path(__file__).resolve().parents[1])


def run(adapter: ProjectAdapter | None = None):
    adapter = adapter or DEFAULT_ADAPTER
    print("Generating build prompts...")

    tasks = adapter.read_json("memory/tasks.json", default=[])
    if not isinstance(tasks, list):
        raise ValueError("memory/tasks.json must contain a list of tasks")

    previous_metrics = load_previous_metrics(adapter)
    requirements_block = render_requirements_block()

    prompts_dir = adapter.resolve("artifacts/prompts")
    prompts_dir.mkdir(parents=True, exist_ok=True)

    for i, task in enumerate(tasks):
        if not isinstance(task, dict) or "task" not in task:
            raise ValueError(f"Task entry {i} must be an object with a 'task' field")

        task_name = task["task"]
        previous_run_section = render_previous_metrics_section(previous_metrics)
        prompt = (
            f"Task: {task_name}\n\n"
            f"{requirements_block}"
            f"{previous_run_section}"
        )
        adapter.write_text_if_changed(f"artifacts/prompts/task_{i}.txt", prompt)

    current_names = {f"task_{index}.txt" for index in range(len(tasks))}
    for existing_file in prompts_dir.glob("task_*.txt"):
        if existing_file.name not in current_names:
            existing_file.unlink(missing_ok=True)

    return {"status": "success", "prompt_count": len(tasks)}
