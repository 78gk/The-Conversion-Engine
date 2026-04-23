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
    print("Generating debug prompts...")

    previous_metrics = load_previous_metrics(adapter)
    previous_run_section = render_previous_metrics_section(previous_metrics)
    requirements_block = render_requirements_block()

    prompt = (
        "Task: fix issues in the current implementation.\n\n"
        f"{requirements_block}"
        "Focus:\n"
        "- incorrect logic\n"
        "- missing error handling\n"
        f"{previous_run_section}"
    )

    adapter.write_text_if_changed("artifacts/prompts/fix.txt", prompt)

    return {"status": "success", "prompt_path": "artifacts/prompts/fix.txt"}
