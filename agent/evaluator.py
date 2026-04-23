from pathlib import Path

from agent.evaluation_script import EvaluationConfig, evaluate

from core.project_adapter import ProjectAdapter


DEFAULT_ADAPTER = ProjectAdapter(Path(__file__).resolve().parents[1])


def run(adapter: ProjectAdapter | None = None):
    adapter = adapter or DEFAULT_ADAPTER
    print("Running evaluation...")

    config = EvaluationConfig(project_root=adapter.root)
    outcome = evaluate(config)
    result = {
        "status": outcome.status,
        "pass@1": outcome.pass_at_1 if outcome.pass_at_1 is not None else 0.0,
        "prompt_count": outcome.prompt_count,
        "report_exists": outcome.report_exists,
        "details": outcome.details,
    }

    adapter.write_json("memory/metrics.json", result)

    return result
